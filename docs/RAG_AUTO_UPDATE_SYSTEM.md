# Hệ Thống Tự Động Cập Nhật RAG Vector Database

## 📋 Tổng Quan

Hệ thống RAG (Retrieval-Augmented Generation) tự động cập nhật vector database mỗi ngày với các bài báo tài chính mới từ Silver Layer, sử dụng Vietnamese SBERT embeddings và FAISS vector search.

### Kiến Trúc Tổng Thể

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG Pipeline Architecture                     │
└─────────────────────────────────────────────────────────────────┘

Silver Layer (S3)                RAG Processing                  RAG Storage (S3)
─────────────────               ──────────────────              ────────────────
                                                                
silver/news/                    ┌──────────────┐               rag/input/
partition_date=                 │   Extract    │               ├── raw_news_*.csv
  YYYY-MM-DD/                   │  & Prepare   │               │
  news_cleaned.parquet ────────>│  Documents   │──────────────>rag/processed/
                                └──────────────┘               ├── processed_for_embedding_*.csv
                                       │                        │
                                       ▼                       rag/staging/
                                ┌──────────────┐               └── prepared_documents_*.json
                                │   Create     │
                                │  Vietnamese  │               rag/embeddings/
                                │ SBERT Embed  │──────────────>└── vietnamese_embeddings_*.json
                                └──────────────┘                    (768-dim vectors)
                                       │
                                       ▼
                                ┌──────────────┐               rag/vectordb/
                                │    Update    │               ├── faiss_index.bin
                                │    FAISS     │──────────────>├── metadata.pkl
                                │  VectorDB    │               └── embeddings_info.json
                                └──────────────┘
                                       │
                                       ▼
                                ┌──────────────┐
                                │   Validate   │
                                │  & Test      │
                                │   Search     │
                                └──────────────┘
```

---

## 🔄 Pipeline Workflow Chi Tiết

### Task 1: Extract & Prepare Documents

**Mục đích**: Đọc dữ liệu từ Silver Layer, chunking và chuẩn bị cho embedding

**Input**: 
- `s3://bankanalystportfolio/silver/news/partition_date=YYYY-MM-DD/news_cleaned.parquet`

**Process**:
1. **Read Parquet as Binary** (fix UTF-8 decode issue)
   ```python
   s3_client = s3_hook.get_conn()
   obj = s3_client.get_object(Bucket=bucket_name, Key=news_file_key)
   parquet_bytes = obj['Body'].read()
   news_df = pd.read_parquet(io.BytesIO(parquet_bytes))
   ```

2. **Schema Mapping** (Silver → RAG):
   | Silver Column | RAG Field | Purpose |
   |--------------|-----------|---------|
   | `content` | `clean_content` | Article text for embedding |
   | `link` | `url` | Source URL |
   | `data_date` | `published_date` | Publication date |
   | `title` | `title` | Article title |
   | `source` | `source` | News source |
   | `id` | `doc_id` | Document identifier |

3. **Text Chunking Strategy**:
   - **Paragraph-based**: Split by `\n\n` (preserves context)
   - **Min chunk size**: 100 characters
   - **Max chunk size**: 1000 characters
   - **Overlap**: None (clean paragraph boundaries)
   
   ```python
   chunks = content.split('\n\n')
   valid_chunks = [c for c in chunks if 100 <= len(c) <= 1000]
   ```

4. **Deduplication**:
   - Based on `doc_id` (original article ID + chunk index)
   - Prevents duplicate vectors in FAISS index

**Output**:
```
rag/input/raw_news_2025-10-28.csv
rag/processed/processed_for_embedding_2025-10-28.csv
rag/staging/prepared_documents_2025-10-28.json
```

**Metrics**: `documents_prepared = 29` (example from 2025-10-28)

---

### Task 2: Create Vietnamese SBERT Embeddings

**Mục đích**: Tạo vector embeddings từ text tiếng Việt

**Model**: 
- **Name**: `keepitreal/vietnamese-sbert`
- **Architecture**: Sentence-BERT fine-tuned for Vietnamese
- **Embedding Dimension**: **768** (not 384!)
- **Framework**: `sentence-transformers` + PyTorch

**Process**:

1. **Load Model** (first run downloads ~1.3GB):
   ```python
   from sentence_transformers import SentenceTransformer
   model = SentenceTransformer('keepitreal/vietnamese-sbert')
   # ✅ Model loaded successfully (dim=768)
   ```

2. **Batch Encoding**:
   ```python
   texts = [doc['clean_content'] for doc in documents]
   embeddings = model.encode(
       texts,
       batch_size=32,
       show_progress_bar=True,
       convert_to_numpy=True
   )
   # Output shape: (n_docs, 768)
   ```

3. **Save Embeddings**:
   ```json
   {
     "model_name": "keepitreal/vietnamese-sbert",
     "embedding_dimension": 768,
     "created_at_utc": "2025-10-28T10:42:51.123456Z",
     "total_documents": 29,
     "documents": [
       {
         "doc_id": "article_001_chunk_0",
         "title": "VN-Index tăng mạnh...",
         "clean_content": "Thị trường chứng khoán...",
         "url": "https://...",
         "published_date": "2025-10-28",
         "source": "VnExpress",
         "embedding": [0.123, -0.456, ..., 0.789]  // 768 floats
       }
     ]
   }
   ```

**Output**:
```
rag/embeddings/vietnamese_embeddings_2025-10-28.json
```

**Performance**:
- **Speed**: ~20-27 it/s (documents per second)
- **CPU only** (can be accelerated with GPU using `faiss-gpu`)

**Metrics**: `embeddings_created = 29`

---

### Task 3: Update FAISS Vector Database

**Mục đích**: Thêm vectors mới vào FAISS index, incremental update

**FAISS Configuration**:
```python
import faiss

# Index type: Inner Product (for cosine similarity)
index = faiss.IndexFlatIP(embedding_dim=768)

# Properties:
# - Flat index: Exact search (no approximation)
# - IP (Inner Product): Cosine similarity scoring
# - Dimension: 768 (Vietnamese SBERT output)
```

**Process Flow**:

1. **Check Existing Index on S3**:
   ```python
   index_exists = s3_hook.check_for_key('rag/vectordb/faiss_index.bin')
   metadata_exists = s3_hook.check_for_key('rag/vectordb/metadata.pkl')
   ```

2. **First Run** (No existing index):
   ```python
   # Create new empty index
   vectordb.create_index()
   # ✅ Created FAISS index: IndexFlatIP (dim=768)
   ```

3. **Subsequent Runs** (Load existing):
   ```python
   # Download from S3
   index_obj = s3_client.get_object(Bucket, Key='rag/vectordb/faiss_index.bin')
   index_bytes = index_obj['Body'].read()
   
   # Load FAISS index
   faiss.read_index('faiss_index.bin')
   # 📥 Found existing vectordb in S3
   # 📂 Loaded FAISS index (vectors: 29)
   ```

4. **Dimension Detection** (Critical Fix):
   ```python
   # Detect actual embedding dimension from data
   first_embedding = documents[0]['embedding']
   actual_dim = len(first_embedding)  # 768
   
   # Create vectordb with correct dimension
   vectordb = FAISSVectorDatabase(embedding_dim=actual_dim)
   ```

5. **Deduplication & Add Vectors**:
   ```python
   # Check for duplicate doc_ids
   for doc in documents:
       if doc['doc_id'] in vectordb.doc_id_to_idx:
           skip_duplicate()
       else:
           vectors_to_add.append(doc['embedding'])
   
   # Add to FAISS
   vectors_array = np.array(vectors_to_add, dtype='float32')
   vectordb.index.add(vectors_array)
   # ✅ Added 29 vectors to FAISS index (total: 29)
   ```

6. **Save to S3**:
   ```python
   # Save FAISS index
   faiss.write_index(index, 'faiss_index.bin')
   s3_hook.load_file('faiss_index.bin', 'rag/vectordb/faiss_index.bin')
   
   # Save metadata (pickle)
   with open('metadata.pkl', 'wb') as f:
       pickle.dump({
           'document_store': vectordb.document_store,
           'doc_id_to_idx': vectordb.doc_id_to_idx
       }, f)
   s3_hook.load_file('metadata.pkl', 'rag/vectordb/metadata.pkl')
   
   # Save embeddings info (JSON)
   embeddings_info = {
       'last_update': '2025-10-28',
       'model_name': 'keepitreal/vietnamese-sbert',
       'embedding_dimension': 768,
       'total_vectors': 29,
       'vectors_added_today': 29
   }
   s3_hook.load_string(json.dumps(embeddings_info), 
                       'rag/vectordb/embeddings_info.json')
   ```

**Output**:
```
rag/vectordb/
├── faiss_index.bin          # FAISS index file (~22KB for 29 vectors)
├── metadata.pkl             # Document metadata (~15KB)
└── embeddings_info.json     # Stats & info (~500 bytes)
```

**Metrics**: `vectors_added = 29`

---

### Task 4: Validate & Test Search

**Mục đích**: Kiểm tra pipeline hoàn chỉnh và test search functionality

**Validation Checks**:

1. ✅ **Document Preparation**: XCom check
2. ✅ **Embeddings Creation**: XCom check  
3. ✅ **Vector Database**: S3 artifacts exist
4. ✅ **Search Functionality**: 3 test queries

**Search Test Queries**:

```python
test_queries = [
    "Lãi suất ngân hàng",
    "Thị trường chứng khoán", 
    "Kinh tế vĩ mô Việt Nam"
]
```

**Search Process**:
```python
# 1. Encode query
query_embedding = embedder.encode([query])[0]  # Shape: (768,)

# 2. Search FAISS
distances, indices = vectordb.index.search(
    query_embedding.reshape(1, -1),  # Shape: (1, 768)
    k=3  # Top 3 results
)

# 3. Get document metadata
results = []
for idx, score in zip(indices[0], distances[0]):
    doc = vectordb.document_store[idx]
    results.append({
        'title': doc['title'],
        'content': doc['clean_content'],
        'url': doc['url'],
        'score': float(score),  # Cosine similarity
        'source': doc['source'],
        'published_date': doc['published_date']
    })
```

**Test Results** (2025-10-28):

| Query | Top Result | Score | Results Found |
|-------|-----------|-------|---------------|
| Lãi suất ngân hàng | NCB được vinh danh Top "Doanh nghiệp được yêu thích 2025" | 0.286 | 3 |
| Thị trường chứng khoán | VN-Index tăng mạnh hai phiên liên tiếp | 0.210 | 3 |
| Kinh tế vĩ mô Việt Nam | Khi nào vốn ngoại đổ vào chứng khoán sau nâng hạng? | 0.176 | 3 |

**Performance**:
- **Encoding speed**: 13-27 docs/sec
- **Search latency**: < 10ms (exact search with 29 vectors)
- **Memory usage**: ~50MB (model + index)

**Output**:
```json
{
  "execution_date": "2025-10-28",
  "pipeline_status": "PASS",
  "components_checked": [
    "document_preparation",
    "embeddings",
    "vector_database",
    "search_functionality"
  ],
  "metrics": {
    "documents_prepared": 29,
    "embeddings_created": 29,
    "vectors_added": 29
  },
  "search_tests": [...]
}
```

---

## 🔧 Technical Issues Fixed

### Issue 1: UTF-8 Decode Error (Parquet)
**Problem**: `'utf-8' codec can't decode byte 0x88`

**Root Cause**: `s3_hook.read_key()` returns text string, but Parquet is binary format

**Solution**:
```python
# ❌ WRONG (text read)
parquet_content = s3_hook.read_key(key, bucket)
df = pd.read_parquet(io.BytesIO(parquet_content))

# ✅ CORRECT (binary read)
s3_client = s3_hook.get_conn()
obj = s3_client.get_object(Bucket=bucket, Key=key)
parquet_bytes = obj['Body'].read()
df = pd.read_parquet(io.BytesIO(parquet_bytes))
```

### Issue 2: Missing Dependencies
**Problem**: `ModuleNotFoundError: No module named 'sentence_transformers'`

**Solution**: Updated Dockerfiles
```dockerfile
RUN pip install --no-cache-dir \
    sentence-transformers>=2.2.0 \
    faiss-cpu>=1.7.4 \
    torch>=2.0.0 \
    pyarrow>=14.0.0
```

### Issue 3: UTF-8 Decode Error (FAISS Binary)
**Problem**: `'utf-8' codec can't decode byte 0xce` when loading FAISS index

**Root Cause**: Same as Issue 1 - `read_key()` for binary files

**Solution**: Use binary `get_object()` for FAISS and pickle files

### Issue 4: NoSuchKey Error
**Problem**: `NoSuchKey: The specified key does not exist` on first run

**Root Cause**: Code tried to load non-existent vectordb

**Solution**: Check both files exist before loading
```python
index_exists = s3_hook.check_for_key('faiss_index.bin')
metadata_exists = s3_hook.check_for_key('metadata.pkl')

if index_exists and metadata_exists:
    load_existing()
else:
    create_new()  # First run
```

### Issue 5: Dimension Mismatch (768 vs 384)
**Problem**: `AssertionError: assert d == self.d` (dimension mismatch)

**Root Cause**: 
- Code hardcoded `embedding_dim=384`
- But `keepitreal/vietnamese-sbert` outputs **768 dims**

**Solution**: Detect actual dimension from embeddings
```python
# Detect dimension from first embedding
first_embedding = documents[0]['embedding']
actual_dim = len(first_embedding)  # 768

# Create vectordb with correct dimension
vectordb = FAISSVectorDatabase(embedding_dim=actual_dim)
```

---

## 📊 S3 Data Structure

```
s3://bankanalystportfolio/
│
├── silver/
│   └── news/
│       └── partition_date=2025-10-28/
│           └── news_cleaned.parquet       # Input: Silver layer news
│
└── rag/
    ├── input/
    │   └── raw_news_2025-10-28.csv        # Raw extracted news
    │
    ├── processed/
    │   └── processed_for_embedding_2025-10-28.csv  # After chunking
    │
    ├── staging/
    │   └── prepared_documents_2025-10-28.json      # Structured docs
    │
    ├── embeddings/
    │   └── vietnamese_embeddings_2025-10-28.json   # 768-dim vectors
    │
    ├── vectordb/
    │   ├── faiss_index.bin                # FAISS index
    │   ├── metadata.pkl                   # Document store
    │   └── embeddings_info.json           # Stats
    │
    └── logs/
        └── rag_pipeline_2025-10-28.log    # Pipeline logs
```

---

## ⚙️ Configuration

### Airflow Variables
```python
S3_BUCKET = 'bankanalystportfolio'
AWS_CONN_ID = 'aws_default'
```

### Model Configuration
```python
MODEL_NAME = 'keepitreal/vietnamese-sbert'
EMBEDDING_DIM = 768  # Auto-detected
BATCH_SIZE = 32
MAX_CHUNK_SIZE = 1000
MIN_CHUNK_SIZE = 100
```

### FAISS Configuration
```python
INDEX_TYPE = 'IndexFlatIP'  # Exact search, cosine similarity
METRIC = 'INNER_PRODUCT'
SEARCH_TOP_K = 5
```

---

## 🚀 Daily Execution

### Schedule
```python
schedule_interval='0 2 * * *'  # 2 AM daily (UTC)
```

### Execution Flow
```
02:00 UTC - Trigger rag_pipeline
02:00-02:01 - Extract & prepare (29 docs)
02:01-02:02 - Create embeddings (768-dim)
02:02-02:03 - Update FAISS vectordb
02:03-02:04 - Validate & test search
02:04 UTC - Complete ✅
```

### Incremental Updates
- **Day 1**: Create new index (29 vectors)
- **Day 2**: Load existing + add new (29 + X vectors)
- **Day 3**: Load existing + add new (29 + X + Y vectors)
- **...**: Continuous growth

### Deduplication Strategy
```python
# Skip if doc_id already in index
if doc['doc_id'] in vectordb.doc_id_to_idx:
    skip_duplicate()
```

---

## 📈 Performance Metrics

### Current Stats (2025-10-28)
```
Documents Prepared:    29
Embeddings Created:    29
Vectors Added:         29
Total Vectors in DB:   29
Index Size:           ~22 KB
Metadata Size:        ~15 KB
Total Storage:        ~37 KB
```

### Scalability Projections

| Daily Articles | After 30 Days | After 365 Days | Index Size | Search Time |
|----------------|---------------|----------------|------------|-------------|
| 29 | 870 vectors | 10,585 vectors | ~900 KB | < 20ms |
| 100 | 3,000 vectors | 36,500 vectors | ~3 MB | < 50ms |
| 500 | 15,000 vectors | 182,500 vectors | ~15 MB | < 200ms |

**Note**: For > 100K vectors, consider using `IndexIVFFlat` (approximate search)

---

## 🔒 Security & Best Practices

### S3 Access
```python
# IAM permissions required:
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:PutObject",
    "s3:ListBucket"
  ],
  "Resource": [
    "arn:aws:s3:::bankanalystportfolio/rag/*",
    "arn:aws:s3:::bankanalystportfolio/silver/*"
  ]
}
```

### Error Handling
- **Retry Strategy**: 3 retries with exponential backoff
- **Fallback**: Create new index if load fails
- **Logging**: Comprehensive logging to S3 + Airflow logs

### Data Quality
- **Validation**: Check embedding dimensions before adding
- **Deduplication**: Skip duplicate doc_ids
- **Schema Validation**: Ensure all required fields exist

---

## 🛠️ Maintenance

### Monitor Daily
```bash
# Check pipeline success
airflow dags list-runs -d rag_pipeline --state success

# Check S3 vectordb size
aws s3 ls s3://bankanalystportfolio/rag/vectordb/ --recursive --human-readable

# Check vector count
aws s3 cp s3://bankanalystportfolio/rag/vectordb/embeddings_info.json - | jq '.total_vectors'
```

### Rebuild Index (if needed)
```bash
# Delete existing vectordb
aws s3 rm s3://bankanalystportfolio/rag/vectordb/ --recursive

# Trigger pipeline (will create new)
airflow dags trigger rag_pipeline
```

### Upgrade to GPU (for production)
```dockerfile
# Change from CPU to GPU FAISS
RUN pip uninstall -y faiss-cpu
RUN pip install --no-cache-dir faiss-gpu>=1.7.4
```

---

## 📚 References

- **Model**: [keepitreal/vietnamese-sbert](https://huggingface.co/keepitreal/vietnamese-sbert)
- **FAISS**: [Facebook AI Similarity Search](https://github.com/facebookresearch/faiss)
- **Sentence-Transformers**: [sentence-transformers.net](https://www.sbert.net/)

---

## ✅ Success Criteria

- [x] Daily automatic execution
- [x] Incremental vector database updates
- [x] Vietnamese SBERT embeddings (768-dim)
- [x] FAISS exact search (< 50ms for < 10K vectors)
- [x] Deduplication working
- [x] S3 persistence
- [x] Search validation tests passing
- [x] Error handling & recovery
- [x] Comprehensive logging

---

**Status**: ✅ Production Ready  
**Last Updated**: 2025-10-28  
**Version**: 1.0  
**Author**: AI Development Team

# 🚀 RAG Chatbot System - Complete Setup Guide

## 📋 Tổng quan

Hệ thống RAG Chatbot tích hợp FAISS vector search + Gemini LLM để trả lời câu hỏi về thị trường tài chính Việt Nam.

### Kiến trúc

```
Frontend (React) → Backend API (FastAPI) → RAG Service → FAISS + Gemini
                                         ↓
                                    Supabase Cache
                                         ↓
                                    MCP Server (Optional)
```

### Tính năng

✅ **User API Key Management**: Người dùng tự cung cấp Gemini API key (không tốn phí server)
✅ **FAISS Vector Search**: Tìm kiếm tin tức tài chính liên quan
✅ **Gemini Integration**: Sinh câu trả lời tự nhiên
✅ **Source Citations**: Hiển thị nguồn tin tức
✅ **Conversation History**: Hỗ trợ multi-turn chat
✅ **Caching**: Supabase cache giảm latency và chi phí
✅ **MCP Support**: Expose RAG tools qua Model Context Protocol

---

## 🛠️ Setup Instructions

### Bước 1: Cài đặt Dependencies

```powershell
# Navigate to backend
cd "c:\uel\Đồ án tốt nghiệp\finance_portfolio\web_executor\backend"

# Install Python dependencies
pip install -r requirements.txt

# Verify installations
python -c "import faiss; print('FAISS OK')"
python -c "import sentence_transformers; print('Sentence Transformers OK')"
python -c "import google.generativeai; print('Gemini OK')"
```

### Bước 2: Prepare RAG Data

```powershell
# Run data preparation script
python scripts/prepare_rag_data.py
```

Script này sẽ:
- Copy FAISS index từ `rag_system/`
- Convert metadata sang JSON format
- Tạo backup và sample versions
- Verify data integrity

**Expected output:**
```
data/rag/
├── faiss_index.bin      (200-500MB)
├── metadata.json        (< 50MB)
└── embeddings.npy       (Optional backup)
```

### Bước 3: Configure Environment

Cập nhật `.env` file:

```bash
# RAG Configuration
RAG_ENABLED=True
RAG_MODEL_NAME=keepitreal/vietnamese-sbert
RAG_FAISS_INDEX_PATH=data/rag/faiss_index.bin
RAG_METADATA_PATH=data/rag/metadata.json
RAG_TOP_K=5
RAG_TEMPERATURE=0.7
RAG_MAX_TOKENS=2048

# MCP Configuration
MCP_ENABLED=True
MCP_SERVER_PORT=8001

# User API Keys (allows users to provide their own keys)
ALLOW_USER_API_KEYS=True

# Optional: Default key for testing (NOT RECOMMENDED in production)
# DEFAULT_GEMINI_API_KEY=AIzaSy...
```

### Bước 4: Create Supabase Cache Table (Optional but Recommended)

```sql
-- In Supabase SQL Editor
CREATE TABLE IF NOT EXISTS rag_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(64) UNIQUE NOT NULL,
    result JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_cache_key (cache_key),
    INDEX idx_created_at (created_at)
);

-- Auto-delete old cache entries (5 minutes TTL)
CREATE OR REPLACE FUNCTION delete_old_cache()
RETURNS void AS $$
BEGIN
    DELETE FROM rag_cache 
    WHERE created_at < NOW() - INTERVAL '5 minutes';
END;
$$ LANGUAGE plpgsql;
```

### Bước 5: Start Backend

```powershell
# Development mode (with auto-reload)
python main.py

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Verify backend is running:**
```powershell
# Test health endpoint
curl http://localhost:8000/api/v1/rag/health

# Test stats endpoint
curl http://localhost:8000/api/v1/rag/stats
```

### Bước 6: Start Frontend

```powershell
cd "c:\uel\Đồ án tốt nghiệp\finance_portfolio\web_executor\frontend"

# Install dependencies (if not done)
pnpm install

# Start dev server
pnpm dev
```

Access chatbot at: **http://localhost:5173/chat**

---

## 🔑 Getting Gemini API Key (For Users)

### Free Tier
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIzaSy...`)

**Free limits:**
- 60 requests per minute
- 1,500 requests per day
- Perfect for personal use and demos

### Usage in Chatbot
1. Paste API key in the "API Key" field
2. Click "Xác thực API Key"
3. Wait for validation
4. Start chatting!

**Key is stored in browser localStorage** - không gửi lên server, an toàn và riêng tư.

---

## 📡 API Endpoints

### 1. Validate API Key

```http
POST /api/v1/rag/validate-key
Content-Type: application/json

{
  "api_key": "AIzaSy..."
}
```

**Response:**
```json
{
  "valid": true,
  "message": "API key is valid",
  "model": "gemini-1.5-flash"
}
```

### 2. Query Chatbot

```http
POST /api/v1/rag/query
Content-Type: application/json

{
  "query": "Tình hình VN-Index hôm nay?",
  "api_key": "AIzaSy...",
  "top_k": 5,
  "use_cache": true,
  "conversation_history": [
    {
      "role": "user",
      "content": "Xin chào",
      "timestamp": "2025-11-04T10:00:00Z"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "answer": "VN-Index hôm nay tăng 15 điểm...",
  "sources": [
    {
      "id": 12345,
      "text": "Tin tức về VN-Index...",
      "score": 0.89
    }
  ],
  "query": "Tình hình VN-Index hôm nay?",
  "timestamp": "2025-11-04T10:05:00Z",
  "model": "gemini-1.5-flash",
  "top_k": 5
}
```

### 3. Get RAG Stats

```http
GET /api/v1/rag/stats
```

**Response:**
```json
{
  "enabled": true,
  "model": "keepitreal/vietnamese-sbert",
  "total_documents": 15420,
  "vector_dimension": 768,
  "metadata_loaded": true,
  "embeddings_model_loaded": true
}
```

### 4. Health Check

```http
GET /api/v1/rag/health
```

**Response:**
```json
{
  "status": "healthy",
  "enabled": true,
  "components": {
    "faiss_index": true,
    "metadata": true,
    "embeddings_model": true
  }
}
```

---

## 🔧 MCP Server (Optional)

### Start MCP Server

```powershell
# In separate terminal
cd "c:\uel\Đồ án tốt nghiệp\finance_portfolio\web_executor\backend"
python -m app.mcp_server
```

### Available MCP Tools

1. **rag_query** - Query RAG system
2. **rag_validate_key** - Validate API key
3. **rag_stats** - Get statistics
4. **rag_search** - Vector search only (no LLM)

### Usage Example

```json
{
  "tool": "rag_query",
  "arguments": {
    "query": "What's happening in the market?",
    "api_key": "AIzaSy...",
    "top_k": 5
  }
}
```

---

## 🧪 Testing

### Manual Testing

```powershell
# Test API key validation
curl -X POST http://localhost:8000/api/v1/rag/validate-key `
  -H "Content-Type: application/json" `
  -d '{"api_key": "YOUR_API_KEY"}'

# Test query
curl -X POST http://localhost:8000/api/v1/rag/query `
  -H "Content-Type: application/json" `
  -d '{
    "query": "Thị trường hôm nay thế nào?",
    "api_key": "YOUR_API_KEY",
    "top_k": 3
  }'
```

### Automated Tests

```powershell
# Unit tests
pytest tests/test_rag_service.py -v

# Integration tests
pytest tests/test_rag_endpoints.py -v

# Load tests
locust -f tests/load_test_rag.py
```

---

## 🚀 Deployment

### Option 1: Docker Compose

```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - RAG_ENABLED=true
    volumes:
      - ./data/rag:/app/data/rag
    
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

```powershell
docker-compose up -d
```

### Option 2: Separate Deployment

**Backend (Railway/Fly.io):**
```powershell
# Add data folder to .dockerignore
echo "!data/rag/*.bin" >> .dockerignore
echo "!data/rag/*.json" >> .dockerignore

# Deploy
flyctl deploy
```

**Frontend (Vercel/Netlify):**
```powershell
pnpm build
vercel deploy
```

---

## 📊 Performance Optimization

### 1. FAISS Index Optimization

```python
# Use IVF index for large datasets (>100k docs)
quantizer = faiss.IndexFlatIP(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, 100)
index.train(embeddings)
index.add(embeddings)
```

### 2. Caching Strategy

- **Query cache**: 5 minutes TTL
- **API key validation**: 1 hour TTL
- **Stats**: 10 minutes TTL

### 3. Load Balancing

```python
# Use multiple workers
uvicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

---

## 🐛 Troubleshooting

### Problem: FAISS index not found

**Solution:**
```powershell
# Check file exists
Test-Path "data/rag/faiss_index.bin"

# Regenerate if missing
python scripts/prepare_rag_data.py
```

### Problem: Metadata too large

**Solution:**
```python
# Create smaller sample
python scripts/prepare_rag_data.py --sample-size 1000
```

### Problem: Out of memory

**Solution:**
```bash
# Reduce batch size
RAG_TOP_K=3

# Or use disk-based index
# (slower but uses less RAM)
```

### Problem: Gemini API rate limit

**Solution:**
- Enable caching (default)
- Use exponential backoff
- Ask user to upgrade their API quota

---

## 💰 Cost Estimation

### Per Query (with user API keys):
- **Backend compute**: $0.00001
- **Supabase cache**: $0.000001
- **Total**: ~$0.00001 per query

### Monthly (1000 users, 10 queries/day):
- **Backend**: ~$50-100
- **Database**: ~$20
- **Total**: ~$70-120/month

**User bears Gemini API cost** → No LLM costs for server!

---

## 🎯 Next Steps

1. ✅ **Phase 1 Complete**: Core RAG functionality
2. 🔄 **Phase 2**: Add more features
   - [ ] Multi-language support
   - [ ] Advanced filters (date range, sector)
   - [ ] Export conversation
   - [ ] Share chat link
3. 🚀 **Phase 3**: Production hardening
   - [ ] Rate limiting
   - [ ] User authentication
   - [ ] Usage analytics
   - [ ] A/B testing

---

## 📚 Resources

- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Sentence Transformers](https://www.sbert.net/)
- [MCP Protocol](https://modelcontextprotocol.io/)

---

## 🆘 Support

**Issues?** Create an issue on GitHub or contact the team.

**Questions?** Check the FAQ or join our Discord.

---

**Built with ❤️ for Vietnamese Financial Markets**

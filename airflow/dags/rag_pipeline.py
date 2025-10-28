"""
RAG Pipeline DAG - Production-ready Vietnamese SBERT & FAISS
Improvements from analysis:
- Real Vietnamese SBERT embeddings (keepitreal/vietnamese-sbert)
- Real FAISS vector database operations
- Document chunking for better context
- Deduplication handling
- Search/retrieval capabilities
- Comprehensive validation & testing

Schedule: Triggered by master_pipeline after gold layer
Author: Finance Portfolio System
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import logging
import os

# Default arguments
default_args = {
    'owner': 'finance_portfolio',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 27),
    'email_on_failure': False,
    'email_on_retry': False,
    'retry_delay': timedelta(minutes=5),
    'retries': 2,
}

# DAG definition
dag = DAG(
    'rag_pipeline',
    default_args=default_args,
    description='Production RAG Pipeline with Real Vietnamese SBERT and FAISS',
    schedule_interval=None,  # Triggered by master_pipeline
    catchup=False,
    max_active_runs=1,
    tags=['rag', 'vietnamese', 'sbert', 'faiss', 'production']
)

def extract_and_prepare_documents(**context):
    """
    Extract processed news and prepare documents with chunking
    Improvements:
    - Smart chunking for long documents
    - Metadata enrichment
    - Deduplication check
    """
    try:
        from datetime import datetime
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        logging.info(f"📰 Extracting and preparing documents for RAG - {date_str}")
        
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import pandas as pd
        import json
        import sys
        
        # Add utils to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))
        from embedding_utils import prepare_documents_for_embedding
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        # Read processed news from silver layer (Parquet format)
        news_file_key = f"silver/news/partition_date={date_str}/news_cleaned.parquet"
        
        if not s3_hook.check_for_key(key=news_file_key, bucket_name=bucket_name):
            logging.warning(f"⚠️ No processed news found for {date_str}")
            logging.info(f"   Expected: {news_file_key}")
            context['task_instance'].xcom_push(key='documents_prepared', value=0)
            return {'documents_prepared': 0, 'execution_date': date_str}
        
        # Load news data from Parquet (read as binary to avoid utf-8 decode errors)
        logging.info(f"📥 Reading Parquet: {news_file_key}")
        import io
        # Use S3 client get_object to read binary parquet bytes
        s3_client = s3_hook.get_conn()
        try:
            obj = s3_client.get_object(Bucket=bucket_name, Key=news_file_key)
            parquet_bytes = obj['Body'].read()
        except Exception as e:
            logging.error(f"❌ Failed to download parquet from S3: {e}")
            context['task_instance'].xcom_push(key='documents_prepared', value=0)
            return {'documents_prepared': 0, 'execution_date': date_str}

        # Read parquet from bytes buffer
        news_df = pd.read_parquet(io.BytesIO(parquet_bytes))
        
        logging.info(f"📄 Loaded {len(news_df)} news articles from Silver layer")
        
        # ===== MAP SILVER SCHEMA TO RAG SCHEMA =====
        # Silver columns: id, data_date, source, title, content, link, _ingested_at_utc, partition_date
        # RAG needs: clean_content (for embedding), url, title, source
        
        # Rename columns to match RAG expectations
        column_mapping = {
            'content': 'clean_content',  # Silver 'content' → RAG 'clean_content' 
            'link': 'url',                # Silver 'link' → RAG 'url'
            'data_date': 'published_date' # Silver 'data_date' → RAG 'published_date'
        }
        
        news_df = news_df.rename(columns=column_mapping)
        
        # Add content_length
        news_df['content_length'] = news_df['clean_content'].fillna('').str.len()
        
        # Add basic categorization (simple keyword-based since Gold layer does NLP)
        def categorize_news(title, content):
            """Simple keyword-based categorization"""
            text = f"{title} {content}".lower()
            
            if any(word in text for word in ['ngân hàng', 'bank', 'tín dụng', 'cho vay', 'lãi suất']):
                return 'BANKING'
            elif any(word in text for word in ['chứng khoán', 'cổ phiếu', 'stock', 'vnindex', 'thị trường']):
                return 'FINANCE'
            elif any(word in text for word in ['gdp', 'kinh tế', 'xuất khẩu', 'nhập khẩu', 'lạm phát']):
                return 'ECONOMY'
            else:
                return 'FINANCE'  # Default
        
        news_df['topic_category'] = news_df.apply(
            lambda row: categorize_news(
                row.get('title', ''), 
                row.get('clean_content', '')
            ), 
            axis=1
        )
        
        # Add basic sentiment (simple rule-based since Gold layer does proper NLP)
        def basic_sentiment(title, content):
            """Simple rule-based sentiment"""
            text = f"{title} {content}".lower()
            
            positive_words = ['tăng trưởng', 'tích cực', 'khả quan', 'tăng', 'phục hồi', 'cải thiện']
            negative_words = ['giảm', 'khó khăn', 'suy thoái', 'lo ngại', 'rủi ro', 'thiệt hại']
            
            pos_count = sum(1 for word in positive_words if word in text)
            neg_count = sum(1 for word in negative_words if word in text)
            
            if pos_count > neg_count:
                return 'POSITIVE'
            elif neg_count > pos_count:
                return 'NEGATIVE'
            else:
                return 'NEUTRAL'
        
        news_df['sentiment_basic'] = news_df.apply(
            lambda row: basic_sentiment(
                row.get('title', ''), 
                row.get('clean_content', '')
            ), 
            axis=1
        )
        
        logging.info(f"✅ Mapped Silver schema to RAG schema")
        logging.info(f"   Columns: {list(news_df.columns)}")
        
        # Filter for quality content
        filtered_df = news_df[
            (news_df['content_length'] >= 100) &  # Minimum 100 characters
            (news_df['clean_content'].notna()) &   # Has content
            (news_df['clean_content'].str.strip() != '')  # Not empty
        ].copy()
        
        if len(filtered_df) == 0:
            logging.warning("⚠️ No suitable articles after filtering")
            context['task_instance'].xcom_push(key='documents_prepared', value=0)
            return {'documents_prepared': 0, 'execution_date': date_str}
        
        logging.info(f"✅ Filtered to {len(filtered_df)} quality articles")
        
        # ===== SAVE RAW INPUT TO S3 =====
        # Save original filtered news as raw input for RAG
        raw_csv = filtered_df.to_csv(index=False)
        raw_input_key = f"rag/input/raw_news_{date_str}.csv"
        
        s3_hook.load_string(
            string_data=raw_csv,
            key=raw_input_key,
            bucket_name=bucket_name,
            replace=True
        )
        logging.info(f"💾 Saved raw input: {raw_input_key}")
        
        # Prepare documents with chunking
        filtered_df['doc_id'] = filtered_df['url'].apply(lambda x: str(hash(x))[-8:])
        filtered_df['doc_date'] = date_str
        filtered_df['doc_category'] = filtered_df['topic_category']
        filtered_df['doc_sentiment'] = filtered_df['sentiment_basic']
        filtered_df['doc_source'] = filtered_df['source'].fillna('Unknown')
        
        # Apply smart chunking
        documents = prepare_documents_for_embedding(
            filtered_df,
            chunking_method='sentences',  # Chunk long documents
            max_chunk_size=512,  # Optimal for SBERT
            add_metadata_to_text=True  # Add category context
        )
        
        logging.info(f"📝 Prepared {len(documents)} document chunks (from {len(filtered_df)} articles)")
        
        # ===== SAVE PROCESSED DATA FOR EMBEDDING =====
        # Save processed documents ready for embedding as CSV
        processed_df = pd.DataFrame([
            {
                'doc_id': doc['doc_id'],
                'parent_doc_id': doc['parent_doc_id'],
                'chunk_index': doc['chunk_index'],
                'total_chunks': doc['total_chunks'],
                'title': doc['title'],
                'text': doc['text'],
                'url': doc['url'],
                'doc_date': doc['doc_date'],
                'doc_category': doc['doc_category'],
                'doc_sentiment': doc['doc_sentiment'],
                'doc_source': doc['doc_source'],
                'content_length': doc['content_length']
            }
            for doc in documents
        ])
        
        processed_csv = processed_df.to_csv(index=False)
        processed_key = f"rag/processed/processed_for_embedding_{date_str}.csv"
        
        s3_hook.load_string(
            string_data=processed_csv,
            key=processed_key,
            bucket_name=bucket_name,
            replace=True
        )
        logging.info(f"💾 Saved processed data: {processed_key}")
        
        # Save prepared documents as JSON (for internal use)
        docs_json = json.dumps(documents, ensure_ascii=False, indent=2)
        docs_key = f"rag/staging/prepared_documents_{date_str}.json"
        
        s3_hook.load_string(
            string_data=docs_json,
            key=docs_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        # Save metadata
        metadata = {
            'processing_date': date_str,
            'total_articles': len(filtered_df),
            'total_chunks': len(documents),
            'avg_chunks_per_article': len(documents) / len(filtered_df),
            'categories': filtered_df['doc_category'].value_counts().to_dict(),
            'sentiments': filtered_df['doc_sentiment'].value_counts().to_dict(),
            '_created_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'
        }
        
        metadata_key = f"rag/metadata/preparation_meta_{date_str}.json"
        s3_hook.load_string(
            string_data=json.dumps(metadata, ensure_ascii=False, indent=2),
            key=metadata_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        # Push to XCom for next task
        context['task_instance'].xcom_push(key='documents_prepared', value=len(documents))
        
        result = {
            'documents_prepared': len(documents),
            'articles_processed': len(filtered_df),
            'execution_date': date_str
        }
        
        logging.info(f"✅ Document preparation completed: {result}")
        return result
        
    except Exception as e:
        logging.error(f"💥 Document preparation failed: {str(e)}")
        raise

def create_real_embeddings(**context):
    """
    Create REAL Vietnamese SBERT embeddings
    Uses: keepitreal/vietnamese-sbert model
    """
    try:
        from datetime import datetime
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        logging.info(f"🤖 Creating REAL Vietnamese SBERT embeddings - {date_str}")
        
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import json
        import numpy as np
        import sys
        
        # Add utils to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))
        from embedding_utils import VietnameseEmbedder
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        # Load prepared documents
        docs_key = f"rag/staging/prepared_documents_{date_str}.json"
        
        if not s3_hook.check_for_key(key=docs_key, bucket_name=bucket_name):
            logging.warning("⚠️ No prepared documents found")
            context['task_instance'].xcom_push(key='embeddings_created', value=0)
            return {'embeddings_created': 0, 'execution_date': date_str}
        
        docs_content = s3_hook.read_key(key=docs_key, bucket_name=bucket_name)
        documents = json.loads(docs_content)
        
        if len(documents) == 0:
            logging.warning("⚠️ No documents to embed")
            context['task_instance'].xcom_push(key='embeddings_created', value=0)
            return {'embeddings_created': 0, 'execution_date': date_str}
        
        logging.info(f"📝 Creating embeddings for {len(documents)} document chunks")
        
        # Initialize Vietnamese SBERT embedder
        embedder = VietnameseEmbedder(model_name="keepitreal/vietnamese-sbert")
        embedder.load_model()
        
        # Extract texts
        texts = [doc['text'] for doc in documents]
        
        # Create embeddings in batches
        embeddings = embedder.encode_texts(
            texts,
            batch_size=32,
            show_progress=True
        )
        
        logging.info(f"✅ Created {len(embeddings)} embeddings (shape: {embeddings.shape})")
        
        # Prepare embedding data for storage
        embedding_data = {
            'processing_date': date_str,
            'model_name': embedder.model_name,
            'embedding_dimension': embedder.embedding_dim,
            'total_documents': len(documents),
            'documents': []
        }
        
        # Add embeddings to documents
        for doc, embedding in zip(documents, embeddings):
            doc_with_embedding = doc.copy()
            doc_with_embedding['embedding'] = embedding.tolist()
            embedding_data['documents'].append(doc_with_embedding)
        
        # Save embeddings
        embeddings_key = f"rag/embeddings/vietnamese_embeddings_{date_str}.json"
        s3_hook.load_string(
            string_data=json.dumps(embedding_data, ensure_ascii=False),  # No indent to save space
            key=embeddings_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        # Save embedding summary
        summary = {
            'processing_date': date_str,
            'total_embeddings': len(embeddings),
            'embedding_dimension': embedder.embedding_dim,
            'model_used': embedder.model_name,
            'embedding_shape': list(embeddings.shape),
            '_created_at_utc': datetime.utcnow().isoformat() + 'Z'
        }
        
        summary_key = f"rag/metadata/embeddings_summary_{date_str}.json"
        s3_hook.load_string(
            string_data=json.dumps(summary, ensure_ascii=False, indent=2),
            key=summary_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        # Push to XCom
        context['task_instance'].xcom_push(key='embeddings_created', value=len(embeddings))
        
        result = {
            'embeddings_created': len(embeddings),
            'embedding_dimension': embedder.embedding_dim,
            'model_used': embedder.model_name,
            'execution_date': date_str
        }
        
        logging.info(f"✅ Real Vietnamese embeddings created: {result}")
        return result
        
    except Exception as e:
        logging.error(f"💥 Embedding creation failed: {str(e)}")
        raise

def update_faiss_vectordb(**context):
    """
    Update REAL FAISS vector database
    With deduplication and proper indexing
    """
    try:
        from datetime import datetime
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        logging.info(f"🗄️ Updating FAISS vector database - {date_str}")
        
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import json
        import numpy as np
        import sys
        
        # Add utils to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))
        from vectordb_utils import create_s3_vectordb_manager, save_vectordb_to_s3
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        # Load embeddings
        embeddings_key = f"rag/embeddings/vietnamese_embeddings_{date_str}.json"
        
        if not s3_hook.check_for_key(key=embeddings_key, bucket_name=bucket_name):
            logging.warning("⚠️ No embeddings found")
            context['task_instance'].xcom_push(key='vectors_added', value=0)
            return {'vectors_added': 0, 'execution_date': date_str}
        
        embeddings_content = s3_hook.read_key(key=embeddings_key, bucket_name=bucket_name)
        embeddings_data = json.loads(embeddings_content)
        
        documents = embeddings_data.get('documents', [])
        if len(documents) == 0:
            logging.warning("⚠️ No documents to index")
            context['task_instance'].xcom_push(key='vectors_added', value=0)
            return {'vectors_added': 0, 'execution_date': date_str}
        
        logging.info(f"📊 Processing {len(documents)} documents for FAISS indexing")
        
        # Prepare vectors and metadata
        embeddings_array = np.array([doc['embedding'] for doc in documents], dtype='float32')
        
        # Auto-detect embedding dimension from actual data
        actual_embedding_dim = embeddings_array.shape[1] if len(embeddings_array.shape) == 2 else len(embeddings_array[0])
        logging.info(f"🔍 Detected embedding dimension: {actual_embedding_dim}")
        logging.info(f"🔍 Embeddings array shape: {embeddings_array.shape}")
        
        # Load or create vector database with correct dimension
        vectordb = create_s3_vectordb_manager(
            s3_hook=s3_hook,
            bucket_name=bucket_name,
            vectordb_prefix="rag/vectordb",
            embedding_dim=actual_embedding_dim  # Use detected dimension
        )
        
        logging.info(f"🔍 VectorDB initialized with dimension: {vectordb.embedding_dim}")
        
        # Validate dimensions match
        if len(embeddings_array.shape) != 2:
            raise ValueError(f"Embeddings must be 2D array, got shape: {embeddings_array.shape}")
        
        if embeddings_array.shape[1] != vectordb.embedding_dim:
            raise ValueError(
                f"Embedding dimension mismatch: got {embeddings_array.shape[1]}, "
                f"expected {vectordb.embedding_dim}"
            )
        
        # Document metadata (without embeddings to save memory)
        doc_metadata = []
        for doc in documents:
            meta = {k: v for k, v in doc.items() if k != 'embedding'}
            doc_metadata.append(meta)
        
        # Add to FAISS index (with deduplication)
        vectors_added = vectordb.add_vectors(
            embeddings=embeddings_array,
            documents=doc_metadata,
            check_duplicates=True  # Skip duplicates
        )
        
        logging.info(f"✅ Added {vectors_added} vectors to FAISS (skipped duplicates)")
        
        # Save updated database to S3
        save_vectordb_to_s3(
            vectordb=vectordb,
            s3_hook=s3_hook,
            bucket_name=bucket_name,
            vectordb_prefix="rag/vectordb"
        )
        
        # Get database stats
        stats = vectordb.get_stats()
        
        # ===== SAVE EMBEDDINGS INFO TO VECTORDB FOLDER =====
        # Create embeddings_info.json with comprehensive information
        embeddings_info = {
            'last_update': date_str,
            'last_update_utc': datetime.utcnow().isoformat() + 'Z',
            'model_name': 'keepitreal/vietnamese-sbert',
            'embedding_dimension': stats.get('embedding_dim', 384),
            'total_vectors': stats['total_vectors'],
            'vectors_added_today': vectors_added,
            'total_documents': stats.get('total_documents', 0),
            'unique_doc_ids': stats.get('unique_doc_ids', 0),
            'index_type': stats.get('index_type', 'IndexFlatIP'),
            'categories_distribution': stats.get('categories', {}),
            'sentiments_distribution': stats.get('sentiments', {}),
            'sources_distribution': stats.get('sources', {}),
            'vectordb_files': {
                'index': 'rag/vectordb/faiss_index.bin',
                'metadata': 'rag/vectordb/faiss_metadata.pkl',
                'info': 'rag/vectordb/embeddings_info.json'
            },
            'pipeline_version': '2.0',
            'description': 'Vietnamese financial news vector database using SBERT and FAISS'
        }
        
        embeddings_info_key = "rag/vectordb/embeddings_info.json"
        s3_hook.load_string(
            string_data=json.dumps(embeddings_info, ensure_ascii=False, indent=2),
            key=embeddings_info_key,
            bucket_name=bucket_name,
            replace=True
        )
        logging.info(f"💾 Saved embeddings info: {embeddings_info_key}")
        
        # Save database stats (legacy format for backward compatibility)
        stats['last_update'] = date_str
        stats['_updated_at_utc'] = datetime.utcnow().isoformat() + 'Z'
        
        stats_key = "rag/vectordb/database_stats.json"
        s3_hook.load_string(
            string_data=json.dumps(stats, ensure_ascii=False, indent=2),
            key=stats_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        # Push to XCom
        context['task_instance'].xcom_push(key='vectors_added', value=vectors_added)
        
        result = {
            'vectors_added': vectors_added,
            'total_vectors': stats['total_vectors'],
            'execution_date': date_str
        }
        
        logging.info(f"✅ FAISS vector database updated: {result}")
        return result
        
    except Exception as e:
        logging.error(f"💥 FAISS update failed: {str(e)}")
        raise

def validate_and_test_search(**context):
    """
    Validate RAG pipeline and test search functionality
    """
    try:
        from datetime import datetime
        import pandas as pd
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        logging.info(f"🔍 Validating RAG pipeline and testing search - {date_str}")
        
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import json
        import sys
        
        # Add utils to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))
        from vectordb_utils import create_s3_vectordb_manager
        from embedding_utils import VietnameseEmbedder
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        validation_results = {
            'execution_date': date_str,
            'pipeline_status': 'PASS',
            'components_checked': [],
            'errors': [],
            'warnings': [],
            'metrics': {},
            'search_tests': []
        }
        
        # Pull XCom data
        ti = context['task_instance']
        docs_prepared = ti.xcom_pull(key='documents_prepared', task_ids='extract_and_prepare_documents')
        embeddings_created = ti.xcom_pull(key='embeddings_created', task_ids='create_real_embeddings')
        vectors_added = ti.xcom_pull(key='vectors_added', task_ids='update_faiss_vectordb')
        
        # Validate pipeline steps
        if docs_prepared and docs_prepared > 0:
            validation_results['components_checked'].append('document_preparation')
            validation_results['metrics']['documents_prepared'] = docs_prepared
        else:
            validation_results['errors'].append("No documents prepared")
            validation_results['pipeline_status'] = 'FAIL'
        
        if embeddings_created and embeddings_created > 0:
            validation_results['components_checked'].append('embeddings')
            validation_results['metrics']['embeddings_created'] = embeddings_created
        else:
            validation_results['errors'].append("No embeddings created")
            validation_results['pipeline_status'] = 'FAIL'
        
        if vectors_added and vectors_added > 0:
            validation_results['components_checked'].append('vector_database')
            validation_results['metrics']['vectors_added'] = vectors_added
        else:
            validation_results['warnings'].append("No new vectors added (might be duplicates)")
        
        # Test search functionality
        try:
            logging.info("🔎 Testing search functionality...")
            
            # Load vector database
            vectordb = create_s3_vectordb_manager(
                s3_hook=s3_hook,
                bucket_name=bucket_name,
                vectordb_prefix="rag/vectordb"
            )
            
            # Initialize embedder for query
            embedder = VietnameseEmbedder(model_name="keepitreal/vietnamese-sbert")
            embedder.load_model()
            
            # Test queries
            test_queries = [
                "Lãi suất ngân hàng",
                "Thị trường chứng khoán",
                "Kinh tế vĩ mô Việt Nam"
            ]
            
            for query in test_queries:
                # Create query embedding
                query_embedding = embedder.encode_single(query)
                
                # Search
                results = vectordb.search(
                    query_embedding=query_embedding,
                    top_k=3
                )
                
                test_result = {
                    'query': query,
                    'results_found': len(results),
                    'top_result': results[0]['title'] if results else None,
                    'top_score': results[0]['similarity_score'] if results else None
                }
                
                validation_results['search_tests'].append(test_result)
                logging.info(f"✅ Search test: {query} -> {len(results)} results")
            
            validation_results['components_checked'].append('search_functionality')
            
        except Exception as search_error:
            validation_results['warnings'].append(f"Search test failed: {str(search_error)}")
            logging.warning(f"⚠️ Search test failed: {str(search_error)}")
        
        # Save validation results
        validation_results['_created_at_utc'] = datetime.utcnow().isoformat() + 'Z'
        validation_key = f"rag/metadata/validation_results_{date_str}.json"
        
        s3_hook.load_string(
            string_data=json.dumps(validation_results, ensure_ascii=False, indent=2),
            key=validation_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        # Log summary
        status_emoji = "✅" if validation_results['pipeline_status'] == 'PASS' else "❌"
        logging.info(f"{status_emoji} RAG pipeline validation: {validation_results['pipeline_status']}")
        logging.info(f"📊 Metrics: {validation_results['metrics']}")
        logging.info(f"� Search tests: {len(validation_results['search_tests'])} completed")
        
        return validation_results
        
    except Exception as e:
        logging.error(f"💥 Validation failed: {str(e)}")
        raise

# Task definitions
prepare_documents_task = PythonOperator(
    task_id='extract_and_prepare_documents',
    python_callable=extract_and_prepare_documents,
    dag=dag,
    retries=2,
    retry_delay=timedelta(minutes=5)
)

create_embeddings_task = PythonOperator(
    task_id='create_real_embeddings',
    python_callable=create_real_embeddings,
    dag=dag,
    retries=2,
    retry_delay=timedelta(minutes=5)
)

update_vectordb_task = PythonOperator(
    task_id='update_faiss_vectordb',
    python_callable=update_faiss_vectordb,
    dag=dag,
    retries=2,
    retry_delay=timedelta(minutes=5)
)

validate_task = PythonOperator(
    task_id='validate_and_test_search',
    python_callable=validate_and_test_search,
    dag=dag,
    retries=1,
    retry_delay=timedelta(minutes=2)
)

# Task dependencies
prepare_documents_task >> create_embeddings_task >> update_vectordb_task >> validate_task

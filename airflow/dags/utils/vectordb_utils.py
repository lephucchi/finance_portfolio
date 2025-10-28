"""
FAISS Vector Database utilities for Vietnamese financial news RAG
"""

import logging
import json
import pickle
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from datetime import datetime


class FAISSVectorDatabase:
    """FAISS vector database manager"""
    
    def __init__(self, embedding_dim: int = 384, index_type: str = "IndexFlatIP"):
        """
        Initialize FAISS database
        
        Args:
            embedding_dim: Dimension of embeddings
            index_type: FAISS index type
                - IndexFlatIP: Exact inner product search (cosine similarity with normalized vectors)
                - IndexFlatL2: Exact L2 distance search
                - IndexIVFFlat: Inverted file index (faster for large datasets)
        """
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.index = None
        self.document_store = []  # Store document metadata
        self.doc_id_to_idx = {}  # Map doc_id to vector index
        
    def create_index(self):
        """Create new FAISS index"""
        try:
            import faiss
            
            if self.index_type == "IndexFlatIP":
                # Inner product (for normalized vectors = cosine similarity)
                self.index = faiss.IndexFlatIP(self.embedding_dim)
            elif self.index_type == "IndexFlatL2":
                # L2 distance
                self.index = faiss.IndexFlatL2(self.embedding_dim)
            elif self.index_type == "IndexIVFFlat":
                # IVF index for faster search on large datasets
                quantizer = faiss.IndexFlatIP(self.embedding_dim)
                self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, 100)  # 100 clusters
            else:
                raise ValueError(f"Unknown index type: {self.index_type}")
            
            logging.info(f"✅ Created FAISS index: {self.index_type} (dim={self.embedding_dim})")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to create FAISS index: {str(e)}")
            raise
    
    def add_vectors(self, embeddings: np.ndarray, documents: List[Dict[str, Any]],
                   check_duplicates: bool = True) -> int:
        """
        Add vectors to FAISS index
        
        Args:
            embeddings: numpy array of shape (n_docs, embedding_dim)
            documents: List of document metadata dicts
            check_duplicates: Check and skip duplicate doc_ids
            
        Returns:
            Number of vectors added
        """
        if self.index is None:
            self.create_index()
        
        try:
            # Validate input
            if len(embeddings) != len(documents):
                raise ValueError("Number of embeddings must match number of documents")
            
            # Validate embedding dimensions
            if len(embeddings.shape) != 2:
                raise ValueError(f"Embeddings must be 2D array, got shape: {embeddings.shape}")
            
            if embeddings.shape[1] != self.embedding_dim:
                raise ValueError(
                    f"Embedding dimension mismatch: got {embeddings.shape[1]}, "
                    f"expected {self.embedding_dim}. "
                    f"Check your embedding model output."
                )
            
            logging.info(f"🔍 Input validation: {len(embeddings)} embeddings of dim {embeddings.shape[1]}")
            
            # Check for duplicates
            vectors_to_add = []
            docs_to_add = []
            
            for embedding, doc in zip(embeddings, documents):
                doc_id = doc.get('doc_id', '')
                
                if check_duplicates and doc_id in self.doc_id_to_idx:
                    logging.warning(f"⚠️ Skipping duplicate doc_id: {doc_id}")
                    continue
                
                vectors_to_add.append(embedding)
                docs_to_add.append(doc)
            
            if len(vectors_to_add) == 0:
                logging.warning("⚠️ No new vectors to add (all duplicates)")
                return 0
            
            # Convert to numpy array
            vectors_array = np.array(vectors_to_add, dtype='float32')
            
            logging.info(f"🔍 Adding {len(vectors_to_add)} vectors to FAISS (shape: {vectors_array.shape})")
            
            # Add to FAISS index
            start_idx = self.index.ntotal
            self.index.add(vectors_array)
            
            # Update document store and mapping
            for i, doc in enumerate(docs_to_add):
                vector_idx = start_idx + i
                doc_id = doc.get('doc_id', str(vector_idx))
                
                # Store document metadata
                doc_with_idx = doc.copy()
                doc_with_idx['vector_idx'] = vector_idx
                doc_with_idx['added_at'] = datetime.utcnow().isoformat() + 'Z'
                
                self.document_store.append(doc_with_idx)
                self.doc_id_to_idx[doc_id] = vector_idx
            
            logging.info(f"✅ Added {len(vectors_to_add)} vectors to FAISS index (total: {self.index.ntotal})")
            return len(vectors_to_add)
            
        except Exception as e:
            logging.error(f"❌ Failed to add vectors: {str(e)}")
            raise
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5,
              filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search similar documents
        
        Args:
            query_embedding: Query vector of shape (embedding_dim,)
            top_k: Number of results to return
            filters: Optional filters (category, sentiment, date_range, etc.)
            
        Returns:
            List of similar documents with scores
        """
        if self.index is None or self.index.ntotal == 0:
            logging.warning("⚠️ Index is empty")
            return []
        
        try:
            # Reshape query to (1, embedding_dim)
            query_vector = query_embedding.reshape(1, -1).astype('float32')
            
            # Search FAISS index
            # Get more results than needed for filtering
            search_k = min(top_k * 3, self.index.ntotal)
            distances, indices = self.index.search(query_vector, search_k)
            
            results = []
            for distance, idx in zip(distances[0], indices[0]):
                if idx == -1:  # FAISS returns -1 for empty results
                    continue
                
                # Get document metadata
                doc = self.document_store[idx].copy()
                doc['similarity_score'] = float(distance)
                
                # Apply filters if provided
                if filters:
                    if not self._matches_filters(doc, filters):
                        continue
                
                results.append(doc)
                
                if len(results) >= top_k:
                    break
            
            logging.info(f"🔍 Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logging.error(f"❌ Search failed: {str(e)}")
            raise
    
    def _matches_filters(self, doc: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if document matches filters"""
        # Category filter
        if 'categories' in filters:
            if doc.get('doc_category') not in filters['categories']:
                return False
        
        # Sentiment filter
        if 'sentiments' in filters:
            if doc.get('doc_sentiment') not in filters['sentiments']:
                return False
        
        # Date range filter
        if 'date_from' in filters:
            if doc.get('doc_date', '') < filters['date_from']:
                return False
        
        if 'date_to' in filters:
            if doc.get('doc_date', '') > filters['date_to']:
                return False
        
        # Minimum content length
        if 'min_length' in filters:
            if doc.get('content_length', 0) < filters['min_length']:
                return False
        
        return True
    
    def save_to_disk(self, index_path: str, metadata_path: str):
        """Save FAISS index and metadata to disk"""
        try:
            import faiss
            
            # Save FAISS index
            faiss.write_index(self.index, index_path)
            logging.info(f"💾 Saved FAISS index to {index_path}")
            
            # Save metadata
            metadata = {
                'embedding_dim': self.embedding_dim,
                'index_type': self.index_type,
                'total_vectors': self.index.ntotal,
                'document_store': self.document_store,
                'doc_id_to_idx': self.doc_id_to_idx,
                'saved_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            logging.info(f"💾 Saved metadata to {metadata_path}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to save: {str(e)}")
            raise
    
    def load_from_disk(self, index_path: str, metadata_path: str):
        """Load FAISS index and metadata from disk"""
        try:
            import faiss
            
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            logging.info(f"📂 Loaded FAISS index from {index_path} (vectors: {self.index.ntotal})")
            
            # Load metadata
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            
            self.embedding_dim = metadata['embedding_dim']
            self.index_type = metadata['index_type']
            self.document_store = metadata['document_store']
            self.doc_id_to_idx = metadata['doc_id_to_idx']
            
            logging.info(f"📂 Loaded metadata from {metadata_path}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to load: {str(e)}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if self.index is None:
            return {'status': 'empty', 'total_vectors': 0}
        
        stats = {
            'status': 'ready',
            'total_vectors': self.index.ntotal,
            'embedding_dim': self.embedding_dim,
            'index_type': self.index_type,
            'total_documents': len(self.document_store),
            'unique_doc_ids': len(self.doc_id_to_idx)
        }
        
        # Category distribution
        if self.document_store:
            categories = {}
            sentiments = {}
            sources = {}
            
            for doc in self.document_store:
                cat = doc.get('doc_category', 'UNKNOWN')
                sent = doc.get('doc_sentiment', 'UNKNOWN')
                src = doc.get('doc_source', 'Unknown')
                
                categories[cat] = categories.get(cat, 0) + 1
                sentiments[sent] = sentiments.get(sent, 0) + 1
                sources[src] = sources.get(src, 0) + 1
            
            stats['categories'] = categories
            stats['sentiments'] = sentiments
            stats['sources'] = sources
        
        return stats


def create_s3_vectordb_manager(s3_hook, bucket_name: str, 
                               vectordb_prefix: str = "rag/vectordb",
                               embedding_dim: int = None):
    """
    Create S3-based vector database manager
    
    Args:
        s3_hook: Airflow S3Hook instance
        bucket_name: S3 bucket name
        vectordb_prefix: S3 prefix for vector database files
        embedding_dim: Embedding dimension (auto-detect from existing index or use provided value)
        
    Returns:
        FAISSVectorDatabase instance
    """
    import tempfile
    import os
    
    # Initialize with provided dimension or default
    vectordb = FAISSVectorDatabase(embedding_dim=embedding_dim) if embedding_dim else FAISSVectorDatabase()
    
    # Check if index exists in S3
    index_key = f"{vectordb_prefix}/faiss_index.bin"
    metadata_key = f"{vectordb_prefix}/metadata.pkl"
    
    try:
        # Check if BOTH index and metadata exist
        index_exists = s3_hook.check_for_key(key=index_key, bucket_name=bucket_name)
        metadata_exists = s3_hook.check_for_key(key=metadata_key, bucket_name=bucket_name)
        
        if index_exists and metadata_exists:
            # Download and load existing index
            logging.info(f"📥 Found existing vectordb in S3: {index_key}")
            with tempfile.TemporaryDirectory() as tmpdir:
                index_path = os.path.join(tmpdir, "faiss_index.bin")
                metadata_path = os.path.join(tmpdir, "metadata.pkl")
                
                # Download from S3 (read as binary bytes, not text)
                s3_client = s3_hook.get_conn()
                
                try:
                    # Read FAISS index binary file
                    index_obj = s3_client.get_object(Bucket=bucket_name, Key=index_key)
                    index_content = index_obj['Body'].read()
                    with open(index_path, 'wb') as f:
                        f.write(index_content)
                    
                    # Read metadata pickle binary file
                    metadata_obj = s3_client.get_object(Bucket=bucket_name, Key=metadata_key)
                    metadata_content = metadata_obj['Body'].read()
                    with open(metadata_path, 'wb') as f:
                        f.write(metadata_content)
                    
                    # Load into memory
                    vectordb.load_from_disk(index_path, metadata_path)
                    logging.info("✅ Loaded existing vector database from S3")
                    
                except Exception as load_error:
                    logging.warning(f"⚠️ Failed to load existing index: {load_error}")
                    logging.info("🔨 Creating new index instead")
                    vectordb.create_index()
        else:
            # Create new index (first run or missing files)
            if index_exists or metadata_exists:
                logging.warning(f"⚠️ Incomplete vectordb found (index: {index_exists}, metadata: {metadata_exists})")
            logging.info("🔨 Creating new FAISS vector database (first run)")
            vectordb.create_index()
        
        return vectordb
        
    except Exception as e:
        logging.error(f"❌ Failed to initialize vector database: {str(e)}")
        raise


def save_vectordb_to_s3(vectordb: FAISSVectorDatabase, s3_hook, 
                        bucket_name: str, vectordb_prefix: str = "rag/vectordb"):
    """Save vector database to S3"""
    import tempfile
    import os
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = os.path.join(tmpdir, "faiss_index.bin")
            metadata_path = os.path.join(tmpdir, "metadata.pkl")
            
            # Save to disk
            vectordb.save_to_disk(index_path, metadata_path)
            
            # Upload to S3
            index_key = f"{vectordb_prefix}/faiss_index.bin"
            metadata_key = f"{vectordb_prefix}/metadata.pkl"
            
            with open(index_path, 'rb') as f:
                s3_hook.load_bytes(f.read(), key=index_key, 
                                  bucket_name=bucket_name, replace=True)
            
            with open(metadata_path, 'rb') as f:
                s3_hook.load_bytes(f.read(), key=metadata_key,
                                  bucket_name=bucket_name, replace=True)
            
            logging.info("✅ Saved vector database to S3")
            return True
            
    except Exception as e:
        logging.error(f"❌ Failed to save to S3: {str(e)}")
        raise

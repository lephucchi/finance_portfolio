"""
Embedding utilities for Vietnamese financial news
Supports multiple Vietnamese SBERT models
"""

import logging
from typing import List, Dict, Any
import numpy as np

class VietnameseEmbedder:
    """Vietnamese text embedder using sentence-transformers"""
    
    def __init__(self, model_name: str = "keepitreal/vietnamese-sbert"):
        """
        Initialize Vietnamese embedder
        
        Args:
            model_name: HuggingFace model name
                - keepitreal/vietnamese-sbert (384 dim)
                - VoVanPhuc/sup-SimCSE-VietNamese-phobert-base (768 dim)
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 384  # Default for vietnamese-sbert
        
    def load_model(self):
        """Load sentence-transformers model"""
        try:
            from sentence_transformers import SentenceTransformer
            
            logging.info(f"🤖 Loading Vietnamese SBERT model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            
            # Get actual embedding dimension
            test_embedding = self.model.encode("test", convert_to_numpy=True)
            self.embedding_dim = len(test_embedding)
            
            logging.info(f"✅ Model loaded successfully (dim={self.embedding_dim})")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to load model: {str(e)}")
            raise
    
    def encode_texts(self, texts: List[str], batch_size: int = 32, 
                     show_progress: bool = True) -> np.ndarray:
        """
        Encode multiple texts to embeddings
        
        Args:
            texts: List of text strings
            batch_size: Batch size for encoding
            show_progress: Show progress bar
            
        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        if self.model is None:
            self.load_model()
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=True  # L2 normalization for cosine similarity
            )
            
            logging.info(f"✅ Encoded {len(texts)} texts (shape: {embeddings.shape})")
            return embeddings
            
        except Exception as e:
            logging.error(f"❌ Encoding failed: {str(e)}")
            raise
    
    def encode_single(self, text: str) -> np.ndarray:
        """Encode single text"""
        if self.model is None:
            self.load_model()
        
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embedding


class ChunkingStrategy:
    """Smart chunking for long Vietnamese documents"""
    
    @staticmethod
    def chunk_by_sentences(text: str, max_chunk_size: int = 512, 
                           overlap: int = 50) -> List[str]:
        """
        Chunk text by sentences with overlap
        
        Args:
            text: Input text
            max_chunk_size: Maximum characters per chunk
            overlap: Overlap characters between chunks
            
        Returns:
            List of text chunks
        """
        # Vietnamese sentence splitting
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > max_chunk_size and current_chunk:
                # Save current chunk
                chunks.append('. '.join(current_chunk) + '.')
                
                # Start new chunk with overlap
                overlap_sentences = []
                overlap_length = 0
                for s in reversed(current_chunk):
                    if overlap_length + len(s) <= overlap:
                        overlap_sentences.insert(0, s)
                        overlap_length += len(s)
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_length = overlap_length
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        # Add last chunk
        if current_chunk:
            chunks.append('. '.join(current_chunk) + '.')
        
        return chunks
    
    @staticmethod
    def chunk_by_paragraphs(text: str, max_chunk_size: int = 512) -> List[str]:
        """Chunk text by paragraphs"""
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            if current_length + para_length > max_chunk_size and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_length = 0
            
            current_chunk.append(para)
            current_length += para_length
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks


def prepare_documents_for_embedding(
    news_df,
    chunking_method: str = 'sentences',
    max_chunk_size: int = 512,
    add_metadata_to_text: bool = True
) -> List[Dict[str, Any]]:
    """
    Prepare news articles for embedding with chunking
    
    Args:
        news_df: DataFrame with news articles
        chunking_method: 'sentences' or 'paragraphs' or 'none'
        max_chunk_size: Maximum chunk size in characters
        add_metadata_to_text: Prepend metadata to text for better context
        
    Returns:
        List of document chunks with metadata
    """
    chunker = ChunkingStrategy()
    documents = []
    
    for idx, row in news_df.iterrows():
        # Prepare base text
        title = row.get('title', '').strip()
        content = row.get('clean_content', '').strip()
        
        if not content:
            continue
        
        # Add metadata context if requested
        if add_metadata_to_text:
            metadata_prefix = f"[{row.get('doc_category', 'UNKNOWN')}] {title}: "
            full_text = metadata_prefix + content
        else:
            full_text = f"{title}. {content}"
        
        # Apply chunking
        if chunking_method == 'sentences' and len(full_text) > max_chunk_size:
            chunks = chunker.chunk_by_sentences(full_text, max_chunk_size)
        elif chunking_method == 'paragraphs' and len(full_text) > max_chunk_size:
            chunks = chunker.chunk_by_paragraphs(full_text, max_chunk_size)
        else:
            chunks = [full_text]
        
        # Create document objects for each chunk
        for chunk_idx, chunk in enumerate(chunks):
            doc = {
                'doc_id': f"{row.get('doc_id', idx)}_{chunk_idx}",
                'parent_doc_id': row.get('doc_id', str(idx)),
                'chunk_index': chunk_idx,
                'total_chunks': len(chunks),
                'title': title,
                'text': chunk,
                'url': row.get('url', ''),
                'doc_date': row.get('doc_date', ''),
                'doc_category': row.get('doc_category', 'UNKNOWN'),
                'doc_sentiment': row.get('doc_sentiment', 'NEUTRAL'),
                'doc_source': row.get('doc_source', 'Unknown'),
                'content_length': len(chunk)
            }
            documents.append(doc)
    
    logging.info(f"📄 Prepared {len(documents)} document chunks from {len(news_df)} articles")
    return documents

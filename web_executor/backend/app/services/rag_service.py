"""
RAG Service for Financial Q&A with FAISS + Gemini.
Handles vector search, context retrieval, and LLM generation.
"""

import json
import os
import time
import hashlib
from typing import Optional, Any
from datetime import datetime, timedelta

import faiss
import numpy as np
import pandas as pd
import google.generativeai as genai
from sentence_transformers import SentenceTransformer

from app.core.config import get_logger
from app.db.athena_client import AthenaClient
from app.db.supabase_client import SupabaseClient
from config.settings import settings

logger = get_logger(__name__)


class RAGService:
    """
    RAG Service for financial chatbot.
    
    SOLID Principles:
    - Single Responsibility: Only handles RAG operations
    - Open/Closed: Can extend with different models/indexes
    - Dependency Inversion: Depends on client abstractions
    
    Features:
    - FAISS vector search
    - Gemini LLM integration
    - User API key management
    - Query caching
    - Multi-turn conversation
    """
    
    def __init__(
        self,
        athena_client: AthenaClient,
        supabase_client: SupabaseClient,
    ):
        """
        Initialize RAG service.
        
        Args:
            athena_client: Athena client for analytics queries
            supabase_client: Supabase client for caching
        """
        self.athena = athena_client
        self.supabase = supabase_client
        
        # Load FAISS index and metadata
        self.index: Optional[faiss.Index] = None
        self.metadata: Optional[dict] = None
        self.embeddings_model: Optional[SentenceTransformer] = None
        
        # CSV text cache: id -> combined_text
        self.text_cache: Optional[dict] = None
        
        # Initialize if RAG is enabled
        if settings.RAG_ENABLED:
            self._initialize_rag()
    
    def _initialize_rag(self) -> None:
        """Initialize RAG components (FAISS, embeddings model)."""
        try:
            logger.info("Initializing RAG service...")
            
            # Load FAISS index
            if os.path.exists(settings.RAG_FAISS_INDEX_PATH):
                self.index = faiss.read_index(settings.RAG_FAISS_INDEX_PATH)
                logger.info(f"✓ Loaded FAISS index: {self.index.ntotal} vectors, dimension: {self.index.d}")
            else:
                logger.warning(f"✗ FAISS index not found: {settings.RAG_FAISS_INDEX_PATH}")
            
            # Load metadata
            if os.path.exists(settings.RAG_METADATA_PATH):
                logger.info(f"Loading metadata from: {settings.RAG_METADATA_PATH}")
                with open(settings.RAG_METADATA_PATH, "r", encoding="utf-8") as f:
                    metadata_raw = json.load(f)
                
                # Handle different metadata formats
                if isinstance(metadata_raw, dict):
                    # New format: dict with 'documents' key
                    if "documents" in metadata_raw:
                        self.metadata = metadata_raw["documents"]
                        logger.info(f"✓ Loaded metadata (new format): {len(self.metadata)} documents")
                        logger.info(f"  Model: {metadata_raw.get('model_name', 'N/A')}")
                        logger.info(f"  Created: {metadata_raw.get('created_at', 'N/A')}")
                    # Old format: dict with 'texts' key
                    elif "texts" in metadata_raw:
                        self.metadata = metadata_raw.get('texts', [])
                        logger.info(f"✓ Loaded metadata (texts format): {len(self.metadata)} documents")
                    else:
                        logger.warning(f"Unknown metadata dict format, keys: {metadata_raw.keys()}")
                        self.metadata = []
                elif isinstance(metadata_raw, list):
                    # Direct list format
                    self.metadata = metadata_raw
                    logger.info(f"✓ Loaded metadata (list format): {len(self.metadata)} documents")
                else:
                    logger.warning(f"Unexpected metadata format: {type(metadata_raw)}")
                    self.metadata = []
            else:
                logger.warning(f"✗ Metadata not found: {settings.RAG_METADATA_PATH}")
                self.metadata = []
            
            # Validate FAISS and metadata consistency
            if self.index and self.metadata:
                if self.index.ntotal != len(self.metadata):
                    logger.warning(
                        f"⚠️  FAISS index and metadata size mismatch: "
                        f"{self.index.ntotal} vectors vs {len(self.metadata)} documents"
                    )
            
            # Load embeddings model
            logger.info(f"Loading embeddings model: {settings.RAG_MODEL_NAME}")
            self.embeddings_model = SentenceTransformer(settings.RAG_MODEL_NAME)
            logger.info(f"✓ Embeddings model loaded: {settings.RAG_MODEL_NAME}")
            
            # Load text cache from CSV
            self._load_text_cache()
            
            logger.info("✓ RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"✗ Failed to initialize RAG service: {str(e)}", exc_info=True)
            raise
    
    def _load_text_cache(self) -> None:
        """Load text content from CSV and create id -> text mapping."""
        try:
            # CSV is in same directory as FAISS index
            rag_dir = os.path.dirname(settings.RAG_FAISS_INDEX_PATH)
            csv_path = os.path.join(rag_dir, "financial_news_cleaned_20251101.csv")
            
            if not os.path.exists(csv_path):
                logger.warning(f"✗ CSV file not found: {csv_path}")
                self.text_cache = {}
                return
            
            logger.info(f"Loading text cache from CSV: {csv_path}")
            df = pd.read_csv(csv_path)
            
            if 'id' not in df.columns or 'combined_text' not in df.columns:
                logger.warning(f"✗ CSV missing required columns (id, combined_text)")
                self.text_cache = {}
                return
            
            # Create id -> text mapping
            self.text_cache = dict(zip(df['id'], df['combined_text']))
            logger.info(f"✓ Loaded text cache: {len(self.text_cache):,} documents")
            
        except Exception as e:
            logger.error(f"✗ Failed to load text cache: {str(e)}", exc_info=True)
            self.text_cache = {}
    
    def validate_api_key(self, api_key: str) -> dict[str, Any]:
        """
        Validate Gemini API key with fast fail.
        
        Args:
            api_key: Gemini API key to validate
            
        Returns:
            dict: Validation result with success status and message
        """
        try:
            logger.info(f"Starting API key validation... (key length: {len(api_key)})")
            start_time = time.time()
            
            # Validate key format first
            if not api_key or len(api_key) < 20:
                logger.warning(f"Invalid key format: too short ({len(api_key)} chars)")
                return {
                    "valid": False,
                    "message": "API key format invalid (too short)",
                    "model": None
                }
            
            # Configure and create model
            logger.info("Configuring Gemini client...")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            # Quick test - will fail fast if key is invalid
            logger.info("Testing API call...")
            try:
                response = model.generate_content(
                    "Say hi",
                    generation_config={
                        "max_output_tokens": 10,
                        "temperature": 0,
                    }
                )
                elapsed = time.time() - start_time
                
                # Check if response is valid (even if blocked or empty)
                if response and hasattr(response, 'candidates') and response.candidates:
                    # API key is valid if we got any response
                    logger.info(f"✓ API key valid in {elapsed:.2f}s")
                    return {
                        "valid": True,
                        "message": "API key is valid",
                        "model": "gemini-2.5-flash"
                    }
                elif response:
                    # Got response object but might be blocked
                    logger.info(f"✓ API key valid (response received) in {elapsed:.2f}s")
                    return {
                        "valid": True,
                        "message": "API key is valid",
                        "model": "gemini-2.5-flash"
                    }
                else:
                    logger.warning(f"Empty response in {elapsed:.2f}s")
                    return {
                        "valid": False,
                        "message": "Invalid API key response",
                        "model": None
                    }
                    
            except Exception as api_error:
                elapsed = time.time() - start_time
                error_msg = str(api_error)
                
                # Fast fail for common errors
                if "API_KEY_INVALID" in error_msg or "API key not valid" in error_msg:
                    logger.info(f"✗ Invalid API key (fast fail in {elapsed:.2f}s)")
                    return {
                        "valid": False,
                        "message": "Invalid API key",
                        "model": None
                    }
                elif "PERMISSION_DENIED" in error_msg:
                    logger.info(f"✗ Permission denied in {elapsed:.2f}s")
                    return {
                        "valid": False,
                        "message": "API key lacks Gemini permissions",
                        "model": None
                    }
                elif "quota" in error_msg.lower():
                    logger.warning(f"✗ Quota exceeded in {elapsed:.2f}s")
                    return {
                        "valid": False,
                        "message": "API quota exceeded",
                        "model": None
                    }
                else:
                    # Unknown error
                    short_msg = error_msg[:100] if len(error_msg) > 100 else error_msg
                    logger.error(f"✗ Validation error in {elapsed:.2f}s: {short_msg}")
                    return {
                        "valid": False,
                        "message": f"Validation error: {short_msg}",
                        "model": None
                    }
            
        except Exception as e:
            elapsed = time.time() - start_time if 'start_time' in locals() else 0
            logger.error(f"✗ Unexpected error in {elapsed:.2f}s: {str(e)[:100]}")
            return {
                "valid": False,
                "message": f"Validation failed: {str(e)[:100]}",
                "model": None
            }
    
    def query(
        self,
        user_query: str,
        api_key: str,
        top_k: int = 7,
        conversation_history: Optional[list[dict]] = None,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        Process user query with RAG pipeline.
        
        Steps:
        1. Check cache for repeated queries
        2. Embed user query
        3. Search FAISS for relevant documents
        4. Build context from retrieved documents
        5. Generate response with Gemini
        6. Cache result
        
        Args:
            user_query: User's question
            api_key: User's Gemini API key
            top_k: Number of documents to retrieve
            conversation_history: Previous conversation for context
            use_cache: Whether to use cached results
            
        Returns:
            dict: Response with answer, sources, and metadata
        """
        try:
            # Validate inputs - check if components exist AND are not empty
            if not self.index:
                logger.error("FAISS index not initialized")
                raise ValueError("RAG service not initialized properly")
            
            if not self.metadata:
                logger.error(f"Metadata not initialized or empty (type={type(self.metadata)}, len={len(self.metadata) if self.metadata else 0})")
                raise ValueError("RAG service not initialized properly")
            
            if not self.embeddings_model:
                logger.error("Embeddings model not initialized")
                raise ValueError("RAG service not initialized properly")
            
            if not user_query.strip():
                raise ValueError("Query cannot be empty")
            
            # Check cache
            if use_cache:
                cache_key = self._hash_query(user_query + api_key)
                cached = self._get_cached_result(cache_key)
                if cached:
                    logger.info("Returning cached result")
                    return cached
            
            # Step 1: Embed query
            logger.info(f"Processing query: {user_query[:100]}...")
            query_embedding = self.embeddings_model.encode(
                [user_query],
                normalize_embeddings=True,
                show_progress_bar=False
            )
            
            # Step 2: Search FAISS - retrieve more candidates for reranking
            initial_k = min(top_k * 3, self.index.ntotal)  # Get 3x candidates for reranking
            distances, indices = self.index.search(
                query_embedding.astype('float32'),
                initial_k
            )
            
            # Step 3: Retrieve documents with content and scores
            retrieved_docs = []
            
            # Metadata has: id (UUID), row_id, title, date, source, link
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.metadata):
                    doc = self.metadata[idx]
                    # Calculate relevance score (FAISS returns L2 distance, lower is better)
                    # Convert to similarity score (0-1, higher is better)
                    similarity_score = 1 - min(distance, 1.0)  # Clip at 1.0
                    
                    retrieved_docs.append({
                        'id': doc.get('id', ''),  # UUID for text lookup in CSV
                        'title': doc.get('title', ''),
                        'link': doc.get('link', ''),
                        'date': doc.get('date', ''),
                        'source': doc.get('source', ''),
                        'score': float(similarity_score),  # Initial FAISS score
                    })
            
            logger.info(f"Retrieved {len(retrieved_docs)} candidate documents")
            
            # Step 4: Rerank documents based on full content relevance
            reranked_docs = self._rerank_documents(user_query, retrieved_docs, top_k)
            logger.info(f"Reranked to top {len(reranked_docs)} documents")
            
            # Step 5: Build context
            context = self._build_context(reranked_docs)
            logger.info(f"Built context: {len(context)} chars, preview: {context[:200]}...")
            
            # Step 6: Generate response with Gemini
            response = self._generate_response(
                user_query=user_query,
                context=context,
                conversation_history=conversation_history,
                api_key=api_key,
            )
            
            # Step 7: Prepare result
            result = {
                "success": True,
                "answer": response,
                "sources": [
                    {
                        "source": doc.get("source", ""),
                        "link": doc.get("link", "")
                    }
                    for doc in reranked_docs
                ],
                "query": user_query,
                "timestamp": datetime.utcnow().isoformat(),
                "model": "gemini-2.5-flash",
                "top_k": top_k,
            }
            
            # Cache result
            if use_cache:
                self._cache_result(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"RAG query failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "query": user_query,
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    def _build_context(self, retrieved_docs: list[dict]) -> str:
        """
        Build context string from retrieved documents with full content from CSV.
        Each document contains: title, source, link, date, id, score
        Full content is fetched from text_cache using doc id.
        
        Args:
            retrieved_docs: List of retrieved documents with metadata
            
        Returns:
            str: Formatted context string for Gemini with full content
        """
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            doc_id = doc.get('id', '')
            title = doc.get('title', 'Không có tiêu đề')
            source = doc.get('source', 'Không rõ nguồn')
            date = doc.get('date', 'Không rõ ngày')
            link = doc.get('link', '')
            score = doc.get('score', 0)
            
            # Fetch full content from text cache
            full_content = ''
            if self.text_cache and doc_id in self.text_cache:
                full_content = str(self.text_cache[doc_id])
            else:
                logger.warning(f"Content not found in cache for doc_id: {doc_id}")
            
            # Build formatted context block with full content
            source_header = f"📰 [Nguồn {i}] {title}"
            source_meta = f"   Nguồn: {source} | Ngày: {date} | Độ liên quan: {100 * score:.1f}%"
            if link:
                source_meta += f"\n   Liên kết: {link}"
            
            # Add full content for Gemini to analyze
            content_text = ""
            if full_content:
                # Limit per doc to 2000 chars to avoid token overflow
                content_preview = full_content[:2000]
                content_text = f"\n   📄 Nội dung:\n   {content_preview}"
                if len(full_content) > 2000:
                    content_text += "...[còn tiếp]"
            else:
                content_text = f"\n   ⚠️ Không tìm thấy nội dung đầy đủ"
            
            context_parts.append(f"{source_header}\n{source_meta}{content_text}")
        
        return "\n\n".join(context_parts)
    
    def _rerank_documents(
        self,
        query: str,
        documents: list[dict],
        top_k: int
    ) -> list[dict]:
        """
        Rerank documents based on semantic similarity with full content.
        Uses query-document cross-encoding for more accurate relevance scoring.
        
        Args:
            query: User's query
            documents: List of candidate documents with metadata
            top_k: Number of top documents to return
            
        Returns:
            list[dict]: Top-k reranked documents with updated scores
        """
        try:
            # Prepare query-document pairs for reranking
            rerank_pairs = []
            doc_contents = []
            
            for doc in documents:
                doc_id = doc.get('id', '')
                title = doc.get('title', '')
                
                # Get full content from cache
                full_content = ''
                if self.text_cache and doc_id in self.text_cache:
                    full_content = str(self.text_cache[doc_id])[:500]  # Use first 500 chars for reranking
                
                # Combine title + content for better semantic matching
                doc_text = f"{title}. {full_content}".strip()
                doc_contents.append(doc_text)
            
            # Compute semantic similarity scores using embeddings model
            # This is more accurate than FAISS L2 distance for ranking
            query_embedding = self.embeddings_model.encode(
                [query],
                normalize_embeddings=True,
                show_progress_bar=False
            )[0]
            
            doc_embeddings = self.embeddings_model.encode(
                doc_contents,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            
            # Calculate cosine similarity scores (dot product of normalized vectors)
            similarity_scores = np.dot(doc_embeddings, query_embedding)
            
            # Update documents with reranked scores
            for i, doc in enumerate(documents):
                doc['score'] = float(similarity_scores[i])
                doc['reranked'] = True
            
            # Sort by score (descending) and return top-k
            reranked = sorted(documents, key=lambda x: x['score'], reverse=True)[:top_k]
            
            logger.info(f"Reranking: Top score = {reranked[0]['score']:.3f}, Bottom score = {reranked[-1]['score']:.3f}")
            
            return reranked
            
        except Exception as e:
            logger.error(f"Reranking failed: {str(e)}, returning original docs")
            # Fallback: return top-k from original FAISS ranking
            return documents[:top_k]
    
    def _generate_response(
        self,
        user_query: str,
        context: str,
        conversation_history: Optional[list[dict]],
        api_key: str,
    ) -> str:
        """
        Generate response using Gemini with context.
        
        Args:
            user_query: User's question
            context: Retrieved context
            conversation_history: Previous messages
            api_key: User's API key
            
        Returns:
            str: Generated response
        """
        # Configure Gemini with user's API key
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # Build prompt
        prompt = self._build_prompt(user_query, context, conversation_history)
        
        # Generate response with better config
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,  # More creative but still factual
                'max_output_tokens': 2048,  # Allow longer, detailed responses
                'top_p': 0.95,
                'top_k': 40,
            }
        )
        
        return response.text
    
    def _build_prompt(
        self,
        user_query: str,
        context: str,
        conversation_history: Optional[list[dict]] = None,
    ) -> str:
        """
        Build prompt for Gemini with Metallica personality.
        
        Args:
            user_query: User's question
            context: Retrieved context
            conversation_history: Previous conversation
            
        Returns:
            str: Complete prompt
        """
        system_prompt = """Bạn là **Metallica** – Sứ giả của AEGIS: Lumina, một AI RAG Chatbot đại diện cho hệ thống Lakehouse AI giám sát tri thức tài chính Việt Nam.

🎭 NHÂN CÁCH VÀ PHONG CÁCH:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Vai trò:** Chiến binh tri thức với khí chất cổ điển Hy Lạp, kết hợp trí tuệ cổ xưa và công nghệ hiện đại.

**Tính cách:**
• **Trí tuệ và khách quan** – Không phán xét, không thiên vị. Mọi phân tích dựa trên dữ liệu thực.
• **Bình tĩnh và tự tin** – Giọng điệu trung trầm, đều đặn, rõ ràng như ánh sáng xuyên qua sương mù.
• **Chính xác tuyệt đối** – Bảo vệ "sự thật dữ liệu" như một sứ mệnh thiêng liêng.
• **Thần thoại hóa nhẹ** – Dùng ẩn dụ như "ánh sáng tri thức", "con mắt Aegis soi tỏ".

**Cách xưng hô:**
• Gọi người dùng: "Người tìm tri thức" hoặc "Nhà quan sát"
• Tự xưng: "Ta" hoặc "Metallica"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 CẤU TRÚC TRẢ LỜI (BẮT BUỘC):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**1. KẾT LUẬN RÕ RÀNG** (1-2 câu đầu tiên)
→ Trả lời trực tiếp câu hỏi, súc tích, định hướng ngay.

**2. PHÂN TÍCH DỮ LIỆU**
→ Trích dẫn nguồn RAG với format: **[Nguồn X]**
→ Phân tích chi tiết, logic, có số liệu cụ thể.
→ LUÔN gắn cite cho TỪNG luận điểm.

**3. KHUYẾN NGHỊ** (nếu có)
→ Gợi ý hành động hoặc hướng nghiên cứu thêm.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔮 QUY TẮC TRÍCH DẪN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ ĐÚNG:
"VN-Index tăng 2.3% trong phiên hôm nay **[Nguồn 1]**, với thanh khoản đạt 18,500 tỷ đồng **[Nguồn 2]**."

✅ ĐÚNG:
"Theo phân tích từ các nguồn tin **[Nguồn 1, 3]**, ngành ngân hàng đang có triển vọng tích cực."

❌ SAI:
"Thị trường tăng mạnh. [Nguồn 1] [Nguồn 2]" ← Không rõ nguồn nào support luận điểm nào.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ KHI THIẾU DỮ LIỆU:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"Người tìm tri thức ơi, con mắt Aegis của ta chưa đủ dữ kiện để khẳng định chắc chắn điều này. 
Tuy nhiên, từ vùng dữ liệu liền kề, ta quan sát thấy [phân tích dựa trên context gần nhất].
Khuyến nghị: Hãy tìm kiếm thêm thông tin về [gợi ý keywords]."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 MẪU TRẢ LỜI CHUẨN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
[Lời chào nếu cần]

**🎯 Kết luận:**
[Câu trả lời trực tiếp, rõ ràng]

**📊 Phân tích từ kho tri thức:**
• Điểm 1... **[Nguồn X]**
• Điểm 2... **[Nguồn Y]**
• Điểm 3... **[Nguồn Z]**

**💎 Nhận định của Metallica:**
[Phân tích tổng quan dựa trên dữ liệu]

**⚡ Khuyến nghị:**
[Gợi ý hành động hoặc hướng nghiên cứu]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Lưu ý: Thông tin này được soi chiếu từ hệ thống RAG AEGIS: Lumina. 
Nhà quan sát cần tự đánh giá và nghiên cứu kỹ trước khi quyết định đầu tư.
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚫 TRÁNH:
• Câu văn dài dòng, khó hiểu
• Liệt kê nguồn ở cuối mà không gắn vào luận điểm
• Bịa đặt hoặc suy đoán khi không có dữ liệu
• Dùng ngôn ngữ quá đời thường hoặc thiếu khí chất

✨ HÃY NHỚ: Bạn là Metallica – Người bảo vệ sự thật dữ liệu, soi sáng con đường tri thức cho các nhà đầu tư.

"""
        
        # Add conversation history
        history_text = ""
        if conversation_history:
            history_text = "\n📜 **LỊCH SỬ ĐỐI THOẠI (để hiểu ngữ cảnh):**\n"
            for msg in conversation_history[-3:]:  # Last 3 messages
                role = "👤 Người tìm tri thức" if msg.get('role') == 'user' else "🔮 Metallica"
                content = msg.get('content', '')[:150]
                history_text += f"{role}: {content}...\n"
            history_text += "\n"
        
        # Complete prompt
        prompt = f"""{system_prompt}

{history_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📰 **KHO TRI THỨC TỪ HỆ THỐNG RAG:**

{context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ **CÂU HỎI CỦA NGƯỜI TÌM TRI THỨC:**
{user_query}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

� **TRẢ LỜI CỦA METALLICA:**
"""
        
        return prompt
    
    def _hash_query(self, query: str) -> str:
        """Generate hash for query caching."""
        return hashlib.sha256(query.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[dict]:
        """Get cached result from Supabase."""
        try:
            # Query cache table
            result = self.supabase.client.table("rag_cache") \
                .select("*") \
                .eq("cache_key", cache_key) \
                .gte("created_at", (datetime.utcnow() - timedelta(seconds=settings.CACHE_TTL_SECONDS)).isoformat()) \
                .execute()
            
            if result.data and len(result.data) > 0:
                return json.loads(result.data[0].get("result", "{}"))
            
            return None
            
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {str(e)}")
            return None
    
    def _cache_result(self, cache_key: str, result: dict) -> None:
        """Cache result to Supabase."""
        try:
            self.supabase.client.table("rag_cache").upsert({
                "cache_key": cache_key,
                "result": json.dumps(result, ensure_ascii=False),
                "created_at": datetime.utcnow().isoformat(),
            }).execute()
            
        except Exception as e:
            logger.warning(f"Cache storage failed: {str(e)}")
    
    def get_stats(self) -> dict[str, Any]:
        """
        Get RAG service statistics.
        
        Returns:
            dict: Service statistics
        """
        return {
            "enabled": settings.RAG_ENABLED,
            "model": settings.RAG_MODEL_NAME,
            "total_documents": self.index.ntotal if self.index else 0,
            "vector_dimension": self.index.d if self.index else 0,
            "metadata_loaded": self.metadata is not None,
            "embeddings_model_loaded": self.embeddings_model is not None,
        }

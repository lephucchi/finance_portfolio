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
                logger.info(f"Loaded FAISS index: {self.index.ntotal} vectors")
            else:
                logger.warning(f"FAISS index not found: {settings.RAG_FAISS_INDEX_PATH}")
            
            # Load metadata
            if os.path.exists(settings.RAG_METADATA_PATH):
                with open(settings.RAG_METADATA_PATH, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                # Metadata is a list of documents
                if isinstance(self.metadata, list):
                    logger.info(f"Loaded metadata: {len(self.metadata)} documents")
                elif isinstance(self.metadata, dict):
                    # Handle dict format with 'texts' key
                    self.metadata = self.metadata.get('texts', [])
                    logger.info(f"Loaded metadata: {len(self.metadata)} documents")
                else:
                    logger.warning(f"Unexpected metadata format: {type(self.metadata)}")
                    self.metadata = []
            else:
                logger.warning(f"Metadata not found: {settings.RAG_METADATA_PATH}")
                self.metadata = []
            
            # Load embeddings model
            logger.info(f"Loading embeddings model: {settings.RAG_MODEL_NAME}")
            self.embeddings_model = SentenceTransformer(settings.RAG_MODEL_NAME)
            logger.info("RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {str(e)}", exc_info=True)
            raise
    
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
            model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
            
            # Quick test - will fail fast if key is invalid
            logger.info("Testing API call...")
            try:
                response = model.generate_content(
                    "hi",
                    generation_config={
                        "max_output_tokens": 5,
                        "temperature": 0,
                    }
                )
                elapsed = time.time() - start_time
                
                if response and response.text:
                    logger.info(f"✓ API key valid in {elapsed:.2f}s")
                    return {
                        "valid": True,
                        "message": "API key is valid",
                        "model": "gemini-2.0-flash-lite"
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
        top_k: int = 5,
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
            # Validate inputs
            if not self.index or not self.metadata or not self.embeddings_model:
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
            
            # Step 2: Search FAISS
            distances, indices = self.index.search(
                query_embedding.astype('float32'),
                min(top_k, self.index.ntotal)
            )
            
            # Step 3: Retrieve documents
            retrieved_docs = []
            
            # Metadata is a list of dicts with fields: row_id, title, date, source, link, length
            # But missing 'text' field - we'll use title as preview
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.metadata):
                    doc = self.metadata[idx]
                    retrieved_docs.append({
                        'id': doc.get('row_id', idx),
                        'text': doc.get('title', '') + f" [Source: {doc.get('source', 'N/A')}]",
                        'score': float(distance),
                        'title': doc.get('title', ''),
                        'link': doc.get('link', ''),
                        'date': doc.get('date', ''),
                        'source': doc.get('source', ''),
                    })
            
            logger.info(f"Retrieved {len(retrieved_docs)} documents")
            
            # Step 4: Build context
            context = self._build_context(retrieved_docs)
            
            # Step 5: Generate response with Gemini
            response = self._generate_response(
                user_query=user_query,
                context=context,
                conversation_history=conversation_history,
                api_key=api_key,
            )
            
            # Step 6: Prepare result
            result = {
                "success": True,
                "answer": response,
                "sources": retrieved_docs,
                "query": user_query,
                "timestamp": datetime.utcnow().isoformat(),
                "model": "gemini-2.0-flash-lite",
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
        Build context string from retrieved documents.
        
        Args:
            retrieved_docs: List of retrieved documents
            
        Returns:
            str: Formatted context string
        """
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            title = doc.get('title', 'Không có tiêu đề')
            source = doc.get('source', 'Không rõ nguồn')
            date = doc.get('date', 'Không rõ ngày')
            link = doc.get('link', '')
            
            # Build source header with metadata
            source_header = f"[Nguồn {i}: {title}]"
            source_meta = f"Từ: {source} | Ngày: {date}"
            if link:
                source_meta += f" | Link: {link}"
            
            context_parts.append(f"{source_header}\n{source_meta}\n{doc['text']}\n")
        
        return "\n".join(context_parts)
    
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
        model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
        
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
        Build prompt for Gemini.
        
        Args:
            user_query: User's question
            context: Retrieved context
            conversation_history: Previous conversation
            
        Returns:
            str: Complete prompt
        """
        system_prompt = """Bạn là Financial Oracle - một chuyên gia tài chính AI uy tín và thân thiện, chuyên phân tích thị trường chứng khoán Việt Nam.

🎯 VAI TRÒ CỦA BẠN:
- Trợ lý phân tích tài chính chuyên sâu với kiến thức về thị trường Việt Nam
- Cung cấp thông tin chính xác, khách quan dựa trên dữ liệu thực tế
- Giải thích các khái niệm phức tạp một cách dễ hiểu
- Hỗ trợ nhà đầu tư đưa ra quyết định sáng suốt

📋 QUY TẮC TRẢ LỜI:
1. **Dựa vào ngữ cảnh**: Chỉ sử dụng thông tin từ các nguồn tin tức được cung cấp
2. **Trích dẫn nguồn**: Luôn ghi rõ thông tin đến từ [Nguồn X] khi trả lời
3. **Cấu trúc rõ ràng**: 
   - Đưa ra câu trả lời tổng quan trước
   - Chi tiết hóa với bullet points hoặc danh sách đánh số
   - Tổng kết hoặc khuyến nghị (nếu phù hợp)
4. **Phong cách**:
   - Tự nhiên, dễ hiểu nhưng chuyên nghiệp
   - Sử dụng emoji phù hợp để dễ đọc (💰 📈 📉 ⚠️ 💡)
   - Tránh câu văn quá dài, khô khan
5. **Trung thực**: Nếu không có thông tin trong ngữ cảnh, hãy thẳng thắn nói rõ
6. **Cảnh báo**: Luôn nhắc nhở rằng đây là thông tin tham khảo, nhà đầu tư cần tự nghiên cứu

💡 MẪU TRẢ LỜI LÝ TƯỞNG:
```
[Câu mở đầu ngắn gọn trả lời trực tiếp câu hỏi]

**Chi tiết:**
- Điểm 1... [Nguồn X]
- Điểm 2... [Nguồn Y]
- Điểm 3...

**Phân tích/Nhận định:** [Nếu cần]
[Đưa ra góc nhìn tổng quan dựa trên dữ liệu]

⚠️ **Lưu ý:** Thông tin mang tính tham khảo, nhà đầu tư cần tự đánh giá và nghiên cứu kỹ trước khi quyết định.
```

🚫 TRÁNH:
- Câu trả lời quá ngắn, thiếu chi tiết
- Liệt kê nguồn ở cuối như một list dài
- Bịa đặt hoặc suy đoán khi không có thông tin
- Ngôn ngữ quá cứng nhắc như văn bản pháp lý

"""
        
        # Add conversation history
        history_text = ""
        if conversation_history:
            history_text = "\n📜 **LỊCH SỬ HỘI THOẠI (để hiểu ngữ cảnh):**\n"
            for msg in conversation_history[-3:]:  # Last 3 messages
                role = "👤 Người dùng" if msg.get('role') == 'user' else "🤖 Oracle"
                content = msg.get('content', '')[:150]  # Limit length
                history_text += f"{role}: {content}...\n"
            history_text += "\n"
        
        # Complete prompt
        prompt = f"""{system_prompt}
{history_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📰 **CÁC NGUỒN TIN TỨC LIÊN QUAN:**

{context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ **CÂU HỎI CỦA NHÀ ĐẦU TƯ:**
{user_query}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 **PHÂN TÍCH CỦA ORACLE:**
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

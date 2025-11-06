"""
Pydantic schemas for RAG endpoints.
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, validator


class APIKeyValidationRequest(BaseModel):
    """Request model for API key validation."""
    
    api_key: str = Field(..., description="Gemini API key to validate")
    
    @validator('api_key')
    def validate_api_key_format(cls, v):
        """Validate API key is not empty."""
        if not v or not v.strip():
            raise ValueError("API key cannot be empty")
        return v.strip()


class APIKeyValidationResponse(BaseModel):
    """Response model for API key validation."""
    
    valid: bool = Field(..., description="Whether the API key is valid")
    message: str = Field(..., description="Validation message")
    model: Optional[str] = Field(None, description="Model name if valid")


class ConversationMessage(BaseModel):
    """Single message in conversation history."""
    
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(None, description="Message timestamp")
    
    @validator('role')
    def validate_role(cls, v):
        """Validate role is either user or assistant."""
        if v not in ['user', 'assistant']:
            raise ValueError("Role must be 'user' or 'assistant'")
        return v


class RAGQueryRequest(BaseModel):
    """Request model for RAG query."""
    
    query: str = Field(..., description="User's question", min_length=1, max_length=2000)
    api_key: str = Field(..., description="User's Gemini API key")
    top_k: int = Field(5, description="Number of documents to retrieve", ge=1, le=20)
    use_cache: bool = Field(True, description="Whether to use cached results")
    conversation_history: Optional[list[ConversationMessage]] = Field(
        None,
        description="Previous conversation messages for context"
    )
    
    @validator('query')
    def validate_query(cls, v):
        """Validate query is not empty."""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()
    
    @validator('api_key')
    def validate_api_key(cls, v):
        """Validate API key is not empty."""
        if not v or not v.strip():
            raise ValueError("API key cannot be empty")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Tình hình thị trường chứng khoán Việt Nam tuần này như thế nào?",
                "api_key": "AIzaSy...",
                "top_k": 5,
                "use_cache": True,
                "conversation_history": [
                    {
                        "role": "user",
                        "content": "Xin chào",
                        "timestamp": "2025-11-04T10:00:00Z"
                    },
                    {
                        "role": "assistant",
                        "content": "Xin chào! Tôi có thể giúp gì cho bạn?",
                        "timestamp": "2025-11-04T10:00:01Z"
                    }
                ]
            }
        }


class RetrievedDocument(BaseModel):
    """Single retrieved document from vector search."""
    
    source: str = Field(..., description="News source (cafef.vn, vietstock.vn, etc.)")
    link: str = Field(..., description="Link to original article")


class RAGQueryResponse(BaseModel):
    """Response model for RAG query."""
    
    success: bool = Field(..., description="Whether the query was successful")
    answer: Optional[str] = Field(None, description="Generated answer")
    sources: Optional[list[RetrievedDocument]] = Field(None, description="Retrieved source documents")
    query: str = Field(..., description="Original query")
    timestamp: datetime = Field(..., description="Response timestamp")
    model: Optional[str] = Field(None, description="Model used for generation")
    top_k: Optional[int] = Field(None, description="Number of documents retrieved")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "answer": "Người tìm tri thức ơi, dựa trên kho tri thức của AEGIS: Lumina...",
                "sources": [
                    {
                        "source": "cafef.vn",
                        "link": "https://cafef.vn/tin-tuc-12345"
                    },
                    {
                        "source": "vietstock.vn",
                        "link": "https://vietstock.vn/bai-viet-67890"
                    }
                ],
                "query": "Tình hình thị trường chứng khoán Việt Nam tuần này như thế nào?",
                "timestamp": "2025-11-06T10:00:00Z",
                "model": "gemini-2.5-flash",
                "top_k": 5
            }
        }


class RAGStatsResponse(BaseModel):
    """Response model for RAG service statistics."""
    
    enabled: bool = Field(..., description="Whether RAG is enabled")
    model: str = Field(..., description="Embeddings model name")
    total_documents: int = Field(..., description="Total number of documents in index")
    vector_dimension: int = Field(..., description="Vector embedding dimension")
    metadata_loaded: bool = Field(..., description="Whether metadata is loaded")
    embeddings_model_loaded: bool = Field(..., description="Whether embeddings model is loaded")
    
    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "model": "keepitreal/vietnamese-sbert",
                "total_documents": 15420,
                "vector_dimension": 768,
                "metadata_loaded": True,
                "embeddings_model_loaded": True
            }
        }


class ConversationSession(BaseModel):
    """Conversation session metadata."""
    
    session_id: str = Field(..., description="Unique session ID")
    created_at: datetime = Field(..., description="Session creation time")
    last_activity: datetime = Field(..., description="Last activity time")
    message_count: int = Field(0, description="Number of messages in session")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123",
                "created_at": "2025-11-04T10:00:00Z",
                "last_activity": "2025-11-04T10:15:30Z",
                "message_count": 5
            }
        }

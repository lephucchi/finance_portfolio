"""
RAG API endpoints for financial chatbot.
Handles chat queries, API key validation, and service stats.
"""

import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any

from app.core.config import get_logger
from app.services.rag_service import RAGService
from app.db.athena_client import AthenaClient
from app.db.supabase_client import SupabaseClient
from app.schemas.rag_schemas import (
    APIKeyValidationRequest,
    APIKeyValidationResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    RAGStatsResponse,
)
from config.settings import settings

logger = get_logger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG Chatbot"])


# ========================
# DEPENDENCY INJECTION
# ========================

# Singleton RAG service instance (cached)
_rag_service_instance: RAGService = None
_rag_service_lock = False  # Simple lock flag

def init_rag_service() -> None:
    """
    Initialize RAG service at application startup.
    Called from main.py lifespan to avoid race conditions.
    """
    global _rag_service_instance, _rag_service_lock
    
    if _rag_service_instance is not None:
        logger.info("RAG service already initialized")
        return
    
    if _rag_service_lock:
        logger.warning("RAG service initialization already in progress")
        return
    
    _rag_service_lock = True
    try:
        logger.info("Creating RAG service instance at startup")
        athena_client = AthenaClient()
        supabase_client = SupabaseClient()
        _rag_service_instance = RAGService(athena_client, supabase_client)
        logger.info("RAG service instance created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG service: {e}", exc_info=True)
        raise
    finally:
        _rag_service_lock = False


async def get_rag_service() -> RAGService:
    """
    Get cached RAG service instance (async dependency).
    Service must be initialized at startup via init_rag_service().
    
    Returns:
        RAGService: Configured RAG service (cached)
        
    Raises:
        RuntimeError: If service not initialized at startup
    """
    global _rag_service_instance
    
    logger.info("get_rag_service() called")  # DEBUG
    
    if _rag_service_instance is None:
        # Fallback: try to initialize if not done at startup
        logger.warning("RAG service not initialized at startup, initializing now...")
        init_rag_service()
    
    if _rag_service_instance is None:
        logger.error("RAG service is None after initialization!")
        raise RuntimeError("RAG service failed to initialize")
    
    logger.info("get_rag_service() returning instance")  # DEBUG
    return _rag_service_instance


# ========================
# ENDPOINTS
# ========================

@router.post(
    "/validate-key",
    response_model=APIKeyValidationResponse,
    summary="Validate Gemini API Key",
    description="Validate a user's Gemini API key before using the chatbot",
)
async def validate_api_key(
    request: APIKeyValidationRequest,
    service: RAGService = Depends(get_rag_service),
) -> APIKeyValidationResponse:
    """
    Validate Gemini API key.
    
    This endpoint allows users to test their API key before chatting.
    
    Args:
        request: API key validation request
        service: RAG service instance
        
    Returns:
        APIKeyValidationResponse: Validation result
        
    Raises:
        HTTPException: If service is not available
    """
    try:
        logger.info(f"Validation request received (key length: {len(request.api_key)})")
        
        if not settings.RAG_ENABLED:
            logger.error("RAG service is disabled")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG service is not enabled"
            )
        
        logger.info("Calling RAG service validate_api_key...")
        # Run blocking sync function in thread pool to avoid blocking event loop
        result = await asyncio.to_thread(service.validate_api_key, request.api_key)
        logger.info(f"Validation result: valid={result.get('valid')}, message={result.get('message')}")
        
        return APIKeyValidationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API key validation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.post(
    "/query",
    response_model=RAGQueryResponse,
    summary="Query RAG Chatbot",
    description="Send a question to the RAG-powered financial chatbot",
)
async def query_rag(
    request: RAGQueryRequest,
    service: RAGService = Depends(get_rag_service),
) -> RAGQueryResponse:
    """
    Process user query with RAG pipeline.
    
    This endpoint:
    1. Embeds the user's query
    2. Searches FAISS for relevant financial news
    3. Generates response using Gemini with retrieved context
    4. Returns answer with source citations
    
    Args:
        request: RAG query request with question and API key
        service: RAG service instance
        
    Returns:
        RAGQueryResponse: Generated answer with sources
        
    Raises:
        HTTPException: If service unavailable or query fails
    """
    try:
        if not settings.RAG_ENABLED:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG service is not enabled"
            )
        
        # Convert conversation history to dict format
        conversation_history = None
        if request.conversation_history:
            conversation_history = [
                msg.model_dump() for msg in request.conversation_history
            ]
        
        # Process query - run in thread pool to avoid blocking event loop
        result = await asyncio.to_thread(
            service.query,
            user_query=request.query,
            api_key=request.api_key,
            top_k=request.top_k,
            conversation_history=conversation_history,
            use_cache=request.use_cache,
        )
        
        # Check if query was successful
        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Query processing failed")
            )
        
        return RAGQueryResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RAG query error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=RAGStatsResponse,
    summary="Get RAG Service Statistics",
    description="Get statistics about the RAG service (documents, model info, etc.)",
)
async def get_rag_stats(
    service: RAGService = Depends(get_rag_service),
) -> RAGStatsResponse:
    """
    Get RAG service statistics.
    
    Returns information about:
    - Number of documents in vector database
    - Embeddings model details
    - Service status
    
    Args:
        service: RAG service instance
        
    Returns:
        RAGStatsResponse: Service statistics
        
    Raises:
        HTTPException: If service unavailable
    """
    try:
        if not settings.RAG_ENABLED:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG service is not enabled"
            )
        
        stats = service.get_stats()
        return RAGStatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get RAG stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stats: {str(e)}"
        )


@router.get(
    "/health",
    summary="RAG Service Health Check",
    description="Check if RAG service is healthy and ready",
)
async def rag_health_check(
    service: RAGService = Depends(get_rag_service),
) -> dict[str, Any]:
    """
    Check RAG service health.
    
    Returns:
        dict: Health status
    """
    try:
        stats = service.get_stats()
        
        # Check if all components are loaded
        is_healthy = (
            stats.get("enabled", False) and
            stats.get("metadata_loaded", False) and
            stats.get("embeddings_model_loaded", False) and
            stats.get("total_documents", 0) > 0
        )
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "enabled": stats.get("enabled", False),
            "components": {
                "faiss_index": stats.get("total_documents", 0) > 0,
                "metadata": stats.get("metadata_loaded", False),
                "embeddings_model": stats.get("embeddings_model_loaded", False),
            },
            "details": stats,
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e),
        }

"""
MCP Server for RAG System Integration.
Exposes RAG functionality via Model Context Protocol for external tools.
"""

import asyncio
import json
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from app.services.rag_service import RAGService
from app.db.athena_client import AthenaClient
from app.db.supabase_client import SupabaseClient
from app.core.config import get_logger
from config.settings import settings

logger = get_logger(__name__)


class RAGMCPServer:
    """
    MCP Server for RAG operations.
    
    Exposes RAG functionality as MCP tools for:
    - Vector search
    - Document retrieval
    - Question answering
    - Service statistics
    """
    
    def __init__(self):
        """Initialize MCP server with RAG service."""
        self.server = Server("finance-rag-mcp")
        self.rag_service: Optional[RAGService] = None
        
        # Register tools
        self._register_tools()
        
        # Register tool handlers
        self._register_handlers()
    
    def _register_tools(self) -> None:
        """Register available MCP tools."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available RAG tools."""
            return [
                Tool(
                    name="rag_query",
                    description=(
                        "Query the RAG system with a financial question. "
                        "Returns AI-generated answer with source citations from Vietnamese financial news."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "User's question about Vietnamese financial markets",
                            },
                            "api_key": {
                                "type": "string",
                                "description": "Gemini API key for LLM generation",
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of documents to retrieve (1-20)",
                                "default": 5,
                            },
                        },
                        "required": ["query", "api_key"],
                    },
                ),
                Tool(
                    name="rag_validate_key",
                    description="Validate a Gemini API key before using it for queries.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "api_key": {
                                "type": "string",
                                "description": "Gemini API key to validate",
                            },
                        },
                        "required": ["api_key"],
                    },
                ),
                Tool(
                    name="rag_stats",
                    description=(
                        "Get statistics about the RAG system including "
                        "number of documents, model info, and service status."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="rag_search",
                    description=(
                        "Search for relevant documents without LLM generation. "
                        "Returns top-k most similar documents to the query."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query",
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of documents to retrieve",
                                "default": 10,
                            },
                        },
                        "required": ["query"],
                    },
                ),
            ]
    
    def _register_handlers(self) -> None:
        """Register tool execution handlers."""
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """
            Execute MCP tool by name.
            
            Args:
                name: Tool name
                arguments: Tool arguments
                
            Returns:
                list[TextContent]: Tool execution results
            """
            # Initialize RAG service if not already done
            if self.rag_service is None:
                await self._initialize_service()
            
            try:
                if name == "rag_query":
                    return await self._handle_rag_query(arguments)
                elif name == "rag_validate_key":
                    return await self._handle_validate_key(arguments)
                elif name == "rag_stats":
                    return await self._handle_stats(arguments)
                elif name == "rag_search":
                    return await self._handle_search(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Tool execution failed: {str(e)}", exc_info=True)
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "error": str(e),
                            "tool": name,
                        }, ensure_ascii=False, indent=2)
                    )
                ]
    
    async def _initialize_service(self) -> None:
        """Initialize RAG service with dependencies."""
        logger.info("Initializing RAG service for MCP server...")
        athena_client = AthenaClient()
        supabase_client = SupabaseClient()
        self.rag_service = RAGService(athena_client, supabase_client)
        logger.info("RAG service initialized")
    
    async def _handle_rag_query(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle rag_query tool execution."""
        query = arguments.get("query", "")
        api_key = arguments.get("api_key", "")
        top_k = arguments.get("top_k", 5)
        
        result = self.rag_service.query(
            user_query=query,
            api_key=api_key,
            top_k=top_k,
            use_cache=True,
        )
        
        return [
            TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )
        ]
    
    async def _handle_validate_key(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle rag_validate_key tool execution."""
        api_key = arguments.get("api_key", "")
        
        result = self.rag_service.validate_api_key(api_key)
        
        return [
            TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )
        ]
    
    async def _handle_stats(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle rag_stats tool execution."""
        stats = self.rag_service.get_stats()
        
        return [
            TextContent(
                type="text",
                text=json.dumps(stats, ensure_ascii=False, indent=2)
            )
        ]
    
    async def _handle_search(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle rag_search tool execution."""
        query = arguments.get("query", "")
        top_k = arguments.get("top_k", 10)
        
        # Embed query
        query_embedding = self.rag_service.embeddings_model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False
        )
        
        # Search FAISS
        distances, indices = self.rag_service.index.search(
            query_embedding.astype('float32'),
            min(top_k, self.rag_service.index.ntotal)
        )
        
        # Retrieve documents with new metadata format
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.rag_service.metadata):
                doc = self.rag_service.metadata[idx]
                results.append({
                    'id': doc.get('row_id', idx),
                    'title': doc.get('title', ''),
                    'source': doc.get('source', ''),
                    'link': doc.get('link', ''),
                    'date': doc.get('date', ''),
                    'score': float(distance),
                })
        
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "query": query,
                    "top_k": top_k,
                    "results": results,
                }, ensure_ascii=False, indent=2)
            )
        ]
    
    async def run(self) -> None:
        """Run MCP server on stdio."""
        logger.info(f"Starting RAG MCP Server...")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point for MCP server."""
    if not settings.MCP_ENABLED:
        logger.error("MCP server is disabled in settings")
        return
    
    server = RAGMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())

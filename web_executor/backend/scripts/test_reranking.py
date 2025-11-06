"""
Test RAG with reranking
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.rag_service import RAGService
from app.db.athena_client import AthenaClient
from app.db.supabase_client import SupabaseClient

print("=" * 60)
print("TEST RAG WITH RERANKING (TOP-7)")
print("=" * 60)

rag = RAGService(AthenaClient(), SupabaseClient())

query = "Phân tích cổ phiếu HPG"
print(f"\n📝 Query: {query}")
print("\n🔍 Processing with reranking...")

try:
    # Test with dummy key - will fail at generation but retrieval+reranking should work
    result = rag.query(
        user_query=query,
        api_key="dummy_key",
        top_k=7  # Now default is 7
    )
    
    print(f"\n✅ Retrieval success: {result.get('success', False)}")
    
    if 'error' in result:
        print(f"\n⚠️  Generation error (expected with dummy key):")
        print(f"    {result['error'][:150]}...")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")

print("\n" + "=" * 60)
print("Check logs above for reranking details:")
print("  - Retrieved X candidate documents")
print("  - Reranked to top 7 documents")
print("  - Reranking: Top score = X.XXX, Bottom score = X.XXX")
print("=" * 60)

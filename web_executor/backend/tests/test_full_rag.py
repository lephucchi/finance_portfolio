"""
Full RAG system test with text content lookup
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.rag_service import RAGService
from app.db.athena_client import AthenaClient
from app.db.supabase_client import SupabaseClient

print("=" * 60)
print("TEST FULL RAG SYSTEM WITH TEXT CONTENT")
print("=" * 60)

# Initialize RAG
rag = RAGService(AthenaClient(), SupabaseClient())

# Test query
query = "Phân tích cổ phiếu HPG"
print(f"\n📝 Query: {query}")
print("\n🔍 Processing...")

# Note: Need real API key for actual response generation
# For now, just test retrieval part
try:
    result = rag.query(
        user_query=query,
        api_key="dummy_key_for_testing",  # Will fail at generation but retrieval should work
        top_k=3
    )
    
    print(f"\n✅ Success: {result.get('success')}")
    print(f"📊 Sources: {len(result.get('sources', []))}")
    
    if 'answer' in result:
        print(f"\n📄 Answer preview (first 300 chars):")
        print(result['answer'][:300])
        print("...")
    
    if 'sources' in result:
        print(f"\n📚 Sources:")
        for i, src in enumerate(result['sources'][:3], 1):
            print(f"   {i}. {src.get('source')} - {src.get('link')}")
    
    if 'error' in result:
        print(f"\n⚠️  Error: {result['error']}")
        
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

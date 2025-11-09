"""
Test RAG service directly without API
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rag_service import RAGService
from app.db.athena_client import AthenaClient
from app.db.supabase_client import SupabaseClient
from config.settings import settings

def main():
    print("=" * 60)
    print("🧪 TESTING RAG SERVICE DIRECTLY")
    print("=" * 60)
    
    # Create clients
    athena = AthenaClient()
    supabase = SupabaseClient()
    
    # Create RAG service
    print("\n1️⃣ Initializing RAG service...")
    rag = RAGService(athena, supabase)
    
    # Check components
    print("\n2️⃣ Checking components:")
    print(f"   FAISS index: {rag.index is not None} (vectors: {rag.index.ntotal if rag.index else 0})")
    print(f"   Metadata: {rag.metadata is not None} (count: {len(rag.metadata) if rag.metadata else 0})")
    print(f"   Embeddings model: {rag.embeddings_model is not None}")
    print(f"   Text cache: {rag.text_cache is not None} (docs: {len(rag.text_cache) if rag.text_cache else 0})")
    
    if rag.metadata and len(rag.metadata) > 0:
        print(f"\n3️⃣ Sample metadata record:")
        sample = rag.metadata[0]
        print(f"   Keys: {list(sample.keys())}")
        print(f"   Title: {sample.get('title', 'N/A')[:100]}")
        print(f"   Source: {sample.get('source', 'N/A')}")
        print(f"   Content length: {len(sample.get('content', ''))}")
    
    if rag.text_cache and len(rag.text_cache) > 0:
        print(f"\n4️⃣ Sample text cache:")
        first_id = list(rag.text_cache.keys())[0]
        first_text = rag.text_cache[first_id]
        print(f"   Doc ID: {first_id}")
        print(f"   Text preview: {first_text[:200]}...")
    
    # Test query (need real API key)
    test_api_key = input("\n5️⃣ Enter Gemini API key to test query (or press Enter to skip): ").strip()
    
    if test_api_key:
        print("\n6️⃣ Testing query...")
        query = "Phân tích cổ phiếu HPG"
        
        result = rag.query(
            user_query=query,
            api_key=test_api_key,
            top_k=3,
        )
        
        print(f"\n7️⃣ Result:")
        print(f"   Success: {result.get('success')}")
        if result.get('success'):
            print(f"   Answer length: {len(result.get('answer', ''))}")
            print(f"   Sources: {len(result.get('sources', []))}")
            print(f"\n   Answer preview:")
            print(f"   {result.get('answer', '')[:500]}...")
        else:
            print(f"   Error: {result.get('error')}")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()

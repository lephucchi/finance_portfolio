import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.rag_service import RAGService
from app.db.athena_client import AthenaClient
from app.db.supabase_client import SupabaseClient

rag = RAGService(AthenaClient(), SupabaseClient())
print(f"Text cache: {len(rag.text_cache) if rag.text_cache else 0} docs")
if len(rag.metadata) > 9474:
    doc = rag.metadata[9474]
    print(f"Metadata[9474] id: {doc.get('id')}")
    if rag.text_cache and doc.get('id') in rag.text_cache:
        text = rag.text_cache[doc.get('id')]
        print(f"Text found: {text[:100]}...")
    else:
        print("Text NOT found in cache")

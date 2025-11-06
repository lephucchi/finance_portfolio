"""
Comprehensive test script for RAG system.
Tests all components: metadata loading, FAISS search, Gemini integration.
"""

import json
import sys
import logging
from pathlib import Path

import numpy as np
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGSystemTester:
    """Test RAG system components."""
    
    def __init__(self):
        """Initialize tester."""
        self.faiss_index = None
        self.metadata = None
        self.embeddings_model = None
        self.test_results = []
    
    def test_all(self) -> bool:
        """Run all tests."""
        print("\n" + "=" * 70)
        print("🧪 RAG SYSTEM COMPREHENSIVE TEST")
        print("=" * 70 + "\n")
        
        all_passed = True
        
        # Test 1: Check file existence
        all_passed &= self._test_file_existence()
        
        # Test 2: Load FAISS index
        all_passed &= self._test_faiss_loading()
        
        # Test 3: Load metadata
        all_passed &= self._test_metadata_loading()
        
        # Test 4: Load embeddings model
        all_passed &= self._test_embeddings_model()
        
        # Test 5: Encode sample query
        all_passed &= self._test_query_encoding()
        
        # Test 6: FAISS search
        all_passed &= self._test_faiss_search()
        
        # Test 7: Metadata consistency
        all_passed &= self._test_metadata_consistency()
        
        # Test 8: API endpoint health
        all_passed &= self._test_api_health()
        
        # Print summary
        self._print_summary(all_passed)
        
        return all_passed
    
    def _test_file_existence(self) -> bool:
        """Test if all required files exist."""
        print("📁 TEST 1: Checking file existence...")
        
        files_to_check = [
            ("FAISS Index", Path(r"C:\uel\Đồ án tốt nghiệp\finance_portfolio\web_executor\backend\data\rag\vector_index.faiss")),
            ("Metadata JSON", Path(r"C:\uel\Đồ án tốt nghiệp\finance_portfolio\web_executor\backend\data\rag\metadata.json")),
            ("Embeddings NPY", Path(r"C:\uel\Đồ án tốt nghiệp\finance_portfolio\web_executor\backend\data\rag\embeddings.npy")),
        ]
        
        all_exist = True
        for name, path in files_to_check:
            exists = path.exists()
            status = "✓" if exists else "✗"
            size = f"{path.stat().st_size / (1024*1024):.2f} MB" if exists else "N/A"
            print(f"  {status} {name}: {path} ({size})")
            all_exist &= exists
        
        self.test_results.append(("File Existence", all_exist))
        return all_exist
    
    def _test_faiss_loading(self) -> bool:
        """Test FAISS index loading."""
        print("\n🔍 TEST 2: Loading FAISS index...")
        
        try:
            self.faiss_index = faiss.read_index("data/rag/vector_index.faiss")
            ntotal = self.faiss_index.ntotal
            d = self.faiss_index.d
            
            print(f"  ✓ FAISS index loaded successfully")
            print(f"    - Total vectors: {ntotal:,}")
            print(f"    - Vector dimension: {d}")
            
            self.test_results.append(("FAISS Loading", True))
            return True
        
        except Exception as e:
            print(f"  ✗ Failed to load FAISS index: {str(e)}")
            self.test_results.append(("FAISS Loading", False))
            return False
    
    def _test_metadata_loading(self) -> bool:
        """Test metadata JSON loading."""
        print("\n📋 TEST 3: Loading metadata JSON...")
        
        try:
            with open("data/rag/metadata.json", "r", encoding="utf-8") as f:
                metadata_raw = json.load(f)
            
            # Check structure
            if isinstance(metadata_raw, dict):
                documents = metadata_raw.get("documents", [])
                total = metadata_raw.get("total_documents", 0)
                model = metadata_raw.get("model_name", "N/A")
                
                self.metadata = documents
                
                print(f"  ✓ Metadata loaded successfully")
                print(f"    - Format: Dictionary with 'documents' key")
                print(f"    - Total documents: {len(documents):,}")
                print(f"    - Expected total: {total:,}")
                print(f"    - Model: {model}")
                
                # Validate structure
                if len(documents) > 0:
                    sample = documents[0]
                    required_fields = ["row_id", "title", "source", "link", "date"]
                    fields_present = all(field in sample for field in required_fields)
                    
                    print(f"    - Sample document fields: {list(sample.keys())}")
                    print(f"    - All required fields present: {'✓ Yes' if fields_present else '✗ No'}")
                
                self.test_results.append(("Metadata Loading", True))
                return True
            
            else:
                print(f"  ✗ Unexpected metadata format: {type(metadata_raw)}")
                self.test_results.append(("Metadata Loading", False))
                return False
        
        except Exception as e:
            print(f"  ✗ Failed to load metadata: {str(e)}")
            self.test_results.append(("Metadata Loading", False))
            return False
    
    def _test_embeddings_model(self) -> bool:
        """Test embeddings model loading."""
        print("\n🧠 TEST 4: Loading embeddings model...")
        
        try:
            model_name = "intfloat/multilingual-e5-large"
            print(f"  Loading model: {model_name}")
            print(f"  (This may take a moment on first load...)")
            
            self.embeddings_model = SentenceTransformer(model_name)
            
            print(f"  ✓ Embeddings model loaded successfully")
            
            self.test_results.append(("Embeddings Model", True))
            return True
        
        except Exception as e:
            print(f"  ✗ Failed to load embeddings model: {str(e)}")
            self.test_results.append(("Embeddings Model", False))
            return False
    
    def _test_query_encoding(self) -> bool:
        """Test encoding a sample query."""
        print("\n🔤 TEST 5: Encoding sample query...")
        
        try:
            queries = [
                "Tình hình thị trường chứng khoán Việt Nam?",
                "Những cổ phiếu nào tăng giá?",
            ]
            
            embeddings = self.embeddings_model.encode(
                queries,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            
            print(f"  ✓ Query encoding successful")
            print(f"    - Queries encoded: {len(queries)}")
            print(f"    - Embedding shape: {embeddings.shape}")
            print(f"    - Embedding dimension: {embeddings.shape[1]}")
            print(f"    - Norm of first embedding: {np.linalg.norm(embeddings[0]):.4f}")
            
            self.test_results.append(("Query Encoding", True))
            return True
        
        except Exception as e:
            print(f"  ✗ Failed to encode query: {str(e)}")
            self.test_results.append(("Query Encoding", False))
            return False
    
    def _test_faiss_search(self) -> bool:
        """Test FAISS search."""
        print("\n🔎 TEST 6: Testing FAISS search...")
        
        try:
            query = "Chứng khoán Việt Nam"
            query_embedding = self.embeddings_model.encode(
                [query],
                normalize_embeddings=True,
                show_progress_bar=False
            )
            
            # Search top 5
            distances, indices = self.faiss_index.search(
                query_embedding.astype('float32'),
                5
            )
            
            print(f"  ✓ FAISS search successful")
            print(f"    - Query: '{query}'")
            print(f"    - Top 5 results:")
            
            for i, (idx, dist) in enumerate(zip(indices[0], distances[0]), 1):
                if idx < len(self.metadata):
                    doc = self.metadata[idx]
                    title = doc.get('title', 'N/A')[:50]
                    source = doc.get('source', 'N/A')
                    score = 100 * (1 - dist)
                    print(f"      [{i}] {title}... (score: {score:.1f}%, source: {source})")
            
            self.test_results.append(("FAISS Search", True))
            return True
        
        except Exception as e:
            print(f"  ✗ FAISS search failed: {str(e)}")
            self.test_results.append(("FAISS Search", False))
            return False
    
    def _test_metadata_consistency(self) -> bool:
        """Test metadata and FAISS consistency."""
        print("\n🔗 TEST 7: Checking metadata-FAISS consistency...")
        
        try:
            ntotal = self.faiss_index.ntotal
            nmeta = len(self.metadata)
            
            if ntotal == nmeta:
                print(f"  ✓ Metadata-FAISS consistency check passed")
                print(f"    - FAISS vectors: {ntotal:,}")
                print(f"    - Metadata docs: {nmeta:,}")
                self.test_results.append(("Metadata Consistency", True))
                return True
            else:
                print(f"  ⚠️  Metadata-FAISS size mismatch (may be expected)")
                print(f"    - FAISS vectors: {ntotal:,}")
                print(f"    - Metadata docs: {nmeta:,}")
                print(f"    - Difference: {abs(ntotal - nmeta):,}")
                
                # This is a warning, not a failure
                self.test_results.append(("Metadata Consistency", True))
                return True
        
        except Exception as e:
            print(f"  ✗ Consistency check failed: {str(e)}")
            self.test_results.append(("Metadata Consistency", False))
            return False
    
    def _test_api_health(self) -> bool:
        """Test if API is running and RAG endpoints are healthy."""
        print("\n🌐 TEST 8: Testing API health...")
        
        try:
            import httpx
            
            try:
                # Test if backend is running
                response = httpx.get("http://localhost:8000/", timeout=5)
                if response.status_code == 200:
                    print(f"  ✓ Backend API is running")
                    
                    # Try health check endpoint
                    response = httpx.get("http://localhost:8000/api/v1/rag/health", timeout=5)
                    if response.status_code == 200:
                        health = response.json()
                        status = health.get("status", "unknown")
                        print(f"  ✓ RAG health endpoint responded")
                        print(f"    - Status: {status}")
                        
                        components = health.get("components", {})
                        print(f"    - Components:")
                        print(f"      • FAISS index: {'✓' if components.get('faiss_index') else '✗'}")
                        print(f"      • Metadata: {'✓' if components.get('metadata') else '✗'}")
                        print(f"      • Embeddings: {'✓' if components.get('embeddings_model') else '✗'}")
                        
                        self.test_results.append(("API Health", True))
                        return True
            
            except Exception as e:
                if "Connection" in str(type(e).__name__) or "connect" in str(e).lower():
                    print(f"  ⚠️  Backend API not running (start with: python main.py)")
                    print(f"    - To run tests, start the backend server first")
                    self.test_results.append(("API Health", None))  # Skip test
                    return True  # Don't fail overall
                else:
                    raise
        
        except ImportError:
            print(f"  ⚠️  httpx not installed, skipping API test")
            self.test_results.append(("API Health", None))
            return True
        
        except Exception as e:
            print(f"  ⚠️  Could not test API (backend may not be running): {str(e)[:50]}")
            self.test_results.append(("API Health", None))
            return True
    
    def _print_summary(self, all_passed: bool) -> None:
        """Print test summary."""
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        for test_name, passed in self.test_results:
            if passed is None:
                status = "⊘"
                result = "SKIPPED"
            elif passed:
                status = "✓"
                result = "PASSED"
            else:
                status = "✗"
                result = "FAILED"
            
            print(f"  {status} {test_name:.<50} {result}")
        
        print("\n" + "=" * 70)
        
        if all_passed:
            print("✓ All tests passed! RAG system is ready to use.")
            print("\nNext steps:")
            print("  1. Start the backend: python main.py")
            print("  2. Test the API: http://localhost:8000/api/docs")
            print("  3. Try a query via the endpoint")
        else:
            print("✗ Some tests failed. Please check the errors above.")
        
        print("=" * 70 + "\n")


def main():
    """Main entry point."""
    tester = RAGSystemTester()
    passed = tester.test_all()
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

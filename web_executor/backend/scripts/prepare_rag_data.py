"""
Script to convert RAG metadata from pickle to JSON format.
Handles large metadata files by creating a manageable JSON version.
"""

import os
import json
import pickle
import numpy as np
from pathlib import Path

# Paths
RAG_SOURCE = Path(r"c:\uel\Đồ án tốt nghiệp\rag_system\data\embeddings\ver_06\rag_outputs")
RAG_DEST = Path(r"c:\uel\Đồ án tốt nghiệp\finance_portfolio\web_executor\backend\data\rag")

print("=" * 60)
print("RAG Data Preparation Script")
print("=" * 60)

# Create destination directory
RAG_DEST.mkdir(parents=True, exist_ok=True)

# Check source files
print("\n📂 Checking source files...")
embeddings_file = RAG_SOURCE / "embeddings.npy"
metadata_file = RAG_SOURCE / "metadata.json"

if embeddings_file.exists():
    print(f"✅ Found: {embeddings_file}")
    embeddings = np.load(embeddings_file)
    print(f"   Shape: {embeddings.shape}")
else:
    print(f"❌ Not found: {embeddings_file}")
    embeddings = None

if metadata_file.exists():
    file_size_mb = metadata_file.stat().st_size / (1024 * 1024)
    print(f"✅ Found: {metadata_file} ({file_size_mb:.2f} MB)")
    
    if file_size_mb > 50:
        print(f"⚠️  File is large ({file_size_mb:.2f} MB), may need processing")
else:
    print(f"❌ Not found: {metadata_file}")

# Check if FAISS index exists in different location
possible_faiss_paths = [
    RAG_SOURCE / "faiss_index.bin",
    RAG_SOURCE / "faiss_metadata.bin",
    RAG_SOURCE / "index.faiss",
]

faiss_index_path = None
for path in possible_faiss_paths:
    if path.exists():
        print(f"✅ Found FAISS index: {path}")
        faiss_index_path = path
        break

if not faiss_index_path:
    print("\n⚠️  No FAISS index found. You may need to create one from embeddings.")
    print("Expected locations:")
    for path in possible_faiss_paths:
        print(f"   - {path}")

# Create FAISS index if we have embeddings but no index
if embeddings is not None and faiss_index_path is None:
    print("\n🔨 Creating FAISS index from embeddings...")
    import faiss
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
    
    # Normalize embeddings
    faiss.normalize_L2(embeddings)
    
    # Add to index
    index.add(embeddings.astype('float32'))
    
    # Save index
    faiss_dest = RAG_DEST / "faiss_index.bin"
    faiss.write_index(index, str(faiss_dest))
    print(f"✅ Created FAISS index: {faiss_dest}")
    print(f"   Total vectors: {index.ntotal}")
    print(f"   Dimension: {index.d}")
elif faiss_index_path:
    # Copy existing FAISS index
    import shutil
    faiss_dest = RAG_DEST / "faiss_index.bin"
    shutil.copy2(faiss_index_path, faiss_dest)
    print(f"✅ Copied FAISS index to: {faiss_dest}")

# Process metadata
print("\n📝 Processing metadata...")
if metadata_file.exists():
    try:
        # Try loading as JSON first
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"✅ Loaded metadata (JSON format)")
        print(f"   Keys: {list(metadata.keys())}")
        
        # Check if we need to limit size
        if 'texts' in metadata:
            total_docs = len(metadata['texts'])
            print(f"   Total documents: {total_docs}")
            
            # Create a smaller version for testing if needed
            if total_docs > 10000:
                print("\n⚠️  Large dataset detected. Creating full and sample versions...")
                
                # Save full version
                metadata_full = RAG_DEST / "metadata_full.json"
                with open(metadata_full, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False)
                print(f"✅ Saved full metadata: {metadata_full}")
                
                # Create sample version (first 1000 docs)
                metadata_sample = {
                    'ids': metadata['ids'][:1000],
                    'texts': metadata['texts'][:1000],
                }
                metadata_dest = RAG_DEST / "metadata.json"
                with open(metadata_dest, 'w', encoding='utf-8') as f:
                    json.dump(metadata_sample, f, ensure_ascii=False, indent=2)
                print(f"✅ Saved sample metadata (1000 docs): {metadata_dest}")
            else:
                # Save directly
                metadata_dest = RAG_DEST / "metadata.json"
                with open(metadata_dest, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                print(f"✅ Saved metadata: {metadata_dest}")
        
    except json.JSONDecodeError:
        print("⚠️  Not a JSON file, trying pickle format...")
        
        # Try pickle format
        try:
            with open(metadata_file, 'rb') as f:
                metadata = pickle.load(f)
            
            print(f"✅ Loaded metadata (pickle format)")
            print(f"   Keys: {list(metadata.keys())}")
            
            # Convert to JSON
            metadata_json = {
                'ids': metadata.get('ids', []),
                'texts': metadata.get('texts', []),
            }
            
            metadata_dest = RAG_DEST / "metadata.json"
            with open(metadata_dest, 'w', encoding='utf-8') as f:
                json.dump(metadata_json, f, ensure_ascii=False, indent=2)
            print(f"✅ Converted and saved metadata: {metadata_dest}")
            
        except Exception as e:
            print(f"❌ Failed to load metadata: {str(e)}")

# Copy embeddings if they exist
if embeddings is not None:
    embeddings_dest = RAG_DEST / "embeddings.npy"
    np.save(embeddings_dest, embeddings)
    print(f"\n✅ Copied embeddings: {embeddings_dest}")
    print(f"   Shape: {embeddings.shape}")

# Summary
print("\n" + "=" * 60)
print("📊 SUMMARY")
print("=" * 60)

dest_files = list(RAG_DEST.glob("*"))
if dest_files:
    print("\n✅ Successfully prepared RAG data:")
    for file in dest_files:
        if file.is_file():
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"   - {file.name} ({size_mb:.2f} MB)")
    
    print("\n📝 Next steps:")
    print("   1. Update .env file with correct paths")
    print("   2. Install dependencies: pip install -r requirements.txt")
    print("   3. Start backend: python main.py")
    print("   4. Test RAG endpoint: GET http://localhost:8000/api/v1/rag/stats")
else:
    print("\n❌ No files were created. Check the source directory and try again.")

print("=" * 60)

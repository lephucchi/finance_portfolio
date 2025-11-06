"""
Rebuild metadata.parquet by mapping combined_text from CSV to metadata rows
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Paths
RAG_DIR = Path(__file__).parent.parent / "data" / "rag"
METADATA_PATH = RAG_DIR / "metadata.parquet"
CSV_PATH = RAG_DIR / "financial_news_cleaned_20251101.csv"
OUTPUT_PATH = RAG_DIR / "metadata_with_text.parquet"

def main():
    print("=" * 60)
    print("🔧 REBUILD METADATA WITH TEXT CONTENT")
    print("=" * 60)
    
    # 1. Load metadata
    print("\n📂 Loading metadata.parquet...")
    metadata_df = pd.read_parquet(METADATA_PATH)
    print(f"   ✅ Loaded {len(metadata_df):,} rows")
    print(f"   Columns: {metadata_df.columns.tolist()}")
    
    # 2. Load CSV
    print("\n📂 Loading CSV with combined_text...")
    csv_df = pd.read_csv(CSV_PATH)
    print(f"   ✅ Loaded {len(csv_df):,} rows")
    print(f"   Columns: {csv_df.columns.tolist()}")
    
    # 3. Create id -> combined_text mapping
    print("\n🔗 Creating ID -> text mapping...")
    text_map = dict(zip(csv_df['id'], csv_df['combined_text']))
    print(f"   ✅ Created mapping for {len(text_map):,} documents")
    
    # 4. Map combined_text to metadata
    print("\n🔄 Mapping combined_text to metadata rows...")
    metadata_df['combined_text'] = metadata_df['id'].map(text_map)
    
    # Check results
    has_text = metadata_df['combined_text'].notna().sum()
    missing_text = metadata_df['combined_text'].isna().sum()
    print(f"   ✅ Mapped text for {has_text:,} rows ({has_text/len(metadata_df)*100:.2f}%)")
    print(f"   ⚠️  Missing text for {missing_text:,} rows ({missing_text/len(metadata_df)*100:.2f}%)")
    
    # Fill missing with empty string
    metadata_df['combined_text'] = metadata_df['combined_text'].fillna("")
    
    # 5. Preview
    print("\n📋 Preview of first row with text:")
    first_row = metadata_df.iloc[0]
    print(f"   ID: {first_row['id']}")
    print(f"   Title: {first_row['title']}")
    print(f"   Text preview: {first_row['combined_text'][:200]}...")
    
    # 6. Save
    print(f"\n💾 Saving to {OUTPUT_PATH.name}...")
    metadata_df.to_parquet(OUTPUT_PATH, index=False)
    print(f"   ✅ Saved {len(metadata_df):,} rows")
    
    # 7. Verify
    print("\n✅ Verifying saved file...")
    verify_df = pd.read_parquet(OUTPUT_PATH)
    print(f"   Shape: {verify_df.shape}")
    print(f"   Columns: {verify_df.columns.tolist()}")
    print(f"   Has combined_text: {'combined_text' in verify_df.columns}")
    
    print("\n" + "=" * 60)
    print("🎉 DONE! Metadata rebuilt successfully")
    print("=" * 60)
    print(f"\n📝 Next steps:")
    print(f"   1. Backup old metadata: metadata.parquet -> metadata_old.parquet")
    print(f"   2. Replace: metadata_with_text.parquet -> metadata.parquet")
    print(f"   3. Convert to JSON: python scripts/convert_metadata.py")

if __name__ == "__main__":
    main()

"""
Convert metadata.parquet to optimized JSON format for RAG system.

This script loads the parquet metadata and creates an optimized JSON file
that maps vector indices to document metadata (title, source, link, date).

Usage:
    python scripts/convert_metadata.py
"""

import json
import os
import logging
from pathlib import Path

import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def convert_metadata() -> None:
    """
    Convert metadata.parquet to optimized JSON format.
    
    The FAISS index has 328,652 vectors (one per metadata row).
    We create a JSON file that maps each vector index to its metadata + content.
    """
    # File paths
    parquet_path = Path("data/rag/metadata.parquet")
    json_output_path = Path("data/rag/metadata.json")
    backup_path = Path("data/rag/metadata_backup.json")
    
    if not parquet_path.exists():
        logger.error(f"Parquet file not found: {parquet_path}")
        raise FileNotFoundError(f"Parquet file not found: {parquet_path}")
    
    logger.info(f"Reading metadata from: {parquet_path}")
    
    # Read parquet file
    df = pd.read_parquet(parquet_path)
    logger.info(f"Loaded {len(df)} metadata records")
    logger.info(f"Columns: {df.columns.tolist()}")
    
    # Check if combined_text exists
    if 'combined_text' not in df.columns:
        logger.warning("⚠️  'combined_text' column not found! Content will be empty.")
        df['combined_text'] = ""
    
    # Display sample data
    logger.info("Sample data:")
    logger.info(df.head())
    
    # Create metadata list optimized for RAG with content
    metadata_list = []
    
    for idx, row in df.iterrows():
        metadata_entry = {
            "id": str(row.get("id", "")),  # UUID for mapping to CSV
            "row_id": int(row.get("row_id", idx)),
            "title": str(row.get("title", "")).strip(),
            "source": str(row.get("source", "")).strip(),
            "link": str(row.get("link", "")).strip(),
            "date": str(row.get("date", "")).strip(),
            "content": str(row.get("combined_text", "")).strip()[:2000],  # Limit to 2000 chars
        }
        metadata_list.append(metadata_entry)
        
        # Log progress
        if (idx + 1) % 50000 == 0:
            logger.info(f"Processed {idx + 1}/{len(df)} records")
    
    # Create final JSON structure
    metadata_dict = {
        "total_documents": len(metadata_list),
        "model_name": "intfloat/multilingual-e5-large",
        "created_at": pd.Timestamp.now().isoformat(),
        "vector_dimension": 1024,  # e5-large produces 1024-dim vectors
        "documents": metadata_list,
    }
    
    # Backup existing JSON if it exists
    if json_output_path.exists():
        logger.info(f"Backing up existing metadata to: {backup_path}")
        os.rename(json_output_path, backup_path)
    
    # Write JSON file
    logger.info(f"Writing metadata to: {json_output_path}")
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(metadata_dict, f, ensure_ascii=False, indent=2)
    
    # Verify file size
    file_size_mb = json_output_path.stat().st_size / (1024 * 1024)
    logger.info(f"✓ Metadata JSON created: {file_size_mb:.2f} MB")
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("CONVERSION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total documents: {metadata_dict['total_documents']}")
    logger.info(f"Model: {metadata_dict['model_name']}")
    logger.info(f"Vector dimension: {metadata_dict['vector_dimension']}")
    logger.info(f"File size: {file_size_mb:.2f} MB")
    logger.info(f"Output: {json_output_path}")
    logger.info(f"Content included: {'combined_text' in df.columns}")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        convert_metadata()
        logger.info("✓ Conversion completed successfully!")
    except Exception as e:
        logger.error(f"✗ Conversion failed: {str(e)}", exc_info=True)
        exit(1)

"""
Rebuild metadata.parquet from CSV with combined_text column.
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rebuild_metadata():
    """Rebuild parquet from CSV source with content."""
    
    # CSV file path
    csv_path = Path("data/rag/financial_news_cleaned_20251101.csv")
    
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return
    
    # Read CSV
    logger.info(f"Reading CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df)} rows")
    logger.info(f"Columns: {df.columns.tolist()}")
    
    # Check for required columns
    required_cols = ['combined_text', 'source', 'link', 'title', 'date']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        logger.error(f"Missing columns: {missing}")
        return
    
    # Add row_id if not exists
    if 'row_id' not in df.columns:
        df['row_id'] = range(len(df))
    
    if 'id' not in df.columns:
        import uuid
        df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
    
    # Select and reorder columns
    output_df = df[['id', 'row_id', 'title', 'link', 'source', 'date', 'combined_text']]
    
    # Save to parquet
    output_path = Path("data/rag/metadata.parquet")
    backup_path = Path("data/rag/metadata_old.parquet")
    
    if output_path.exists():
        logger.info(f"Backing up old parquet to: {backup_path}")
        output_path.rename(backup_path)
    
    logger.info(f"Writing new parquet: {output_path}")
    output_df.to_parquet(output_path, index=False)
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info(f"✓ New parquet created: {file_size_mb:.2f} MB")
    logger.info(f"Total rows: {len(output_df)}")
    logger.info(f"Columns: {output_df.columns.tolist()}")
    
    # Show sample
    logger.info("\nSample row:")
    sample = output_df.iloc[0]
    for col in output_df.columns:
        val = sample[col]
        if isinstance(val, str) and len(val) > 100:
            logger.info(f"  {col}: {val[:100]}...")
        else:
            logger.info(f"  {col}: {val}")

if __name__ == "__main__":
    rebuild_metadata()

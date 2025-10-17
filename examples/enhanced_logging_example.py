"""
Example: Enhanced Logging in Bronze Layer Pipeline
"""

from utils.enhanced_logger import get_enhanced_logger, log_pipeline_start, log_pipeline_success, log_pipeline_error
import os
import time
import random
from datetime import datetime

def enhanced_bronze_news_example():
    """Example of using enhanced logging in bronze news pipeline"""
    
    # Initialize enhanced logger
    logger = get_enhanced_logger("bronze_news_pipeline", "INFO")
    
    # Start pipeline operation
    metadata = log_pipeline_start(
        logger, 
        pipeline_name="news_extraction",
        layer="bronze", 
        operation="extract_and_store"
    )
    
    try:
        # Simulate data extraction
        logger.log_progress(metadata, "Starting news data extraction")
        time.sleep(1)  # Simulate work
        
        # Log source discovery
        sources = ["vnexpress", "cafef", "dantri", "tuoitre"]
        logger.log_progress(metadata, f"Discovered {len(sources)} news sources", 
                          sources=sources, discovery_time=datetime.now().isoformat())
        
        # Simulate extraction from each source
        extracted_files = []
        s3_paths = []
        total_articles = 0
        
        for source in sources:
            logger.log_progress(metadata, f"Extracting from {source}")
            time.sleep(0.5)  # Simulate extraction
            
            # Simulate results
            article_count = random.randint(10, 50)
            total_articles += article_count
            
            # Generate file paths
            file_path = f"/tmp/bronze/news/{source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            s3_path = f"bronze/news/raw/{source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            extracted_files.append(file_path)
            s3_paths.append(s3_path)
            
            logger.log_progress(metadata, f"Extracted {article_count} articles from {source}",
                              source=source, article_count=article_count, file_path=file_path)
        
        # Log file operations
        logger.log_file_operations(metadata, file_paths=extracted_files, s3_paths=s3_paths)
        
        # Simulate data validation
        logger.log_progress(metadata, "Performing data quality checks")
        time.sleep(0.5)
        
        # Simulate some validation metrics
        quality_metrics = {
            "duplicate_articles": random.randint(0, 5),
            "invalid_dates": random.randint(0, 2),
            "missing_content": random.randint(0, 3),
            "data_completeness_score": round(random.uniform(0.85, 0.98), 3),
            "source_coverage": f"{len(sources)}/4 sources active"
        }
        
        # Log data quality
        error_count = quality_metrics["duplicate_articles"] + quality_metrics["invalid_dates"] + quality_metrics["missing_content"]
        logger.log_data_quality(
            metadata,
            source_count=total_articles + error_count,
            target_count=total_articles,
            error_count=error_count,
            quality_metrics=quality_metrics
        )
        
        # Simulate S3 upload
        logger.log_progress(metadata, "Uploading to S3")
        time.sleep(1)
        
        # Success logging
        final_metadata = log_pipeline_success(logger, metadata, total_articles + error_count, total_articles)
        
        print("\n🎉 Pipeline completed successfully!")
        print(f"📊 Final Stats:")
        print(f"   - Total Articles Processed: {total_articles + error_count}")
        print(f"   - Valid Articles: {total_articles}")
        print(f"   - Error Count: {error_count}")
        print(f"   - Files Created: {len(extracted_files)}")
        print(f"   - S3 Objects: {len(s3_paths)}")
        
        return final_metadata
        
    except Exception as e:
        # Error logging
        context = {
            "total_sources": len(sources) if 'sources' in locals() else 0,
            "files_processed": len(extracted_files) if 'extracted_files' in locals() else 0,
            "current_operation": "extraction"
        }
        
        final_metadata = log_pipeline_error(logger, metadata, e, context)
        
        print(f"\n❌ Pipeline failed: {str(e)}")
        return final_metadata

def enhanced_silver_transformation_example():
    """Example of enhanced logging in silver layer transformation"""
    
    logger = get_enhanced_logger("silver_transformation", "INFO")
    
    metadata = log_pipeline_start(
        logger,
        pipeline_name="news_transformation",
        layer="silver",
        operation="clean_and_transform"
    )
    
    try:
        # Simulate reading from bronze
        logger.log_progress(metadata, "Reading bronze layer data")
        bronze_files = 45  # Simulate file count
        
        # Simulate transformation steps
        transformations = [
            ("text_cleaning", "Cleaning and normalizing text"),
            ("date_standardization", "Standardizing date formats"),
            ("category_mapping", "Mapping news categories"),
            ("sentiment_analysis", "Analyzing sentiment scores"),
            ("deduplication", "Removing duplicate articles")
        ]
        
        processed_records = bronze_files * 25  # Simulate records
        
        for step, description in transformations:
            logger.log_progress(metadata, description)
            time.sleep(0.3)
            
            # Simulate some metrics for each step
            step_metrics = {
                f"{step}_processing_time": round(random.uniform(0.1, 0.5), 2),
                f"{step}_records_affected": random.randint(10, processed_records),
                f"{step}_accuracy_score": round(random.uniform(0.88, 0.99), 3)
            }
            
            for key, value in step_metrics.items():
                metadata.metrics[key] = value
        
        # Quality metrics
        quality_metrics = {
            "transformation_accuracy": 0.945,
            "data_completeness": 0.987,
            "duplicate_removal_rate": 0.034,
            "sentiment_confidence_avg": 0.823
        }
        
        # Final count after transformations
        final_count = int(processed_records * 0.95)  # Some records removed
        error_count = processed_records - final_count
        
        logger.log_data_quality(
            metadata,
            source_count=processed_records,
            target_count=final_count,
            error_count=error_count,
            quality_metrics=quality_metrics
        )
        
        # S3 paths for silver layer
        silver_s3_paths = [
            f"silver/news/cleaned/{datetime.now().strftime('%Y/%m/%d')}/news_cleaned.parquet",
            f"silver/news/sentiment/{datetime.now().strftime('%Y/%m/%d')}/news_sentiment.parquet",
            f"silver/news/categories/{datetime.now().strftime('%Y/%m/%d')}/news_categorized.parquet"
        ]
        
        logger.log_file_operations(metadata, s3_paths=silver_s3_paths)
        
        final_metadata = log_pipeline_success(logger, metadata, processed_records, final_count)
        
        print(f"\n✨ Silver transformation completed!")
        print(f"📈 Transformation Stats:")
        print(f"   - Input Records: {processed_records}")
        print(f"   - Output Records: {final_count}")
        print(f"   - Quality Score: {quality_metrics['transformation_accuracy']:.1%}")
        
        return final_metadata
        
    except Exception as e:
        context = {"transformation_step": "unknown", "records_processed": 0}
        return log_pipeline_error(logger, metadata, e, context)

def create_pipeline_summary():
    """Create a summary report for all pipelines"""
    logger = get_enhanced_logger("pipeline_summary", "INFO")
    
    print("\n📋 Creating Pipeline Summary Reports...")
    
    pipelines = ["news_extraction", "stock_extraction", "news_transformation", "gold_analysis"]
    
    for pipeline in pipelines:
        print(f"\n--- {pipeline.upper()} SUMMARY ---")
        summary = logger.create_summary_report(pipeline, timeframe_hours=24)
        
        if summary:
            print(f"✅ Report generated for {pipeline}")
        else:
            print(f"⚠️  No data available for {pipeline}")

if __name__ == "__main__":
    print("🚀 Testing Enhanced Logging System")
    print("=" * 50)
    
    # Test bronze layer logging
    print("\n1️⃣  Testing Bronze Layer Logging...")
    bronze_result = enhanced_bronze_news_example()
    
    # Test silver layer logging  
    print("\n2️⃣  Testing Silver Layer Logging...")
    silver_result = enhanced_silver_transformation_example()
    
    # Create summary reports
    print("\n3️⃣  Creating Summary Reports...")
    create_pipeline_summary()
    
    print("\n🎯 Enhanced Logging Test Complete!")
    print("\nNext steps:")
    print("- Integrate enhanced_logger into existing DAG files")
    print("- Add enhanced logging to bronze_layer_pipeline.py")
    print("- Add enhanced logging to silver_layer_pipeline.py") 
    print("- Add enhanced logging to gold_layer_pipeline.py")
    print("- Update master_dag.py with summary reporting")
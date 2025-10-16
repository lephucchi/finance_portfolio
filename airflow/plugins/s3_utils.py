"""
S3 Connection and Utilities for Airflow DAGs
Provides centralized S3 operations and connection management

Author: Banking Portfolio Team
Version: 2.0
Date: October 2025
"""

import os
import logging
from datetime import datetime
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.exceptions import AirflowException
import json

class S3Manager:
    """Centralized S3 operations manager"""
    
    def __init__(self, aws_conn_id='aws_default'):
        self.aws_conn_id = aws_conn_id
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'bankanalystportfolio')
        self.s3_hook = None
        
    def get_s3_hook(self):
        """Get S3Hook instance with error handling"""
        if self.s3_hook is None:
            try:
                self.s3_hook = S3Hook(aws_conn_id=self.aws_conn_id)
                logging.info(f"✅ S3Hook initialized for bucket: {self.bucket_name}")
            except Exception as e:
                logging.error(f"❌ Failed to initialize S3Hook: {str(e)}")
                raise AirflowException(f"S3 connection failed: {str(e)}")
        return self.s3_hook
    
    def check_bucket_access(self):
        """Verify bucket access and permissions"""
        try:
            s3_hook = self.get_s3_hook()
            
            if not s3_hook.check_for_bucket(self.bucket_name):
                raise AirflowException(f"Bucket {self.bucket_name} not found or not accessible")
            
            # Test write permission
            test_key = f"health-check/access-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
            s3_hook.load_string(
                string_data="Access test successful",
                key=test_key,
                bucket_name=self.bucket_name,
                replace=True
            )
            
            # Clean up test file
            s3_hook.delete_objects(bucket=self.bucket_name, keys=[test_key])
            
            logging.info(f"✅ S3 bucket access verified: {self.bucket_name}")
            return True
            
        except Exception as e:
            logging.error(f"❌ S3 bucket access check failed: {str(e)}")
            raise AirflowException(f"S3 access verification failed: {str(e)}")
    
    def upload_json_data(self, data, s3_key, replace=True):
        """Upload JSON data to S3 with error handling"""
        try:
            s3_hook = self.get_s3_hook()
            
            json_content = json.dumps(data, indent=2, ensure_ascii=False)
            
            s3_hook.load_string(
                string_data=json_content,
                key=s3_key,
                bucket_name=self.bucket_name,
                replace=replace
            )
            
            logging.info(f"📤 Uploaded JSON data to s3://{self.bucket_name}/{s3_key}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to upload {s3_key}: {str(e)}")
            raise AirflowException(f"S3 upload failed: {str(e)}")
    
    def upload_string_data(self, content, s3_key, replace=True):
        """Upload string content to S3"""
        try:
            s3_hook = self.get_s3_hook()
            
            s3_hook.load_string(
                string_data=content,
                key=s3_key,
                bucket_name=self.bucket_name,
                replace=replace
            )
            
            logging.info(f"📤 Uploaded string data to s3://{self.bucket_name}/{s3_key}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to upload {s3_key}: {str(e)}")
            raise AirflowException(f"S3 upload failed: {str(e)}")
    
    def check_file_exists(self, s3_key):
        """Check if file exists in S3"""
        try:
            s3_hook = self.get_s3_hook()
            exists = s3_hook.check_for_key(key=s3_key, bucket_name=self.bucket_name)
            logging.info(f"🔍 File check {s3_key}: {'EXISTS' if exists else 'NOT FOUND'}")
            return exists
            
        except Exception as e:
            logging.error(f"❌ Failed to check file {s3_key}: {str(e)}")
            return False
    
    def list_files_with_prefix(self, prefix):
        """List files with given prefix"""
        try:
            s3_hook = self.get_s3_hook()
            files = s3_hook.list_keys(bucket_name=self.bucket_name, prefix=prefix)
            
            if files:
                logging.info(f"📁 Found {len(files)} files with prefix: {prefix}")
                return files
            else:
                logging.info(f"📁 No files found with prefix: {prefix}")
                return []
                
        except Exception as e:
            logging.error(f"❌ Failed to list files with prefix {prefix}: {str(e)}")
            return []
    
    def create_folder_structure(self):
        """Create required folder structure in S3"""
        try:
            folder_structure = [
                'bronze/stocks/raw/',
                'bronze/stocks/metadata/',
                'bronze/news/raw/',
                'bronze/news/metadata/',
                'bronze/others/raw/',
                'bronze/others/metadata/',
                'silver/stocks/processed/',
                'silver/stocks/metadata/',
                'silver/news/processed/',
                'silver/news/metadata/',
                'silver/others/processed/',
                'silver/others/metadata/',
                'gold/analytics/',
                'gold/serving/',
                'gold/metadata/',
                'rag/input/',
                'rag/processed/',
                'rag/model/',
                'rag/vectordb/',
                'rag/vectordb/backup/',
                'rag/logs/',
                'logs/master-dag/',
                'logs/bronze-dag/',
                'logs/silver-dag/',
                'logs/gold-dag/',
                'logs/rag-dag/',
                'health-check/'
            ]
            
            s3_hook = self.get_s3_hook()
            
            for folder in folder_structure:
                readme_key = f"{folder}README.md"
                readme_content = f"# {folder}\n\nCreated by Airflow DAG at {datetime.now()}"
                
                if not self.check_file_exists(readme_key):
                    s3_hook.load_string(
                        string_data=readme_content,
                        key=readme_key,
                        bucket_name=self.bucket_name
                    )
                    logging.info(f"📁 Created folder: {folder}")
            
            logging.info("✅ S3 folder structure verified/created")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to create folder structure: {str(e)}")
            raise AirflowException(f"Folder structure creation failed: {str(e)}")

# Utility functions for DAGs
def get_s3_manager():
    """Get S3Manager instance"""
    return S3Manager()

def validate_s3_connection():
    """Validate S3 connection for DAG tasks"""
    s3_manager = get_s3_manager()
    return s3_manager.check_bucket_access()

def ensure_s3_structure():
    """Ensure S3 folder structure exists"""
    s3_manager = get_s3_manager()
    return s3_manager.create_folder_structure()

def upload_data_to_s3(data, s3_key):
    """Upload data to S3 with proper error handling"""
    s3_manager = get_s3_manager()
    return s3_manager.upload_json_data(data, s3_key)

# Data quality utilities
class DataQualityChecker:
    """Data quality validation utilities"""
    
    @staticmethod
    def validate_stock_data(stock_records):
        """Validate stock data quality"""
        validation_results = {
            'passed': True,
            'issues': [],
            'quality_score': 0.0,
            'record_count': len(stock_records)
        }
        
        if not stock_records:
            validation_results['passed'] = False
            validation_results['issues'].append("No stock records found")
            return validation_results
        
        # Check required fields
        required_fields = ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume']
        issues = []
        
        for i, record in enumerate(stock_records):
            # Check missing fields
            missing_fields = [field for field in required_fields if field not in record]
            if missing_fields:
                issues.append(f"Record {i}: Missing fields {missing_fields}")
            
            # Check data types and ranges
            if 'open' in record and record['open'] <= 0:
                issues.append(f"Record {i}: Invalid open price")
            
            if 'volume' in record and record['volume'] < 0:
                issues.append(f"Record {i}: Invalid volume")
        
        validation_results['issues'] = issues[:10]  # Limit to first 10 issues
        validation_results['passed'] = len(issues) == 0
        validation_results['quality_score'] = max(0, (1 - len(issues) / len(stock_records)) * 100)
        
        return validation_results
    
    @staticmethod
    def validate_news_data(news_records):
        """Validate news data quality"""
        validation_results = {
            'passed': True,
            'issues': [],
            'quality_score': 0.0,
            'record_count': len(news_records)
        }
        
        if not news_records:
            validation_results['passed'] = False
            validation_results['issues'].append("No news records found")
            return validation_results
        
        required_fields = ['id', 'title', 'content', 'source', 'publish_date']
        issues = []
        
        for i, record in enumerate(news_records):
            missing_fields = [field for field in required_fields if field not in record]
            if missing_fields:
                issues.append(f"Record {i}: Missing fields {missing_fields}")
            
            # Check content length
            if 'content' in record and len(record['content']) < 10:
                issues.append(f"Record {i}: Content too short")
        
        validation_results['issues'] = issues[:10]
        validation_results['passed'] = len(issues) == 0
        validation_results['quality_score'] = max(0, (1 - len(issues) / len(news_records)) * 100)
        
        return validation_results
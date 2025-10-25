"""
Enhanced Logging and Metadata System for Finance Portfolio Pipeline
"""

import logging
import json
import boto3
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import uuid
import traceback

@dataclass
class PipelineMetadata:
    """Structured metadata for pipeline operations"""
    pipeline_name: str
    layer: str  # bronze, silver, gold, rag
    operation: str  # extract, transform, load, process
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"  # running, success, failed, skipped
    source_count: int = 0
    target_count: int = 0
    error_count: int = 0
    file_paths: List[str] = None
    s3_paths: List[str] = None
    metrics: Dict[str, Any] = None
    error_details: Optional[str] = None
    dag_run_id: Optional[str] = None
    task_id: Optional[str] = None
    
    def __post_init__(self):
        if self.file_paths is None:
            self.file_paths = []
        if self.s3_paths is None:
            self.s3_paths = []
        if self.metrics is None:
            self.metrics = {}

class EnhancedLogger:
    """Enhanced logging system with S3 metadata tracking"""
    
    def __init__(self, name: str, log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level))
        
        # Console handler with detailed format
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # S3 client for metadata storage
        try:
            self.s3_client = boto3.client('s3')
            self.bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        except Exception as e:
            self.logger.warning(f"S3 client initialization failed: {e}")
            self.s3_client = None
    
    def start_pipeline_operation(self, 
                                pipeline_name: str,
                                layer: str,
                                operation: str,
                                dag_run_id: Optional[str] = None,
                                task_id: Optional[str] = None) -> PipelineMetadata:
        """Start tracking a pipeline operation"""
        metadata = PipelineMetadata(
            pipeline_name=pipeline_name,
            layer=layer,
            operation=operation,
            start_time=datetime.now(timezone.utc),
            dag_run_id=dag_run_id,
            task_id=task_id
        )
        
        self.logger.info(f"🚀 Starting {layer} {operation} operation for {pipeline_name}")
        self.logger.info(f"   Operation ID: {id(metadata)}")
        self.logger.info(f"   DAG Run: {dag_run_id}")
        self.logger.info(f"   Task: {task_id}")
        
        return metadata
    
    def log_progress(self, metadata: PipelineMetadata, message: str, **kwargs):
        """Log progress with structured data"""
        self.logger.info(f"📊 {metadata.pipeline_name} | {message}")
        
        # Update metrics
        for key, value in kwargs.items():
            metadata.metrics[key] = value
            self.logger.info(f"   {key}: {value}")
    
    def log_data_quality(self, metadata: PipelineMetadata, 
                        source_count: int,
                        target_count: int,
                        error_count: int = 0,
                        quality_metrics: Dict[str, Any] = None):
        """Log data quality metrics"""
        metadata.source_count = source_count
        metadata.target_count = target_count
        metadata.error_count = error_count
        
        self.logger.info(f"📈 Data Quality Report for {metadata.pipeline_name}")
        self.logger.info(f"   Source Records: {source_count:,}")
        self.logger.info(f"   Target Records: {target_count:,}")
        self.logger.info(f"   Error Records: {error_count:,}")
        
        if source_count > 0:
            success_rate = ((source_count - error_count) / source_count) * 100
            self.logger.info(f"   Success Rate: {success_rate:.2f}%")
        
        if quality_metrics:
            metadata.metrics.update(quality_metrics)
            for key, value in quality_metrics.items():
                self.logger.info(f"   {key}: {value}")
    
    def log_file_operations(self, metadata: PipelineMetadata,
                           file_paths: List[str] = None,
                           s3_paths: List[str] = None):
        """Log file operations"""
        if file_paths:
            metadata.file_paths.extend(file_paths)
            self.logger.info(f"📁 File Operations:")
            for path in file_paths[-5:]:  # Show last 5
                self.logger.info(f"   {path}")
            if len(file_paths) > 5:
                self.logger.info(f"   ... and {len(file_paths) - 5} more files")
        
        if s3_paths:
            metadata.s3_paths.extend(s3_paths)
            self.logger.info(f"☁️  S3 Operations:")
            for path in s3_paths[-5:]:  # Show last 5
                self.logger.info(f"   s3://{self.bucket_name}/{path}")
            if len(s3_paths) > 5:
                self.logger.info(f"   ... and {len(s3_paths) - 5} more S3 objects")
    
    def log_s3_operation(self, metadata: PipelineMetadata, 
                        operation: str, 
                        s3_key: str, 
                        file_type: str):
        """Log individual S3 operation"""
        metadata.s3_paths.append(s3_key)
        self.logger.info(f"☁️  S3 {operation.upper()}: {file_type} -> s3://{self.bucket_name}/{s3_key}")
    
    def finish_pipeline_operation(self, metadata: PipelineMetadata, 
                                 status: str = "success",
                                 error_details: str = None) -> Dict[str, Any]:
        """Finish tracking pipeline operation and save metadata"""
        metadata.end_time = datetime.now(timezone.utc)
        metadata.status = status
        metadata.error_details = error_details
        
        duration = (metadata.end_time - metadata.start_time).total_seconds()
        
        if status == "success":
            self.logger.info(f"✅ {metadata.pipeline_name} {metadata.operation} completed successfully")
        else:
            self.logger.error(f"❌ {metadata.pipeline_name} {metadata.operation} failed")
            if error_details:
                self.logger.error(f"   Error: {error_details}")
        
        self.logger.info(f"   Duration: {duration:.2f} seconds")
        self.logger.info(f"   Final Status: {status}")
        
        # Only return metadata dict - don't save to S3
        metadata_dict = self._get_pipeline_metadata_dict(metadata)
        
        return metadata_dict
    
    def _get_pipeline_metadata_dict(self, metadata: PipelineMetadata) -> Dict[str, Any]:
        """Convert pipeline metadata to dict format without saving to S3"""
        try:
            # Convert to dict and handle datetime serialization
            metadata_dict = asdict(metadata)
            metadata_dict['start_time'] = metadata.start_time.isoformat()
            if metadata.end_time:
                metadata_dict['end_time'] = metadata.end_time.isoformat()
                metadata_dict['duration_seconds'] = (metadata.end_time - metadata.start_time).total_seconds()
            
            self.logger.info(f"📊 Pipeline metadata prepared (not saved to S3)")
            
            return metadata_dict
            
        except Exception as e:
            self.logger.error(f"Failed to prepare metadata: {e}")
            return asdict(metadata)
            return asdict(metadata)
    
    def log_error_with_context(self, metadata: PipelineMetadata, 
                              error: Exception,
                              context: Dict[str, Any] = None):
        """Log error with full context"""
        error_details = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        self.logger.error(f"🚨 Error in {metadata.pipeline_name} {metadata.operation}")
        self.logger.error(f"   Error Type: {error_details['error_type']}")
        self.logger.error(f"   Error Message: {error_details['error_message']}")
        
        if context:
            self.logger.error("   Context:")
            for key, value in context.items():
                self.logger.error(f"     {key}: {value}")
        
        # Save error details
        metadata.error_details = json.dumps(error_details)
        metadata.error_count += 1
    
    def create_summary_report(self, pipeline_name: str, 
                            timeframe_hours: int = 24) -> Dict[str, Any]:
        """Create pipeline summary report"""
        if not self.s3_client:
            self.logger.warning("S3 client not available, cannot create summary report")
            return {}
        
        try:
            # Get metadata from last 24 hours
            cutoff_time = datetime.now(timezone.utc).timestamp() - (timeframe_hours * 3600)
            
            # List metadata objects
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"metadata/pipeline_operations/",
                MaxKeys=1000
            )
            
            operations = []
            for obj in response.get('Contents', []):
                if obj['LastModified'].timestamp() > cutoff_time:
                    try:
                        metadata_obj = self.s3_client.get_object(
                            Bucket=self.bucket_name,
                            Key=obj['Key']
                        )
                        metadata = json.loads(metadata_obj['Body'].read())
                        if metadata.get('pipeline_name') == pipeline_name:
                            operations.append(metadata)
                    except Exception:
                        continue
            
            # Generate summary
            summary = {
                'pipeline_name': pipeline_name,
                'timeframe_hours': timeframe_hours,
                'total_operations': len(operations),
                'successful_operations': len([op for op in operations if op.get('status') == 'success']),
                'failed_operations': len([op for op in operations if op.get('status') == 'failed']),
                'total_records_processed': sum(op.get('target_count', 0) for op in operations),
                'total_errors': sum(op.get('error_count', 0) for op in operations),
                'operations_by_layer': {},
                'latest_operation': None
            }
            
            # Group by layer
            for op in operations:
                layer = op.get('layer', 'unknown')
                if layer not in summary['operations_by_layer']:
                    summary['operations_by_layer'][layer] = {'count': 0, 'success': 0, 'failed': 0}
                summary['operations_by_layer'][layer]['count'] += 1
                if op.get('status') == 'success':
                    summary['operations_by_layer'][layer]['success'] += 1
                elif op.get('status') == 'failed':
                    summary['operations_by_layer'][layer]['failed'] += 1
            
            # Latest operation
            if operations:
                summary['latest_operation'] = max(operations, key=lambda x: x.get('start_time', ''))
            
            self.logger.info(f"📋 Pipeline Summary Report for {pipeline_name}")
            self.logger.info(f"   Timeframe: Last {timeframe_hours} hours")
            self.logger.info(f"   Total Operations: {summary['total_operations']}")
            self.logger.info(f"   Success Rate: {(summary['successful_operations']/max(summary['total_operations'], 1)*100):.1f}%")
            self.logger.info(f"   Records Processed: {summary['total_records_processed']:,}")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to create summary report: {e}")
            return {}

# Convenience functions for common use cases
def get_enhanced_logger(name: str, log_level: str = "INFO") -> EnhancedLogger:
    """Get an enhanced logger instance"""
    return EnhancedLogger(name, log_level)

def log_pipeline_start(logger: EnhancedLogger, 
                      pipeline_name: str, 
                      layer: str, 
                      operation: str,
                      dag_run_id: Optional[str] = None,
                      task_id: Optional[str] = None) -> PipelineMetadata:
    """Quick start for pipeline logging"""
    return logger.start_pipeline_operation(pipeline_name, layer, operation, dag_run_id, task_id)

def log_pipeline_success(logger: EnhancedLogger, metadata: PipelineMetadata, source_count: int, target_count: int):
    """Quick success logging"""
    logger.log_data_quality(metadata, source_count, target_count)
    return logger.finish_pipeline_operation(metadata, "success")

def log_pipeline_error(logger: EnhancedLogger, metadata: PipelineMetadata, error: Exception, context: Dict[str, Any] = None):
    """Quick error logging"""
    logger.log_error_with_context(metadata, error, context)
    return logger.finish_pipeline_operation(metadata, "failed", str(error))
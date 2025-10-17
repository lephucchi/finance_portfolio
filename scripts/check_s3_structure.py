#!/usr/bin/env python3
"""
S3 Structure Checker Script
Kiểm tra chi tiết cấu trúc S3 bucket cho Finance Portfolio Pipeline

Author: Banking Portfolio Team
Date: October 2025
"""

import os
import sys
import boto3
import json
from datetime import datetime
from collections import defaultdict
import pandas as pd

# Add project paths
sys.path.append('/opt/airflow')
sys.path.append('/opt/airflow/utils')

class S3StructureChecker:
    def __init__(self, bucket_name=None):
        """Initialize S3 client and bucket"""
        self.bucket_name = bucket_name or os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        try:
            # Initialize S3 client
            self.s3_client = boto3.client('s3')
            self.s3_resource = boto3.resource('s3')
            self.bucket = self.s3_resource.Bucket(self.bucket_name)
            
            print(f"✅ Connected to S3 bucket: {self.bucket_name}")
        except Exception as e:
            print(f"❌ Failed to connect to S3: {str(e)}")
            sys.exit(1)

    def check_bucket_access(self):
        """Check if bucket exists and is accessible"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"✅ Bucket '{self.bucket_name}' is accessible")
            return True
        except Exception as e:
            print(f"❌ Cannot access bucket '{self.bucket_name}': {str(e)}")
            return False

    def get_bucket_size_and_count(self):
        """Get total bucket size and object count"""
        try:
            total_size = 0
            total_count = 0
            
            for obj in self.bucket.objects.all():
                total_size += obj.size
                total_count += 1
            
            # Convert size to human readable format
            def human_readable_size(size_bytes):
                if size_bytes == 0:
                    return "0 B"
                
                size_names = ["B", "KB", "MB", "GB", "TB"]
                import math
                i = int(math.floor(math.log(size_bytes, 1024)))
                p = math.pow(1024, i)
                s = round(size_bytes / p, 2)
                return f"{s} {size_names[i]}"
            
            return {
                'total_objects': total_count,
                'total_size': human_readable_size(total_size),
                'total_size_bytes': total_size
            }
        except Exception as e:
            print(f"❌ Error getting bucket stats: {str(e)}")
            return None

    def analyze_directory_structure(self):
        """Analyze the complete directory structure"""
        print(f"\n🔍 Analyzing S3 bucket structure: {self.bucket_name}")
        
        directory_stats = defaultdict(lambda: {
            'count': 0, 
            'size': 0, 
            'latest_modified': None,
            'file_types': defaultdict(int),
            'sample_files': []
        })
        
        try:
            for obj in self.bucket.objects.all():
                # Get directory path (everything before the last '/')
                key_parts = obj.key.split('/')
                if len(key_parts) > 1:
                    directory = '/'.join(key_parts[:-1]) + '/'
                else:
                    directory = 'root/'
                
                # Get file extension
                filename = key_parts[-1]
                if '.' in filename:
                    file_ext = filename.split('.')[-1].lower()
                else:
                    file_ext = 'no_extension'
                
                # Update stats
                directory_stats[directory]['count'] += 1
                directory_stats[directory]['size'] += obj.size
                directory_stats[directory]['file_types'][file_ext] += 1
                
                # Track latest modification
                if (directory_stats[directory]['latest_modified'] is None or 
                    obj.last_modified > directory_stats[directory]['latest_modified']):
                    directory_stats[directory]['latest_modified'] = obj.last_modified
                
                # Sample files (up to 3)
                if len(directory_stats[directory]['sample_files']) < 3:
                    directory_stats[directory]['sample_files'].append({
                        'file': filename,
                        'size': obj.size,
                        'modified': obj.last_modified.strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            return directory_stats
            
        except Exception as e:
            print(f"❌ Error analyzing structure: {str(e)}")
            return None

    def print_structure_report(self, directory_stats):
        """Print detailed structure report"""
        if not directory_stats:
            print("❌ No directory stats available")
            return
        
        print(f"\n📊 S3 BUCKET STRUCTURE REPORT")
        print("=" * 80)
        
        # Sort directories by path
        sorted_dirs = sorted(directory_stats.items())
        
        for directory, stats in sorted_dirs:
            print(f"\n📁 {directory}")
            print(f"   📊 Files: {stats['count']}")
            print(f"   💾 Size: {self.human_readable_size(stats['size'])}")
            
            if stats['latest_modified']:
                print(f"   🕒 Latest: {stats['latest_modified'].strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            # File types
            if stats['file_types']:
                print(f"   📄 File types:")
                for ext, count in sorted(stats['file_types'].items()):
                    print(f"      .{ext}: {count} files")
            
            # Sample files
            if stats['sample_files']:
                print(f"   📋 Sample files:")
                for sample in stats['sample_files']:
                    size_str = self.human_readable_size(sample['size'])
                    print(f"      {sample['file']} ({size_str}) - {sample['modified']}")

    def check_pipeline_structure(self):
        """Check if expected pipeline structure exists"""
        expected_structure = {
            'bronze/': 'Raw data ingestion layer',
            'silver/': 'Cleaned and transformed data',
            'gold/': 'Business logic and aggregated data',
            'rag/': 'RAG system documents and embeddings',
            'logs/': 'Pipeline execution logs',
            'metadata/': 'Data schemas and metadata',
            'health-check/': 'System health monitoring'
        }
        
        print(f"\n🏗️ PIPELINE STRUCTURE VALIDATION")
        print("=" * 80)
        
        existing_prefixes = set()
        for obj in self.bucket.objects.all():
            if '/' in obj.key:
                prefix = obj.key.split('/')[0] + '/'
                existing_prefixes.add(prefix)
        
        for expected_prefix, description in expected_structure.items():
            if expected_prefix in existing_prefixes:
                print(f"✅ {expected_prefix:<15} - {description}")
            else:
                print(f"❌ {expected_prefix:<15} - {description} (MISSING)")

    def generate_detailed_report(self):
        """Generate comprehensive S3 report"""
        print(f"\n🚀 S3 STRUCTURE ANALYSIS STARTED")
        print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Check bucket access
        if not self.check_bucket_access():
            return False
        
        # Get bucket statistics
        bucket_stats = self.get_bucket_size_and_count()
        if bucket_stats:
            print(f"\n📈 BUCKET STATISTICS")
            print(f"   Total objects: {bucket_stats['total_objects']:,}")
            print(f"   Total size: {bucket_stats['total_size']}")
        
        # Analyze directory structure
        directory_stats = self.analyze_directory_structure()
        if directory_stats:
            self.print_structure_report(directory_stats)
        
        # Check pipeline structure
        self.check_pipeline_structure()
        
        print(f"\n✅ S3 ANALYSIS COMPLETED")
        print("=" * 80)
        
        return True

    def human_readable_size(self, size_bytes):
        """Convert bytes to human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"

    def export_structure_to_json(self, output_file=None):
        """Export structure analysis to JSON file"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"/tmp/s3_structure_report_{timestamp}.json"
        
        try:
            directory_stats = self.analyze_directory_structure()
            bucket_stats = self.get_bucket_size_and_count()
            
            report_data = {
                'bucket_name': self.bucket_name,
                'analysis_timestamp': datetime.now().isoformat(),
                'bucket_statistics': bucket_stats,
                'directory_structure': {}
            }
            
            # Convert directory stats to JSON serializable format
            for directory, stats in directory_stats.items():
                report_data['directory_structure'][directory] = {
                    'count': stats['count'],
                    'size_bytes': stats['size'],
                    'size_human': self.human_readable_size(stats['size']),
                    'latest_modified': stats['latest_modified'].isoformat() if stats['latest_modified'] else None,
                    'file_types': dict(stats['file_types']),
                    'sample_files': stats['sample_files']
                }
            
            with open(output_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            print(f"📄 Structure report exported to: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Error exporting report: {str(e)}")
            return None

def main():
    """Main execution function"""
    print("🔍 S3 STRUCTURE CHECKER")
    print("=" * 50)
    
    # Initialize checker
    checker = S3StructureChecker()
    
    # Generate detailed report
    success = checker.generate_detailed_report()
    
    if success:
        # Export to JSON
        json_file = checker.export_structure_to_json()
        if json_file:
            print(f"\n📋 Detailed report saved to: {json_file}")

if __name__ == "__main__":
    main()
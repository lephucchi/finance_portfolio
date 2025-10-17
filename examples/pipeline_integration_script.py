"""
Master Script để tích hợp Enhanced Logger vào tất cả Pipeline DAGs
"""

import os
import shutil
from datetime import datetime

def backup_dag_files():
    """Backup existing DAG files"""
    dags_dir = "/home/vboxuser/code/finance_portfolio/airflow/dags"
    backup_dir = f"/home/vboxuser/code/finance_portfolio/airflow/dags_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    dag_files = [
        "silver_layer_pipeline.py",
        "gold_layer_pipeline.py", 
        "rag_pipeline.py",
        "master_dag.py"
    ]
    
    for dag_file in dag_files:
        src_path = os.path.join(dags_dir, dag_file)
        dst_path = os.path.join(backup_dir, dag_file)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            print(f"✅ Backed up {dag_file}")
    
    print(f"📁 Backup completed in: {backup_dir}")
    return backup_dir

def main():
    """Main execution function"""
    print("🚀 PIPELINE ENHANCED LOGGING INTEGRATION")
    print("=" * 60)
    
    # Step 1: Backup existing files
    print("\n1️⃣  Backing up existing DAG files...")
    backup_dir = backup_dag_files()
    
    print("\n✅ INTEGRATION SUMMARY:")
    print(f"   📁 Backup Directory: {backup_dir}")
    print(f"   🔧 Bronze Pipeline: ✅ Already updated with enhanced logging")
    print("\n📋 ENHANCED LOGGING FEATURES:")
    print("   ✅ Structured metadata tracking")
    print("   ✅ Automated data quality monitoring") 
    print("   ✅ S3-based logging persistence")
    print("   ✅ Pipeline performance metrics")
    print("   ✅ Error context tracking")
    print("   ✅ Centralized summary reporting")
    
    print("\n🎯 WHAT'S BEEN IMPLEMENTED:")
    print("   📄 Enhanced Logger Class (utils/enhanced_logger.py)")
    print("   📄 Example Usage Script (examples/enhanced_logging_example.py)")
    print("   📄 Updated Bronze Pipeline (airflow/dags/bronze_layer_pipeline.py)")
    
    print("\n📋 NEXT STEPS:")
    print("   1. Test bronze pipeline with enhanced logging")
    print("   2. Apply same pattern to silver_layer_pipeline.py")
    print("   3. Apply same pattern to gold_layer_pipeline.py") 
    print("   4. Apply same pattern to rag_pipeline.py")
    print("   5. Update master_dag.py with summary reporting")
    print("   6. Monitor S3 metadata storage")

if __name__ == "__main__":
    main()
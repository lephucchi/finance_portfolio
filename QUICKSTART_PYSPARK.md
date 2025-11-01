# 🚀 Quick Start - PySpark Migration Testing

## Step-by-Step After Docker Build Completes

### 1. Start Containers
```powershell
docker-compose up -d
```

Wait 2-3 minutes for Airflow to initialize.

### 2. Verify Java-Spark Connectivity (CRITICAL)
```powershell
docker exec -it finance_portfolio-airflow-webserver-1 python /opt/airflow/test_java_spark.py
```

**Expected output:**
```
✅ PASS: Environment Variables
✅ PASS: Java Executable  
✅ PASS: JAVA_HOME Path
✅ PASS: PySpark Import
✅ PASS: Spark Session Creation (CRITICAL)
✅ PASS: Hadoop AWS JARs

Total: 6/6 tests passed
🎉 ALL TESTS PASSED - PySpark ready for production!
```

If **Test 5 (Spark Session Creation)** fails, Java gateway issue persists.

### 3. Manual Java Verification (If Test Fails)
```powershell
# Check Java version
docker exec -it finance_portfolio-airflow-webserver-1 java -version

# Check environment variables
docker exec -it finance_portfolio-airflow-webserver-1 bash -c 'echo $JAVA_HOME && echo $SPARK_HOME'

# Check Spark can find Java
docker exec -it finance_portfolio-airflow-webserver-1 bash -c 'cd $SPARK_HOME && bin/spark-submit --version'
```

### 4. Test Silver Layer DAG
```powershell
# Trigger Silver DAG
docker exec -it finance_portfolio-airflow-webserver-1 airflow dags trigger silver_layer_pipeline

# Watch logs (in new terminal)
docker logs -f finance_portfolio-airflow-webserver-1
```

**Look for:**
- `📈 Starting PySpark stock data processing`
- `✅ Spark session created successfully`
- `✅ Stock data processed successfully`

### 5. Test Gold Layer DAG  
```powershell
# Trigger Gold DAG
docker exec -it finance_portfolio-airflow-webserver-1 airflow dags trigger gold_layer_pipeline

# Check for Window function calculations
docker exec -it finance_portfolio-airflow-webserver-1 airflow tasks test gold_layer_pipeline create_market_features 2025-10-31
```

### 6. Check S3 Outputs
```python
# In Python (or Airflow UI > Admin > Variables)
import boto3
s3 = boto3.client('s3')

# Silver layer output (Parquet)
s3.list_objects_v2(
    Bucket='bankanalystportfolio',
    Prefix='silver/stocks/partition_date=2025-10-31/'
)

# Gold layer output (Parquet with features)
s3.list_objects_v2(
    Bucket='bankanalystportfolio', 
    Prefix='gold/analytics/partition_date=2025-10-31/'
)
```

---

## 🔧 Troubleshooting

### Issue: "Java gateway process exited"

**Root Causes:**
1. JAVA_HOME not set correctly
2. Java binary not in PATH
3. Spark can't find Java executable
4. Memory limits too low

**Solutions:**

#### A. Verify Java Installation
```powershell
docker exec -it finance_portfolio-airflow-webserver-1 bash -c '
  ls -la /usr/lib/jvm/java-17-openjdk-amd64/bin/java &&
  /usr/lib/jvm/java-17-openjdk-amd64/bin/java -version
'
```

#### B. Check Spark Logs
```powershell
docker exec -it finance_portfolio-airflow-webserver-1 bash -c 'ls -lrt /tmp/spark-* 2>/dev/null | tail -5'
```

#### C. Test Minimal Spark Session
```python
# Run inside container
docker exec -it finance_portfolio-airflow-webserver-1 python -c "
from pyspark.sql import SparkSession
spark = SparkSession.builder.master('local[1]').appName('test').getOrCreate()
print('Spark version:', spark.version)
spark.stop()
"
```

#### D. Increase Memory Limits (docker-compose.yml)
```yaml
environment:
  - SPARK_DRIVER_MEMORY=1g
  - SPARK_EXECUTOR_MEMORY=1g
deploy:
  resources:
    limits:
      memory: 4G
```

### Issue: "OutOfMemoryError: Java heap space"

**Solution:** Update `get_spark_session()` in DAGs:
```python
spark = SparkSession.builder \
    .config("spark.driver.memory", "2g") \
    .config("spark.executor.memory", "2g") \
    .config("spark.driver.maxResultSize", "1g") \
    .getOrCreate()
```

### Issue: S3 Access Denied

**Solution:** Check AWS credentials in docker-compose.yml:
```yaml
environment:
  - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
  - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
  - AWS_DEFAULT_REGION=ap-southeast-1
```

---

## 📊 Expected Performance

### Before (Pandas):
- Stock processing: ~5-10 min for 1M rows
- Memory usage: High (loads entire dataset)
- Scalability: Limited to single machine RAM

### After (PySpark):
- Stock processing: ~2-5 min for 1M rows (parallelized)
- Memory usage: Distributed across executors
- Scalability: Can scale to billions of rows with cluster

### Window Functions (Gold Layer):
- MA (Moving Averages): Distributed calculation across partitions
- RSI: Efficient gain/loss averaging without full data load
- Volatility: Rolling standard deviation with optimal window sizing

---

## ✅ Success Criteria

After all tests pass, you should have:

1. ✅ Java 17 running in container
2. ✅ Spark 3.5.0 accessible from Python
3. ✅ Hadoop AWS JARs for S3 connectivity
4. ✅ Silver Layer DAG processing Bronze → Silver Parquet
5. ✅ Gold Layer DAG creating technical indicators (MA, RSI, volatility)
6. ✅ S3 outputs in correct partition structure
7. ✅ No "Java gateway exited" errors

---

## 🎯 Next Steps

Once PySpark migration validated:

1. **Monitor production runs** - Check execution times, memory usage
2. **Optimize Spark configs** - Tune executor/driver memory for your data volume
3. **Migrate remaining Gold functions** - Convert 4 Pandas functions to PySpark if needed
4. **RAG pipeline** - Decide on Option 1 (separate container) or Option 2 (add PyTorch back)
5. **Scale testing** - Try with larger datasets (10M+ rows)

---

## 📞 Support

If Java gateway issue persists after all troubleshooting:
1. Share full error logs from `docker logs finance_portfolio-airflow-webserver-1`
2. Share `test_java_spark.py` output
3. Share `docker exec ... java -version` output
4. Check if OpenJDK 17 package is actually installed: `docker exec ... dpkg -l | grep openjdk`

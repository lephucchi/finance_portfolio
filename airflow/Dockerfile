# Custom Airflow image with Spark and vnstock dependencies
FROM apache/airflow:2.7.1-python3.10

# Install system dependencies
USER root

# Install Java for Spark
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    openjdk-11-jdk \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# Download and install Spark
ENV SPARK_VERSION=3.5.0
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-*.zip:$PYTHONPATH

RUN curl -L "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" \
    | tar -xz -C /opt/ \
    && mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} $SPARK_HOME \
    && chown -R airflow:root $SPARK_HOME

# Switch back to airflow user
USER airflow

# Copy .env file if it exists
COPY --chown=airflow:root .env* ./

# Install PySpark directly without constraints (critical for DAGs)
RUN pip install --no-cache-dir pyspark==3.5.0 py4j==0.10.9.7

# Use Airflow constraints file to avoid dependency hell
ENV AIRFLOW_VERSION=2.7.1
ENV PYTHON_VERSION=3.10
ENV CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# Install only pyarrow for Spark compatibility (RAG dependencies moved to backend)
RUN pip install --no-cache-dir pyarrow>=14.0.0

# Install vnstock3 for Vietnamese stock data
RUN pip install --no-cache-dir vnstock3>=3.2.0

# Set Spark configurations
ENV SPARK_CONF_DIR=$SPARK_HOME/conf
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Re-set PYTHONPATH to ensure PySpark is available (Airflow may override it)
ENV PYTHONPATH=/opt/spark/python:/opt/spark/python/lib/py4j-0.10.9.7-src.zip:${PYTHONPATH}
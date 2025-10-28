# Custom Airflow image with Spark and vnstock dependencies
FROM apache/airflow:2.7.1-python3.9

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

# Copy requirements if needed
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt || true

# Install RAG System dependencies explicitly
RUN pip install --no-cache-dir \
    sentence-transformers>=2.2.0 \
    faiss-cpu>=1.7.4 \
    torch>=2.0.0 \
    pyarrow>=14.0.0

# Set Spark configurations
ENV SPARK_CONF_DIR=$SPARK_HOME/conf
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3
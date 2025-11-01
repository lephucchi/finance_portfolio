# Use the official Apache Airflow image as base
FROM apache/airflow:2.9.2-python3.10

# Switch to root to install system dependencies
USER root

# Install system dependencies including Java for PySpark
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    openjdk-17-jdk-headless \
    procps \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Java environment variables for Spark
# Find the actual Java path dynamically
RUN update-alternatives --install /usr/bin/java java /usr/lib/jvm/java-17-openjdk-amd64/bin/java 1 && \
    update-alternatives --set java /usr/lib/jvm/java-17-openjdk-amd64/bin/java

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# Verify Java installation
RUN java -version && echo "✅ Java installed successfully"

# Download and install Spark
ENV SPARK_VERSION=3.5.0
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
RUN curl -L https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    | tar -xz -C /opt/ && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME} && \
    chown -R airflow:root ${SPARK_HOME}

ENV PATH=$PATH:${SPARK_HOME}/bin:${SPARK_HOME}/sbin
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Download Hadoop AWS JARs for S3 support (matching Spark 3.5.0 / Hadoop 3.3.4)
RUN mkdir -p ${SPARK_HOME}/jars && \
    curl -L https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar \
    -o ${SPARK_HOME}/jars/hadoop-aws-3.3.4.jar && \
    curl -L https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar \
    -o ${SPARK_HOME}/jars/aws-java-sdk-bundle-1.12.262.jar && \
    chown -R airflow:root ${SPARK_HOME}/jars && \
    ls -lh ${SPARK_HOME}/jars/hadoop* && \
    ls -lh ${SPARK_HOME}/jars/aws* && \
    echo "✅ Hadoop JARs downloaded successfully"

# Switch back to airflow user
USER airflow

# Copy requirements and install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --timeout=120 -r /requirements.txt

# Install PySpark with Hadoop AWS dependencies for S3 support
RUN pip install --no-cache-dir --timeout=120 \
    pyspark==3.5.0 \
    pyarrow>=14.0.0 \
    py4j>=0.10.9 \
    findspark>=2.0.0

# Install Vietnamese stock analysis packages (lightweight)
RUN pip install --no-cache-dir --timeout=120 \
    vnstock3==3.2.1 \
    ipython \
    boto3 \
    s3fs

# Validate PySpark can find Java
RUN python3 -c "import os; print('JAVA_HOME:', os.environ.get('JAVA_HOME')); print('SPARK_HOME:', os.environ.get('SPARK_HOME'))" && \
    python3 -c "import subprocess; subprocess.run(['java', '-version'], check=True)" && \
    echo "✅ Java accessible from Python"

# Copy the DAGs and plugins
COPY airflow/dags /opt/airflow/dags
COPY airflow/plugins /opt/airflow/plugins
COPY utils /opt/airflow/utils

# Set environment variables
ENV PYTHONPATH=/opt/airflow:/opt/airflow/dags:/opt/airflow/plugins:/opt/airflow/utils
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=False

# Spark configurations for Airflow
ENV SPARK_HOME=/opt/spark
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

USER airflow
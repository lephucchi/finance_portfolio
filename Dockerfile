# Use the official Apache Airflow image as base
FROM apache/airflow:2.9.2-python3.10

# Switch to root to install system dependencies
USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Copy requirements and install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Install Vietnamese stock analysis and RAG packages
RUN pip install --no-cache-dir \
    vnstock3==3.2.1 \
    ipython \
    boto3 \
    s3fs \
    findspark \
    sentence-transformers>=2.2.0 \
    faiss-cpu>=1.7.4 \
    torch>=2.0.0 \
    pyarrow>=14.0.0

# Copy the DAGs and plugins
COPY airflow/dags /opt/airflow/dags
COPY airflow/plugins /opt/airflow/plugins
COPY utils /opt/airflow/utils

# Set environment variables
ENV PYTHONPATH=/opt/airflow:/opt/airflow/dags:/opt/airflow/plugins:/opt/airflow/utils
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=False
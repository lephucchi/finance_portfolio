# Custom Airflow image with vnstock dependencies
FROM apache/airflow:2.7.1-python3.9

# Install system dependencies
USER root
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Copy requirements if needed
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt || true
# ============================================================
# ETL Dockerfile – SentinelX Trust AI
# Service: Data Engineering / Spark ETL Pipeline (Niraj Kadam)
# Base: Python 3.11 + OpenJDK 17 (required by Apache Spark)
# Author: Niraj Kadam – DevOps & Engineering Operations
# ============================================================

FROM python:3.11-slim

LABEL maintainer="radhika.patil@sentinelxlabs.com"
LABEL project="SentinelX Trust AI"
LABEL service="etl-pipeline"

# Install OpenJDK 17 (required for Apache Spark) and system tools
RUN apt-get update && apt-get install -y --no-install-recommends \
        openjdk-17-jre-headless \
        procps \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME for PySpark
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

WORKDIR /etl

# Install Python ETL dependencies
COPY deployment/docker/etl/requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy backend source (ETL uses shared config/settings and database models)
COPY backend/app/ ./app/

# Create data volume directories
RUN mkdir -p /data/raw /data/bronze /data/silver /output/dlq /output/reports/etl /logs

# Add app to Python path
ENV PYTHONPATH="/etl/app:${PYTHONPATH}"

# Create non-root user
RUN addgroup --system sentinelx && adduser --system --ingroup sentinelx sentinelx \
    && chown -R sentinelx:sentinelx /etl /data /output /logs
USER sentinelx

# Default: run the Spark ETL pipeline service
CMD ["python", "app/services/etl/spark_etl.py"]

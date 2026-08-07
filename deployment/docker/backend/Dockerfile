# ============================================================
# Backend Dockerfile – SentinelX Trust AI
# Service: FastAPI Backend (Niraj Kadam)
# Base: Python 3.11 Slim
# Author: Niraj Kadam – DevOps & Engineering Operations
# ============================================================

# Stage 1: Builder – install dependencies in isolated layer
FROM python:3.11-slim AS builder

WORKDIR /install

# Copy only requirements to leverage Docker layer caching
COPY deployment/docker/backend/requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install/packages -r requirements.txt


# ============================================================
# Stage 2: Runtime – lean production image
# ============================================================
FROM python:3.11-slim AS runtime

LABEL maintainer="radhika.patil@sentinelxlabs.com"
LABEL project="SentinelX Trust AI"
LABEL service="fastapi-backend"

# Install runtime system dependencies only (psycopg2 needs libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder stage
COPY --from=builder /install/packages /usr/local

# Copy backend source code to match project layout for relative pathing
COPY backend/app/ /app/backend/app/

WORKDIR /app/backend/app

# Create non-root user for security
RUN addgroup --system sentinelx && adduser --system --ingroup sentinelx sentinelx
USER sentinelx

# Expose FastAPI default port
EXPOSE 8000

# Health check – polls /api/v1/health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl --fail http://localhost:8000/api/v1/health || exit 1

# Entrypoint: start Uvicorn server
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

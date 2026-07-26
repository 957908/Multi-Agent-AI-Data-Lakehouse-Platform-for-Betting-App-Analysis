# ============================================================
# Scraper Dockerfile – SentinelX Trust AI
# Service: Data Acquisition Engine (Rayri Sharma)
# Base: Python 3.11 Slim + Playwright Chromium
# Author: Radhika Patil – DevOps & Engineering Operations
# ============================================================

FROM python:3.11-slim

LABEL maintainer="radhika.patil@sentinelxlabs.com"
LABEL project="SentinelX Trust AI"
LABEL service="data-acquisition-scraper"

# System dependencies required by Playwright Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
        # Core Chromium runtime dependencies
        libnss3 \
        libnspr4 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libdbus-1-3 \
        libexpat1 \
        libxcb1 \
        libxkbcommon0 \
        libx11-6 \
        libxcomposite1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libasound2 \
        libatspi2.0-0 \
        # Utility
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /scraper

# Install Python dependencies
COPY scraper/requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    # Install only Chromium browser for Playwright (smallest footprint)
    && playwright install chromium \
    && playwright install-deps chromium

# Copy scraper source
COPY scraper/ .

# Create output volume mount point
RUN mkdir -p /scraper/output /scraper/logs

# Create non-root user
RUN addgroup --system sentinelx && adduser --system --ingroup sentinelx sentinelx \
    && chown -R sentinelx:sentinelx /scraper
USER sentinelx

# Default: run main scraper orchestrator
# Can be overridden in docker-compose for scheduled mode
CMD ["python", "scraper/main.py"]

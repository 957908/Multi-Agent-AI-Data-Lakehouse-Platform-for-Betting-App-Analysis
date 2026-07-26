# 🚀 SentinelX Trust AI – Deployment & Local Development Guide

> **Author:** Radhika Patil – Senior DevOps & Engineering Operations  
> **Sprint:** DevOps Foundation (Sprint 1)  
> **Last Updated:** 2026-07-26

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Service Architecture](#service-architecture)
4. [Environment Configuration](#environment-configuration)
5. [Running Individual Services](#running-individual-services)
6. [Volume Management](#volume-management)
7. [Health Checks](#health-checks)
8. [Logging](#logging)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Ensure the following are installed before running the platform:

| Tool | Minimum Version | Purpose |
|---|---|---|
| Docker Desktop | 24.0+ | Container runtime |
| Docker Compose | V2 (`docker compose`) | Service orchestration |
| Git | 2.40+ | Version control |

> **Windows Users:** Enable WSL2 backend in Docker Desktop settings for optimal performance.

---

## Quick Start

### Step 1: Clone the Repository
```bash
git clone https://github.com/957908/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis.git
cd Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis
```

### Step 2: Configure Environment
```bash
# Copy the environment template
cp deployment/.env.example .env

# Edit and fill in all required values (see Environment Configuration section)
# CRITICAL: Set DB_PASSWORD and JWT_SECRET_KEY at minimum
```

### Step 3: Start Core Platform Stack
```bash
# From the project root – starts PostgreSQL + Backend + pgAdmin
docker compose -f deployment/docker-compose.yml up -d
```

### Step 4: Verify Services Are Healthy
```bash
docker compose -f deployment/docker-compose.yml ps
```

Expected output:
```
NAME                     STATUS          PORTS
sentinelx-postgres       running (healthy)   0.0.0.0:5432->5432/tcp
sentinelx-backend        running (healthy)   0.0.0.0:8000->8000/tcp
sentinelx-pgadmin        running             0.0.0.0:5050->80/tcp
```

### Step 5: Access Services
| Service | URL |
|---|---|
| **FastAPI Backend** | http://localhost:8000 |
| **Swagger API Docs** | http://localhost:8000/docs |
| **ReDoc API Docs** | http://localhost:8000/redoc |
| **pgAdmin UI** | http://localhost:5050 |

---

## Service Architecture

```text
┌─────────────────────────────────────────────┐
│             sentinelx-network               │
│                                             │
│  ┌──────────┐    ┌───────────┐              │
│  │ postgres │◄───│  backend  │              │
│  │ :5432    │    │ :8000     │              │
│  └──────────┘    └───────────┘              │
│       ▲               ▲                     │
│  ┌──────────┐    ┌───────────┐              │
│  │ pgadmin  │    │   etl     │ (on-demand)  │
│  │ :5050    │    │ (profile) │              │
│  └──────────┘    └───────────┘              │
│                       ▲                     │
│                  ┌───────────┐              │
│                  │  scraper  │ (on-demand)  │
│                  │ (profile) │              │
│                  └───────────┘              │
└─────────────────────────────────────────────┘
```

### Service Startup Order
```
postgres → (healthy) → backend + pgadmin
postgres → (healthy) → etl (when using --profile etl)
```

---

## Environment Configuration

All configuration is managed via the root `.env` file. Never commit `.env` to version control.

| Variable | Required | Default | Description |
|---|---|---|---|
| `DB_HOST` | ✅ | `postgres` | PostgreSQL hostname (use `postgres` in Docker) |
| `DB_PORT` | ✅ | `5432` | PostgreSQL port |
| `DB_USER` | ✅ | `postgres` | Database user |
| `DB_PASSWORD` | ✅ | — | **Must be set. No default.** |
| `DB_NAME` | ✅ | `sentinelx_trust_ai` | Database name |
| `JWT_SECRET_KEY` | ✅ | — | **Must be set. Generate with `secrets.token_hex(32)`** |
| `JWT_ALGORITHM` | ❌ | `HS256` | JWT signing algorithm |
| `HEADLESS` | ❌ | `true` | Set to `true` in Docker, `false` for local debug |
| `TARGET_SITE` | ❌ | `onexbet` | Scraper target site |
| `LOG_LEVEL` | ❌ | `INFO` | Log verbosity (`DEBUG`, `INFO`, `WARNING`) |

> See [.env.example](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/deployment/.env.example) for the complete list.

---

## Running Individual Services

### Start only Core Services (Backend + DB)
```bash
docker compose -f deployment/docker-compose.yml up -d postgres backend pgadmin
```

### Run the Scraper (on-demand)
```bash
# Uses the 'scraper' Docker Compose profile
docker compose -f deployment/docker-compose.yml --profile scraper run --rm scraper
```

### Run the ETL Pipeline (on-demand)
```bash
# Uses the 'etl' Docker Compose profile
docker compose -f deployment/docker-compose.yml --profile etl run --rm etl
```

### Rebuild a Specific Service After Code Changes
```bash
docker compose -f deployment/docker-compose.yml build backend --no-cache
docker compose -f deployment/docker-compose.yml up -d backend
```

### Stop All Services
```bash
docker compose -f deployment/docker-compose.yml down
```

### Stop and Remove All Volumes (⚠️ deletes data)
```bash
docker compose -f deployment/docker-compose.yml down -v
```

---

## Volume Management

Named Docker volumes ensure data persists across container restarts.

| Volume Name | Service | Contents |
|---|---|---|
| `sentinelx_postgres_data` | postgres | All database tables and records |
| `sentinelx_pgadmin_data` | pgadmin | pgAdmin server configurations |
| `sentinelx_app_logs` | backend | FastAPI application logs |
| `sentinelx_scraper_output` | scraper → etl | Raw scraped JSON files (shared) |
| `sentinelx_scraper_logs` | scraper | Scraper run logs |
| `sentinelx_etl_bronze` | etl | Bronze layer Parquet files |
| `sentinelx_etl_silver` | etl | Silver layer cleaned data |
| `sentinelx_etl_output` | etl | DLQ + ETL reports |
| `sentinelx_etl_logs` | etl | ETL pipeline logs |

### Inspect a Volume
```bash
docker volume inspect sentinelx_postgres_data
```

---

## Health Checks

Both PostgreSQL and the FastAPI backend implement Docker health checks.

```bash
# View health status
docker inspect sentinelx-postgres --format='{{.State.Health.Status}}'
docker inspect sentinelx-backend --format='{{.State.Health.Status}}'

# View recent health check log
docker inspect sentinelx-backend --format='{{range .State.Health.Log}}{{.Output}}{{end}}'
```

---

## Logging

All service logs are accessible via Docker and also written to named volumes.

```bash
# Stream backend logs
docker logs -f sentinelx-backend

# Stream PostgreSQL logs
docker logs -f sentinelx-postgres

# View last 100 lines of scraper output
docker logs --tail=100 sentinelx-scraper
```

---

## Troubleshooting

### Backend fails to connect to PostgreSQL
- Ensure `DB_HOST=postgres` in `.env` (not `localhost`)
- Wait for postgres to pass health check: `docker compose ps`
- Check postgres logs: `docker logs sentinelx-postgres`

### Scraper Chromium crash in container
- Ensure `HEADLESS=true` in `.env`
- Add `--shm-size=2gb` to scraper service if crashes persist (memory issue)

### Port already in use
```bash
# Find what's using port 8000
netstat -ano | findstr :8000   # Windows
lsof -i :8000                  # Linux/Mac
```

### Rebuild from scratch
```bash
docker compose -f deployment/docker-compose.yml down -v --rmi local
docker compose -f deployment/docker-compose.yml up -d --build
```

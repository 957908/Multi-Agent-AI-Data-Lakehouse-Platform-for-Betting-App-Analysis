# 🛠️ SentinelX Trust AI — Administrator & Operations Guide

This guide is intended for system administrators and DevOps engineers responsible for installing, configuring, maintaining, and troubleshooting the **SentinelX Trust AI** platform.

---

## 📋 Table of Contents
1. [Prerequisites & System Setup](#1-prerequisites--system-setup)
2. [Configuration Settings Reference](#2-configuration-settings-reference)
3. [Database & User Administration](#3-database--user-administration)
4. [Monitoring & Dashboards Management](#4-monitoring--dashboards-management)
5. [Upgrade & Rollback Procedures](#5-upgrade--rollback-procedures)
6. [Troubleshooting & Common Failure States](#6-troubleshooting--common-failure-states)

---

## 1. Prerequisites & System Setup

### Hardware Requirements
- **CPU:** 4 Cores minimum (8 Cores recommended for running ETL Spark clusters alongside scrapers).
- **RAM:** 8 GB minimum (16 GB recommended).
- **Disk:** 50 GB SSD minimum for raw/curated layers.

### Software Prerequisites
- **Docker Engine:** `v24.0+`
- **Docker Compose:** `v2.20+`

### Quick Start Inbound Port Rules
Configure local firewall (e.g. UFW or AWS Security Groups) to restrict external interface port exposures:

| Port | Protocol | Inbound Source | Description |
| :--- | :--- | :--- | :--- |
| `80` | TCP | Any | HTTP redirect to HTTPS |
| `443` | TCP | Any | Production SSL/TLS Endpoint |
| `3000` | TCP | Blocked / Localhost | Grafana panel (Proxied via HTTPS at `/grafana/`) |
| `9090` | TCP | Blocked / Localhost | Prometheus panel (Internal network only) |
| `5432` | TCP | Blocked / Localhost | PostgreSQL database (Internal network only) |

---

## 2. Configuration Settings Reference

The system configuration is loaded from environment variables defined in the `.env` file at the project root.

| Env Variable | Default | Purpose |
| :--- | :--- | :--- |
| `DB_HOST` | `postgres` | Hostname of the Postgres container |
| `DB_PORT` | `5432` | Postgres database listening port |
| `DB_USER` | `postgres` | Admin DB username |
| `DB_PASSWORD` | `<CHANGE_ME>` | Production database password |
| `JWT_SECRET_KEY` | — | Secret string for JWT token generation |
| `ENABLE_METRICS` | `true` | Exposes `/metrics` endpoint on the backend |
| `GF_ADMIN_PASSWORD` | `admin` | Grafana dashboard admin password |

---

## 3. Database & User Administration

### Initializing schemas
To run initial migration schemas and set up database tables, run:
```bash
docker-compose -f deployment/docker-compose.yml run --rm backend python main.py --init-db
```

### Backing Up the Database
To trigger a manual database snapshot:
```bash
docker exec sentinelx-postgres pg_dump -U postgres sentinelx_trust_ai > ./backups/manual_backup.sql
```

### Restoring the Database
To restore a database dump:
```bash
# Terminate existing connections first
docker exec sentinelx-postgres psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'sentinelx_trust_ai';"

# Run restore
docker exec -i sentinelx-postgres psql -U postgres -d sentinelx_trust_ai < ./backups/manual_backup.sql
```

---

## 4. Monitoring & Dashboards Management

The operational dashboards are fully provisioned inside Grafana on start.

- **URL Endpoint:** `https://<YOUR_DOMAIN>/grafana/`
- **Default Username:** `admin`
- **Default Password:** Defined via `GF_ADMIN_PASSWORD` in `.env`.

To update dashboard metrics panels, modify [sentinelx_metrics.json](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/deployment/monitoring/grafana/dashboards/sentinelx_metrics.json) and run:
```bash
docker-compose -f deployment/docker-compose.yml restart grafana
```

---

## 5. Upgrade & Rollback Procedures

### Upgrading the Platform
To deploy a new image release:
1. Fetch latest changes from the release tag branch:
   ```bash
   git fetch --tags
   git checkout v1.0.0-RC1
   ```
2. Rebuild and restart the containers gracefully:
   ```bash
   docker-compose -f deployment/docker-compose.yml up -d --build --remove-orphans
   ```

### Rolling Back
If a release fails validation checks, revert to the last stable tag:
```bash
git checkout v0.3.0-alpha
docker-compose -f deployment/docker-compose.yml up -d --build
```

---

## 6. Troubleshooting & Common Failure States

### Out of Memory (OOM) Container Crash
- **Symptom:** Backend or ETL container exits with code `137`.
- **Cause:** Host system memory exhausted.
- **Resolution:** In [PRODUCTION_GUIDE.md](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/deployment/PRODUCTION_GUIDE.md), adjust memory allocations or upgrade host RAM.

### DB Connection Timeouts
- **Symptom:** Backend log displays `Database connectivity is degraded`.
- **Cause:** PostgreSQL connection pool exhausted or postgres service is restarting.
- **Resolution:** Increase `pool_size` in `connection.py` or inspect PostgreSQL logs:
  ```bash
  docker logs sentinelx-postgres
  ```

### Scraper Proxy Block
- **Symptom:** Scraper logs show navigation timeout on authentication pages.
- **Cause:** Target betting platforms blocking the container IP.
- **Resolution:** Configure proxy settings in `.env` or set `HEADLESS=false` on local debug machines to bypass captcha filters.

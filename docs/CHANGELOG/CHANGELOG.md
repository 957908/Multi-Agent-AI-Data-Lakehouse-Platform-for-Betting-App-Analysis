# Changelog - SentinelX Trust AI

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0-alpha] - 2026-07-29

### Added
- Expose Prometheus metrics endpoint `/metrics` on FastAPI backend utilizing `prometheus-fastapi-instrumentator`.
- Integrated Prometheus monitoring service into `docker-compose.yml` to collect FastAPI, PostgreSQL, and host metrics.
- Integrated Grafana service into `docker-compose.yml` pre-configured with auto-provisioned Prometheus datasource and a comprehensive Operational Dashboard.
- Configured Node Exporter service for host container system telemetry.
- Configured Postgres Exporter service for PostgreSQL database performance metrics.
- Added GitHub Actions workflow `.github/workflows/ci.yml` verifying linting (`ruff`/`black`), docker-compose configuration, and dry-run docker builds for backend, scraper, and ETL services.
- Created `deployment/PRODUCTION_GUIDE.md` detailing security hardening, resource limits, network security, database isolation, log rotation, and data backups.
- Added `ENABLE_METRICS` environment variable to backend service and documented it in `.env.example`.

## [0.2.0-alpha] - 2026-07-26

### Added
- `deployment/` directory with complete Docker containerization stack.
- `deployment/docker/backend/Dockerfile` — multi-stage FastAPI backend image (Python 3.11 slim).
- `deployment/docker/scraper/Dockerfile` — Playwright Chromium scraper image with all browser runtime dependencies.
- `deployment/docker/etl/Dockerfile` — PySpark ETL image with OpenJDK 17 runtime.
- `deployment/docker/postgres/init.sql` — PostgreSQL schema bootstrap script for `etl_runs` and `payment_records` tables.
- `deployment/docker-compose.yml` — full service orchestration with health checks, named volumes, internal Docker network, and Docker Compose profiles (`scraper`, `etl`).
- `deployment/.env.example` — safe environment configuration template documenting all required variables.
- `deployment/README.md` — comprehensive local setup, deployment, troubleshooting, and volume management guide.
- Updated `.gitignore` to suppress Hadoop binaries, JVM crash logs, scraper runtime directories, and ETL Spark warehouse.

## [0.1.0-alpha] - 2026-07-26

### Added
- Standardized documentation directories and index structure.
- Root level `.gitignore` configured to ignore runtime environments (`.venv`), node modules, environment files (`.env`), and scraper local debug HTML/PNG logs.
- Configured git remote repository tracking pointing to `https://github.com/957908/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis`.
- Established branch workflow (`main`, `develop` setup).
- Initialized official **Risk Register**, **Architecture Decision Records (ADR)** tracker, and **Changelog** format.

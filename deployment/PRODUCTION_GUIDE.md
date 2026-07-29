# 🛡️ Production Deployment & Hardening Guide

This document defines the operational standards, security configurations, and deployment procedures for promoting the **SentinelX Trust AI** platform to a production environment.

---

## 📋 Table of Contents
1. [Environment & Secrets Management](#1-environment--secrets-management)
2. [Resource Limits & Orchestration](#2-resource-limits--orchestration)
3. [Network & Database Security](#3-network--database-security)
4. [Monitoring Stack Hardening](#4-monitoring-stack-hardening)
5. [Docker Log Rotation](#5-docker-log-rotation)
6. [Data Backup & Recovery](#6-data-backup--recovery)

---

## 1. Environment & Secrets Management

In production, **never** hardcode passwords or secrets in configuration files or `docker-compose.yml`. Use environment files (`.env`) kept outside of git repositories, or utilize a secret manager (such as AWS Secrets Manager, HashiCorp Vault, or Docker Secrets).

### Required Production Settings Matrix

| Service | Environment Variable | Recommended Value / Action | Purpose |
| :--- | :--- | :--- | :--- |
| **Postgres** | `DB_PASSWORD` | Strong alphanumeric value (min 24 chars) | Protects DB storage |
| **Backend** | `JWT_SECRET_KEY` | Hex string `python -c "import secrets; print(secrets.token_hex(32))"` | Signs session tokens |
| **Backend** | `ENABLE_METRICS` | `true` | Enables Prometheus exposition |
| **Backend** | `ADMIN_PASSWORD` | Change default! Strong password | Root admin password |
| **Backend** | `ANALYST_PASSWORD` | Change default! Strong password | Analyst password |
| **Backend** | `READER_PASSWORD` | Change default! Strong password | Reader password |
| **Grafana** | `GF_ADMIN_PASSWORD` | Strong admin user password | Visualisation panel admin |

---

## 2. Resource Limits & Orchestration

To prevent a single service from exhausting host memory or CPU resources, apply explicit resource limits in your production compose overrides.

Add the following `deploy` config blocks under each service in `docker-compose.prod.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M

  postgres:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 1G
```

---

## 3. Network & Database Security

### Port Exposure Control
By default, the database port (`5432`) is exposed to the host system. In production, remove public port mapping:

```yaml
# In docker-compose.yml (Dev):
ports:
  - "5432:5432"

# In production configuration:
# Remove the ports directive completely so only container network can resolve postgres!
```

All backend and ETL services resolve PostgreSQL via the internal network bridge `sentinelx-network`, which prevents database exposure to the outside world.

### Firewall Hardening
Allow inbound traffic only on ports `8000` (FastAPI backend reverse proxy, e.g., Nginx) and `3000` (Grafana dashboard). Block public access to:
- Port `9090` (Prometheus)
- Port `9100` (Node Exporter)
- Port `9187` (Postgres Exporter)

---

## 4. Monitoring Stack Hardening

### Grafana Access Controls
- Ensure `GF_USERS_ALLOW_SIGN_UP=false` is set in the environment to prevent random user registration.
- Rotate the default admin credentials immediately.
- Use Role-Based Access Control (RBAC) in Grafana to restrict editing dashboards to admins, while giving analysts read-only views.

### Prometheus & Exporter Isolation
Prometheus and the exporters do not have built-in authentication in their basic forms.
- **Node Exporter:** Do not publish `9100` port to the public interface. Remove the port publishing option `ports: - "9100:9100"` from `docker-compose.yml` if external scraping is not required.
- **Prometheus:** Always keep port `9090` blocked via local host firewall (IPtables/UFW) or use Basic Auth via reverse proxy.

---

## 5. Docker Log Rotation

To prevent container logs from consuming all available host disk space, configure Docker's global logging options in `docker-compose.yml` or `/etc/docker/daemon.json`:

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "5"
```
This ensures a maximum of `250MB` of logs are kept for each container.

---

## 6. Data Backup & Recovery

Configure a daily cron job to back up the database without downtime using `pg_dump`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/sentinelx"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/sentinelx_db_${TIMESTAMP}.sql"

# Execute pg_dump inside the container
docker exec sentinelx-postgres pg_dump -U postgres sentinelx_trust_ai > "${BACKUP_FILE}"

# Compress the backup file
gzip "${BACKUP_FILE}"

# Keep only the last 30 days of backups
find "${BACKUP_DIR}" -name "sentinelx_db_*.sql.gz" -mtime +30 -exec rm {} \;
```
Ensure backups are synced to an offsite secure storage bucket (e.g. AWS S3, Google Cloud Storage) with encryption enabled.

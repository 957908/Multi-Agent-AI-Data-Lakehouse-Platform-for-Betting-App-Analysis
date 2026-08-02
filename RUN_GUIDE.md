# 🏃 SentinelX Trust AI — Comprehensive Execution & Run Guide

This guide provides step-by-step instructions to configure, launch, seed, and operate the entire **SentinelX Trust AI** application stack locally.

---

## 📋 Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Step 1: Environmental Configuration](#step-1-environmental-configuration)
3. [Step 2: Starting the Docker Infrastructure](#step-2-starting-the-docker-infrastructure)
4. [Step 3: Initializing & Seeding the Database](#step-3-initializing--seeding-the-database)
5. [Step 4: Launching the Frontend Dashboard](#step-4-launching-the-frontend-dashboard)
6. [Step 5: Verifying Operational Endpoints](#step-5-verifying-operational-endpoints)
7. [Step 6: Running Scrapers & ETL On-Demand](#step-6-running-scrapers--etl-on-demand)

---

## 1. Prerequisites
Ensure the following software packages are installed and running on your host system:
- **Docker Desktop** (Engine `v24.0+`, Compose `v2.20+`)
- **Python 3.11+** (Ensure a virtual environment `venv` is active)
- **Node.js 20+** (with `npm` package manager)

---

## Step 1: Environmental Configuration

The project uses environment files to parameterize port bindings, database credentials, and URL configs.

1. Create a `.env` configuration file in the project root directory. (Use the database settings defined below to prevent host conflicts):
   ```ini
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5434                          # Bind to 5434 to avoid conflicts with native Postgres (5432)
   DB_USER=postgres
   DB_PASSWORD=your_secure_password
   DB_NAME=sentinelx_trust_ai

   # JWT Security
   JWT_SECRET_KEY=sentinelx_super_secure_jwt_secret_key_123
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Seeded User Accounts
   ADMIN_EMAIL=admin@sentinelx.com
   ADMIN_PASSWORD=AdminPassword123
   ANALYST_EMAIL=analyst@sentinelx.com
   ANALYST_PASSWORD=AnalystPassword123
   ```
2. Copy this root `.env` configuration directly into the `/deployment` folder. This is required because Docker Compose resolves configuration variables relative to the folder containing `docker-compose.yml`:
   ```bash
   # Windows PowerShell
   Copy-Item .env deployment/.env -Force

   # Linux / macOS
   cp .env deployment/.env
   ```

---

## Step 2: Starting the Docker Infrastructure

The platform uses a secure bridge network (`sentinelx-network`) to host database, API backend, telemetry scrapers, and Nginx SSL gateway services.

1. Start all container daemons using Docker Compose:
   ```bash
   docker-compose -f deployment/docker-compose.yml up -d --build
   ```
2. Confirm all services are online and healthy:
   ```bash
   docker ps
   ```
   *Expected containers running: `sentinelx-nginx` (healthy, port 80/443), `sentinelx-backend` (healthy, port 8000), `sentinelx-postgres` (healthy, port 5434), `sentinelx-prometheus` (port 9090), `sentinelx-grafana`, `sentinelx-pgadmin` (port 5050), and exporters.*

---

## Step 3: Initializing & Seeding the Database

Before accessing payment metrics, you must initialize the PostgreSQL database schema and seed it with transactions.

1. **Initialize DB Tables Schema:**
   Execute the database creation metadata inside the active backend container:
   ```bash
   docker-compose -f deployment/docker-compose.yml exec backend python main.py --init-db
   ```
2. **Seed Sample Data:**
   Run the seeding script locally to populate the active PostgreSQL container with high-fidelity platform analytics, metrics, and UPI/Crypto transaction histories:
   ```bash
   # Windows
   .\.venv\Scripts\python backend/app/database/seed_db.py

   # Linux / macOS
   source .venv/bin/activate
   python backend/app/database/seed_db.py
   ```

---

## Step 4: Launching the Frontend Dashboard

The user interface dashboard is a Next.js web application that connects to the backend APIs and Nginx gateways.

1. Navigate to the `/frontend` directory:
   ```bash
   cd frontend
   ```
2. Install npm packages and build the production bundles:
   ```bash
   npm install
   npm run build
   ```
3. Start the Next.js production server:
   ```bash
   npm run start
   ```
   *The console is now accessible at **[http://localhost:3000](http://localhost:3000)**.*

---

## Step 5: Verifying Operational Endpoints

Once the stack is running, you can test connectivity across all interfaces:

| Interface URL | Type | Description |
| :--- | :---: | :--- |
| **[http://localhost:3000](http://localhost:3000)** | Web Browser | Next.js Dashboard Console |
| **[https://localhost/api/v1/health](https://localhost/api/v1/health)** | Web API (SSL) | Direct health check from Nginx (returns `database: healthy`) |
| **[https://localhost/api/v1/gold/platforms](https://localhost/api/v1/gold/platforms)** | Web API (SSL) | Queries the Gold analytics table populated in Step 3 |
| **[https://localhost/docs](https://localhost/docs)** | Web Browser | Interactive Swagger API endpoints dashboard |
| **[https://localhost/grafana/](https://localhost/grafana/)** | Web Browser | Grafana Observability Dashboards |
| **[http://127.0.0.1:5050](http://127.0.0.1:5050)** | Web Browser | pgAdmin 4 SQL Database Management Panel |

*Note: Accessing HTTPS routes locally will show a security warning. Click **Advanced** -> **Proceed to localhost** to bypass.*

---

## Step 6: Running Scrapers & ETL On-Demand

For testing transactional ingestion, you can trigger individual scrapers or ETL runs manually.

1. **Trigger Headless Web Scraper:**
   ```bash
   # Run Playwright scraper for 1xBet
   .\.venv\Scripts\python scraper/scraper/main.py --site onexbet
   ```
   *Scraped raw data will be exported as JSON under `/scraper/scraper/output/`.*

2. **Trigger Data Ingestion ETL Pipeline:**
   Inside the `etl` Spark container, run the Medallion pipeline to process raw snapshots into Silver/Gold database records:
   ```bash
   docker-compose -f deployment/docker-compose.yml run --rm etl
   ```

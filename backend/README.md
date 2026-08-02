# ⚡ SentinelX Trust AI — Backend API Service Module

This module provides the asynchronous REST API, security layer, database repositories, AI Trust Engine, and RAG services for the **SentinelX Trust AI** platform.

---

## 📂 Directory Layout
```text
backend/
├── app/
│   ├── api/v1/                   # REST endpoint routers (auth, etl, health, gold, search, etc.)
│   ├── config/                   # settings.py configuration management (merged Priya + Arjun)
│   ├── core/                     # security.py, exceptions.py
│   ├── database/                 # connection.py, models.py, init_db.py
│   ├── repositories/             # etl_repository.py, payment_repository.py
│   ├── schemas/                  # Pydantic validation schemas
│   ├── services/                 # AI Trust engine, RAG search, validation layers, Spark ETL
│   ├── main.py                   # CLI orchestrator (db init, ETL runs)
│   └── server.py                 # FastAPI Uvicorn application entrypoint
└── tests/                        # unit, api, integration, and E2E simulation tests
```

---

## ⚙️ Local Development & Setup

### Prerequisites
- Python 3.11+
- Virtual Environment (`venv` active)
- PostgreSQL 16 active database instance

### 1. Installation
Install core python dependencies from the deployment requirements:
```bash
pip install -r ../deployment/docker/backend/requirements.txt
```

### 2. Environment Variables Configuration
Configure environment parameters in your root `.env` file (see [deployment/.env.example](../deployment/.env.example) for templates):
```ini
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=sentinelx_trust_ai
JWT_SECRET_KEY=generate_with_python_secrets_token_hex_32
ENABLE_METRICS=true
```

### 3. Database Initialization
Run the CLI orchestrator to construct the tables schema:
```bash
python app/main.py --init-db
```

### 4. Running the Server
Launch the FastAPI uvicorn daemon:
```bash
python app/server.py
```
- **REST API URL:** `http://localhost:8000`
- **Swagger Documentation:** `http://localhost:8000/docs`
- **Prometheus Telemetry Endpoint:** `http://localhost:8000/metrics`

---

## 🧪 Running Tests
To execute backend API and AI service verification checks:
```bash
python -m unittest discover -s tests
```
All unit tests should complete successfully with zero errors.

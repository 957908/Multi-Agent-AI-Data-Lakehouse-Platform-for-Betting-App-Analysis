"""
File: server.py
Purpose:
    Main entry point for starting the SentinelX Trust AI backend REST API server.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 5.0
"""

import sys
import time
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
import uvicorn

# Ensure backend/app/ is at the front of python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from api.v1.router import api_router
from prometheus_fastapi_instrumentator import Instrumentator
from core.exceptions import (
    BaseAppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)

logger = logging.getLogger("backend.server")

tags_metadata = [
    {
        "name": "Health",
        "description": "System availability, uptime telemetry, and database connectivity checks."
    },
    {
        "name": "Authentication",
        "description": "JWT authentication token issuance, credentials verification, and active session profiles."
    },
    {
        "name": "Payment Records",
        "description": "Curated Silver layer payment records with read-only search and filtering."
    },
    {
        "name": "ETL Management",
        "description": "Execution run logs, ingestion metrics, and quality reports for data pipelines."
    },
    {
        "name": "Platform Statistics",
        "description": "Aggregated summary metrics, payment channel distributions, and regional coverage."
    },
    {
        "name": "Search",
        "description": "Advanced multi-criteria search supporting free text, platform, country, and trust filters."
    },
    {
        "name": "Gold Layer Analytics",
        "description": "Pre-computed Gold layer platform trust analytics and payment method insights."
    },
    {
        "name": "AI Intelligence",
        "description": "Rule-Based Trust Score engine, AI risk analysis reports, and provider-agnostic RAG search."
    }
]

app = FastAPI(
    title="SentinelX Trust AI – Unified Backend & AI Platform",
    description=(
        "# 🛡️ SentinelX Trust AI Platform API\n\n"
        "Enterprise-grade backend API connecting Data Acquisition (Rayri Sharma), Data Engineering ETL (Priya Iyer), "
        "and AI Intelligence (Arjun Mehta) into a unified intelligence platform for betting app analysis.\n\n"
        "### Key Features:\n"
        "- **Gold Layer Integration:** Pre-computed platform analytics and payment reliability metrics.\n"
        "- **Rule-Based Trust Engine:** Explainable trust score calculation (0-100) and risk flag breakdowns.\n"
        "- **Provider-Agnostic RAG:** RAG-assisted context search for platform payment compliance.\n"
        "- **Role-Based Access Control:** Secure JWT authentication supporting Admin, Analyst, and Reader roles.\n"
        "- **Unified Envelope:** Every endpoint returns standard `APIResponse` JSON structures."
    ),
    version="5.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests_and_latency(request: Request, call_next):
    """
    Middleware logging incoming request method, path, response status, and latency.
    """
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    logger.info(
        f"Request: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.4f}s"
    )
    return response


# Register global exception handlers
app.add_exception_handler(BaseAppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API v1 router
app.include_router(api_router, prefix="/api/v1")

# Instrument FastAPI app for Prometheus metrics scraping
Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    env_var_name="ENABLE_METRICS",
    excluded_handlers=[
        "/metrics",
        "/api/v1/health",
        "/docs",
        "/redoc",
        "/api/v1/openapi.json"
    ]
).instrument(app).expose(app, endpoint="/metrics")


if __name__ == "__main__":
    logger.info("Launching SentinelX Trust AI Server on http://127.0.0.1:8000")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)

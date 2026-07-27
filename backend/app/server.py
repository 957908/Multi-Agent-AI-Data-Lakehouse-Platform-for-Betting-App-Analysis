"""
File: server.py
Purpose:
    Main entry point for starting the SentinelX Trust AI backend REST API server.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

import sys
import time
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Ensure backend/app/ is in the python path
sys.path.append(str(Path(__file__).resolve().parent))

from api.v1.router import api_router
from core.exceptions import BaseAppException, app_exception_handler, general_exception_handler

logger = logging.getLogger("backend.server")

app = FastAPI(
    title="SentinelX Trust AI Backend API",
    description="Enterprise API layer for betting ecosystem analysis, risk metrics, and trust score intelligence.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests_and_latency(request: Request, call_next):
    """
    Middleware registering incoming request endpoints, method, status codes, and execution times.
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


# Register global exceptions
app.add_exception_handler(BaseAppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include APIs
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    logger.info("Launching FastAPI server on http://127.0.0.1:8000")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)

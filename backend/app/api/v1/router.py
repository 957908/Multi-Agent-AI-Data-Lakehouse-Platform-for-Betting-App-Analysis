"""
File: router.py
Purpose:
    Aggregates sub-routers into a unified v1 router hierarchy.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 5.0
"""

from fastapi import APIRouter
from api.v1.endpoints.health import router as health_router
from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.payment_records import router as payment_router
from api.v1.endpoints.etl import router as etl_router
from api.v1.endpoints.statistics import router as stats_router
from api.v1.endpoints.search import router as search_router
from api.v1.endpoints.ai import router as ai_router
from api.v1.endpoints.gold import router as gold_router

api_router = APIRouter()

# Register endpoint groups
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(payment_router)
api_router.include_router(etl_router)
api_router.include_router(stats_router)
api_router.include_router(search_router)
api_router.include_router(ai_router)
api_router.include_router(gold_router)

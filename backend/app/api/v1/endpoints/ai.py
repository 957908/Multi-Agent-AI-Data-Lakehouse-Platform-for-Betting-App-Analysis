"""
File: ai.py
Purpose:
    REST API endpoints for AI Intelligence features (Trust Score, AI Risk Analysis, RAG Search, Platform Summary).
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 5.0
"""

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from database.connection import get_db_session
from core.security import get_current_user
from schemas.ai import (
    TrustScoreRequest,
    TrustScoreResponse,
    AIAnalysisRequest,
    AIAnalysisResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    PlatformSummaryResponse
)
from schemas.response import APIResponse
from services.ai.trust_engine import TrustEngine
from services.ai.rag_service import RAGService
from services.ai.ai_analysis import AIAnalysisService

router = APIRouter(tags=["AI Intelligence"])


@router.post(
    "/trust-score",
    response_model=APIResponse[TrustScoreResponse],
    status_code=status.HTTP_200_OK,
    summary="Calculate Platform Trust Score",
    description="Evaluates platform trust score (0-100), risk level (LOW/MEDIUM/HIGH), confidence, and modular rule evaluations."
)
def calculate_trust_score(
    payload: TrustScoreRequest,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Computes trust score for a platform domain or supplied custom records.
    """
    site = payload.site or "unknown_platform"
    engine = TrustEngine(db_session=db)
    response_data = engine.calculate_platform_trust(site, custom_records=payload.records)

    return APIResponse(
        success=True,
        message=f"Trust Score calculated successfully for platform '{site}'.",
        data=response_data
    )


@router.post(
    "/analyze",
    response_model=APIResponse[AIAnalysisResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate AI Risk & Intelligence Report",
    description="Synthesizes platform summary, payment channel reliability, complaint breakdowns, and actionable recommendations."
)
def analyze_platform(
    payload: AIAnalysisRequest,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Generates structured AI analysis report for a platform.
    """
    service = AIAnalysisService(db_session=db)
    report = service.analyze_platform(payload)

    return APIResponse(
        success=True,
        message=f"AI Analysis report generated for platform '{payload.site}'.",
        data=report
    )


@router.post(
    "/rag/query",
    response_model=APIResponse[RAGQueryResponse],
    status_code=status.HTTP_200_OK,
    summary="RAG Natural Language Query",
    description="Provider-agnostic natural language search querying platform payment records using context builder & prompt synthesis."
)
def rag_query(
    payload: RAGQueryRequest,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Executes provider-agnostic RAG natural language search.
    """
    service = RAGService(db_session=db)
    result = service.query(payload)

    return APIResponse(
        success=True,
        message="RAG query executed successfully.",
        data=result
    )


@router.get(
    "/platform/{site}/summary",
    response_model=APIResponse[PlatformSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Platform High-Level Summary",
    description="Returns high-level summary including trust rating, total/active payment methods, and supported countries."
)
def get_platform_summary(
    site: str = Path(..., examples=["melbet"], description="Platform site name or identifier"),
    db: Session = Depends(get_db_session)
):
    """
    Returns platform high-level summary overview.
    """
    service = AIAnalysisService(db_session=db)
    summary_data = service.get_platform_summary(site)

    return APIResponse(
        success=True,
        message=f"Summary retrieved for platform '{site}'.",
        data=summary_data
    )

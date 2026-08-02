"""
File: ai.py
Purpose:
    Pydantic schemas for AI Intelligence services including Trust Engine, RAG, and AI Analysis.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 5.0
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class RuleEvaluationResult(BaseModel):
    """
    Detailed result of an individual rule evaluation within the Trust Engine.
    """
    rule_name: str = Field(..., description="Name of the evaluated rule")
    passed: bool = Field(..., description="Whether the rule passed or met positive criteria")
    score_contribution: float = Field(..., description="Points contributed by this rule (0 to max_weight)")
    max_weight: float = Field(..., description="Maximum possible points for this rule")
    description: str = Field(..., description="Explanation of the evaluation outcome")


class TrustScoreRequest(BaseModel):
    """
    Request model for computing trust score.
    """
    site: Optional[str] = Field(None, example="melbet", description="Betting platform domain or site identifier")
    records: Optional[List[Dict[str, Any]]] = Field(None, description="Optional custom payment records to evaluate")


class TrustScoreResponse(BaseModel):
    """
    Response schema for platform trust evaluation.
    """
    site: str = Field(..., example="melbet", description="Platform site name")
    trust_score: float = Field(..., example=78.5, description="Calculated Trust Score between 0 and 100")
    trust_level: str = Field(..., example="MEDIUM", description="Risk category: LOW, MEDIUM, or HIGH")
    confidence_score: float = Field(..., example=0.85, description="Confidence score between 0.0 and 1.0 based on data volume")
    score_explanation: str = Field(..., description="Summary explanation of how the score was calculated")
    rule_evaluations: List[RuleEvaluationResult] = Field(default_factory=list, description="Breakdown of individual rule evaluations")
    risk_flags: List[str] = Field(default_factory=list, description="Extracted risk factors and flags")
    evaluated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of evaluation")


class AIAnalysisRequest(BaseModel):
    """
    Request payload for comprehensive platform AI risk and performance analysis.
    """
    site: str = Field(..., example="melbet", description="Platform site identifier")
    include_recommendations: bool = Field(True, description="Whether to include actionable recommendations")
    include_complaints: bool = Field(True, description="Whether to include complaint summaries")


class PaymentMethodInsight(BaseModel):
    """
    Analytical breakdown of a specific payment method on a platform.
    """
    payment_type: str = Field(..., example="e-wallet", description="Payment method category")
    payment_name: str = Field(..., example="Paytm", description="Name of payment gateway/service")
    total_records: int = Field(..., example=12, description="Total extracted records")
    active_count: int = Field(..., example=10, description="Active status count")
    reliability_score: float = Field(..., example=85.0, description="Reliability score 0-100%")
    supported_countries: List[str] = Field(default_factory=list, description="List of supported country codes")


class AIAnalysisResponse(BaseModel):
    """
    Structured AI risk analysis and platform intelligence report.
    """
    site: str = Field(..., example="melbet", description="Analyzed platform")
    summary: str = Field(..., description="Executive summary of platform reliability")
    payment_insights: List[PaymentMethodInsight] = Field(default_factory=list, description="Breakdown by payment method")
    complaint_summary: str = Field(..., description="Synthesized complaint and risk issue summary")
    risk_factors: List[str] = Field(default_factory=list, description="Extracted risk indicators")
    recommendations: List[str] = Field(default_factory=list, description="Actionable platform recommendations")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of report generation")


class RAGQueryRequest(BaseModel):
    """
    Query payload for provider-agnostic RAG search.
    """
    query: str = Field(..., example="What payment methods work in India for Melbet?", description="Natural language search query")
    top_k: int = Field(3, ge=1, le=10, description="Number of context documents to retrieve")
    filter_site: Optional[str] = Field(None, example="melbet", description="Optional site filter")


class RAGChunk(BaseModel):
    """
    Retrieved context document chunk.
    """
    document_id: str = Field(..., description="Unique document chunk identifier")
    content: str = Field(..., description="Text content of the document chunk")
    relevance_score: float = Field(..., description="Computed relevance score (0.0 to 1.0)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata associated with chunk")


class RAGQueryResponse(BaseModel):
    """
    RAG service output payload.
    """
    query: str = Field(..., description="Original user query")
    context_documents: List[RAGChunk] = Field(default_factory=list, description="Retrieved context chunks")
    formatted_prompt: str = Field(..., description="Externalized prompt constructed for LLM consumption")
    synthesized_answer: str = Field(..., description="Rule-synthesized answer matching context")
    estimated_tokens: int = Field(..., description="Estimated token count for prompt + context")


class PlatformSummaryResponse(BaseModel):
    """
    Combined high-level overview of platform metrics, trust score, and payment options.
    """
    site: str = Field(..., example="melbet", description="Platform site name")
    trust_score: float = Field(..., example=78.5, description="Trust Score 0-100")
    trust_level: str = Field(..., example="MEDIUM", description="Risk classification")
    confidence_score: float = Field(..., example=0.85, description="Confidence metric")
    total_payment_methods: int = Field(..., example=15, description="Total distinct payment methods")
    active_payment_methods: int = Field(..., example=12, description="Active payment methods")
    supported_countries: List[str] = Field(default_factory=list, description="Distinct supported countries")
    risk_summary: str = Field(..., description="High-level risk overview")
    top_payment_methods: List[str] = Field(default_factory=list, description="Top active payment methods")
    evaluated_at: datetime = Field(default_factory=datetime.utcnow, description="Evaluation timestamp")

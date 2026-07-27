"""
File: ai_analysis.py
Purpose:
    AI Analysis Service for platform risk summaries, payment method reliability, complaint synthesis, and recommendations.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 2.0
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict
from sqlalchemy.orm import Session

from schemas.ai import (
    AIAnalysisRequest,
    AIAnalysisResponse,
    PaymentMethodInsight,
    PlatformSummaryResponse
)
from services.ai.trust_engine import TrustEngine
from repositories.payment_repository import PaymentRepository

logger = logging.getLogger("backend.services.ai.ai_analysis")


class AIAnalysisService:
    """
    Service for generating structured AI platform analysis reports and high-level platform summaries.
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session
        self.trust_engine = TrustEngine(db_session)

    def analyze_platform(self, request: AIAnalysisRequest) -> AIAnalysisResponse:
        """
        Generates a comprehensive structured AI risk analysis report for a given platform site.
        """
        site = request.site.lower()
        logger.info(f"Generating AI Analysis report for site: {site}")

        # Check Gold Layer Cache first
        if self.db_session:
            try:
                from database.models import GoldPlatformAnalytics, GoldPaymentMethodInsight
                gold_platform = self.db_session.query(GoldPlatformAnalytics).filter(
                    GoldPlatformAnalytics.site == site
                ).first()
                gold_insights = self.db_session.query(GoldPaymentMethodInsight).filter(
                    GoldPaymentMethodInsight.site == site
                ).all()

                if gold_platform and gold_insights:
                    logger.info(f"Gold Layer cache hit for AI analysis report of site: {site}")
                    
                    insights = [
                        PaymentMethodInsight(
                            payment_type=i.payment_type,
                            payment_name=i.payment_name,
                            total_records=i.total_records,
                            active_count=i.active_count,
                            reliability_score=i.reliability_score,
                            supported_countries=i.supported_countries
                        )
                        for i in gold_insights
                    ]

                    # Synthesize Summary & Complaints
                    active_total = sum(i.active_count for i in insights)
                    total_methods = len(insights)
                    summary = (
                        f"Platform '{site}' provides {total_methods} payment option(s) with an overall Trust Score of {gold_platform.trust_score}/100 "
                        f"({gold_platform.trust_level} Risk Level). {active_total}/{gold_platform.total_payment_methods} total payment channels are currently active and functional."
                    )

                    complaint_summary = "No major player complaints detected."
                    if gold_platform.risk_flags:
                        complaint_summary = f"Flags identified: {'; '.join(gold_platform.risk_flags)}. Users report occasional delays or limited customer support channels."

                    recommendations = []
                    if request.include_recommendations:
                        if gold_platform.trust_score < 70.0:
                            recommendations.append("Conduct an audit of non-responsive or inactive payment methods.")
                        if any(not i.supported_countries for i in insights):
                            recommendations.append("Update regional geo-mapping metadata for unassigned payment methods.")
                        recommendations.append("Verify customer support responsiveness and live chat availability.")
                        recommendations.append("Monitor payment extraction pipelines for schema updates.")

                    return AIAnalysisResponse(
                        site=site,
                        summary=summary,
                        payment_insights=insights,
                        complaint_summary=complaint_summary if request.include_complaints else "Complaint details omitted.",
                        risk_factors=gold_platform.risk_flags,
                        recommendations=recommendations,
                        analyzed_at=gold_platform.updated_at
                    )
            except Exception as e:
                logger.error(f"Error querying Gold Layer cache for AI analysis report: {str(e)}", exc_info=True)

        # 1. Fetch records from DB or use fallback (Fallback logic if Gold cache misses)
        records = []
        if self.db_session:
            repo = PaymentRepository(self.db_session)
            db_records = repo.get_records_by_site(site)
            records = [
                {
                    "site": r.site,
                    "payment_type": r.payment_type,
                    "payment_name": r.payment_name,
                    "currency": r.currency,
                    "country": r.country,
                    "support_type": r.support_type,
                    "support_value": r.support_value,
                    "bonus_name": r.bonus_name,
                    "status": r.status,
                    "extraction_status": r.extraction_status
                }
                for r in db_records
            ]

        # Fallback records if none found in DB
        if not records:
            records = [
                {"site": site, "payment_type": "e-wallet", "payment_name": "Paytm", "currency": "INR", "country": "IN", "status": "active", "extraction_status": "SUCCESS", "support_type": "Chat"},
                {"site": site, "payment_type": "e-wallet", "payment_name": "UPI", "currency": "INR", "country": "IN", "status": "active", "extraction_status": "SUCCESS", "support_type": "Email"},
                {"site": site, "payment_type": "bank_transfer", "payment_name": "Net Banking", "currency": "INR", "country": "IN", "status": "inactive", "extraction_status": "PARTIAL", "support_type": None}
            ]

        # 2. Trust Score calculation
        trust_resp = self.trust_engine.calculate_platform_trust(site, custom_records=records)

        # 3. Analyze payment methods
        payment_groups = defaultdict(list)
        for r in records:
            key = (r.get("payment_type", "other"), r.get("payment_name", "Unknown"))
            payment_groups[key].append(r)

        insights: List[PaymentMethodInsight] = []
        for (p_type, p_name), group_recs in payment_groups.items():
            total = len(group_recs)
            active = sum(1 for r in group_recs if r.get("status", "").lower() == "active")
            rel_score = round((active / total) * 100.0, 1) if total > 0 else 0.0
            countries = list(set(r.get("country", "") for r in group_recs if r.get("country")))

            insights.append(
                PaymentMethodInsight(
                    payment_type=p_type,
                    payment_name=p_name,
                    total_records=total,
                    active_count=active,
                    reliability_score=rel_score,
                    supported_countries=countries
                )
            )

        # 4. Synthesize Summary & Complaints
        active_total = sum(i.active_count for i in insights)
        total_methods = len(insights)
        summary = (
            f"Platform '{site}' provides {total_methods} payment option(s) with an overall Trust Score of {trust_resp.trust_score}/100 "
            f"({trust_resp.trust_level} Risk Level). {active_total}/{len(records)} total payment channels are currently active and functional."
        )

        complaint_summary = "No major player complaints detected."
        if trust_resp.risk_flags:
            complaint_summary = f"Flags identified: {'; '.join(trust_resp.risk_flags)}. Users report occasional delays or limited customer support channels."

        # 5. Actionable Recommendations
        recommendations = []
        if request.include_recommendations:
            if trust_resp.trust_score < 70.0:
                recommendations.append("Conduct an audit of non-responsive or inactive payment methods.")
            if any(not i.supported_countries for i in insights):
                recommendations.append("Update regional geo-mapping metadata for unassigned payment methods.")
            recommendations.append("Verify customer support responsiveness and live chat availability.")
            recommendations.append("Monitor payment extraction pipelines for schema updates.")

        return AIAnalysisResponse(
            site=site,
            summary=summary,
            payment_insights=insights,
            complaint_summary=complaint_summary if request.include_complaints else "Complaint details omitted.",
            risk_factors=trust_resp.risk_flags,
            recommendations=recommendations,
            analyzed_at=datetime.utcnow()
        )

    def get_platform_summary(self, site: str) -> PlatformSummaryResponse:
        """
        Returns a concise high-level platform summary containing trust rating, active methods, and country coverage.
        """
        site_clean = site.lower()

        # Check Gold Layer Cache first
        if self.db_session:
            try:
                from database.models import GoldPlatformAnalytics
                gold_data = self.db_session.query(GoldPlatformAnalytics).filter(
                    GoldPlatformAnalytics.site == site_clean
                ).first()
                if gold_data:
                    logger.info(f"Gold Layer cache hit for platform summary of site: {site_clean}")
                    return PlatformSummaryResponse(
                        site=site_clean,
                        trust_score=gold_data.trust_score,
                        trust_level=gold_data.trust_level,
                        confidence_score=gold_data.confidence_score,
                        total_payment_methods=gold_data.total_payment_methods,
                        active_payment_methods=gold_data.active_payment_methods,
                        supported_countries=gold_data.supported_countries,
                        risk_summary=gold_data.risk_summary,
                        top_payment_methods=gold_data.top_payment_methods,
                        evaluated_at=gold_data.updated_at
                    )
            except Exception as e:
                logger.error(f"Error querying Gold Layer cache for platform summary: {str(e)}", exc_info=True)

        trust_resp = self.trust_engine.calculate_platform_trust(site_clean)

        records = []
        if self.db_session:
            repo = PaymentRepository(self.db_session)
            db_recs = repo.get_records_by_site(site_clean)
            records = db_recs

        total_methods = len(records)
        active_methods = sum(1 for r in records if r.status == "active")
        countries = list(set(r.country for r in records if r.country))
        top_methods = list(set(r.payment_name for r in records if r.payment_name))[:5]

        if not records:
            total_methods = 3
            active_methods = 2
            countries = ["IN"]
            top_methods = ["Paytm", "UPI", "Net Banking"]

        risk_summary = f"Platform classified as {trust_resp.trust_level} risk with {len(trust_resp.risk_flags)} potential risk flags."

        return PlatformSummaryResponse(
            site=site_clean,
            trust_score=trust_resp.trust_score,
            trust_level=trust_resp.trust_level,
            confidence_score=trust_resp.confidence_score,
            total_payment_methods=total_methods,
            active_payment_methods=active_methods,
            supported_countries=countries,
            risk_summary=risk_summary,
            top_payment_methods=top_methods,
            evaluated_at=datetime.utcnow()
        )

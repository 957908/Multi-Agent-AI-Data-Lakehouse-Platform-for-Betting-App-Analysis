"""
File: trust_engine.py
Purpose:
    Rule-Based Trust Score Calculation Engine connected with live Gold Layer datasets.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 5.0
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from config.settings import settings
from schemas.ai import TrustScoreResponse, RuleEvaluationResult
from repositories.payment_repository import PaymentRepository
from repositories.gold_repository import GoldRepository

logger = logging.getLogger("backend.services.ai.trust_engine")


class TrustEngine:
    """
    Rule-Based Trust Engine connected with live Gold Layer database records and auto-syncing analytics.
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session
        self.w_completeness = settings.TRUST_WEIGHT_COMPLETENESS  # 25.0
        self.w_diversity = settings.TRUST_WEIGHT_DIVERSITY        # 30.0
        self.w_quality = settings.TRUST_WEIGHT_QUALITY            # 25.0
        self.w_footprint = settings.TRUST_WEIGHT_FOOTPRINT          # 20.0

    def calculate_platform_trust(self, site: str, custom_records: Optional[List[Dict[str, Any]]] = None, sync_gold: bool = True) -> TrustScoreResponse:
        """
        Calculates normalized trust score for a platform by evaluating live database records against modular rules.
        Auto-syncs computed trust metrics with the Gold Layer (gold_platform_analytics table).
        """
        site_clean = site.lower()
        logger.info(f"Executing Gold-integrated Trust Engine calculation for site: {site_clean}")

        records = custom_records
        db_records = []
        if records is None and self.db_session is not None:
            payment_repo = PaymentRepository(self.db_session)
            db_records = payment_repo.get_records_by_site(site_clean)
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
                    "extraction_status": r.extraction_status,
                    "status": r.status,
                    "scraped_at": r.scraped_at
                }
                for r in db_records
            ]

        if not records:
            # Check if Gold analytics pre-exist even if raw silver records are absent
            if self.db_session:
                gold_repo = GoldRepository(self.db_session)
                gold_analytics = gold_repo.get_platform_analytics(site_clean)
                if gold_analytics:
                    logger.info(f"Loaded pre-computed Gold analytics for site '{site_clean}'")
                    return TrustScoreResponse(
                        site=gold_analytics.site,
                        trust_score=gold_analytics.trust_score,
                        trust_level=gold_analytics.trust_level,
                        confidence_score=gold_analytics.confidence_score,
                        score_explanation=f"Pre-computed Gold Layer analytics for platform '{gold_analytics.site}'.",
                        rule_evaluations=[],
                        risk_flags=gold_analytics.risk_flags or [],
                        evaluated_at=gold_analytics.updated_at
                    )

            logger.warning(f"No records found for site '{site_clean}'. Returning baseline default score.")
            return TrustScoreResponse(
                site=site_clean,
                trust_score=40.0,
                trust_level="LOW",
                confidence_score=0.10,
                score_explanation=f"Platform '{site_clean}' has insufficient scraped data. Assigned default baseline score of 40.0.",
                rule_evaluations=[
                    RuleEvaluationResult(
                        rule_name="Data Volume Check",
                        passed=False,
                        score_contribution=0.0,
                        max_weight=100.0,
                        description="No scraped payment records available for evaluation."
                    )
                ],
                risk_flags=["Insufficient platform data", "Unverified payment infrastructure"],
                evaluated_at=datetime.utcnow()
            )

        # Evaluate rules
        rule_results: List[RuleEvaluationResult] = []
        risk_flags: List[str] = []

        # Rule 1: Data Completeness (Max 25 pts)
        rule_1 = self._eval_completeness(records)
        rule_results.append(rule_1)
        if not rule_1.passed:
            risk_flags.append("Incomplete support or bonus metadata")

        # Rule 2: Payment Method Diversity (Max 30 pts)
        rule_2 = self._eval_diversity(records)
        rule_results.append(rule_2)
        if not rule_2.passed:
            risk_flags.append("Limited payment method options (< 3 distinct methods)")

        # Rule 3: Extraction & Data Quality (Max 25 pts)
        rule_3 = self._eval_quality(records)
        rule_results.append(rule_3)
        if not rule_3.passed:
            risk_flags.append("Elevated extraction failure rate or inactive payment channels")

        # Rule 4: Platform Footprint & Regional Coverage (Max 20 pts)
        rule_4 = self._eval_footprint(records)
        rule_results.append(rule_4)
        if not rule_4.passed:
            risk_flags.append("Narrow regional reach or restricted currency support")

        # Compute total trust score
        total_score = round(sum(r.score_contribution for r in rule_results), 1)
        total_score = max(0.0, min(100.0, total_score))

        # Assign Trust Level
        if total_score >= 75.0:
            trust_level = "HIGH"
        elif total_score >= 50.0:
            trust_level = "MEDIUM"
        else:
            trust_level = "LOW"

        confidence = round(min(1.0, len(records) / 10.0), 2)
        explanation = (
            f"Platform '{site_clean}' achieved a Trust Score of {total_score}/100 ({trust_level} Trust Level) "
            f"evaluated across {len(records)} payment record(s). Passed {sum(1 for r in rule_results if r.passed)}/4 modular trust rules."
        )

        response = TrustScoreResponse(
            site=site_clean,
            trust_score=total_score,
            trust_level=trust_level,
            confidence_score=confidence,
            score_explanation=explanation,
            rule_evaluations=rule_results,
            risk_flags=risk_flags,
            evaluated_at=datetime.utcnow()
        )

        # Auto-sync with Gold Layer
        if sync_gold and self.db_session is not None and custom_records is None:
            try:
                gold_repo = GoldRepository(self.db_session)
                active_count = sum(1 for r in records if r.get("status", "").lower() == "active")
                countries = list(set(r.get("country") for r in records if r.get("country")))
                methods = list(set(r.get("payment_name") for r in records if r.get("payment_name")))[:5]
                last_scraped = max([r.get("scraped_at") for r in records if r.get("scraped_at")] or [datetime.utcnow()])

                gold_repo.upsert_platform_analytics({
                    "site": site_clean,
                    "trust_score": total_score,
                    "trust_level": trust_level,
                    "confidence_score": confidence,
                    "total_payment_methods": len(records),
                    "active_payment_methods": active_count,
                    "supported_countries": countries,
                    "top_payment_methods": methods,
                    "risk_summary": f"Platform evaluated as {trust_level} trust ({total_score}/100) with {len(risk_flags)} risk flag(s).",
                    "risk_flags": risk_flags,
                    "last_scraped_at": last_scraped
                })
                logger.info(f"Successfully synced Trust Score to Gold Layer for site '{site_clean}'")
            except Exception as e:
                logger.warning(f"Could not sync Gold analytics for site '{site_clean}': {e}")

        return response

    def _eval_completeness(self, records: List[Dict[str, Any]]) -> RuleEvaluationResult:
        total = len(records)
        complete_count = sum(
            1 for r in records
            if r.get("support_type") or r.get("support_value") or r.get("bonus_name")
        )
        ratio = complete_count / total if total > 0 else 0.0
        score = round(ratio * self.w_completeness, 1)
        passed = ratio >= 0.5

        return RuleEvaluationResult(
            rule_name="Metadata Completeness",
            passed=passed,
            score_contribution=score,
            max_weight=self.w_completeness,
            description=f"{complete_count}/{total} records ({int(ratio*100)}%) contain full customer support or bonus metadata."
        )

    def _eval_diversity(self, records: List[Dict[str, Any]]) -> RuleEvaluationResult:
        unique_methods = set(r.get("payment_name") for r in records if r.get("payment_name"))
        unique_types = set(r.get("payment_type") for r in records if r.get("payment_type"))
        method_count = len(unique_methods)

        if method_count >= 6:
            score = self.w_diversity
            passed = True
        elif method_count >= 3:
            score = round(self.w_diversity * 0.75, 1)
            passed = True
        elif method_count >= 1:
            score = round(self.w_diversity * 0.40, 1)
            passed = False
        else:
            score = 0.0
            passed = False

        return RuleEvaluationResult(
            rule_name="Payment Diversity",
            passed=passed,
            score_contribution=score,
            max_weight=self.w_diversity,
            description=f"Found {method_count} unique payment method(s) across {len(unique_types)} payment category/categories."
        )

    def _eval_quality(self, records: List[Dict[str, Any]]) -> RuleEvaluationResult:
        total = len(records)
        success_count = sum(
            1 for r in records
            if r.get("extraction_status", "").upper() == "SUCCESS" and r.get("status", "").lower() == "active"
        )
        ratio = success_count / total if total > 0 else 0.0
        score = round(ratio * self.w_quality, 1)
        passed = ratio >= 0.70

        return RuleEvaluationResult(
            rule_name="Extraction Data Quality",
            passed=passed,
            score_contribution=score,
            max_weight=self.w_quality,
            description=f"{success_count}/{total} records ({int(ratio*100)}%) successfully extracted with active status."
        )

    def _eval_footprint(self, records: List[Dict[str, Any]]) -> RuleEvaluationResult:
        currencies = set(r.get("currency") for r in records if r.get("currency"))
        countries = set(r.get("country") for r in records if r.get("country"))
        
        has_multi_currency = len(currencies) > 1 or len(countries) > 1
        score = self.w_footprint if has_multi_currency else round(self.w_footprint * 0.60, 1)
        passed = len(currencies) >= 1 and len(countries) >= 1

        return RuleEvaluationResult(
            rule_name="Regional Footprint",
            passed=passed,
            score_contribution=score,
            max_weight=self.w_footprint,
            description=f"Supports {len(currencies)} currency/currencies across {len(countries)} country region(s)."
        )

"""
File: gold_repository.py
Purpose:
    Encapsulates database access patterns for Gold Layer platform analytics and payment insights tables.
Author: Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 5.0
"""

import logging
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy import desc, asc, or_
from sqlalchemy.orm import Session
from database.models import GoldPlatformAnalytics, GoldPaymentMethodInsight

logger = logging.getLogger("backend.repositories.gold_repository")


class GoldRepository:
    """
    Repository class providing access and persistence methods for Gold Layer tables.
    """

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def get_platform_analytics(self, site: str) -> Optional[GoldPlatformAnalytics]:
        """Retrieves pre-computed Gold platform analytics by site domain."""
        if not self.db:
            return None
        return self.db.query(GoldPlatformAnalytics).filter(
            GoldPlatformAnalytics.site.ilike(site)
        ).first()

    def list_platform_analytics(
        self,
        q: Optional[str] = None,
        site: Optional[str] = None,
        risk_level: Optional[str] = None,
        min_trust_score: Optional[float] = None,
        max_trust_score: Optional[float] = None,
        country: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "trust_score",
        sort_order: str = "desc"
    ) -> Tuple[List[GoldPlatformAnalytics], int]:
        """
        Retrieves a paginated list of Gold platform analytics matching criteria.
        """
        if not self.db:
            return [], 0

        query = self.db.query(GoldPlatformAnalytics)

        if q:
            pattern = f"%{q}%"
            query = query.filter(
                or_(
                    GoldPlatformAnalytics.site.ilike(pattern),
                    GoldPlatformAnalytics.risk_summary.ilike(pattern),
                    GoldPlatformAnalytics.trust_level.ilike(pattern)
                )
            )

        if site:
            query = query.filter(GoldPlatformAnalytics.site.ilike(f"%{site}%"))
        if risk_level:
            query = query.filter(GoldPlatformAnalytics.trust_level.ilike(risk_level))
        if min_trust_score is not None:
            query = query.filter(GoldPlatformAnalytics.trust_score >= min_trust_score)
        if max_trust_score is not None:
            query = query.filter(GoldPlatformAnalytics.trust_score <= max_trust_score)

        total_count = query.count()

        sort_col = sort_by if hasattr(GoldPlatformAnalytics, sort_by) else "trust_score"
        sort_attr = getattr(GoldPlatformAnalytics, sort_col)
        sort_expr = desc(sort_attr) if sort_order.lower() == "desc" else asc(sort_attr)
        query = query.order_by(sort_expr)

        offset = (page - 1) * size
        results = query.offset(offset).limit(size).all()

        # In-memory country filtering if JSONB array filtering is needed across sqlite/pg
        if country and results:
            filtered_results = [
                r for r in results
                if r.supported_countries and any(country.upper() == c.upper() for c in r.supported_countries)
            ]
            return filtered_results, len(filtered_results)

        return results, total_count

    def get_payment_insights(self, site: str) -> List[GoldPaymentMethodInsight]:
        """Retrieves payment method insights for a platform site."""
        if not self.db:
            return []
        return self.db.query(GoldPaymentMethodInsight).filter(
            GoldPaymentMethodInsight.site.ilike(site)
        ).all()

    def search_payment_insights(
        self,
        site: Optional[str] = None,
        payment_type: Optional[str] = None,
        payment_name: Optional[str] = None,
        country: Optional[str] = None
    ) -> List[GoldPaymentMethodInsight]:
        """Searches payment method insights across platforms and payment types."""
        if not self.db:
            return []

        query = self.db.query(GoldPaymentMethodInsight)
        if site:
            query = query.filter(GoldPaymentMethodInsight.site.ilike(f"%{site}%"))
        if payment_type:
            query = query.filter(GoldPaymentMethodInsight.payment_type.ilike(f"%{payment_type}%"))
        if payment_name:
            query = query.filter(GoldPaymentMethodInsight.payment_name.ilike(f"%{payment_name}%"))

        results = query.all()
        if country and results:
            results = [
                r for r in results
                if r.supported_countries and any(country.upper() == c.upper() for c in r.supported_countries)
            ]
        return results

    def upsert_platform_analytics(self, analytics_data: Dict[str, Any]) -> GoldPlatformAnalytics:
        """Upserts a GoldPlatformAnalytics record into PostgreSQL."""
        if not self.db:
            raise ValueError("Database session required for upsert.")

        site = analytics_data["site"].lower()
        existing = self.db.query(GoldPlatformAnalytics).filter(
            GoldPlatformAnalytics.site.ilike(site)
        ).first()

        now = datetime.utcnow()
        if existing:
            existing.trust_score = analytics_data.get("trust_score", existing.trust_score)
            existing.trust_level = analytics_data.get("trust_level", existing.trust_level)
            existing.confidence_score = analytics_data.get("confidence_score", existing.confidence_score)
            existing.total_payment_methods = analytics_data.get("total_payment_methods", existing.total_payment_methods)
            existing.active_payment_methods = analytics_data.get("active_payment_methods", existing.active_payment_methods)
            existing.supported_countries = analytics_data.get("supported_countries", existing.supported_countries)
            existing.top_payment_methods = analytics_data.get("top_payment_methods", existing.top_payment_methods)
            existing.risk_summary = analytics_data.get("risk_summary", existing.risk_summary)
            existing.risk_flags = analytics_data.get("risk_flags", existing.risk_flags)
            existing.last_scraped_at = analytics_data.get("last_scraped_at", now)
            existing.updated_at = now
            record = existing
        else:
            record = GoldPlatformAnalytics(
                site=site,
                trust_score=analytics_data.get("trust_score", 50.0),
                trust_level=analytics_data.get("trust_level", "MEDIUM"),
                confidence_score=analytics_data.get("confidence_score", 0.5),
                total_payment_methods=analytics_data.get("total_payment_methods", 0),
                active_payment_methods=analytics_data.get("active_payment_methods", 0),
                supported_countries=analytics_data.get("supported_countries", []),
                top_payment_methods=analytics_data.get("top_payment_methods", []),
                risk_summary=analytics_data.get("risk_summary", "Evaluation pending."),
                risk_flags=analytics_data.get("risk_flags", []),
                last_scraped_at=analytics_data.get("last_scraped_at", now),
                updated_at=now
            )
            self.db.add(record)

        self.db.commit()
        self.db.refresh(record)
        return record

"""
File: payment_repository.py
Purpose:
    Encapsulates database access patterns for the payment_records table.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 2.0
"""

from typing import List, Tuple, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import func, desc, asc, or_
from sqlalchemy.orm import Session
from database.models import PaymentRecordModel


class PaymentRepository:
    """
    Repository class providing data access methods for PaymentRecordModel.
    Supports both instance-based and static invocation patterns.
    """

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def get_records_by_site(self, site: str) -> List[PaymentRecordModel]:
        """Retrieves all payment records for a given site/platform domain."""
        if not self.db:
            return []
        return self.db.query(PaymentRecordModel).filter(
            PaymentRecordModel.site.ilike(site)
        ).all()

    def get_paginated_records(self, page: int = 1, size: int = 20) -> Tuple[List[PaymentRecordModel], int]:
        """Retrieves paginated records for general listings."""
        if not self.db:
            return [], 0
        return self.list_records(self.db, page=page, size=size)

    def search_records(
        self,
        q: Optional[str] = None,
        site: Optional[str] = None,
        payment_name: Optional[str] = None,
        payment_type: Optional[str] = None,
        country: Optional[str] = None,
        currency: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "scraped_at",
        sort_order: str = "desc"
    ) -> Tuple[List[PaymentRecordModel], int]:
        """
        Advanced multi-field search and filtering across payment records.
        """
        db_sess = self.db
        if not db_sess:
            return [], 0

        query = db_sess.query(PaymentRecordModel)

        # Free text search query 'q'
        if q:
            search_pattern = f"%{q}%"
            query = query.filter(
                or_(
                    PaymentRecordModel.site.ilike(search_pattern),
                    PaymentRecordModel.payment_name.ilike(search_pattern),
                    PaymentRecordModel.payment_type.ilike(search_pattern),
                    PaymentRecordModel.bonus_name.ilike(search_pattern)
                )
            )

        # Explicit filters
        if site:
            query = query.filter(PaymentRecordModel.site.ilike(f"%{site}%"))
        if payment_name:
            query = query.filter(PaymentRecordModel.payment_name.ilike(f"%{payment_name}%"))
        if payment_type:
            query = query.filter(PaymentRecordModel.payment_type.ilike(f"%{payment_type}%"))
        if country:
            query = query.filter(PaymentRecordModel.country.ilike(country))
        if currency:
            query = query.filter(PaymentRecordModel.currency.ilike(currency))
        if status:
            query = query.filter(PaymentRecordModel.status.ilike(status))

        total_count = query.count()

        # Dynamic Sorting
        sort_col = sort_by if hasattr(PaymentRecordModel, sort_by) else "scraped_at"
        sort_attr = getattr(PaymentRecordModel, sort_col)
        sort_expression = desc(sort_attr) if sort_order.lower() == "desc" else asc(sort_attr)
        query = query.order_by(sort_expression)

        # Pagination
        offset = (page - 1) * size
        records = query.offset(offset).limit(size).all()

        return records, total_count

    @staticmethod
    def get_by_id(db: Session, record_id: UUID) -> Optional[PaymentRecordModel]:
        """Retrieves a single payment record by its unique UUID."""
        return db.query(PaymentRecordModel).filter(PaymentRecordModel.id == record_id).first()

    @staticmethod
    def list_records(
        db: Session,
        site: Optional[str] = None,
        payment_type: Optional[str] = None,
        status: Optional[str] = None,
        country: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[PaymentRecordModel], int]:
        """Retrieves a paginated list of payment records matching filter parameters."""
        query = db.query(PaymentRecordModel)

        if site:
            query = query.filter(PaymentRecordModel.site.ilike(site))
        if payment_type:
            query = query.filter(PaymentRecordModel.payment_type.ilike(payment_type))
        if status:
            query = query.filter(PaymentRecordModel.status.ilike(status))
        if country:
            query = query.filter(PaymentRecordModel.country.ilike(country))

        total_count = query.count()

        sort_col = sort_by if hasattr(PaymentRecordModel, sort_by) else "created_at"
        sort_attr = getattr(PaymentRecordModel, sort_col)
        sort_expression = desc(sort_attr) if sort_order.lower() == "desc" else asc(sort_attr)
        query = query.order_by(sort_expression)

        offset = (page - 1) * size
        records = query.offset(offset).limit(size).all()

        return records, total_count

    @staticmethod
    def get_statistics(db: Session) -> Dict[str, Any]:
        """Aggregates summary statistics from stored payment records."""
        total_records = db.query(PaymentRecordModel).count()
        unique_sites = db.query(PaymentRecordModel.site).distinct().count()
        unique_payment_types = db.query(PaymentRecordModel.payment_type).distinct().count()

        site_counts = db.query(
            PaymentRecordModel.site,
            func.count(PaymentRecordModel.id).label("count")
        ).group_by(PaymentRecordModel.site).all()

        type_counts = db.query(
            PaymentRecordModel.payment_type,
            func.count(PaymentRecordModel.id).label("count")
        ).group_by(PaymentRecordModel.payment_type).all()

        country_counts = db.query(
            PaymentRecordModel.country,
            func.count(PaymentRecordModel.id).label("count")
        ).group_by(PaymentRecordModel.country).all()

        return {
            "total_records": total_records,
            "unique_sites": unique_sites,
            "unique_payment_types": unique_payment_types,
            "distribution_by_site": [{"site": row[0], "count": row[1]} for row in site_counts],
            "distribution_by_type": [{"payment_type": row[0], "count": row[1]} for row in type_counts],
            "distribution_by_country": [{"country": row[0], "count": row[1]} for row in country_counts]
        }

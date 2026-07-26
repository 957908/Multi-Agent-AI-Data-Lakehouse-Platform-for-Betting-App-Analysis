"""
File: payment_repository.py
Purpose:
    Encapsulates database access patterns for the payment_records table.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

from typing import List, Tuple, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import func, desc, asc
from sqlalchemy.orm import Session
from database.models import PaymentRecordModel


class PaymentRepository:
    """
    Repository class providing access methods for PaymentRecordModel.
    """

    @staticmethod
    def get_by_id(db: Session, record_id: UUID) -> Optional[PaymentRecordModel]:
        """
        Retrieves a single payment record by its unique ID.
        """
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
        """
        Retrieves a paginated list of payment records matching filter parameters.
        """
        query = db.query(PaymentRecordModel)

        # Filters
        if site:
            query = query.filter(PaymentRecordModel.site.ilike(site))
        if payment_type:
            query = query.filter(PaymentRecordModel.payment_type.ilike(payment_type))
        if status:
            query = query.filter(PaymentRecordModel.status.ilike(status))
        if country:
            query = query.filter(PaymentRecordModel.country.ilike(country))

        # Total count before pagination limit
        total_count = query.count()

        # Sorting
        if hasattr(PaymentRecordModel, sort_by):
            sort_attr = getattr(PaymentRecordModel, sort_by)
            sort_expression = desc(sort_attr) if sort_order.lower() == "desc" else asc(sort_attr)
            query = query.order_by(sort_expression)
        else:
            query = query.order_by(desc(PaymentRecordModel.created_at))

        # Pagination
        offset = (page - 1) * size
        records = query.offset(offset).limit(size).all()

        return records, total_count

    @staticmethod
    def get_statistics(db: Session) -> Dict[str, Any]:
        """
        Aggregates summary statistics from stored payment records.
        """
        total_records = db.query(PaymentRecordModel).count()
        unique_sites = db.query(PaymentRecordModel.site).distinct().count()
        unique_payment_types = db.query(PaymentRecordModel.payment_type).distinct().count()

        # Group by Distributions
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

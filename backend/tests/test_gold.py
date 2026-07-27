"""
File: test_gold.py
Purpose:
    Integration testing for the Gold Layer aggregation pipeline and backend query optimizations.
    Mocks database calls to enable 100% local, fast verification.
Author: Priya Iyer
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

import sys
import shutil
import unittest
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch

# Ensure backend/app/ is in python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

import pandas as pd
from config.settings import settings
from database.models import PaymentRecordModel, GoldPlatformAnalytics, GoldPaymentMethodInsight
from services.etl.gold_pipeline import GoldPipeline
from services.ai.ai_analysis import AIAnalysisService
from schemas.ai import AIAnalysisRequest


class TestGoldLayer(unittest.TestCase):
    """
    Test suite verifying Gold Layer aggregations, parquet storage,
    database upserts, and backend service optimizations.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Sets up temporary directories for local Parquet files."""
        cls.test_dir = Path(__file__).resolve().parent / "test_data_gold"
        cls.test_dir.mkdir(exist_ok=True)
        
        # Override paths to target the test data directory
        settings.SILVER_DATA_DIR = str(cls.test_dir / "silver")

        # Mock Silver dataset records in memory
        cls.mock_silver_records = [
            PaymentRecordModel(
                site="melbet",
                payment_type="UPI",
                payment_name="UPI Instant",
                currency="INR",
                country="IN",
                support_type="live_chat",
                support_value="https://melbet.support",
                bonus_name="Welcome Bonus",
                status="active",
                extraction_status="SUCCESS",
                scraped_at=datetime(2026, 7, 26, 12, 0, 0),
                source_url="https://melbet.com/payments"
            ),
            PaymentRecordModel(
                site="melbet",
                payment_type="Cryptocurrency",
                payment_name="Bitcoin",
                currency="INR",
                country="IN",
                support_type="live_chat",
                support_value="https://melbet.support",
                bonus_name="Welcome Bonus",
                status="active",
                extraction_status="SUCCESS",
                scraped_at=datetime(2026, 7, 26, 12, 0, 0),
                source_url="https://melbet.com/payments"
            )
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        """Cleans up the temporary directories."""
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir, ignore_errors=True)

    def test_gold_aggregation_pipeline(self) -> None:
        """
        Tests the Gold aggregation pipeline: reads Silver records,
        aggregates them, saves Parquet, and upserts to PostgreSQL.
        """
        # Mock database session
        mock_db = MagicMock()
        
        # Mock query return values
        # 1. Distinct sites query
        mock_db.query.return_value.distinct.return_value.all.return_value = [("melbet",)]
        # 2. Site records query
        mock_db.query.return_value.filter.return_value.all.return_value = self.mock_silver_records

        run_path_key = "2026-07-27/10-00"
        pipeline = GoldPipeline(mock_db)
        
        result = pipeline.run_aggregation(run_path_key)

        # Assert pipeline success telemetry
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["platform_count"], 1)
        self.assertEqual(result["insight_count"], 2)  # UPI and Cryptocurrency

        # Verify Gold Parquet file outputs
        gold_root = Path(settings.SILVER_DATA_DIR).parent / "gold"
        
        analytics_file = gold_root / "platform_analytics" / run_path_key / "platform_analytics.parquet"
        self.assertTrue(analytics_file.exists(), "Gold Platform Analytics Parquet was not created.")
        
        insights_file = gold_root / "payment_method_insights" / run_path_key / "payment_method_insights.parquet"
        self.assertTrue(insights_file.exists(), "Gold Payment Method Insights Parquet was not created.")

        # Read generated Parquet to verify accuracy of pre-calculated scores
        analytics_df = pd.read_parquet(str(analytics_file))
        self.assertEqual(len(analytics_df), 1)
        self.assertEqual(analytics_df.iloc[0]["site"], "melbet")
        self.assertGreater(analytics_df.iloc[0]["trust_score"], 40.0)
        self.assertEqual(analytics_df.iloc[0]["total_payment_methods"], 2)

        # Verify database execute calls (for upserts)
        self.assertGreaterEqual(mock_db.execute.call_count, 3)  # 1 platform summary + 2 insights upserts
        mock_db.commit.assert_called_once()

    def test_backend_caching_and_optimizations(self) -> None:
        """
        Tests that AIAnalysisService queries Gold Layer tables first,
        and uses them as a fast-path cache before falling back.
        """
        mock_db = MagicMock()
        
        # Setup mock Gold data
        mock_gold_platform = GoldPlatformAnalytics(
            site="melbet",
            trust_score=85.0,
            trust_level="HIGH",
            confidence_score=0.90,
            total_payment_methods=12,
            active_payment_methods=10,
            supported_countries=["IN", "BG"],
            top_payment_methods=["UPI", "Paytm", "PhonePe"],
            risk_summary="Low risk platform based on Gold Layer pre-computations",
            risk_flags=["Minimal risk indicators"],
            last_scraped_at=datetime(2026, 7, 26, 12, 0, 0),
            updated_at=datetime(2026, 7, 27, 8, 0, 0)
        )
        
        mock_gold_insights = [
            GoldPaymentMethodInsight(
                site="melbet",
                payment_type="UPI",
                payment_name="UPI Instant",
                total_records=5,
                active_count=5,
                reliability_score=100.0,
                supported_countries=["IN"]
            )
        ]

        # Configure the db query mock to return our Gold Layer objects
        # First query (GoldPlatformAnalytics) -> returns mock_gold_platform
        # Second query (GoldPaymentMethodInsight) -> returns mock_gold_insights
        mock_db.query.return_value.filter.return_value.first.return_value = mock_gold_platform
        mock_db.query.return_value.filter.return_value.all.return_value = mock_gold_insights

        service = AIAnalysisService(mock_db)

        # 1. Test get_platform_summary Cache Hit
        summary_resp = service.get_platform_summary("melbet")
        self.assertEqual(summary_resp.site, "melbet")
        self.assertEqual(summary_resp.trust_score, 85.0)
        self.assertEqual(summary_resp.trust_level, "HIGH")
        self.assertEqual(summary_resp.total_payment_methods, 12)
        self.assertEqual(summary_resp.risk_summary, "Low risk platform based on Gold Layer pre-computations")

        # 2. Test analyze_platform Cache Hit
        req = AIAnalysisRequest(site="melbet", include_recommendations=True, include_complaints=True)
        analysis_resp = service.analyze_platform(req)
        self.assertEqual(analysis_resp.site, "melbet")
        self.assertIn("overall Trust Score of 85.0/100", analysis_resp.summary)
        self.assertEqual(len(analysis_resp.payment_insights), 1)
        self.assertEqual(analysis_resp.payment_insights[0].reliability_score, 100.0)
        self.assertEqual(analysis_resp.risk_factors, ["Minimal risk indicators"])


if __name__ == "__main__":
    unittest.main()

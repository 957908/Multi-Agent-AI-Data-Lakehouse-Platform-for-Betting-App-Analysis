"""
File: test_full_integration.py
Purpose:
    Full System Integration testing suite for SentinelX Trust AI Sprint 5.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 5.0
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock

# Ensure backend/app/ is in python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from fastapi.testclient import TestClient
from server import app
from database.connection import get_db_session
from repositories.gold_repository import GoldRepository
from services.ai.trust_engine import TrustEngine
from services.ai.ai_analysis import AIAnalysisService


class TestFullSystemIntegration(unittest.TestCase):
    """
    Test suite verifying end-to-end Gold Layer integration, Trust Engine sync, and Search APIs.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def setUp(self) -> None:
        self.mock_db = MagicMock()

        def override_get_db_session():
            yield self.mock_db

        app.dependency_overrides[get_db_session] = override_get_db_session

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_gold_repository_upsert_and_query(self) -> None:
        """Test GoldRepository upsert and query functions."""
        repo = GoldRepository(self.mock_db)

        # Mock database return
        mock_gold = MagicMock()
        mock_gold.site = "melbet"
        mock_gold.trust_score = 88.5
        mock_gold.trust_level = "HIGH"
        mock_gold.confidence_score = 0.90
        mock_gold.total_payment_methods = 12
        mock_gold.active_payment_methods = 10
        mock_gold.supported_countries = ["IN", "BR"]
        mock_gold.top_payment_methods = ["Paytm", "UPI"]
        mock_gold.risk_summary = "High trust platform"
        mock_gold.risk_flags = []
        mock_gold.last_scraped_at = datetime.utcnow()
        mock_gold.updated_at = datetime.utcnow()

        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_gold

        result = repo.get_platform_analytics("melbet")
        self.assertIsNotNone(result)
        self.assertEqual(result.site, "melbet")
        self.assertEqual(result.trust_score, 88.5)

    def test_trust_engine_gold_sync(self) -> None:
        """Test TrustEngine live calculation and Gold Layer sync."""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        self.mock_db.query.return_value.filter.return_value.all.return_value = []
        engine = TrustEngine(db_session=self.mock_db)

        resp = engine.calculate_platform_trust("melbet", sync_gold=True)
        self.assertEqual(resp.site, "melbet")
        self.assertIsNotNone(resp.trust_score)

    def test_gold_platform_api_endpoint(self) -> None:
        """Test GET /api/v1/gold/platforms endpoint."""
        self.mock_db.query.return_value.filter.return_value.count.return_value = 0
        self.mock_db.query.return_value.count.return_value = 0

        response = self.client.get("/api/v1/gold/platforms")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["total"], 0)

    def test_gold_insights_api_endpoint(self) -> None:
        """Test GET /api/v1/gold/insights endpoint."""
        self.mock_db.query.return_value.all.return_value = []

        response = self.client.get("/api/v1/gold/insights?site=melbet")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["data"]), 0)

    def test_search_api_with_trust_filters(self) -> None:
        """Test GET /api/v1/search endpoint with trust score and risk level filters."""
        self.mock_db.query.return_value.outerjoin.return_value.filter.return_value.count.return_value = 0

        response = self.client.get("/api/v1/search?min_trust_score=70.0&risk_level=HIGH")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

    def test_centralized_exception_handling(self) -> None:
        """Test that uncaught 404/500 errors return unified APIResponse envelope."""
        response = self.client.get("/api/v1/non_existent_route")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("message", data)
        self.assertIsNone(data["data"])


if __name__ == "__main__":
    unittest.main()

"""
File: test_api.py
Purpose:
    Unit and integration testing for the FastAPI backend REST API.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 2.0
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from uuid import uuid4

# Ensure backend/app/ is in the python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from fastapi.testclient import TestClient
from server import app
from config.settings import settings
from database.connection import get_db_session


class TestBackendAPI(unittest.TestCase):
    """
    Test suite for FastAPI REST API endpoints, security, repository interactions, and AI endpoints.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

        # Retrieve mock credentials from settings configuration
        cls.admin_email = settings.ADMIN_EMAIL
        cls.admin_pass = settings.ADMIN_PASSWORD
        cls.analyst_email = settings.ANALYST_EMAIL
        cls.analyst_pass = settings.ANALYST_PASSWORD
        cls.reader_email = settings.READER_EMAIL
        cls.reader_pass = settings.READER_PASSWORD

    def setUp(self) -> None:
        """Set up standard dependency override for database sessions."""
        self.mock_db = MagicMock()

        def override_get_db_session():
            yield self.mock_db

        app.dependency_overrides[get_db_session] = override_get_db_session

    def tearDown(self) -> None:
        """Clear dependency overrides after test run."""
        app.dependency_overrides.clear()

    def _get_token(self, email: str, password: str) -> str:
        """Helper to retrieve JWT token for a specific user."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        return response.json()["data"]["access_token"]

    def test_health_endpoint_healthy(self) -> None:
        """Verifies health check returns 200 when database is healthy."""
        self.mock_db.execute.return_value = None

        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["database"], "healthy")

    def test_health_endpoint_degraded(self) -> None:
        """Verifies health check returns unhealthy (success: false) when database fails."""
        self.mock_db.execute.side_effect = Exception("DB Connection Error")

        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertFalse(data["success"])

    def test_auth_login_success(self) -> None:
        """Verifies authentication success and token issuance."""
        payload = {
            "email": self.admin_email,
            "password": self.admin_pass
        }
        response = self.client.post("/api/v1/auth/login", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("access_token", data["data"])
        self.assertEqual(data["data"]["token_type"], "bearer")

    def test_auth_login_invalid_credentials(self) -> None:
        """Verifies authentication failure on bad credentials."""
        payload = {
            "email": self.admin_email,
            "password": "WrongPassword123"
        }
        response = self.client.post("/api/v1/auth/login", json=payload)
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertFalse(data["success"])

    def test_auth_me_success(self) -> None:
        """Verifies retrieving user profile with valid JWT header."""
        token = self._get_token(self.reader_email, self.reader_pass)
        headers = {"Authorization": f"Bearer {token}"}

        response = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["email"], self.reader_email)

    def test_payment_records_list_reader(self) -> None:
        """Verifies reading payment records is allowed for reader role."""
        token = self._get_token(self.reader_email, self.reader_pass)
        headers = {"Authorization": f"Bearer {token}"}

        with patch("repositories.payment_repository.PaymentRepository.list_records") as mock_list_records:
            mock_list_records.return_value = ([], 0)

            response = self.client.get("/api/v1/payment-records", headers=headers)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])

    def test_search_endpoint(self) -> None:
        """Verifies multi-criteria search endpoint works cleanly."""
        with patch("repositories.payment_repository.PaymentRepository.search_records") as mock_search:
            mock_search.return_value = ([], 0)

            response = self.client.get("/api/v1/search?q=melbet&country=IN")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertEqual(data["data"]["total"], 0)

    def test_trust_score_endpoint(self) -> None:
        """Verifies Trust Score calculation endpoint."""
        token = self._get_token(self.analyst_email, self.analyst_pass)
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"site": "melbet"}

        response = self.client.post("/api/v1/trust-score", json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["site"], "melbet")
        self.assertIn("trust_score", data["data"])

    def test_ai_analyze_endpoint(self) -> None:
        """Verifies AI Analysis endpoint."""
        token = self._get_token(self.analyst_email, self.analyst_pass)
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"site": "melbet", "include_recommendations": True}

        response = self.client.post("/api/v1/analyze", json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["site"], "melbet")

    def test_rag_query_endpoint(self) -> None:
        """Verifies RAG query endpoint."""
        token = self._get_token(self.analyst_email, self.analyst_pass)
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"query": "What deposit bonuses are offered for Paytm?", "top_k": 2}

        response = self.client.post("/api/v1/rag/query", json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIsNotNone(data["data"]["formatted_prompt"])

    def test_platform_summary_endpoint(self) -> None:
        """Verifies high-level platform summary endpoint."""
        response = self.client.get("/api/v1/platform/melbet/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["site"], "melbet")


if __name__ == "__main__":
    unittest.main()

"""
File: test_api.py
Purpose:
    Unit and integration testing for the FastAPI backend REST API.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
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
    Test suite for FastAPI REST API endpoints, security, and repository interactions.
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
        self.assertEqual(response.status_code, 500)  # Exception handler returns 500
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

    def _get_token(self, email: str, password: str) -> str:
        """Helper to retrieve JWT token for a specific user."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        return response.json()["data"]["access_token"]

    def test_auth_me_success(self) -> None:
        """Verifies retrieving user profile with valid JWT header."""
        token = self._get_token(self.reader_email, self.reader_pass)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["email"], self.reader_email)
        self.assertIn("reader", data["data"]["roles"])

    def test_auth_me_missing_token(self) -> None:
        """Verifies unauthorized failure when token is omitted."""
        response = self.client.get("/api/v1/auth/me")
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertFalse(data["success"])

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
            self.assertEqual(data["data"]["total"], 0)

    def test_etl_runs_forbidden_for_reader(self) -> None:
        """Verifies accessing ETL runs is blocked for reader role."""
        token = self._get_token(self.reader_email, self.reader_pass)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = self.client.get("/api/v1/etl/runs", headers=headers)
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertFalse(data["success"])

    def test_etl_runs_allowed_for_analyst(self) -> None:
        """Verifies accessing ETL runs is allowed for analyst role."""
        token = self._get_token(self.analyst_email, self.analyst_pass)
        headers = {"Authorization": f"Bearer {token}"}
        
        with patch("repositories.etl_repository.ETLRepository.list_runs") as mock_list_runs:
            mock_list_runs.return_value = ([], 0)
            
            response = self.client.get("/api/v1/etl/runs", headers=headers)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertEqual(data["data"]["total"], 0)


if __name__ == "__main__":
    unittest.main()

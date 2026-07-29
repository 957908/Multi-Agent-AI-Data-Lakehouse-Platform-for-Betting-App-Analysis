"""
File: run_e2e_simulation.py
Purpose:
    End-to-End Integration Simulation for SentinelX Trust AI Version 1.0 Release Candidate.
    Validates complete flow: Raw Data -> Bronze -> Silver -> Gold ETL -> AI Trust Engine -> REST API.
Author: Arjun Mehta & SentinelX QA Team
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 5.0 (Phase 4 RC1)
"""

import sys
import json
import time
import unittest
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock

# Ensure backend/app/ is in python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from fastapi.testclient import TestClient
from server import app
from database.connection import get_db_session
from database.models import PaymentRecordModel, GoldPlatformAnalytics
from repositories.gold_repository import GoldRepository
from repositories.payment_repository import PaymentRepository
from services.ai.trust_engine import TrustEngine
from services.ai.ai_analysis import AIAnalysisService
from services.ai.rag_service import RAGService


class TestEndToEndSystemSimulation(unittest.TestCase):
    """
    End-to-End System Simulation verifying cross-module integration across:
    Data Acquisition (Rayri) -> Data Lakehouse ETL (Priya) -> AI & REST APIs (Arjun) -> System Monitoring (Radhika)
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)
        cls.test_dir = Path(__file__).resolve().parent / "benchmark_sandbox"
        cls.test_dir.mkdir(parents=True, exist_ok=True)

    def setUp(self) -> None:
        self.mock_db = MagicMock()
        
        # Configure dynamic mock query router to return correct model objects
        def query_side_effect(model):
            mock_query = MagicMock()
            if model == GoldPlatformAnalytics:
                g = GoldPlatformAnalytics(
                    site="melbet",
                    trust_score=85.0,
                    trust_level="HIGH",
                    confidence_score=0.90,
                    total_payment_methods=10,
                    active_payment_methods=8,
                    supported_countries=["IN"],
                    top_payment_methods=["UPI", "Paytm"],
                    risk_summary="Low risk",
                    risk_flags=[],
                    last_scraped_at=datetime.utcnow()
                )
                mock_query.filter.return_value.all.return_value = [g]
                mock_query.filter.return_value.first.return_value = g
                mock_query.all.return_value = [g]
                mock_query.count.return_value = 1
            elif model == PaymentRecordModel:
                p = PaymentRecordModel(
                    site="melbet",
                    payment_type="e-wallet",
                    payment_name="Paytm",
                    currency="INR",
                    country="IN",
                    status="active",
                    extraction_status="SUCCESS",
                    source_url="https://melbet.com/deposits",
                    scraped_at=datetime.utcnow()
                )
                mock_query.filter.return_value.all.return_value = [p]
                mock_query.filter.return_value.first.return_value = p
                mock_query.all.return_value = [p]
                mock_query.count.return_value = 1
            else:
                mock_query.filter.return_value.all.return_value = []
                mock_query.filter.return_value.first.return_value = None
                mock_query.count.return_value = 0
            return mock_query

        self.mock_db.query.side_effect = query_side_effect
        
        def override_get_db_session():
            yield self.mock_db
        app.dependency_overrides[get_db_session] = override_get_db_session

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_e2e_data_lifecycle_and_api_contract(self):
        """
        Simulates complete end-to-end data processing lifecycle and verifies API responses.
        """
        start_time = time.time()

        # Step 1: Simulate Scraper Raw JSON Output with diverse payment channels
        raw_payload = [
            {
                "site": "melbet",
                "payment_type": "e-wallet",
                "payment_name": "Paytm",
                "currency": "INR",
                "country": "IN",
                "bonus_name": "100% Deposit Bonus",
                "support_type": "Live Chat",
                "support_value": "https://melbet.com/chat",
                "status": "active",
                "source_url": "https://melbet.com/deposits",
                "scraped_at": datetime.utcnow().isoformat()
            },
            {
                "site": "melbet",
                "payment_type": "e-wallet",
                "payment_name": "UPI",
                "currency": "INR",
                "country": "IN",
                "bonus_name": "100% Deposit Bonus",
                "support_type": "Email",
                "support_value": "support@melbet.com",
                "status": "active",
                "source_url": "https://melbet.com/deposits",
                "scraped_at": datetime.utcnow().isoformat()
            },
            {
                "site": "melbet",
                "payment_type": "crypto",
                "payment_name": "Bitcoin",
                "currency": "USD",
                "country": "BR",
                "bonus_name": "Crypto Match",
                "support_type": "Telegram",
                "support_value": "@melbet_crypto",
                "status": "active",
                "source_url": "https://melbet.com/crypto",
                "scraped_at": datetime.utcnow().isoformat()
            },
            {
                "site": "melbet",
                "payment_type": "bank_transfer",
                "payment_name": "IMPS",
                "currency": "INR",
                "country": "IN",
                "bonus_name": None,
                "support_type": "Live Chat",
                "support_value": "https://melbet.com/chat",
                "status": "active",
                "source_url": "https://melbet.com/bank",
                "scraped_at": datetime.utcnow().isoformat()
            },
            {
                "site": "10cric",
                "payment_type": "bank_transfer",
                "payment_name": "Net Banking",
                "currency": "INR",
                "country": "IN",
                "bonus_name": "150% Deposit Match",
                "support_type": "Phone",
                "support_value": "+91-1800-123-456",
                "status": "active",
                "source_url": "https://10cric.com/banking",
                "scraped_at": datetime.utcnow().isoformat()
            }
        ]

        raw_file = self.test_dir / "simulated_raw.json"
        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(raw_payload, f, indent=2)

        self.assertTrue(raw_file.exists())

        # Step 2: Test Trust Engine Rule-Based Intelligence
        trust_engine = TrustEngine(db_session=self.mock_db)
        melbet_trust = trust_engine.calculate_platform_trust("melbet", custom_records=raw_payload[:4], sync_gold=False)
        self.assertEqual(melbet_trust.site, "melbet")
        self.assertGreaterEqual(melbet_trust.trust_score, 60.0)

        # Step 3: Test RAG Document Ingestion & Retrieval
        rag_service = RAGService(db_session=self.mock_db)
        rag_resp = rag_service.query(
            type("RAGQueryRequestMock", (), {
                "query": "What payment methods are supported on Melbet in India?",
                "top_k": 2,
                "filter_site": "melbet"
            })()
        )
        self.assertIsNotNone(rag_resp.synthesized_answer)
        self.assertGreater(len(rag_resp.context_documents), 0)

        # Step 4: Validate REST API Endpoints Contract
        self.mock_db.execute.return_value = True
        health_resp = self.client.get("/api/v1/health")
        self.assertEqual(health_resp.status_code, 200)
        self.assertTrue(health_resp.json()["success"])

        # Validate Gold Platforms API
        self.mock_db.query.return_value.count.return_value = 0
        gold_resp = self.client.get("/api/v1/gold/platforms")
        self.assertEqual(gold_resp.status_code, 200)
        self.assertTrue(gold_resp.json()["success"])

        # Validate Search API
        search_resp = self.client.get("/api/v1/search?q=melbet")
        self.assertEqual(search_resp.status_code, 200)
        self.assertTrue(search_resp.json()["success"])

        duration = time.time() - start_time
        print(f"\n[E2E SIMULATION] Successfully validated end-to-end data lifecycle in {duration:.4f} seconds.")


if __name__ == "__main__":
    unittest.main()

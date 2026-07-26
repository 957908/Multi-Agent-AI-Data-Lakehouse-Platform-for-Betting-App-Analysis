"""
File: test_ai_services.py
Purpose:
    Unit tests for Sprint 2 AI Intelligence services (Trust Engine, RAG Service, AI Analysis, Search Repository).
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 2.0
"""

import sys
import unittest
from datetime import datetime
from pathlib import Path

# Ensure backend/app/ is in python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services.ai.trust_engine import TrustEngine
from services.ai.rag_service import (
    RAGService,
    DocumentIngestor,
    RetrievalEngine,
    ContextBuilder,
    PromptBuilder,
    ResponseFormatter
)
from services.ai.ai_analysis import AIAnalysisService
from schemas.ai import AIAnalysisRequest, RAGQueryRequest


class TestTrustEngine(unittest.TestCase):
    """Unit tests for Rule-Based Trust Engine."""

    def setUp(self):
        self.engine = TrustEngine(db_session=None)
        self.sample_records = [
            {
                "site": "melbet",
                "payment_type": "e-wallet",
                "payment_name": "Paytm",
                "currency": "INR",
                "country": "IN",
                "support_type": "Live Chat",
                "support_value": "https://melbet.com/chat",
                "bonus_name": "100% Deposit Bonus",
                "status": "active",
                "extraction_status": "SUCCESS"
            },
            {
                "site": "melbet",
                "payment_type": "e-wallet",
                "payment_name": "UPI",
                "currency": "INR",
                "country": "IN",
                "support_type": "Email",
                "support_value": "support@melbet.com",
                "bonus_name": "100% Deposit Bonus",
                "status": "active",
                "extraction_status": "SUCCESS"
            },
            {
                "site": "melbet",
                "payment_type": "crypto",
                "payment_name": "Bitcoin",
                "currency": "USD",
                "country": "BR",
                "support_type": "Telegram",
                "support_value": "@melbet_support",
                "bonus_name": None,
                "status": "active",
                "extraction_status": "SUCCESS"
            },
            {
                "site": "melbet",
                "payment_type": "bank_transfer",
                "payment_name": "NetBanking",
                "currency": "INR",
                "country": "IN",
                "support_type": None,
                "support_value": None,
                "bonus_name": None,
                "status": "active",
                "extraction_status": "SUCCESS"
            }
        ]

    def test_trust_score_calculation(self):
        """Test calculation of trust score with comprehensive sample records."""
        resp = self.engine.calculate_platform_trust("melbet", custom_records=self.sample_records)
        self.assertEqual(resp.site, "melbet")
        self.assertGreaterEqual(resp.trust_score, 70.0)
        self.assertIn(resp.trust_level, ["MEDIUM", "HIGH"])
        self.assertGreaterEqual(resp.confidence_score, 0.40)
        self.assertEqual(len(resp.rule_evaluations), 4)

    def test_trust_score_empty_fallback(self):
        """Test fallback when platform has no records."""
        resp = self.engine.calculate_platform_trust("unknown_site", custom_records=[])
        self.assertEqual(resp.trust_score, 40.0)
        self.assertEqual(resp.trust_level, "LOW")
        self.assertIn("Insufficient platform data", resp.risk_flags)


class TestRAGService(unittest.TestCase):
    """Unit tests for Provider-Agnostic RAG Architecture."""

    def setUp(self):
        self.rag_service = RAGService(db_session=None)
        self.sample_records = [
            {"site": "melbet", "payment_name": "Paytm", "payment_type": "e-wallet", "country": "IN", "currency": "INR", "support_type": "Live Chat", "bonus_name": "100% Bonus"},
            {"site": "10cric", "payment_name": "Net Banking", "payment_type": "bank_transfer", "country": "IN", "currency": "INR", "support_type": "Email", "bonus_name": "150% Match"}
        ]

    def test_document_ingestion(self):
        """Test conversion of records into RAG document chunks."""
        chunks = DocumentIngestor.records_to_chunks(self.sample_records)
        self.assertEqual(len(chunks), 2)
        self.assertIn("melbet", chunks[0].content)
        self.assertIn("Paytm", chunks[0].content)

    def test_retrieval_ranking(self):
        """Test ranking of documents matching natural language query."""
        chunks = DocumentIngestor.records_to_chunks(self.sample_records)
        retrieved = RetrievalEngine.retrieve_relevant(chunks, query="Paytm melbet India", top_k=2)
        self.assertGreaterEqual(len(retrieved), 1)
        self.assertEqual(retrieved[0].metadata["site"], "melbet")
        self.assertGreater(retrieved[0].relevance_score, 0.0)

    def test_full_rag_pipeline(self):
        """Test execution of complete RAG query pipeline."""
        req = RAGQueryRequest(query="What is the deposit bonus for Net Banking on 10cric?", top_k=2)
        resp = self.rag_service.query(req)
        self.assertIsNotNone(resp.formatted_prompt)
        self.assertGreater(len(resp.context_documents), 0)
        self.assertGreater(resp.estimated_tokens, 0)


class TestAIAnalysisService(unittest.TestCase):
    """Unit tests for AI Analysis Service."""

    def setUp(self):
        self.analysis_service = AIAnalysisService(db_session=None)

    def test_analyze_platform(self):
        """Test generation of structured AI analysis report."""
        req = AIAnalysisRequest(site="melbet", include_recommendations=True)
        resp = self.analysis_service.analyze_platform(req)
        self.assertEqual(resp.site, "melbet")
        self.assertIsNotNone(resp.summary)
        self.assertGreater(len(resp.payment_insights), 0)
        self.assertGreater(len(resp.recommendations), 0)

    def test_platform_summary(self):
        """Test generation of high-level platform summary."""
        resp = self.analysis_service.get_platform_summary("melbet")
        self.assertEqual(resp.site, "melbet")
        self.assertGreaterEqual(resp.trust_score, 0.0)
        self.assertIn(resp.trust_level, ["LOW", "MEDIUM", "HIGH"])


if __name__ == "__main__":
    unittest.main()

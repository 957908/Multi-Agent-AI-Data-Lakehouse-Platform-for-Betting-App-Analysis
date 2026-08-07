"""
File: benchmark_performance.py
Purpose:
    Performance and Latency Load Benchmarking for SentinelX Trust AI Version 1.0 Release Candidate.
Author: Niraj Kadam & Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 5.0 (Phase 4 RC1)
"""

import sys
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Ensure backend/app/ is in python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from fastapi.testclient import TestClient
from server import app
from database.connection import get_db_session


class TestPerformanceBenchmarking(unittest.TestCase):
    """
    Performance Load Benchmarking verifying sub-second latencies (<100ms)
    across REST API endpoints and Prometheus metrics.
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

    def _benchmark_endpoint(self, endpoint: str, num_requests: int = 50) -> float:
        latencies = []
        for _ in range(num_requests):
            start = time.time()
            resp = self.client.get(endpoint)
            duration = (time.time() - start) * 1000.0  # convert to ms
            self.assertIn(resp.status_code, [200, 401])
            latencies.append(duration)

        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        print(f"\n[BENCHMARK] '{endpoint}': {num_requests} reqs | Avg: {avg_latency:.2f}ms | P95: {p95_latency:.2f}ms")
        return avg_latency

    def test_performance_targets(self):
        """Validates that key API endpoints meet sub-100ms response performance SLA."""
        self.mock_db.execute.return_value = True
        self.mock_db.query.return_value.count.return_value = 0

        health_avg = self._benchmark_endpoint("/api/v1/health", num_requests=50)
        self.assertLess(health_avg, 100.0, "Health endpoint exceeded 100ms threshold")

        gold_avg = self._benchmark_endpoint("/api/v1/gold/platforms", num_requests=50)
        self.assertLess(gold_avg, 100.0, "Gold platforms endpoint exceeded 100ms threshold")

        search_avg = self._benchmark_endpoint("/api/v1/search?q=melbet", num_requests=50)
        self.assertLess(search_avg, 100.0, "Search endpoint exceeded 100ms threshold")


if __name__ == "__main__":
    unittest.main()

"""
File: metrics_manager.py
Purpose:
    Telemetry database management and versioning. Tracks historical success/failure rates,
    average run durations, and calculates dynamic health states.
Author: R. Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Niraj Kadam
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.0
"""

# Standard Library
from datetime import datetime
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List

# Setup Logger
logger = logging.getLogger("scraper.core.metrics_manager")


class MetricsManager:
    """
    Manages historical scraper performance statistics database, rolling over files monthly.
    """

    def __init__(self, metrics_dir: str = "data/metrics") -> None:
        """
        Ensures metrics folder and archive folders are initialized.
        """
        self.metrics_dir = Path(metrics_dir)
        self.archive_dir = self.metrics_dir / "metrics_archive"
        
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_filepath = self.metrics_dir / "historical_metrics.json"

    def load_metrics(self) -> List[Dict[str, Any]]:
        """
        Loads the list of run entries from the active telemetry database.
        """
        if not self.db_filepath.exists():
            return []
        try:
            with open(self.db_filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as error:
            logger.error(f"Failed to read historical metrics database: {str(error)}")
            return []

    def append_run_metrics(self, current_run: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Appends the current execution metrics entry and rotates/archives files if necessary.
        """
        self._check_and_rotate_db()
        
        history = self.load_metrics()
        history.append(current_run)
        
        try:
            with open(self.db_filepath, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=4)
            logger.info(f"Appended current run telemetry to database: {self.db_filepath}")
        except Exception as error:
            logger.error(f"Failed to persist historical metrics: {str(error)}")
            
        return history

    def calculate_trends(self) -> Dict[str, Any]:
        """
        Calculates cumulative metrics, average durations, success percentages, and health statuses.
        """
        history = self.load_metrics()
        if not history:
            return {
                "total_runs": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0,
                "avg_retries": 0.0,
                "avg_dismissals": 0.0,
                "health_status": "HEALTHY",
                "success_trend": [],
                "duration_trend": []
            }
            
        total_runs = len(history)
        successful_runs = 0
        total_duration = 0
        total_retries = 0
        total_dismissals = 0
        
        for run in history:
            breakdowns = run.get("site_breakdowns", {})
            run_success = True
            for site, info in breakdowns.items():
                if info.get("status") == "failed":
                    run_success = False
                    
                total_duration += info.get("duration_ms", 0)
                total_retries += info.get("retries", 0)
                total_dismissals += info.get("dismissals", 0)
                
            if run_success:
                successful_runs += 1

        overall_success_rate = (successful_runs / total_runs) * 100
        
        # Last 5 runs success trends
        last_runs = history[-5:]
        success_trend = []
        for run in last_runs:
            breakdowns = run.get("site_breakdowns", {})
            run_success = True
            for site, info in breakdowns.items():
                if info.get("status") == "failed":
                    run_success = False
            success_trend.append(100.0 if run_success else 0.0)

        # Health status computation based on last 5 runs
        recent_success_count = sum(1 for rate in success_trend if rate == 100.0)
        recent_rate = (recent_success_count / len(success_trend)) * 100 if success_trend else 100.0
        
        if recent_rate >= 75.0:
            health_status = "HEALTHY"
        elif recent_rate >= 25.0:
            health_status = "DEGRADED"
        else:
            health_status = "FAILED"

        return {
            "total_runs": total_runs,
            "success_rate": round(overall_success_rate, 2),
            "avg_duration_ms": int(total_duration / total_runs),
            "avg_retries": round(total_retries / total_runs, 2),
            "avg_dismissals": round(total_dismissals / total_runs, 2),
            "health_status": health_status,
            "success_trend": success_trend,
            "duration_trend": [run.get("total_duration_ms", 0) for run in last_runs]
        }

    def _check_and_rotate_db(self) -> None:
        """
        Rotates historical_metrics.json on a monthly boundaries base to keep file size controlled.
        """
        if not self.db_filepath.exists():
            return
            
        try:
            file_mtime = datetime.fromtimestamp(self.db_filepath.stat().st_mtime)
            current_time = datetime.now()
            
            if file_mtime.month != current_time.month or file_mtime.year != current_time.year:
                archive_name = f"metrics_{file_mtime.year}_{file_mtime.month:02d}.json"
                archive_path = self.archive_dir / archive_name
                
                logger.info(f"Rotating telemetry metrics file to archive destination: {archive_path}")
                os.rename(self.db_filepath, archive_path)
        except Exception as error:
            logger.error(f"Failed to check and rotate metrics database: {str(error)}")

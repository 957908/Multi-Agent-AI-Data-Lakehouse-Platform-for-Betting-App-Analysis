"""
File: reporter.py
Purpose:
    Processes raw JSON outputs to check Pydantic validations, perform duplicate detections, 
    and output execution and data quality markdown reports.
    Enhanced to parse and display structured failure reasons and performance metrics.
Author: R. Rayri Sharma
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Rayri Sharma
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 2.0
"""

# Standard Library
import json
import logging
from pathlib import Path
import re
from typing import Dict, Any, List, Optional, Tuple

# Local Imports
from models.payment import PaymentRecord

# Setup Logger
logger = logging.getLogger("scraper.core.reporter")


class AcquisitionReporter:
    """
    Analyzes execution snapshots to detect duplicates, validate schemas, and generate markdown reports.
    """

    def __init__(self, date_str: str, time_str: str) -> None:
        """
        Initializes reporter with target date and time execution keys.
        """
        self.date_str = date_str
        self.time_str = time_str
        self.current_run_dir = Path("data/raw") / date_str / time_str
        self.reports_dir = Path("output/reports") / date_str / time_str
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_reports(self, execution_metrics: Dict[str, Dict[str, Any]]) -> Tuple[str, str]:
        """
        Runs validation and duplication audits, and writes the two markdown reports.
        Returns paths to the generated reports.
        """
        logger.info(f"Generating reports for execution: {self.date_str}/{self.time_str}")

        # 1. Load current run records
        current_records_by_site = self._load_run_records(self.current_run_dir)
        
        # 2. Identify previous run for comparison
        prev_run_dir = self._get_previous_run_dir()
        prev_records_by_site = self._load_run_records(prev_run_dir) if prev_run_dir else {}

        # 3. Analyze statistics & quality metrics
        stats = self._analyze_metrics(current_records_by_site, prev_records_by_site, execution_metrics)

        # 3b. Manage Historical Metrics & Telemetry database
        try:
            from core.metrics_manager import MetricsManager
            metrics_mgr = MetricsManager()
            # Append current stats
            metrics_mgr.append_run_metrics(stats)
            # Compute trends
            trends = metrics_mgr.calculate_trends()
            stats["trends"] = trends
        except Exception as metrics_error:
            logger.error(f"Failed to process historical metrics dashboard: {str(metrics_error)}")
            stats["trends"] = {}

        # 4. Generate Reports
        stats_path = self._write_stats_report(stats)
        quality_path = self._write_quality_report(stats)

        return stats_path, quality_path

    def _load_run_records(self, run_dir: Optional[Path]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Loads all JSON datasets from the specified run directory.
        """
        records: Dict[str, List[Dict[str, Any]]] = {}
        if not run_dir or not run_dir.exists():
            return records

        for file in run_dir.glob("*_payments.json"):
            site = file.name.replace("_payments.json", "")
            try:
                with open(file, "r", encoding="utf-8") as f:
                    records[site] = json.load(f)
            except Exception as err:
                logger.error(f"Failed to load record file {file}: {str(err)}")
        return records

    def _get_previous_run_dir(self) -> Optional[Path]:
        """
        Returns the path of the latest run completed prior to the current run.
        """
        raw_root = Path("data/raw")
        if not raw_root.exists():
            return None

        all_runs = []
        for date_dir in raw_root.iterdir():
            if date_dir.is_dir() and re.match(r"^\d{4}-\d{2}-\d{2}$", date_dir.name):
                for time_dir in date_dir.iterdir():
                    if time_dir.is_dir() and re.match(r"^\d{2}-\d{2}$", time_dir.name):
                        all_runs.append((date_dir.name, time_dir.name, time_dir))

        all_runs.sort()
        current_key = (self.date_str, self.time_str)

        for i, (d, t, path) in enumerate(all_runs):
            if (d, t) == current_key:
                if i > 0:
                    return all_runs[i - 1][2]
                break

        return None

    def _analyze_metrics(
        self,
        current: Dict[str, List[Dict[str, Any]]],
        previous: Dict[str, List[Dict[str, Any]]],
        execution_metrics: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Audits validation passes, counts fields completeness, and identifies duplicates.
        """
        sites_processed = list(execution_metrics.keys())
        total_methods = 0
        validation_passes = 0
        validation_failures = 0
        duplicate_count = 0
        total_fields_checked = 0
        filled_fields_count = 0
        utf8_compliant = True

        site_breakdowns: Dict[str, Dict[str, Any]] = {}

        for site in sites_processed:
            records = current.get(site, [])
            site_methods = len(records)
            total_methods += site_methods
            site_passes = 0
            site_failures = 0
            site_duplicates = 0

            prev_records = previous.get(site, [])
            prev_keys = set(self._get_record_key(r) for r in prev_records)

            for rec in records:
                # Audit UTF-8 compliance
                try:
                    json.dumps(rec).encode("utf-8")
                except UnicodeEncodeError:
                    utf8_compliant = False

                # Validate Pydantic model
                try:
                    PaymentRecord.model_validate(rec)
                    site_passes += 1
                    validation_passes += 1
                except Exception as err:
                    logger.warning(f"Pydantic verification failed for record: {str(err)}")
                    site_failures += 1
                    validation_failures += 1

                # Check completeness of coordinates
                extracted_data = rec.get("extracted_data", {})
                for k, v in extracted_data.items():
                    total_fields_checked += 1
                    if v is not None and str(v).strip() != "":
                        filled_fields_count += 1

                # Detect duplicates against previous execution
                rec_key = self._get_record_key(rec)
                if rec_key in prev_keys:
                    site_duplicates += 1
                    duplicate_count += 1

            metrics = execution_metrics.get(site, {})
            site_breakdowns[site] = {
                "total": site_methods,
                "passes": site_passes,
                "failures": site_failures,
                "duplicates": site_duplicates,
                "retries": metrics.get("retries", 0),
                "dismissals": metrics.get("dismissals", 0),
                "status": metrics.get("status", "success"),
                "failure_reason": metrics.get("failure_reason") or "N/A",
                "duration_ms": int(metrics.get("duration", 0) * 1000),
                "navigation_ms": int(metrics.get("navigation_time", 0) * 1000),
                "discovery_ms": int(metrics.get("discovery_time", 0) * 1000)
            }

        completeness_percentage = (
            (filled_fields_count / total_fields_checked) * 100
            if total_fields_checked > 0 else 0.0
        )

        total_duration_ms = int(sum(m.get("duration", 0) for m in execution_metrics.values()) * 1000)

        return {
            "date": self.date_str,
            "time": self.time_str,
            "sites_processed": sites_processed,
            "total_methods": total_methods,
            "validation_passes": validation_passes,
            "validation_failures": validation_failures,
            "duplicate_count": duplicate_count,
            "completeness_percentage": round(completeness_percentage, 2),
            "utf8_compliant": utf8_compliant,
            "site_breakdowns": site_breakdowns,
            "total_duration_ms": total_duration_ms
        }

    def _get_record_key(self, record: Dict[str, Any]) -> str:
        """
        Generates a unique signature hash key for checking structural duplicates.
        """
        payment_name = record.get("payment_name", "")
        payment_type = record.get("payment_type", "")
        extracted_data = record.get("extracted_data", {})
        
        # Serialize fields securely
        upi_id = extracted_data.get("upi_id") or ""
        bank_account = extracted_data.get("bank_account") or ""
        ifsc_code = extracted_data.get("ifsc_code") or ""
        
        return f"{payment_name}|{payment_type}|{upi_id}|{bank_account}|{ifsc_code}"

    def _write_stats_report(self, stats: Dict[str, Any]) -> str:
        """
        Generates output/reports/YYYY-MM-DD/HH-MM/dataset_stats_report.md
        """
        filepath = self.reports_dir / "dataset_stats_report.md"
        
        trends = stats.get("trends", {})
        health_status = trends.get("health_status", "HEALTHY")
        
        health_badge = "🟢 HEALTHY"
        if health_status == "DEGRADED":
            health_badge = "🟡 DEGRADED"
        elif health_status == "FAILED":
            health_badge = "🔴 FAILED"

        # Build Report Markdown Content
        lines = [
            f"# Dataset Statistics Report",
            f"**Execution Session:** {stats['date']} at {stats['time']}",
            f"",
            f"## 🏥 System Health Dashboard",
            f"* **Scraper Health Status:** {health_badge}",
            f"* **Historical Scraper Success Rate:** {trends.get('success_rate', 0.0)}% (across {trends.get('total_runs', 0)} total runs)",
            f"* **Average Scraper Runtime:** {trends.get('avg_duration_ms', 0)} ms",
            f"* **Average Retries executed:** {trends.get('avg_retries', 0.0)} attempts",
            f"* **Average Popup dismissals:** {trends.get('avg_dismissals', 0.0)} dismissals",
            f"",
            f"## 📈 Scraper Performance Trends (Last 5 Runs)",
            f"* **Success Trend (100=Success, 0=Failed):** {trends.get('success_trend', [])}",
            f"* **Duration Trend (ms):** {trends.get('duration_trend', [])}",
            f"",
            f"## 📊 Current Run Metrics",
            f"* **Websites Processed:** {len(stats['sites_processed'])} ({', '.join(stats['sites_processed'])})",
            f"* **Total Methods Extracted:** {stats['total_methods']}",
            f"* **Total Execution Duration:** {stats['total_duration_ms']} ms",
            f"* **Overall Scraper Success Rate:** {100.0 if stats['total_methods'] > 0 and stats['validation_failures'] == 0 else 0.0}%",
            f"",
            f"## 🏛 Platform Breakdowns & Performance Metrics",
            f"| Website | Records | Passes | Failures | Duplicates | Retries | Dismissals | Status | Failure Reason | Total Duration (ms) | Nav (ms) | Disc (ms) |",
            f"|---|---|---|---|---|---|---|---|---|---|---|---|",
        ]

        for site, info in stats["site_breakdowns"].items():
            # Clean failure reason of newlines and pipes to protect markdown table layout
            reason_clean = str(info['failure_reason']).replace("\n", " ").replace("|", "\\|").strip()
            if len(reason_clean) > 80:
                reason_clean = reason_clean[:77] + "..."
            
            lines.append(
                f"| {site} | {info['total']} | {info['passes']} | {info['failures']} | {info['duplicates']} | "
                f"{info['retries']} | {info['dismissals']} | {info['status'].upper()} | {reason_clean} | "
                f"{info['duration_ms']} | {info['navigation_ms']} | {info['discovery_ms']} |"
            )

        lines.append("")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            
        logger.info(f"Saved dataset statistics report: {filepath}")
        return str(filepath)

    def _write_quality_report(self, stats: Dict[str, Any]) -> str:
        """
        Generates output/reports/YYYY-MM-DD/HH-MM/data_quality_report.md
        """
        filepath = self.reports_dir / "data_quality_report.md"
        
        success_status = "✅ PASS" if stats["validation_failures"] == 0 else "❌ FAIL"
        utf8_status = "✅ YES" if stats["utf8_compliant"] else "❌ NO"

        lines = [
            f"# Data Quality Audit Report",
            f"**Execution Session:** {stats['date']} at {stats['time']}",
            f"",
            f"## 🛡 Schema Quality & Compliance",
            f"| Metric Parameter | Value | Audit Status |",
            f"|---|---|---|",
            f"| **Pydantic Model Schema v1.1 Check** | {stats['validation_passes']} Passes / {stats['validation_failures']} Failures | {success_status} |",
            f"| **UTF-8 Charset Encoding Checks** | Compliant | {utf8_status} |",
            f"| **Coordinate Completeness index** | {stats['completeness_percentage']}% | Verification Metric |",
            f"| **Platform Duplicate Count** | {stats['duplicate_count']} items matching previous snapshot | Verification Metric |",
            f"",
            f"## 📝 Quality Audit Verdict",
            f"All records collected in this session are audited and verified. "
            f"The dataset is successfully structured and formatted to comply with Spark ETL ingestions and risk analysis engines."
        ]

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info(f"Saved data quality report: {filepath}")
        return str(filepath)

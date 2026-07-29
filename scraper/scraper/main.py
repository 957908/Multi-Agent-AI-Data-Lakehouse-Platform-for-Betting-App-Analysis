"""
File: main.py
Purpose:
    Integrated orchestration entrypoint for the SentinelX Trust AI scraper pipeline.
    Captures structured failure reasons and performance metrics ( rtry, dismissals, duration checks).
Author: R. Rayri Sharma
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Rayri Sharma
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 2.0
"""

# Standard Library
import argparse
from datetime import datetime
import importlib
import logging
import os
from pathlib import Path
import shutil
import sys
import time
from typing import Dict, Any

# Local Imports
from config import settings
from core.browser import BrowserManager
from adapters.factory import AdapterFactory
from core.utils import setup_logging
from core.reporter import AcquisitionReporter

# Setup module logger
logger = logging.getLogger("scraper.main")


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser(description="SentinelX Trust AI Data Acquisition Runner")
    parser.add_argument(
        "--site",
        type=str,
        default=os.getenv("TARGET_SITE", "onexbet"),
        help="Target site identifier to scrape (e.g. onexbet, melbet, 10cric, 22xbet, all)"
    )
    return parser.parse_args()


def reorganize_evidence(site_name: str, date_str: str, time_str: str) -> None:
    """
    Moves generated JSON outputs, screenshots, and HTML files to the raw historical directories.
    Helps isolate and preserve snapshots cleanly without redesigning frozen modules.
    """
    # Target Locations
    raw_dir = Path("data/raw") / date_str / time_str
    html_target_dir = Path("output/html") / date_str / time_str / site_name
    screenshot_target_dir = Path("output/screenshots") / date_str / time_str / site_name

    raw_dir.mkdir(parents=True, exist_ok=True)
    html_target_dir.mkdir(parents=True, exist_ok=True)
    screenshot_target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Move JSON Output
    json_source = Path("output") / f"{site_name}_payments.json"
    if json_source.exists():
        json_target = raw_dir / f"{site_name}_payments.json"
        shutil.copy(str(json_source), str(json_target))
        json_source.unlink()
        logger.info(f"Moved JSON dataset to raw Data Lake: {json_target}")

    # 2. Move HTML Snapshots
    html_dir = Path("output/html")
    for html_file in html_dir.glob(f"{site_name}_*.html"):
        clean_name = html_file.name.replace(f"{site_name}_", "")
        shutil.move(str(html_file), str(html_target_dir / clean_name))

    # 3. Move Screenshots
    screenshot_dir = Path("output/screenshots")
    for screenshot_file in screenshot_dir.glob(f"{site_name}_*.png"):
        clean_name = screenshot_file.name.replace(f"{site_name}_", "")
        shutil.move(str(screenshot_file), str(screenshot_target_dir / clean_name))


def scrape_site(site_name: str, date_str: str, time_str: str) -> Dict[str, Any]:
    """
    Executes the acquisition pipeline for a target website, capturing detailed execution statistics.
    """
    start_time = time.time()
    logger.info(f"--- Starting scraping run for site: {site_name} ---")

    metrics = {
        "duration": 0.0,
        "navigation_time": 0.0,
        "discovery_time": 0.0,
        "retries": 0,
        "dismissals": 0,
        "status": "success",
        "failure_reason": None
    }

    # Resolve target URL from settings
    url_env_map = {
        "onexbet": settings.ONEXBET_URL,
        "1xbet": settings.ONEXBET_URL,
        "melbet": settings.MELBET_URL,
        "10cric": settings.TENCRIC_URL,
        "tencric": settings.TENCRIC_URL,
        "22xbet": settings.PLAY22_URL,
        "twentytwobet": settings.PLAY22_URL,
    }

    target_url = url_env_map.get(site_name)
    if not target_url:
        metrics["status"] = "failed"
        metrics["failure_reason"] = "URL Configuration Missing"
        return metrics

    # Resolve selectors module dynamically
    try:
        module_name_map = {
            "onexbet": "onexbet",
            "1xbet": "onexbet",
            "melbet": "melbet",
            "10cric": "tencric",
            "tencric": "tencric",
            "22xbet": "twentytwoxbet",
            "twentytwobet": "twentytwoxbet"
        }
        module_name = module_name_map.get(site_name, site_name)
        selector_module_path = f"config.selectors.{module_name}"
        selectors_module = importlib.import_module(selector_module_path)
        selectors = getattr(selectors_module, "SELECTORS")
    except Exception as error:
        metrics["status"] = "failed"
        metrics["failure_reason"] = f"Selector Load Error: {str(error)}"
        return metrics

    # Start browser manager and run adapter cycle
    browser_mgr = BrowserManager()
    page = None

    try:
        browser_mgr.start_browser()
        
        # Session state load check
        from core.session import SessionManager
        session_mgr = SessionManager()
        state_path = session_mgr.get_state_path(site_name)
        has_state = session_mgr.has_session(site_name)
        
        if has_state:
            context = browser_mgr.create_context(storage_state_path=state_path)
        else:
            context = browser_mgr.create_context()
            
        page = context.new_page()

        # Resolve Adapter from Factory
        adapter = AdapterFactory.get_adapter(site_name, page, context, target_url, selectors)

        # 1. Navigation Flow execution
        nav_start = time.time()
        try:
            adapter.open_homepage()
            adapter.capture_evidence("homepage")
            
            adapter.login_if_required()
            
            adapter.navigate_to_deposit()
            adapter.capture_evidence("deposit_page")
            metrics["navigation_time"] = time.time() - nav_start
        except Exception as nav_err:
            metrics["navigation_time"] = time.time() - nav_start
            metrics["status"] = "failed"
            err_msg = str(nav_err).lower()
            if "timeout" in err_msg:
                metrics["failure_reason"] = "Navigation Timeout"
            elif "login" in err_msg or "auth" in err_msg:
                metrics["failure_reason"] = "Login Failed"
            else:
                metrics["failure_reason"] = f"Navigation Failed: {str(nav_err)}"
            raise

        # 2. Discovery Flow execution
        disc_start = time.time()
        try:
            records = adapter.discover_payment_methods()
            adapter.extract_payment_details()
            
            # Extract retries and dismissals metrics from discovery instance
            if hasattr(adapter, "discovery") and adapter.discovery:
                metrics["retries"] = adapter.discovery.retries_executed_count
                metrics["dismissals"] = adapter.discovery.popup_dismissals_count
                
            metrics["discovery_time"] = time.time() - disc_start
        except Exception as disc_err:
            metrics["discovery_time"] = time.time() - disc_start
            metrics["status"] = "failed"
            err_msg = str(disc_err).lower()
            if "timeout" in err_msg:
                metrics["failure_reason"] = "Payment Page Not Found"
            elif "selector" in err_msg:
                metrics["failure_reason"] = "Selector Not Found"
            else:
                metrics["failure_reason"] = f"Extraction Failed: {str(disc_err)}"
            raise

        # Validate and export if methods found
        if records:
            validation_passed = adapter.validate_data()
            if validation_passed:
                export_path = adapter.export_json(f"{site_name}_payments")
                logger.info(f"Adapter JSON export completed at: {export_path}")
            else:
                metrics["status"] = "failed"
                metrics["failure_reason"] = "Pydantic Validation Failed"
                logger.error("Extracted records failed model validation check. Skipping export.")
        else:
            logger.warning("No payment methods were extracted during this run.")

    except Exception as error:
        logger.critical(f"Acquisition pipeline crashed during run on '{site_name}': {str(error)}")
        # Guarantee diagnostics snapshots capture on failure
        if page:
            from core.utils import save_html
            from core.screenshot import take_screenshot
            try:
                save_html(page, f"crash_{site_name}")
            except Exception:
                pass
            try:
                take_screenshot(page, f"crash_{site_name}")
            except Exception:
                pass
        
        metrics["status"] = "failed"
        if not metrics["failure_reason"]:
            metrics["failure_reason"] = f"Runtime Crash: {str(error)}"
        raise

    finally:
        browser_mgr.close_browser()

    # Reorganize evidence files to timestamped folders
    reorganize_evidence(site_name, date_str, time_str)
    
    metrics["duration"] = time.time() - start_time
    logger.info(f"--- Completed scraping run for site '{site_name}' in {metrics['duration']:.2f} seconds. ---")
    return metrics


def run_pipeline() -> None:
    """
    Executes the complete acquisition lifecycle using the Site Adapter Factory.
    """
    # 1. Setup Logging
    setup_logging()
    logger.info("Starting SentinelX Trust AI Data Acquisition Pipeline...")

    # 2. Parse CLI Arguments
    args = parse_arguments()
    site_arg = args.site.lower().strip()

    # Generate single timestamp execution keys for this run
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H-%M")

    # Resolve target sites to run
    if site_arg == "all":
        sites = ["onexbet", "melbet", "10cric", "22xbet"]
    else:
        # Check alias compatibility
        if site_arg == "1xbet":
            sites = ["onexbet"]
        elif site_arg == "tencric":
            sites = ["10cric"]
        elif site_arg == "twentytwobet":
            sites = ["22xbet"]
        else:
            sites = [site_arg]

    execution_metrics: Dict[str, Dict[str, Any]] = {}

    for site in sites:
        start_time = time.time()
        try:
            metrics = scrape_site(site, date_str, time_str)
            execution_metrics[site] = metrics
        except Exception as run_error:
            logger.error(f"Gracefully skipped site '{site}' due to fatal execution failure: {str(run_error)}")
            # Populate fallback metrics for this site
            duration = time.time() - start_time
            execution_metrics[site] = {
                "duration": duration,
                "navigation_time": 0.0,
                "discovery_time": 0.0,
                "retries": 0,
                "dismissals": 0,
                "status": "failed",
                "failure_reason": f"Execution Error: {str(run_error)}"
            }

    # 3. Post-run analytics reporting
    try:
        reporter = AcquisitionReporter(date_str, time_str)
        stats_path, quality_path = reporter.generate_reports(execution_metrics)
        logger.info(f"Reports successfully generated:\nStats: {stats_path}\nQuality: {quality_path}")
    except Exception as report_error:
        logger.error(f"Failed to generate reports post-execution: {str(report_error)}")

    logger.info("Pipeline execution sequence finished.")


if __name__ == "__main__":
    run_pipeline()
"""
File: scheduler.py
Purpose:
    Recurring cron-like scheduler for running the multi-site payment scraper automatically.
Author: R. Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Niraj Kadam
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.0
"""

# Standard Library
import argparse
import logging
import os
import subprocess
import sys
import time

# Local Imports
from core.utils import setup_logging

# Setup Logger
logger = logging.getLogger("scraper.scheduler")


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line scheduler configurations.
    """
    parser = argparse.ArgumentParser(description="SentinelX Trust AI Scraper Loop Scheduler")
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Recurring schedule interval in seconds (default: 3600 seconds / 1 hour)"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=0,
        help="Number of times the cycle should execute before exiting. 0 runs indefinitely."
    )
    return parser.parse_args()


def run_scheduler() -> None:
    """
    Starts the schedule loop, launching the main scraper process in a clean subprocess.
    """
    setup_logging()
    args = parse_arguments()
    
    interval = args.interval
    max_iterations = args.iterations
    
    logger.info("==================================================")
    logger.info("   SentinelX Trust AI Scraper Loop Scheduler      ")
    logger.info(f"   Interval: {interval}s | Iterations: {max_iterations if max_iterations > 0 else 'Indefinite'}")
    logger.info("==================================================")
    
    iteration_count = 0
    main_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")

    while True:
        iteration_count += 1
        logger.info(f"Starting scheduled scraping cycle #{iteration_count}...")
        
        try:
            # Execute main pipeline as a clean subprocess to prevent browser leakage/crashes
            # Pass all sites to run
            cmd = [sys.executable, main_script, "--site", "all"]
            result = subprocess.run(cmd, capture_output=False, check=True)
            logger.info(f"Scheduled scraping cycle #{iteration_count} completed successfully with exit code: {result.returncode}")
        except subprocess.CalledProcessError as sub_err:
            logger.error(f"Scheduled scraping cycle #{iteration_count} failed in execution: {str(sub_err)}")
        except Exception as err:
            logger.error(f"Unexpected error during iteration #{iteration_count}: {str(err)}")

        # Check iteration termination
        if max_iterations > 0 and iteration_count >= max_iterations:
            logger.info("Reached target iteration execution limit. Stopping scheduler.")
            break
            
        logger.info(f"Sleeping for {interval} seconds until next scheduled run...")
        time.sleep(interval)


if __name__ == "__main__":
    run_scheduler()

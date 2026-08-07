"""
File: retry_utils.py
Purpose:
    Centralized retry logic wrapper for resilient scraper operations.
Author: R. Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Niraj Kadam
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.0
"""

# Standard Library
import logging
import time
from typing import Callable, TypeVar, Any, Tuple

# Setup Logger
logger = logging.getLogger("scraper.core.retry_utils")

T = TypeVar("T")


def retry_operation(
    func: Callable[[], T],
    retries: int = 3,
    delay: float = 1.0,
    exceptions: Tuple[type, ...] = (Exception,),
    action_name: str = "Operation"
) -> T:
    """
    Executes a callable block, retrying up to `retries` times if catching `exceptions`.
    """
    for attempt in range(1, retries + 1):
        try:
            return func()
        except exceptions as err:
            logger.warning(
                f"[{action_name}] Attempt {attempt}/{retries} failed with error: {str(err)}. "
                f"Retrying in {delay}s..."
            )
            if attempt == retries:
                logger.error(f"[{action_name}] All {retries} retry attempts failed.")
                raise
            time.sleep(delay)
            # Increase delay slightly for backoff
            delay *= 1.5
            
    # Fallback to satisfy static analyzer checks
    raise RuntimeError(f"[{action_name}] Execution reached unexpected end state.")

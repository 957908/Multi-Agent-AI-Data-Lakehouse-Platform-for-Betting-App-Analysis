"""
File: response.py
Purpose:
    Defines the standard uniform API response wrapper envelope.
Author: Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    Standard envelope format returned by all API endpoints.
    """
    success: bool
    message: str
    data: Optional[T] = None

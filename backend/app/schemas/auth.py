"""
File: auth.py
Purpose:
    Pydantic schemas for authentication and authorization requests and responses.
Author: Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

from typing import List
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Payload to request a login token."""
    email: str = Field(..., description="User's login email address")
    password: str = Field(..., description="User's raw login password")


class TokenResponse(BaseModel):
    """Response returned upon successful authentication containing JWT access token."""
    access_token: str = Field(..., description="JWT token to authorize requests")
    token_type: str = Field(default="bearer", description="Token scheme used")
    expires_in: int = Field(..., description="Lifetime of token in seconds")


class UserResponse(BaseModel):
    """User profile details retrieved from auth session."""
    email: str = Field(..., description="Authorized email address")
    roles: List[str] = Field(..., description="Assigned authorization roles")

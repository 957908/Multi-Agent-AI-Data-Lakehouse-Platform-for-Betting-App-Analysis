"""
File: auth.py
Purpose:
    Exposes endpoints for user authentication, session creation, and profile retrieval.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

from datetime import timedelta
import logging
from fastapi import APIRouter, Depends
from config.settings import settings
from core.security import USER_REGISTRY, verify_password, create_access_token, get_current_user
from core.exceptions import AuthException
from schemas.auth import LoginRequest, TokenResponse, UserResponse
from schemas.response import APIResponse

logger = logging.getLogger("backend.api.auth")
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=APIResponse[TokenResponse])
def login(payload: LoginRequest) -> APIResponse[TokenResponse]:
    """
    Authenticates user credentials and issues a signed JWT token.
    """
    email = payload.email
    password = payload.password

    user = USER_REGISTRY.get(email)
    if not user or not verify_password(password, user["hashed_password"]):
        logger.warning(f"Failed login attempt for email: {email}")
        raise AuthException("Incorrect email or password")

    logger.info(f"User authenticated successfully: {email}")
    
    expires_in_secs = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    access_token = create_access_token(
        data={"sub": email, "roles": user["roles"]},
        expires_delta=timedelta(seconds=expires_in_secs)
    )

    token_data = TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in_secs
    )

    return APIResponse(
        success=True,
        message="Authentication successful",
        data=token_data
    )


@router.get("/me", response_model=APIResponse[UserResponse])
def get_me(current_user: dict = Depends(get_current_user)) -> APIResponse[UserResponse]:
    """
    Retrieves current authenticated user's email and role settings.
    """
    user_data = UserResponse(
        email=current_user["email"],
        roles=current_user["roles"]
    )
    return APIResponse(
        success=True,
        message="User profile retrieved",
        data=user_data
    )

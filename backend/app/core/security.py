"""
File: security.py
Purpose:
    Handles JWT authentication, password hashing, and Role-Based Access Control (RBAC).
Author: Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any, Optional
import jwt
import bcrypt
from fastapi import Depends, Header, status
from fastapi.security import OAuth2PasswordBearer
from config.settings import settings
from core.exceptions import AuthException, PermissionDeniedException

logger = logging.getLogger("backend.core.security")

# Reusable OAuth2 password scheme for extracting headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    """
    Hashes a raw password using bcrypt.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against its hashed value.
    """
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as e:
        logger.error(f"Password verification failure: {str(e)}")
        return False


# In-Memory static user database configured from settings
# We pre-hash the passwords for safety
USER_REGISTRY: Dict[str, Dict[str, Any]] = {
    settings.ADMIN_EMAIL: {
        "email": settings.ADMIN_EMAIL,
        "hashed_password": hash_password(settings.ADMIN_PASSWORD),
        "roles": ["admin"]
    },
    settings.ANALYST_EMAIL: {
        "email": settings.ANALYST_EMAIL,
        "hashed_password": hash_password(settings.ANALYST_PASSWORD),
        "roles": ["analyst"]
    },
    settings.READER_EMAIL: {
        "email": settings.READER_EMAIL,
        "hashed_password": hash_password(settings.READER_PASSWORD),
        "roles": ["reader"]
    }
}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a secure signed JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to generate JWT: {str(e)}", exc_info=True)
        raise AuthException("Could not create access token")


def decode_access_token(token: str) -> dict:
    """
    Decodes and validates a JWT token.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT validation failed: Token expired")
        raise AuthException("Token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"JWT validation failed: Invalid token - {str(e)}")
        raise AuthException("Invalid authentication token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Dependency that extracts and validates JWT token, returning the current user dict.
    """
    if not token:
        raise AuthException("Authentication credentials were not provided")
    
    payload = decode_access_token(token)
    email: Optional[str] = payload.get("sub")
    if not email:
        raise AuthException("Invalid authentication payload")
    
    user = USER_REGISTRY.get(email)
    if not user:
        raise AuthException("User no longer exists in system")
    
    return {
        "email": user["email"],
        "roles": user["roles"]
    }


class RoleChecker:
    """
    Dependency check verifying if the authenticated user has any of the allowed roles.
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_roles = current_user.get("roles", [])
        # Check if user has at least one of the allowed roles
        has_permission = any(role in self.allowed_roles for role in user_roles)
        if not has_permission:
            logger.warning(f"Unauthorized access attempt by {current_user.get('email')} requiring {self.allowed_roles}")
            raise PermissionDeniedException(f"Permission denied. Required roles: {self.allowed_roles}")
        return current_user

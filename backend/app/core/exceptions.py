"""
File: exceptions.py
Purpose:
    Defines application-wide exception handling schemas and base classes.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from schemas.response import APIResponse


class BaseAppException(Exception):
    """Base class for all custom application errors."""
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthException(BaseAppException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Invalid credentials or missing token"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class PermissionDeniedException(BaseAppException):
    """Raised when role permission validation fails."""
    def __init__(self, message: str = "Access denied: insufficient permissions"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundException(BaseAppException):
    """Raised when requested database record is missing."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class ValidationException(BaseAppException):
    """Raised when parameters or payload fail check rules."""
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """
    Translates internal application errors to uniform APIResponse structure.
    """
    response_payload = APIResponse(
        success=False,
        message=exc.message,
        data=None
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=response_payload.model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all exception handler to avoid leaking traceback to production consumers.
    """
    # Safe error representation
    response_payload = APIResponse(
        success=False,
        message="An unexpected system error occurred.",
        data=None
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_payload.model_dump()
    )

"""
File: exceptions.py
Purpose:
    Defines application-wide exception handling schemas and centralized global exception handlers.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 5.0
"""

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from schemas.response import APIResponse

logger = logging.getLogger("backend.core.exceptions")


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
    """Translates custom application errors into the uniform APIResponse envelope."""
    payload = APIResponse(success=False, message=exc.message, data=None)
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Translates standard HTTP exceptions into the uniform APIResponse envelope."""
    payload = APIResponse(success=False, message=str(exc.detail), data=None)
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Translates FastAPI request validation errors into the uniform APIResponse envelope."""
    error_msg = f"Request validation failed: {exc.errors()[0]['msg']}" if exc.errors() else "Validation error"
    payload = APIResponse(success=False, message=error_msg, data=None)
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=payload.model_dump())


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Translates database errors safely into the uniform APIResponse envelope."""
    logger.error(f"Database Exception on path {request.url.path}: {exc}")
    payload = APIResponse(success=False, message="A database operation error occurred.", data=None)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payload.model_dump())


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler translating unexpected exceptions into the uniform APIResponse envelope."""
    logger.error(f"Unhandled Exception on path {request.url.path}: {exc}", exc_info=True)
    payload = APIResponse(success=False, message="An unexpected system error occurred.", data=None)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payload.model_dump())

"""
Internationalization middleware for Park Tycoon Game.

This middleware handles request-level language detection and provides
translation context for API responses.
"""

import logging
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.i18n_service import get_i18n_service

logger = logging.getLogger(__name__)


class I18nMiddleware(BaseHTTPMiddleware):
    """Middleware for handling internationalization in requests."""
    
    def __init__(self, app, default_language: str = "zh"):
        """
        Initialize the I18n middleware.
        
        Args:
            app: FastAPI application instance
            default_language: Default language code to use
        """
        super().__init__(app)
        self.default_language = default_language
        self.i18n_service = get_i18n_service()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and detect language preference.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response
        """
        # Detect language from various sources
        detected_language = self._detect_request_language(request)
        
        # Store language in request state for use in handlers
        request.state.language = detected_language
        request.state.i18n_service = self.i18n_service
        
        logger.debug(f"Request language detected: {detected_language}")
        
        # Process request
        response = await call_next(request)
        
        # Add language header to response
        response.headers["Content-Language"] = detected_language
        
        return response
    
    def _detect_request_language(self, request: Request) -> str:
        """
        Detect language preference from request.
        
        Priority order:
        1. Query parameter 'lang'
        2. Header 'X-Language'
        3. Accept-Language header
        4. Default language
        
        Args:
            request: HTTP request
            
        Returns:
            Detected language code
        """
        # 1. Check query parameter
        lang_param = request.query_params.get("lang")
        if lang_param and self.i18n_service.is_language_supported(lang_param):
            return lang_param
        
        # 2. Check custom header
        lang_header = request.headers.get("X-Language")
        if lang_header and self.i18n_service.is_language_supported(lang_header):
            return lang_header
        
        # 3. Check Accept-Language header
        accept_language = request.headers.get("Accept-Language")
        if accept_language:
            detected = self.i18n_service.detect_language_from_header(accept_language)
            if detected != self.default_language:  # Only use if actually detected
                return detected
        
        # 4. Fall back to default
        return self.default_language


def get_request_language(request: Request) -> str:
    """
    Get the detected language for the current request.
    
    Args:
        request: HTTP request
        
    Returns:
        Language code for the request
    """
    return getattr(request.state, 'language', 'zh')


def get_request_i18n_service(request: Request):
    """
    Get the I18n service instance for the current request.
    
    Args:
        request: HTTP request
        
    Returns:
        I18nService instance
    """
    return getattr(request.state, 'i18n_service', get_i18n_service())
"""
Internationalization API endpoints for Park Tycoon Game.

This module provides endpoints for language selection and translation management.
"""

import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel

from app.services.i18n_service import get_i18n_service
from app.core.i18n_helpers import (
    get_translation_helper, 
    create_success_response, 
    create_error_response
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/i18n", tags=["internationalization"])


class LanguageInfo(BaseModel):
    """Language information model."""
    code: str
    name: str
    native_name: str


class TranslationResponse(BaseModel):
    """Translation response model."""
    key: str
    value: str
    language: str
    category: str


class LanguageSelectionRequest(BaseModel):
    """Language selection request model."""
    language_code: str


# Language information mapping
LANGUAGE_INFO = {
    "en": LanguageInfo(code="en", name="English", native_name="English"),
    "zh": LanguageInfo(code="zh", name="Chinese", native_name="中文"),
    "es": LanguageInfo(code="es", name="Spanish", native_name="Español"),
    "fr": LanguageInfo(code="fr", name="French", native_name="Français")
}


@router.get("/languages", response_model=Dict)
async def get_available_languages(request: Request):
    """
    Get list of available languages.
    
    Returns:
        List of supported languages with their information
    """
    try:
        i18n_service = get_i18n_service()
        available_languages = i18n_service.get_available_languages()
        
        languages_info = [
            LANGUAGE_INFO[lang].dict() for lang in available_languages 
            if lang in LANGUAGE_INFO
        ]
        
        return create_success_response(
            request,
            data={
                "languages": languages_info,
                "default_language": i18n_service.DEFAULT_LANGUAGE
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting available languages: {e}")
        return create_error_response(
            request,
            "internal_error",
            status_code=500,
            details={"message": "Failed to retrieve available languages"}
        )


@router.get("/translations", response_model=Dict)
async def get_translations(
    request: Request,
    category: Optional[str] = Query(None, description="Translation category to filter by"),
    keys: Optional[str] = Query(None, description="Comma-separated list of specific keys to retrieve")
):
    """
    Get translations for the current request language.
    
    Args:
        category: Optional category filter (ui, module, error, etc.)
        keys: Optional comma-separated list of specific keys
        
    Returns:
        Dictionary of translations
    """
    try:
        helper = get_translation_helper(request)
        i18n_service = helper.i18n_service
        language = helper.language
        
        if keys:
            # Get specific keys
            key_list = [key.strip() for key in keys.split(",")]
            translations = {}
            for key in key_list:
                translations[key] = helper.translate(key)
        elif category:
            # Get translations by category
            translations = i18n_service.get_translations_by_category(category, language)
        else:
            # Get common UI translations by default
            translations = i18n_service.get_translations_by_category("ui", language)
        
        return create_success_response(
            request,
            data={
                "translations": translations,
                "category": category,
                "language": language,
                "total_count": len(translations)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting translations: {e}")
        return create_error_response(
            request,
            "internal_error",
            status_code=500,
            details={"message": "Failed to retrieve translations"}
        )


@router.get("/translations/{key}", response_model=Dict)
async def get_translation(request: Request, key: str):
    """
    Get a specific translation by key.
    
    Args:
        key: Translation key to retrieve
        
    Returns:
        Translation information
    """
    try:
        helper = get_translation_helper(request)
        translation = helper.translate(key)
        
        return create_success_response(
            request,
            data={
                "key": key,
                "value": translation,
                "language": helper.language,
                "found": translation != key  # True if translation was found
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting translation for key '{key}': {e}")
        return create_error_response(
            request,
            "internal_error",
            status_code=500,
            details={"message": f"Failed to retrieve translation for key '{key}'"}
        )


@router.post("/language/select", response_model=Dict)
async def select_language(request: Request, language_request: LanguageSelectionRequest):
    """
    Validate and confirm language selection.
    
    Note: This endpoint validates the language choice but doesn't store it server-side.
    Language selection is handled via headers, query parameters, or client-side storage.
    
    Args:
        language_request: Language selection request
        
    Returns:
        Confirmation of language selection with sample translations
    """
    try:
        i18n_service = get_i18n_service()
        requested_language = language_request.language_code
        
        # Validate language
        if not i18n_service.is_language_supported(requested_language):
            return create_error_response(
                request,
                "unsupported_language",
                status_code=400,
                details={
                    "requested_language": requested_language,
                    "supported_languages": i18n_service.get_available_languages()
                }
            )
        
        # Get sample translations in the selected language
        sample_translations = i18n_service.get_translations_by_category("ui", requested_language)
        
        return create_success_response(
            request,
            data={
                "selected_language": requested_language,
                "language_info": LANGUAGE_INFO.get(requested_language, {}).dict() if requested_language in LANGUAGE_INFO else {},
                "sample_translations": dict(list(sample_translations.items())[:5]),  # First 5 translations
                "instructions": {
                    "header": f"Set 'X-Language: {requested_language}' header for future requests",
                    "query_param": f"Add '?lang={requested_language}' to request URLs",
                    "accept_language": f"Set 'Accept-Language: {requested_language}' header"
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error selecting language: {e}")
        return create_error_response(
            request,
            "internal_error",
            status_code=500,
            details={"message": "Failed to process language selection"}
        )


@router.get("/language/current", response_model=Dict)
async def get_current_language(request: Request):
    """
    Get the current detected language for the request.
    
    Returns:
        Current language information and detection details
    """
    try:
        helper = get_translation_helper(request)
        current_language = helper.language
        
        # Determine how language was detected
        detection_method = "default"
        if request.query_params.get("lang"):
            detection_method = "query_parameter"
        elif request.headers.get("X-Language"):
            detection_method = "custom_header"
        elif request.headers.get("Accept-Language"):
            detection_method = "accept_language_header"
        
        return create_success_response(
            request,
            data={
                "current_language": current_language,
                "language_info": LANGUAGE_INFO.get(current_language, {}).dict() if current_language in LANGUAGE_INFO else {},
                "detection_method": detection_method,
                "available_languages": get_i18n_service().get_available_languages()
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting current language: {e}")
        return create_error_response(
            request,
            "internal_error",
            status_code=500,
            details={"message": "Failed to get current language information"}
        )


@router.get("/cache/stats", response_model=Dict)
async def get_cache_stats(request: Request):
    """
    Get translation cache statistics.
    
    Returns:
        Cache statistics and performance information
    """
    try:
        i18n_service = get_i18n_service()
        cache_stats = i18n_service.get_cache_stats()
        
        return create_success_response(
            request,
            data={
                "cache_stats": cache_stats,
                "supported_languages": i18n_service.get_available_languages()
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return create_error_response(
            request,
            "internal_error",
            status_code=500,
            details={"message": "Failed to retrieve cache statistics"}
        )


@router.post("/cache/clear", response_model=Dict)
async def clear_translation_cache(
    request: Request,
    language: Optional[str] = Query(None, description="Specific language to clear (clears all if not specified)")
):
    """
    Clear translation cache.
    
    Args:
        language: Optional specific language to clear
        
    Returns:
        Confirmation of cache clearing
    """
    try:
        i18n_service = get_i18n_service()
        
        if language:
            if not i18n_service.is_language_supported(language):
                return create_error_response(
                    request,
                    "unsupported_language",
                    status_code=400,
                    details={"requested_language": language}
                )
            i18n_service.clear_cache(language)
            message = f"Cache cleared for language: {language}"
        else:
            i18n_service.clear_cache()
            message = "All translation cache cleared"
        
        return create_success_response(
            request,
            data={
                "message": message,
                "cleared_language": language,
                "cache_stats": i18n_service.get_cache_stats()
            }
        )
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return create_error_response(
            request,
            "internal_error",
            status_code=500,
            details={"message": "Failed to clear translation cache"}
        )
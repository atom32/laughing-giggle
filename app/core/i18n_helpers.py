"""
Translation helpers for API responses in Park Tycoon Game.

These helpers provide convenient functions for translating content
in API responses and handling localized data.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from fastapi import Request

from app.services.i18n_service import get_i18n_service
from app.core.i18n_middleware import get_request_language, get_request_i18n_service

logger = logging.getLogger(__name__)


class TranslationHelper:
    """Helper class for handling translations in API responses."""
    
    def __init__(self, request: Request):
        """
        Initialize translation helper with request context.
        
        Args:
            request: HTTP request containing language context
        """
        self.request = request
        self.language = get_request_language(request)
        self.i18n_service = get_request_i18n_service(request)
    
    def translate(self, key: str, fallback: Optional[str] = None) -> str:
        """
        Translate a key using the request's language.
        
        Args:
            key: Translation key
            fallback: Fallback text if translation not found
            
        Returns:
            Translated string
        """
        translation = self.i18n_service.get_translation(key, self.language)
        
        # If translation equals the key (not found) and fallback provided
        if translation == key and fallback is not None:
            return fallback
        
        return translation
    
    def translate_dict(self, data: Dict[str, Any], key_mappings: Dict[str, str]) -> Dict[str, Any]:
        """
        Translate specific keys in a dictionary.
        
        Args:
            data: Dictionary to translate
            key_mappings: Mapping of data keys to translation keys
            
        Returns:
            Dictionary with translated values
        """
        result = data.copy()
        
        for data_key, translation_key in key_mappings.items():
            if data_key in result:
                result[data_key] = self.translate(translation_key, result[data_key])
        
        return result
    
    def translate_list(self, items: List[Dict[str, Any]], key_mappings: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Translate specific keys in a list of dictionaries.
        
        Args:
            items: List of dictionaries to translate
            key_mappings: Mapping of data keys to translation keys
            
        Returns:
            List with translated dictionaries
        """
        return [self.translate_dict(item, key_mappings) for item in items]
    
    def get_localized_field(self, base_key: str, field_name: str) -> str:
        """
        Get a localized field value using i18n key pattern.
        
        Args:
            base_key: Base translation key
            field_name: Field name to append
            
        Returns:
            Translated field value
        """
        translation_key = f"{base_key}.{field_name}"
        return self.translate(translation_key)
    
    def create_localized_response(self, data: Any, translations: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Create a localized API response.
        
        Args:
            data: Response data
            translations: Additional translations to include
            
        Returns:
            Localized response dictionary
        """
        response = {
            "data": data,
            "language": self.language,
            "translations": translations or {}
        }
        
        return response
    
    def get_ui_translations(self) -> Dict[str, str]:
        """
        Get common UI translations for the current language.
        
        Returns:
            Dictionary of UI translations
        """
        return self.i18n_service.get_translations_by_category("ui", self.language)
    
    def get_module_translations(self) -> Dict[str, str]:
        """
        Get module translations for the current language.
        
        Returns:
            Dictionary of module translations
        """
        return self.i18n_service.get_translations_by_category("module", self.language)
    
    def get_error_message(self, error_key: str, default_message: str = None) -> str:
        """
        Get localized error message.
        
        Args:
            error_key: Error translation key
            default_message: Default error message if translation not found
            
        Returns:
            Localized error message
        """
        full_key = f"error.{error_key}" if not error_key.startswith("error.") else error_key
        return self.translate(full_key, default_message or error_key)


def get_translation_helper(request: Request) -> TranslationHelper:
    """
    Get a translation helper instance for the request.
    
    Args:
        request: HTTP request
        
    Returns:
        TranslationHelper instance
    """
    return TranslationHelper(request)


def translate_response_data(
    request: Request, 
    data: Union[Dict, List], 
    key_mappings: Dict[str, str]
) -> Union[Dict, List]:
    """
    Convenience function to translate response data.
    
    Args:
        request: HTTP request
        data: Data to translate (dict or list of dicts)
        key_mappings: Mapping of data keys to translation keys
        
    Returns:
        Translated data
    """
    helper = get_translation_helper(request)
    
    if isinstance(data, dict):
        return helper.translate_dict(data, key_mappings)
    elif isinstance(data, list):
        return helper.translate_list(data, key_mappings)
    else:
        return data


def create_error_response(
    request: Request, 
    error_key: str, 
    status_code: int = 400,
    details: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create a localized error response.
    
    Args:
        request: HTTP request
        error_key: Error translation key
        status_code: HTTP status code
        details: Additional error details
        
    Returns:
        Localized error response
    """
    helper = get_translation_helper(request)
    
    return {
        "error": {
            "code": error_key,
            "message": helper.get_error_message(error_key),
            "status_code": status_code,
            "details": details or {}
        },
        "language": helper.language
    }


def create_success_response(
    request: Request,
    data: Any = None,
    message_key: str = None,
    include_translations: bool = False
) -> Dict[str, Any]:
    """
    Create a localized success response.
    
    Args:
        request: HTTP request
        data: Response data
        message_key: Success message translation key
        include_translations: Whether to include common translations
        
    Returns:
        Localized success response
    """
    helper = get_translation_helper(request)
    
    response = {
        "success": True,
        "data": data,
        "language": helper.language
    }
    
    if message_key:
        response["message"] = helper.translate(message_key)
    
    if include_translations:
        response["translations"] = {
            "ui": helper.get_ui_translations(),
            "modules": helper.get_module_translations()
        }
    
    return response
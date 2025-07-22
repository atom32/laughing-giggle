"""
Internationalization (i18n) service for Park Tycoon Game.

This service handles translation key resolution, language detection,
and caching for performance optimization.
"""

import logging
from typing import Dict, List, Optional, Set
from functools import lru_cache
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.translation import Translation

logger = logging.getLogger(__name__)


class I18nService:
    """Service for handling internationalization operations."""
    
    # Supported languages
    SUPPORTED_LANGUAGES = {"en", "zh", "es", "fr"}
    DEFAULT_LANGUAGE = "zh"  # Chinese as default per requirements
    
    def __init__(self):
        """Initialize the I18n service."""
        self._cache: Dict[str, Dict[str, str]] = {}
        self._cache_loaded: Set[str] = set()
    
    def get_translation(
        self, 
        key: str, 
        language_code: str = None, 
        fallback_language: str = None
    ) -> str:
        """
        Get translation for a given key and language.
        
        Args:
            key: Translation key (e.g., 'ui.welcome')
            language_code: Target language code (defaults to DEFAULT_LANGUAGE)
            fallback_language: Fallback language if translation not found
            
        Returns:
            Translated string or the key itself if no translation found
        """
        if language_code is None:
            language_code = self.DEFAULT_LANGUAGE
        
        if fallback_language is None:
            fallback_language = "en" if language_code != "en" else self.DEFAULT_LANGUAGE
        
        # Validate language code
        if language_code not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported language code: {language_code}, using default")
            language_code = self.DEFAULT_LANGUAGE
        
        # Try to get from cache first
        translation = self._get_from_cache(key, language_code)
        if translation is not None:
            return translation
        
        # Load from database if not in cache
        translation = self._load_translation_from_db(key, language_code)
        if translation is not None:
            self._cache_translation(key, language_code, translation)
            return translation
        
        # Try fallback language
        if fallback_language != language_code:
            fallback_translation = self._get_from_cache(key, fallback_language)
            if fallback_translation is None:
                fallback_translation = self._load_translation_from_db(key, fallback_language)
                if fallback_translation is not None:
                    self._cache_translation(key, fallback_language, fallback_translation)
            
            if fallback_translation is not None:
                logger.debug(f"Using fallback translation for key '{key}': {fallback_language}")
                return fallback_translation
        
        # Return key as fallback if no translation found
        logger.warning(f"No translation found for key '{key}' in languages {language_code}, {fallback_language}")
        return key
    
    def get_translations_by_category(
        self, 
        category: str, 
        language_code: str = None
    ) -> Dict[str, str]:
        """
        Get all translations for a specific category.
        
        Args:
            category: Translation category (e.g., 'ui', 'module')
            language_code: Target language code
            
        Returns:
            Dictionary of key-value translation pairs
        """
        if language_code is None:
            language_code = self.DEFAULT_LANGUAGE
        
        if language_code not in self.SUPPORTED_LANGUAGES:
            language_code = self.DEFAULT_LANGUAGE
        
        # Load category translations if not cached
        if not self._is_category_cached(category, language_code):
            self._load_category_from_db(category, language_code)
        
        # Return cached translations for the category
        return {
            key: value for key, value in self._cache.get(language_code, {}).items()
            if key.startswith(f"{category}.")
        }
    
    def get_available_languages(self) -> List[str]:
        """
        Get list of available languages.
        
        Returns:
            List of supported language codes
        """
        return list(self.SUPPORTED_LANGUAGES)
    
    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language_code: Language code to check
            
        Returns:
            True if language is supported, False otherwise
        """
        return language_code in self.SUPPORTED_LANGUAGES
    
    def detect_language_from_header(self, accept_language: str) -> str:
        """
        Detect preferred language from Accept-Language header.
        
        Args:
            accept_language: Accept-Language header value
            
        Returns:
            Best matching supported language code
        """
        if not accept_language:
            return self.DEFAULT_LANGUAGE
        
        # Parse Accept-Language header
        languages = []
        for lang_range in accept_language.split(','):
            lang_range = lang_range.strip()
            if ';' in lang_range:
                lang, quality = lang_range.split(';', 1)
                try:
                    quality = float(quality.split('=')[1])
                except (ValueError, IndexError):
                    quality = 1.0
            else:
                lang = lang_range
                quality = 1.0
            
            # Extract language code (ignore region)
            lang_code = lang.strip().lower().split('-')[0]
            if lang_code in self.SUPPORTED_LANGUAGES:
                languages.append((lang_code, quality))
        
        if not languages:
            return self.DEFAULT_LANGUAGE
        
        # Sort by quality and return best match
        languages.sort(key=lambda x: x[1], reverse=True)
        return languages[0][0]
    
    def preload_translations(self, language_code: str = None) -> None:
        """
        Preload all translations for a language into cache.
        
        Args:
            language_code: Language to preload (defaults to all supported languages)
        """
        languages_to_load = [language_code] if language_code else self.SUPPORTED_LANGUAGES
        
        for lang in languages_to_load:
            if lang not in self.SUPPORTED_LANGUAGES:
                continue
                
            if lang not in self._cache_loaded:
                logger.info(f"Preloading translations for language: {lang}")
                self._load_all_translations_from_db(lang)
                self._cache_loaded.add(lang)
    
    def clear_cache(self, language_code: str = None) -> None:
        """
        Clear translation cache.
        
        Args:
            language_code: Specific language to clear (clears all if None)
        """
        if language_code:
            self._cache.pop(language_code, None)
            self._cache_loaded.discard(language_code)
            logger.info(f"Cleared cache for language: {language_code}")
        else:
            self._cache.clear()
            self._cache_loaded.clear()
            logger.info("Cleared all translation cache")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_translations = sum(len(translations) for translations in self._cache.values())
        return {
            "cached_languages": len(self._cache),
            "total_cached_translations": total_translations,
            "preloaded_languages": len(self._cache_loaded)
        }
    
    # Private methods
    
    def _get_from_cache(self, key: str, language_code: str) -> Optional[str]:
        """Get translation from cache."""
        return self._cache.get(language_code, {}).get(key)
    
    def _cache_translation(self, key: str, language_code: str, value: str) -> None:
        """Cache a translation."""
        if language_code not in self._cache:
            self._cache[language_code] = {}
        self._cache[language_code][key] = value
    
    def _is_category_cached(self, category: str, language_code: str) -> bool:
        """Check if a category is fully cached for a language."""
        if language_code not in self._cache:
            return False
        
        # Simple heuristic: if we have any translations for this category, assume it's cached
        # In a production system, you might want to track this more precisely
        return any(key.startswith(f"{category}.") for key in self._cache[language_code])
    
    def _load_translation_from_db(self, key: str, language_code: str) -> Optional[str]:
        """Load a single translation from database."""
        session = SessionLocal()
        try:
            translation = session.query(Translation).filter(
                Translation.key == key,
                Translation.language_code == language_code
            ).first()
            
            return translation.value if translation else None
            
        except Exception as e:
            logger.error(f"Error loading translation {key} for {language_code}: {e}")
            return None
        finally:
            session.close()
    
    def _load_category_from_db(self, category: str, language_code: str) -> None:
        """Load all translations for a category from database."""
        session = SessionLocal()
        try:
            translations = session.query(Translation).filter(
                Translation.category == category,
                Translation.language_code == language_code
            ).all()
            
            for translation in translations:
                self._cache_translation(translation.key, language_code, translation.value)
                
            logger.debug(f"Loaded {len(translations)} translations for category '{category}' in {language_code}")
            
        except Exception as e:
            logger.error(f"Error loading category {category} for {language_code}: {e}")
        finally:
            session.close()
    
    def _load_all_translations_from_db(self, language_code: str) -> None:
        """Load all translations for a language from database."""
        session = SessionLocal()
        try:
            translations = session.query(Translation).filter(
                Translation.language_code == language_code
            ).all()
            
            for translation in translations:
                self._cache_translation(translation.key, language_code, translation.value)
                
            logger.info(f"Loaded {len(translations)} translations for language {language_code}")
            
        except Exception as e:
            logger.error(f"Error loading all translations for {language_code}: {e}")
        finally:
            session.close()


# Global service instance
_i18n_service = None


def get_i18n_service() -> I18nService:
    """
    Get the global I18n service instance.
    
    Returns:
        I18nService instance
    """
    global _i18n_service
    if _i18n_service is None:
        _i18n_service = I18nService()
    return _i18n_service


# Convenience functions

def translate(key: str, language_code: str = None) -> str:
    """
    Convenience function to get a translation.
    
    Args:
        key: Translation key
        language_code: Target language code
        
    Returns:
        Translated string
    """
    return get_i18n_service().get_translation(key, language_code)


def t(key: str, lang: str = None) -> str:
    """
    Short alias for translate function.
    
    Args:
        key: Translation key
        lang: Target language code
        
    Returns:
        Translated string
    """
    return translate(key, lang)
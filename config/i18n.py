"""
Internationalization (i18n) configuration and utilities for the Flask farming game.

This module provides Flask-Babel integration, language detection, and translation utilities.
"""

import os
import logging
from flask import request, session, current_app
from flask_babel import Babel, get_locale
from werkzeug.datastructures import LanguageAccept

logger = logging.getLogger(__name__)

# Global Babel instance
babel = Babel()

# Supported languages configuration
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Español'
}

DEFAULT_LANGUAGE = 'en'


def init_babel(app):
    """
    Initialize Flask-Babel with the Flask application.
    
    Args:
        app: Flask application instance
    """
    try:
        # Initialize Babel with the app
        babel.init_app(app)
        
        # Configure Babel settings
        app.config['LANGUAGES'] = SUPPORTED_LANGUAGES
        app.config['BABEL_DEFAULT_LOCALE'] = DEFAULT_LANGUAGE
        app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
        
        # For Flask-Babel 3.x, locale selection is handled automatically
        # We'll use session-based language selection which is already implemented
        
        logger.info(f"Flask-Babel initialized with languages: {list(SUPPORTED_LANGUAGES.keys())}")
        logger.info(f"Default language set to: {DEFAULT_LANGUAGE}")
        
    except Exception as e:
        logger.error(f"Failed to initialize Flask-Babel: {e}")
        raise


# Note: Flask-Babel 3.1.0 handles locale selection automatically
# The get_locale_selector function is available for manual locale detection if needed


def get_locale_selector():
    """
    Determine the best language to use for the current request.
    
    Priority order:
    1. URL parameter 'lang'
    2. User's stored language preference (from session)
    3. User's database language preference (if logged in)
    4. Browser's Accept-Language header
    5. Default language
    
    Returns:
        str: Language code (e.g., 'en', 'es')
    """
    try:
        # 1. Check for URL parameter
        requested_language = request.args.get('lang')
        if requested_language and is_language_supported(requested_language):
            session['language'] = requested_language
            return requested_language
        
        # 2. Check session for stored preference
        if 'language' in session:
            session_lang = session['language']
            if is_language_supported(session_lang):
                return session_lang
        
        # 3. Check user's database preference (if logged in)
        if 'user_id' in session:
            try:
                from models import User
                user = User.query.get(session['user_id'])
                if user and user.preferred_language and is_language_supported(user.preferred_language):
                    session['language'] = user.preferred_language
                    return user.preferred_language
            except Exception as e:
                logger.warning(f"Error retrieving user language preference: {e}")
        
        # 4. Check browser's Accept-Language header
        browser_language = detect_browser_language()
        if browser_language:
            session['language'] = browser_language
            return browser_language
        
        # 5. Fall back to default language
        session['language'] = DEFAULT_LANGUAGE
        return DEFAULT_LANGUAGE
        
    except Exception as e:
        logger.warning(f"Error in locale selection: {e}")
        session['language'] = DEFAULT_LANGUAGE
        return DEFAULT_LANGUAGE


def detect_browser_language():
    """
    Detect the user's preferred language from browser headers.
    
    Returns:
        str or None: Supported language code or None if no match
    """
    try:
        if not request.headers.get('Accept-Language'):
            return None
        
        # Parse Accept-Language header
        accept_languages = LanguageAccept(request.headers.get('Accept-Language'))
        
        # Find the best match from supported languages
        for language_code in SUPPORTED_LANGUAGES.keys():
            if accept_languages.best_match([language_code]):
                logger.debug(f"Browser language detected: {language_code}")
                return language_code
        
        # Check for language variants (e.g., 'en-US' -> 'en')
        for lang_range in accept_languages:
            base_lang = lang_range[0].split('-')[0].lower()
            if base_lang in SUPPORTED_LANGUAGES:
                logger.debug(f"Browser language variant detected: {base_lang}")
                return base_lang
        
        return None
        
    except Exception as e:
        logger.warning(f"Error detecting browser language: {e}")
        return None


def is_language_supported(language_code):
    """
    Check if a language code is supported by the application.
    
    Args:
        language_code (str): Language code to validate
        
    Returns:
        bool: True if language is supported, False otherwise
    """
    if not language_code:
        return False
    
    return language_code.lower() in SUPPORTED_LANGUAGES


def get_available_languages():
    """
    Get list of available languages with their display names.
    
    Returns:
        dict: Dictionary mapping language codes to display names
    """
    return SUPPORTED_LANGUAGES.copy()


def get_current_language():
    """
    Get the current language code for the request.
    
    Returns:
        str: Current language code
    """
    try:
        current_locale = get_locale()
        return str(current_locale) if current_locale else DEFAULT_LANGUAGE
    except Exception as e:
        logger.warning(f"Error getting current language: {e}")
        return DEFAULT_LANGUAGE


def set_language_preference(language_code):
    """
    Set the user's language preference in the session.
    
    Args:
        language_code (str): Language code to set
        
    Returns:
        bool: True if language was set successfully, False otherwise
    """
    try:
        if is_language_supported(language_code):
            session['language'] = language_code
            logger.debug(f"Language preference set to: {language_code}")
            return True
        else:
            logger.warning(f"Attempted to set unsupported language: {language_code}")
            return False
    except Exception as e:
        logger.error(f"Error setting language preference: {e}")
        return False


def safe_translate(message_key, **kwargs):
    """
    Safely translate a message key with fallback handling.
    
    This function provides robust translation with fallback logic:
    1. Try to translate using Flask-Babel
    2. If translation fails or is missing, return the key itself
    3. Log warnings for missing translations
    
    Args:
        message_key (str): Translation key to translate
        **kwargs: Variables to substitute in the translated message
        
    Returns:
        str: Translated message or fallback text
    """
    try:
        from flask_babel import gettext
        
        # Attempt translation
        translated = gettext(message_key, **kwargs)
        
        # Check if translation was found (gettext returns the key if not found)
        if translated == message_key and message_key not in ['en', 'es']:
            logger.warning(f"Missing translation for key: '{message_key}' in language: {get_current_language()}")
        
        return translated
        
    except Exception as e:
        logger.error(f"Translation error for key '{message_key}': {e}")
        return message_key


def safe_ngettext(singular_key, plural_key, num, **kwargs):
    """
    Safely translate plural messages with fallback handling.
    
    Args:
        singular_key (str): Translation key for singular form
        plural_key (str): Translation key for plural form  
        num (int): Number to determine singular/plural
        **kwargs: Variables to substitute in the translated message
        
    Returns:
        str: Translated message or fallback text
    """
    try:
        from flask_babel import ngettext
        
        translated = ngettext(singular_key, plural_key, num, **kwargs)
        
        # Log if translation seems to be missing
        expected_key = singular_key if num == 1 else plural_key
        if translated == expected_key:
            logger.warning(f"Missing plural translation for keys: '{singular_key}'/'{plural_key}' in language: {get_current_language()}")
        
        return translated
        
    except Exception as e:
        logger.error(f"Plural translation error for keys '{singular_key}'/'{plural_key}': {e}")
        return singular_key if num == 1 else plural_key


def validate_language_code(language_code):
    """
    Validate and normalize a language code.
    
    Args:
        language_code (str): Language code to validate
        
    Returns:
        str or None: Normalized language code if valid, None otherwise
    """
    if not language_code:
        return None
    
    # Normalize to lowercase
    normalized = language_code.lower().strip()
    
    # Handle language variants (e.g., 'en-US' -> 'en')
    base_language = normalized.split('-')[0]
    
    # Check if base language is supported
    if base_language in SUPPORTED_LANGUAGES:
        return base_language
    
    return None


def get_language_display_name(language_code):
    """
    Get the display name for a language code.
    
    Args:
        language_code (str): Language code
        
    Returns:
        str: Display name or the language code if not found
    """
    return SUPPORTED_LANGUAGES.get(language_code, language_code)


def check_translation_files():
    """
    Check if translation files exist for all supported languages.
    
    Returns:
        dict: Status of translation files for each language
    """
    translation_status = {}
    translations_dir = os.path.join(os.getcwd(), 'translations')
    
    for lang_code in SUPPORTED_LANGUAGES.keys():
        lang_dir = os.path.join(translations_dir, lang_code, 'LC_MESSAGES')
        po_file = os.path.join(lang_dir, 'messages.po')
        mo_file = os.path.join(lang_dir, 'messages.mo')
        
        translation_status[lang_code] = {
            'po_exists': os.path.exists(po_file),
            'mo_exists': os.path.exists(mo_file),
            'directory_exists': os.path.exists(lang_dir)
        }
    
    return translation_status


def get_missing_translations():
    """
    Get information about missing translation files.
    
    Returns:
        list: List of languages with missing translation files
    """
    missing = []
    status = check_translation_files()
    
    for lang_code, file_status in status.items():
        if not file_status['mo_exists']:
            missing.append({
                'language': lang_code,
                'display_name': get_language_display_name(lang_code),
                'po_exists': file_status['po_exists'],
                'directory_exists': file_status['directory_exists']
            })
    
    return missing


def log_translation_status():
    """
    Log the current status of translation files.
    """
    try:
        status = check_translation_files()
        missing = get_missing_translations()
        
        logger.info("Translation file status:")
        for lang_code, file_status in status.items():
            display_name = get_language_display_name(lang_code)
            po_status = "✓" if file_status['po_exists'] else "✗"
            mo_status = "✓" if file_status['mo_exists'] else "✗"
            logger.info(f"  {lang_code} ({display_name}): PO {po_status}, MO {mo_status}")
        
        if missing:
            logger.warning(f"Missing compiled translations for: {[m['language'] for m in missing]}")
        else:
            logger.info("All translation files are available")
            
    except Exception as e:
        logger.error(f"Error checking translation status: {e}")


# Convenience functions for common translation patterns
def flash_message(message_key, category='info', **kwargs):
    """
    Create a translated flash message.
    
    Args:
        message_key (str): Translation key for the message
        category (str): Flash message category
        **kwargs: Variables for message formatting
        
    Returns:
        tuple: (translated_message, category) for use with Flask's flash()
    """
    translated_message = safe_translate(message_key, **kwargs)
    return translated_message, category


def translate_error(error_key, **kwargs):
    """
    Translate an error message with consistent error formatting.
    
    Args:
        error_key (str): Translation key for the error
        **kwargs: Variables for error message formatting
        
    Returns:
        str: Translated error message
    """
    return safe_translate(f"error.{error_key}", **kwargs)


def translate_success(success_key, **kwargs):
    """
    Translate a success message with consistent success formatting.
    
    Args:
        success_key (str): Translation key for the success message
        **kwargs: Variables for success message formatting
        
    Returns:
        str: Translated success message
    """
    return safe_translate(f"success.{success_key}", **kwargs)
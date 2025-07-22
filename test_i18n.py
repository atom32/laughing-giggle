"""
Unit tests for internationalization (i18n) functionality.

Tests the i18n system including:
- Locale detection and language preference handling
- Translation loading and fallback mechanisms
- Language switching and session management
- Translation utility functions
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
from flask import Flask, session, request
from config.i18n import (
    init_babel, get_locale_selector, detect_browser_language,
    is_language_supported, get_available_languages, get_current_language,
    set_language_preference, safe_translate, safe_ngettext,
    validate_language_code, get_language_display_name,
    check_translation_files, get_missing_translations
)


class TestI18nFunctionality(unittest.TestCase):
    """Test cases for i18n functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['TESTING'] = True
        
        # Initialize Babel
        init_babel(self.app)
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.app_context.pop()
    
    def test_language_support_validation(self):
        """Test language support validation."""
        # Test supported languages
        self.assertTrue(is_language_supported('en'))
        self.assertTrue(is_language_supported('es'))
        self.assertTrue(is_language_supported('fr'))
        
        # Test unsupported languages
        self.assertFalse(is_language_supported('de'))
        self.assertFalse(is_language_supported('zh'))
        self.assertFalse(is_language_supported(''))
        self.assertFalse(is_language_supported(None))
    
    def test_available_languages(self):
        """Test getting available languages."""
        languages = get_available_languages()
        
        self.assertIsInstance(languages, dict)
        self.assertIn('en', languages)
        self.assertIn('es', languages)
        self.assertIn('fr', languages)
        self.assertEqual(languages['en'], 'English')
        self.assertEqual(languages['es'], 'Español')
        self.assertEqual(languages['fr'], 'Français')
    
    def test_language_code_validation(self):
        """Test language code validation and normalization."""
        # Valid codes
        self.assertEqual(validate_language_code('en'), 'en')
        self.assertEqual(validate_language_code('ES'), 'es')
        self.assertEqual(validate_language_code('fr'), 'fr')
        
        # Language variants
        self.assertEqual(validate_language_code('en-US'), 'en')
        self.assertEqual(validate_language_code('es-MX'), 'es')
        
        # Invalid codes
        self.assertIsNone(validate_language_code('de'))
        self.assertIsNone(validate_language_code(''))
        self.assertIsNone(validate_language_code(None))
        self.assertIsNone(validate_language_code('invalid'))
    
    def test_language_display_names(self):
        """Test getting language display names."""
        self.assertEqual(get_language_display_name('en'), 'English')
        self.assertEqual(get_language_display_name('es'), 'Español')
        self.assertEqual(get_language_display_name('fr'), 'Français')
        self.assertEqual(get_language_display_name('unknown'), 'unknown')
    
    def test_browser_language_detection(self):
        """Test browser language detection from Accept-Language header."""
        with self.app.test_request_context(headers={'Accept-Language': 'en-US,en;q=0.9,es;q=0.8'}):
            detected = detect_browser_language()
            self.assertEqual(detected, 'en')
        
        with self.app.test_request_context(headers={'Accept-Language': 'es-ES,es;q=0.9'}):
            detected = detect_browser_language()
            self.assertEqual(detected, 'es')
        
        with self.app.test_request_context(headers={'Accept-Language': 'fr-FR,fr;q=0.9'}):
            detected = detect_browser_language()
            self.assertEqual(detected, 'fr')
        
        # Test unsupported language
        with self.app.test_request_context(headers={'Accept-Language': 'de-DE,de;q=0.9'}):
            detected = detect_browser_language()
            self.assertIsNone(detected)
        
        # Test no Accept-Language header
        with self.app.test_request_context():
            detected = detect_browser_language()
            self.assertIsNone(detected)
    
    def test_locale_selector_priority(self):
        """Test locale selector priority order."""
        # Test URL parameter priority
        with self.app.test_request_context('/?lang=es'):
            with self.client.session_transaction() as sess:
                locale = get_locale_selector()
                self.assertEqual(locale, 'es')
                self.assertEqual(sess.get('language'), 'es')
        
        # Test session priority
        with self.app.test_request_context():
            with self.client.session_transaction() as sess:
                sess['language'] = 'fr'
                locale = get_locale_selector()
                self.assertEqual(locale, 'fr')
        
        # Test browser language fallback
        with self.app.test_request_context(headers={'Accept-Language': 'es-ES,es;q=0.9'}):
            with self.client.session_transaction() as sess:
                # Clear session
                sess.pop('language', None)
                locale = get_locale_selector()
                self.assertEqual(locale, 'es')
                self.assertEqual(sess.get('language'), 'es')
        
        # Test default fallback
        with self.app.test_request_context():
            with self.client.session_transaction() as sess:
                sess.pop('language', None)
                locale = get_locale_selector()
                self.assertEqual(locale, 'en')  # DEFAULT_LANGUAGE
    
    def test_set_language_preference(self):
        """Test setting language preference in session."""
        with self.app.test_request_context():
            with self.client.session_transaction() as sess:
                # Test valid language
                result = set_language_preference('es')
                self.assertTrue(result)
                
                # Test invalid language
                result = set_language_preference('invalid')
                self.assertFalse(result)
    
    def test_safe_translate_fallback(self):
        """Test safe translation with fallback behavior."""
        with self.app.test_request_context():
            # Test with a key that likely doesn't exist
            result = safe_translate('nonexistent.key')
            self.assertEqual(result, 'nonexistent.key')
            
            # Test with variables
            result = safe_translate('test.message', username='TestUser')
            # Should return the key since translation doesn't exist
            self.assertEqual(result, 'test.message')
    
    def test_safe_ngettext_fallback(self):
        """Test safe plural translation with fallback behavior."""
        with self.app.test_request_context():
            # Test singular
            result = safe_ngettext('item', 'items', 1)
            self.assertEqual(result, 'item')
            
            # Test plural
            result = safe_ngettext('item', 'items', 2)
            self.assertEqual(result, 'items')
            
            # Test with variables
            result = safe_ngettext('%(num)d item', '%(num)d items', 1, num=1)
            self.assertEqual(result, '1 item')
            
            result = safe_ngettext('%(num)d item', '%(num)d items', 3, num=3)
            self.assertEqual(result, '3 items')
    
    def test_translation_file_checking(self):
        """Test translation file existence checking."""
        status = check_translation_files()
        
        self.assertIsInstance(status, dict)
        self.assertIn('en', status)
        self.assertIn('es', status)
        self.assertIn('fr', status)
        
        # Each language should have status info
        for lang_code, file_status in status.items():
            self.assertIn('po_exists', file_status)
            self.assertIn('mo_exists', file_status)
            self.assertIn('directory_exists', file_status)
            self.assertIsInstance(file_status['po_exists'], bool)
            self.assertIsInstance(file_status['mo_exists'], bool)
            self.assertIsInstance(file_status['directory_exists'], bool)
    
    def test_missing_translations_detection(self):
        """Test detection of missing translation files."""
        missing = get_missing_translations()
        
        self.assertIsInstance(missing, list)
        
        # Each missing translation should have required info
        for missing_lang in missing:
            self.assertIn('language', missing_lang)
            self.assertIn('display_name', missing_lang)
            self.assertIn('po_exists', missing_lang)
            self.assertIn('directory_exists', missing_lang)
    
    @patch('config.i18n.logger')
    def test_error_handling_in_locale_selector(self, mock_logger):
        """Test error handling in locale selector."""
        with self.app.test_request_context():
            # Mock an exception in user lookup
            with patch('config.i18n.User') as mock_user:
                mock_user.query.get.side_effect = Exception("Database error")
                
                with self.client.session_transaction() as sess:
                    sess['user_id'] = 1
                    locale = get_locale_selector()
                    
                    # Should fall back to default and log warning
                    self.assertEqual(locale, 'en')
                    mock_logger.warning.assert_called()
    
    def test_current_language_detection(self):
        """Test getting current language for request."""
        with self.app.test_request_context():
            with self.client.session_transaction() as sess:
                sess['language'] = 'es'
                
                # This test depends on Flask-Babel's get_locale() function
                # In a real scenario, this would return the current locale
                current_lang = get_current_language()
                self.assertIsInstance(current_lang, str)
                self.assertIn(current_lang, ['en', 'es', 'fr'])


class TestI18nIntegration(unittest.TestCase):
    """Integration tests for i18n functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['TESTING'] = True
        
        # Initialize Babel
        init_babel(self.app)
        
        # Add a test route
        @self.app.route('/test')
        def test_route():
            from flask_babel import gettext
            return gettext('Welcome back, Farmer %(username)s!', username='TestUser')
        
        self.client = self.app.test_client()
    
    def test_language_switching_in_request(self):
        """Test language switching within a request context."""
        with self.app.test_request_context():
            # Set language preference
            set_language_preference('es')
            
            # Get current language
            current = get_current_language()
            self.assertIsInstance(current, str)
    
    def test_babel_initialization(self):
        """Test that Babel is properly initialized."""
        # Check that Babel configuration is set
        self.assertIn('LANGUAGES', self.app.config)
        self.assertIn('BABEL_DEFAULT_LOCALE', self.app.config)
        self.assertIn('BABEL_DEFAULT_TIMEZONE', self.app.config)
        
        # Check language configuration
        languages = self.app.config['LANGUAGES']
        self.assertIn('en', languages)
        self.assertIn('es', languages)
        self.assertIn('fr', languages)


if __name__ == '__main__':
    unittest.main()
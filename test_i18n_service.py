"""
Unit tests for I18nService operations.
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.translation import Translation
from app.services.i18n_service import I18nService, get_i18n_service, translate, t


# Test database setup
@pytest.fixture
def test_db():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    # Add test translations
    test_translations = [
        Translation(key="ui.welcome", language_code="en", value="Welcome", category="ui"),
        Translation(key="ui.welcome", language_code="zh", value="欢迎", category="ui"),
        Translation(key="ui.welcome", language_code="es", value="Bienvenido", category="ui"),
        Translation(key="ui.login", language_code="en", value="Login", category="ui"),
        Translation(key="ui.login", language_code="zh", value="登录", category="ui"),
        Translation(key="module.market", language_code="en", value="Market", category="module"),
        Translation(key="module.market", language_code="zh", value="市场", category="module"),
        Translation(key="error.not_found", language_code="en", value="Not found", category="error"),
        Translation(key="missing.key", language_code="en", value="Missing key", category="test"),
    ]
    
    session.add_all(test_translations)
    session.commit()
    
    yield session
    session.close()


@pytest.fixture
def i18n_service():
    """Create a fresh I18nService instance for testing."""
    return I18nService()


class TestI18nService:
    """Test cases for I18nService."""
    
    def test_supported_languages(self, i18n_service):
        """Test supported languages configuration."""
        expected_languages = {"en", "zh", "es", "fr"}
        assert i18n_service.SUPPORTED_LANGUAGES == expected_languages
        assert i18n_service.DEFAULT_LANGUAGE == "zh"
    
    def test_get_available_languages(self, i18n_service):
        """Test getting available languages."""
        languages = i18n_service.get_available_languages()
        assert isinstance(languages, list)
        assert set(languages) == {"en", "zh", "es", "fr"}
    
    def test_is_language_supported(self, i18n_service):
        """Test language support checking."""
        assert i18n_service.is_language_supported("en") is True
        assert i18n_service.is_language_supported("zh") is True
        assert i18n_service.is_language_supported("es") is True
        assert i18n_service.is_language_supported("fr") is True
        assert i18n_service.is_language_supported("de") is False
        assert i18n_service.is_language_supported("invalid") is False
    
    @patch('app.services.i18n_service.SessionLocal')
    def test_get_translation_from_database(self, mock_session_local, i18n_service):
        """Test getting translation from database."""
        # Mock database session
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        
        # Mock translation result
        mock_translation = Mock()
        mock_translation.value = "Welcome"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_translation
        
        result = i18n_service.get_translation("ui.welcome", "en")
        
        assert result == "Welcome"
        mock_session.close.assert_called_once()
    
    @patch('app.services.i18n_service.SessionLocal')
    def test_get_translation_not_found(self, mock_session_local, i18n_service):
        """Test getting translation when key doesn't exist."""
        # Mock database session
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        
        # Mock no translation found
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = i18n_service.get_translation("nonexistent.key", "en")
        
        # Should return the key itself as fallback
        assert result == "nonexistent.key"
        # Session close should be called (may be called multiple times for fallback attempts)
        assert mock_session.close.call_count >= 1
    
    @patch('app.services.i18n_service.SessionLocal')
    def test_get_translation_with_fallback(self, mock_session_local, i18n_service):
        """Test getting translation with fallback language."""
        # Mock database session
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        
        # Mock no translation in primary language, but exists in fallback
        def mock_query_filter_first():
            # First call (primary language) returns None
            # Second call (fallback language) returns translation
            if not hasattr(mock_query_filter_first, 'call_count'):
                mock_query_filter_first.call_count = 0
            mock_query_filter_first.call_count += 1
            
            if mock_query_filter_first.call_count == 1:
                return None
            else:
                mock_translation = Mock()
                mock_translation.value = "Welcome"
                return mock_translation
        
        mock_session.query.return_value.filter.return_value.first.side_effect = mock_query_filter_first
        
        result = i18n_service.get_translation("ui.welcome", "fr", "en")
        
        assert result == "Welcome"
    
    def test_caching_functionality(self, i18n_service):
        """Test translation caching."""
        # Cache a translation
        i18n_service._cache_translation("test.key", "en", "Test Value")
        
        # Retrieve from cache
        cached_value = i18n_service._get_from_cache("test.key", "en")
        assert cached_value == "Test Value"
        
        # Test cache miss
        missing_value = i18n_service._get_from_cache("missing.key", "en")
        assert missing_value is None
    
    def test_cache_stats(self, i18n_service):
        """Test cache statistics."""
        # Initially empty
        stats = i18n_service.get_cache_stats()
        assert stats["cached_languages"] == 0
        assert stats["total_cached_translations"] == 0
        assert stats["preloaded_languages"] == 0
        
        # Add some cached translations
        i18n_service._cache_translation("test1", "en", "Value1")
        i18n_service._cache_translation("test2", "en", "Value2")
        i18n_service._cache_translation("test3", "zh", "Value3")
        
        stats = i18n_service.get_cache_stats()
        assert stats["cached_languages"] == 2
        assert stats["total_cached_translations"] == 3
    
    def test_clear_cache(self, i18n_service):
        """Test cache clearing functionality."""
        # Add some cached translations
        i18n_service._cache_translation("test1", "en", "Value1")
        i18n_service._cache_translation("test2", "zh", "Value2")
        
        # Clear specific language
        i18n_service.clear_cache("en")
        assert i18n_service._get_from_cache("test1", "en") is None
        assert i18n_service._get_from_cache("test2", "zh") == "Value2"
        
        # Clear all cache
        i18n_service.clear_cache()
        assert i18n_service._get_from_cache("test2", "zh") is None
        assert len(i18n_service._cache) == 0
    
    @patch('app.services.i18n_service.SessionLocal')
    def test_get_translations_by_category(self, mock_session_local, i18n_service):
        """Test getting translations by category."""
        # Mock database session
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        
        # Mock category translations
        mock_translations = [
            Mock(key="ui.welcome", value="Welcome"),
            Mock(key="ui.login", value="Login"),
            Mock(key="ui.logout", value="Logout")
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_translations
        
        result = i18n_service.get_translations_by_category("ui", "en")
        
        # Should have cached the translations
        assert "ui.welcome" in i18n_service._cache["en"]
        assert "ui.login" in i18n_service._cache["en"]
        assert "ui.logout" in i18n_service._cache["en"]
        
        mock_session.close.assert_called_once()
    
    def test_detect_language_from_header(self, i18n_service):
        """Test language detection from Accept-Language header."""
        # Test simple language
        result = i18n_service.detect_language_from_header("en")
        assert result == "en"
        
        # Test language with region
        result = i18n_service.detect_language_from_header("en-US")
        assert result == "en"
        
        # Test multiple languages with quality
        result = i18n_service.detect_language_from_header("fr;q=0.8,en;q=0.9,zh;q=1.0")
        assert result == "zh"
        
        # Test unsupported language falls back to default
        result = i18n_service.detect_language_from_header("de,it")
        assert result == "zh"  # DEFAULT_LANGUAGE
        
        # Test empty header
        result = i18n_service.detect_language_from_header("")
        assert result == "zh"  # DEFAULT_LANGUAGE
        
        # Test malformed header
        result = i18n_service.detect_language_from_header("invalid-header")
        assert result == "zh"  # DEFAULT_LANGUAGE
    
    def test_unsupported_language_fallback(self, i18n_service):
        """Test fallback to default language for unsupported languages."""
        with patch.object(i18n_service, '_load_translation_from_db') as mock_load:
            mock_load.return_value = "Test Value"
            
            result = i18n_service.get_translation("test.key", "unsupported_lang")
            
            # Should use default language instead
            mock_load.assert_called_with("test.key", "zh")
    
    @patch('app.services.i18n_service.SessionLocal')
    def test_preload_translations(self, mock_session_local, i18n_service):
        """Test preloading translations."""
        # Mock database session
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        
        # Mock translations
        mock_translations = [
            Mock(key="ui.welcome", value="Welcome"),
            Mock(key="ui.login", value="Login")
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_translations
        
        # Preload specific language
        i18n_service.preload_translations("en")
        
        assert "en" in i18n_service._cache_loaded
        assert "ui.welcome" in i18n_service._cache["en"]
        assert "ui.login" in i18n_service._cache["en"]
        
        mock_session.close.assert_called()


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @patch('app.services.i18n_service.get_i18n_service')
    def test_translate_function(self, mock_get_service):
        """Test translate convenience function."""
        mock_service = Mock()
        mock_service.get_translation.return_value = "Test Translation"
        mock_get_service.return_value = mock_service
        
        result = translate("test.key", "en")
        
        assert result == "Test Translation"
        mock_service.get_translation.assert_called_once_with("test.key", "en")
    
    @patch('app.services.i18n_service.get_i18n_service')
    def test_t_function_alias(self, mock_get_service):
        """Test t function alias."""
        mock_service = Mock()
        mock_service.get_translation.return_value = "Test Translation"
        mock_get_service.return_value = mock_service
        
        result = t("test.key", "zh")
        
        assert result == "Test Translation"
        mock_service.get_translation.assert_called_once_with("test.key", "zh")


class TestGlobalServiceInstance:
    """Test global service instance management."""
    
    def test_get_i18n_service_singleton(self):
        """Test that get_i18n_service returns the same instance."""
        service1 = get_i18n_service()
        service2 = get_i18n_service()
        
        assert service1 is service2
        assert isinstance(service1, I18nService)
    
    def test_service_instance_persistence(self):
        """Test that service instance persists across calls."""
        service = get_i18n_service()
        service._cache_translation("test.persistence", "en", "Persistent Value")
        
        # Get service again and check if cache persists
        service2 = get_i18n_service()
        cached_value = service2._get_from_cache("test.persistence", "en")
        
        assert cached_value == "Persistent Value"


class TestErrorHandling:
    """Test error handling in I18nService."""
    
    @patch('app.services.i18n_service.SessionLocal')
    def test_database_error_handling(self, mock_session_local, i18n_service):
        """Test handling of database errors."""
        # Mock database session that raises an exception
        mock_session = Mock()
        mock_session_local.return_value = mock_session
        mock_session.query.side_effect = Exception("Database error")
        
        result = i18n_service.get_translation("test.key", "en")
        
        # Should return key as fallback when database error occurs
        assert result == "test.key"
        # Session close should be called (may be called multiple times for fallback attempts)
        assert mock_session.close.call_count >= 1
    
    def test_invalid_language_code_handling(self, i18n_service):
        """Test handling of invalid language codes."""
        with patch.object(i18n_service, '_load_translation_from_db') as mock_load:
            mock_load.return_value = "Default Value"
            
            # Test None language code
            result = i18n_service.get_translation("test.key", None)
            mock_load.assert_called_with("test.key", "zh")  # Should use default
            
            # Test empty string language code
            result = i18n_service.get_translation("test.key", "")
            mock_load.assert_called_with("test.key", "zh")  # Should use default
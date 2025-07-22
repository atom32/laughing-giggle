"""
Unit tests for configuration management system.

Tests the AppConfig class with various scenarios including:
- INI file loading and parsing
- Environment detection and overrides
- Default fallback behavior
- Error handling for missing/invalid files
"""

import unittest
import tempfile
import os
import configparser
from unittest.mock import patch, MagicMock
from config.config import AppConfig
from config import defaults


class TestAppConfig(unittest.TestCase):
    """Test cases for AppConfig class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.temp_dir, 'test_settings.ini')
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
        os.rmdir(self.temp_dir)
    
    def create_test_config(self, content):
        """Create a test configuration file with given content."""
        with open(self.test_config_file, 'w') as f:
            f.write(content)
    
    def test_load_valid_config_file(self):
        """Test loading a valid configuration file."""
        config_content = """
[DEFAULT]
secret_key = test-secret-key
database_uri = sqlite:///test.db
port = 5000
debug = True

[development]
debug = True
database_uri = sqlite:///dev.db

[production]
debug = False
secret_key = prod-secret-key
"""
        self.create_test_config(config_content)
        
        config = AppConfig(environment='development', config_file=self.test_config_file)
        
        # Test environment-specific override
        self.assertEqual(config.get('database_uri'), 'sqlite:///dev.db')
        self.assertTrue(config.get('debug', value_type=bool))
        
        # Test fallback to DEFAULT section
        self.assertEqual(config.get('secret_key'), 'test-secret-key')
        self.assertEqual(config.get('port', value_type=int), 5000)
    
    def test_environment_detection(self):
        """Test automatic environment detection."""
        config_content = """
[DEFAULT]
secret_key = default-key

[development]
secret_key = dev-key

[production]
secret_key = prod-key
"""
        self.create_test_config(config_content)
        
        # Test explicit environment
        config = AppConfig(environment='production', config_file=self.test_config_file)
        self.assertEqual(config.environment, 'production')
        self.assertEqual(config.get('secret_key'), 'prod-key')
        
        # Test environment detection from ENV variable
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            config = AppConfig(config_file=self.test_config_file)
            self.assertEqual(config.environment, 'development')
            self.assertEqual(config.get('secret_key'), 'dev-key')
    
    def test_missing_config_file_creates_default(self):
        """Test that missing config file triggers default file creation."""
        non_existent_file = os.path.join(self.temp_dir, 'missing.ini')
        
        config = AppConfig(config_file=non_existent_file)
        
        # Should create the file
        self.assertTrue(os.path.exists(non_existent_file))
        
        # Should load default values
        self.assertEqual(config.get('secret_key'), defaults.SECRET_KEY)
        self.assertEqual(config.get('database_uri'), defaults.DATABASE_URI)
    
    def test_value_type_conversion(self):
        """Test conversion of string values to different types."""
        config_content = """
[DEFAULT]
port = 8080
debug = true
max_level = 50
available_languages = en,es,fr
"""
        self.create_test_config(config_content)
        
        config = AppConfig(config_file=self.test_config_file)
        
        # Test type conversions
        self.assertEqual(config.get('port', value_type=int), 8080)
        self.assertTrue(config.get('debug', value_type=bool))
        self.assertEqual(config.get('max_level', value_type=int), 50)
        self.assertEqual(config.get('available_languages', value_type=list), ['en', 'es', 'fr'])
    
    def test_fallback_behavior(self):
        """Test fallback behavior when keys are missing."""
        config_content = """
[DEFAULT]
secret_key = test-key
"""
        self.create_test_config(config_content)
        
        config = AppConfig(config_file=self.test_config_file)
        
        # Test fallback to provided default
        self.assertEqual(config.get('missing_key', 'fallback_value'), 'fallback_value')
        
        # Test fallback to defaults module
        self.assertEqual(config.get('database_uri'), defaults.DATABASE_URI)
    
    def test_configuration_validation(self):
        """Test configuration validation logic."""
        # Valid configuration
        valid_config = """
[DEFAULT]
secret_key = valid-secret-key
database_uri = sqlite:///valid.db
port = 5000
starting_coins = 100
starting_farm_size = 6
max_level = 100
experience_per_level = 1000
default_language = en
available_languages = en,es,fr
"""
        self.create_test_config(valid_config)
        config = AppConfig(config_file=self.test_config_file)
        self.assertTrue(config.validate_config())
        
        # Invalid configuration - empty secret key
        invalid_config = """
[DEFAULT]
secret_key = 
database_uri = sqlite:///test.db
port = 5000
starting_coins = 100
starting_farm_size = 6
max_level = 100
experience_per_level = 1000
default_language = en
available_languages = en,es,fr
"""
        self.create_test_config(invalid_config)
        config = AppConfig(config_file=self.test_config_file)
        self.assertFalse(config.validate_config())
    
    def test_convenience_methods(self):
        """Test convenience methods for common configuration values."""
        config_content = """
[DEFAULT]
secret_key = test-secret
database_uri = sqlite:///test.db
debug = false
host = 0.0.0.0
port = 8080
starting_coins = 500
starting_wheat = 10
starting_corn = 5
starting_carrots = 3
starting_farm_size = 8
max_level = 50
experience_per_level = 2000
"""
        self.create_test_config(config_content)
        
        config = AppConfig(config_file=self.test_config_file)
        
        # Test convenience methods
        self.assertEqual(config.get_secret_key(), 'test-secret')
        self.assertEqual(config.get_database_uri(), 'sqlite:///test.db')
        self.assertFalse(config.get_debug_mode())
        self.assertEqual(config.get_host(), '0.0.0.0')
        self.assertEqual(config.get_port(), 8080)
        
        # Test starting resources
        resources = config.get_starting_resources()
        expected_resources = {
            'coins': 500,
            'wheat': 10,
            'corn': 5,
            'carrots': 3,
            'farm_size': 8
        }
        self.assertEqual(resources, expected_resources)
        
        # Test game settings
        game_settings = config.get_game_settings()
        expected_settings = {
            'max_level': 50,
            'experience_per_level': 2000
        }
        self.assertEqual(game_settings, expected_settings)
    
    def test_database_directory_creation(self):
        """Test that database directory is created for SQLite URIs."""
        db_path = os.path.join(self.temp_dir, 'subdir', 'test.db')
        config_content = f"""
[DEFAULT]
database_uri = sqlite:///{db_path}
secret_key = test-key
"""
        self.create_test_config(config_content)
        
        config = AppConfig(config_file=self.test_config_file)
        
        # Get database URI should create the directory
        uri = config.get_database_uri()
        self.assertEqual(uri, f'sqlite:///{db_path}')
        self.assertTrue(os.path.exists(os.path.dirname(db_path)))
    
    def test_error_handling_invalid_file(self):
        """Test error handling for invalid configuration files."""
        # Create invalid INI file
        invalid_config = """
[DEFAULT
secret_key = test-key
invalid syntax here
"""
        self.create_test_config(invalid_config)
        
        # Should handle the error gracefully and use defaults
        config = AppConfig(config_file=self.test_config_file)
        self.assertEqual(config.get('secret_key'), defaults.SECRET_KEY)
    
    @patch('config.config.logger')
    def test_logging_behavior(self, mock_logger):
        """Test that appropriate logging occurs during configuration loading."""
        # Test successful loading
        config_content = """
[DEFAULT]
secret_key = test-key
"""
        self.create_test_config(config_content)
        
        config = AppConfig(config_file=self.test_config_file)
        
        # Should log successful loading
        mock_logger.info.assert_called()
        
        # Test missing file logging
        mock_logger.reset_mock()
        non_existent = os.path.join(self.temp_dir, 'missing.ini')
        config = AppConfig(config_file=non_existent)
        
        # Should log file creation
        mock_logger.info.assert_called()


if __name__ == '__main__':
    unittest.main()
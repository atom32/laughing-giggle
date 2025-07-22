"""
Integration tests for complete i18n and configuration workflows.

Tests end-to-end functionality including:
- Language switching from user interface
- User registration and login with language preferences
- Template rendering with different languages
- Configuration loading in different environments
"""

import unittest
import tempfile
import os
from flask import Flask
from models import db, User, Farm
from config.config import AppConfig
from config.i18n import init_babel
from routes import init_routes
from utils import init_database


class TestI18nIntegration(unittest.TestCase):
    """Integration tests for i18n functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test database
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, 'test.db')
        
        # Create test app
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.test_db_path}'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize components
        db.init_app(self.app)
        init_babel(self.app)
        init_routes(self.app)
        
        self.client = self.app.test_client()
        
        # Create database tables
        with self.app.app_context():
            init_database(self.app, db)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        os.rmdir(self.temp_dir)
    
    def test_user_registration_with_language_preference(self):
        """Test user registration with automatic language detection."""
        with self.app.test_request_context(headers={'Accept-Language': 'es-ES,es;q=0.9'}):
            response = self.client.post('/register', data={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpass123'
            }, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            
            # Check that user was created with detected language
            with self.app.app_context():
                user = User.query.filter_by(username='testuser').first()
                self.assertIsNotNone(user)
                self.assertEqual(user.preferred_language, 'es')
    
    def test_login_loads_user_language_preference(self):
        """Test that login loads user's language preference into session."""
        # Create test user with Spanish preference
        with self.app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                preferred_language='es'
            )
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
        
        # Login
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Check session has user's language preference
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('language'), 'es')
    
    def test_language_switching_endpoint(self):
        """Test the language switching endpoint."""
        # Test valid language switch
        response = self.client.get('/set_language/es', 
                                 headers={'Referer': '/dashboard'})
        
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Check session was updated
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('language'), 'es')
        
        # Test invalid language
        response = self.client.get('/set_language/invalid',
                                 headers={'Referer': '/dashboard'})
        
        self.assertEqual(response.status_code, 302)  # Still redirects
        
        # Session should not be updated with invalid language
        with self.client.session_transaction() as sess:
            self.assertNotEqual(sess.get('language'), 'invalid')
    
    def test_language_switching_with_logged_in_user(self):
        """Test language switching saves preference to database for logged-in users."""
        # Create and login user
        with self.app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                preferred_language='en'
            )
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
            user_id = user.id
        
        # Login
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Switch language
        response = self.client.get('/set_language/fr')
        self.assertEqual(response.status_code, 302)
        
        # Check database was updated
        with self.app.app_context():
            user = User.query.get(user_id)
            self.assertEqual(user.preferred_language, 'fr')
    
    def test_template_rendering_with_different_languages(self):
        """Test that templates render correctly with different languages."""
        # Create and login user
        with self.app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                preferred_language='en'
            )
            user.set_password('testpass123')
            db.session.add(user)
            
            # Create farm for user
            farm = Farm(user_id=user.id, name="Test Farm", size=6)
            db.session.add(farm)
            db.session.commit()
        
        # Login
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Test English (default)
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Farm Manager', response.data)
        
        # Switch to Spanish and test
        self.client.get('/set_language/es')
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        # Template should still render (even if not all strings are translated)
        self.assertIn(b'Farm Manager', response.data)
    
    def test_profile_language_preference_update(self):
        """Test updating language preference through profile page."""
        # Create and login user
        with self.app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                preferred_language='en'
            )
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
            user_id = user.id
        
        # Login
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Update language preference through profile
        response = self.client.post('/profile', data={
            'language': 'fr'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Check database was updated
        with self.app.app_context():
            user = User.query.get(user_id)
            self.assertEqual(user.preferred_language, 'fr')
        
        # Check session was updated
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('language'), 'fr')


class TestConfigurationIntegration(unittest.TestCase):
    """Integration tests for configuration management."""
    
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
        """Create a test configuration file."""
        with open(self.test_config_file, 'w') as f:
            f.write(content)
    
    def test_app_creation_with_custom_config(self):
        """Test creating app with custom configuration."""
        config_content = """
[DEFAULT]
secret_key = custom-secret-key
database_uri = sqlite:///custom.db
debug = false
port = 8080

[testing]
debug = true
database_uri = sqlite:///:memory:
"""
        self.create_test_config(config_content)
        
        # Create app with custom config
        app = Flask(__name__)
        config = AppConfig(environment='testing', config_file=self.test_config_file)
        
        app.secret_key = config.get_secret_key()
        app.config['SQLALCHEMY_DATABASE_URI'] = config.get_database_uri()
        app.config['DEBUG'] = config.get_debug_mode()
        
        # Test configuration was applied
        self.assertEqual(app.secret_key, 'custom-secret-key')
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], 'sqlite:///:memory:')
        self.assertTrue(app.config['DEBUG'])
    
    def test_configuration_validation_in_app_context(self):
        """Test configuration validation during app initialization."""
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
        
        # Invalid configuration
        invalid_config = """
[DEFAULT]
secret_key = 
database_uri = sqlite:///test.db
port = -1
starting_coins = -100
"""
        self.create_test_config(invalid_config)
        
        config = AppConfig(config_file=self.test_config_file)
        self.assertFalse(config.validate_config())
    
    def test_environment_specific_overrides(self):
        """Test that environment-specific settings override defaults."""
        config_content = """
[DEFAULT]
debug = false
database_uri = sqlite:///default.db
port = 5000

[development]
debug = true
database_uri = sqlite:///dev.db

[production]
debug = false
database_uri = sqlite:///prod.db
secret_key = production-secret

[testing]
database_uri = sqlite:///:memory:
starting_coins = 10000
"""
        self.create_test_config(config_content)
        
        # Test development environment
        dev_config = AppConfig(environment='development', config_file=self.test_config_file)
        self.assertTrue(dev_config.get_debug_mode())
        self.assertEqual(dev_config.get_database_uri(), 'sqlite:///dev.db')
        self.assertEqual(dev_config.get_port(), 5000)  # Falls back to DEFAULT
        
        # Test production environment
        prod_config = AppConfig(environment='production', config_file=self.test_config_file)
        self.assertFalse(prod_config.get_debug_mode())
        self.assertEqual(prod_config.get_database_uri(), 'sqlite:///prod.db')
        self.assertEqual(prod_config.get_secret_key(), 'production-secret')
        
        # Test testing environment
        test_config = AppConfig(environment='testing', config_file=self.test_config_file)
        self.assertEqual(test_config.get_database_uri(), 'sqlite:///:memory:')
        self.assertEqual(test_config.get_starting_resources()['coins'], 10000)


if __name__ == '__main__':
    unittest.main()
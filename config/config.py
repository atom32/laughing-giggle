import os
import configparser
import logging
from typing import Any, Optional
from config import defaults

logger = logging.getLogger(__name__)

class AppConfig:
    """Centralized configuration management for the farming game application.
    
    This class loads configuration from INI files with environment-specific sections
    and provides fallback to default values when configuration is missing or invalid.
    """
    
    def __init__(self, environment: Optional[str] = None, config_file: str = 'config/settings.ini'):
        """Initialize configuration loader.
        
        Args:
            environment: Target environment (development, production, testing).
                        If None, will be detected from FLASK_ENV or default to 'development'
            config_file: Path to the INI configuration file
        """
        self.config_file = config_file
        self.environment = environment or self._detect_environment()
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _detect_environment(self) -> str:
        """Detect the current environment from environment variables."""
        env = os.getenv('FLASK_ENV', os.getenv('ENVIRONMENT', defaults.DEFAULT_ENVIRONMENT))
        
        if env not in defaults.SUPPORTED_ENVIRONMENTS:
            logger.warning(f"Unknown environment '{env}', defaulting to '{defaults.DEFAULT_ENVIRONMENT}'")
            return defaults.DEFAULT_ENVIRONMENT
        
        return env
    
    def _load_config(self):
        """Load configuration from INI file with error handling."""
        try:
            if os.path.exists(self.config_file):
                self.config.read(self.config_file)
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                logger.warning(f"Configuration file {self.config_file} not found, using defaults")
                self._create_default_config_file()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            logger.info("Continuing with default configuration values")
    
    def _create_default_config_file(self):
        """Create a default configuration file if it doesn't exist."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Create default configuration content
            default_config = configparser.ConfigParser()
            
            # DEFAULT section
            default_config['DEFAULT'] = {
                'database_uri': defaults.DATABASE_URI,
                'database_track_modifications': str(defaults.DATABASE_TRACK_MODIFICATIONS),
                'secret_key': defaults.SECRET_KEY,
                'password_salt': defaults.PASSWORD_SALT,
                'debug': str(defaults.DEBUG),
                'host': defaults.HOST,
                'port': str(defaults.PORT),
                'starting_coins': str(defaults.STARTING_COINS),
                'starting_wheat': str(defaults.STARTING_WHEAT),
                'starting_corn': str(defaults.STARTING_CORN),
                'starting_carrots': str(defaults.STARTING_CARROTS),
                'starting_farm_size': str(defaults.STARTING_FARM_SIZE),
                'max_level': str(defaults.MAX_LEVEL),
                'experience_per_level': str(defaults.EXPERIENCE_PER_LEVEL),
                'default_language': defaults.DEFAULT_LANGUAGE,
                'available_languages': ','.join(defaults.AVAILABLE_LANGUAGES)
            }
            
            # Development environment
            default_config['development'] = {
                'debug': 'True',
                'database_uri': 'sqlite:///instance/farm.db'
            }
            
            # Production environment
            default_config['production'] = {
                'debug': 'False',
                'secret_key': 'CHANGE-THIS-IN-PRODUCTION',
                'password_salt': 'CHANGE-THIS-IN-PRODUCTION',
                'database_uri': 'sqlite:///instance/farm_prod.db'
            }
            
            # Testing environment
            default_config['testing'] = {
                'debug': 'False',
                'database_uri': 'sqlite:///:memory:',
                'starting_coins': '10000'
            }
            
            with open(self.config_file, 'w') as f:
                default_config.write(f)
            
            # Reload the configuration
            self.config = default_config
            logger.info(f"Created default configuration file at {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to create default configuration file: {e}")
    
    def get(self, key: str, fallback: Any = None, value_type: type = str) -> Any:
        """Get configuration value with environment-specific override support.
        
        Args:
            key: Configuration key to retrieve
            fallback: Fallback value if key is not found
            value_type: Type to convert the value to (str, int, bool, float)
        
        Returns:
            Configuration value converted to the specified type
        """
        try:
            # Try environment-specific section first
            if self.config.has_section(self.environment) and self.config.has_option(self.environment, key):
                value = self.config.get(self.environment, key)
            # Fall back to DEFAULT section
            elif self.config.has_option('DEFAULT', key):
                value = self.config.get('DEFAULT', key)
            # Use provided fallback
            elif fallback is not None:
                return fallback
            # Use defaults module fallback
            else:
                default_value = getattr(defaults, key.upper(), None)
                if default_value is not None:
                    return default_value
                raise KeyError(f"Configuration key '{key}' not found")
            
            # Convert to requested type
            return self._convert_value(value, value_type)
            
        except Exception as e:
            logger.warning(f"Error getting configuration value '{key}': {e}")
            if fallback is not None:
                return fallback
            # Try defaults module as last resort
            return getattr(defaults, key.upper(), None)
    
    def _convert_value(self, value: str, value_type: type) -> Any:
        """Convert string configuration value to specified type."""
        if value_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif value_type == int:
            return int(value)
        elif value_type == float:
            return float(value)
        elif value_type == list:
            return [item.strip() for item in value.split(',') if item.strip()]
        else:
            return value
    
    def validate_config(self) -> bool:
        """Validate critical configuration values.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Validate required string values are not empty
            required_strings = ['secret_key', 'database_uri']
            for key in required_strings:
                value = self.get(key)
                if not value or value.strip() == '':
                    logger.error(f"Required configuration '{key}' is empty")
                    return False
            
            # Validate numeric values are positive
            numeric_configs = [
                ('port', int), ('starting_coins', int), ('starting_farm_size', int),
                ('max_level', int), ('experience_per_level', int)
            ]
            for key, value_type in numeric_configs:
                value = self.get(key, value_type=value_type)
                if value <= 0:
                    logger.error(f"Configuration '{key}' must be positive, got {value}")
                    return False
            
            # Validate language configuration
            default_lang = self.get('default_language')
            available_langs = self.get('available_languages', value_type=list)
            if default_lang not in available_langs:
                logger.error(f"Default language '{default_lang}' not in available languages {available_langs}")
                return False
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    # Convenience methods for commonly used configuration values
    def get_database_uri(self) -> str:
        """Get database URI with environment-specific override."""
        uri = self.get('database_uri', defaults.DATABASE_URI)
        
        # Ensure directory exists for SQLite databases
        if uri.startswith('sqlite:///') and not uri.endswith(':memory:'):
            db_path = uri.replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                try:
                    os.makedirs(db_dir, exist_ok=True)
                    logger.info(f"Created database directory: {db_dir}")
                except Exception as e:
                    logger.warning(f"Failed to create database directory {db_dir}: {e}")
        
        return uri
    
    def get_secret_key(self) -> str:
        """Get secret key with environment-specific override."""
        return self.get('secret_key', defaults.SECRET_KEY)
    
    def get_debug_mode(self) -> bool:
        """Get debug mode setting."""
        return self.get('debug', defaults.DEBUG, bool)
    
    def get_host(self) -> str:
        """Get application host."""
        return self.get('host', defaults.HOST)
    
    def get_port(self) -> int:
        """Get application port."""
        return self.get('port', defaults.PORT, int)
    
    def get_starting_resources(self) -> dict:
        """Get starting resources for new users."""
        return {
            'coins': self.get('starting_coins', defaults.STARTING_COINS, int),
            'wheat': self.get('starting_wheat', defaults.STARTING_WHEAT, int),
            'corn': self.get('starting_corn', defaults.STARTING_CORN, int),
            'carrots': self.get('starting_carrots', defaults.STARTING_CARROTS, int),
            'farm_size': self.get('starting_farm_size', defaults.STARTING_FARM_SIZE, int)
        }
    
    def get_game_settings(self) -> dict:
        """Get game-related configuration."""
        return {
            'max_level': self.get('max_level', defaults.MAX_LEVEL, int),
            'experience_per_level': self.get('experience_per_level', defaults.EXPERIENCE_PER_LEVEL, int)
        }
    
    def get_i18n_settings(self) -> dict:
        """Get internationalization settings."""
        return {
            'default_language': self.get('default_language', defaults.DEFAULT_LANGUAGE),
            'available_languages': self.get('available_languages', defaults.AVAILABLE_LANGUAGES, list)
        }
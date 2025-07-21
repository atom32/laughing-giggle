# Default configuration values for the farming game application
# These values are used as fallbacks when configuration files are missing or incomplete

# Database configuration
DATABASE_URI = 'sqlite:///instance/farm.db'
DATABASE_TRACK_MODIFICATIONS = False

# Security configuration
SECRET_KEY = 'farm-manager-secret-key-change-in-production'
PASSWORD_SALT = 'farm-salt-change-in-production'

# Application configuration
DEBUG = True
HOST = '127.0.0.1'
PORT = 5000

# Game configuration
STARTING_COINS = 1000
STARTING_WHEAT = 50
STARTING_CORN = 30
STARTING_CARROTS = 20
STARTING_FARM_SIZE = 6
MAX_LEVEL = 100
EXPERIENCE_PER_LEVEL = 100

# Admin configuration
DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_EMAIL = 'admin@farm.local'
DEFAULT_ADMIN_PASSWORD = 'admin123'
DEFAULT_ADMIN_COINS = 50000
DEFAULT_ADMIN_RESOURCES = 1000
DEFAULT_ADMIN_LEVEL = 10
DEFAULT_ADMIN_EXPERIENCE = 1000

# I18n configuration (for future use)
DEFAULT_LANGUAGE = 'en'
AVAILABLE_LANGUAGES = ['en', 'es']

# Environment detection
SUPPORTED_ENVIRONMENTS = ['development', 'production', 'testing']
DEFAULT_ENVIRONMENT = 'development'
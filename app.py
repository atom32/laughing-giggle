from flask import Flask
from models import db
from routes import init_routes
from utils import init_database
from config.config import AppConfig
from config.i18n import init_babel
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(environment=None, config_file=None):
    """Create and configure the Flask application.
    
    Args:
        environment: Target environment (development, production, testing)
        config_file: Path to configuration file (optional)
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    #print("Using database URI:", app.config["SQLALCHEMY_DATABASE_URI"])

    try:
        # Initialize configuration system
        config_path = config_file or 'config/settings.ini'
        config = AppConfig(environment=environment, config_file=config_path)
        
        # Validate configuration
        if not config.validate_config():
            logger.warning("Configuration validation failed, continuing with available settings")
        
        # Configure Flask application
        app.secret_key = config.get_secret_key()
        app.config['SQLALCHEMY_DATABASE_URI'] = config.get_database_uri()
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.get('database_track_modifications', False, bool)
        
        # Store config instance for use in other parts of the application
        app.config['APP_CONFIG'] = config
        
        logger.info(f"Application configured for {config.environment} environment")
        
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        logger.info("Falling back to hardcoded defaults")
        
        # Fallback to hardcoded values if configuration fails
        app.secret_key = 'farm-manager-secret-key-change-in-production'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/farm.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['APP_CONFIG'] = None
    
    try:
        # Initialize database
        db.init_app(app)
        
        # Initialize Flask-Babel for internationalization
        init_babel(app)
        
        # Add template context functions for i18n
        from config.i18n import get_available_languages, get_current_language
        from flask_babel import gettext, ngettext, get_locale
        from utils import get_current_user
        
        @app.context_processor
        def inject_i18n_functions():
            """Make i18n functions available in all templates."""
            return {
                'get_available_languages': get_available_languages,
                'get_current_language': get_current_language,
                'get_current_user': get_current_user,
                'get_locale': get_locale,
                '_': gettext,
                'gettext': gettext,
                'ngettext': ngettext
            }
        
        # Initialize routes
        init_routes(app)
        
        # Initialize database with default data
        init_database(app, db)
        
        logger.info("Application initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        raise
    
    return app

if __name__ == '__main__':
    try:
        app = create_app()
        config = app.config.get('APP_CONFIG')
        
        if config:
            # Use configuration values for development server
            host = config.get_host()
            port = config.get_port()
            debug = config.get_debug_mode()
            
            logger.info(f"Starting development server on {host}:{port} (debug={debug})")
            app.run(host=host, port=port, debug=debug)
        else:
            # Fallback if configuration failed
            logger.warning("Using fallback configuration for development server")
            app.run(debug=True)
            
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
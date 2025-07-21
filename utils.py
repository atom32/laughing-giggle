from flask import session, redirect, url_for, flash
from flask_babel import gettext as _
from functools import wraps
from models import User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash(_('Admin access required!'), 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def init_database(app, db):
    """Initialize database and create default data"""
    with app.app_context():
        db.create_all()
        
        # Import here to avoid circular imports
        from models import User, Crop
        from werkzeug.security import generate_password_hash
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Get configuration instance
        config = app.config.get('APP_CONFIG')
        
        # Create default admin if doesn't exist
        admin_username = config.get('default_admin_username', 'admin') if config else 'admin'
        admin = User.query.filter_by(username=admin_username).first()
        
        if not admin:
            if config:
                # Use configuration values
                admin_email = config.get('default_admin_email', 'admin@farm.local')
                admin_password = config.get('default_admin_password', 'admin123')
                admin_coins = config.get('default_admin_coins', 50000, int)
                admin_resources = config.get('default_admin_resources', 1000, int)
                admin_level = config.get('default_admin_level', 10, int)
                admin_experience = config.get('default_admin_experience', 1000, int)
            else:
                # Fallback to hardcoded values
                admin_email = 'admin@farm.local'
                admin_password = 'admin123'
                admin_coins = 50000
                admin_resources = 1000
                admin_level = 10
                admin_experience = 1000
            
            admin = User(
                username=admin_username,
                email=admin_email,
                password_hash=generate_password_hash(admin_password),
                is_admin=True,
                coins=admin_coins,
                wheat=admin_resources,
                corn=admin_resources,
                carrots=admin_resources,
                level=admin_level,
                experience=admin_experience,
                preferred_language='en'
            )
            db.session.add(admin)
            logger.info(f"Created default admin user: {admin_username}")
        
        # Create default crops if they don't exist
        if not Crop.query.first():
            crops = [
                Crop(name='Wheat', growth_time=5, sell_price=15, buy_price=5, experience_gain=2),
                Crop(name='Corn', growth_time=10, sell_price=30, buy_price=10, experience_gain=4),
                Crop(name='Carrots', growth_time=15, sell_price=50, buy_price=20, experience_gain=6),
                Crop(name='Tomatoes', growth_time=20, sell_price=75, buy_price=30, experience_gain=8),
                Crop(name='Potatoes', growth_time=25, sell_price=100, buy_price=40, experience_gain=10),
            ]
            for crop in crops:
                db.session.add(crop)
            logger.info("Created default crop data")
        
        try:
            db.session.commit()
            logger.info("Database initialization completed successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            db.session.rollback()
            raise
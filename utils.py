from flask import session, redirect, url_for, flash
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
            flash('Admin access required!', 'error')
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
        
        # Create default admin if doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@farm.local',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                coins=50000,
                wheat=1000,
                corn=1000,
                carrots=1000,
                level=10,
                experience=1000
            )
            db.session.add(admin)
        
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
        
        db.session.commit()
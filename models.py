from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    preferred_language = db.Column(db.String(5), default='en')
    
    # Farm resources
    coins = db.Column(db.Integer, default=1000)
    wheat = db.Column(db.Integer, default=50)
    corn = db.Column(db.Integer, default=30)
    carrots = db.Column(db.Integer, default=20)
    experience = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)

class Farm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    size = db.Column(db.Integer, default=10)  # Number of plots
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('farms', lazy=True))

class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    growth_time = db.Column(db.Integer, nullable=False)  # minutes
    sell_price = db.Column(db.Integer, nullable=False)
    buy_price = db.Column(db.Integer, nullable=False)
    experience_gain = db.Column(db.Integer, default=1)

class Plot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=True)
    planted_at = db.Column(db.DateTime, nullable=True)
    is_ready = db.Column(db.Boolean, default=False)
    
    farm = db.relationship('Farm', backref=db.backref('plots', lazy=True))
    crop = db.relationship('Crop', backref=db.backref('plots', lazy=True))
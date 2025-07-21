from flask import Flask
from models import db
from routes import init_routes
from utils import init_database
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = 'farm-manager-secret-key-change-in-production'
    
    # Use a simple database path in the current directory
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farm.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Initialize routes
    init_routes(app)
    
    # Initialize database with default data
    init_database(app, db)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
#!/usr/bin/env python3
"""
Test script to verify language preference routes.
"""

from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

def test_language_routes():
    """Test language preference routes."""
    print("Testing language preference routes...")
    
    # Create app and test client
    app = create_app(environment='testing')
    client = app.test_client()
    
    with app.app_context():
        # Create a test user
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpass'),
            preferred_language='en'
        )
        db.session.add(test_user)
        db.session.commit()
        
        print(f"Created test user: {test_user.username} with language: {test_user.preferred_language}")
        
        # Test 1: Test set_language route without login (guest user)
        print("\n1. Testing set_language route for guest user...")
        with client.session_transaction() as sess:
            sess.clear()
        
        response = client.get('/set_language/es', follow_redirects=True)
        print(f"   Response status: {response.status_code}")
        
        with client.session_transaction() as sess:
            session_lang = sess.get('language')
            print(f"   Session language after setting to 'es': {session_lang}")
        
        # Test 2: Test set_language route with logged in user
        print("\n2. Testing set_language route for logged in user...")
        
        # Login the test user
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
        
        response = client.get('/set_language/es', follow_redirects=True)
        print(f"   Response status: {response.status_code}")
        
        # Check if user's database preference was updated
        updated_user = User.query.get(test_user.id)
        print(f"   User's database language preference: {updated_user.preferred_language}")
        
        with client.session_transaction() as sess:
            session_lang = sess.get('language')
            print(f"   Session language: {session_lang}")
        
        # Test 3: Test invalid language
        print("\n3. Testing invalid language...")
        response = client.get('/set_language/invalid', follow_redirects=True)
        print(f"   Response status: {response.status_code}")
        
        # User's preference should remain unchanged
        user_after_invalid = User.query.get(test_user.id)
        print(f"   User's language after invalid request: {user_after_invalid.preferred_language}")
        
        # Test 4: Test profile route with language update
        print("\n4. Testing profile route with language update...")
        
        response = client.post('/profile', data={'preferred_language': 'en'}, follow_redirects=True)
        print(f"   Response status: {response.status_code}")
        
        # Check if user's preference was updated back to English
        user_after_profile = User.query.get(test_user.id)
        print(f"   User's language after profile update: {user_after_profile.preferred_language}")
        
        # Clean up
        db.session.delete(test_user)
        db.session.commit()
        print("\n✓ Test user cleaned up")

if __name__ == '__main__':
    test_language_routes()
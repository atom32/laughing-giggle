#!/usr/bin/env python3
"""
Test script to verify language preference functionality.
"""

import sqlite3
import os
from app import create_app
from models import db, User

def test_language_preference():
    """Test language preference functionality."""
    print("Testing language preference functionality...")
    
    # Create app and test client
    app = create_app(environment='testing')
    
    with app.app_context():
        # Test 1: Check if User model has preferred_language field
        print("\n1. Testing User model preferred_language field...")
        try:
            user = User.query.first()
            if user:
                print(f"   ✓ User '{user.username}' has preferred_language: '{user.preferred_language}'")
            else:
                print("   ! No users found in database")
        except Exception as e:
            print(f"   ✗ Error accessing preferred_language field: {e}")
        
        # Test 2: Test language validation
        print("\n2. Testing language validation...")
        from config.i18n import is_language_supported
        
        test_languages = ['en', 'es', 'fr', 'invalid', None, '']
        for lang in test_languages:
            result = is_language_supported(lang)
            status = "✓" if result else "✗"
            print(f"   {status} Language '{lang}': {result}")
        
        # Test 3: Test available languages
        print("\n3. Testing available languages...")
        from config.i18n import get_available_languages
        
        available = get_available_languages()
        print(f"   Available languages: {available}")
        
        # Test 4: Test language preference update
        print("\n4. Testing language preference update...")
        try:
            user = User.query.first()
            if user:
                original_lang = user.preferred_language
                print(f"   Original language: {original_lang}")
                
                # Update to Spanish
                user.preferred_language = 'es'
                db.session.commit()
                
                # Verify update
                updated_user = User.query.get(user.id)
                print(f"   Updated language: {updated_user.preferred_language}")
                
                # Restore original
                user.preferred_language = original_lang
                db.session.commit()
                print(f"   Restored language: {user.preferred_language}")
                
                print("   ✓ Language preference update successful")
            else:
                print("   ! No users found for testing")
        except Exception as e:
            print(f"   ✗ Error updating language preference: {e}")

if __name__ == '__main__':
    test_language_preference()
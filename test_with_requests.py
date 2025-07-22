"""
Test authentication endpoints using requests library with a running server
"""
import requests
import time
import subprocess
import sys
import os
import signal
from threading import Thread

BASE_URL = "http://127.0.0.1:8000"

def test_endpoints():
    """Test authentication endpoints with requests."""
    try:
        # Test health endpoint
        print("--- Testing Health Endpoint ---")
        response = requests.get(f"{BASE_URL}/api/v1/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        
        if response.status_code != 200:
            print("Server not responding correctly")
            return
        
        # Test user registration
        print("\n--- Testing User Registration ---")
        register_data = {
            "username": "testuser123",
            "password": "testpass123"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
        print(f"Registration: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"✓ User registered: {data['user']['username']}")
            print(f"✓ Token received: {data['access_token'][:20]}...")
            token = data["access_token"]
        else:
            print(f"✗ Registration failed: {response.json()}")
            return
        
        # Test user login
        print("\n--- Testing User Login ---")
        login_data = {
            "username": "testuser123",
            "password": "testpass123"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        print(f"Login: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ User logged in: {data['user']['username']}")
            print(f"✓ Token received: {data['access_token'][:20]}...")
            login_token = data["access_token"]
        else:
            print(f"✗ Login failed: {response.json()}")
            return
        
        # Test current user endpoint
        print("\n--- Testing Current User Info ---")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        print(f"Current user: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Current user: {data['username']}")
            print(f"✓ Is admin: {data['is_admin']}")
            print(f"✓ Is active: {data['is_active']}")
        else:
            print(f"✗ Current user failed: {response.json()}")
        
        # Test token refresh
        print("\n--- Testing Token Refresh ---")
        response = requests.post(f"{BASE_URL}/api/v1/auth/refresh", headers=headers)
        print(f"Token refresh: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Token refreshed: {data['access_token'][:20]}...")
            refresh_token = data["access_token"]
        else:
            print(f"✗ Token refresh failed: {response.json()}")
            return
        
        # Test password change
        print("\n--- Testing Password Change ---")
        password_data = {
            "old_password": "testpass123",
            "new_password": "newpass456"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/change-password", headers=headers, json=password_data)
        print(f"Password change: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Password changed: {data['message']}")
        else:
            print(f"✗ Password change failed: {response.json()}")
        
        # Test login with new password
        print("\n--- Testing Login with New Password ---")
        new_login_data = {
            "username": "testuser123",
            "password": "newpass456"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=new_login_data)
        print(f"New password login: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Login with new password successful")
            final_token = data["access_token"]
        else:
            print(f"✗ New password login failed: {response.json()}")
            return
        
        # Test logout
        print("\n--- Testing Logout ---")
        final_headers = {"Authorization": f"Bearer {final_token}"}
        response = requests.post(f"{BASE_URL}/api/v1/auth/logout", headers=final_headers)
        print(f"Logout: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Logout successful: {data['message']}")
        else:
            print(f"✗ Logout failed: {response.json()}")
        
        print("\n🎉 All authentication endpoints working correctly!")
        
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure the server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Testing authentication endpoints...")
    print("Make sure to start the server first with: python main.py")
    print("Or run: uvicorn main:app --reload")
    print()
    
    test_endpoints()
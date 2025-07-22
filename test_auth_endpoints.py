"""
Integration tests for authentication API endpoints
"""
import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestUserRegistration:
    """Test user registration endpoint."""
    
    def test_register_success(self, client: TestClient):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json={
            "username": "newuser123",
            "password": "newpass123"
        })
        
        assert response.status_code == 201
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["user"]["username"] == "newuser123"
        assert data["user"]["is_admin"] is False
        assert data["user"]["is_active"] is True
    
    def test_register_duplicate_username(self, client: TestClient):
        """Test registration with duplicate username."""
        # First registration
        client.post("/api/v1/auth/register", json={
            "username": "duplicate123",
            "password": "testpass123"
        })
        
        # Second registration with same username
        response = client.post("/api/v1/auth/register", json={
            "username": "duplicate123",
            "password": "newpass123"
        })
        
        assert response.status_code == 409
        assert "Username already exists" in response.json()["detail"]
    
    def test_register_invalid_username(self, client: TestClient):
        """Test registration with invalid username."""
        # Too short username
        response = client.post("/api/v1/auth/register", json={
            "username": "ab",
            "password": "validpass123"
        })
        assert response.status_code == 422
        
        # Empty username
        response = client.post("/api/v1/auth/register", json={
            "username": "",
            "password": "validpass123"
        })
        assert response.status_code == 422
        
        # Username with invalid characters
        response = client.post("/api/v1/auth/register", json={
            "username": "user@name",
            "password": "validpass123"
        })
        assert response.status_code == 422
    
    def test_register_invalid_password(self, client: TestClient):
        """Test registration with invalid password."""
        # Too short password
        response = client.post("/api/v1/auth/register", json={
            "username": "validuser1",
            "password": "short"
        })
        assert response.status_code == 422
        
        # Password without numbers
        response = client.post("/api/v1/auth/register", json={
            "username": "validuser2",
            "password": "onlyletters"
        })
        assert response.status_code == 422
        
        # Password without letters
        response = client.post("/api/v1/auth/register", json={
            "username": "validuser3",
            "password": "123456"
        })
        assert response.status_code == 422


class TestUserLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, client: TestClient):
        """Test successful user login."""
        # First register a user
        client.post("/api/v1/auth/register", json={
            "username": "loginuser",
            "password": "loginpass123"
        })
        
        # Then login
        response = client.post("/api/v1/auth/login", json={
            "username": "loginuser",
            "password": "loginpass123"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["user"]["username"] == "loginuser"
    
    def test_login_invalid_username(self, client: TestClient):
        """Test login with invalid username."""
        response = client.post("/api/v1/auth/login", json={
            "username": "nonexistent",
            "password": "testpass123"
        })
        
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]
    
    def test_login_invalid_password(self, client: TestClient):
        """Test login with invalid password."""
        # Register user first
        client.post("/api/v1/auth/register", json={
            "username": "wrongpassuser",
            "password": "correctpass123"
        })
        
        # Try login with wrong password
        response = client.post("/api/v1/auth/login", json={
            "username": "wrongpassuser",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]
    
    def test_login_case_insensitive_username(self, client: TestClient):
        """Test login with different case username."""
        # Register user
        client.post("/api/v1/auth/register", json={
            "username": "caseuser",
            "password": "casepass123"
        })
        
        # Login with uppercase username
        response = client.post("/api/v1/auth/login", json={
            "username": "CASEUSER",
            "password": "casepass123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["username"] == "caseuser"


class TestUserLogout:
    """Test user logout endpoint."""
    
    def test_logout_success(self, client: TestClient):
        """Test successful user logout."""
        # Register and login to get token
        register_response = client.post("/api/v1/auth/register", json={
            "username": "logoutuser",
            "password": "logoutpass123"
        })
        token = register_response.json()["access_token"]
        
        # Logout
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully logged out"
    
    def test_logout_invalid_token(self, client: TestClient):
        """Test logout with invalid token."""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]
    
    def test_logout_missing_token(self, client: TestClient):
        """Test logout without token."""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == 403


class TestCurrentUser:
    """Test current user information endpoint."""
    
    def test_get_current_user_success(self, client: TestClient):
        """Test getting current user information."""
        # Register user to get token
        register_response = client.post("/api/v1/auth/register", json={
            "username": "meuser",
            "password": "mepass123"
        })
        token = register_response.json()["access_token"]
        
        # Get current user info
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["username"] == "meuser"
        assert data["is_admin"] is False
        assert data["is_active"] is True
        assert "created_at" in data
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_get_current_user_missing_token(self, client: TestClient):
        """Test getting current user without token."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 403


class TestTokenRefresh:
    """Test token refresh endpoint."""
    
    def test_refresh_token_success(self, client: TestClient):
        """Test successful token refresh."""
        # Register user to get token
        register_response = client.post("/api/v1/auth/register", json={
            "username": "refreshuser",
            "password": "refreshpass123"
        })
        original_token = register_response.json()["access_token"]
        
        # Refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {original_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["user"]["username"] == "refreshuser"
        assert data["access_token"] != original_token  # New token should be different
    
    def test_refresh_token_invalid_token(self, client: TestClient):
        """Test token refresh with invalid token."""
        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
        assert "Invalid or expired token" in response.json()["detail"]
    
    def test_refresh_token_missing_token(self, client: TestClient):
        """Test token refresh without token."""
        response = client.post("/api/v1/auth/refresh")
        
        assert response.status_code == 403


class TestPasswordChange:
    """Test password change endpoint."""
    
    def test_change_password_success(self, client: TestClient):
        """Test successful password change."""
        # Register user
        register_response = client.post("/api/v1/auth/register", json={
            "username": "changeuser",
            "password": "oldpass123"
        })
        token = register_response.json()["access_token"]
        
        # Change password
        response = client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "old_password": "oldpass123",
                "new_password": "newpass456"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password changed successfully"
        
        # Verify old password no longer works
        login_response = client.post("/api/v1/auth/login", json={
            "username": "changeuser",
            "password": "oldpass123"
        })
        assert login_response.status_code == 401
        
        # Verify new password works
        login_response = client.post("/api/v1/auth/login", json={
            "username": "changeuser",
            "password": "newpass456"
        })
        assert login_response.status_code == 200
    
    def test_change_password_wrong_old_password(self, client: TestClient):
        """Test password change with wrong old password."""
        # Register user
        register_response = client.post("/api/v1/auth/register", json={
            "username": "wrongolduser",
            "password": "correctpass123"
        })
        token = register_response.json()["access_token"]
        
        # Try to change with wrong old password
        response = client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "old_password": "wrongpassword",
                "new_password": "newpass456"
            }
        )
        
        assert response.status_code == 401
        assert "Current password is incorrect" in response.json()["detail"]
    
    def test_change_password_invalid_new_password(self, client: TestClient):
        """Test password change with invalid new password."""
        # Register user
        register_response = client.post("/api/v1/auth/register", json={
            "username": "invalidnewuser",
            "password": "validpass123"
        })
        token = register_response.json()["access_token"]
        
        # Too short password
        response = client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "old_password": "validpass123",
                "new_password": "short"
            }
        )
        assert response.status_code == 422
        
        # Password without numbers
        response = client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "old_password": "validpass123",
                "new_password": "onlyletters"
            }
        )
        assert response.status_code == 422
    
    def test_change_password_invalid_token(self, client: TestClient):
        """Test password change with invalid token."""
        response = client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": "Bearer invalid_token"},
            json={
                "old_password": "testpass123",
                "new_password": "newpass456"
            }
        )
        
        assert response.status_code == 401


class TestAuthenticationFlow:
    """Test complete authentication flow."""
    
    def test_complete_auth_flow(self, client: TestClient):
        """Test complete authentication flow from registration to logout."""
        # 1. Register new user
        register_response = client.post("/api/v1/auth/register", json={
            "username": "flowuser",
            "password": "flowpass123"
        })
        assert register_response.status_code == 201
        register_token = register_response.json()["access_token"]
        
        # 2. Get user info with registration token
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {register_token}"}
        )
        assert me_response.status_code == 200
        assert me_response.json()["username"] == "flowuser"
        
        # 3. Login with credentials
        login_response = client.post("/api/v1/auth/login", json={
            "username": "flowuser",
            "password": "flowpass123"
        })
        assert login_response.status_code == 200
        login_token = login_response.json()["access_token"]
        
        # 4. Refresh token
        refresh_response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {login_token}"}
        )
        assert refresh_response.status_code == 200
        refresh_token = refresh_response.json()["access_token"]
        
        # 5. Change password
        change_response = client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {refresh_token}"},
            json={
                "old_password": "flowpass123",
                "new_password": "newflowpass456"
            }
        )
        assert change_response.status_code == 200
        
        # 6. Login with new password
        new_login_response = client.post("/api/v1/auth/login", json={
            "username": "flowuser",
            "password": "newflowpass456"
        })
        assert new_login_response.status_code == 200
        final_token = new_login_response.json()["access_token"]
        
        # 7. Logout
        logout_response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {final_token}"}
        )
        assert logout_response.status_code == 200
        assert logout_response.json()["message"] == "Successfully logged out"


if __name__ == "__main__":
    pytest.main([__file__])
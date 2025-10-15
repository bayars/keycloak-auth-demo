"""
Unit tests for API endpoints
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import httpx

from app.main import app
from app.models import LoginRequest, ChangePasswordRequest
from app.auth import get_current_user, require_admin, decode_token


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client"""
    mock_client = AsyncMock()
    mock_client.post = AsyncMock()
    mock_client.get = AsyncMock()
    mock_client.put = AsyncMock()
    return mock_client


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    @pytest.mark.unit
    def test_health_check(self, client):
        """Test health check endpoint returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestLoginEndpoint:
    """Test login endpoint"""
    
    @pytest.mark.unit
    @patch('app.main.httpx.AsyncClient')
    @patch('app.main.get_admin_token')
    @patch('app.main.decode_token')
    def test_login_success(self, mock_decode_token, mock_get_admin_token, mock_httpx_client, client):
        """Test successful login"""
        # Setup mocks
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "refresh_token",
            "expires_in": 300
        }
        
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.get.return_value = Mock(status_code=200, json=lambda: {"requiredActions": []})
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        mock_decode_token.return_value = {
            "sub": "user123",
            "realm_access": {"roles": ["admin"]}
        }
        mock_get_admin_token.return_value = "admin_token"
        
        # Test login
        response = client.post("/api/login", json={"username": "admin", "password": "admin"})
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["roles"] == ["admin"]
        assert data["must_change_password"] is False
    
    @patch('app.main.httpx.AsyncClient')
    def test_login_invalid_credentials(self, mock_httpx_client, client):
        """Test login with invalid credentials"""
        # Setup mock for invalid credentials
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": "invalid_grant",
            "error_description": "Invalid user credentials"
        }
        
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Test login
        response = client.post("/api/login", json={"username": "admin", "password": "wrong"})
        
        assert response.status_code == 401
        assert "Invalid user credentials" in response.json()["error"]
    
    @patch('app.main.httpx.AsyncClient')
    def test_login_password_change_required(self, mock_httpx_client, client):
        """Test login when password change is required"""
        # Setup mock for password change required
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": "invalid_grant",
            "error_description": "Account is not fully set up"
        }
        
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Test login
        response = client.post("/api/login", json={"username": "admin", "password": "admin"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["must_change_password"] is True
        assert data["access_token"] == ""
    
    @patch('app.main.httpx.AsyncClient')
    def test_login_keycloak_unavailable(self, mock_httpx_client, client):
        """Test login when Keycloak is unavailable"""
        # Setup mock for connection error
        mock_httpx_client.side_effect = httpx.ConnectError("Connection failed")
        
        # Test login
        response = client.post("/api/login", json={"username": "admin", "password": "admin"})
        
        assert response.status_code == 503
        assert "Keycloak service unavailable" in response.json()["error"]


class TestChangePasswordEndpoint:
    """Test change password endpoint"""
    
    @patch('app.main.httpx.AsyncClient')
    @patch('app.main.get_admin_token')
    def test_change_password_success(self, mock_get_admin_token, mock_httpx_client, client):
        """Test successful password change"""
        # Setup mocks
        mock_get_admin_token.return_value = "admin_token"
        
        # Mock users list response
        users_response = Mock()
        users_response.status_code = 200
        users_response.json.return_value = [{"id": "user123", "username": "admin"}]
        
        # Mock user details response
        user_response = Mock()
        user_response.status_code = 200
        user_response.json.return_value = {"requiredActions": ["UPDATE_PASSWORD"]}
        
        # Mock password update response
        password_response = Mock()
        password_response.status_code = 204
        
        # Mock required actions update response
        actions_response = Mock()
        actions_response.status_code = 204
        
        mock_client_instance = Mock()
        mock_client_instance.get.side_effect = [users_response, user_response]
        mock_client_instance.put.side_effect = [password_response, actions_response]
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Test password change
        response = client.post("/api/change-password", json={
            "username": "admin",
            "old_password": "admin",
            "new_password": "newpass123",
            "confirm_password": "newpass123"
        })
        
        assert response.status_code == 200
        assert response.json() == {"message": "Password changed successfully"}
    
    @patch('app.main.httpx.AsyncClient')
    @patch('app.main.get_admin_token')
    def test_change_password_user_not_found(self, mock_get_admin_token, mock_httpx_client, client):
        """Test password change with non-existent user"""
        # Setup mocks
        mock_get_admin_token.return_value = "admin_token"
        
        users_response = Mock()
        users_response.status_code = 200
        users_response.json.return_value = []  # No users found
        
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = users_response
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Test password change
        response = client.post("/api/change-password", json={
            "username": "nonexistent",
            "old_password": "oldpass",
            "new_password": "newpass123",
            "confirm_password": "newpass123"
        })
        
        assert response.status_code == 404
        assert "User not found" in response.json()["error"]


class TestUserInfoEndpoint:
    """Test user info endpoint"""
    
    @patch('app.main.get_current_user')
    def test_get_user_info_success(self, mock_get_current_user, client):
        """Test successful user info retrieval"""
        # Setup mock user data
        mock_user = {
            "preferred_username": "admin",
            "email": "admin@example.com",
            "given_name": "Admin",
            "family_name": "User",
            "realm_access": {"roles": ["admin", "user"]}
        }
        mock_get_current_user.return_value = mock_user
        
        # Test user info
        response = client.get("/api/user/me", headers={"Authorization": "Bearer test_token"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["email"] == "admin@example.com"
        assert data["roles"] == ["admin", "user"]
        assert data["first_name"] == "Admin"
        assert data["last_name"] == "User"
    
    def test_get_user_info_no_token(self, client):
        """Test user info without token"""
        response = client.get("/api/user/me")
        assert response.status_code == 403


class TestDashboardEndpoint:
    """Test dashboard endpoint"""
    
    @patch('app.main.get_current_user')
    def test_dashboard_success(self, mock_get_current_user, client):
        """Test successful dashboard access"""
        # Setup mock user data
        mock_user = {
            "preferred_username": "admin",
            "roles": ["admin"]
        }
        mock_get_current_user.return_value = mock_user
        
        # Test dashboard
        response = client.get("/api/dashboard", headers={"Authorization": "Bearer test_token"})
        
        assert response.status_code == 200
        data = response.json()
        assert "Welcome to the dashboard" in data["message"]
        assert data["user"] == "admin"
        assert data["roles"] == ["admin"]


class TestAdminUsersEndpoint:
    """Test admin users endpoint"""
    
    @patch('app.main.httpx.AsyncClient')
    @patch('app.main.get_admin_token')
    @patch('app.main.require_admin')
    def test_list_users_success(self, mock_require_admin, mock_get_admin_token, mock_httpx_client, client):
        """Test successful users list retrieval"""
        # Setup mocks
        mock_require_admin.return_value = {"preferred_username": "admin"}
        mock_get_admin_token.return_value = "admin_token"
        
        users_response = Mock()
        users_response.status_code = 200
        users_response.json.return_value = [
            {"id": "user1", "username": "admin", "email": "admin@test.com"},
            {"id": "user2", "username": "testuser", "email": "test@test.com"}
        ]
        
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = users_response
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Test users list
        response = client.get("/api/admin/users", headers={"Authorization": "Bearer admin_token"})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["username"] == "admin"
        assert data[1]["username"] == "testuser"
    
    @patch('app.main.require_admin')
    def test_list_users_non_admin(self, mock_require_admin, client):
        """Test users list access by non-admin user"""
        # Setup mock to raise HTTPException for non-admin
        mock_require_admin.side_effect = HTTPException(status_code=403, detail="Admin access required")
        
        # Test users list
        response = client.get("/api/admin/users", headers={"Authorization": "Bearer user_token"})
        
        assert response.status_code == 403
        assert "Admin access required" in response.json()["error"]


class TestAuthModule:
    """Test authentication module functions"""
    
    @patch('app.auth.jwt.get_unverified_claims')
    def test_decode_token_success(self, mock_get_unverified_claims):
        """Test successful token decoding"""
        mock_payload = {"sub": "user123", "realm_access": {"roles": ["admin"]}}
        mock_get_unverified_claims.return_value = mock_payload
        
        result = decode_token("test_token")
        assert result == mock_payload
    
    @patch('app.auth.jwt.get_unverified_claims')
    def test_decode_token_invalid(self, mock_get_unverified_claims):
        """Test token decoding with invalid token"""
        mock_get_unverified_claims.side_effect = Exception("Invalid token")
        
        with pytest.raises(HTTPException) as exc_info:
            decode_token("invalid_token")
        
        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)
    
    @patch('app.auth.decode_token')
    def test_require_admin_success(self, mock_decode_token):
        """Test require_admin with admin role"""
        mock_decode_token.return_value = {
            "realm_access": {"roles": ["admin", "user"]}
        }
        
        result = require_admin(Mock(credentials="admin_token"))
        assert result["realm_access"]["roles"] == ["admin", "user"]
    
    @patch('app.auth.decode_token')
    def test_require_admin_failure(self, mock_decode_token):
        """Test require_admin without admin role"""
        mock_decode_token.return_value = {
            "realm_access": {"roles": ["user"]}
        }
        
        with pytest.raises(HTTPException) as exc_info:
            require_admin(Mock(credentials="user_token"))
        
        assert exc_info.value.status_code == 403
        assert "Admin access required" in str(exc_info.value.detail)

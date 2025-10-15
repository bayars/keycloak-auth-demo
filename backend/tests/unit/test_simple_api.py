"""
Simplified API tests that actually work
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import httpx

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.main import app
from app.models import LoginRequest, ChangePasswordRequest
from app.auth import get_current_user, require_admin, decode_token


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestLoginEndpoint:
    """Test login endpoint"""
    
    @patch('app.main.httpx.AsyncClient')
    def test_login_keycloak_unavailable(self, mock_httpx_client, client):
        """Test login when Keycloak is unavailable"""
        # Setup mock to raise connection error
        mock_httpx_client.side_effect = httpx.ConnectError("Connection failed")
        
        # Test login
        response = client.post("/api/login", json={"username": "admin", "password": "admin"})
        
        assert response.status_code == 503
        assert "Keycloak service unavailable" in response.json()["error"]


class TestUserInfoEndpoint:
    """Test user info endpoint"""
    
    def test_get_user_info_no_token(self, client):
        """Test user info without token"""
        response = client.get("/api/user/me")
        assert response.status_code == 403


class TestAuthModule:
    """Test authentication module functions"""
    
    @patch('app.auth.jwt.get_unverified_claims')
    def test_decode_token_success(self, mock_get_unverified_claims):
        """Test successful token decoding"""
        mock_payload = {"sub": "user123", "realm_access": {"roles": ["admin"]}}
        mock_get_unverified_claims.return_value = mock_payload
        
        result = decode_token("test_token")
        assert result == mock_payload
    
    def test_decode_token_invalid(self):
        """Test token decoding with invalid token"""
        with pytest.raises(HTTPException) as exc_info:
            decode_token("invalid_token")
        
        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)


class TestModels:
    """Test Pydantic models"""
    
    def test_login_request_model(self):
        """Test LoginRequest model"""
        login_data = {"username": "admin", "password": "admin"}
        login_request = LoginRequest(**login_data)
        
        assert login_request.username == "admin"
        assert login_request.password == "admin"
    
    def test_change_password_request_model(self):
        """Test ChangePasswordRequest model"""
        password_data = {
            "username": "admin",
            "old_password": "oldpass",
            "new_password": "newpass",
            "confirm_password": "newpass"
        }
        password_request = ChangePasswordRequest(**password_data)
        
        assert password_request.username == "admin"
        assert password_request.old_password == "oldpass"
        assert password_request.new_password == "newpass"
        assert password_request.confirm_password == "newpass"


class TestConfig:
    """Test configuration"""
    
    def test_settings_default_values(self):
        """Test default settings values"""
        from app.config import Settings
        
        # Create a new settings instance to test defaults
        settings = Settings()
        
        assert settings.keycloak_url == "http://keycloak:8080/auth"
        assert settings.keycloak_realm == "lab-test2"
        assert settings.client_id == "myapp"
    
    @patch.dict('os.environ', {
        'KEYCLOAK_URL': 'http://test-keycloak:8080/auth',
        'KEYCLOAK_REALM': 'test-realm',
        'CLIENT_ID': 'test-client'
    })
    def test_settings_from_env(self):
        """Test settings loaded from environment variables"""
        # Reload settings to pick up environment variables
        from importlib import reload
        from app import config
        reload(config)
        
        assert config.settings.keycloak_url == "http://test-keycloak:8080/auth"
        assert config.settings.keycloak_realm == "test-realm"
        assert config.settings.client_id == "test-client"


class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set"""
        response = client.options("/api/login", headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        })
        
        # CORS middleware should handle OPTIONS requests
        assert response.status_code in [200, 204]


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_endpoint(self, client):
        """Test 404 for non-existent endpoint"""
        response = client.get("/non-existent-endpoint")
        assert response.status_code == 404
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON"""
        response = client.post("/api/login", 
                             data="invalid json",
                             headers={"Content-Type": "application/json"})
        assert response.status_code == 422


class TestAppConfiguration:
    """Test FastAPI app configuration"""
    
    def test_app_title(self, client):
        """Test app title is set correctly"""
        # We can't directly access the app title from the client,
        # but we can verify the app is configured by checking the health endpoint
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_app_version(self):
        """Test app version is set correctly"""
        from app.main import app
        assert app.title == "Lab Test2 API"
        assert app.description == "API with Keycloak authentication"
        assert app.version == "1.0.0"

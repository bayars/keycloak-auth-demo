"""
Integration tests for API with Keycloak
"""
import pytest
import asyncio
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
import httpx

from app.main import app
from app.config import Settings


@pytest.fixture
def client():
    """Test client for integration tests"""
    return TestClient(app)


@pytest.fixture
def test_settings():
    """Test settings for integration tests"""
    return Settings(
        keycloak_url="http://test-keycloak:8080/auth",
        keycloak_realm="test-realm",
        client_id="test-client"
    )


class TestKeycloakIntegration:
    """Integration tests with Keycloak"""
    
    @patch('app.main.settings')
    @patch('app.main.httpx.AsyncClient')
    def test_full_login_flow(self, mock_httpx_client, mock_settings, client):
        """Test complete login flow with Keycloak"""
        # Setup settings
        mock_settings.keycloak_url = "http://test-keycloak:8080/auth"
        mock_settings.keycloak_realm = "test-realm"
        mock_settings.client_id = "test-client"
        
        # Mock Keycloak token response
        token_response = Mock()
        token_response.status_code = 200
        token_response.json.return_value = {
            "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test",
            "refresh_token": "refresh_token",
            "expires_in": 300,
            "token_type": "Bearer"
        }
        
        # Mock admin token response
        admin_token_response = Mock()
        admin_token_response.status_code = 200
        admin_token_response.json.return_value = {
            "access_token": "admin_token"
        }
        
        # Mock user details response
        user_response = Mock()
        user_response.status_code = 200
        user_response.json.return_value = {
            "requiredActions": []
        }
        
        # Setup httpx client mocks
        mock_client_instance = Mock()
        mock_client_instance.post.side_effect = [token_response, admin_token_response]
        mock_client_instance.get.return_value = user_response
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Test login
        response = client.post("/api/login", json={
            "username": "admin",
            "password": "admin"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["must_change_password"] is False
    
    @patch('app.main.settings')
    @patch('app.main.httpx.AsyncClient')
    def test_password_change_flow(self, mock_httpx_client, mock_settings, client):
        """Test complete password change flow"""
        # Setup settings
        mock_settings.keycloak_url = "http://test-keycloak:8080/auth"
        mock_settings.keycloak_realm = "test-realm"
        mock_settings.client_id = "test-client"
        
        # Mock admin token response
        admin_token_response = Mock()
        admin_token_response.status_code = 200
        admin_token_response.json.return_value = {
            "access_token": "admin_token"
        }
        
        # Mock users list response
        users_response = Mock()
        users_response.status_code = 200
        users_response.json.return_value = [{
            "id": "user123",
            "username": "admin"
        }]
        
        # Mock user details response
        user_response = Mock()
        user_response.status_code = 200
        user_response.json.return_value = {
            "requiredActions": ["UPDATE_PASSWORD"]
        }
        
        # Mock password update responses
        password_response = Mock()
        password_response.status_code = 204
        
        actions_response = Mock()
        actions_response.status_code = 204
        
        # Setup httpx client mocks
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = admin_token_response
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
    
    @patch('app.main.settings')
    @patch('app.main.httpx.AsyncClient')
    def test_admin_users_list_flow(self, mock_httpx_client, mock_settings, client):
        """Test admin users list flow"""
        # Setup settings
        mock_settings.keycloak_url = "http://test-keycloak:8080/auth"
        mock_settings.keycloak_realm = "test-realm"
        
        # Mock admin token response
        admin_token_response = Mock()
        admin_token_response.status_code = 200
        admin_token_response.json.return_value = {
            "access_token": "admin_token"
        }
        
        # Mock users list response
        users_response = Mock()
        users_response.status_code = 200
        users_response.json.return_value = [
            {
                "id": "user1",
                "username": "admin",
                "email": "admin@test.com",
                "firstName": "Admin",
                "lastName": "User",
                "enabled": True
            },
            {
                "id": "user2",
                "username": "testuser",
                "email": "test@test.com",
                "firstName": "Test",
                "lastName": "User",
                "enabled": True
            }
        ]
        
        # Setup httpx client mocks
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = admin_token_response
        mock_client_instance.get.return_value = users_response
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Mock JWT token for admin access
        with patch('app.main.decode_token') as mock_decode:
            mock_decode.return_value = {
                "realm_access": {"roles": ["admin"]}
            }
            
            # Test admin users list
            response = client.get("/api/admin/users", headers={
                "Authorization": "Bearer admin_token"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["username"] == "admin"
            assert data[1]["username"] == "testuser"


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @patch('app.main.httpx.AsyncClient')
    def test_keycloak_connection_error(self, mock_httpx_client, client):
        """Test handling of Keycloak connection errors"""
        # Setup mock to raise connection error
        mock_httpx_client.side_effect = httpx.ConnectError("Connection failed")
        
        # Test login with connection error
        response = client.post("/api/login", json={
            "username": "admin",
            "password": "admin"
        })
        
        assert response.status_code == 503
        assert "Keycloak service unavailable" in response.json()["error"]
    
    @patch('app.main.httpx.AsyncClient')
    def test_keycloak_timeout_error(self, mock_httpx_client, client):
        """Test handling of Keycloak timeout errors"""
        # Setup mock to raise timeout error
        mock_httpx_client.side_effect = httpx.TimeoutException("Request timeout")
        
        # Test login with timeout error
        response = client.post("/api/login", json={
            "username": "admin",
            "password": "admin"
        })
        
        assert response.status_code == 503
        assert "Keycloak service unavailable" in response.json()["error"]
    
    @patch('app.main.httpx.AsyncClient')
    @patch('app.main.get_admin_token')
    def test_admin_token_failure(self, mock_get_admin_token, mock_httpx_client, client):
        """Test handling of admin token failure"""
        # Setup mock to return None for admin token
        mock_get_admin_token.return_value = None
        
        # Mock users list response
        users_response = Mock()
        users_response.status_code = 200
        users_response.json.return_value = []
        
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = users_response
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Mock JWT token for admin access
        with patch('app.main.decode_token') as mock_decode:
            mock_decode.return_value = {
                "realm_access": {"roles": ["admin"]}
            }
            
            # Test admin users list with failed admin token
            response = client.get("/api/admin/users", headers={
                "Authorization": "Bearer admin_token"
            })
            
            assert response.status_code == 500
            assert "Failed to fetch users" in response.json()["error"]


class TestCORSIntegration:
    """Test CORS integration"""
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set"""
        response = client.options("/api/login", headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        })
        
        # CORS middleware should handle OPTIONS requests
        assert response.status_code in [200, 204]


class TestJWTValidation:
    """Test JWT validation integration"""
    
    @patch('app.main.decode_token')
    def test_jwt_validation_success(self, mock_decode_token, client):
        """Test successful JWT validation"""
        # Setup mock token payload
        mock_payload = {
            "sub": "user123",
            "preferred_username": "admin",
            "realm_access": {"roles": ["admin"]}
        }
        mock_decode_token.return_value = mock_payload
        
        # Test protected endpoint
        response = client.get("/api/user/me", headers={
            "Authorization": "Bearer valid_token"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
    
    @patch('app.main.decode_token')
    def test_jwt_validation_failure(self, mock_decode_token, client):
        """Test JWT validation failure"""
        # Setup mock to raise exception
        mock_decode_token.side_effect = Exception("Invalid token")
        
        # Test protected endpoint
        response = client.get("/api/user/me", headers={
            "Authorization": "Bearer invalid_token"
        })
        
        assert response.status_code == 401
        assert "Invalid token" in response.json()["error"]


class TestConcurrentRequests:
    """Test concurrent request handling"""
    
    @patch('app.main.httpx.AsyncClient')
    def test_concurrent_logins(self, mock_httpx_client, client):
        """Test handling of concurrent login requests"""
        # Setup mock responses
        token_response = Mock()
        token_response.status_code = 200
        token_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "refresh_token",
            "expires_in": 300
        }
        
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = token_response
        mock_client_instance.get.return_value = Mock(status_code=200, json=lambda: {"requiredActions": []})
        mock_httpx_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Mock other dependencies
        with patch('app.main.get_admin_token') as mock_admin_token, \
             patch('app.main.decode_token') as mock_decode_token:
            
            mock_admin_token.return_value = "admin_token"
            mock_decode_token.return_value = {
                "sub": "user123",
                "realm_access": {"roles": ["admin"]}
            }
            
            # Test multiple concurrent requests
            import threading
            import time
            
            results = []
            
            def make_request():
                response = client.post("/api/login", json={
                    "username": "admin",
                    "password": "admin"
                })
                results.append(response.status_code)
            
            # Create multiple threads
            threads = []
            for _ in range(5):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # All requests should succeed
            assert all(status == 200 for status in results)
            assert len(results) == 5

"""
Simple integration tests for API
"""
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
import httpx
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.main import app


@pytest.fixture
def client():
    """Test client for integration tests"""
    return TestClient(app)


class TestAPIIntegration:
    """Integration tests for API endpoints"""
    
    def test_health_endpoint_integration(self, client):
        """Test health endpoint integration"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_cors_integration(self, client):
        """Test CORS integration"""
        response = client.options("/api/login", headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        })
        assert response.status_code in [200, 204]
    
    def test_error_handling_integration(self, client):
        """Test error handling integration"""
        # Test 404
        response = client.get("/non-existent")
        assert response.status_code == 404
        
        # Test invalid JSON
        response = client.post("/api/login", 
                             data="invalid json",
                             headers={"Content-Type": "application/json"})
        assert response.status_code == 422
    
    def test_authentication_flow_integration(self, client):
        """Test authentication flow integration"""
        # Test protected endpoint without token
        response = client.get("/api/user/me")
        assert response.status_code == 403
        
        # Test dashboard without token
        response = client.get("/api/dashboard")
        assert response.status_code == 403
        
        # Test admin endpoint without token
        response = client.get("/api/admin/users")
        assert response.status_code == 403


class TestAppIntegration:
    """Test app integration"""
    
    def test_app_startup(self, client):
        """Test app starts up correctly"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_app_configuration(self):
        """Test app configuration"""
        from app.main import app
        
        assert app.title == "Lab Test2 API"
        assert app.description == "API with Keycloak authentication"
        assert app.version == "1.0.0"
    
    def test_middleware_integration(self, client):
        """Test middleware integration"""
        # Test CORS middleware
        response = client.options("/api/login", headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        })
        assert response.status_code in [200, 204]
        
        # Test exception handling middleware
        response = client.get("/non-existent")
        assert response.status_code == 404


class TestModelIntegration:
    """Test model integration"""
    
    def test_login_model_integration(self, client):
        """Test login model integration"""
        # Test with valid data
        response = client.post("/api/login", json={
            "username": "admin",
            "password": "admin"
        })
        # Should fail due to Keycloak being unavailable, but model validation should pass
        assert response.status_code in [503, 422]
    
    def test_change_password_model_integration(self, client):
        """Test change password model integration"""
        # Test with valid data
        response = client.post("/api/change-password", json={
            "username": "admin",
            "old_password": "oldpass",
            "new_password": "newpass",
            "confirm_password": "newpass"
        })
        # Should fail due to Keycloak being unavailable, but model validation should pass
        assert response.status_code in [503, 422]


class TestErrorIntegration:
    """Test error integration"""
    
    def test_http_exception_handling(self, client):
        """Test HTTP exception handling"""
        # Test 404 handling
        response = client.get("/non-existent-endpoint")
        assert response.status_code == 404
        
        # Test 422 handling (validation error)
        response = client.post("/api/login", json={
            "invalid": "data"
        })
        assert response.status_code == 422
    
    def test_service_unavailable_handling(self, client):
        """Test service unavailable handling"""
        # This will trigger the Keycloak unavailable error
        response = client.post("/api/login", json={
            "username": "admin",
            "password": "admin"
        })
        # Should return 503 due to Keycloak being unavailable
        assert response.status_code == 503
        assert "Keycloak service unavailable" in response.json()["error"]

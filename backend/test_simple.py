"""
Ultra-simple test for GitHub Actions
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import_app():
    """Test that we can import the app module"""
    try:
        from app.main import app
        assert app is not None
        print("✅ Successfully imported app")
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        raise

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
        print("✅ Health endpoint working")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        raise

def test_login_endpoint_error():
    """Test that login endpoint returns expected error (no Keycloak)"""
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.post("/api/login", json={"username": "test", "password": "test"})
        
        # Should return 503 due to Keycloak being unavailable
        assert response.status_code == 503
        assert "Keycloak service unavailable" in response.json()["error"]
        print("✅ Login endpoint returns expected error")
    except Exception as e:
        print(f"❌ Login endpoint test failed: {e}")
        raise

def test_user_info_requires_auth():
    """Test that user info endpoint requires authentication"""
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/api/user/me")
        
        # Should return 403 due to missing authentication
        assert response.status_code == 403
        print("✅ User info endpoint requires authentication")
    except Exception as e:
        print(f"❌ User info endpoint test failed: {e}")
        raise

if __name__ == "__main__":
    print("Running simple API tests...")
    test_import_app()
    test_health_endpoint()
    test_login_endpoint_error()
    test_user_info_requires_auth()
    print("✅ All tests passed!")

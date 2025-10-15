"""
Test configuration and conftest.py for pytest
"""
import pytest
import asyncio
from unittest.mock import patch, Mock
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app"))

from app.config import Settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Test settings configuration"""
    return Settings(
        keycloak_url="http://test-keycloak:8080/auth",
        keycloak_realm="test-realm",
        client_id="test-client"
    )


@pytest.fixture
def mock_env():
    """Mock environment variables for testing"""
    env_vars = {
        "KEYCLOAK_URL": "http://test-keycloak:8080/auth",
        "KEYCLOAK_REALM": "test-realm",
        "CLIENT_ID": "test-client"
    }
    
    with patch.dict(os.environ, env_vars, clear=True):
        yield env_vars


@pytest.fixture
def mock_keycloak_responses():
    """Mock Keycloak API responses"""
    return {
        "successful_token": {
            "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test",
            "refresh_token": "refresh_token",
            "expires_in": 300,
            "token_type": "Bearer"
        },
        "invalid_credentials": {
            "error": "invalid_grant",
            "error_description": "Invalid user credentials"
        },
        "password_change_required": {
            "error": "invalid_grant",
            "error_description": "Account is not fully set up"
        },
        "admin_token": {
            "access_token": "admin_token_here",
            "expires_in": 300
        },
        "users_list": [
            {
                "id": "user1",
                "username": "admin",
                "email": "admin@test.com",
                "firstName": "Admin",
                "lastName": "User",
                "enabled": True,
                "emailVerified": True,
                "requiredActions": []
            },
            {
                "id": "user2",
                "username": "testuser",
                "email": "test@test.com",
                "firstName": "Test",
                "lastName": "User",
                "enabled": True,
                "emailVerified": True,
                "requiredActions": []
            }
        ],
        "user_with_password_change": {
            "id": "user1",
            "username": "admin",
            "email": "admin@test.com",
            "firstName": "Admin",
            "lastName": "User",
            "enabled": True,
            "emailVerified": True,
            "requiredActions": ["UPDATE_PASSWORD"]
        }
    }


@pytest.fixture
def mock_jwt_payloads():
    """Mock JWT payloads for testing"""
    return {
        "admin_user": {
            "sub": "user1",
            "preferred_username": "admin",
            "email": "admin@test.com",
            "given_name": "Admin",
            "family_name": "User",
            "realm_access": {
                "roles": ["admin", "user"]
            },
            "exp": 9999999999,
            "iat": 1234567800
        },
        "regular_user": {
            "sub": "user2",
            "preferred_username": "testuser",
            "email": "test@test.com",
            "given_name": "Test",
            "family_name": "User",
            "realm_access": {
                "roles": ["user"]
            },
            "exp": 9999999999,
            "iat": 1234567800
        }
    }


@pytest.fixture
def mock_httpx_responses():
    """Mock httpx responses for testing"""
    def create_mock_response(status_code, json_data=None, text=None):
        response = Mock()
        response.status_code = status_code
        if json_data:
            response.json.return_value = json_data
        if text:
            response.text = text
        return response
    
    return create_mock_response


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment for each test"""
    # This fixture runs automatically for each test
    with patch('app.config.settings') as mock_settings:
        mock_settings.keycloak_url = "http://test-keycloak:8080/auth"
        mock_settings.keycloak_realm = "test-realm"
        mock_settings.client_id = "test-client"
        yield


# Pytest markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow

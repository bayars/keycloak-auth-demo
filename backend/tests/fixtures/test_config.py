"""
Test configuration and utilities
"""
import pytest
import os
from unittest.mock import patch
from app.config import Settings


@pytest.fixture
def test_settings():
    """Test settings configuration"""
    return Settings(
        keycloak_url="http://test-keycloak:8080/auth",
        keycloak_realm="test-realm",
        client_id="test-client"
    )


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    env_vars = {
        "KEYCLOAK_URL": "http://test-keycloak:8080/auth",
        "KEYCLOAK_REALM": "test-realm",
        "CLIENT_ID": "test-client"
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def mock_keycloak_responses():
    """Mock various Keycloak API responses"""
    return {
        "token_success": {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "expires_in": 300,
            "token_type": "Bearer"
        },
        "token_error": {
            "error": "invalid_grant",
            "error_description": "Invalid user credentials"
        },
        "password_change_required": {
            "error": "invalid_grant",
            "error_description": "Account is not fully set up"
        },
        "admin_token": {
            "access_token": "mock_admin_token",
            "expires_in": 300
        },
        "users_list": [
            {
                "id": "user1",
                "username": "admin",
                "email": "admin@test.com",
                "enabled": True
            }
        ],
        "user_details": {
            "id": "user1",
            "username": "admin",
            "email": "admin@test.com",
            "requiredActions": ["UPDATE_PASSWORD"]
        }
    }


@pytest.fixture
def mock_jwt_decode():
    """Mock JWT decode function"""
    def mock_decode(token):
        if token == "mock_access_token":
            return {
                "sub": "user1",
                "preferred_username": "admin",
                "realm_access": {"roles": ["admin"]},
                "exp": 9999999999
            }
        elif token == "mock_user_token":
            return {
                "sub": "user2",
                "preferred_username": "testuser",
                "realm_access": {"roles": ["user"]},
                "exp": 9999999999
            }
        else:
            raise Exception("Invalid token")
    
    return mock_decode

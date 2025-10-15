"""
Test fixtures and mock data for API testing
"""
import pytest
from unittest.mock import Mock
from typing import Dict, Any
import json


@pytest.fixture
def mock_keycloak_token_response():
    """Mock successful Keycloak token response"""
    return {
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.EkN-DOsnsuRjRO6BxXemmJDm3HbxrbRzXglbN2S4sOkopdU4IsDxTI8jO19W_A4K8ZPJijNLb4KsxN508aJQ",
        "refresh_token": "refresh_token_here",
        "expires_in": 300,
        "token_type": "Bearer"
    }


@pytest.fixture
def mock_jwt_payload():
    """Mock JWT payload for testing"""
    return {
        "sub": "user123",
        "preferred_username": "admin",
        "email": "admin@example.com",
        "given_name": "Admin",
        "family_name": "User",
        "realm_access": {
            "roles": ["admin", "user"]
        },
        "exp": 1234567890,
        "iat": 1234567800
    }


@pytest.fixture
def mock_user_payload():
    """Mock user payload for testing"""
    return {
        "sub": "user456",
        "preferred_username": "testuser",
        "email": "test@example.com",
        "given_name": "Test",
        "family_name": "User",
        "realm_access": {
            "roles": ["user"]
        },
        "exp": 1234567890,
        "iat": 1234567800
    }


@pytest.fixture
def mock_keycloak_users_response():
    """Mock Keycloak users list response"""
    return [
        {
            "id": "user123",
            "username": "admin",
            "email": "admin@example.com",
            "firstName": "Admin",
            "lastName": "User",
            "enabled": True,
            "emailVerified": True,
            "requiredActions": []
        },
        {
            "id": "user456",
            "username": "testuser",
            "email": "test@example.com",
            "firstName": "Test",
            "lastName": "User",
            "enabled": True,
            "emailVerified": True,
            "requiredActions": []
        }
    ]


@pytest.fixture
def mock_keycloak_user_with_password_change():
    """Mock user with password change requirement"""
    return {
        "id": "user123",
        "username": "admin",
        "email": "admin@example.com",
        "firstName": "Admin",
        "lastName": "User",
        "enabled": True,
        "emailVerified": True,
        "requiredActions": ["UPDATE_PASSWORD"]
    }


@pytest.fixture
def mock_keycloak_error_response():
    """Mock Keycloak error response"""
    return {
        "error": "invalid_grant",
        "error_description": "Invalid user credentials"
    }


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for testing"""
    mock_client = Mock()
    mock_client.post = Mock()
    mock_client.get = Mock()
    mock_client.put = Mock()
    return mock_client


@pytest.fixture
def sample_login_request():
    """Sample login request data"""
    return {
        "username": "admin",
        "password": "admin"
    }


@pytest.fixture
def sample_change_password_request():
    """Sample change password request data"""
    return {
        "username": "admin",
        "old_password": "admin",
        "new_password": "newpassword123",
        "confirm_password": "newpassword123"
    }


@pytest.fixture
def mock_admin_token():
    """Mock admin token for Keycloak API calls"""
    return "admin_token_here"


@pytest.fixture
def mock_keycloak_public_keys():
    """Mock Keycloak public keys response"""
    return {
        "keys": [
            {
                "kty": "RSA",
                "kid": "test-key-id",
                "use": "sig",
                "alg": "RS256",
                "n": "test-modulus",
                "e": "AQAB"
            }
        ]
    }

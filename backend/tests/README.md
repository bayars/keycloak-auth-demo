# API Testing Documentation

This document describes the testing setup for the Lab Test2 API with Keycloak authentication.

## Test Structure

```
backend/
├── tests/
│   ├── unit/                    # Unit tests
│   │   └── test_api_endpoints.py
│   ├── integration/             # Integration tests
│   │   └── test_keycloak_integration.py
│   ├── fixtures/                # Test fixtures and mock data
│   │   ├── test_data.py
│   │   └── test_config.py
│   ├── conftest.py             # Pytest configuration
│   └── run_tests.py            # Test runner script
├── pyproject.toml              # Dependencies and test configuration
└── app/                        # Application code
```

## Test Categories

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual functions and endpoints in isolation
- **Scope**: Fast, focused tests with mocked dependencies
- **Coverage**: All API endpoints, authentication functions, and utility functions

### Integration Tests (`tests/integration/`)
- **Purpose**: Test complete workflows and interactions with external services
- **Scope**: Tests that verify the integration between components
- **Coverage**: Keycloak authentication flow, error handling, CORS, concurrent requests

## Test Endpoints Covered

### 1. Health Check (`/health`)
- ✅ Returns healthy status
- ✅ No authentication required

### 2. Login (`/api/login`)
- ✅ Successful login with valid credentials
- ✅ Invalid credentials handling
- ✅ Password change requirement detection
- ✅ Keycloak service unavailable handling
- ✅ Token generation and role extraction

### 3. Change Password (`/api/change-password`)
- ✅ Successful password change
- ✅ User not found handling
- ✅ Required actions management
- ✅ Password verification bypass for required actions

### 4. User Info (`/api/user/me`)
- ✅ Successful user info retrieval
- ✅ JWT token validation
- ✅ Role extraction
- ✅ No token handling

### 5. Dashboard (`/api/dashboard`)
- ✅ Authenticated access
- ✅ User information display
- ✅ Role-based access

### 6. Admin Users (`/api/admin/users`)
- ✅ Admin role requirement
- ✅ Users list retrieval
- ✅ Non-admin access denial
- ✅ Keycloak admin API integration

## Test Fixtures

### Mock Data (`fixtures/test_data.py`)
- `mock_keycloak_token_response`: Successful token response
- `mock_jwt_payload`: JWT payload for testing
- `mock_keycloak_users_response`: Users list response
- `mock_keycloak_error_response`: Error responses
- `sample_login_request`: Login request data
- `sample_change_password_request`: Password change data

### Configuration (`fixtures/test_config.py`)
- `test_settings`: Test configuration
- `mock_env_vars`: Environment variables
- `mock_keycloak_responses`: Various API responses
- `mock_jwt_decode`: JWT decoding mock

## Running Tests

### Prerequisites
```bash
cd backend
pip install -e .[test]
```

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Unit Tests Only
```bash
python -m pytest tests/unit/ -v -m unit
```

### Run Integration Tests Only
```bash
python -m pytest tests/integration/ -v -m integration
```

### Run with Coverage
```bash
python -m pytest tests/ -v --cov=app --cov-report=html
```

### Run Specific Test File
```bash
python -m pytest tests/unit/test_api_endpoints.py -v
```

### Run Specific Test Function
```bash
python -m pytest tests/unit/test_api_endpoints.py::TestLoginEndpoint::test_login_success -v
```

## Test Configuration

### Pytest Configuration (`pyproject.toml`)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=app",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow tests",
]
asyncio_mode = "auto"
```

### Test Dependencies
- `pytest>=7.4.0`: Test framework
- `pytest-asyncio>=0.21.0`: Async test support
- `pytest-mock>=3.11.0`: Mocking utilities
- `pytest-cov>=4.1.0`: Coverage reporting
- `httpx>=0.26.0`: HTTP client for testing
- `factory-boy>=3.3.0`: Test data factories
- `freezegun>=1.2.0`: Time mocking

## GitHub Actions CI/CD

### Workflows
1. **`api-tests.yml`**: Full integration tests with Keycloak service
2. **`api-tests-mocked.yml`**: Fast tests with mocked dependencies

### CI Pipeline Steps
1. **Test**: Run unit and integration tests
2. **Lint**: Code quality checks (flake8, black, isort, mypy)
3. **Security**: Security scanning (safety, bandit)
4. **Docker**: Docker image build and test

### Test Matrix
- Python 3.11
- Python 3.12
- Ubuntu Latest

## Mock Strategy

### Keycloak Integration
- **Unit Tests**: All Keycloak calls are mocked
- **Integration Tests**: Mock httpx responses to simulate Keycloak behavior
- **CI Tests**: Use mocked responses for fast execution

### JWT Token Handling
- Mock JWT payloads for different user types
- Test token validation and role extraction
- Simulate token expiration and invalid tokens

### Error Scenarios
- Network connectivity issues
- Keycloak service unavailable
- Invalid credentials
- Token expiration
- Permission denied

## Coverage Goals

- **Target**: >90% code coverage
- **Critical Paths**: Authentication, authorization, error handling
- **Exclusions**: Configuration files, main entry points

## Test Data Management

### Test Users
- **Admin User**: `admin` / `adminpass` (admin role)
- **Regular User**: `testuser` / `testpass` (user role)

### Test Scenarios
- Valid authentication flow
- Password change requirements
- Role-based access control
- Error handling and recovery
- Concurrent request handling

## Best Practices

### Test Organization
- One test class per endpoint
- Descriptive test method names
- Clear setup and teardown
- Isolated test cases

### Mocking Guidelines
- Mock external dependencies
- Use realistic test data
- Test both success and failure paths
- Verify mock interactions

### Assertions
- Test response status codes
- Verify response data structure
- Check error messages
- Validate side effects

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure app directory is in Python path
2. **Mock Failures**: Check mock setup and return values
3. **Async Issues**: Use pytest-asyncio for async tests
4. **Coverage**: Ensure all code paths are tested

### Debug Commands
```bash
# Run tests with verbose output
python -m pytest tests/ -v -s

# Run specific test with debugging
python -m pytest tests/unit/test_api_endpoints.py::TestLoginEndpoint::test_login_success -v -s --pdb

# Check test discovery
python -m pytest --collect-only tests/
```

## Future Enhancements

### Planned Improvements
- Performance testing
- Load testing with Keycloak
- End-to-end testing
- API contract testing
- Mutation testing

### Additional Test Types
- Property-based testing
- Chaos engineering tests
- Security penetration tests
- Accessibility tests

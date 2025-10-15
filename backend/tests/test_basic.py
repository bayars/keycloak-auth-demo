"""
Minimal test to verify GitHub Actions environment
"""
import pytest
import sys
import os

def test_python_version():
    """Test that we're running Python 3.11 or 3.12"""
    assert sys.version_info >= (3, 11), f"Python version {sys.version_info} is too old"

def test_working_directory():
    """Test that we're in the correct working directory"""
    assert os.path.exists("app"), "app directory not found"
    assert os.path.exists("tests"), "tests directory not found"

def test_import_path():
    """Test that we can import the app module"""
    try:
        import app.main
        assert True, "Successfully imported app.main"
    except ImportError as e:
        pytest.fail(f"Failed to import app.main: {e}")

def test_basic_functionality():
    """Test basic Python functionality"""
    assert 1 + 1 == 2, "Basic math failed"
    assert "hello" in "hello world", "String operations failed"

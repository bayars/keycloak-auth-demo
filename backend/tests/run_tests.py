"""
Test runner script for running tests locally
"""
import subprocess
import sys
import os
from pathlib import Path


def run_tests():
    """Run all tests with pytest"""
    # Change to backend directory
    backend_dir = Path(__file__).parent.parent / "backend"
    os.chdir(backend_dir)
    
    # Install test dependencies
    print("Installing test dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", ".[test]"], check=True)
    
    # Run tests
    print("Running tests...")
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-report=xml"
    ]
    
    result = subprocess.run(cmd)
    return result.returncode


def run_unit_tests():
    """Run only unit tests"""
    backend_dir = Path(__file__).parent.parent / "backend"
    os.chdir(backend_dir)
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/unit/",
        "-v",
        "--tb=short",
        "-m", "unit"
    ]
    
    result = subprocess.run(cmd)
    return result.returncode


def run_integration_tests():
    """Run only integration tests"""
    backend_dir = Path(__file__).parent.parent / "backend"
    os.chdir(backend_dir)
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/integration/",
        "-v",
        "--tb=short",
        "-m", "integration"
    ]
    
    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "unit":
            exit_code = run_unit_tests()
        elif sys.argv[1] == "integration":
            exit_code = run_integration_tests()
        else:
            print("Usage: python run_tests.py [unit|integration]")
            exit_code = 1
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)

#!/usr/bin/env python3
"""
Test runner script for GitHub Actions
"""
import sys
import os
import subprocess

def main():
    # Add the backend directory to Python path
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, backend_dir)
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Run pytest with the working test files
    test_files = [
        "tests/test_basic.py",
        "tests/unit/test_simple_api.py",
        "tests/integration/test_simple_integration.py"
    ]
    
    cmd = [
        sys.executable, "-m", "pytest",
        *test_files,
        "-v",
        "--tb=short",
        "--cov=app",
        "--cov-report=xml",
        "--cov-report=html"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())

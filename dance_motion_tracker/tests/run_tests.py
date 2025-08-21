#!/usr/bin/env python3
"""
Test runner for Dance Motion Tracker
"""
import sys
import unittest
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_all_tests():
    """Run all unit tests"""
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(str(start_dir), pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()

def run_specific_test(test_module):
    """Run a specific test module"""
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_module)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def check_dependencies():
    """Check if all required dependencies are available for testing"""
    
    missing_deps = []
    
    try:
        import cv2
    except ImportError:
        missing_deps.append('opencv-python')
    
    try:
        import mediapipe
    except ImportError:
        missing_deps.append('mediapipe')
    
    try:
        import numpy
    except ImportError:
        missing_deps.append('numpy')
    
    try:
        import flask
    except ImportError:
        missing_deps.append('flask')
    
    try:
        import pandas
    except ImportError:
        missing_deps.append('pandas')
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nPlease install missing dependencies:")
        print(f"   pip install {' '.join(missing_deps)}")
        return False
    
    print("✅ All required dependencies are available")
    return True

def main():
    """Main test runner function"""
    
    print("🧪 Dance Motion Tracker - Test Suite")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        test_module = sys.argv[1]
        print(f"Running specific test: {test_module}")
        success = run_specific_test(test_module)
    else:
        print("Running all tests...")
        success = run_all_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
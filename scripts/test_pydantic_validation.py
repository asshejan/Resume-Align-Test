#!/usr/bin/env python3
"""
Test script to demonstrate Pydantic validation for CV endpoints
"""
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.schemas.examples import (
    validate_cv_request_data,
    demonstrate_cv_data_validation,
    demonstrate_json_serialization
)

def main():
    """Run all validation examples"""
    print("🚀 Testing Pydantic Validation for CV Endpoints\n")
    
    try:
        print("=" * 60)
        print("1. Testing Request Data Validation")
        print("=" * 60)
        validate_cv_request_data()
        
        print("\n" + "=" * 60)
        print("2. Testing CV Data Structure Validation")
        print("=" * 60)
        demonstrate_cv_data_validation()
        
        print("\n" + "=" * 60)
        print("3. Testing JSON Serialization")
        print("=" * 60)
        demonstrate_json_serialization()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
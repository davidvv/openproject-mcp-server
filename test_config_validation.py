#!/usr/bin/env python3
"""
Test script to validate the configuration setup.
This script tests the enhanced configuration validation without requiring external dependencies.
"""

import os
import sys

def test_env_file():
    """Test that .env file exists and has proper structure."""
    print("🔍 Testing .env file...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
    
    required_vars = ['OPENPROJECT_URL', 'OPENPROJECT_API_KEY', 'MCP_HOST', 'MCP_PORT', 'MCP_LOG_LEVEL']
    
    for var in required_vars:
        if var not in content:
            print(f"❌ Missing required variable: {var}")
            return False
    
    print("✅ .env file structure is correct")
    return True

def test_config_validation():
    """Test configuration validation logic."""
    print("🔍 Testing configuration validation...")
    
    # Test 1: Missing required variables
    print("  Testing missing OPENPROJECT_URL...")
    os.environ.pop('OPENPROJECT_URL', None)
    try:
        from src.config import Settings
        settings = Settings()
        print("❌ Should have failed with missing OPENPROJECT_URL")
        return False
    except ValueError as e:
        if "OPENPROJECT_URL" in str(e) and "not set" in str(e):
            print("✅ Correctly detected missing OPENPROJECT_URL")
        else:
            print(f"❌ Wrong error message: {e}")
            return False
    
    # Test 2: Invalid URL format
    print("  Testing invalid URL format...")
    os.environ['OPENPROJECT_URL'] = 'invalid-url'
    try:
        settings = Settings()
        print("❌ Should have failed with invalid URL")
        return False
    except ValueError as e:
        if "must start with http://" in str(e):
            print("✅ Correctly detected invalid URL format")
        else:
            print(f"❌ Wrong error message: {e}")
            return False
    
    # Test 3: Invalid port
    print("  Testing invalid port...")
    os.environ['OPENPROJECT_URL'] = 'http://localhost:8080'
    os.environ['OPENPROJECT_API_KEY'] = 'test_key'
    os.environ['MCP_PORT'] = '99999'
    try:
        settings = Settings()
        print("❌ Should have failed with invalid port")
        return False
    except ValueError as e:
        if "must be between 1 and 65535" in str(e):
            print("✅ Correctly detected invalid port")
        else:
            print(f"❌ Wrong error message: {e}")
            return False
    
    # Test 4: Valid configuration
    print("  Testing valid configuration...")
    os.environ['MCP_PORT'] = '8080'
    try:
        settings = Settings()
        print("✅ Valid configuration accepted")
        print(f"   OpenProject URL: {settings.openproject_url}")
        print(f"   MCP Port: {settings.mcp_port}")
        print(f"   Log Level: {settings.log_level}")
        return True
    except Exception as e:
        print(f"❌ Valid configuration failed: {e}")
        return False

def main():
    """Run all configuration tests."""
    print("🧪 Testing OpenProject MCP Server Configuration")
    print("=" * 50)
    
    success = True
    
    # Test .env file
    if not test_env_file():
        success = False
    
    print()
    
    # Test configuration validation
    if not test_config_validation():
        success = False
    
    print()
    print("=" * 50)
    if success:
        print("🎉 All configuration tests passed!")
        print("✅ The configuration setup is working correctly.")
    else:
        print("❌ Some configuration tests failed.")
        print("Please check the errors above and fix the configuration.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
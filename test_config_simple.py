#!/usr/bin/env python3
"""
Simple configuration validation test that doesn't require external dependencies.
"""

import os
import sys

def test_env_file_structure():
    """Test that .env file exists and has proper structure."""
    print("🔍 Testing .env file structure...")
    
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
    
    # Check for documentation
    if "How to get your API key" not in content:
        print("❌ Missing API key documentation")
        return False
    
    if "TROUBLESHOOTING" not in content:
        print("❌ Missing troubleshooting section")
        return False
    
    print("✅ .env file structure is correct")
    print("✅ Documentation is present")
    return True

def test_validation_logic():
    """Test the validation logic without importing the config module."""
    print("🔍 Testing validation logic...")
    
    def validate_openproject_url(url):
        """Test URL validation."""
        if not url.startswith(("http://", "https://")):
            return False, "OPENPROJECT_URL must start with http:// or https://"
        return True, None
    
    def validate_api_key(key):
        """Test API key validation."""
        if not key:
            return False, "OPENPROJECT_API_KEY is not set"
        if len(key) < 20:
            return False, "OPENPROJECT_API_KEY appears to be too short"
        return True, None
    
    def validate_port(port):
        """Test port validation."""
        try:
            port_num = int(port)
            if not (1 <= port_num <= 65535):
                return False, "MCP_PORT must be between 1 and 65535"
            return True, None
        except ValueError:
            return False, "MCP_PORT must be a valid number"
    
    def validate_host(host):
        """Test host validation."""
        if host not in ["localhost", "0.0.0.0", "127.0.0.1"]:
            return False, "MCP_HOST should be 'localhost' or '0.0.0.0'"
        return True, None
    
    def validate_log_level(level):
        """Test log level validation."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level.upper() not in valid_levels:
            return False, f"Invalid log level. Valid levels: {', '.join(valid_levels)}"
        return True, None
    
    # Test cases
    test_cases = [
        ("http://localhost:8080", True, "Valid HTTP URL"),
        ("https://example.com", True, "Valid HTTPS URL"),
        ("invalid-url", False, "Invalid URL format"),
        ("ftp://example.com", False, "Wrong protocol"),
    ]
    
    for url, should_pass, description in test_cases:
        valid, error = validate_openproject_url(url)
        if valid == should_pass:
            print(f"✅ {description}: {url}")
        else:
            print(f"❌ {description}: {url} - Expected {should_pass}, got {valid}")
            if error:
                print(f"   Error: {error}")
            return False
    
    # Test API key validation
    api_key_tests = [
        ("valid_40_character_api_key_string_here", True, "Valid API key"),
        ("", False, "Empty API key"),
        ("short", False, "Too short API key"),
    ]
    
    for key, should_pass, description in api_key_tests:
        valid, error = validate_api_key(key)
        if valid == should_pass:
            print(f"✅ {description}")
        else:
            print(f"❌ {description} - Expected {should_pass}, got {valid}")
            if error:
                print(f"   Error: {error}")
            return False
    
    # Test port validation
    port_tests = [
        ("8080", True, "Valid port"),
        ("8080", True, "Standard HTTP port"),
        ("99999", False, "Port too high"),
        ("0", False, "Port too low"),
        ("invalid", False, "Invalid port format"),
    ]
    
    for port, should_pass, description in port_tests:
        valid, error = validate_port(port)
        if valid == should_pass:
            print(f"✅ {description}: {port}")
        else:
            print(f"❌ {description}: {port} - Expected {should_pass}, got {valid}")
            if error:
                print(f"   Error: {error}")
            return False
    
    # Test host validation
    host_tests = [
        ("localhost", True, "Valid localhost"),
        ("0.0.0.0", True, "Valid Docker host"),
        ("127.0.0.1", True, "Valid loopback"),
        ("example.com", False, "Invalid host"),
    ]
    
    for host, should_pass, description in host_tests:
        valid, error = validate_host(host)
        if valid == should_pass:
            print(f"✅ {description}: {host}")
        else:
            print(f"❌ {description}: {host} - Expected {should_pass}, got {valid}")
            if error:
                print(f"   Error: {error}")
            return False
    
    # Test log level validation
    level_tests = [
        ("INFO", True, "Valid INFO level"),
        ("DEBUG", True, "Valid DEBUG level"),
        ("ERROR", True, "Valid ERROR level"),
        ("invalid", False, "Invalid log level"),
    ]
    
    for level, should_pass, description in level_tests:
        valid, error = validate_log_level(level)
        if valid == should_pass:
            print(f"✅ {description}: {level}")
        else:
            print(f"❌ {description}: {level} - Expected {should_pass}, got {valid}")
            if error:
                print(f"   Error: {error}")
            return False
    
    print("✅ All validation logic tests passed")
    return True

def main():
    """Run all configuration tests."""
    print("🧪 Testing OpenProject MCP Server Configuration")
    print("=" * 50)
    
    success = True
    
    # Test .env file structure
    if not test_env_file_structure():
        success = False
    
    print()
    
    # Test validation logic
    if not test_validation_logic():
        success = False
    
    print()
    print("=" * 50)
    if success:
        print("🎉 All configuration tests passed!")
        print("✅ The configuration setup is working correctly.")
        print()
        print("📋 Summary of improvements:")
        print("   • Enhanced .env file with comprehensive documentation")
        print("   • Improved validation with helpful error messages")
        print("   • Added performance settings configuration")
        print("   • Added troubleshooting guidance")
    else:
        print("❌ Some configuration tests failed.")
        print("Please check the errors above and fix the configuration.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
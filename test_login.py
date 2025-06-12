#!/usr/bin/env python3
"""
Simple test script for the DropCountr login functionality
"""

from pydropcountr import DropCountrClient

def test_client_creation():
    """Test that we can create a client instance"""
    client = DropCountrClient()
    assert not client.is_logged_in()
    print("✓ Client creation test passed")

def test_login_with_invalid_credentials():
    """Test login with obviously invalid credentials"""
    client = DropCountrClient()
    
    # This should fail gracefully
    try:
        result = client.login("invalid@example.com", "wrongpassword")
        print(f"Login with invalid credentials returned: {result}")
        print("✓ Invalid login test completed (no exception thrown)")
    except Exception as e:
        print(f"✓ Invalid login test completed (exception: {e})")

if __name__ == "__main__":
    print("Running basic tests for PyDropCountr...")
    test_client_creation()
    test_login_with_invalid_credentials()
    print("Basic tests completed!")
    print("\nTo test with real credentials, use:")
    print("from pydropcountr import DropCountrClient")
    print("client = DropCountrClient()")
    print("success = client.login('your@email.com', 'yourpassword')")
    print("print(f'Login successful: {success}')")
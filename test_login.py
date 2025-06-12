#!/usr/bin/env python3
"""
Simple test script for the DropCountr login functionality
"""

from pydropcountr import DropCountrClient, UsageData, UsageResponse

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

def test_usage_data_class():
    """Test the UsageData class"""
    usage = UsageData(
        during="2025-06-01T00:00:00Z/2025-06-02T00:00:00Z",
        total_gallons=7.4805193,
        irrigation_gallons=0.0,
        irrigation_events=0.0,
        is_leaking=False
    )
    
    # Test property access
    assert usage.total_gallons == 7.4805193
    assert not usage.is_leaking
    
    # Test date parsing
    start_date = usage.start_date
    end_date = usage.end_date
    assert start_date.year == 2025
    assert start_date.month == 6
    assert start_date.day == 1
    assert end_date.day == 2
    
    print("✓ UsageData class test passed")

def test_get_usage_without_login():
    """Test that get_usage fails when not logged in"""
    client = DropCountrClient()
    
    try:
        result = client.get_usage(1258809, "2025-06-01T00:00:00.000Z", "2025-06-30T23:59:59.000Z")
        print("✗ Expected ValueError for get_usage without login")
    except ValueError as e:
        print("✓ get_usage correctly raises ValueError when not logged in")
    except Exception as e:
        print(f"✗ Unexpected exception: {e}")

if __name__ == "__main__":
    print("Running basic tests for PyDropCountr...")
    test_client_creation()
    test_login_with_invalid_credentials()
    test_usage_data_class()
    test_get_usage_without_login()
    print("Basic tests completed!")
    print("\nTo test with real credentials and usage data, use:")
    print("from pydropcountr import DropCountrClient")
    print("client = DropCountrClient()")
    print("success = client.login('your@email.com', 'yourpassword')")
    print("if success:")
    print("    usage = client.get_usage(SERVICE_CONNECTION_ID, '2025-06-01T00:00:00.000Z', '2025-06-30T23:59:59.000Z')")
    print("    if usage:")
    print("        print(f'Total records: {usage.total_items}')")
    print("        for record in usage.usage_data[:3]:  # Show first 3 records")
    print("            print(f'{record.start_date.date()}: {record.total_gallons} gallons')")
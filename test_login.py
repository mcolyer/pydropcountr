#!/usr/bin/env python3
"""
Simple test script for the DropCountr login functionality
"""

from datetime import datetime

from pydropcountr import DropCountrClient, ServiceConnection, UsageData


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
        is_leaking=False,
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


def test_datetime_conversion():
    """Test the datetime conversion functionality"""
    client = DropCountrClient()

    # Test string input (should pass through)
    str_date = "2025-06-01T00:00:00.000Z"
    result = client._datetime_to_iso(str_date)
    assert result == str_date

    # Test datetime input
    dt = datetime(2025, 6, 1, 0, 0, 0)
    result = client._datetime_to_iso(dt)
    assert result == "2025-06-01T00:00:00.000Z"

    print("✓ Datetime conversion test passed")


def test_get_usage_without_login():
    """Test that get_usage fails when not logged in"""
    client = DropCountrClient()

    # Test with datetime objects
    start_date = datetime(2025, 6, 1)
    end_date = datetime(2025, 6, 30, 23, 59, 59)

    try:
        client.get_usage(1258809, start_date, end_date)
        print("✗ Expected ValueError for get_usage without login")
    except ValueError:
        print("✓ get_usage correctly raises ValueError when not logged in")
    except Exception as e:
        print(f"✗ Unexpected exception: {e}")


def test_service_connection_class():
    """Test the ServiceConnection class"""
    # Test creating from API response format
    api_data = {
        "id": 1064520,
        "name": "Main Service",
        "address": "123 Main St",
        "account_number": "ACC123",
        "service_type": "Water",
        "status": "Active",
        "meter_serial": "METER123",
        "@id": "https://dropcountr.com/api/service_connections/1064520",
    }

    service = ServiceConnection.from_api_response(api_data)
    assert service.id == 1064520
    assert service.name == "Main Service"
    assert service.address == "123 Main St"
    assert service.account_number == "ACC123"

    print("✓ ServiceConnection class test passed")


def test_service_methods_without_login():
    """Test that service methods fail when not logged in"""
    client = DropCountrClient()

    # Test get_service_connection
    try:
        client.get_service_connection(1064520)
        print("✗ Expected ValueError for get_service_connection without login")
    except ValueError:
        print("✓ get_service_connection correctly raises ValueError when not logged in")
    except Exception as e:
        print(f"✗ Unexpected exception: {e}")

    # Test list_service_connections
    try:
        client.list_service_connections()
        print("✗ Expected ValueError for list_service_connections without login")
    except ValueError:
        print(
            "✓ list_service_connections correctly raises ValueError when not logged in"
        )
    except Exception as e:
        print(f"✗ Unexpected exception: {e}")


if __name__ == "__main__":
    print("Running basic tests for PyDropCountr...")
    test_client_creation()
    test_login_with_invalid_credentials()
    test_usage_data_class()
    test_datetime_conversion()
    test_get_usage_without_login()
    test_service_connection_class()
    test_service_methods_without_login()
    print("Basic tests completed!")
    print("\nTo test with real credentials and usage data, use:")
    print("from pydropcountr import DropCountrClient")
    print("from datetime import datetime")
    print("client = DropCountrClient()")
    print("success = client.login('your@email.com', 'yourpassword')")
    print("if success:")
    print("    # List all service connections")
    print("    services = client.list_service_connections()")
    print("    if services:")
    print("        print(f'Found {len(services)} service connections:')")
    print("        for service in services:")
    print("            print(f'  {service.id}: {service.name} at {service.address}')")
    print("    ")
    print("    # Get specific service details")
    print("    service = client.get_service_connection(SERVICE_CONNECTION_ID)")
    print("    if service:")
    print("        print(f'Service: {service.name} (ID: {service.id})')")
    print("    ")
    print("    # Get usage data for a service")
    print("    start_date = datetime(2025, 6, 1)")
    print("    end_date = datetime(2025, 6, 30, 23, 59, 59)")
    print("    usage = client.get_usage(SERVICE_CONNECTION_ID, start_date, end_date)")
    print("    if usage:")
    print("        print(f'Total records: {usage.total_items}')")
    print("        for record in usage.usage_data[:3]:  # Show first 3 records")
    print(
        "            print(f'{record.start_date.date()}: {record.total_gallons} gallons')"
    )

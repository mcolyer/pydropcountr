# PyDropCountr - Python Library for DropCountr.com

## Project Overview
This is a Python library for interacting with dropcountr.com, providing easy access to water usage data through clean Python objects.

## Features
- User authentication with login/logout
- Water usage data fetching with date ranges
- Structured data objects (UsageData, UsageResponse)
- Date parsing and validation
- Session management with rack.session cookies

## Development Setup
- This project uses `uv` for dependency management
- Python 3.12+ required
- Dependencies: requests>=2.31.0
- Run tests with: `uv run python test_login.py`
- Run linting with: `uv run ruff check` (when configured)

## Usage Examples

### Basic Login
```python
from pydropcountr import DropCountrClient

client = DropCountrClient()
success = client.login('your@email.com', 'yourpassword')
if success:
    print("Logged in successfully!")
```

### Fetch Usage Data
```python
# Get daily usage data for June 2025
# Note: start_date and end_date must be full ISO datetime strings with timezone
usage = client.get_usage(
    service_connection_id=1258809,
    start_date='2025-06-01T00:00:00.000Z',    # Full datetime with timezone
    end_date='2025-06-30T23:59:59.000Z',      # Full datetime with timezone
    period='day'  # Can be 'day', 'hour', etc.
)

if usage:
    print(f"Total records: {usage.total_items}")
    for record in usage.usage_data[:3]:
        print(f"{record.start_date.date()}: {record.total_gallons} gallons")
```

## API Information
- Login URL: https://dropcountr.com/login
- Login method: POST with email and password parameters
- Usage API: https://dropcountr.com/api/service_connections/{id}/usage
- Authentication: rack.session cookie must be maintained for subsequent requests
- API version: application/vnd.dropcountr.api+json;version=2

## Data Classes
- `UsageData`: Individual usage record with gallons, irrigation data, leak detection
- `UsageResponse`: Full API response with usage data array and metadata
- Both classes include proper type hints and date parsing utilities

## Development Notes
- Keep authentication session state for API calls
- Implement proper error handling for login failures and API errors
- Return data as clean Python objects with type safety
- Service connection IDs must be obtained from the DropCountr dashboard
- **Important**: Date parameters must be full ISO 8601 datetime strings with timezone (e.g., '2025-06-01T00:00:00.000Z'), not just dates
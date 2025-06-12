# PyDropCountr - Python Library for DropCountr.com

## Project Overview
This is a Python library for interacting with dropcountr.com, providing easy access to water usage data through clean Python objects.

## Features
- User authentication with login/logout
- Service connection management (list and get details)
- Water usage data fetching with date ranges
- Structured data objects (ServiceConnection, UsageData, UsageResponse)
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

### List Service Connections
```python
# Get all service connections for the authenticated user
services = client.list_service_connections()
if services:
    print(f"Found {len(services)} service connections:")
    for service in services:
        print(f"  {service.id}: {service.name} at {service.address}")
```

### Get Service Connection Details
```python
# Get details for a specific service connection
service = client.get_service_connection(1064520)
if service:
    print(f"Service: {service.name}")
    print(f"Address: {service.address}")
    print(f"Account: {service.account_number}")
    print(f"Status: {service.status}")
```

### Fetch Usage Data
```python
from datetime import datetime

# Get daily usage data for June 2025 using Python datetime objects
usage = client.get_usage(
    service_connection_id=1258809,
    start_date=datetime(2025, 6, 1),           # Python datetime object
    end_date=datetime(2025, 6, 30, 23, 59, 59), # Python datetime object
    period='day'  # Can be 'day', 'hour', etc.
)

if usage:
    print(f"Total records: {usage.total_items}")
    for record in usage.usage_data[:3]:
        print(f"{record.start_date.date()}: {record.total_gallons} gallons")

# Alternative: You can still use ISO datetime strings
usage = client.get_usage(
    service_connection_id=1258809,
    start_date='2025-06-01T00:00:00.000Z',
    end_date='2025-06-30T23:59:59.000Z',
    period='day'
)
```

## API Information
- Login URL: https://dropcountr.com/login
- Login method: POST with email and password parameters
- Service connections list: https://dropcountr.com/api/service_connections
- Service connection details: https://dropcountr.com/api/service_connections/{id}
- Usage API: https://dropcountr.com/api/service_connections/{id}/usage
- Authentication: rack.session cookie must be maintained for subsequent requests
- API version: application/vnd.dropcountr.api+json;version=2

## Data Classes
- `ServiceConnection`: Service connection details including ID, name, address, account info
- `UsageData`: Individual usage record with gallons, irrigation data, leak detection
- `UsageResponse`: Full API response with usage data array and metadata
- All classes include proper type hints and parsing utilities

## Development Notes
- Keep authentication session state for API calls
- Implement proper error handling for login failures and API errors
- Return data as clean Python objects with type safety
- **Service Discovery**: Use `list_service_connections()` to discover available service connection IDs
- **Date Parameters**: The library accepts both Python `datetime` objects (recommended) and ISO 8601 datetime strings
- When using datetime objects, the library automatically converts them to the required API format
- Timezone handling: datetime objects are converted to UTC with 'Z' suffix for API compatibility

## Changelog Management

### Using CHANGELOG.md
This project maintains a comprehensive CHANGELOG.md file following [Keep a Changelog](https://keepachangelog.com/) format:

**When to update the changelog:**
- Every significant change to the library or CLI
- New features, bug fixes, API changes, or breaking changes
- Before each release to move items from [Unreleased] to a version section

**How to update the changelog:**
1. Add new changes under the `[Unreleased]` section
2. Use appropriate categories: Added, Changed, Deprecated, Removed, Fixed, Security
3. Write clear, user-focused descriptions of changes
4. Include relevant details like new CLI flags, API changes, or breaking changes

**Release process:**
1. Update CHANGELOG.md with new version section
2. Move items from [Unreleased] to the new version section with date
3. Update version number in pyproject.toml
4. Create git tag with version number: `git tag v0.x.x`
5. Create GitHub release with changelog notes

**Example changelog entry:**
```markdown
## [Unreleased]

### Added
- New CLI flag `--format` for output formatting
- Support for JSON output in CLI

### Fixed
- Authentication timeout handling
- Memory leak in session management
```
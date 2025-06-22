# PyDropCountr 💧

A Python library for interacting with [DropCountr.com](https://dropcountr.com) water usage monitoring systems.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🔐 **Authentication**: Secure login with session management
- 🏠 **Service Discovery**: List and get details for your service connections
- 📊 **Usage Data**: Fetch water usage data with flexible date ranges
- 🐍 **Pythonic API**: Clean, type-safe interface with Pydantic models
- ⏰ **Smart Dates**: Accepts both Python `datetime` objects and ISO strings
- 🖥️ **CLI Tool**: Command-line interface for quick usage reports

## Installation

```bash
pip install pydropcountr
```

For development:
```bash
git clone https://github.com/yourusername/pydropcountr.git
cd pydropcountr
uv install --dev
```

## CLI Usage

PyDropCountr includes a command-line tool for quick usage reports:

### Quick Start
```bash
# Set credentials as environment variables (recommended)
export DROPCOUNTR_EMAIL="your@email.com"
export DROPCOUNTR_PASSWORD="yourpassword"

# Get yesterday's usage + last 7 days (default behavior)
dropcountr usage

# Get last 30 days
dropcountr usage --days=30

# Get specific date range
dropcountr usage --start_date=2025-06-01 --end_date=2025-06-15

# List all service connections
dropcountr services
```

### CLI Options
```bash
# All commands support these authentication options:
--email=your@email.com --password=yourpass

# Usage command options:
dropcountr usage [options]
  --service_id=1234567      # Use specific service (defaults to first)
  --start_date=YYYY-MM-DD   # Start date
  --end_date=YYYY-MM-DD     # End date  
  --days=30                 # Days back from today
  --period=day              # Granularity: 'day' or 'hour'

# Get help for any command:
dropcountr usage --help
dropcountr services --help
```

### Environment Variables
```bash
export DROPCOUNTR_EMAIL="your@email.com"
export DROPCOUNTR_PASSWORD="yourpassword"
```

## Python API Usage

### Quick Start
```python
from pydropcountr import DropCountrClient
from datetime import datetime

# Create client and login
client = DropCountrClient()
success = client.login('your@email.com', 'yourpassword')

if success:
    # Discover your service connections
    services = client.list_service_connections()
    print(f"Found {len(services)} service connections:")
    
    for service in services:
        print(f"  {service.id}: {service.name} at {service.address}")
    
    # Get usage data for a service
    service_id = services[0].id
    start_date = datetime(2025, 6, 1)
    end_date = datetime(2025, 6, 30, 23, 59, 59)
    
    usage = client.get_usage(service_id, start_date, end_date)
    if usage:
        print(f"\\nUsage data: {usage.total_items} records")
        for record in usage.usage_data[:5]:  # Show first 5 days
            print(f"  {record.start_date.date()}: {record.total_gallons:.1f} gallons")
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

## API Reference

### DropCountrClient

The main client for interacting with DropCountr.

#### Initialization
```python
# Default: Pacific timezone (America/Los_Angeles)
client = DropCountrClient()

# Custom timezone
client = DropCountrClient(timezone="America/New_York")
client = DropCountrClient(timezone="UTC")

# Using ZoneInfo object
from zoneinfo import ZoneInfo
client = DropCountrClient(timezone=ZoneInfo("Europe/London"))
```

#### Authentication
```python
success = client.login(email: str, password: str) -> bool
client.logout() -> None
client.is_logged_in() -> bool
```

#### Service Connections
```python
# List all service connections
services = client.list_service_connections() -> List[ServiceConnection] | None

# Get specific service details
service = client.get_service_connection(service_id: int) -> ServiceConnection | None
```

#### Usage Data
```python
# Get usage data with datetime objects (recommended)
usage = client.get_usage(
    service_connection_id: int,
    start_date: datetime,
    end_date: datetime,
    period: str = "day"  # or "hour"
) -> UsageResponse | None

# Alternative: Use ISO datetime strings
usage = client.get_usage(
    service_connection_id=1234,
    start_date='2025-06-01T00:00:00.000Z',
    end_date='2025-06-30T23:59:59.000Z'
)
```

### Data Models

All response data is validated using Pydantic models:

#### ServiceConnection
```python
class ServiceConnection(BaseModel):
    id: int                           # Service connection ID
    name: str                         # Service name
    address: str                      # Service address
    account_number: str | None        # Account number
    service_type: str | None          # Service type
    status: str | None                # Service status
    meter_serial: str | None          # Meter serial number
    api_id: str | None                # API identifier
```

#### UsageData
```python
class UsageData(BaseModel):
    during: str                       # Time period (ISO interval)
    total_gallons: float              # Total usage in gallons (≥0)
    irrigation_gallons: float         # Irrigation usage (≥0)
    irrigation_events: float          # Number of irrigation events (≥0)
    is_leaking: bool                  # Leak detection status
    
    # Convenience properties
    start_date: datetime              # Parsed start date (timezone-aware)
    end_date: datetime                # Parsed end date (timezone-aware)
```

#### UsageResponse
```python
class UsageResponse(BaseModel):
    usage_data: List[UsageData]       # List of usage records
    total_items: int                  # Total number of items (≥0)
    api_id: str                       # API response identifier
    consumed_via_id: str              # Service connection identifier
```

## Error Handling

The library raises clear exceptions for common issues:

```python
try:
    usage = client.get_usage(service_id, start_date, end_date)
except ValueError as e:
    print(f"Authentication or parameter error: {e}")
except requests.RequestException as e:
    print(f"Network error: {e}")
```

Common errors:
- `ValueError`: Not logged in or invalid parameters
- `requests.RequestException`: Network connectivity issues
- Returns `None`: API returned unexpected data format

## Date and Timezone Handling

The library accepts both Python `datetime` objects and ISO 8601 strings:

```python
from datetime import datetime

# Recommended: Python datetime objects
start_date = datetime(2025, 6, 1)
end_date = datetime(2025, 6, 30, 23, 59, 59)

# Alternative: ISO datetime strings
start_date = '2025-06-01T00:00:00.000Z'
end_date = '2025-06-30T23:59:59.000Z'
```

### Timezone Behavior

**⚠️ Breaking Change in v0.1.3**: Timezone handling has been fixed to correctly represent local time.

PyDropCountr now properly handles timezone-aware datetime objects:

- **Default timezone**: Pacific Time (`America/Los_Angeles`) - configurable during client initialization
- **API timestamps**: Despite having 'Z' suffix, timestamps are actually in local time (not UTC)
- **Returned datetimes**: All `start_date` and `end_date` properties are timezone-aware
- **Standard library**: Uses Python 3.12+ `zoneinfo` module (no external dependencies)

```python
from datetime import datetime
from zoneinfo import ZoneInfo

# Default Pacific timezone
client = DropCountrClient()
usage = client.get_usage(service_id, start_date, end_date)

# Returned datetimes are timezone-aware in Pacific time
for record in usage.usage_data:
    print(record.start_date)  # 2025-06-01 08:00:00-07:00 (PDT)
    print(record.start_date.tzinfo)  # America/Los_Angeles

# Custom timezone for other regions
client = DropCountrClient(timezone="America/New_York")
# or
client = DropCountrClient(timezone=ZoneInfo("UTC"))
```

**Migration from v0.1.2**: If you were previously working around the incorrect UTC timestamps, you'll need to update your code as datetimes are now correctly timezone-aware in local time.

## Development

### Setup
```bash
git clone https://github.com/yourusername/pydropcountr.git
cd pydropcountr
uv install --dev
```

### Testing
```bash
uv run python test_login.py
```

### Linting
```bash
uv run ruff check
uv run ruff format
uv run mypy pydropcountr.py
```

### Project Structure
```
pydropcountr/
├── pydropcountr.py       # Main library
├── cli.py                # Command-line interface
├── test_login.py         # Test suite
├── pyproject.toml        # Project configuration
├── README.md             # This file
└── CLAUDE.md            # Development notes
```

## Requirements

- Python 3.12+
- requests >= 2.31.0
- pydantic >= 2.0.0
- fire >= 0.7.0

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Disclaimer

This is an unofficial library for DropCountr.com. Use at your own risk and respect the service's terms of use.
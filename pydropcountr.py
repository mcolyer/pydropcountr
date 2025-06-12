"""
PyDropCountr - Python library for interacting with dropcountr.com
"""

from datetime import datetime

import requests
from pydantic import BaseModel, Field


class UsageData(BaseModel):
    """Represents a single usage data record from DropCountr"""
    during: str = Field(description="Time period for this usage record")
    total_gallons: float = Field(ge=0, description="Total water usage in gallons")
    irrigation_gallons: float = Field(ge=0, description="Irrigation usage in gallons")
    irrigation_events: float = Field(ge=0, description="Number of irrigation events")
    is_leaking: bool = Field(description="Whether a leak was detected")

    @property
    def start_date(self) -> datetime:
        """Parse and return the start date from the during field"""
        return datetime.fromisoformat(self.during.split('/')[0].replace('Z', '+00:00'))

    @property
    def end_date(self) -> datetime:
        """Parse and return the end date from the during field"""
        return datetime.fromisoformat(self.during.split('/')[1].replace('Z', '+00:00'))


class UsageResponse(BaseModel):
    """Represents the full usage API response"""
    usage_data: list[UsageData] = Field(description="List of usage data records")
    total_items: int = Field(ge=0, description="Total number of items in response")
    api_id: str = Field(description="API identifier for this response")
    consumed_via_id: str = Field(description="Service connection API identifier")


class ServiceConnection(BaseModel):
    """Represents a service connection from DropCountr"""
    id: int = Field(description="Unique service connection identifier")
    name: str = Field(description="Service connection name")
    address: str = Field(description="Service address")
    account_number: str | None = Field(None, description="Account number")
    service_type: str | None = Field(None, description="Type of service")
    status: str | None = Field(None, description="Service status")
    meter_serial: str | None = Field(None, description="Water meter serial number")
    api_id: str | None = Field(None, description="API identifier")

    @classmethod
    def from_api_response(cls, data: dict) -> 'ServiceConnection':
        """Create ServiceConnection from API response data"""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            address=data.get('address', ''),
            account_number=data.get('account_number'),
            service_type=data.get('service_type'),
            status=data.get('status'),
            meter_serial=data.get('meter_serial'),
            api_id=data.get('@id')
        )


class DropCountrClient:
    """Client for interacting with the DropCountr.com API"""

    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://dropcountr.com"
        self.logged_in = False

    def _datetime_to_iso(self, dt: datetime | str) -> str:
        """Convert datetime object or string to ISO format string for API"""
        if isinstance(dt, str):
            return dt
        elif isinstance(dt, datetime):
            # Format as ISO string with milliseconds and Z suffix
            iso_string = dt.isoformat()
            # Add milliseconds if not present
            if '.' not in iso_string:
                iso_string += '.000'
            # Replace timezone info with Z
            if iso_string.endswith('+00:00'):
                iso_string = iso_string.replace('+00:00', 'Z')
            elif not iso_string.endswith('Z'):
                iso_string += 'Z'
            return iso_string
        else:
            raise ValueError(f"Expected datetime or str, got {type(dt)}")

    def login(self, email: str, password: str) -> bool:
        """
        Login to dropcountr.com

        Args:
            email: User's email address
            password: User's password

        Returns:
            bool: True if login successful, False otherwise

        Raises:
            requests.RequestException: If there's a network error
        """
        login_url = f"{self.base_url}/login"

        login_data = {
            "email": email,
            "password": password
        }

        try:
            response = self.session.post(login_url, data=login_data)
            response.raise_for_status()

            # Check if we have a rack.session cookie
            if 'rack.session' in self.session.cookies:
                self.logged_in = True
                return True
            else:
                # Login failed - check response for error indicators
                if response.status_code == 200:
                    # Might be a redirect or error page, check content
                    if "login" in response.url.lower() or "error" in response.text.lower():
                        self.logged_in = False
                        return False
                self.logged_in = True
                return True

        except requests.RequestException as e:
            self.logged_in = False
            raise e

    def is_logged_in(self) -> bool:
        """Check if the client is currently logged in"""
        return self.logged_in

    def logout(self):
        """Clear the session and logout"""
        self.session.cookies.clear()
        self.logged_in = False

    def get_usage(self, service_connection_id: int, start_date: datetime | str, end_date: datetime | str, period: str = "day") -> UsageResponse | None:
        """
        Get usage data for a service connection

        Args:
            service_connection_id: The service connection ID
            start_date: Start date as datetime object or ISO format string
            end_date: End date as datetime object or ISO format string
            period: Period granularity ("day", "hour", etc.)

        Returns:
            UsageResponse object containing usage data, or None if failed

        Raises:
            requests.RequestException: If there's a network error
            ValueError: If not logged in or invalid date format
        """
        if not self.logged_in:
            raise ValueError("Must be logged in to fetch usage data")

        # Convert datetime objects to ISO strings
        start_iso = self._datetime_to_iso(start_date)
        end_iso = self._datetime_to_iso(end_date)

        # Format the during parameter
        during = f"{start_iso}/{end_iso}"

        url = f"{self.base_url}/api/service_connections/{service_connection_id}/usage"

        headers = {
            'accept': 'application/vnd.dropcountr.api+json;version=2',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'referer': f'{self.base_url}/dashboard',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
        }

        params = {
            'during': during,
            'period': period
        }

        try:
            response = self.session.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()

            if 'data' not in data:
                return None

            # Parse usage data
            usage_records = []
            for record in data['data']['member']:
                usage_records.append(UsageData(
                    during=record['during'],
                    total_gallons=record['total_gallons'],
                    irrigation_gallons=record['irrigation_gallons'],
                    irrigation_events=record['irrigation_events'],
                    is_leaking=record['is_leaking']
                ))

            return UsageResponse(
                usage_data=usage_records,
                total_items=data['data']['totalItems'],
                api_id=data['data']['@id'],
                consumed_via_id=data['data']['consumed_via']['@id']
            )

        except requests.RequestException as e:
            raise e
        except (KeyError, ValueError):
            return None

    def get_service_connection(self, service_connection_id: int) -> ServiceConnection | None:
        """
        Get details for a specific service connection

        Args:
            service_connection_id: The service connection ID

        Returns:
            ServiceConnection object containing service details, or None if failed

        Raises:
            requests.RequestException: If there's a network error
            ValueError: If not logged in
        """
        if not self.logged_in:
            raise ValueError("Must be logged in to fetch service connection details")

        url = f"{self.base_url}/api/service_connections/{service_connection_id}"

        headers = {
            'accept': 'application/vnd.dropcountr.api+json;version=2',
            'accept-language': 'en-US,en;q=0.9',
            'referer': f'{self.base_url}/dashboard',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
        }

        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            if 'data' not in data:
                return None

            return ServiceConnection.from_api_response(data['data'])

        except requests.RequestException as e:
            raise e
        except (KeyError, ValueError):
            return None

    def list_service_connections(self) -> list[ServiceConnection] | None:
        """
        List all service connections for the authenticated user

        Returns:
            List of ServiceConnection objects, or None if failed

        Raises:
            requests.RequestException: If there's a network error
            ValueError: If not logged in
        """
        if not self.logged_in:
            raise ValueError("Must be logged in to fetch service connections")

        url = f"{self.base_url}/api/service_connections"

        headers = {
            'accept': 'application/vnd.dropcountr.api+json;version=2',
            'accept-language': 'en-US,en;q=0.9',
            'referer': f'{self.base_url}/dashboard',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
        }

        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            if 'data' not in data or 'member' not in data['data']:
                return None

            service_connections = []
            for service_data in data['data']['member']:
                service_connections.append(ServiceConnection.from_api_response(service_data))

            return service_connections

        except requests.RequestException as e:
            raise e
        except (KeyError, ValueError):
            return None

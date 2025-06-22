"""
PyDropCountr - Python library for interacting with dropcountr.com
"""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from pydantic import BaseModel, Field


class UsageData(BaseModel):
    """Represents a single usage data record from DropCountr"""

    during: str = Field(description="Time period for this usage record")
    total_gallons: float = Field(ge=0, description="Total water usage in gallons")
    irrigation_gallons: float = Field(ge=0, description="Irrigation usage in gallons")
    irrigation_events: float = Field(ge=0, description="Number of irrigation events")
    is_leaking: bool = Field(description="Whether a leak was detected")
    _timezone: ZoneInfo | None = None

    @property
    def start_date(self) -> datetime:
        """Parse and return the start date from the during field as timezone-aware datetime"""
        dt_str = self.during.split("/")[0].replace("Z", "")
        dt = datetime.fromisoformat(dt_str)
        if self._timezone:
            return dt.replace(tzinfo=self._timezone)
        return dt.replace(tzinfo=ZoneInfo("America/Los_Angeles"))

    @property
    def end_date(self) -> datetime:
        """Parse and return the end date from the during field as timezone-aware datetime"""
        dt_str = self.during.split("/")[1].replace("Z", "")
        dt = datetime.fromisoformat(dt_str)
        if self._timezone:
            return dt.replace(tzinfo=self._timezone)
        return dt.replace(tzinfo=ZoneInfo("America/Los_Angeles"))

    def set_timezone(self, timezone: ZoneInfo | str) -> None:
        """Set the timezone for parsing datetime fields"""
        if isinstance(timezone, str):
            self._timezone = ZoneInfo(timezone)
        else:
            self._timezone = timezone


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
    def from_api_response(cls, data: dict) -> "ServiceConnection":
        """Create ServiceConnection from API response data"""
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            address=data.get("address", ""),
            account_number=data.get("account_number"),
            service_type=data.get("service_type"),
            status=data.get("status"),
            meter_serial=data.get("meter_serial"),
            api_id=data.get("@id"),
        )


class DropCountrClient:
    """Client for interacting with the DropCountr.com API"""

    def __init__(self, timezone: str | ZoneInfo = "America/Los_Angeles") -> None:
        self.session = requests.Session()
        self.base_url = "https://dropcountr.com"
        self.logged_in = False
        self.user_id: int | None = None
        self.logger = logging.getLogger(__name__)

        # Set timezone for datetime parsing
        if isinstance(timezone, str):
            self.timezone = ZoneInfo(timezone)
        else:
            self.timezone = timezone

    def _datetime_to_iso(self, dt: datetime | str) -> str:
        """Convert datetime object or string to ISO format string for API"""
        if isinstance(dt, str):
            return dt
        elif isinstance(dt, datetime):
            # Format as ISO string with milliseconds and Z suffix
            iso_string = dt.isoformat()
            # Add milliseconds if not present
            if "." not in iso_string:
                iso_string += ".000"
            # Replace timezone info with Z
            if iso_string.endswith("+00:00"):
                iso_string = iso_string.replace("+00:00", "Z")
            elif not iso_string.endswith("Z"):
                iso_string += "Z"
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
        self.logger.debug(f"Attempting login to {login_url}")

        login_data = {"email": email, "password": password}

        try:
            self.logger.debug("Sending POST request to login endpoint")
            response = self.session.post(login_url, data=login_data)
            self.logger.debug(f"Login response status: {response.status_code}")
            self.logger.debug(f"Login response URL: {response.url}")
            response.raise_for_status()

            # Check if we have a rack.session cookie
            cookies = dict(self.session.cookies)
            self.logger.debug(f"Cookies after login: {list(cookies.keys())}")
            if "rack.session" in self.session.cookies:
                self.logger.debug("rack.session cookie found - login successful")
                self.logged_in = True
                return True
            else:
                self.logger.debug("No rack.session cookie found")
                # Login failed - check response for error indicators
                if response.status_code == 200:
                    # Might be a redirect or error page, check content
                    if (
                        "login" in response.url.lower()
                        or "error" in response.text.lower()
                    ):
                        self.logger.debug("Login page or error detected in response")
                        self.logged_in = False
                        return False
                self.logged_in = True
                return True

        except requests.RequestException as e:
            self.logged_in = False
            raise e

    def is_logged_in(self) -> bool:
        """Check if the client is currently logged in"""
        return bool(self.logged_in)

    def logout(self) -> None:
        """Clear the session and logout"""
        self.session.cookies.clear()
        self.logged_in = False

    def get_usage(
        self,
        service_connection_id: int,
        start_date: datetime | str,
        end_date: datetime | str,
        period: str = "day",
    ) -> UsageResponse | None:
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
            "accept": "application/vnd.dropcountr.api+json;version=2",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "referer": f"{self.base_url}/dashboard",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        }

        params = {"during": during, "period": period}

        try:
            response = self.session.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()

            if "data" not in data:
                return None

            # Parse usage data
            usage_records = []
            for record in data["data"]["member"]:
                usage_data = UsageData(
                    during=record["during"],
                    total_gallons=record["total_gallons"],
                    irrigation_gallons=record["irrigation_gallons"],
                    irrigation_events=record["irrigation_events"],
                    is_leaking=record["is_leaking"],
                )
                usage_data.set_timezone(self.timezone)
                usage_records.append(usage_data)

            return UsageResponse(
                usage_data=usage_records,
                total_items=data["data"]["totalItems"],
                api_id=data["data"]["@id"],
                consumed_via_id=data["data"]["consumed_via"]["@id"],
            )

        except requests.RequestException as e:
            raise e
        except (KeyError, ValueError):
            return None

    def get_service_connection(
        self, service_connection_id: int
    ) -> ServiceConnection | None:
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
        # Get all service connections and find the one with matching ID
        service_connections = self.list_service_connections()
        if not service_connections:
            return None

        for service in service_connections:
            if service.id == service_connection_id:
                return service

        return None

    def get_user_data(self) -> dict | None:
        """
        Get current user data from /api/me endpoint

        Returns:
            User data dictionary, or None if failed

        Raises:
            requests.RequestException: If there's a network error
            ValueError: If not logged in
        """
        if not self.logged_in:
            raise ValueError("Must be logged in to fetch user data")

        url = f"{self.base_url}/api/me"
        self.logger.debug(f"Fetching user data from {url}")

        headers = {
            "accept": "application/vnd.dropcountr.api+json;version=2",
            "accept-language": "en-US,en;q=0.9",
            "referer": f"{self.base_url}/dashboard",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        }

        try:
            self.logger.debug("Sending GET request to /api/me")
            response = self.session.get(url, headers=headers)
            self.logger.debug(f"User data response status: {response.status_code}")
            response.raise_for_status()

            data = response.json()
            self.logger.debug(f"User data response type: {type(data)}")
            self.logger.debug(
                f"User data response length: {len(data) if isinstance(data, list | dict) else 'N/A'}"
            )

            # Check for both response formats: [true, user_data] and {'data': user_data}
            user_data = None
            if isinstance(data, list) and len(data) == 2 and data[0] is True:
                # Old format: [true, user_data]
                user_data = data[1]
                self.logger.debug("Found user data in old format [true, user_data]")
            elif isinstance(data, dict) and "data" in data:
                # New format: {'data': user_data}
                user_data = data["data"]
                self.logger.debug("Found user data in new format {'data': user_data}")
            else:
                self.logger.debug(f"Unexpected response format: {data}")
                return None

            if user_data:
                self.logger.debug(
                    f"Found user data with keys: {list(user_data.keys()) if isinstance(user_data, dict) else 'Not a dict'}"
                )
                # Store user ID for potential future use
                if "id" in user_data:
                    self.user_id = user_data["id"]
                    self.logger.debug(f"Stored user ID: {self.user_id}")
                return dict(user_data)

            return None

        except requests.RequestException as e:
            raise e
        except (KeyError, ValueError, IndexError):
            return None

    def list_service_connections(self) -> list[ServiceConnection] | None:
        """
        List all service connections for the authenticated user across all premises

        Returns:
            List of ServiceConnection objects, or None if failed

        Raises:
            requests.RequestException: If there's a network error
            ValueError: If not logged in
        """
        self.logger.debug("Getting user data for service connections")
        user_data = self.get_user_data()
        if not user_data:
            self.logger.debug("No user data returned")
            return None

        try:
            all_service_connections = []

            # First, get service connections from the current premise (in attributes)
            self.logger.debug("Checking current premise in user attributes...")
            attributes = user_data.get("attributes", {})
            self.logger.debug(
                f"User attributes keys: {list(attributes.keys()) if attributes else 'No attributes'}"
            )

            service_connections_data = attributes.get("service_connections", [])
            self.logger.debug(
                f"Found {len(service_connections_data)} service connections in current premise"
            )

            for service_data in service_connections_data:
                self.logger.debug(
                    f"Processing service connection from current premise: {service_data.get('name', 'Unknown')}"
                )
                service_connection = self._create_service_connection_from_data(
                    service_data, user_data
                )
                if service_connection:
                    all_service_connections.append(service_connection)

            # Then, check all other premises
            premises = user_data.get("premises", [])
            self.logger.debug(f"Found {len(premises)} total premises to check")

            for premise in premises:
                premise_url = premise.get("@id", "")
                premise_id = self._extract_id_from_url(premise_url)
                self.logger.debug(f"Checking premise: {premise_url}")

                # Skip the current premise (already processed above)
                current_premise_id = attributes.get("premise_id")
                if premise_id == current_premise_id:
                    self.logger.debug(
                        f"Skipping current premise {premise_id} (already processed)"
                    )
                    continue

                # Fetch premise data
                premise_data = self._get_premise_data(premise_id)
                if premise_data:
                    premise_service_connections = premise_data.get(
                        "service_connections", []
                    )
                    self.logger.debug(
                        f"Found {len(premise_service_connections)} service connections in premise {premise_id}"
                    )

                    for service_data in premise_service_connections:
                        self.logger.debug(
                            f"Processing service connection from premise {premise_id}: {service_data.get('name', 'Unknown')}"
                        )
                        service_connection = self._create_service_connection_from_data(
                            service_data, premise_data
                        )
                        if service_connection:
                            all_service_connections.append(service_connection)

            self.logger.debug(
                f"Total service connections found: {len(all_service_connections)}"
            )
            return all_service_connections if all_service_connections else None

        except (KeyError, ValueError, TypeError) as e:
            self.logger.debug(f"Error processing service connections: {e}")
            return None

    def _get_premise_data(self, premise_id: int) -> dict | None:
        """
        Get premise data from /api/premises/{id} endpoint

        Args:
            premise_id: The premise ID to fetch

        Returns:
            Premise data dictionary, or None if failed
        """
        if not self.logged_in:
            return None

        url = f"{self.base_url}/api/premises/{premise_id}"
        self.logger.debug(f"Fetching premise data from {url}")

        headers = {
            "accept": "application/vnd.dropcountr.api+json;version=2",
            "accept-language": "en-US,en;q=0.9",
            "referer": f"{self.base_url}/dashboard",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        }

        try:
            self.logger.debug(f"Sending GET request to /api/premises/{premise_id}")
            response = self.session.get(url, headers=headers)
            self.logger.debug(
                f"Premise {premise_id} response status: {response.status_code}"
            )
            response.raise_for_status()

            data = response.json()
            self.logger.debug(f"Premise {premise_id} response type: {type(data)}")

            # Handle both response formats like in get_user_data
            premise_data = None
            if isinstance(data, list) and len(data) == 2 and data[0] is True:
                premise_data = data[1]
                self.logger.debug(
                    f"Found premise {premise_id} data in old format [true, premise_data]"
                )
            elif isinstance(data, dict) and "data" in data:
                premise_data = data["data"]
                self.logger.debug(
                    f"Found premise {premise_id} data in new format with 'data' key"
                )
            else:
                self.logger.debug(
                    f"Unexpected premise {premise_id} response format: {type(data)}"
                )
                return None

            if premise_data:
                self.logger.debug(
                    f"Premise {premise_id} has {len(premise_data.get('service_connections', []))} service connections"
                )
                return dict(premise_data)

            return None

        except requests.RequestException as e:
            self.logger.debug(f"Error fetching premise {premise_id}: {e}")
            return None
        except (KeyError, ValueError, IndexError) as e:
            self.logger.debug(f"Error parsing premise {premise_id} data: {e}")
            return None

    def _create_service_connection_from_data(
        self, service_data: dict, context_data: dict
    ) -> ServiceConnection | None:
        """
        Create a ServiceConnection object from service data and context

        Args:
            service_data: Service connection data from API
            context_data: User or premise data for additional context (address, account info)

        Returns:
            ServiceConnection object or None if failed
        """
        try:
            connection_data = {
                "id": self._extract_id_from_url(service_data.get("@id", "")),
                "name": service_data.get("name", ""),
                "meter_id": service_data.get("meter_id", ""),
                "measurement_period": service_data.get("measurement_period", ""),
                "is_disconnected": service_data.get("is_disconnected", False),
                "@id": service_data.get("@id", ""),
            }

            # Get address from context (could be user data or premise data)
            address = ""
            if "address" in context_data:
                address_data = context_data.get("address", {})
                if isinstance(address_data, dict):
                    street = address_data.get("street", "")
                    city = address_data.get("city", "")
                    state = address_data.get("state", "")
                    zip_code = address_data.get("zip_code", "")

                    # Build full address
                    address_parts = [street]
                    if city:
                        address_parts.append(city)
                    if state:
                        if city:
                            address_parts[-1] = f"{city}, {state}"
                        else:
                            address_parts.append(state)
                    if zip_code:
                        address_parts.append(zip_code)

                    address = ", ".join(filter(None, address_parts))
                else:
                    address = str(address_data)
            elif "name" in context_data:
                address = context_data.get("name", "")

            # Get account info from context
            account_number = context_data.get("account_id", "")
            service_type = context_data.get("account_type", "")
            if not service_type and "attributes" in context_data:
                service_type = context_data.get("attributes", {}).get(
                    "account_type", ""
                )

            self.logger.debug(
                f"Service {connection_data['id']}: address='{address}', account='{account_number}', type='{service_type}'"
            )

            # Create ServiceConnection with available data
            service_connection = ServiceConnection(
                id=connection_data["id"],
                name=connection_data["name"],
                address=address,
                account_number=account_number,
                service_type=service_type,
                status="active"
                if not connection_data["is_disconnected"]
                else "disconnected",
                meter_serial=connection_data["meter_id"],
                api_id=connection_data["@id"],
            )

            return service_connection

        except (KeyError, ValueError, TypeError) as e:
            self.logger.debug(f"Error creating service connection: {e}")
            return None

    def _extract_id_from_url(self, url: str) -> int:
        """Extract numeric ID from API URL like https://dropcountr.com/api/service_connections/1258809"""
        if not url:
            return 0
        try:
            return int(url.split("/")[-1])
        except (ValueError, IndexError):
            return 0

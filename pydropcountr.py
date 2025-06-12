"""
PyDropCountr - Python library for interacting with dropcountr.com
"""

import requests
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass


@dataclass
class UsageData:
    """Represents a single usage data record from DropCountr"""
    during: str
    total_gallons: float
    irrigation_gallons: float
    irrigation_events: float
    is_leaking: bool
    
    @property
    def start_date(self) -> datetime:
        """Parse and return the start date from the during field"""
        return datetime.fromisoformat(self.during.split('/')[0].replace('Z', '+00:00'))
    
    @property
    def end_date(self) -> datetime:
        """Parse and return the end date from the during field"""
        return datetime.fromisoformat(self.during.split('/')[1].replace('Z', '+00:00'))


@dataclass
class UsageResponse:
    """Represents the full usage API response"""
    usage_data: List[UsageData]
    total_items: int
    api_id: str
    consumed_via_id: str


class DropCountrClient:
    """Client for interacting with the DropCountr.com API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://dropcountr.com"
        self.logged_in = False
    
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
    
    def get_usage(self, service_connection_id: int, start_date: str, end_date: str, period: str = "day") -> Optional[UsageResponse]:
        """
        Get usage data for a service connection
        
        Args:
            service_connection_id: The service connection ID
            start_date: Start date in ISO format (e.g., "2025-06-01T00:00:00.000Z")
            end_date: End date in ISO format (e.g., "2025-06-30T23:59:59.000Z")
            period: Period granularity ("day", "hour", etc.)
            
        Returns:
            UsageResponse object containing usage data, or None if failed
            
        Raises:
            requests.RequestException: If there's a network error
            ValueError: If not logged in
        """
        if not self.logged_in:
            raise ValueError("Must be logged in to fetch usage data")
        
        # Format the during parameter
        during = f"{start_date}/{end_date}"
        
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
        except (KeyError, ValueError) as e:
            return None
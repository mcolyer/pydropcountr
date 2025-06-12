"""
PyDropCountr - Python library for interacting with dropcountr.com
"""

import requests
from typing import Optional


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
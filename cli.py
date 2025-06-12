#!/usr/bin/env python3
"""
PyDropCountr CLI - Command line interface for DropCountr water usage monitoring
"""

import os
import sys
from datetime import datetime, timedelta

import fire

from pydropcountr import DropCountrClient


class DropCountrCLI:
    """Command line interface for DropCountr water usage monitoring"""

    def __init__(self):
        self.client = DropCountrClient()

    def _login(self, email: str | None = None, password: str | None = None) -> bool:
        """Handle login with credentials from args or environment variables"""
        # Try arguments first, then environment variables
        email = email or os.getenv("DROPCOUNTR_EMAIL")
        password = password or os.getenv("DROPCOUNTR_PASSWORD")

        if not email or not password:
            print("Error: Email and password required. Provide via:")
            print("  - Arguments: --email=your@email.com --password=yourpass")
            print("  - Environment: DROPCOUNTR_EMAIL and DROPCOUNTR_PASSWORD")
            sys.exit(1)

        try:
            success = self.client.login(email, password)
            if not success:
                print("Error: Login failed. Check your credentials.")
                sys.exit(1)
            return True
        except Exception as e:
            print(f"Error: Login failed - {e}")
            sys.exit(1)

    def _get_service_id(self, service_id: int | None = None) -> int:
        """Get service ID from argument or use first available service"""
        if service_id is not None:
            return service_id

        # Get first service connection
        try:
            services = self.client.list_service_connections()
            if not services:
                print("Error: No service connections found")
                sys.exit(1)

            service = services[0]
            print(f"Using service: {service.name} (ID: {service.id})")
            return service.id
        except Exception as e:
            print(f"Error: Failed to get service connections - {e}")
            sys.exit(1)

    def _format_usage_data(self, usage_data, title: str):
        """Format and display usage data"""
        if not usage_data:
            print(f"{title}: No data available")
            return

        print(f"\n{title}:")
        total_gallons = 0
        for record in usage_data:
            date_str = record.start_date.strftime("%Y-%m-%d")
            gallons = record.total_gallons
            total_gallons += gallons
            leak_indicator = " 🚨" if record.is_leaking else ""
            print(f"  {date_str}: {gallons:,.1f} gallons{leak_indicator}")

        print(f"  Total: {total_gallons:,.1f} gallons")
        return total_gallons

    def usage(
        self,
        email: str | None = None,
        password: str | None = None,
        service_id: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        period: str = "day",
        days: int | None = None,
    ):
        """
        Get water usage data (default: yesterday + last 7 days)

        Args:
            email: DropCountr email (or set DROPCOUNTR_EMAIL env var)
            password: DropCountr password (or set DROPCOUNTR_PASSWORD env var)
            service_id: Service connection ID (uses first service if not specified)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            period: Data granularity ("day" or "hour")
            days: Number of days back from today (overrides start_date/end_date)

        Examples:
            # Default: Show yesterday + last 7 days
            dropcountr usage

            # Show last 30 days
            dropcountr usage --days=30

            # Show specific date range
            dropcountr usage --start_date=2025-06-01 --end_date=2025-06-15

            # Use specific service
            dropcountr usage --service_id=1234567
        """
        # Login
        self._login(email, password)

        # Get service ID
        actual_service_id = self._get_service_id(service_id)

        # Determine date range
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if days is not None:
            # Use days parameter
            end_dt = today - timedelta(days=1)  # Yesterday
            start_dt = today - timedelta(days=days)
        elif start_date and end_date:
            # Use specific date range
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59
            )
        else:
            # Default: yesterday + last 7 days
            yesterday = today - timedelta(days=1)
            week_ago = today - timedelta(days=7)

            # Show yesterday first
            print("=" * 50)
            try:
                yesterday_usage = self.client.get_usage(
                    actual_service_id,
                    yesterday,
                    yesterday.replace(hour=23, minute=59, second=59),
                    period,
                )
                if yesterday_usage and yesterday_usage.usage_data:
                    self._format_usage_data(yesterday_usage.usage_data, "Yesterday")
                else:
                    print("Yesterday: No data available")
            except Exception as e:
                print(f"Error getting yesterday's usage: {e}")

            # Show last 7 days
            print("=" * 50)
            start_dt = week_ago
            end_dt = yesterday.replace(hour=23, minute=59, second=59)

        # Get and display usage data
        try:
            usage = self.client.get_usage(actual_service_id, start_dt, end_dt, period)

            if usage and usage.usage_data:
                date_range = f"{start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}"
                if not (start_date or end_date or days):
                    date_range = "Last 7 Days"
                self._format_usage_data(usage.usage_data, date_range)
            else:
                print("No usage data available for the specified period")

        except Exception as e:
            print(f"Error: Failed to get usage data - {e}")
            sys.exit(1)

    def services(
        self,
        email: str | None = None,
        password: str | None = None,
    ):
        """
        List all service connections

        Args:
            email: DropCountr email (or set DROPCOUNTR_EMAIL env var)
            password: DropCountr password (or set DROPCOUNTR_PASSWORD env var)
        """
        # Login
        self._login(email, password)

        try:
            services = self.client.list_service_connections()
            if not services:
                print("No service connections found")
                return

            print(f"Found {len(services)} service connection(s):")
            print("=" * 60)
            for service in services:
                print(f"ID: {service.id}")
                print(f"Name: {service.name}")
                print(f"Address: {service.address}")
                if service.account_number:
                    print(f"Account: {service.account_number}")
                if service.status:
                    print(f"Status: {service.status}")
                print("-" * 40)

        except Exception as e:
            print(f"Error: Failed to get service connections - {e}")
            sys.exit(1)


def main():
    """Main CLI entry point"""
    fire.Fire(DropCountrCLI)


if __name__ == "__main__":
    main()

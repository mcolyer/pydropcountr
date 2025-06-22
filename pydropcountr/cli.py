#!/usr/bin/env python3
"""
PyDropCountr CLI - Command line interface for DropCountr water usage monitoring
"""

import logging
import os
import sys
from datetime import datetime, timedelta

import fire

from .pydropcountr import DropCountrClient, ServiceConnection


class DropCountrCLI:
    """Command line interface for DropCountr water usage monitoring"""

    def __init__(self, debug: bool = False):
        self.debug = debug
        if debug:
            logging.basicConfig(
                level=logging.DEBUG, format="%(levelname)s: %(message)s"
            )
            print("Debug mode enabled")
        else:
            logging.basicConfig(
                level=logging.WARNING, format="%(levelname)s: %(message)s"
            )

        self.logger = logging.getLogger(__name__)
        self.client = DropCountrClient()

        if debug:
            self.logger.debug("DropCountrCLI initialized with debug mode")

    def _login(self, email: str | None = None, password: str | None = None) -> bool:
        """Handle login with credentials from args or environment variables"""
        # Try arguments first, then environment variables
        email = email or os.getenv("DROPCOUNTR_EMAIL")
        password = password or os.getenv("DROPCOUNTR_PASSWORD")

        # Safe debug logging for email
        if email and "@" in email:
            email_debug = f"{email[:3]}***@{email.split('@')[1]}"
        else:
            email_debug = f"'{email}'" if email else "None"
        self.logger.debug(f"Login attempt with email: {email_debug}")

        if not email or not password:
            print("Error: Email and password required. Provide via:")
            print("  - Arguments: --email=your@email.com --password=yourpass")
            print("  - Environment: DROPCOUNTR_EMAIL and DROPCOUNTR_PASSWORD")
            sys.exit(1)

        try:
            self.logger.debug("Attempting login...")
            success = self.client.login(email, password)
            self.logger.debug(f"Login result: {success}")
            if not success:
                print("Error: Login failed. Check your credentials.")
                sys.exit(1)
            self.logger.debug("Login successful")
            return True
        except Exception as e:
            self.logger.debug(f"Login exception: {e}")
            print(f"Error: Login failed - {e}")
            sys.exit(1)

    def _get_service_id(self, service_id: int | None = None) -> int:
        """Get service ID from argument or use first available service"""
        if service_id is not None:
            self.logger.debug(f"Using provided service_id: {service_id}")
            # Get service details to show address
            service = self._get_service_details(service_id)
            if service:
                print(f"Using service: {service.name} (ID: {service.id})")
                print(f"Address: {service.address}")
            return service_id

        # Get first service connection
        try:
            self.logger.debug("Fetching service connections...")
            services = self.client.list_service_connections()
            self.logger.debug(
                f"Retrieved {len(services) if services else 0} service connections"
            )

            if not services:
                self.logger.debug("No service connections returned from API")
                print("Error: No service connections found")
                sys.exit(1)

            service = services[0]
            self.logger.debug(
                f"Using first service: {service.name} (ID: {service.id}) at {service.address}"
            )
            print(f"Using service: {service.name} (ID: {service.id})")
            print(f"Address: {service.address}")
            return service.id
        except Exception as e:
            self.logger.debug(f"Exception getting service connections: {e}")
            print(f"Error: Failed to get service connections - {e}")
            sys.exit(1)

    def _get_service_details(self, service_id: int) -> ServiceConnection | None:
        """Get service connection details by ID"""
        try:
            self.logger.debug(f"Fetching details for service ID: {service_id}")
            services = self.client.list_service_connections()
            if services:
                for service in services:
                    if service.id == service_id:
                        self.logger.debug(
                            f"Found service {service_id}: {service.name} at {service.address}"
                        )
                        return service
            self.logger.debug(f"Service {service_id} not found")
            return None
        except Exception as e:
            self.logger.debug(f"Error getting service details for {service_id}: {e}")
            return None

    def _format_usage_data(
        self, usage_data: list, title: str, period: str = "day", verbose: bool = False
    ) -> float | None:
        """Format and display usage data"""
        if not usage_data:
            print(f"{title}: No data available")
            return None

        print(f"\n{title}:")
        total_gallons = 0
        for record in usage_data:
            if period == "hour":
                date_str = record.start_date.strftime("%Y-%m-%d %H:%M %Z")
            else:
                date_str = record.start_date.strftime("%Y-%m-%d")
            gallons = record.total_gallons
            total_gallons += gallons
            leak_indicator = " 🚨" if record.is_leaking else ""

            if verbose:
                # Show raw data
                print(f"  {date_str}: {gallons:,.1f} gallons{leak_indicator}")
                print(f"    Period: {record.during}")
                print(f"    Start date: {record.start_date}")
                print(f"    End date: {record.end_date}")
                print(f"    Total gallons: {record.total_gallons}")
                print(f"    Irrigation gallons: {record.irrigation_gallons}")
                print(f"    Irrigation events: {record.irrigation_events}")
                print(f"    Leak detected: {record.is_leaking}")
                print()
            else:
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
        verbose: bool = False,
    ) -> None:
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
            verbose: Show detailed raw API data

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
                    self._format_usage_data(
                        yesterday_usage.usage_data, "Yesterday", period, verbose
                    )
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
                date_range = (
                    f"{start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}"
                )
                if not (start_date or end_date or days):
                    date_range = "Last 7 Days"
                self._format_usage_data(usage.usage_data, date_range, period, verbose)
            else:
                print("No usage data available for the specified period")

        except Exception as e:
            print(f"Error: Failed to get usage data - {e}")
            sys.exit(1)

    def services(
        self,
        email: str | None = None,
        password: str | None = None,
    ) -> None:
        """
        List all service connections

        Args:
            email: DropCountr email (or set DROPCOUNTR_EMAIL env var)
            password: DropCountr password (or set DROPCOUNTR_PASSWORD env var)
        """
        # Login
        self.logger.debug("Services command: Starting login...")
        self._login(email, password)

        try:
            self.logger.debug("Services command: Fetching service connections...")
            services = self.client.list_service_connections()
            self.logger.debug(
                f"Services command: Retrieved {len(services) if services else 0} services"
            )

            if not services:
                self.logger.debug("Services command: No services found")
                print("No service connections found")
                return

            print(f"Found {len(services)} service connection(s):")
            print("=" * 60)
            for service in services:
                self.logger.debug(f"Service: ID={service.id}, Name={service.name}")
                print(f"ID: {service.id}")
                print(f"Name: {service.name}")
                print(f"Address: {service.address}")
                if service.account_number:
                    print(f"Account: {service.account_number}")
                if service.service_type:
                    print(f"Type: {service.service_type}")
                if service.status:
                    print(f"Status: {service.status}")
                print("-" * 40)

        except Exception as e:
            self.logger.debug(f"Services command exception: {e}")
            print(f"Error: Failed to get service connections - {e}")
            sys.exit(1)


def main() -> None:
    """Main CLI entry point"""
    import sys

    # Check for debug flag and remove it from sys.argv before Fire processes it
    debug = False
    if "--debug" in sys.argv:
        debug = True
        sys.argv.remove("--debug")

    # Create CLI instance with debug flag
    cli = DropCountrCLI(debug=debug)
    fire.Fire(cli)


if __name__ == "__main__":
    main()

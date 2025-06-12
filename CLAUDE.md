# PyDropCountr - Python Library for DropCountr.com

## Project Overview
This is a Python library for interacting with dropcountr.com, providing easy access to data through Python objects.

## Development Setup
- This project uses `uv` for dependency management
- Python 3.12+ required
- Run tests with: `uv run pytest` (when tests are implemented)
- Run linting with: `uv run ruff check` (when configured)

## API Information
- Login URL: https://dropcountr.com/login
- Login method: POST with email and password parameters
- Authentication: rack.session cookie must be maintained for subsequent requests

## Development Notes
- Keep authentication session state for API calls
- Implement proper error handling for login failures
- Return data as clean Python objects
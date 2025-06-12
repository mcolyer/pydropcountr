# Changelog

All notable changes to PyDropCountr will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Debug logging support with `--debug` flag for CLI troubleshooting
- Comprehensive logging throughout library and CLI for better error tracking
- Backward compatibility for API response format changes

### Fixed
- API response format handling for `/api/me` endpoint (changed from `[true, user_data]` to `{'data': user_data}`)
- Service connections discovery now works correctly with updated API format

### Changed
- Improved error messages and debugging capabilities

## [0.3.0] - 2025-06-12

### Added
- Comprehensive CLI interface using Fire library
- Default behavior showing yesterday + last 7 days usage
- Support for all CLI flags (email, password, service_id, dates, period)
- Environment variable support for credentials (DROPCOUNTR_EMAIL, DROPCOUNTR_PASSWORD)
- CLI entry point in pyproject.toml as `dropcountr` command

### Changed
- CLI now automatically selects first available service connection as default

## [0.2.0] - 2025-06-12

### Added
- Pydantic data models for type safety and validation
- Comprehensive README.md with usage examples
- GitHub Actions CI/CD pipeline with linting and testing
- Support for modern Python type hints (X | Y union syntax)
- Service connection management APIs (`list_service_connections`, `get_service_connection`)
- Support for Python datetime objects in `get_usage()` method (alongside ISO strings)
- Data validation constraints (e.g., gallons >= 0)

### Changed
- Migrated from dataclasses to Pydantic BaseModel for all data structures
- Updated to modern Python syntax throughout codebase
- Enhanced type hints and validation

### Fixed
- Date parameter handling now supports both datetime objects and ISO strings
- Improved error handling and validation

## [0.1.0] - 2025-05-25

### Added
- Initial PyDropCountr library implementation
- User authentication with login/logout functionality
- Session management with rack.session cookies
- Water usage data fetching with date ranges
- Structured data objects (ServiceConnection, UsageData, UsageResponse)
- Date parsing and validation utilities
- Support for uv dependency management
- Basic test suite

### Features
- Login to dropcountr.com with email/password
- Fetch usage data for service connections with flexible date ranges
- Parse usage data into clean Python objects
- Handle authentication state and session management
- Support for different time periods (day, hour)
- Irrigation and leak detection data parsing

---

## Release Guidelines

### Version Numbers
- **Major (X.y.z)**: Breaking changes to public API
- **Minor (x.Y.z)**: New features, backward compatible
- **Patch (x.y.Z)**: Bug fixes, backward compatible

### Change Categories
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

### Release Process
1. Update CHANGELOG.md with new version section
2. Move items from [Unreleased] to new version section
3. Update version in pyproject.toml
4. Create git tag with version number
5. Create GitHub release with changelog notes
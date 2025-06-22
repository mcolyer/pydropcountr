# Changelog

All notable changes to PyDropCountr will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-06-22

### Changed
- **BREAKING**: Fixed timezone handling for API datetime responses
- Datetime objects returned by `start_date` and `end_date` are now timezone-aware in local time instead of incorrectly parsed as UTC
- Added configurable timezone support to `DropCountrClient` constructor (defaults to `America/Los_Angeles`)
- API timestamps with 'Z' suffix are now correctly interpreted as local time rather than UTC

### Added
- Timezone configuration parameter to `DropCountrClient.__init__(timezone=...)`
- Support for custom timezones using IANA timezone names or `ZoneInfo` objects
- All datetime properties now return timezone-aware datetime objects

## [0.1.2] - 2025-06-12

### Fixed
- All MyPy type checking errors for improved code quality and IDE support
- Missing return type annotations throughout library and CLI
- Type compatibility issues in ServiceConnection instantiation
- Return type consistency across all public methods

## [0.1.1] - 2025-06-12

### Added
- GitHub Actions workflow for automated PyPI publishing with trusted publishing
- Debug logging support with `--debug` flag for CLI troubleshooting
- Comprehensive logging throughout library and CLI for better error tracking
- PUBLISHING.md guide for PyPI deployment and trusted publishing setup
- Support for multiple premises - now discovers all service connections across user's properties
- Complete address information (street, city, state, zip) in services and usage commands
- Service type information (Multi Family, Single Family) in services list
- Enhanced CLI with address display for better property identification

### Fixed
- API response format handling for `/api/me` endpoint (supports both old and new formats)
- Multiple premises support - fixed bug where only first premise's service connections were found
- Service connections discovery now works correctly across all user premises
- Email None handling in debug logging to prevent crashes with missing credentials
- Linting issues and code formatting for clean CI/CD runs

### Changed
- Restructured project as proper Python package with `pydropcountr/` directory
- Updated build system to use Hatchling with comprehensive PyPI metadata
- Improved error messages and debugging capabilities throughout
- Enhanced address display format with complete location information
- Updated CI workflow to work with new package structure and latest tooling

## [0.1.0] - 2025-06-12

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
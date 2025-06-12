# Publishing Guide

This document explains how to publish PyDropCountr to PyPI using GitHub Actions.

## GitHub Actions Workflows

### CI Workflow (`.github/workflows/ci.yml`)
Runs on every push and pull request:
- **Linting**: Ruff code formatting and style checks
- **Type checking**: MyPy static type analysis
- **Testing**: Basic functionality tests
- **Security**: Bandit security scanning
- **Multi-version**: Tests on Python 3.12 and 3.13

### Publish Workflow (`.github/workflows/publish.yml`)
Runs when version tags are pushed:
- **Testing**: Full test suite on multiple Python versions
- **Building**: Creates wheel and source distributions
- **Publishing**: Automatically uploads to PyPI using trusted publishing

## Setting Up PyPI Trusted Publishing

PyPI trusted publishing allows GitHub Actions to publish packages without storing API tokens as secrets.

### 1. Configure PyPI Project

1. Go to [PyPI](https://pypi.org) and create an account if needed
2. Create a new project for `pydropcountr` (or manage existing project)
3. Navigate to project settings → "Publishing" tab
4. Add a new trusted publisher with these settings:
   - **Owner**: `mcolyer`
   - **Repository name**: `pydropcountr`
   - **Workflow filename**: `publish.yml`
   - **Environment name**: `release`

### 2. GitHub Repository Settings

1. Go to repository Settings → Environments
2. Create a new environment named `release`
3. Configure protection rules (optional but recommended):
   - Required reviewers
   - Deployment branches (only `main`)

## Publishing Process

### Automatic Publishing (Recommended)

1. **Update version** in `pyproject.toml`:
   ```toml
   version = "0.2.0"
   ```

2. **Update CHANGELOG.md**:
   - Move items from `[Unreleased]` to new version section
   - Add release date

3. **Commit and tag**:
   ```bash
   git add .
   git commit -m "Release v0.2.0"
   git tag v0.2.0
   git push origin main
   git push origin v0.2.0
   ```

4. **GitHub Actions** will automatically:
   - Run full test suite
   - Build distributions
   - Publish to PyPI
   - Create GitHub release (if configured)

### Manual Publishing (Fallback)

If needed, you can still publish manually:

```bash
# Build distributions
uv run python -m build

# Check distributions
uv run twine check dist/*

# Upload to PyPI
uv run twine upload dist/*
```

## Version Management

### Version Numbering
Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (X.y.z): Breaking changes
- **MINOR** (x.Y.z): New features, backward compatible
- **PATCH** (x.y.Z): Bug fixes, backward compatible

### Pre-release Versions
For testing:
- **Alpha**: `0.2.0a1`
- **Beta**: `0.2.0b1`
- **Release Candidate**: `0.2.0rc1`

### Development Versions
For development snapshots:
- **Dev**: `0.2.0.dev1`

## Security Considerations

- **No API tokens**: Uses PyPI trusted publishing
- **Environment protection**: Release environment can have additional safeguards
- **Code scanning**: Bandit security linter runs on all changes
- **Dependency scanning**: GitHub Dependabot enabled

## Troubleshooting

### Failed Publishing
1. Check GitHub Actions logs
2. Verify PyPI trusted publisher configuration
3. Ensure version number is unique
4. Check for validation errors in distribution files

### Version Conflicts
```bash
# List existing versions
pip index versions pydropcountr

# Check PyPI project page
# https://pypi.org/project/pydropcountr/
```

### Testing New Versions
Use TestPyPI for testing:
```bash
# Upload to TestPyPI
uv run twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ pydropcountr
```
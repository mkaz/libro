# GitHub Actions CI/CD

This directory contains GitHub Actions workflows for automated testing, quality checks, and deployment.

## Workflows

### CI Pipeline (`ci.yml`)
**Triggered on:** Push to main/trunk/develop branches and all pull requests

**What it does:**
- Tests across Python 3.10, 3.11, and 3.12
- Runs linting with ruff (code style and formatting)
- Performs type checking with mypy
- Executes the complete test suite
- Tests basic CLI functionality
- Builds the package to ensure it's distributable

**Status:** Required for merging PRs

### Code Quality (`quality.yml`)
**Triggered on:** All pushes and pull requests

**What it does:**
- Fast quality checks on Python 3.11
- Code formatting verification
- Linting checks
- Type annotation validation
- Quick test run with early exit on failure

**Status:** Required for merging PRs

## Local Development

Before pushing changes, run the same checks locally:

```bash
# Run all CI checks
just ci

# Or run individual checks
just lint          # Linting and formatting
just type-check    # Type checking
just test          # Test suite
```

## Troubleshooting CI Failures

### Linting Failures
```bash
# Fix formatting issues
just lint-fix

# Check remaining issues
just lint
```

### Type Check Failures
```bash
# Run type checking locally
just type-check

# Common fixes:
# - Add missing type annotations
# - Fix return type mismatches
# - Handle Optional types properly
```

### Test Failures
```bash
# Run tests with verbose output
just test

# Run specific test file
uv run python -m pytest tests/test_models.py -v

# Run tests with debugging
uv run python -m pytest tests/ -v --tb=long
```

### Build Failures
```bash
# Test local build
just build

# Check dependencies
uv sync --dev
```

## CI Performance

- **Code Quality workflow:** ~30-45 seconds
- **Full CI pipeline:** ~2-3 minutes per Python version

The workflows are optimized for speed while maintaining comprehensive coverage.

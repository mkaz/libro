#!/usr/bin/env just --justfile
set quiet

# List all recipes
default:
    @just --list

# Run lint and format checks
lint:
    echo "Running ruff to check..."
    uv run python -m ruff check src/libro/
    uv run python -m ruff format --check src/libro/
    echo "."

# Fix lint and format checks
lint-fix:
    echo "Fixing lint issues..."
    uv run python -m ruff check --fix src/libro/
    uv run python -m ruff format src/libro/
    echo "."

# Run mypy typecheck
type-check:
    echo "Running mypy to type check..."
    uv run python -m mypy --package libro

# Run tests
test:
    echo "Running tests..."
    uv run python -m pytest tests/ -v

# Run all CI checks locally
ci: lint type-check test
    echo "All CI checks passed!"

# Clean Python artifacts
clean:
    echo "Cleaning..."
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    echo "."

# Install dependencies
install:
    echo "Installing dependencies"
    uv sync
    echo "."

# Install developer dependencies
dev-install:
    echo "Installing developer dependencies"
    uv sync --dev
    echo "."

# Build the project
build: clean lint dev-install
    echo "Building"
    uv run -m build
    echo "."

# Publish the project to PyPI
publish: build
    echo "Publishing to PyPI"
    uv run -m twine upload dist/*
    echo "."

# Run the CLI application
run *args:
    uv run libro {{args}}

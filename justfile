#!/usr/bin/env just --justfile
set quiet

# List all recipes
default:
    @just --list

# Run checks
lint:
    echo "Running ruff to lint..."
    uv run python -m ruff check src/libro/
    echo "."

# Run mypy typecheck
type-check:
    echo "Running mypy to type check..."
    uv run python -m mypy --package libro

# Clean Python artifacts
clean:
    echo "Cleaning..."
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    echo "."

## uv
# Uv runs the project out of the local .venv
# Create venv by running `uv venv`

# Install dependencies
install:
    echo "Installing dependencies"
    uv sync
    echo "."

# Build the project
build: clean lint install
    echo "Building"
    uv run -m build
    echo "."

# Publish the project to PyPI
publish: build
    echo "Publishing to PyPI 🚀"
    uv run -m twine upload dist/*
    echo "."

# Run the CLI application
run *args:
    uv run libro {{args}}

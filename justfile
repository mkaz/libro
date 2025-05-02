#!/usr/bin/env just --justfile
set quiet

# List all recipes
default:
    @just --list

# Run pre-commit checks
lint:
    echo "Linting 🔬"
    ruff check src/libro/
    echo "."

# Clean Python artifacts
clean:
    echo "Scrub a dub dub 🧼"
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
    echo "Installing dependencies 📦"
    uv sync
    echo "."

# Build the project
build: clean lint install
    echo "Building 📦"
    uv sync
    echo "."

# Publish the project to PyPI
publish: build
    echo "Publishing to PyPI 🚀"
    py -m twine upload dist/*
    echo "."

# Run the CLI application
run *args:
    uv run libro {{args}}

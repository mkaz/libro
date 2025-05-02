#!/usr/bin/env just --justfile

# List all recipes
default:
    @just --list

# Run pre-commit checks
lint:
    ruff check src/libro/

# Clean Python artifacts
clean:
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

## uv
# Uv runs the project out of the local .venv
# Create venv by running `uv venv`

# Build the project
install:
    uv sync

build: install
    uv build

# Run the CLI application
run *args:
    uv run libro {{args}}

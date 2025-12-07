#!/usr/bin/env just --justfile
set quiet

# List all recipes
default:
    @just --list

# Build the libro binary
build:
    echo "Building libro..."
    go build -o libro cmd/libro/main.go
    echo "Build complete: ./libro"

# Run the application
run *args:
    go run cmd/libro/main.go {{args}}

# Format Go code
fmt:
    echo "Formatting Go code..."
    go fmt ./...
    echo "."

vet:
    echo "Running go vet..."
    go vet ./...
    echo "."

# Run tests
test:
    echo "Running tests..."
    go test ./... -v

# Install dependencies
deps:
    echo "Downloading dependencies..."
    go mod download
    go mod tidy
    echo "."

# Run all checks (format, vet, test)
check: fmt vet test
    echo "All checks passed!"

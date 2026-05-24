#!/usr/bin/env just --justfile
set quiet

# List all recipes
default:
    @just --list

# Start dev server with hot-reload
dev:
    npm run dev

# Build and package production DMG
package:
    npm run package

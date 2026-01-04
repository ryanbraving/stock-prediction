#!/bin/bash

echo "Stopping and removing containers..."

# Stop containers
podman stop stock-backend stock-frontend 2>/dev/null || true

# Remove containers
podman rm stock-backend stock-frontend 2>/dev/null || true

# Remove network
podman network rm app-network 2>/dev/null || true

echo "Cleanup complete!"
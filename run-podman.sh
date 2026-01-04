#!/bin/bash

# Build and run with Podman
echo "Building containers with Podman..."

# Build backend
podman build -f Dockerfile.backend -t stock-prediction-backend .

# Build frontend  
podman build -f Dockerfile.frontend -t stock-prediction-frontend .

echo "Starting containers..."

# Create network
podman network create app-network 2>/dev/null || true

# Run backend
podman run -d \
  --name stock-backend \
  --network app-network \
  -p 8000:8000 \
  -v ./backend-drf:/app:Z \
  stock-prediction-backend

# Run frontend
podman run -d \
  --name stock-frontend \
  --network app-network \
  -p 3000:3000 \
  stock-prediction-frontend

echo "Containers started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"

# Show running containers
podman ps
#!/bin/bash

# Function to check if Docker daemon is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "Docker daemon is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to wait for a service to be available
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    echo "Waiting for $service_name to be available at $host:$port..."
    while ! nc -z "$host" "$port"; do
        echo "$service_name is not ready yet. Retrying in 1 second..."
        sleep 1
    done
    echo "$service_name is now available."
}

# Check Docker status
echo "Checking Docker daemon status..."
check_docker
echo "Docker is running."

# Create data directory
echo "Creating data directory..."
mkdir -p data

# Set the application port to 8000
export APP_PORT=8000

# Start services
echo "Starting services..."
docker-compose up -d --build

# Display message indicating the app is running on port 8000
echo "App is running on port $APP_PORT."

# Wait for Redis to be ready (using localhost)
wait_for_service "localhost" "6379" "Redis"

# Initialize database
echo "Initializing database..."
docker-compose exec app python -c "
from app.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
"

echo "Deployment completed successfully."
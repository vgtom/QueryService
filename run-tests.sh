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

# Create test docker-compose file
cat > docker-compose.test.yml << EOL
version: '3.8'

services:
  test-redis:
    image: redis:6-alpine
    ports:
      - "6380:6379"  # Different port to avoid conflicts with main redis

  tests:
    build: .
    command: pytest -v
    environment:
      - SQL_QUERY_MANAGER_SECRET_KEY=test-key
      - DATABASE_URL="sqlite:///:memory:"
      - REDIS_HOST=test-redis
      - REDIS_PORT=6379
    depends_on:
      - test-redis
EOL

# Start test environment
echo "Starting test environment..."
docker-compose -f docker-compose.test.yml up -d test-redis

# Wait for test Redis to be ready (using localhost and mapped port)
wait_for_service "localhost" "6380" "Test Redis"

# Run tests
echo "Running tests..."
docker-compose -f docker-compose.test.yml run --rm tests --build

# Cleanup
echo "Cleaning up test environment..."
docker-compose -f docker-compose.test.yml down -v

echo "Test run completed." 
#!/bin/bash
# Start the TerraFlow Analytics Docker stack

echo "Starting TerraFlow Analytics Docker Stack..."
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose down

# Pull latest images
echo "Pulling Docker images..."
docker-compose pull

# Start the stack
echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to initialize..."
sleep 30

# Check service status
echo ""
echo "Service Status:"
echo "=============================================="
docker-compose ps

echo ""
echo "Services are starting up. Access points:"
echo "  - Jupyter Notebook: http://localhost:8888"
echo "  - Spark Master UI: http://localhost:8080"
echo "  - HDFS NameNode UI: http://localhost:9870"
echo ""
echo "To view logs: docker-compose logs -f [service-name]"
echo "To stop stack: docker-compose down"
echo ""

# Get Jupyter token
echo "Retrieving Jupyter token..."
sleep 5
docker logs jupyter-pyspark 2>&1 | grep "token=" | tail -1

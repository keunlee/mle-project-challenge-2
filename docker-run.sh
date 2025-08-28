#!/bin/bash

# Docker run script for MLE Project Challenge 2
set -e

echo "Building and running MLE Project Challenge 2 Docker container..."

# Build the Docker image
echo "Building Docker image..."
docker build -t mle-project-challenge-2 .

# Run the container
echo "Starting container..."
docker run -d \
  --name mle-api \
  -p 8000:8000 \
  -v "$(pwd)/model:/app/model:ro" \
  -v "$(pwd)/data:/app/data:ro" \
  --restart unless-stopped \
  mle-project-challenge-2

echo "Container started successfully!"
echo "API available at: http://localhost:8000"
echo "API docs available at: http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "  View logs: docker logs -f mle-api"
echo "  Stop container: docker stop mle-api"
echo "  Remove container: docker rm mle-api"
echo "  Restart container: docker restart mle-api"

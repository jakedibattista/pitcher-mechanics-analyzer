#!/bin/bash

# Set proxy environment variables
export HTTP_PROXY="http://proxy.wal-mart.com:8080"
export HTTPS_PROXY="http://proxy.wal-mart.com:8080"
export NO_PROXY="localhost,127.0.0.1"

# Build the Docker image
docker build \
  --build-arg HTTP_PROXY=$HTTP_PROXY \
  --build-arg HTTPS_PROXY=$HTTPS_PROXY \
  --build-arg NO_PROXY=$NO_PROXY \
  --platform linux/amd64 \
  -t gcr.io/baseball-pitcher-analyzer/pitcher-analyzer .

# Make the script executable
chmod +x scripts/build_docker.sh 
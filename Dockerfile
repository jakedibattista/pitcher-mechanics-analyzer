# Use Python 3.9 slim image with specific platform
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set proxy environment variables if needed
ENV HTTP_PROXY="http://proxy.wal-mart.com:8080"
ENV HTTPS_PROXY="http://proxy.wal-mart.com:8080"
ENV NO_PROXY="localhost,127.0.0.1"

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

# Unset proxy variables for application runtime
ENV HTTP_PROXY=""
ENV HTTPS_PROXY=""
ENV NO_PROXY=""

# Copy the rest of the application
COPY . .

# Production settings
ENV PORT=8080
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Create directory for credentials
RUN mkdir -p /app/credentials

# Run Streamlit (simplified command)
CMD streamlit run pitcher_analyzer/streamlit_app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0

# Set environment variables
ENV PYTHONPATH=/app
ENV GCS_BUCKET=baseball-pitcher-analyzer-videos 
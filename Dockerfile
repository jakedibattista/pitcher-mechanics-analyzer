# Use Python 3.9 slim image with specific platform
FROM python:3.9-slim

# Set proxy environment variables for build process
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}
ENV NO_PROXY=${NO_PROXY}

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port for Streamlit
EXPOSE 8501

# Command to run the application
CMD streamlit run pitcher_analyzer/streamlit_app.py \
    --server.address=0.0.0.0

# Set environment variables
ENV PYTHONPATH=/app
ENV GCS_BUCKET=baseball-pitcher-analyzer-videos 
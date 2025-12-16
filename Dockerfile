# Dockerfile for running tests in containers

FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy test framework
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HEADLESS=true

# Run tests by default
CMD ["pytest", "-v", "-m", "smoke"]
# Use Python 3.9 as the base image
FROM python:3.9-slim

# Install system dependencies for portaudio
RUN apt-get update && apt-get install -y \
    build-essential \
    portaudio19-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a directory for the app
WORKDIR /app

# Copy requirements first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn  # Added Gunicorn here

# Copy the rest of the application
COPY . .

# Explicitly expose port (for documentation - Cloud Run uses $PORT)
EXPOSE 8080

# Use Gunicorn as the production server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "300", "--workers", "1", "app:app"]
# Docker & Dockerfile for optional containerization

FROM arm32v7/python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libatlas-base-dev \
    libjasper-dev \
    libtiff5 \
    libjasper1 \
    libharfbuzz0b \
    libwebp6 \
    libhdf5-dev \
    libopenjp2-7 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application
COPY backend /app/backend
COPY frontend /app/frontend

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "-u", "backend/app.py"]

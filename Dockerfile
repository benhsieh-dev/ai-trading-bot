# Use Python 3.11 slim image for better compatibility and smaller size
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Verify Node.js installation
RUN node --version && npm --version

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend package files for caching
COPY frontend/package*.json frontend/

# Install Node.js dependencies
RUN cd frontend && npm install

# Copy application code
COPY . .

# Build Angular app
RUN cd frontend && npm run build

# Verify Angular build
RUN ls -la frontend/dist/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port (Render uses PORT environment variable)
EXPOSE $PORT

# Health check to ensure the app is running (Render uses dynamic port)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/api/status || exit 1

# Default command to run the application
CMD ["python", "app.py"]
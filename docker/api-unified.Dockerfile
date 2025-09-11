# Nexus Platform - Unified API Service Dockerfile
# Combines FastAPI backend with integrated system features

FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY nexus_requirements_core.txt .
RUN pip install --no-cache-dir --user -r nexus_requirements_core.txt

# Production stage
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r nexus && useradd -r -g nexus nexus

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/nexus/.local

# Copy API service and related files
COPY nexus_web_launcher.py .
COPY nexus_system_integrator.py .
COPY NEXUS_app/backend/ ./backend/
COPY *.json .

# Set environment variables
ENV PATH=/home/nexus/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV FLASK_APP=nexus_web_launcher.py
ENV FLASK_ENV=production
ENV API_ENV=production
ENV NEXUS_APP_BACKEND=true

# Create logs directory
RUN mkdir -p /app/logs && chown -R nexus:nexus /app

# Change ownership to nexus user
RUN chown -R nexus:nexus /app

# Switch to non-root user
USER nexus

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the API service
CMD ["python", "nexus_web_launcher.py"]

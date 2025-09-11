#!/bin/bash
# Launch Optimized Docker Environment for Nexus Platform

set -e

echo "🚀 Launching Optimized Nexus Platform Docker Environment"

# Check if Docker is running
if ! /Applications/Docker.app/Contents/Resources/bin/docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create necessary directories
mkdir -p docker/configs/{postgres,grafana,prometheus}

# Set environment variables
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-"nexus_password123"}
export REDIS_PASSWORD=${REDIS_PASSWORD:-"redis_password123"}
export NEO4J_PASSWORD=${NEO4J_PASSWORD:-"neo4j_password123"}
export MINIO_ROOT_USER=${MINIO_ROOT_USER:-"nexus_admin"}
export MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD:-"minio_password123"}
export RABBITMQ_USER=${RABBITMQ_USER:-"nexus_user"}
export RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD:-"rabbitmq_password123"}
export GRAFANA_PASSWORD=${GRAFANA_PASSWORD:-"admin123"}
export WORKERS=${WORKERS:-4}

# Create PostgreSQL configuration
cat > docker/configs/postgres/postgresql.conf << EOF
# PostgreSQL Configuration for Nexus Platform
listen_addresses = '*'
port = 5432
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0
EOF

# Create PostgreSQL init script
cat > docker/configs/postgres/init.sql << EOF
-- Initialize Nexus Platform Database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create additional databases if needed
-- CREATE DATABASE nexus_analytics;
-- CREATE DATABASE nexus_logs;
EOF

# Create Prometheus configuration
cat > docker/configs/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'nexus-app'
    static_configs:
      - targets: ['nexus-app-opt:9090']
    scrape_interval: 10s
    metrics_path: /metrics
EOF

# Create Grafana datasource configuration
mkdir -p docker/configs/grafana/datasources
cat > docker/configs/grafana/datasources/prometheus.yml << EOF
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus-opt:9090
    access: proxy
    isDefault: true
EOF

# Create Grafana dashboard directory
mkdir -p docker/configs/grafana/dashboards

# Build the optimized Docker image
echo "🔨 Building optimized Nexus App image..."
/Applications/Docker.app/Contents/Resources/bin/docker build -f docker/Dockerfile.optimized -t nexus-app:optimized ../NEXUS_app/backend/

# Stop any existing containers
echo "🛑 Stopping existing containers..."
/Applications/Docker.app/Contents/Resources/bin/docker-compose -f docker//Applications/Docker.app/Contents/Resources/bin/docker-compose.optimized.yml down --remove-orphans || true

# Start the optimized environment
echo "🚀 Starting optimized Nexus Platform..."
/Applications/Docker.app/Contents/Resources/bin/docker-compose -f docker//Applications/Docker.app/Contents/Resources/bin/docker-compose.optimized.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
/Applications/Docker.app/Contents/Resources/bin/docker-compose -f docker//Applications/Docker.app/Contents/Resources/bin/docker-compose.optimized.yml ps

# Display access information
echo ""
echo "✅ Nexus Platform Optimized Environment Started!"
echo ""
echo "📊 Service Access URLs:"
echo "  �� Nexus App:        http://localhost:8000"
echo "  📈 Grafana:          http://localhost:3000 (admin/admin123)"
echo "  📊 Prometheus:       http://localhost:9090"
echo "  🐘 PostgreSQL:       localhost:5432"
echo "  🔴 Redis:            localhost:6379"
echo "  🦄 Neo4j:            http://localhost:7474"
echo "  �� MinIO:            http://localhost:9001"
echo "  🐰 RabbitMQ:         http://localhost:15672"
echo ""
echo "🔧 Useful Commands:"
echo "  View logs:           /Applications/Docker.app/Contents/Resources/bin/docker-compose -f docker//Applications/Docker.app/Contents/Resources/bin/docker-compose.optimized.yml logs -f"
echo "  Stop services:       /Applications/Docker.app/Contents/Resources/bin/docker-compose -f docker//Applications/Docker.app/Contents/Resources/bin/docker-compose.optimized.yml down"
echo "  Restart services:    /Applications/Docker.app/Contents/Resources/bin/docker-compose -f docker//Applications/Docker.app/Contents/Resources/bin/docker-compose.optimized.yml restart"
echo "  Scale app:           /Applications/Docker.app/Contents/Resources/bin/docker-compose -f docker//Applications/Docker.app/Contents/Resources/bin/docker-compose.optimized.yml up -d --scale nexus-app=3"
echo ""
echo "🎯 Environment Variables:"
echo "  WORKERS=$WORKERS"
echo "  POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
echo "  REDIS_PASSWORD=$REDIS_PASSWORD"
echo ""
```


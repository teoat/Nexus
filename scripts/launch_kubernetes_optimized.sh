#!/bin/bash
# Launch Optimized Kubernetes Environment for Nexus Platform

set -e

echo "�� Launching Optimized Nexus Platform Kubernetes Environment"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Kubernetes cluster is not accessible. Please check your cluster connection."
    exit 1
fi

# Create namespace and apply configurations
echo "📦 Creating namespace and applying configurations..."

# Apply namespace and resource quotas
kubectl apply -f k8s/optimized/namespace.yaml

# Apply secrets and configmaps
kubectl apply -f k8s/optimized/secrets.yaml

# Apply infrastructure services
kubectl apply -f k8s/optimized/postgresql.yaml
kubectl apply -f k8s/optimized/redis.yaml

# Wait for infrastructure to be ready
echo "⏳ Waiting for infrastructure services to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/postgresql -n nexus-platform
kubectl wait --for=condition=available --timeout=300s deployment/redis -n nexus-platform

# Build and push Docker image (if registry is configured)
echo "🔨 Building and pushing Nexus App image..."
# Uncomment the following lines if you have a container registry configured
# docker build -f docker/Dockerfile.optimized -t your-registry/nexus-app:optimized ../NEXUS_app/backend/
# docker push your-registry/nexus-app:optimized

# Apply application services
kubectl apply -f k8s/optimized/nexus-app.yaml
kubectl apply -f k8s/optimized/monitoring.yaml

# Wait for application to be ready
echo "⏳ Waiting for application services to be ready..."
kubectl wait -

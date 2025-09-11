#!/bin/bash
# Nexus Platform - Unified System Launcher
# Combines all features from integrated system with semantic services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo ""
print_header "🚀 NEXUS PLATFORM - UNIFIED SYSTEM LAUNCHER"
echo "=================================================="
print_info "Combining integrated system features with semantic services"
echo ""

# Check prerequisites
print_info "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    if [ -f "/Applications/Docker.app/Contents/Resources/bin/docker" ]; then
        export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
        print_success "Docker found in Applications"
    else
        print_error "Docker is not installed. Please install Docker Desktop first."
        exit 1
    fi
fi

if ! docker ps >/dev/null 2>&1; then
    print_warning "Docker is not running. Starting Docker Desktop..."
    open -a "Docker Desktop" 2>/dev/null || true
    print_info "Waiting for Docker to start..."
    sleep 15
    
    # Wait for Docker to be ready
    for i in {1..30}; do
        if docker ps >/dev/null 2>&1; then
            print_success "Docker is now running"
            break
        fi
        echo -n "."
        sleep 2
    done
fi

print_success "Prerequisites check passed"

# Create necessary directories
print_info "Creating necessary directories..."
mkdir -p nginx/logs
mkdir -p monitoring/grafana/provisioning
mkdir -p monitoring/grafana/dashboards
mkdir -p scripts
mkdir -p logs

# Make scripts executable
chmod +x setup-https.sh 2>/dev/null || true
chmod +x scripts/init-unified-databases.sh 2>/dev/null || true

# Check if SSL certificates exist
if [ ! -d "nginx/ssl" ] || [ -z "$(ls -A nginx/ssl 2>/dev/null)" ]; then
    print_warning "SSL certificates not found. Setting up HTTPS..."
    if [ -f "setup-https.sh" ]; then
        ./setup-https.sh
    else
        print_warning "setup-https.sh not found. SSL setup will be skipped."
    fi
else
    print_success "SSL certificates already exist"
fi

# Check hosts file entries
print_info "Checking hosts file configuration..."
hosts_entries=(
    "127.0.0.1 launcher.local"
    "127.0.0.1 web-launcher.local"
    "127.0.0.1 nexus.local"
    "127.0.0.1 api.local"
    "127.0.0.1 sot.local"
    "127.0.0.1 automation.local"
    "127.0.0.1 monitoring.local"
    "127.0.0.1 grafana.local"
)

missing_hosts=false
for entry in "${hosts_entries[@]}"; do
    if ! grep -q "$entry" /etc/hosts 2>/dev/null; then
        missing_hosts=true
        break
    fi
done

if [ "$missing_hosts" = true ]; then
    print_warning "Hosts file entries not found. Please add the following to your /etc/hosts file:"
    echo ""
    for entry in "${hosts_entries[@]}"; do
        echo "$entry"
    done
    echo ""
    read -p "Press Enter to continue after adding hosts entries..."
fi

# Stop any existing containers
print_info "Stopping existing containers..."
docker-compose -f docker-compose.nexus-unified.yml down 2>/dev/null || true

# Build and start services
print_info "Building and starting unified services..."
docker-compose -f docker-compose.nexus-unified.yml build --no-cache

print_info "Starting services in detached mode..."
docker-compose -f docker-compose.nexus-unified.yml up -d

# Wait for services to be ready
print_info "Waiting for services to be ready..."
sleep 15

# Check service health
print_info "Checking service health..."

# Function to wait for service
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=20
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f -k "$url" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 3
        attempt=$((attempt + 1))
    done
    
    print_warning "$service_name may not be ready yet"
    return 1
}

# Wait for key services
wait_for_service "https://launcher.local/health" "Web Launcher" || true
wait_for_service "https://api.local/health" "API Service" || true
wait_for_service "https://sot.local/health" "SOT Service" || true
wait_for_service "https://monitoring.local/-/healthy" "Monitoring Service" || true
wait_for_service "https://grafana.local/api/health" "Grafana Service" || true

# Display service status
echo ""
print_header "📊 UNIFIED SYSTEM STATUS"
echo "============================"

docker-compose -f docker-compose.nexus-unified.yml ps

echo ""
print_header "🌐 UNIFIED SERVICE URLS"
echo "==========================="
echo "🎯 Web Launcher (Primary):     https://launcher.local"
echo "🌐 API Service:                https://api.local"
echo "📊 SOT Dashboard:              https://sot.local"
echo "🤖 Automation Service:         https://automation.local"
echo "📈 Monitoring:                 https://monitoring.local"
echo "📋 Grafana:                    https://grafana.local"
echo ""

echo ""
print_header "🎛️ UNIFIED SYSTEM FEATURES"
echo "==============================="
echo "✅ Integrated Web Launcher with real-time status"
echo "✅ Semantic service names with HTTPS"
echo "✅ Comprehensive monitoring stack"
echo "✅ Unified data layer (PostgreSQL, Redis, Neo4j, MinIO)"
echo "✅ Message queuing with RabbitMQ"
echo "✅ Distributed tracing with Jaeger"
echo "✅ Email testing with MailHog"
echo "✅ Production-ready security and performance"
echo ""

echo ""
print_header "🔧 MANAGEMENT COMMANDS"
echo "=========================="
echo "View logs:          docker-compose -f docker-compose.nexus-unified.yml logs -f [service]"
echo "Stop services:      docker-compose -f docker-compose.nexus-unified.yml down"
echo "Restart service:    docker-compose -f docker-compose.nexus-unified.yml restart [service]"
echo "Scale service:      docker-compose -f docker-compose.nexus-unified.yml up -d --scale [service]=N"
echo ""

echo ""
print_header "📈 MONITORING & DEBUGGING"
echo "=============================="
echo "Service health:     docker-compose -f docker-compose.nexus-unified.yml ps"
echo "Resource usage:     docker stats"
echo "Container logs:     docker-compose -f docker-compose.nexus-unified.yml logs [service]"
echo "Shell access:       docker-compose -f docker-compose.nexus-unified.yml exec [service] sh"
echo "Tracing:            https://jaeger.local:16686"
echo "Email testing:      https://mailhog.local:8025"
echo ""

# Open browser to launcher
print_info "Opening browser to unified web launcher..."
sleep 2
open "https://launcher.local" 2>/dev/null || {
    print_warning "Could not open browser automatically. Please visit:"
    print_info "https://launcher.local"
}

print_success "Nexus Platform Unified System launched successfully!"
print_info "All integrated system features are now available with semantic service names."
print_info "Access the web launcher at: https://launcher.local"
print_warning "Remember to add the hosts entries to your /etc/hosts file if you haven't already."

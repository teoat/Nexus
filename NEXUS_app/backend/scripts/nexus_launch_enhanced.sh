#!/bin/bash

# Enhanced Nexus Platform Launcher
# Integrated Docker + Frenly AI + Frontend Launch with Browser Opening

set -ex

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_highlight() {
    echo -e "${PURPLE}[HIGHLIGHT]${NC} $1"
}

# Display header
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                🚀 NEXUS PLATFORM LAUNCHER 🚀                ║"
echo "║         Integrated Docker + Frenly AI + Frontend            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check prerequisites
print_status "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker and try again."
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_success "Docker is running"

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    print_error "Python is not installed. Please install Python and try again."
    exit 1
fi

print_success "Python is available"

# Navigate to project directory
cd "$(dirname "$0")"
print_status "Working directory: $(pwd)"

# Stage 1: Start Core Infrastructure Services
print_highlight "🗄️  STAGE 1: Starting Core Infrastructure Services"
cd ../../../nexus_docker
docker-compose up -d postgresql redis rabbitmq neo4j minio

# Wait for services to be healthy using a polling mechanism
print_status "⏳ Waiting for infrastructure services to become healthy..."
INFRA_SERVICES=("postgresql" "redis" "rabbitmq" "neo4j" "minio")
ALL_INFRA_HEALTHY=false
RETRIES=0
MAX_RETRIES=10 # Approximately 10 * 6 = 60 seconds of polling

while [ "$ALL_INFRA_HEALTHY" = false ] && [ "$RETRIES" -lt "$MAX_RETRIES" ]; do
    ALL_INFRA_HEALTHY=true
    for service in "${INFRA_SERVICES[@]}"; do
        # Get the full status line for the service from docker-compose ps
        SERVICE_LINE=$(docker-compose ps | grep "nexus-$service" | head -n 1)

        if [[ "$SERVICE_LINE" == *"healthy"* ]]; then
            print_status "$service is healthy"
        elif [[ "$SERVICE_LINE" == *"unhealthy"* ]]; then
            print_status "$service is unhealthy"
            ALL_INFRA_HEALTHY=false
        elif [[ "$SERVICE_LINE" == *"Exited"* ]]; then
            print_status "$service has exited"
            ALL_INFRA_HEALTHY=false
        else
            print_status "$service is not yet healthy (Current status: $SERVICE_LINE)"
            ALL_INFRA_HEALTHY=false
        fi
    done

    if [ "$ALL_INFRA_HEALTHY" = false ]; then
        RETRIES=$((RETRIES+1))
        sleep 6 # Poll every 6 seconds
    fi
done

if [ "$ALL_INFRA_HEALTHY" = false ]; then
    print_error "Infrastructure services failed to become healthy after $((MAX_RETRIES * 6)) seconds. Exiting."
    docker-compose ps
    exit 1
else
    print_success "All infrastructure services are healthy!"
fi

# Stage 2: Start Frenly AI Service
print_highlight "🤖 STAGE 2: Starting Frenly AI Service"

# Start Frenly AI using Docker Compose (already in nexus_docker directory)
docker-compose up -d frenly-ai

# Check Frenly AI initial logs for immediate errors
print_status "Checking Frenly AI initial logs..."
docker-compose logs frenly-ai

# Wait for Frenly AI to start
print_status "⏳ Waiting for Frenly AI to become healthy..."
sleep 5 # Give Frenly AI a bit more time before starting health checks

# Test Frenly AI health with retries
FRENLY_HEALTHY=false
MAX_FRENLY_RETRIES=20 # Increase retries to 100 seconds total (20 * 5s)
for i in {1..$MAX_FRENLY_RETRIES}; do
    # Use -f to fail silently on HTTP errors (4xx/5xx) and -s to suppress output
    # Check for HTTP 200 status code
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/health)
    if [ "$HTTP_STATUS" -eq 200 ]; then
        print_success "Frenly AI is healthy and responding"
        FRENLY_HEALTHY=true
        break
    else
        print_status "Frenly AI not ready yet (HTTP Status: $HTTP_STATUS), waiting... (attempt $i/$MAX_FRENLY_RETRIES)"
        echo "DEBUG: HTTP_STATUS = $HTTP_STATUS"
        sleep 5
    fi
done

if [ "$FRENLY_HEALTHY" = false ]; then
    print_error "Frenly AI failed to start properly after $((MAX_FRENLY_RETRIES * 5)) seconds"
    print_status "Checking Frenly AI logs..."
    docker-compose logs frenly-ai
    exit 1
fi

# Stage 3: Start Frontend Service
print_highlight "🌐 STAGE 3: Starting Frontend Service"

# Check if frontend directory exists
if [ ! -d "../NEXUS_app/frontend/web" ]; then
    print_error "Frontend directory not found: ../NEXUS_app/frontend/web"
    print_status "Available directories in NEXUS_app:"
    ls -la ../NEXUS_app/ | head -10
    exit 1
fi

cd ../NEXUS_app/frontend

# Kill any existing Node.js processes
pkill -f "node" 2>/dev/null || true
pkill -f "npm" 2>/dev/null || true

# Install npm dependencies if node_modules not present
if [ ! -d "node_modules" ]; then
    print_status "node_modules not found. Installing npm dependencies..."
    npm install
    print_success "npm dependencies installed."
fi

# Start Next.js development server for frontend
print_status "Starting Next.js frontend development server..."
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
print_status "Next.js frontend server started with PID: $FRONTEND_PID"

# Wait for frontend to start
print_status "⏳ Waiting for Next.js frontend to become healthy..."
NEXTJS_HEALTHY=false
MAX_NEXTJS_RETRIES=30 # 30 retries * 5 seconds = 150 seconds
for i in {1..$MAX_NEXTJS_RETRIES}; do
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
    if [ "$HTTP_STATUS" -eq 200 ]; then
        print_success "Next.js frontend is healthy and responding"
        NEXTJS_HEALTHY=true
        break
    else
        print_status "Next.js frontend not ready yet (HTTP Status: $HTTP_STATUS), waiting... (attempt $i/$MAX_NEXTJS_RETRIES)"
        sleep 5
    fi
done

if [ "$NEXTJS_HEALTHY" = false ]; then
    print_error "Next.js frontend failed to start properly after $((MAX_NEXTJS_RETRIES * 5)) seconds"
    print_status "Checking Next.js frontend logs..."
    cat /tmp/frontend.log
    exit 1
fi

# Stage 4: Display Service Status
print_highlight "📊 STAGE 4: Service Status Summary"
cd ../../../nexus_docker

echo ""
echo -e "${GREEN}✅ All Services Successfully Started!${NC}"
echo ""
echo "🗄️  Infrastructure Services:"
docker-compose ps | grep "nexus_" | while read line; do
    if echo "$line" | grep -q "healthy"; then
        echo -e "   ${GREEN}✅${NC} $(echo "$line" | awk '{print $1}' | sed 's/nexus_//g')"
    else
        echo -e "   ${YELLOW}⏳${NC} $(echo "$line" | awk '{print $1}' | sed 's/nexus_//g')"
    fi
done

echo ""
echo "🤖 AI Services:"
if curl -s http://localhost:8002/health > /dev/null; then
    echo -e "   ${GREEN}✅${NC} Frenly AI Service (Meta Agent Coordinator)"
else
    echo -e "   ${RED}❌${NC} Frenly AI Service"
fi

echo ""
echo "🌐 Frontend Services:"
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "   ${GREEN}✅${NC} Nexus Web Interface (Next.js)"
else
    echo -e "   ${RED}❌${NC} Nexus Web Interface (Next.js)"
fi

# Stage 5: Service Access Information
print_highlight "🌐 STAGE 5: Access Your Platform"

echo ""
echo "🌐 Main Access Points:"
echo -e "   ${BLUE}🔍 Nexus Platform:${NC}    http://localhost:3000"
echo -e "   ${BLUE}🤖 Frenly AI:${NC}         http://localhost:8002"
echo ""
echo "🗄️  Infrastructure Services:"
echo -e "   ${BLUE}🐘 PostgreSQL:${NC}        localhost:5432"
echo -e "   ${BLUE}🔴 Redis:${NC}             localhost:6379"
echo -e "   ${BLUE}🌐 Neo4j Browser:${NC}     http://localhost:7474"
echo -e "   ${BLUE}🐰 RabbitMQ Mgmt:${NC}     http://localhost:15672 (guest/guest)"
echo -e "   ${BLUE}🗂️  MinIO Console:${NC}     http://localhost:9001 (minioadmin/minioadmin)"

# Stage 6: Open Browser (macOS)
print_highlight "🌐 STAGE 6: Opening Browser to Starting Page"

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "http://localhost:3000"
    print_success "Browser opened to Nexus Platform main page"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:3000"
        print_success "Browser opened to Nexus Platform main page"
    else
        print_warning "Could not auto-open browser. Please manually visit: http://localhost:3000"
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows
    start "http://localhost:3000"
    print_success "Browser opened to Nexus Platform main page"
else
    print_warning "Unknown OS. Please manually visit: http://localhost:3000"
fi

# Save process ID for cleanup (only frontend has a PID since Frenly AI runs in Docker)
echo "$FRONTEND_PID" > /tmp/nexus-frontend-pid
echo "docker-frenly-ai" > /tmp/nexus-frenly-container
echo "Next.js frontend" > /tmp/nexus-frontend-type

echo ""
print_highlight "🎉 Nexus Platform Launch Complete!"
echo ""
echo "📚 Quick Start Guide:"
echo "   1. 🏠 Visit the main platform page (should already be open)"
echo "   2. 🤖 Test Frenly AI at http://localhost:8002"
echo "   3. 📊 Explore the platform features using the navigation tabs"
echo "   4. 🔍 Start with the 'Getting Started' section"
echo ""
echo "🛑 To stop all services:"
echo "   ./nexus_stop.sh"
echo ""
echo "📋 Useful commands:"
echo "   docker-compose ps              # Check Docker service status"
echo "   curl http://localhost:8002/status  # Check Frenly AI status"
echo "   docker-compose logs -f <service>   # View service logs"
echo ""
print_success "Platform ready for use! 🚀"

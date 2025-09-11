#!/bin/bash

# Nexus Platform Stop Script
# Gracefully stops all Nexus Platform services

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              🛑 STOPPING NEXUS PLATFORM 🛑              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Navigate to project directory
cd "$(dirname "$0")"
print_status "Working directory: $(pwd)"

# Stop Python services
print_status "Stopping Python services..."

# Stop Frenly AI
if [ -f /tmp/nexus-frenly-pid ]; then
    FRENLY_PID=$(cat /tmp/nexus-frenly-pid)
    if kill -0 "$FRENLY_PID" 2>/dev/null; then
        kill "$FRENLY_PID"
        print_success "Frenly AI service stopped (PID: $FRENLY_PID)"
    else
        print_warning "Frenly AI service was not running"
    fi
    rm -f /tmp/nexus-frenly-pid
fi

# Stop Frontend
if [ -f /tmp/nexus-frontend-pid ]; then
    FRONTEND_PID=$(cat /tmp/nexus-frontend-pid)
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID"
        print_success "Frontend service stopped (PID: $FRONTEND_PID)"
    else
        print_warning "Frontend service was not running"
    fi
    rm -f /tmp/nexus-frontend-pid
fi

# Cleanup any remaining processes
pkill -f "python main.py" 2>/dev/null || true
pkill -f "python -m http.server 3000" 2>/dev/null || true

# Stop Docker services
print_status "Stopping Docker services..."
cd nexus_docker
docker-compose down

print_success "All Nexus Platform services stopped successfully!"

echo ""
echo "🧹 Cleanup completed:"
echo "   - Docker containers stopped"
echo "   - Python processes terminated"
echo "   - Process ID files removed"
echo ""
echo "To restart the platform, run:"
echo "   ./nexus_launch_enhanced.sh"

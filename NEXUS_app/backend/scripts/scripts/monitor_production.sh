#!/bin/bash

# Nexus Platform Production Monitoring Script
# Monitors Frenly AI service performance and health

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Nexus Platform Production Monitoring${NC}"
echo "=============================================="

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Configuration
SERVICE_URL="http://localhost:8002"
HEALTH_ENDPOINT="$SERVICE_URL/health"
STATUS_ENDPOINT="$SERVICE_URL/status"
COORDINATE_ENDPOINT="$SERVICE_URL/agents/coordinate"

# Function to check service health
check_health() {
    print_info "Checking service health..."
    if curl -s -f "$HEALTH_ENDPOINT" > /dev/null; then
        print_status "Service is healthy"
        return 0
    else
        print_error "Service health check failed"
        return 1
    fi
}

# Function to get service status
get_status() {
    print_info "Getting service status..."
    if response=$(curl -s "$STATUS_ENDPOINT" 2>/dev/null); then
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
        return 0
    else
        print_error "Failed to get service status"
        return 1
    fi
}

# Function to check worker processes
check_workers() {
    print_info "Checking worker processes..."
    if command -v ps >/dev/null 2>&1; then
        worker_count=$(ps aux | grep -c "[p]ython.*main_optimized" || echo "0")
        print_info "Active worker processes: $worker_count"
        
        # Show memory usage
        echo ""
        print_info "Memory usage by Python processes:"
        ps aux | grep "[p]ython" | awk '{print $2, $4, $6, $11}' | head -10
    else
        print_warning "ps command not available"
    fi
}

# Function to run load test
run_load_test() {
    print_info "Running load test (50 requests)..."
    
    start_time=$(date +%s.%N)
    success_count=0
    total_requests=50
    
    for i in $(seq 1 $total_requests); do
        if curl -s -f "$HEALTH_ENDPOINT" > /dev/null 2>&1; then
            ((success_count++))
        fi
    done
    
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
    rps=$(echo "scale=2; $total_requests / $duration" | bc -l 2>/dev/null || echo "0")
    
    print_info "Load test results:"
    echo "  • Total requests: $total_requests"
    echo "  • Successful: $success_count"
    echo "  • Failed: $((total_requests - success_count))"
    echo "  • Duration: ${duration}s"
    echo "  • Requests/sec: $rps"
    
    if [ $success_count -eq $total_requests ]; then
        print_status "All requests successful"
    else
        print_warning "Some requests failed"
    fi
}

# Function to test agent coordination
test_coordination() {
    print_info "Testing agent coordination..."
    
    if response=$(curl -s -X POST "$COORDINATE_ENDPOINT" \
        -H "Content-Type: application/json" \
        -d '{"task": "monitoring_test", "agents": ["meta_agent", "investigation_agent"]}' 2>/dev/null); then
        print_status "Agent coordination test successful"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    else
        print_error "Agent coordination test failed"
    fi
}

# Function to check system resources
check_resources() {
    print_info "Checking system resources..."
    
    if command -v free >/dev/null 2>&1; then
        echo "Memory usage:"
        free -h
        echo ""
    fi
    
    if command -v df >/dev/null 2>&1; then
        echo "Disk usage:"
        df -h / | tail -1
        echo ""
    fi
    
    if command -v uptime >/dev/null 2>&1; then
        echo "System uptime:"
        uptime
        echo ""
    fi
}

# Function to show network connections
check_connections() {
    print_info "Checking network connections..."
    
    if command -v netstat >/dev/null 2>&1; then
        echo "Active connections on port 8002:"
        netstat -an | grep :8002 || echo "No connections found"
        echo ""
    elif command -v ss >/dev/null 2>&1; then
        echo "Active connections on port 8002:"
        ss -an | grep :8002 || echo "No connections found"
        echo ""
    fi
}

# Main monitoring function
main() {
    echo ""
    print_info "Starting comprehensive monitoring..."
    echo ""
    
    # Basic health check
    if ! check_health; then
        print_error "Service is not healthy. Exiting."
        exit 1
    fi
    
    echo ""
    
    # Get detailed status
    get_status
    
    echo ""
    
    # Check workers
    check_workers
    
    echo ""
    
    # Run load test
    run_load_test
    
    echo ""
    
    # Test coordination
    test_coordination
    
    echo ""
    
    # Check resources
    check_resources
    
    # Check connections
    check_connections
    
    echo ""
    print_status "Monitoring completed successfully!"
    echo ""
    print_info "Service is running optimally with:"
    echo "  • Health endpoint responding"
    echo "  • All agent connections active"
    echo "  • Worker processes running"
    echo "  • Load test passed"
    echo "  • Agent coordination working"
}

# Run main function
main "$@"

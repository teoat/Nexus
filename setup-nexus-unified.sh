#!/bin/bash
# Nexus Platform - Unified Setup Script
# Sets up HTTPS certificates and hosts entries for unified system

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

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
print_header "🔐 NEXUS PLATFORM - UNIFIED HTTPS SETUP"
echo "============================================="

# Check if mkcert is installed
if ! command -v mkcert &> /dev/null; then
    print_warning "mkcert is not installed. Installing..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install mkcert
        else
            print_error "Homebrew is required to install mkcert on macOS"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y mkcert
        else
            print_error "Package manager not supported. Please install mkcert manually."
            exit 1
        fi
    else
        print_error "Unsupported operating system. Please install mkcert manually."
        exit 1
    fi
else
    print_success "mkcert is already installed"
fi

# Create SSL directory
SSL_DIR="./nginx/ssl"
mkdir -p "$SSL_DIR"

print_info "Creating local CA..."
mkcert -install

print_info "Generating certificates for unified service names..."

# Generate certificates for all unified services
mkcert -cert-file "$SSL_DIR/launcher.local.crt" -key-file "$SSL_DIR/launcher.local.key" launcher.local
mkcert -cert-file "$SSL_DIR/web-launcher.local.crt" -key-file "$SSL_DIR/web-launcher.local.key" web-launcher.local
mkcert -cert-file "$SSL_DIR/nexus.local.crt" -key-file "$SSL_DIR/nexus.local.key" nexus.local
mkcert -cert-file "$SSL_DIR/api.local.crt" -key-file "$SSL_DIR/api.local.key" api.local
mkcert -cert-file "$SSL_DIR/sot.local.crt" -key-file "$SSL_DIR/sot.local.key" sot.local
mkcert -cert-file "$SSL_DIR/automation.local.crt" -key-file "$SSL_DIR/automation.local.key" automation.local
mkcert -cert-file "$SSL_DIR/monitoring.local.crt" -key-file "$SSL_DIR/monitoring.local.key" monitoring.local
mkcert -cert-file "$SSL_DIR/grafana.local.crt" -key-file "$SSL_DIR/grafana.local.key" grafana.local

# Set proper permissions
chmod 600 "$SSL_DIR"/*.key
chmod 644 "$SSL_DIR"/*.crt

print_success "SSL certificates generated successfully!"

echo ""
print_header "📝 HOSTS FILE ENTRIES"
echo "========================"
echo "Add the following entries to your /etc/hosts file:"
echo ""
echo "127.0.0.1 launcher.local"
echo "127.0.0.1 web-launcher.local"
echo "127.0.0.1 nexus.local"
echo "127.0.0.1 api.local"
echo "127.0.0.1 sot.local"
echo "127.0.0.1 automation.local"
echo "127.0.0.1 monitoring.local"
echo "127.0.0.1 grafana.local"
echo ""

print_success "Unified HTTPS setup complete!"
print_info "Next step: Run ./launch-nexus-unified.sh to start the unified system"

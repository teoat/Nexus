#!/bin/bash
# Nexus Platform - Archive Unused Files Script
# Archives legacy files and consolidates the system

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
print_header "🗄️ NEXUS PLATFORM - ARCHIVE UNUSED FILES"
echo "=============================================="

# Create archive directory
ARCHIVE_DIR="archived/unified-system-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$ARCHIVE_DIR"

print_info "Creating archive directory: $ARCHIVE_DIR"

# Archive old Docker Compose files
print_info "Archiving old Docker Compose files..."
if [ -f "docker-compose.semantic.yml" ]; then
    mv docker-compose.semantic.yml "$ARCHIVE_DIR/"
    print_success "Moved docker-compose.semantic.yml to archive"
fi

if [ -f "docker/docker-compose.simple.yml" ]; then
    mv docker/docker-compose.simple.yml "$ARCHIVE_DIR/"
    print_success "Moved docker/docker-compose.simple.yml to archive"
fi

if [ -f "docker/docker-compose.optimized.yml" ]; then
    mv docker/docker-compose.optimized.yml "$ARCHIVE_DIR/"
    print_success "Moved docker/docker-compose.optimized.yml to archive"
fi

# Archive old Nginx configurations
print_info "Archiving old Nginx configurations..."
if [ -f "nginx/nginx.conf" ]; then
    mv nginx/nginx.conf "$ARCHIVE_DIR/nginx-semantic.conf"
    print_success "Moved nginx/nginx.conf to archive"
fi

# Archive old launch scripts
print_info "Archiving old launch scripts..."
old_scripts=(
    "launch-semantic-services.sh"
    "quick-launch.sh"
    "implement-semantic-services.sh"
)

for script in "${old_scripts[@]}"; do
    if [ -f "$script" ]; then
        mv "$script" "$ARCHIVE_DIR/"
        print_success "Moved $script to archive"
    fi
done

# Archive old Dockerfiles
print_info "Archiving old Dockerfiles..."
old_dockerfiles=(
    "docker/api.Dockerfile"
    "docker/auth.Dockerfile"
    "docker/ui.Dockerfile"
    "docker/sot.Dockerfile"
)

for dockerfile in "${old_dockerfiles[@]}"; do
    if [ -f "$dockerfile" ]; then
        mv "$dockerfile" "$ARCHIVE_DIR/"
        print_success "Moved $dockerfile to archive"
    fi
done

# Archive old Kubernetes manifests
print_info "Archiving old Kubernetes manifests..."
if [ -d "k8s/optimized" ]; then
    mv k8s/optimized "$ARCHIVE_DIR/k8s-optimized"
    print_success "Moved k8s/optimized to archive"
fi

# Archive old documentation
print_info "Archiving old documentation..."
old_docs=(
    "Documentation.md"
    "LAUNCH_AND_TROUBLESHOOTING_GUIDE.md"
    "NEXUS_UNIFIED_SYSTEM_ANALYSIS.md"
    "hosts-configuration.txt"
)

for doc in "${old_docs[@]}"; do
    if [ -f "$doc" ]; then
        mv "$doc" "$ARCHIVE_DIR/"
        print_success "Moved $doc to archive"
    fi
done

# Archive old SOT files
print_info "Archiving old SOT files..."
old_sot_files=(
    "nexus_comprehensive_sot.json"
    "python_version_sot.json"
)

for sot_file in "${old_sot_files[@]}"; do
    if [ -f "$sot_file" ]; then
        mv "$sot_file" "$ARCHIVE_DIR/"
        print_success "Moved $sot_file to archive"
    fi
done

# Archive old monitoring configurations
print_info "Archiving old monitoring configurations..."
if [ -f "monitoring/prometheus.yml" ]; then
    mv monitoring/prometheus.yml "$ARCHIVE_DIR/prometheus-semantic.yml"
    print_success "Moved monitoring/prometheus.yml to archive"
fi

# Archive old scripts
print_info "Archiving old scripts..."
old_scripts_dir=(
    "scripts/init-multiple-databases.sh"
)

for script in "${old_scripts_dir[@]}"; do
    if [ -f "$script" ]; then
        mv "$script" "$ARCHIVE_DIR/"
        print_success "Moved $script to archive"
    fi
done

# Archive old setup scripts
print_info "Archiving old setup scripts..."
if [ -f "setup-https.sh" ]; then
    mv setup-https.sh "$ARCHIVE_DIR/"
    print_success "Moved setup-https.sh to archive"
fi

# Create archive manifest
print_info "Creating archive manifest..."
cat > "$ARCHIVE_DIR/ARCHIVE_MANIFEST.md" << EOF
# Archive Manifest - Nexus Platform Unified System

**Archive Date**: $(date)
**Archive Directory**: $ARCHIVE_DIR
**Reason**: Consolidation into unified system

## Archived Files

### Docker Compose Files
- docker-compose.semantic.yml
- docker/docker-compose.simple.yml
- docker/docker-compose.optimized.yml

### Nginx Configurations
- nginx/nginx.conf (semantic version)

### Launch Scripts
- launch-semantic-services.sh
- quick-launch.sh
- implement-semantic-services.sh

### Dockerfiles
- docker/api.Dockerfile
- docker/auth.Dockerfile
- docker/ui.Dockerfile
- docker/sot.Dockerfile

### Kubernetes Manifests
- k8s/optimized/ (entire directory)

### Documentation
- Documentation.md
- LAUNCH_AND_TROUBLESHOOTING_GUIDE.md
- NEXUS_UNIFIED_SYSTEM_ANALYSIS.md
- hosts-configuration.txt

### SOT Files
- nexus_comprehensive_sot.json
- python_version_sot.json

### Monitoring Configurations
- monitoring/prometheus.yml

### Scripts
- scripts/init-multiple-databases.sh
- setup-https.sh

## Replacement Files

These files have been replaced by the unified system:

- **docker-compose.nexus-unified.yml** - Unified Docker Compose configuration
- **nginx/nginx-unified.conf** - Unified Nginx configuration
- **launch-nexus-unified.sh** - Unified launch script
- **docker/web-launcher.Dockerfile** - Unified web launcher
- **docker/api-unified.Dockerfile** - Unified API service
- **k8s/unified/** - Unified Kubernetes manifests
- **nexus_unified_sot.json** - Unified SOT configuration
- **monitoring/prometheus-unified.yml** - Unified monitoring configuration

## Migration Notes

The unified system combines all features from the integrated system with semantic service names and production-ready optimizations. All functionality has been preserved and enhanced.

EOF

print_success "Created archive manifest: $ARCHIVE_DIR/ARCHIVE_MANIFEST.md"

# Create new unified setup script
print_info "Creating unified setup script..."
cat > setup-nexus-unified.sh << 'EOF'
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
EOF

chmod +x setup-nexus-unified.sh
print_success "Created unified setup script: setup-nexus-unified.sh"

# Create unified hosts configuration
print_info "Creating unified hosts configuration..."
cat > hosts-unified-configuration.txt << 'EOF'
# Nexus Platform Unified System - Hosts Configuration
# Add these entries to your hosts file for unified system access

# For macOS/Linux: /etc/hosts
# For Windows: C:\Windows\System32\drivers\etc\hosts

127.0.0.1 launcher.local
127.0.0.1 web-launcher.local
127.0.0.1 nexus.local
127.0.0.1 api.local
127.0.0.1 sot.local
127.0.0.1 automation.local
127.0.0.1 monitoring.local
127.0.0.1 grafana.local

# Instructions:
# 1. Copy the above entries (excluding comments)
# 2. Add them to your system's hosts file
# 3. Save the file (may require administrator/sudo privileges)
# 4. Test by running: ping launcher.local

# Verification commands:
# macOS/Linux: ping launcher.local
# Windows: ping launcher.local

# If you get "unknown host" errors, verify the hosts file was saved correctly
# and that your system is reading from the correct hosts file location.
EOF

print_success "Created unified hosts configuration: hosts-unified-configuration.txt"

# Display summary
echo ""
print_header "📊 ARCHIVE SUMMARY"
echo "===================="
print_success "Archive completed successfully!"
print_info "Archive location: $ARCHIVE_DIR"
print_info "Total files archived: $(find "$ARCHIVE_DIR" -type f | wc -l)"
echo ""
print_info "New unified files created:"
print_info "  - setup-nexus-unified.sh"
print_info "  - hosts-unified-configuration.txt"
echo ""
print_info "Next steps:"
print_info "  1. Run: ./setup-nexus-unified.sh"
print_info "  2. Add hosts entries from hosts-unified-configuration.txt"
print_info "  3. Run: ./launch-nexus-unified.sh"
echo ""

print_success "Archive and consolidation complete!"

#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
# File: NEXUS_app/scripts/start_production.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Nexus Platform API in Production Mode${NC}"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Error: main.py not found. Please run from the backend directory.${NC}"
    exit 1
fi

# Set environment variables
export ENVIRONMENT=production
export WORKERS=${WORKERS:-4}
export PORT=${PORT:-8000}
export LOG_LEVEL=${LOG_LEVEL:-info}

echo -e "${BLUE}Configuration:${NC}"
echo "  • Environment: $ENVIRONMENT"
echo "  • Workers: $WORKERS"
echo "  • Port: $PORT"
echo "  • Log Level: $LOG_LEVEL"
echo ""

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo -e "${YELLOW}⚠️  Gunicorn not found. Installing...${NC}"
    pip install gunicorn
fi

# Create logs directory
mkdir -p logs

# Start the application
echo -e "${GREEN}✅ Starting Gunicorn server...${NC}"
exec gunicorn \
    --config gunicorn.conf.py \
    --bind 0.0.0.0:$PORT \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level $LOG_LEVEL \
    --preload \
    main:app

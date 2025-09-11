#!/bin/bash

# Enhanced Continuous SOT Automation Launcher
# Integrates Tier 3 Redundancy with Single Source of Truth

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_PATH="$PROJECT_ROOT/nexus_env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
AUTOMATION_SCRIPT="enhanced_continuous_sot_automation.py"
CONFIG_FILE="enhanced_sot_config.json"
PID_FILE="enhanced_continuous_sot_automation.pid"
LOG_FILE="enhanced_continuous_sot_automation.log"
STATUS_FILE="enhanced_sot_status.json"

# Default parameters
DEFAULT_CYCLES=0
DEFAULT_INTERVAL=60
DEFAULT_MIN_TODOS=20
DEFAULT_MAX_TODOS=100
DEFAULT_MAX_WORKERS=20
DEFAULT_MAX_RETRIES=5

# Function to show usage
show_usage() {
    echo "Enhanced Continuous SOT Automation Launcher"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start       Start the enhanced SOT automation system"
    echo "  stop        Stop the enhanced SOT automation system"
    echo "  restart     Restart the enhanced SOT automation system"
    echo "  status      Show system status"
    echo "  logs        Show recent logs"
    echo "  monitor     Show real-time monitoring"
    echo "  health      Check system health"
    echo "  help        Show this help message"
    echo ""
    echo "Options for start command:"
    echo "  --cycles N              Maximum number of cycles (0 = infinite)"
    echo "  --interval N            Cycle interval in seconds"
    echo "  --min-todos N           Minimum todos per cycle"
    echo "  --max-todos N           Maximum todos per cycle"
    echo "  --max-workers N         Maximum number of workers"
    echo "  --max-retries N         Maximum retries for failed tasks"
    echo "  --enable-scaling        Enable auto-scaling"
    echo "  --enable-refinement     Enable refinement mode"
    echo "  --background            Run in background"
    echo ""
    echo "Examples:"
    echo "  $0 start --cycles 100 --interval 30 --min-todos 20 --max-todos 50"
    echo "  $0 start --enable-scaling --enable-refinement --background"
    echo "  $0 status"
    echo "  $0 logs"
}

# Function to check if system is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            # PID file exists but process is not running
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to activate virtual environment
activate_venv() {
    if [ -d "$VENV_PATH" ]; then
        log_info "Activating virtual environment: $VENV_PATH"
        export PATH="$VENV_PATH/bin:$PATH"
        export VIRTUAL_ENV="$VENV_PATH"
        return 0
    else
        log_error "Virtual environment not found: $VENV_PATH"
        log_info "Please create virtual environment first:"
        log_info "  python -m venv nexus_env"
        log_info "  source nexus_env/bin/activate"
        log_info "  pip install -r requirements.txt"
        return 1
    fi
}

# Function to check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        return 1
    fi
    
    # Check required Python packages
    local python_cmd="python3"
    if [ -d "$VENV_PATH" ] && [ -f "$VENV_PATH/bin/python" ]; then
        python_cmd="$VENV_PATH/bin/python"
    fi
    
    local required_packages=("psutil" "requests")
    for package in "${required_packages[@]}"; do
        if ! $python_cmd -c "import $package" 2>/dev/null; then
            log_error "Required package '$package' is not installed"
            log_info "Install with: $python_cmd -m pip install $package"
            return 1
        fi
    done
    
    log_success "All dependencies are available"
    return 0
}

# Function to start the system
start_system() {
    local cycles=$DEFAULT_CYCLES
    local interval=$DEFAULT_INTERVAL
    local min_todos=$DEFAULT_MIN_TODOS
    local max_todos=$DEFAULT_MAX_TODOS
    local max_workers=$DEFAULT_MAX_WORKERS
    local max_retries=$DEFAULT_MAX_RETRIES
    local enable_scaling=false
    local enable_refinement=false
    local background=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --cycles)
                cycles="$2"
                shift 2
                ;;
            --interval)
                interval="$2"
                shift 2
                ;;
            --min-todos)
                min_todos="$2"
                shift 2
                ;;
            --max-todos)
                max_todos="$2"
                shift 2
                ;;
            --max-workers)
                max_workers="$2"
                shift 2
                ;;
            --max-retries)
                max_retries="$2"
                shift 2
                ;;
            --enable-scaling)
                enable_scaling=true
                shift
                ;;
            --enable-refinement)
                enable_refinement=true
                shift
                ;;
            --background)
                background=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Check if already running
    if is_running; then
        log_warning "Enhanced SOT automation system is already running"
        local pid=$(cat "$PID_FILE")
        log_info "PID: $pid"
        return 0
    fi
    
    # Change to project directory
    cd "$PROJECT_ROOT"
    
    # Check dependencies
    if ! check_dependencies; then
        exit 1
    fi
    
    # Activate virtual environment (optional)
    activate_venv || log_info "Using system Python environment"
    
    # Check if automation script exists
    if [ ! -f "$AUTOMATION_SCRIPT" ]; then
        log_error "Automation script not found: $AUTOMATION_SCRIPT"
        exit 1
    fi
    
    # Check if config file exists
    if [ ! -f "$CONFIG_FILE" ]; then
        log_warning "Config file not found: $CONFIG_FILE"
        log_info "Using default configuration"
    fi
    
    # Build command
    local python_cmd="python3"
    if [ -d "$VENV_PATH" ] && [ -f "$VENV_PATH/bin/python" ]; then
        python_cmd="$VENV_PATH/bin/python"
    fi
    
    local cmd="$python_cmd $AUTOMATION_SCRIPT"
    cmd="$cmd --config $CONFIG_FILE"
    cmd="$cmd --cycles $cycles"
    cmd="$cmd --interval $interval"
    cmd="$cmd --min-todos $min_todos"
    cmd="$cmd --max-todos $max_todos"
    
    if [ "$enable_scaling" = true ]; then
        cmd="$cmd --enable-scaling"
    fi
    
    if [ "$enable_refinement" = true ]; then
        cmd="$cmd --enable-refinement"
    fi
    
    log_info "Starting Enhanced Continuous SOT Automation System..."
    log_info "Command: $cmd"
    log_info "Cycles: $cycles"
    log_info "Interval: ${interval}s"
    log_info "Min todos per cycle: $min_todos"
    log_info "Max todos per cycle: $max_todos"
    log_info "Auto-scaling: $enable_scaling"
    log_info "Refinement mode: $enable_refinement"
    
    # Start the system
    if [ "$background" = true ]; then
        log_info "Starting in background..."
        nohup $cmd > "$LOG_FILE" 2>&1 &
        local pid=$!
        echo $pid > "$PID_FILE"
        log_success "Enhanced SOT automation system started in background"
        log_info "PID: $pid"
        log_info "Log file: $LOG_FILE"
    else
        log_info "Starting in foreground..."
        exec $cmd
    fi
}

# Function to stop the system
stop_system() {
    if ! is_running; then
        log_warning "Enhanced SOT automation system is not running"
        return 0
    fi
    
    local pid=$(cat "$PID_FILE")
    log_info "Stopping Enhanced SOT automation system (PID: $pid)..."
    
    # Try graceful shutdown first
    kill -TERM "$pid" 2>/dev/null || true
    
    # Wait for graceful shutdown
    local count=0
    while [ $count -lt 10 ] && is_running; do
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if still running
    if is_running; then
        log_warning "Graceful shutdown failed, forcing kill..."
        kill -KILL "$pid" 2>/dev/null || true
        sleep 2
    fi
    
    # Clean up PID file
    if [ -f "$PID_FILE" ]; then
        rm -f "$PID_FILE"
    fi
    
    log_success "Enhanced SOT automation system stopped"
}

# Function to restart the system
restart_system() {
    log_info "Restarting Enhanced SOT automation system..."
    stop_system
    sleep 2
    start_system --background
}

# Function to show status
show_status() {
    echo "Enhanced Continuous SOT Automation System Status"
    echo "================================================"
    echo ""
    
    if is_running; then
        local pid=$(cat "$PID_FILE")
        log_success "System is RUNNING"
        echo "PID: $pid"
        
        # Show process info
        if command -v ps &> /dev/null; then
            echo ""
            echo "Process Information:"
            ps -p "$pid" -o pid,ppid,pcpu,pmem,etime,command 2>/dev/null || echo "Process info not available"
        fi
        
        # Show status file if exists
        if [ -f "$STATUS_FILE" ]; then
            echo ""
            echo "Status Information:"
            python3 -c "
import json
try:
    with open('$STATUS_FILE', 'r') as f:
        data = json.load(f)
    print(f\"System: {data.get('system_name', 'N/A')}\")
    print(f\"Version: {data.get('version', 'N/A')}\")
    print(f\"Status: {data.get('status', 'N/A')}\")
    print(f\"Cycle Count: {data.get('cycle_count', 0)}\")
    print(f\"Tasks Processed: {data.get('total_tasks_processed', 0)}\")
    print(f\"Tasks Completed: {data.get('total_tasks_completed', 0)}\")
    print(f\"Tasks Failed: {data.get('total_tasks_failed', 0)}\")
    print(f\"Uptime: {data.get('uptime', 0):.0f}s\")
    print(f\"SOT Authority: {data.get('sot_authority', False)}\")
    print(f\"Redundancy Level: {data.get('redundancy_level', 0)}\")
except Exception as e:
    print(f\"Error reading status: {e}\")
" 2>/dev/null || echo "Status file not readable"
        fi
        
    else
        log_error "System is NOT RUNNING"
        
        # Check if PID file exists
        if [ -f "$PID_FILE" ]; then
            log_warning "Stale PID file found: $PID_FILE"
        fi
    fi
    
    echo ""
    echo "Files:"
    echo "  PID file: $PID_FILE"
    echo "  Log file: $LOG_FILE"
    echo "  Status file: $STATUS_FILE"
    echo "  Config file: $CONFIG_FILE"
}

# Function to show logs
show_logs() {
    local lines=${1:-50}
    
    if [ ! -f "$LOG_FILE" ]; then
        log_error "Log file not found: $LOG_FILE"
        return 1
    fi
    
    echo "Recent logs (last $lines lines):"
    echo "================================"
    tail -n "$lines" "$LOG_FILE"
}

# Function to show real-time monitoring
show_monitor() {
    log_info "Starting real-time monitoring (Press Ctrl+C to stop)..."
    
    while true; do
        clear
        echo "Enhanced Continuous SOT Automation - Real-time Monitoring"
        echo "========================================================="
        echo "Time: $(date)"
        echo ""
        
        if is_running; then
            local pid=$(cat "$PID_FILE")
            echo "Status: RUNNING (PID: $pid)"
            
            # Show system resources
            if command -v top &> /dev/null; then
                echo ""
                echo "System Resources:"
                top -l 1 -n 0 | grep "CPU usage\|PhysMem" || echo "Resource info not available"
            fi
            
            # Show status file
            if [ -f "$STATUS_FILE" ]; then
                echo ""
                echo "Automation Status:"
                python3 -c "
import json
try:
    with open('$STATUS_FILE', 'r') as f:
        data = json.load(f)
    print(f\"  Tasks Processed: {data.get('total_tasks_processed', 0)}\")
    print(f\"  Tasks Completed: {data.get('total_tasks_completed', 0)}\")
    print(f\"  Tasks Failed: {data.get('total_tasks_failed', 0)}\")
    print(f\"  Cycle Count: {data.get('cycle_count', 0)}\")
    print(f\"  Uptime: {data.get('uptime', 0):.0f}s\")
    print(f\"  SOT Authority: {data.get('sot_authority', False)}\")
except Exception as e:
    print(f\"  Error reading status: {e}\")
" 2>/dev/null || echo "  Status not available"
            fi
            
        else
            echo "Status: NOT RUNNING"
        fi
        
        echo ""
        echo "Press Ctrl+C to stop monitoring..."
        
        sleep 5
    done
}

# Function to check health
check_health() {
    log_info "Checking system health..."
    
    # Check if system is running
    if ! is_running; then
        log_error "System is not running"
        return 1
    fi
    
    # Check log file
    if [ -f "$LOG_FILE" ]; then
        local log_size=$(wc -l < "$LOG_FILE" 2>/dev/null || echo "0")
        echo "Log file: $LOG_FILE ($log_size lines)"
        
        # Check for recent errors
        local error_count=$(grep -c "ERROR" "$LOG_FILE" 2>/dev/null || echo "0")
        if [ "$error_count" -gt 0 ]; then
            log_warning "Found $error_count errors in log file"
            echo "Recent errors:"
            grep "ERROR" "$LOG_FILE" | tail -5
        else
            log_success "No errors found in log file"
        fi
    else
        log_warning "Log file not found: $LOG_FILE"
    fi
    
    # Check status file
    if [ -f "$STATUS_FILE" ]; then
        echo "Status file: $STATUS_FILE"
        if python3 -c "import json; json.load(open('$STATUS_FILE'))" 2>/dev/null; then
            log_success "Status file is valid JSON"
        else
            log_error "Status file is not valid JSON"
        fi
    else
        log_warning "Status file not found: $STATUS_FILE"
    fi
    
    # Check SOT files
    if [ -f "nexus_enhanced_sot.json" ]; then
        echo "SOT file: nexus_enhanced_sot.json"
        if python3 -c "import json; json.load(open('nexus_enhanced_sot.json'))" 2>/dev/null; then
            log_success "SOT file is valid JSON"
        else
            log_error "SOT file is not valid JSON"
        fi
    else
        log_warning "SOT file not found: nexus_enhanced_sot.json"
    fi
    
    log_success "Health check completed"
}

# Main script logic
main() {
    case "${1:-help}" in
        start)
            shift
            start_system "$@"
            ;;
        stop)
            stop_system
            ;;
        restart)
            shift
            restart_system
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "${2:-50}"
            ;;
        monitor)
            show_monitor
            ;;
        health)
            check_health
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            log_error "Unknown command: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"

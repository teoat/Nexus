#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Process Monitor MCP Server
Tracks all running processes and ensures they follow the unified file organization structure.
"""

import asyncio
import json
import logging
import os
import psutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import mcp.server
import mcp.server.stdio
from mcp.server import NotificationOptions
from mcp import Resource, Tool

# Ensure log directory exists
log_dir = Path("data/logs")
log_dir.mkdir(parents=True, exist_ok=True)

# Configure logging to a shared file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=log_dir / "mcp_combined.log",
    filemode='a'
)
logger = logging.getLogger(__name__)

@dataclass
class ProcessInfo:
    """Information about a running process"""
    pid: int
    name: str
    cmdline: List[str]
    status: str
    cpu_percent: float
    memory_percent: float
    create_time: float
    working_directory: str
    file_paths: List[str] = None
    agent_id: Optional[str] = None
    task: Optional[str] = None
    
    def __post_init__(self):
        if self.file_paths is None:
            self.file_paths = []

class ProcessMonitor:
    """Monitors running processes and validates file organization compliance"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.processes: Dict[int, ProcessInfo] = {}
        self.process_file = self.workspace_path / ".mcp" / "processes.json"
        
        # Ensure MCP directory exists
        self.process_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Single source of truth files for validation
        self.sot_files = {
            "file_organization": "docs/UNIFIED_FILE_ORGANIZATION.md",
            "structure_analysis": "docs/FILE_STRUCTURE_ANALYSIS.md",
            "implementation_roadmap": "docs/IMPLEMENTATION_ROADMAP.md"
        }
        
        # Load existing process data
        self.load_processes()
    
    def load_processes(self):
        """Load existing process data from file"""
        try:
            if self.process_file.exists():
                with open(self.process_file, 'r') as f:
                    data = json.load(f)
                    for pid_str, process_data in data.items():
                        pid = int(pid_str)
                        self.processes[pid] = ProcessInfo(**process_data)
                logger.info(f"Loaded {len(self.processes)} existing processes")
        except Exception as e:
            logger.error(f"Error loading processes: {e}")
    
    def save_processes(self):
        """Save process data to file"""
        try:
            with open(self.process_file, 'w') as f:
                json.dump({str(pid): asdict(process) for pid, process in self.processes.items()}, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving processes: {e}")
    
    def scan_processes(self):
        """Scan all running processes"""
        current_pids = set()
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'create_time']):
            try:
                proc_info = proc.info
                pid = proc_info['pid']
                current_pids.add(pid)
                
                # Get additional process information
                try:
                    proc_obj = psutil.Process(pid)
                    cpu_percent = proc_obj.cpu_percent()
                    memory_percent = proc_obj.memory_percent()
                    working_directory = proc_obj.cwd()
                    
                    # Get open files
                    try:
                        open_files = proc_obj.open_files()
                        file_paths = [f.path for f in open_files if f.path]
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        file_paths = []
                    
                    # Check if this is a new process or update existing
                    if pid not in self.processes:
                        process_info = ProcessInfo(
                            pid=pid,
                            name=proc_info['name'],
                            cmdline=proc_info['cmdline'] or [],
                            status=proc_info['status'],
                            cpu_percent=cpu_percent,
                            memory_percent=memory_percent,
                            create_time=proc_info['create_time'],
                            working_directory=working_directory,
                            file_paths=file_paths
                        )
                        self.processes[pid] = process_info
                        logger.info(f"New process detected: {pid} - {proc_info['name']}")
                    else:
                        # Update existing process
                        existing = self.processes[pid]
                        existing.status = proc_info['status']
                        existing.cpu_percent = cpu_percent
                        existing.memory_percent = memory_percent
                        existing.file_paths = file_paths
                        existing.working_directory = working_directory
                
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Remove terminated processes
        terminated_pids = set(self.processes.keys()) - current_pids
        for pid in terminated_pids:
            process_name = self.processes[pid].name
            del self.processes[pid]
            logger.info(f"Process terminated: {pid} - {process_name}")
        
        # Save updated process data
        self.save_processes()
        
        return len(self.processes)
    
    def get_process_info(self, pid: int) -> Optional[ProcessInfo]:
        return self.processes.get(pid)
    
    def list_processes(self) -> List[ProcessInfo]:
        """List all monitored processes"""
        return list(self.processes.values())
    
    def find_processes_by_name(self, name: str) -> List[ProcessInfo]:
        """Find processes by name"""
        return [p for p in self.processes.values() if name.lower() in p.name.lower()]
    
    def find_processes_by_file(self, file_path: str) -> List[ProcessInfo]:
        return [p for p in self.processes.values() if file_path in p.file_paths]
    
    def validate_file_organization(self, file_path: str) -> Dict[str, Any]:
        """Validate if a file follows the unified organization structure"""
        full_path = Path(file_path)
        
        # Check if file is within workspace
        try:
            relative_path = full_path.relative_to(self.workspace_path)
        except ValueError:
            return {
                "file_path": str(full_path),
                "valid": False,
                "error": "File is outside workspace"
            }
        
        # Check naming conventions
        valid_naming = self._check_naming_conventions(relative_path)
        
        # Check directory structure
        valid_structure = self._check_directory_structure(relative_path)
        
        # Get recommendations
        recommendations = self._get_structure_recommendations(relative_path, valid_naming, valid_structure)
        
        return {
            "file_path": str(relative_path),
            "valid_naming": valid_naming,
            "valid_structure": valid_structure,
            "overall_valid": valid_naming and valid_structure,
            "recommendations": recommendations
        }
    
    def _check_naming_conventions(self, relative_path: Path) -> bool:
        """Check if file/directory names follow conventions"""
        for part in relative_path.parts:
            # Check for lowercase with underscores
            if not part.islower():
                return False
            
            # Check for valid characters (lowercase, numbers, underscores, hyphens)
            if not all(c.islower() or c.isdigit() or c in ['_', '-'] for c in part):
                return False
            
            if any(c in part for c in [' ', '(', ')', '[', ']', '{', '}', '&', '+', '=']):
                return False
        
        return True
    
    def _check_directory_structure(self, relative_path: Path) -> bool:
        """Check if file is in the correct directory according to unified organization"""
        path_str = str(relative_path)
        
        # Define valid directory patterns based on UNIFIED_FILE_ORGANIZATION.md
        valid_patterns = [
            "NEXUS_app/core/ai_engine/",
            "NEXUS_app/core/business_services/",
            "NEXUS_app/interfaces/api/",
            "NEXUS_app/interfaces/frontend/",
            "nexus_docker/services/",
            "docs/",
            "monitoring/",
            "automation/",
            "deployment/"
        ]
        
        return any(pattern in path_str for pattern in valid_patterns)
    
    def _get_structure_recommendations(self, relative_path: Path, valid_naming: bool, valid_structure: bool) -> List[str]:
        """Get recommendations for improving file organization"""
        recommendations = []
        
        if not valid_naming:
            recommendations.append("Rename to use lowercase with underscores only")
        
        if not valid_structure:
            recommendations.append("Move file to appropriate directory according to unified organization")
            recommendations.append("Review UNIFIED_FILE_ORGANIZATION.md for correct placement")
        
        file_extension = relative_path.suffix.lower()
        if file_extension in ['.py', '.js', '.ts', '.jsx', '.tsx']:
        
        if file_extension == '.md':
            if 'docs/' not in str(relative_path):
                recommendations.append("Documentation files should be in docs/ directory")
        
        return recommendations
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        total_processes = len(self.processes)
        high_cpu_processes = [p for p in self.processes.values() if p.cpu_percent > 80]
        high_memory_processes = [p for p in self.processes.values() if p.memory_percent > 80]
        
        # Check file organization compliance
        compliance_score = 0
        total_files = 0
        
        for process in self.processes.values():
            for file_path in process.file_paths:
                if file_path and Path(file_path).exists():
                    total_files += 1
                    validation = self.validate_file_organization(file_path)
                    if validation.get('overall_valid', False):
                        compliance_score += 1
        
        compliance_percentage = (compliance_score / total_files * 100) if total_files > 0 else 100
        
        return {
            "total_processes": total_processes,
            "high_cpu_processes": len(high_cpu_processes),
            "high_memory_processes": len(high_memory_processes),
            "file_organization_compliance": f"{compliance_percentage:.1f}%",
            "compliance_score": compliance_score,
            "total_files_checked": total_files,
            "timestamp": datetime.now().isoformat()
        }
    
    def log_activity(self, level: str, message: str, metadata: Dict[str, Any] = None):
        """Log process monitor activity using the centralized logger"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "metadata": metadata or {}
        }
        
        # Use the configured logger, which writes to mcp_combined.log
        if level == "info":
            logger.info(f"[ProcessMonitorActivity] {json.dumps(log_entry)}")
        elif level == "warning":
            logger.warning(f"[ProcessMonitorActivity] {json.dumps(log_entry)}")
        elif level == "error":
            logger.error(f"[ProcessMonitorActivity] {json.dumps(log_entry)}")
        else:
            logger.debug(f"[ProcessMonitorActivity] {json.dumps(log_entry)}")

# Global monitor instance
monitor = ProcessMonitor(os.getenv("PROCESS_MONITOR_WORKSPACE_PATH", "/Users/Arief/Desktop/Nexus"))

# MCP Server setup
server = mcp.server.Server("process-monitor")

@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="process://processes",
            name="Running Processes",
            description="List of all monitored processes",
            mimeType="application/json"
        ),
        Resource(
            uri="process://health",
            name="System Health",
            description="Overall system health metrics",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content"""
    if uri == "process://processes":
        processes = monitor.list_processes()
        return json.dumps([asdict(process) for process in processes], indent=2)
    elif uri == "process://health":
        health = monitor.get_system_health()
        return json.dumps(health, indent=2)
    else:
        raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="scan_processes",
            description="Scan and update all running processes",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="list_processes",
            description="List all monitored processes",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_process_info",
            inputSchema={
                "type": "object",
                "properties": {
                    "pid": {"type": "integer", "description": "Process ID"}
                },
                "required": ["pid"]
            }
        ),
        Tool(
            name="find_processes_by_name",
            description="Find processes by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Process name to search for"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="find_processes_by_file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "File path to search for"}
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="validate_file_organization",
            description="Validate if a file follows the unified organization structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to file to validate"}
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="get_system_health",
            description="Get overall system health metrics",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> str:
    """Execute tool calls"""
    try:
        if name == "scan_processes":
            count = monitor.scan_processes()
            monitor.log_activity("info", f"Process scan completed: {count} processes found")
            return f"Process scan completed: {count} processes found"
        
        elif name == "list_processes":
            processes = monitor.list_processes()
            return f"Monitored processes:\n{json.dumps([asdict(process) for process in processes], indent=2)}"
        
        elif name == "get_process_info":
            process = monitor.get_process_info(arguments["pid"])
            if process:
                return f"Process info:\n{json.dumps(asdict(process), indent=2)}"
            else:
                return "Process not found"
        
        elif name == "find_processes_by_name":
            processes = monitor.find_processes_by_name(arguments["name"])
            return f"Processes matching '{arguments['name']}':\n{json.dumps([asdict(process) for process in processes], indent=2)}"
        
        elif name == "find_processes_by_file":
            processes = monitor.find_processes_by_file(arguments["file_path"])
            return f"Processes with file '{arguments['file_path']}':\n{json.dumps([asdict(process) for process in processes], indent=2)}"
        
        elif name == "validate_file_organization":
            result = monitor.validate_file_organization(arguments["file_path"])
            return f"File organization validation:\n{json.dumps(result, indent=2)}"
        
        elif name == "get_system_health":
            health = monitor.get_system_health()
            return f"System health:\n{json.dumps(health, indent=2)}"
        
        else:
            return f"Unknown tool: {name}"
    
    except Exception as e:
        logger.error(f"Error in tool call {name}: {e}")
        return f"Error: {str(e)}"

async def main():
    """Main function to run the MCP server"""
    logger.info("Starting Process Monitor MCP Server...")
    
    # Initial process scan
    monitor.scan_processes()
    
    # Start the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            NotificationOptions()
        )

if __name__ == "__main__":
    asyncio.run(main())

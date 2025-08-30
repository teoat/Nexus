"""
Python-related tasks for the NexusX automation system.
"""

import asyncio
import logging
import os
import subprocess
import sys
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger("PythonTasks")

async def setup_python_env(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Set up the Python virtual environment for the project.
    
    Args:
        params: Task parameters including:
            - todo_id: ID of the todo item
            - python_version: Optional Python version to use (default: 3.12)
            
    Returns:
        Dict with success status and results
    """
    logger.info("Setting up Python environment")
    
    todo_id = params.get("todo_id")
    python_version = params.get("python_version", "3.12")
    project_root = params.get("project_root", os.getcwd())
    
    # Check for existing setup script
    setup_script = os.path.join(project_root, "scripts", "setup", "setup_nexus.sh")
    
    try:
        if os.path.exists(setup_script) and os.access(setup_script, os.X_OK):
            # Execute existing setup script
            logger.info(f"Executing setup script: {setup_script}")
            
            process = await asyncio.create_subprocess_shell(
                f"bash {setup_script}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info("Setup script executed successfully")
                return {
                    "success": True,
                    "todo_id": todo_id,
                    "output": stdout.decode() if stdout else "",
                    "env_path": os.path.join(project_root, "nexus_env")
                }
            else:
                logger.error(f"Setup script failed: {stderr.decode() if stderr else ''}")
                return {
                    "success": False,
                    "todo_id": todo_id,
                    "error": stderr.decode() if stderr else "Unknown error",
                    "output": stdout.decode() if stdout else ""
                }
        else:
            # No script found, create environment manually
            logger.info("No setup script found, creating environment manually")
            return await _create_python_env_manually(project_root, python_version, todo_id)
            
    except Exception as e:
        logger.exception("Error setting up Python environment")
        return {
            "success": False,
            "todo_id": todo_id,
            "error": str(e)
        }

async def _create_python_env_manually(project_root: str, python_version: str, todo_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create Python environment manually if setup script not available
    """
    env_path = os.path.join(project_root, "nexus_env")
    requirements_path = os.path.join(project_root, "requirements.txt")
    
    try:
        # Create venv
        logger.info(f"Creating Python virtual environment at {env_path}")
        
        # Determine Python executable
        python_cmd = f"python{python_version}"
        
        # Check if Python version exists
        process = await asyncio.create_subprocess_shell(
            f"{python_cmd} --version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        if process.returncode != 0:
            logger.warning(f"{python_cmd} not found, falling back to 'python'")
            python_cmd = "python"
        
        # Create virtual environment
        process = await asyncio.create_subprocess_shell(
            f"{python_cmd} -m venv {env_path}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Failed to create virtual environment: {stderr.decode() if stderr else ''}")
            return {
                "success": False,
                "todo_id": todo_id,
                "error": stderr.decode() if stderr else "Failed to create virtual environment"
            }
            
        # Install requirements if they exist
        if os.path.exists(requirements_path):
            logger.info(f"Installing requirements from {requirements_path}")
            
            pip_path = os.path.join(env_path, "bin", "pip") if os.name != "nt" else os.path.join(env_path, "Scripts", "pip.exe")
            
            process = await asyncio.create_subprocess_shell(
                f"{pip_path} install -r {requirements_path}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Failed to install requirements: {stderr.decode() if stderr else ''}")
                return {
                    "success": False,
                    "todo_id": todo_id,
                    "error": stderr.decode() if stderr else "Failed to install requirements"
                }
        
        # Make activation scripts executable
        for script in ["activate_nexus_env.sh", "nexus_python.sh"]:
            script_path = os.path.join(project_root, script)
            if os.path.exists(script_path):
                try:
                    os.chmod(script_path, 0o755)  # rwxr-xr-x
                except Exception as e:
                    logger.warning(f"Failed to make {script} executable: {e}")
        
        logger.info("Python environment setup completed successfully")
        return {
            "success": True,
            "todo_id": todo_id,
            "env_path": env_path
        }
        
    except Exception as e:
        logger.exception("Error creating Python environment manually")
        return {
            "success": False,
            "todo_id": todo_id,
            "error": str(e)
        }

async def setup_logging(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Set up structured logging with correlation IDs
    
    Args:
        params: Task parameters including:
            - todo_id: ID of the todo item
            - correlation_ids: Whether to include correlation IDs (default: True)
            
    Returns:
        Dict with success status and results
    """
    logger.info("Setting up structured logging")
    
    todo_id = params.get("todo_id")
    correlation_ids = params.get("correlation_ids", True)
    project_root = params.get("project_root", os.getcwd())
    
    try:
        # Create logging directory
        logs_dir = os.path.join(project_root, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        # Create logging utility module
        logging_util_dir = os.path.join(project_root, "backend", "utils")
        os.makedirs(logging_util_dir, exist_ok=True)
        
        # Create logging utility file
        logging_util_path = os.path.join(logging_util_dir, "logging.py")
        
        with open(logging_util_path, "w") as f:
            f.write("""'''
Structured logging utilities for NexusX
'''

import json
import logging
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Correlation ID context
_request_context = {}

def generate_correlation_id() -> str:
    '''Generate a unique correlation ID'''
    return str(uuid.uuid4())

def get_correlation_id() -> Optional[str]:
    '''Get the current correlation ID'''
    return _request_context.get('correlation_id')

def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    '''Set the correlation ID for the current context'''
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    _request_context['correlation_id'] = correlation_id
    return correlation_id

def clear_correlation_id() -> None:
    '''Clear the correlation ID from the current context'''
    _request_context.pop('correlation_id', None)

class StructuredLogFormatter(logging.Formatter):
    '''
    JSON formatter for structured logging
    '''
    def format(self, record: logging.LogRecord) -> str:
        '''Format the log record as JSON'''
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Include correlation ID if available
        correlation_id = get_correlation_id()
        if correlation_id:
            log_data['correlation_id'] = correlation_id
            
        # Include exception info if available
        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            log_data['exception'] = {
                'type': exc_type.__name__,
                'message': str(exc_value)
            }
            
        # Include extra fields
        for key, value in record.__dict__.items():
            if key.startswith('_') or key in ('args', 'asctime', 'created', 'exc_info', 'exc_text', 
                                             'filename', 'funcName', 'id', 'levelname', 'levelno',
                                             'lineno', 'module', 'msecs', 'message', 'msg',
                                             'name', 'pathname', 'process', 'processName',
                                             'relativeCreated', 'stack_info', 'thread', 'threadName'):
                continue
            log_data[key] = value
            
        return json.dumps(log_data)

def setup_logging(
    log_level: int = logging.INFO,
    enable_console: bool = True,
    log_file: Optional[str] = None,
    enable_json: bool = True
) -> None:
    '''
    Configure application logging
    
    Args:
        log_level: Logging level (default: INFO)
        enable_console: Enable console logging (default: True)
        log_file: Path to log file (default: None)
        enable_json: Use JSON format for logs (default: True)
    '''
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    # Create formatter
    if enable_json:
        formatter = StructuredLogFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s (%(correlation_id)s): %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Example usage
    logging.info('Logging system initialized', extra={'service': 'logging_setup'})
    
class LoggingMiddleware:
    '''
    Middleware for FastAPI that adds correlation ID to requests
    '''
    async def __call__(self, request, call_next):
        # Extract correlation ID from headers or generate a new one
        correlation_id = request.headers.get('X-Correlation-ID')
        if not correlation_id:
            correlation_id = generate_correlation_id()
            
        # Set correlation ID for this request
        set_correlation_id(correlation_id)
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Add correlation ID to response headers
            response.headers['X-Correlation-ID'] = correlation_id
            
            return response
        finally:
            # Clear the correlation ID
            clear_correlation_id()
""")
        
        logger.info("Created structured logging utility")
        
        # Create an example usage file
        example_path = os.path.join(project_root, "backend", "logging_example.py")
        with open(example_path, "w") as f:
            f.write("""'''
Example usage of structured logging
'''

import logging
from backend.utils.logging import setup_logging, set_correlation_id

# Configure logging
setup_logging(
    log_level=logging.INFO,
    enable_console=True,
    log_file='logs/nexus.log',
    enable_json=True
)

# Example function using correlation IDs
def process_request(request_id):
    # Set correlation ID for this request context
    set_correlation_id(request_id)
    
    logging.info(f"Processing request", extra={
        'request_id': request_id,
        'service': 'example_service'
    })
    
    try:
        # Simulate some work
        result = 42 / 0  # Will cause exception
    except Exception as e:
        logging.error(f"Error processing request: {e}", exc_info=True)

if __name__ == "__main__":
    # Example usage
    process_request("example-request-123")
""")
        
        return {
            "success": True,
            "todo_id": todo_id,
            "files_created": [logging_util_path, example_path],
            "logs_dir": logs_dir
        }
        
    except Exception as e:
        logger.exception("Error setting up logging")
        return {
            "success": False,
            "todo_id": todo_id,
            "error": str(e)
        }

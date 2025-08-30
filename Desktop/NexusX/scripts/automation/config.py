"""
Configuration module for the NexusX automation system.
"""

import os
import pathlib
from typing import Dict, List, Optional, Any

# Base paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Worker configuration
WORKER_CONFIG = {
    "default": {
        "max_workers": 4,
        "skills": {
            "primary": ["python", "nexus", "docker"],
            "secondary": ["health", "process", "io"]
        }
    },
    "backup": {
        "max_workers": 8,
        "skills": {
            "primary": ["frontend", "docker", "database"],
            "secondary": ["python", "nexus", "io"]
        }
    },
    "swarm": {
        "max_workers": 16,
        "skills": {
            "primary": ["collaborate", "nexus"],
            "secondary": ["python", "docker", "frontend", "health", "database", "io"]
        }
    }
}

# Task type mapping
TASK_TYPES = {
    "python-environment": {
        "command": "nexus:setup_python_env",
        "skills": ["python"]
    },
    "health-checks": {
        "command": "nexus:implement_health_check",
        "skills": ["health"]
    },
    "docker-setup": {
        "command": "nexus:create_docker_service",
        "skills": ["docker"]
    },
    "error-handling": {
        "command": "nexus:setup_logging",
        "skills": ["python", "process"]
    },
    "frontend": {
        "command": "nexus:implement_frontend",
        "skills": ["frontend"]
    },
    "database-setup": {
        "command": "nexus:setup_database",
        "skills": ["database"]
    },
    "api": {
        "command": "nexus:implement_api",
        "skills": ["python", "api"]
    }
}

# Service-specific configurations
SERVICES = [
    "api-gateway",
    "ai-engine",
    "fraud-detection",
    "forensic-analysis",
    "frenly-ai"
]

# Todo file location
TODO_FILE = os.path.join(PROJECT_ROOT, ".todos.json")

# Execution intervals
SCANNER_INTERVAL = 10.0  # seconds
MONITOR_INTERVAL = 1.0  # seconds
AUTOSCALER_INTERVAL = 1.0  # seconds

# Dashboard configuration
DASHBOARD_ENABLED = True
DASHBOARD_PREFIX = os.path.join(LOGS_DIR, "nexus_dashboard")

# System utilization targets
TARGET_UTILIZATION = 0.7
MAX_DEFAULT_PER_CPU = 2

def get_project_structure():
    """Returns a dictionary with the project structure"""
    structure = {
        "frontend": os.path.join(PROJECT_ROOT, "frontend"),
        "backend": os.path.join(PROJECT_ROOT, "backend"),
        "docker": os.path.join(PROJECT_ROOT, "docker"),
        "config": os.path.join(PROJECT_ROOT, "config"),
        "scripts": os.path.join(PROJECT_ROOT, "scripts"),
        "docs": os.path.join(PROJECT_ROOT, "docs"),
        "tests": os.path.join(PROJECT_ROOT, "tests")
    }
    return structure

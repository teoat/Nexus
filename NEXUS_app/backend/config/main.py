# File: NEXUS_app/backend/main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import json
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import List, Optional
import re
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Any, Dict
import multiprocessing
import psutil
from datetime import datetime
import re
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Nexus Platform API",
    description="""
    ## Nexus Platform API
    
    Comprehensive API for the Nexus Platform including:
    - Agent Management
    - AI Services
    - Authentication & Authorization
    - Monitoring & Health Checks
    
    ### Authentication
    Most endpoints require JWT authentication. Include the token in the Authorization header:
    ```
    Authorization: Bearer <your-jwt-token>
    ```
    """,
    version="2.0.0",
    contact={
        "name": "Nexus Platform Team",
        "email": "support@nexusplatform.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://api.nexusplatform.com", "description": "Production server"},
    ],
    tags_metadata=[
        {
            "name": "agents",
            "description": "Agent management and coordination operations",
        },
        {
            "name": "ai",
            "description": "AI services and model management",
        },
        {
            "name": "auth",
            "description": "Authentication and authorization",
        },
        {
            "name": "monitoring",
            "description": "System monitoring and health checks",
        },
        {
            "name": "orchestration",
            "description": "Platform orchestration and management",
        },
    ]
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Nexus Platform API",
        version="2.0.0",
        description="Comprehensive API for the Nexus Platform",
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
        }
    }
    
    # Add global security
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# File: NEXUS_app/backend/routers.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

# Agent Management Router
agent_router = APIRouter(
    prefix="/api/v1/agents",
    tags=["agents"],
    responses={
        404: {"description": "Agent not found"},
        403: {"description": "Insufficient permissions"},
    }
)

class AgentCreate(BaseModel):
    config: dict = Field(..., description="Agent configuration")
    
class AgentResponse(BaseModel):
    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent name")
    type: str = Field(..., description="Agent type")
    status: str = Field(..., description="Agent status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

@agent_router.post(
    "/",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new agent",
    description="""
    Create a new agent in the Nexus Platform.
    
    **Parameters:**
    - **name**: Unique agent name
    - **type**: Agent type (ai, orchestration, monitoring, etc.)
    
    **Returns:**
    - Created agent information with generated ID
    
    
    This endpoint allows authorized users to create new agents
    """
    # Implementation here
    pass

@agent_router.get(
    "/",
    response_model=List[AgentResponse],
    summary="List all agents",
    description="""
    Retrieve a list of all agents in the system.
    
    **Query Parameters:**
    - **status**: Filter by agent status (optional)
    - **type**: Filter by agent type (optional)
    - **limit**: Maximum number of agents to return (default: 100)
    - **offset**: Number of agents to skip (default: 0)
    
    **Returns:**
    - List of agents with their current status and configuration
    """,
    responses={
        200: {
            "description": "List of agents retrieved successfully",
            "content": {
                "application/json": {
                        {
                            "id": "agent_123",
                            "name": "frenly-ai-agent",
                            "type": "ai",
                            "status": "active",
                            "created_at": "2025-01-27T10:00:00Z",
                            "updated_at": "2025-01-27T10:00:00Z"
                        }
                    ]
                }
            }
        }
    }
)
async def list_agents(
    status: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """
    List all agents with optional filtering.
    
    Supports filtering by status and type, with pagination support.
    """
    # Implementation here
    pass

# File: NEXUS_app/backend/middleware/security.py
from fastapi import Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import List, Optional
import re

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        allowed_hosts: List[str] = None,
        max_request_size: int = 16 * 1024 * 1024,  # 16MB
        rate_limit_requests: int = 100,
        rate_limit_window: int = 60,  # seconds
    ):
        super().__init__(app)
        self.allowed_hosts = allowed_hosts or ["localhost", "127.0.0.1"]
        self.max_request_size = max_request_size
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.request_counts = {}
        
        # Security headers
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https:; "
                "font-src 'self' https://cdn.jsdelivr.net;"
            )
        }

    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()
        
        # Security checks
        try:
            # 1. Host validation
            await self._validate_host(request)
            
            # 2. Request size validation
            await self._validate_request_size(request)
            
            # 3. Rate limiting
            await self._check_rate_limit(request)
            
            # 4. SQL injection protection
            await self._check_sql_injection(request)
            
            # 5. XSS protection
            await self._check_xss(request)
            
        except HTTPException as e:
            logger.warning(f"Security violation: {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={"error": "Security violation", "detail": e.detail}
            )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        # Add timing header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

    async def _validate_host(self, request: Request):
        """Validate request host"""
        host = request.headers.get("host", "").split(":")[0]
        if host not in self.allowed_hosts:
            raise HTTPException(
                status_code=403,
                detail=f"Host '{host}' not allowed"
            )

    async def _validate_request_size(self, request: Request):
        """Validate request size"""
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            raise HTTPException(
                status_code=413,
                detail="Request too large"
            )

    async def _check_rate_limit(self, request: Request):
        """Check rate limiting"""
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        self.request_counts = {
            ip: times for ip, times in self.request_counts.items()
            if any(t > current_time - self.rate_limit_window for t in times)
        }
        
        # Check current client
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        client_requests = self.request_counts[client_ip]
        client_requests = [t for t in client_requests if t > current_time - self.rate_limit_window]
        
        if len(client_requests) >= self.rate_limit_requests:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        
        client_requests.append(current_time)
        self.request_counts[client_ip] = client_requests

    async def _check_sql_injection(self, request: Request):
        """Check for SQL injection attempts"""
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]\s*=\s*['\"])",
            r"(\b(OR|AND)\s+1\s*=\s*1)",
            r"(\b(OR|AND)\s+['\"]\s*=\s*['\"])",
        ]
        
        # Check URL parameters
        for param_name, param_value in request.query_params.items():
            if self._contains_sql_pattern(param_value, sql_patterns):
                raise HTTPException(
                    status_code=400,
                    detail="Potential SQL injection detected"
                )
        
        # Check form data
        if request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded"):
            form_data = await request.form()
            for field_name, field_value in form_data.items():
                if self._contains_sql_pattern(str(field_value), sql_patterns):
                    raise HTTPException(
                        status_code=400,
                        detail="Potential SQL injection detected"
                    )

    async def _check_xss(self, request: Request):
        """Check for XSS attempts"""
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
        ]
        
        # Check URL parameters
        for param_name, param_value in request.query_params.items():
            if self._contains_xss_pattern(param_value, xss_patterns):
                raise HTTPException(
                    status_code=400,
                    detail="Potential XSS detected"
                )

    def _contains_sql_pattern(self, text: str, patterns: List[str]) -> bool:
        """Check if text contains SQL injection patterns"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _contains_xss_pattern(self, text: str, patterns: List[str]) -> bool:
        """Check if text contains XSS patterns"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

# File: NEXUS_app/backend/middleware/validation.py
from fastapi import Request, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
import json
import re
from typing import Any, Dict

class InputValidationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.max_string_length = 10000
        self.max_array_length = 1000
        self.max_object_depth = 10

    async def dispatch(self, request: Request, call_next):
        # Validate request body
        if request.method in ["POST", "PUT", "PATCH"]:
            await self._validate_request_body(request)
        
        # Validate query parameters
        await self._validate_query_params(request)
        
        response = await call_next(request)
        return response

    async def _validate_request_body(self, request: Request):
        """Validate request body for size and content"""
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            body = await request.body()
            
            if len(body) > self.max_string_length:
                raise HTTPException(
                    status_code=413,
                    detail="Request body too large"
                )
            
            try:
                data = json.loads(body)
                self._validate_json_data(data, depth=0)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid JSON format"
                )

    def _validate_json_data(self, data: Any, depth: int):
        """Recursively validate JSON data"""
        if depth > self.max_object_depth:
            raise HTTPException(
                status_code=400,
                detail="Object nesting too deep"
            )
        
        if isinstance(data, dict):
            for key, value in data.items():
                self._validate_string(key)
                self._validate_json_data(value, depth + 1)
        elif isinstance(data, list):
            if len(data) > self.max_array_length:
                raise HTTPException(
                    status_code=400,
                    detail="Array too large"
                )
            for item in data:
                self._validate_json_data(item, depth + 1)
        elif isinstance(data, str):
            self._validate_string(data)

    def _validate_string(self, text: str):
        """Validate string content"""
        if len(text) > self.max_string_length:
            raise HTTPException(
                status_code=400,
                detail="String too long"
            )
        
        # Check for null bytes
        if "\x00" in text:
            raise HTTPException(
                status_code=400,
                detail="Invalid character in string"
            )

    async def _validate_query_params(self, request: Request):
        """Validate query parameters"""
        for param_name, param_value in request.query_params.items():
            self._validate_string(param_name)
            self._validate_string(param_value)

# File: NEXUS_app/backend/config/cors.py
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List

def get_cors_config() -> dict:
    """Get CORS configuration based on environment"""
    
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        # Production CORS - restrictive
        return {
            "allow_origins": [
                "https://nexusplatform.com",
                "https://www.nexusplatform.com",
                "https://app.nexusplatform.com",
            ],
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Authorization",
                "Content-Type",
                "X-Requested-With",
                "X-API-Key",
            ],
            "expose_headers": ["X-Process-Time", "X-Rate-Limit-Remaining"],
            "max_age": 3600,
        }
    else:
        # Development CORS - permissive
        return {
            "allow_origins": [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
            ],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
            "expose_headers": ["*"],
            "max_age": 3600,
        }

def setup_cors_middleware(app):
    cors_config = get_cors_config()
    
    app.add_middleware(
        CORSMiddleware,
        **cors_config
    )

# File: NEXUS_app/backend/gunicorn.conf.py
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', 8000)}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'nexus-platform-api'

# Server mechanics
daemon = False
pidfile = '/tmp/nexus-platform-api.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

# Preload app for better performance
preload_app = True

# Worker timeout
graceful_timeout = 30

# Worker class configuration
worker_tmp_dir = '/dev/shm'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Nexus Platform API server is ready. Workers: %s", workers)

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")

# File: NEXUS_app/scripts/start_production.sh
#!/bin/bash
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

# File: NEXUS_app/backend/routers/health.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import psutil
import os
from datetime import datetime

health_router = APIRouter(prefix="/health", tags=["monitoring"])

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    environment: str
    worker_id: str
    memory_usage: dict
    cpu_usage: float

@health_router.get("/", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint"""
    
    # Get process information
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="2.0.0",
        environment=os.getenv("ENVIRONMENT", "development"),
        worker_id=f"worker-{os.getpid()}",
        memory_usage={
            "rss": memory_info.rss,
            "vms": memory_info.vms,
            "percent": process.memory_percent()
        },
        cpu_usage=process.cpu_percent()
    )

@health_router.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    # Add any readiness checks here
    return {"status": "ready"}

@health_router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    # Add any liveness checks here
    return {"status": "alive"}

# File: NEXUS_app/scripts/generate_api_docs.py
#!/usr/bin/env python3
"""
API Documentation Generator
"""

import json
import requests
from pathlib import Path

def generate_api_docs():
    """Generate API documentation from running service"""
    
    try:
        response = requests.get("http://localhost:8000/openapi.json")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API service. Make sure it's running on localhost:8000")
        return
    
    docs_dir = Path("docs/api")
    docs_dir.mkdir(exist_ok=True)
    
    with open(docs_dir / "openapi.json", "w") as f:
    
    # Generate markdown documentation
    
    print("✅ API documentation generated successfully!")
    print(f"📁 Documentation saved to: {docs_dir}")
    print("🌐 Swagger UI available at: http://localhost:8000/docs")

    


## API Information

## Base URLs
"""
    
        md_content += f"- **{server['description']}**: {server['url']}\n"
    
    md_content += "\n## Authentication\n\n"
    
    # Add authentication information
            md_content += f"### {scheme_name}\n"
            md_content += f"- **Type**: {scheme['type']}\n"
            if scheme['type'] == 'http':
                md_content += f"- **Scheme**: {scheme['scheme']}\n"
            md_content += "\n"
    
    # Add endpoints
    md_content += "\n## Endpoints\n\n"
    
        md_content += f"### {path}\n\n"
        
        for method, details in methods.items():
            md_content += f"#### {method.upper()} {path}\n\n"
            md_content += f"{details.get('summary', 'No summary available')}\n\n"
            
            if 'description' in details:
                md_content += f"{details['description']}\n\n"
            
            # Add parameters
            if 'parameters' in details:
                md_content += "**Parameters:**\n\n"
                for param in details['parameters']:
                    md_content += f"- **{param['name']}** ({param.get('in', 'unknown')}): {param.get('description', 'No description')}\n"
                md_content += "\n"
            
            # Add request body
            if 'requestBody' in details:
                md_content += "**Request Body:**\n\n"
                md_content += f"{details['requestBody'].get('description', 'No description')}\n\n"
            
            # Add responses
            if 'responses' in details:
                md_content += "**Responses:**\n\n"
                for status_code, response in details['responses'].items():
                    md_content += f"- **{status_code}**: {response.get('description', 'No description')}\n"
                md_content += "\n"
            
            md_content += "---\n\n"
    
    # Save markdown file
    with open(docs_dir / "api_documentation.md", "w") as f:
        f.write(md_content)

if __name__ == "__main__":
    generate_api_docs()
```

#### **Verification Steps**
1. Start the API service: `cd NEXUS_app/backend && python main.py`
2. Visit Swagger UI: `http://localhost:8000/docs`
4. Run documentation generator: `python scripts/generate_api_docs.py`
5. Verify generated documentation files

---

## 🔒 **PRIORITY 2: SECURITY MIDDLEWARE IMPLEMENTATION**

### **2.1. Production Security Middleware**

#### **Objective**
Implement comprehensive security middleware for production deployment.

#### **Implementation Steps**

**Step 1: Enhanced Security Middleware**
```python
# File: NEXUS_app/backend/middleware/security.py
from fastapi import Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import List, Optional
import re

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        allowed_hosts: List[str] = None,
        max_request_size: int = 16 * 1024 * 1024,  # 16MB
        rate_limit_requests: int = 100,
        rate_limit_window: int = 60,  # seconds
    ):
        super().__init__(app)
        self.allowed_hosts = allowed_hosts or ["localhost", "127.0.0.1"]
        self.max_request_size = max_request_size
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.request_counts = {}
        
        # Security headers
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https:; "
                "font-src 'self' https://cdn.jsdelivr.net;"
            )
        }

    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()
        
        # Security checks
        try:
            # 1. Host validation
            await self._validate_host(request)
            
            # 2. Request size validation
            await self._validate_request_size(request)
            
            # 3. Rate limiting
            await self._check_rate_limit(request)
            
            # 4. SQL injection protection
            await self._check_sql_injection(request)
            
            # 5. XSS protection
            await self._check_xss(request)
            
        except HTTPException as e:
            logger.warning(f"Security violation: {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={"error": "Security violation", "detail": e.detail}
            )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        # Add timing header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

    async def _validate_host(self, request: Request):
        """Validate request host"""
        host = request.headers.get("host", "").split(":")[0]
        if host not in self.allowed_hosts:
            raise HTTPException(
                status_code=403,
                detail=f"Host '{host}' not allowed"
            )

    async def _validate_request_size(self, request: Request):
        """Validate request size"""
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            raise HTTPException(
                status_code=413,
                detail="Request too large"
            )

    async def _check_rate_limit(self, request: Request):
        """Check rate limiting"""
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        self.request_counts = {
            ip: times for ip, times in self.request_counts.items()
            if any(t > current_time - self.rate_limit_window for t in times)
        }
        
        # Check current client
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        client_requests = self.request_counts[client_ip]
        client_requests = [t for t in client_requests if t > current_time - self.rate_limit_window]
        
        if len(client_requests) >= self.rate_limit_requests:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        
        client_requests.append(current_time)
        self.request_counts[client_ip] = client_requests

    async def _check_sql_injection(self, request: Request):
        """Check for SQL injection attempts"""
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]\s*=\s*['\"])",
            r"(\b(OR|AND)\s+1\s*=\s*1)",
            r"(\b(OR|AND)\s+['\"]\s*=\s*['\"])",
        ]
        
        # Check URL parameters
        for param_name, param_value in request.query_params.items():
            if self._contains_sql_pattern(param_value, sql_patterns):
                raise HTTPException(
                    status_code=400,
                    detail="Potential SQL injection detected"
                )
        
        # Check form data
        if request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded"):
            form_data = await request.form()
            for field_name, field_value in form_data.items():
                if self._contains_sql_pattern(str(field_value), sql_patterns):
                    raise HTTPException(
                        status_code=400,
                        detail="Potential SQL injection detected"
                    )

    async def _check_xss(self, request: Request):
        """Check for XSS attempts"""
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
        ]
        
        # Check URL parameters
        for param_name, param_value in request.query_params.items():
            if self._contains_xss_pattern(param_value, xss_patterns):
                raise HTTPException(
                    status_code=400,
                    detail="Potential XSS detected"
                )

    def _contains_sql_pattern(self, text: str, patterns: List[str]) -> bool:
        """Check if text contains SQL injection patterns"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _contains_xss_pattern(self, text: str, patterns: List[str]) -> bool:
        """Check if text contains XSS patterns"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
```

**Step 2: Enhanced CORS Configuration**
```python
# File: NEXUS_app/backend/config/cors.py
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List

def get_cors_config() -> dict:
    """Get CORS configuration based on environment"""
    
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        # Production CORS - restrictive
        return {
            "allow_origins": [
                "https://nexusplatform.com",
                "https://www.nexusplatform.com",
                "https://app.nexusplatform.com",
            ],
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Authorization",
                "Content-Type",
                "X-Requested-With",
                "X-API-Key",
            ],
            "expose_headers": ["X-Process-Time", "X-Rate-Limit-Remaining"],
            "max_age": 3600,
        }
    else:
        # Development CORS - permissive
        return {
            "allow_origins": [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
            ],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
            "expose_headers": ["*"],
            "max_age": 3600,
        }

def setup_cors_middleware(app):
    cors_config = get_cors_config()
    
    app.add_middleware(
        CORSMiddleware,
        **cors_config
    )
```

**Step 3: Input Validation Middleware**
```python
# File: NEXUS_app/backend/middleware/validation.py
from fastapi import Request, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
import json
import re
from typing import Any, Dict

class InputValidationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.max_string_length = 10000
        self.max_array_length = 1000
        self.max_object_depth = 10

    async def dispatch(self, request: Request, call_next):
        # Validate request body
        if request.method in ["POST", "PUT", "PATCH"]:
            await self._validate_request_body(request)
        
        # Validate query parameters
        await self._validate_query_params(request)
        
        response = await call_next(request)
        return response

    async def _validate_request_body(self, request: Request):
        """Validate request body for size and content"""
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            body = await request.body()
            
            if len(body) > self.max_string_length:
                raise HTTPException(
                    status_code=413,
                    detail="Request body too large"
                )
            
            try:
                data = json.loads(body)
                self._validate_json_data(data, depth=0)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid JSON format"
                )

    def _validate_json_data(self, data: Any, depth: int):
        """Recursively validate JSON data"""
        if depth > self.max_object_depth:
            raise HTTPException(
                status_code=400,
                detail="Object nesting too deep"
            )
        
        if isinstance(data, dict):
            for key, value in data.items():
                self._validate_string(key)
                self._validate_json_data(value, depth + 1)
        elif isinstance(data, list):
            if len(data) > self.max_array_length:
                raise HTTPException(
                    status_code=400,
                    detail="Array too large"
                )
            for item in data:
                self._validate_json_data(item, depth + 1)
        elif isinstance(data, str):
            self._validate_string(data)

    def _validate_string(self, text: str):
        """Validate string content"""
        if len(text) > self.max_string_length:
            raise HTTPException(
                status_code=400,
                detail="String too long"
            )
        
        # Check for null bytes
        if "\x00" in text:
            raise HTTPException(
                status_code=400,
                detail="Invalid character in string"
            )

    async def _validate_query_params(self, request: Request):
        """Validate query parameters"""
        for param_name, param_value in request.query_params.items():
            self._validate_string(param_name)
            self._validate_string(param_value)
```

**Step 4: Apply Security Middleware**
```python
# File: NEXUS_app/backend/main.py
from middleware.security import SecurityMiddleware
from middleware.validation import InputValidationMiddleware
from config.cors import setup_cors_middleware

# Setup CORS
setup_cors_middleware(app)

# Add security middleware
app.add_middleware(SecurityMiddleware, allowed_hosts=["localhost", "127.0.0.1"])

# Add input validation middleware
app.add_middleware(InputValidationMiddleware)
```

#### **Verification Steps**
5. Verify CORS configuration with browser developer tools

---

## ⚡ **PRIORITY 3: MULTI-WORKER CONFIGURATION**

### **3.1. Production-Ready Multi-Worker Setup**

#### **Objective**
Configure Gunicorn with multiple workers for better performance and scalability.

#### **Implementation Steps**

**Step 1: Gunicorn Configuration**
```python
# File: NEXUS_app/backend/gunicorn.conf.py
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', 8000)}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'nexus-platform-api'

# Server mechanics
daemon = False
pidfile = '/tmp/nexus-platform-api.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

# Preload app for better performance
preload_app = True

# Worker timeout
graceful_timeout = 30

# Worker class configuration
worker_tmp_dir = '/dev/shm'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Nexus Platform API server is ready. Workers: %s", workers)

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")
```

**Step 2: Production Startup Script**
```bash
#!/bin/bash
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
```

**Step 3: Health Check Endpoint for Workers**
```python
# File: NEXUS_app/backend/routers/health.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import psutil
import os
from datetime import datetime

health_router = APIRouter(prefix="/health", tags=["monitoring"])

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    environment: str
    worker_id: str
    memory_usage: dict
    cpu_usage: float

@health_router.get("/", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint"""
    
    # Get process information
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="2.0.0",
        environment=os.getenv("ENVIRONMENT", "development"),
        worker_id=f"worker-{os.getpid()}",
        memory_usage={
            "rss": memory_info.rss,
            "vms": memory_info.vms,
            "percent": process.memory_percent()
        },
        cpu_usage=process.cpu_percent()
    )

@health_router.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    # Add any readiness checks here
    return {"status": "ready"}

@health_router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    # Add any liveness checks here
    return {"status": "alive"}
```

**Step 4: Docker Configuration for Multi-Worker**
```dockerfile
# File: NEXUS_app/backend/Dockerfile.prod
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Start command
CMD ["gunicorn", "--config", "gunicorn.conf.py", "main:app"]
```

#### **Verification Steps**
1. Start production server: `./scripts/start_production.sh`
2. Check worker processes: `ps aux | grep gunicorn`
5. Monitor worker memory usage and restart behavior

---

## 📊 **IMPLEMENTATION TIMELINE**

### **Week 1: API Documentation**
- Day 3-4: Create detailed router documentation
- Day 5: Set up Swagger UI and documentation generator

### **Week 2: Security Middleware**
- Day 1-2: Implement security middleware
- Day 3-4: Add input validation and CORS configuration

### **Week 3: Multi-Worker Setup**
- Day 1-2: Configure Gunicorn for production
- Day 3-4: Set up health checks and monitoring

---

## ✅ **SUCCESS CRITERIA**

### **API Documentation**
- [ ] Interactive Swagger UI available at `/docs`

### **Security Middleware**
- [ ] All security headers present in responses
- [ ] Rate limiting working correctly
- [ ] SQL injection and XSS protection active
- [ ] CORS properly configured for production

### **Multi-Worker Setup**
- [ ] Multiple worker processes running
- [ ] Health checks responding correctly
- [ ] Worker restart on memory limits
- [ ] Performance improvement measurable

---

**Next Steps**: Choose which implementation plan to start with, and I'll provide detailed guidance for execution.
```

Perfect! I've created comprehensive implementation plans for the three highest priority items:

## 🎯 **SUMMARY OF IMPLEMENTATION PLANS**

### **1. 📚 API Documentation & Enhancement**

### **2. 🔒 Security Middleware Implementation**
- **Production-ready security headers** and CORS configuration
- **Rate limiting and request validation** middleware
- **SQL injection and XSS protection** with pattern detection

### **3. ⚡ Multi-Worker Configuration**
- **Gunicorn production setup** with optimized worker configuration
- **Health check endpoints** for Kubernetes readiness/liveness probes
- **Worker process management** with automatic restart on memory limits
- **Docker configuration** for production deployment

##  **RECOMMENDED NEXT STEPS**

1. **Start with API Documentation** - This will immediately improve developer experience
2. **Implement Security Middleware** - Critical for production readiness
3. **Configure Multi-Worker Setup** - Essential for performance and scalability

**Which implementation plan would you like to start with?** I can provide step-by-step guidance for any of these, or help you prioritize based on your immediate needs.

Each plan includes:

#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
📚 Comprehensive API Documentation Generator
Generates complete API documentation for all Nexus Platform endpoints
"""

import json
import requests
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import yaml
from jinja2 import Template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveAPIDocsGenerator:
    """Generates comprehensive API documentation for all endpoints"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.docs_dir = self.workspace_path / "docs" / "api"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        # API service endpoints
        self.api_endpoints = [
            "http://localhost:8000",
            "http://localhost:3000",
            "http://localhost:5000"
        ]
        
        # Documentation templates
        self.templates = {
            "main": self._get_main_template(),
            "endpoint": self._get_endpoint_template(),
            "authentication": self._get_auth_template(),
            "errors": self._get_errors_template()
        }
        
        logger.info("✅ API Documentation Generator initialized")
    
    def _get_main_template(self) -> str:
        """Main documentation template"""
        return """# {{ title }}

{{ description }}

## 📋 Table of Contents

- [API Information](#api-information)
- [Authentication](#authentication)
- [Base URLs](#base-urls)
- [Endpoints](#endpoints)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

## 🔧 API Information

- **Version**: {{ version }}
- **Contact**: {{ contact.email }}
- **License**: {{ license.name }}
- **Last Updated**: {{ last_updated }}

## 🔐 Authentication

{{ auth_docs }}

## 🌐 Base URLs

{% for server in servers %}
- **{{ server.description }}**: `{{ server.url }}`
{% endfor %}

## 📡 Endpoints

{% for tag, endpoints in endpoints_by_tag.items() %}
### {{ tag.title() }}

{% for endpoint in endpoints %}
#### {{ endpoint.method.upper() }} {{ endpoint.path }}

{{ endpoint.summary }}

**Description**: {{ endpoint.description }}

{% if endpoint.parameters %}
**Parameters**:
{% for param in endpoint.parameters %}
- `{{ param.name }}` ({{ param.type }}) - {{ param.description }}
  - Required: {{ param.required }}
  - Location: {{ param.location }}
{% endfor %}
{% endif %}

{% if endpoint.request_body %}
**Request Body**:
```json
{{ endpoint.request_body }}
```

{% endif %}
**Response**:
```json
```

**Status Codes**:
{% for status, details in endpoint.status_codes.items() %}
- `{{ status }}`: {{ details.description }}
{% endfor %}


{% endif %}
---

{% endfor %}
{% endfor %}

## ❌ Error Handling

{{ error_docs }}

## ⚡ Rate Limiting

- **Default Rate Limit**: 1000 requests per hour per API key
- **Burst Limit**: 100 requests per minute
- **Headers**: Rate limit information is included in response headers


### Python SDK

```python
import requests

# Initialize client
client = NexusAPIClient(
    base_url="https://api.nexusplatform.com",
    api_key="your-api-key"
)



### JavaScript SDK

```javascript
const NexusAPI = require('nexus-platform-sdk');

// Initialize client
const client = new NexusAPI({
    baseUrl: 'https://api.nexusplatform.com',
    apiKey: 'your-api-key'
});


client.createReconciliationJob({
    name: 'Monthly Reconciliation',
    sourceAccount: 'bank_001',
    targetAccount: 'internal_001'
});
```


```bash
# Get system status
curl -X GET "https://api.nexusplatform.com/api/v1/system/status" \
  -H "Authorization: Bearer your-jwt-token"

# Create reconciliation job
curl -X POST "https://api.nexusplatform.com/api/v1/reconciliation/jobs" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Monthly Reconciliation",
    "source_account": "bank_001",
    "target_account": "internal_001"
  }'
```

## 📝 Changelog

### Version 2.0.0 ({{ last_updated }})
- Added comprehensive reconciliation API
- Enhanced fraud detection endpoints
- Improved error handling and validation
- Added rate limiting and security headers

### Version 1.5.0 (2024-01-01)
- Initial API release
- Basic agent management
- Authentication system
- Monitoring endpoints

---

**Generated on**: {{ generated_at }}
**Generator Version**: 2.0.0
"""
    
    def _get_endpoint_template(self) -> str:
        """Individual endpoint documentation template"""
        return """## {{ method.upper() }} {{ path }}

{{ summary }}

### Description
{{ description }}

### Parameters
{% for param in parameters %}
- **{{ param.name }}** (`{{ param.type }}`) - {{ param.description }}
  - Required: {{ param.required }}
  - Location: {{ param.location }}

### Request Body
```json
{{ request_body }}
```

### Response
```json
```

### Status Codes
{% for status, details in status_codes.items() %}
- **{{ status }}**: {{ details.description }}
{% endfor %}

    
    def _get_auth_template(self) -> str:
        """Authentication documentation template"""
        return """### JWT Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### API Key Authentication

Some endpoints support API key authentication:

```
X-API-Key: <your-api-key>
```

### Getting Authentication Tokens

#### 1. Login with credentials
```bash
curl -X POST "https://api.nexusplatform.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your-username",
    "password": "your-password"
  }'
```

#### 2. Use the returned JWT token
```bash
curl -X GET "https://api.nexusplatform.com/api/v1/system/status" \
  -H "Authorization: Bearer <jwt-token>"
```

### Token Refresh

JWT tokens expire after 24 hours. Use the refresh endpoint to get a new token:

```bash
curl -X POST "https://api.nexusplatform.com/api/v1/auth/refresh" \
  -H "Authorization: Bearer <current-jwt-token>"
```
"""
    
    def _get_errors_template(self) -> str:
        """Error handling documentation template"""
        return """### Error Response Format

All errors follow a consistent format:

```json
{
  "error": "Error message",
  "status_code": 400,
  "timestamp": 1640995200.0,
  "details": {
  }
}
```

### Common Error Codes

- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

### Validation Errors

When request validation fails, the response includes detailed field errors:

```json
{
  "error": "Validation failed",
  "status_code": 422,
  "timestamp": 1640995200.0,
  "details": {
    "field_errors": {
      "email": ["Invalid email format"],
      "password": ["Password must be at least 8 characters"]
    }
  }
}
```
"""
    
    async def generate_comprehensive_docs(self) -> Dict[str, Any]:
        """Generate comprehensive API documentation"""
        logger.info("🚀 Generating comprehensive API documentation...")
        
        try:
            
            # Generate unified documentation
            
            # Generate individual service docs
            
            
            # Generate changelog
            changelog = await self._generate_changelog()
            
            # Save all documentation
            
            logger.info("✅ Comprehensive API documentation generated successfully")
            return {
                "success": True,
                "message": "API documentation generated",
                "files_created": len(list(self.docs_dir.glob("*.md"))),
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate API documentation: {e}")
            return {"success": False, "error": str(e)}
    
        
        for endpoint in self.api_endpoints:
            try:
                response = requests.get(f"{endpoint}/openapi.json", timeout=10)
                if response.status_code == 200:
                else:
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ Could not connect to {endpoint}: {e}")
        
    
        unified_docs = {
            "title": "Nexus Platform API Documentation",
            "description": "Comprehensive API documentation for the Nexus Platform ecosystem",
            "version": "2.0.0",
            "contact": {"email": "support@nexusplatform.com"},
            "license": {"name": "MIT License"},
            "last_updated": datetime.now().isoformat(),
            "servers": [
                {"url": "https://api.nexusplatform.com", "description": "Production server"},
                {"url": "http://localhost:8000", "description": "Development server"}
            ],
            "endpoints_by_tag": {},
            "auth_docs": self.templates["authentication"],
            "error_docs": self.templates["errors"]
        }
        
        
        return unified_docs
    
        
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    endpoint = await self._create_endpoint_doc(path, method, details, service_url)
                    
                    # Group by tags
                    tags = details.get("tags", ["general"])
                    for tag in tags:
                        if tag not in unified_docs["endpoints_by_tag"]:
                            unified_docs["endpoints_by_tag"][tag] = []
                        unified_docs["endpoints_by_tag"][tag].append(endpoint)
    
    async def _create_endpoint_doc(self, path: str, method: str, details: Dict[str, Any], service_url: str) -> Dict[str, Any]:
        """Create documentation for individual endpoint"""
        return {
            "path": path,
            "method": method.upper(),
            "summary": details.get("summary", ""),
            "description": details.get("description", ""),
            "parameters": self._extract_parameters(details.get("parameters", [])),
            "request_body": self._extract_request_body(details.get("requestBody", {})),
            "status_codes": self._extract_status_codes(details.get("responses", {})),
        }
    
    def _extract_parameters(self, parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract parameter information"""
        extracted = []
        for param in parameters:
            extracted.append({
                "name": param.get("name", ""),
                "type": param.get("schema", {}).get("type", "string"),
                "description": param.get("description", ""),
                "required": param.get("required", False),
                "location": param.get("in", "query"),
            })
        return extracted
    
    def _extract_request_body(self, request_body: Dict[str, Any]) -> str:
        """Extract request body schema"""
        if not request_body:
            return ""
        
        content = request_body.get("content", {})
        if "application/json" in content:
            schema = content["application/json"].get("schema", {})
            return json.dumps(schema, indent=2)
        
        return ""
    
        if "200" in responses:
            content = responses["200"].get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                return json.dumps(schema, indent=2)
        
        return "{}"
    
    def _extract_status_codes(self, responses: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """Extract status codes and descriptions"""
        status_codes = {}
        for code, details in responses.items():
            status_codes[code] = {
                "description": details.get("description", "")
            }
        return status_codes
    
        url = f"{service_url}{path}"
        headers = ["-H \"Content-Type: application/json\""]
        
        # Add authentication header if required
        if details.get("security"):
            headers.append("-H \"Authorization: Bearer <your-jwt-token>\"")
        
        headers_str = " \\\n  ".join(headers)
        
        if method.upper() in ["POST", "PUT", "PATCH"]:
            return f"curl -X {method.upper()} \"{url}\" \\\n  {headers_str} \\\n  {body}"
        else:
            return f"curl -X {method.upper()} \"{url}\" \\\n  {headers_str}"
    
        """Generate individual service documentation"""
        service_docs = {}
        
            service_name = service_url.split("//")[1].split(":")[0]
            
            template = Template(self.templates["main"])
            doc_content = template.render(
                last_updated=datetime.now().isoformat(),
                endpoints_by_tag={},  # Will be populated
                auth_docs=self.templates["authentication"],
                error_docs=self.templates["errors"],
                generated_at=datetime.now().isoformat()
            )
            
            service_docs[service_name] = doc_content
        
        return service_docs
    
            "python": self._generate_python_sdk(),
            "javascript": self._generate_javascript_sdk(),
        }
        
    
    def _generate_python_sdk(self) -> str:
import requests
from typing import Dict, Any, Optional

class NexusAPIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        response = self.session.get(f"{self.base_url}/api/v1/system/status")
        response.raise_for_status()
        return response.json()
    
    def create_reconciliation_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create reconciliation job"""
        response = self.session.post(
            f"{self.base_url}/api/v1/reconciliation/jobs",
            json=job_data
        )
        response.raise_for_status()
        return response.json()
    
    def get_fraud_alerts(self, limit: int = 100) -> Dict[str, Any]:
        """Get fraud alerts"""
        response = self.session.get(
            f"{self.base_url}/api/v1/fraud/alerts",
            params={'limit': limit}
        )
        response.raise_for_status()
        return response.json()


# Get system status
status = client.get_system_status()
print(f"System Status: {status['overall']}")
'''
    
    def _generate_javascript_sdk(self) -> str:
class NexusAPIClient {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.apiKey = apiKey;
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }
    
    async request(method, endpoint, data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        const options = {
            method,
            headers: this.headers
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async getSystemStatus() {
        return await this.request('GET', '/api/v1/system/status');
    }
    
    async createReconciliationJob(jobData) {
        return await this.request('POST', '/api/v1/reconciliation/jobs', jobData);
    }
    
    async getFraudAlerts(limit = 100) {
        return await this.request('GET', `/api/v1/fraud/alerts?limit=${limit}`);
    }
}

const client = new NexusAPIClient(
    'https://api.nexusplatform.com',
    'your-api-key'
);

// Get system status
client.getSystemStatus()
    .then(status => console.log('System Status:', status.overall))
    .catch(error => console.error('Error:', error));
'''
    

## Authentication
# Login
curl -X POST "https://api.nexusplatform.com/api/v1/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "your-username",
    "password": "your-password"
  }'

## System Status
curl -X GET "https://api.nexusplatform.com/api/v1/system/status" \\
  -H "Authorization: Bearer <your-jwt-token>"

## Reconciliation Jobs
# Create job
curl -X POST "https://api.nexusplatform.com/api/v1/reconciliation/jobs" \\
  -H "Authorization: Bearer <your-jwt-token>" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Monthly Reconciliation",
    "source_account": "bank_001",
    "target_account": "internal_001"
  }'

# Get jobs
curl -X GET "https://api.nexusplatform.com/api/v1/reconciliation/jobs" \\
  -H "Authorization: Bearer <your-jwt-token>"

## Fraud Detection
# Get alerts
curl -X GET "https://api.nexusplatform.com/api/v1/fraud/alerts" \\
  -H "Authorization: Bearer <your-jwt-token>"

# Create alert
curl -X POST "https://api.nexusplatform.com/api/v1/fraud/alerts" \\
  -H "Authorization: Bearer <your-jwt-token>" \\
  -H "Content-Type: application/json" \\
  -d '{
    "transaction_id": "txn_123",
    "risk_score": 85,
    "description": "High-risk transaction detected"
  }'
'''
    
    async def _generate_changelog(self) -> str:
        """Generate API changelog"""
        return '''# API Changelog

## Version 2.0.0 (2024-09-04)

### Added
- Comprehensive reconciliation API with job management
- Enhanced fraud detection endpoints with real-time monitoring
- GDPR compliance endpoints for data management
- Database optimization endpoints for performance monitoring
- Interactive API documentation with Swagger UI

### Changed
- Improved error handling with detailed validation messages
- Enhanced authentication with JWT token refresh
- Updated response formats for better consistency
- Optimized database queries for large-scale operations

### Fixed
- Fixed rate limiting issues with burst requests
- Resolved authentication token expiration handling
- Fixed pagination for large result sets
- Corrected error response format consistency

## Version 1.5.0 (2024-01-01)

### Added
- Initial API release with core functionality
- Basic agent management endpoints
- Authentication and authorization system
- System monitoring and health check endpoints

### Security
- Implemented JWT-based authentication
- Added rate limiting and request validation
- Enhanced security headers and CORS configuration
'''
    
    async def _save_documentation(self, unified_docs: Dict[str, Any], service_docs: Dict[str, str], 
        """Save all generated documentation"""
        
        # Save main unified documentation
        main_template = Template(self.templates["main"])
        main_content = main_template.render(
            **unified_docs,
            generated_at=datetime.now().isoformat()
        )
        
        with open(self.docs_dir / "README.md", "w") as f:
            f.write(main_content)
        
        # Save individual service documentation
        for service_name, content in service_docs.items():
            with open(self.docs_dir / f"{service_name}_api.md", "w") as f:
                f.write(content)
        
        
            with open(sdk_dir / f"{language}_sdk.py" if language == "python" else f"{language}_sdk.js", "w") as f:
        
        # Save changelog
        with open(self.docs_dir / "CHANGELOG.md", "w") as f:
            f.write(changelog)
        
        
            service_name = service_url.split("//")[1].split(":")[0]
        
        logger.info(f"✅ Documentation saved to {self.docs_dir}")

    
    result = await generator.generate_comprehensive_docs()
    print(f"Documentation generation result: {result}")

if __name__ == "__main__":
    asyncio.run(main())

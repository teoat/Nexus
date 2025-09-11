#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
📚 Static API Documentation Generator
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class StaticAPIDocGenerator:
    def __init__(self):
        self.docs_dir = Path("docs/api")
        self.docs_dir.mkdir(exist_ok=True)
        
    def generate_comprehensive_docs(self):
        print("🚀 Generating comprehensive API documentation...")
        
        
        # Generate all documentation formats
        
        print("✅ Comprehensive API documentation generated successfully!")
        return True
    
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Nexus Platform API",
                "description": """
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
                "version": "2.0.0",
                "contact": {
                    "name": "Nexus Platform Team",
                    "email": "support@nexusplatform.com",
                },
                "license": {
                    "name": "MIT License",
                    "url": "https://opensource.org/licenses/MIT",
                },
            },
            "servers": [
                {"url": "http://localhost:8000", "description": "Development server"},
                {"url": "https://api.nexusplatform.com", "description": "Production server"},
            ],
            "tags": [
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
            ],
            "paths": {
                "/health": {
                    "get": {
                        "tags": ["monitoring"],
                        "summary": "Health Check",
                        "description": "Check the health status of the API",
                        "responses": {
                            "200": {
                                "description": "Service is healthy",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
    
        # JSON format
        with open(self.docs_dir / "openapi.json", "w") as f:
        
        # YAML format
        with open(self.docs_dir / "openapi.yaml", "w") as f:
        
    
        """Generate comprehensive markdown documentation"""
        
        with open(self.docs_dir / "README.md", "w") as f:
            f.write(md_content)
        
        print("📝 Markdown documentation generated")
    
        """Create markdown header section"""
        return f"""# {info.get('title', 'API Documentation')}

{info.get('description', '')}

## 📋 API Information

| Field | Value |
|-------|-------|
| **Version** | {info.get('version', 'N/A')} |
| **Contact** | {info.get('contact', {}).get('email', 'N/A')} |
| **License** | {info.get('license', {}).get('name', 'N/A')} |
| **Generated** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |

## 🌐 Base URLs

"""
    
        """Create authentication section"""
        
        auth_section = "## 🔐 Authentication\n\n"
        
        for scheme_name, scheme in security_schemes.items():
            auth_section += f"### {scheme_name}\n\n"
            
            if scheme.get("type") == "http" and scheme.get("scheme") == "bearer":
                auth_section += """**Bearer Token Authentication**

Include the JWT token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

**Getting a Token:**

1. Make a POST request to `/auth/login` with your credentials
2. Extract the `access_token` from the response
3. Use the token in subsequent requests


"""
            elif scheme.get("type") == "apiKey":
                auth_section += f"""**API Key Authentication**

Include the API key in the `{scheme.get('in', 'header')}` as `{scheme.get('name', 'X-API-Key')}`:

```http
{scheme.get('name', 'X-API-Key')}: <your-api-key>
```

"""
        
        return auth_section
    
        """Create endpoints documentation section"""
        
        endpoints_section = "## 🛠️ API Endpoints\n\n"
        
        # Group endpoints by tags
        endpoints_by_tag = {}
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    tags = operation.get("tags", ["default"])
                    for tag in tags:
                        if tag not in endpoints_by_tag:
                            endpoints_by_tag[tag] = []
                        endpoints_by_tag[tag].append({
                            "path": path,
                            "method": method.upper(),
                            "operation": operation
                        })
        
        # Generate documentation for each tag
        for tag, endpoints in endpoints_by_tag.items():
            endpoints_section += f"### {tag.title()}\n\n"
            
            for endpoint in endpoints:
                operation = endpoint["operation"]
                endpoints_section += f"#### `{endpoint['method']} {endpoint['path']}`\n\n"
                
                if operation.get("summary"):
                    endpoints_section += f"**{operation['summary']}**\n\n"
                
                if operation.get("description"):
                    endpoints_section += f"{operation['description']}\n\n"
                
                # Parameters
                parameters = operation.get("parameters", [])
                if parameters:
                    endpoints_section += "**Parameters:**\n\n"
                    endpoints_section += "| Name | Type | Location | Required | Description |\n"
                    endpoints_section += "|------|------|----------|----------|-------------|\n"
                    
                    for param in parameters:
                        param_schema = param.get("schema", {})
                        endpoints_section += f"| {param.get('name', 'N/A')} | {param_schema.get('type', 'N/A')} | {param.get('in', 'N/A')} | {param.get('required', False)} | {param.get('description', 'N/A')} |\n"
                    endpoints_section += "\n"
                
                # Request body
                request_body = operation.get("requestBody", {})
                if request_body:
                    endpoints_section += "**Request Body:**\n\n"
                    content = request_body.get("content", {})
                    for content_type, content_schema in content.items():
                        endpoints_section += f"*Content-Type: {content_type}*\n\n"
                        if content_schema.get("schema"):
                            endpoints_section += f"```json\n{json.dumps(content_schema['schema'], indent=2)}\n```\n\n"
                
                # Responses
                responses = operation.get("responses", {})
                if responses:
                    endpoints_section += "**Responses:**\n\n"
                    for status_code, response in responses.items():
                        endpoints_section += f"**{status_code}** - {response.get('description', 'N/A')}\n\n"
                        if response.get("content"):
                            for content_type, content_schema in response["content"].items():
                                if content_schema.get("schema"):
                                    endpoints_section += f"*Content-Type: {content_type}*\n\n"
                                    endpoints_section += f"```json\n{json.dumps(content_schema['schema'], indent=2)}\n```\n\n"
                
                
                endpoints_section += "---\n\n"
        
        return endpoints_section
    
        """Create schemas documentation section"""
        
        if not schemas:
            return ""
        
        schemas_section = "## 📊 Data Models\n\n"
        
        for schema_name, schema in schemas.items():
            schemas_section += f"### {schema_name}\n\n"
            
            if schema.get("description"):
                schemas_section += f"{schema['description']}\n\n"
            
            if schema.get("properties"):
                schemas_section += "| Property | Type | Required | Description |\n"
                schemas_section += "|----------|------|----------|-------------|\n"
                
                required_fields = schema.get("required", [])
                for prop_name, prop_schema in schema["properties"].items():
                    prop_type = prop_schema.get("type", "N/A")
                    if prop_schema.get("items"):
                        prop_type = f"array[{prop_schema['items'].get('type', 'N/A')}]"
                    required = "Yes" if prop_name in required_fields else "No"
                    description = prop_schema.get("description", "N/A")
                    schemas_section += f"| {prop_name} | {prop_type} | {required} | {description} |\n"
                
                schemas_section += "\n"
            
            
            schemas_section += "---\n\n"
        
        return schemas_section
    

### Authentication Flow

```python
import requests

# 1. Login to get token
login_response = requests.post("http://localhost:8000/auth/login", json={
    "password": "password"
})

token = login_response.json()["access_token"]

# 2. Use token in subsequent requests
headers = {"Authorization": f"Bearer {token}"}

# 3. Make authenticated requests
response = requests.get("http://localhost:8000/api/agents", headers=headers)
print(response.json())
```

### Error Handling

```python
import requests

try:
    response = requests.get("http://localhost:8000/api/protected-endpoint")
    response.raise_for_status()
    data = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Authentication required")
    elif e.response.status_code == 403:
        print("Access forbidden")
    elif e.response.status_code == 429:
        print("Rate limit exceeded")
    else:
        print(f"HTTP error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
```

"""
    
        """Create error codes section"""
        return """## ❌ Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Bad Request | Check request parameters and format |
| 401 | Unauthorized | Provide valid authentication token |
| 403 | Forbidden | Check user permissions |
| 404 | Not Found | Verify endpoint URL and resource ID |
| 422 | Validation Error | Check request body validation |
| 429 | Too Many Requests | Implement rate limiting |
| 500 | Internal Server Error | Contact support |

"""
    
        """Create rate limiting section"""
        return """## ⚡ Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Limit**: 100 requests per minute per IP
- **Headers**: Rate limit information is included in response headers
- **Exceeded**: Returns 429 status code when limit exceeded

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

"""
    
        """Create changelog section"""
        return f"""## 📝 Changelog


- Initial API documentation
- Comprehensive endpoint coverage

"""
    
        """Generate Postman collection"""
        collection = {
            "info": {
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "auth": {
                "type": "bearer",
                "bearer": [
                    {
                        "key": "token",
                        "value": "{{access_token}}",
                        "type": "string"
                    }
                ]
            },
            "variable": [
                {
                    "key": "base_url",
                    "value": "http://localhost:8000",
                    "type": "string"
                }
            ],
            "item": []
        }
        
        # Convert OpenAPI paths to Postman requests
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    request = {
                        "name": operation.get("summary", f"{method.upper()} {path}"),
                        "request": {
                            "method": method.upper(),
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json",
                                    "type": "text"
                                }
                            ],
                            "url": {
                                "raw": f"{{{{base_url}}}}{path}",
                                "host": ["{{base_url}}"],
                                "path": path.strip("/").split("/")
                            }
                        }
                    }
                    collection["item"].append(request)
        
        with open(self.docs_dir / "postman_collection.json", "w") as f:
            json.dump(collection, f, indent=2)
        
        print("📮 Postman collection generated")
    
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    
                    curl_cmd = f"curl -X {method.upper()} \"http://localhost:8000{path}\" \\\n"
                    curl_cmd += "  -H \"Authorization: Bearer <your-token>\" \\\n"
                    curl_cmd += "  -H \"Content-Type: application/json\""
                    
                    if method.upper() in ["POST", "PUT", "PATCH"]:
                        curl_cmd += " \\\n  -d '{\"key\": \"value\"}'"
                    
        
        
    

```python
import requests
from typing import Optional, Dict, Any

class NexusAPIClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def get_health(self) -> Dict[str, Any]:
        """Get API health status"""
        return self._request("GET", "/health")
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user"""
        return self._request("POST", "/auth/login", json={
            "email": email,
            "password": password
        })
    
    def get_agents(self) -> Dict[str, Any]:
        """Get list of agents"""
        return self._request("GET", "/api/agents")
    
    def create_agent(self, name: str, agent_type: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new agent"""
        return self._request("POST", "/api/agents", json={
            "name": name,
            "type": agent_type,
            "config": config or {}
        })

# Usage
client = NexusAPIClient("http://localhost:8000")
health = client.get_health()
print(health)
```

'''
        
            f.write(python_sdk)
        

class NexusAPIClient {
    constructor(baseUrl, apiKey = null) {
        this.baseUrl = baseUrl.replace(/\\/$/, '');
        this.apiKey = apiKey;
    }
    
    async request(method, endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (this.apiKey) {
            headers['Authorization'] = `Bearer ${this.apiKey}`;
        }
        
        const response = await fetch(url, {
            method,
            headers,
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async getHealth() {
        return this.request('GET', '/health');
    }
    
    async login(email, password) {
        return this.request('POST', '/auth/login', {
            body: JSON.stringify({ email, password })
        });
    }
    
    async getAgents() {
        return this.request('GET', '/api/agents');
    }
    
    async createAgent(name, type, config = {}) {
        return this.request('POST', '/api/agents', {
            body: JSON.stringify({ name, type, config })
        });
    }
}

// Usage
const client = new NexusAPIClient('http://localhost:8000');
client.getHealth().then(health => console.log(health));
```

'''
        
            f.write(js_sdk)
        
    


```python
import requests

    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    assert "status" in response.json()

    response = requests.get("http://localhost:8000/health")
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
```


```python
    response = requests.post("http://localhost:8000/auth/login", json={
        "password": "password"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

    response = requests.post("http://localhost:8000/auth/login", json={
        "password": "wrong"
    })
    assert response.status_code == 401
```


```python
    for i in range(105):  # Exceed rate limit
        response = requests.get("http://localhost:8000/health")
        if i < 100:
            assert response.status_code == 200
        else:
            assert response.status_code == 429

    response = requests.get("http://localhost:8000/health")
    assert "X-Content-Type-Options" in response.headers
    assert "X-Frame-Options" in response.headers
    assert "Strict-Transport-Security" in response.headers
```


```python
    response = requests.get("http://localhost:8000/api/agents")
    assert response.status_code == 401

    # First login to get token
    login_response = requests.post("http://localhost:8000/auth/login", json={
        "password": "password"
    })
    token = login_response.json()["access_token"]
    
    # Then get agents
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("http://localhost:8000/api/agents", headers=headers)
    assert response.status_code == 200
    assert "agents" in response.json()

    # Login first
    login_response = requests.post("http://localhost:8000/auth/login", json={
        "password": "password"
    })
    token = login_response.json()["access_token"]
    
    # Create agent
    headers = {"Authorization": f"Bearer {token}"}
    agent_data = {
        "type": "automation",
        "config": {"enabled": True}
    }
    response = requests.post("http://localhost:8000/api/agents", 
                           headers=headers, json=agent_data)
    assert response.status_code == 201
```

'''
        
        

def main():
    """Main function"""
    generator = StaticAPIDocGenerator()
    success = generator.generate_comprehensive_docs()
    
    if success:
        print("\n🎉 All documentation generated successfully!")
        print(f"📁 Documentation saved to: {generator.docs_dir}")
        print("📝 Markdown docs: docs/api/README.md")
        print("📮 Postman collection: docs/api/postman_collection.json")
    else:
        print("\n❌ Documentation generation failed!")

if __name__ == "__main__":
    main()

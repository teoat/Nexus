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

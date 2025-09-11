#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Input Validation and Sanitization System
========================================

Validate all inputs to prevent:
- File path injection
- Command injection
- Data corruption
- Unauthorized access
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import html
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InputValidationError(Exception):
    """Exception raised for input validation errors"""
    pass

class InputValidationSystem:
    def __init__(self, workspace_root: str = "/Users/Arief/Desktop/Nexus"):
        self.workspace_root = Path(workspace_root)
        
        # Dangerous patterns to detect
        self.dangerous_patterns = [
            r'\.\./',  # Path traversal
            r'\.\.\\',  # Windows path traversal
            r'rm\s+',  # Remove command
            r'del\s+',  # Delete command
            r'format\s+',  # Format command
            r'shutdown',  # Shutdown command
            r'reboot',  # Reboot command
            r'<script',  # Script injection
            r'javascript:',  # JavaScript injection
            r'data:',  # Data URI
            r'vbscript:',  # VBScript injection
            r'onload=',  # Event handler injection
            r'onerror=',  # Event handler injection
            r'onclick=',  # Event handler injection
            r'exec\s*\(',  # Code execution
            r'eval\s*\(',  # Code evaluation
            r'__import__',  # Dynamic import
            r'getattr',  # Attribute access
            r'setattr',  # Attribute modification
            r'delattr',  # Attribute deletion
            r'globals\s*\(',  # Global access
            r'locals\s*\(',  # Local access
            r'vars\s*\(',  # Variable access
            r'dir\s*\(',  # Directory listing
            r'open\s*\(',  # File access
            r'file\s*\(',  # File access
            r'input\s*\(',  # Input function
            r'raw_input\s*\(',  # Raw input function
            r'compile\s*\(',  # Code compilation
            r'__builtins__',  # Built-in access
            r'__import__',  # Import access
            r'__globals__',  # Global access
            r'__locals__',  # Local access
            r'__code__',  # Code access
            r'__func__',  # Function access
            r'__self__',  # Self access
            r'__class__',  # Class access
            r'__bases__',  # Base classes
            r'__mro__',  # Method resolution order
            r'__subclasses__',  # Subclasses
            r'__mro__',  # Method resolution order
            r'__subclasses__',  # Subclasses
            r'__getattribute__',  # Attribute getter
            r'__setattr__',  # Attribute setter
            r'__delattr__',  # Attribute deleter
            r'__getitem__',  # Item getter
            r'__setitem__',  # Item setter
            r'__delitem__',  # Item deleter
            r'__call__',  # Call method
            r'__enter__',  # Context manager enter
            r'__exit__',  # Context manager exit
            r'__iter__',  # Iterator
            r'__next__',  # Next item
            r'__len__',  # Length
            r'__bool__',  # Boolean conversion
            r'__int__',  # Integer conversion
            r'__float__',  # Float conversion
            r'__str__',  # String conversion
            r'__repr__',  # Representation
            r'__hash__',  # Hash
            r'__eq__',  # Equality
            r'__ne__',  # Inequality
            r'__lt__',  # Less than
            r'__le__',  # Less than or equal
            r'__gt__',  # Greater than
            r'__ge__',  # Greater than or equal
            r'__add__',  # Addition
            r'__sub__',  # Subtraction
            r'__mul__',  # Multiplication
            r'__truediv__',  # True division
            r'__floordiv__',  # Floor division
            r'__mod__',  # Modulo
            r'__pow__',  # Power
            r'__lshift__',  # Left shift
            r'__rshift__',  # Right shift
            r'__and__',  # Bitwise AND
            r'__or__',  # Bitwise OR
            r'__xor__',  # Bitwise XOR
            r'__invert__',  # Bitwise NOT
            r'__pos__',  # Unary plus
            r'__neg__',  # Unary minus
            r'__abs__',  # Absolute value
            r'__round__',  # Round
            r'__trunc__',  # Truncate
            r'__floor__',  # Floor
            r'__ceil__',  # Ceiling
            r'__index__',  # Index
            r'__int__',  # Integer conversion
            r'__float__',  # Float conversion
            r'__complex__',  # Complex conversion
            r'__oct__',  # Octal conversion
            r'__hex__',  # Hexadecimal conversion
            r'__bool__',  # Boolean conversion
            r'__bytes__',  # Bytes conversion
            r'__format__',  # Format
            r'__sizeof__',  # Size
            r'__reduce__',  # Pickle reduce
            r'__reduce_ex__',  # Pickle reduce ex
            r'__getstate__',  # Pickle get state
            r'__setstate__',  # Pickle set state
            r'__getnewargs__',  # Pickle get new args
            r'__getnewargs_ex__',  # Pickle get new args ex
            r'__getinitargs__',  # Pickle get init args
            r'__getinitargs_ex__',  # Pickle get init args ex
            r'__getnewargs__',  # Pickle get new args
            r'__getnewargs_ex__',  # Pickle get new args ex
            r'__getinitargs__',  # Pickle get init args
            r'__getinitargs_ex__',  # Pickle get init args ex
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.dangerous_patterns]
        
        # Allowed file extensions
        self.allowed_extensions = {
            '.py', '.md', '.json', '.txt', '.log', '.yml', '.yaml',
            '.sh', '.bat', '.cmd', '.ps1', '.sql', '.html', '.css',
            '.js', '.ts', '.tsx', '.jsx', '.vue', '.svelte'
        }
        
        # Maximum lengths
        self.max_lengths = {
            'task_line': 1000,
            'file_path': 500,
            'command': 200,
            'json_string': 10000,
            'url': 2000
        }
    
    def validate_task_input(self, task_line: str) -> str:
        """Validate task input for security and integrity"""
        if not isinstance(task_line, str):
            raise InputValidationError("Task must be a string")
        
        # Check length
        if len(task_line) > self.max_lengths['task_line']:
            raise InputValidationError(f"Task too long (max {self.max_lengths['task_line']} characters)")
        
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(task_line):
                raise InputValidationError(f"Potentially dangerous content detected: {pattern.pattern}")
        
        # Sanitize HTML
        sanitized = html.escape(task_line)
        
        return sanitized.strip()
    
    def validate_file_path(self, file_path: str) -> Path:
        """Validate and sanitize file path"""
        if not isinstance(file_path, str):
            raise InputValidationError("File path must be a string")
        
        # Check length
        if len(file_path) > self.max_lengths['file_path']:
            raise InputValidationError(f"File path too long (max {self.max_lengths['file_path']} characters)")
        
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(file_path):
                raise InputValidationError(f"Potentially dangerous file path: {pattern.pattern}")
        
        # Convert to Path object
        path = Path(file_path)
        
        # Resolve path to prevent directory traversal
        try:
            resolved_path = path.resolve()
        except Exception as e:
            raise InputValidationError(f"Invalid file path: {e}")
        
        # Check if path is within workspace
        try:
            resolved_path.relative_to(self.workspace_root)
        except ValueError:
            raise InputValidationError("File path outside workspace not allowed")
        
        # Check file extension
        if resolved_path.suffix and resolved_path.suffix not in self.allowed_extensions:
            raise InputValidationError(f"File extension not allowed: {resolved_path.suffix}")
        
        return resolved_path
    
    def validate_command(self, command: str) -> str:
        """Validate command input"""
        if not isinstance(command, str):
            raise InputValidationError("Command must be a string")
        
        # Check length
        if len(command) > self.max_lengths['command']:
            raise InputValidationError(f"Command too long (max {self.max_lengths['command']} characters)")
        
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(command):
                raise InputValidationError(f"Potentially dangerous command: {pattern.pattern}")
        
        # Sanitize command
        sanitized = html.escape(command)
        
        return sanitized.strip()
    
    def validate_json_input(self, json_string: str) -> Dict[str, Any]:
        """Validate JSON input"""
        if not isinstance(json_string, str):
            raise InputValidationError("JSON input must be a string")
        
        # Check length
        if len(json_string) > self.max_lengths['json_string']:
            raise InputValidationError(f"JSON too long (max {self.max_lengths['json_string']} characters)")
        
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(json_string):
                raise InputValidationError(f"Potentially dangerous JSON content: {pattern.pattern}")
        
        # Parse JSON
        try:
            parsed = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise InputValidationError(f"Invalid JSON: {e}")
        
        # Validate parsed content
        if isinstance(parsed, dict):
            for key, value in parsed.items():
                if not isinstance(key, str):
                    raise InputValidationError("JSON keys must be strings")
                if len(key) > 100:
                    raise InputValidationError("JSON key too long")
                if isinstance(value, str) and len(value) > 1000:
                    raise InputValidationError("JSON string value too long")
        
        return parsed
    
    def validate_url(self, url: str) -> str:
        """Validate URL input"""
        if not isinstance(url, str):
            raise InputValidationError("URL must be a string")
        
        # Check length
        if len(url) > self.max_lengths['url']:
            raise InputValidationError(f"URL too long (max {self.max_lengths['url']} characters)")
        
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(url):
                raise InputValidationError(f"Potentially dangerous URL: {pattern.pattern}")
        
        # Parse URL
        try:
            parsed = urllib.parse.urlparse(url)
        except Exception as e:
            raise InputValidationError(f"Invalid URL: {e}")
        
        # Check scheme
        allowed_schemes = {'http', 'https', 'file'}
        if parsed.scheme and parsed.scheme not in allowed_schemes:
            raise InputValidationError(f"URL scheme not allowed: {parsed.scheme}")
        
        # Sanitize URL
        sanitized = urllib.parse.quote(url, safe=':/?#[]@!$&()*+,;=')
        
        return sanitized
    
    def sanitize_html(self, html_content: str) -> str:
        """Sanitize HTML content"""
        if not isinstance(html_content, str):
            raise InputValidationError("HTML content must be a string")
        
        # Escape HTML entities
        sanitized = html.escape(html_content)
        
        return sanitized
    
    def sanitize_sql(self, sql_content: str) -> str:
        """Sanitize SQL content"""
        if not isinstance(sql_content, str):
            raise InputValidationError("SQL content must be a string")
        
        # Check for dangerous SQL patterns
        dangerous_sql_patterns = [
            r'drop\s+table',
            r'drop\s+database',
            r'delete\s+from',
            r'truncate\s+table',
            r'alter\s+table',
            r'create\s+table',
            r'insert\s+into',
            r'update\s+set',
            r'grant\s+',
            r'revoke\s+',
            r'exec\s*\(',
            r'execute\s*\(',
            r'sp_',
            r'xp_',
            r'--',  # SQL comment
            r'/\*',  # SQL comment
            r'\*/',  # SQL comment
            r'union\s+select',
            r'select\s+.*\s+from\s+.*\s+union',
            r'insert\s+into\s+.*\s+values\s*\(',
            r'update\s+.*\s+set\s+.*\s+where',
            r'delete\s+from\s+.*\s+where',
        ]
        
        for pattern in dangerous_sql_patterns:
            if re.search(pattern, sql_content, re.IGNORECASE):
                raise InputValidationError(f"Potentially dangerous SQL: {pattern}")
        
        # Escape single quotes
        sanitized = sql_content.replace("'", "''")
        
        return sanitized
    
    def validate_email(self, email: str) -> str:
        """Validate email address"""
        if not isinstance(email, str):
            raise InputValidationError("Email must be a string")
        
        # Check length
        if len(email) > 254:
            raise InputValidationError("Email too long")
        
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(email):
                raise InputValidationError(f"Potentially dangerous email: {pattern.pattern}")
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise InputValidationError("Invalid email format")
        
        return email.lower().strip()
    
    def validate_username(self, username: str) -> str:
        """Validate username"""
        if not isinstance(username, str):
            raise InputValidationError("Username must be a string")
        
        # Check length
        if len(username) < 3 or len(username) > 50:
            raise InputValidationError("Username must be 3-50 characters")
        
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(username):
                raise InputValidationError(f"Potentially dangerous username: {pattern.pattern}")
        
        # Check for valid characters
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise InputValidationError("Username can only contain letters, numbers, underscores, and hyphens")
        
        return username.lower().strip()
    
    def validate_password(self, password: str) -> str:
        """Validate password"""
        if not isinstance(password, str):
            raise InputValidationError("Password must be a string")
        
        # Check length
        if len(password) < 8 or len(password) > 128:
            raise InputValidationError("Password must be 8-128 characters")
        
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(password):
                raise InputValidationError(f"Potentially dangerous password: {pattern.pattern}")
        
        # Check complexity
        if not re.search(r'[A-Z]', password):
            raise InputValidationError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            raise InputValidationError("Password must contain at least one lowercase letter")
        
        if not re.search(r'[0-9]', password):
            raise InputValidationError("Password must contain at least one number")
        
        if not re.search(r'[^A-Za-z0-9]', password):
            raise InputValidationError("Password must contain at least one special character")
        
        return password
    
    def validate_ip_address(self, ip: str) -> str:
        """Validate IP address"""
        if not isinstance(ip, str):
            raise InputValidationError("IP address must be a string")
        
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(ip):
                raise InputValidationError(f"Potentially dangerous IP address: {pattern.pattern}")
        
        # Basic IP validation
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        
        if not (re.match(ipv4_pattern, ip) or re.match(ipv6_pattern, ip)):
            raise InputValidationError("Invalid IP address format")
        
        # Validate IPv4 octets
        if re.match(ipv4_pattern, ip):
            octets = ip.split('.')
            for octet in octets:
                if int(octet) > 255:
                    raise InputValidationError("Invalid IPv4 address")
        
        return ip.strip()
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return {
            'dangerous_patterns_count': len(self.dangerous_patterns),
            'allowed_extensions_count': len(self.allowed_extensions),
            'max_lengths': self.max_lengths,
            'workspace_root': str(self.workspace_root)
        }

def main():
    """Main function"""
    validator = InputValidationSystem()
    
    print("🔒 Input Validation and Sanitization System")
    print("=" * 50)
    
    # Test various validations
    test_cases = [
        ("Task input", "⏳ **API** (🔴 critical) - Valid task"),
        ("File path", "master_todo.md"),
        ("Command", "python script.py"),
        ("JSON", '{"key": "value"}'),
        ("URL", "https://example.com"),
        ("Email", "user@example.com"),
        ("Username", "testuser123"),
        ("IP address", "192.168.1.1")
    ]
    
    for test_type, test_value in test_cases:
        try:
            if test_type == "Task input":
                result = validator.validate_task_input(test_value)
            elif test_type == "File path":
                result = validator.validate_file_path(test_value)
            elif test_type == "Command":
                result = validator.validate_command(test_value)
            elif test_type == "JSON":
                result = validator.validate_json_input(test_value)
            elif test_type == "URL":
                result = validator.validate_url(test_value)
            elif test_type == "Email":
                result = validator.validate_email(test_value)
            elif test_type == "Username":
                result = validator.validate_username(test_value)
            elif test_type == "IP address":
                result = validator.validate_ip_address(test_value)
            
            print(f"✅ {test_type}: {result}")
            
        except InputValidationError as e:
            print(f"❌ {test_type}: {e}")
    
    # Test dangerous inputs
    print("\n🚨 Testing dangerous inputs:")
    dangerous_tests = [
        ("Path traversal", "../../../etc/passwd"),
        ("Command injection", "rm -rf /"),
        ("Script injection", "<script>alert('xss')</script>"),
        ("SQL injection", "'; DROP TABLE users; --")
    ]
    
    for test_type, test_value in dangerous_tests:
        try:
            result = validator.validate_task_input(test_value)
            print(f"❌ {test_type}: Should have been rejected but got: {result}")
        except InputValidationError as e:
            print(f"✅ {test_type}: Correctly rejected - {e}")
    
    # Show stats
    stats = validator.get_validation_stats()
    print(f"\n📊 Validation Statistics:")
    print(f"   Dangerous patterns: {stats['dangerous_patterns_count']}")
    print(f"   Allowed extensions: {stats['allowed_extensions_count']}")
    print(f"   Workspace root: {stats['workspace_root']}")

if __name__ == "__main__":
    main()

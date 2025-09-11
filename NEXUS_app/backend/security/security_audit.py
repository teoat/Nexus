#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔒 Security Audit Module for Nexus Platform
Comprehensive security checks and vulnerability scanning
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime
import subprocess
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class SecurityAuditor:
    """Comprehensive security audit system"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "vulnerabilities": [],
            "recommendations": []
        }
    
    async def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run all security checks"""
        logger.info("🔍 Starting comprehensive security audit...")
        
        # Run all security checks
        await self.check_dependencies()
        await self.check_authentication_security()
        await self.check_input_validation()
        await self.check_file_upload_security()
        await self.check_database_security()
        await self.check_api_security()
        await self.check_environment_security()
        await self.check_headers_security()
        
        # Generate security score
        self.audit_results["security_score"] = self._calculate_security_score()
        
        logger.info(f"✅ Security audit completed. Score: {self.audit_results['security_score']}/100")
        return self.audit_results
    
    async def check_dependencies(self):
        """Check for vulnerable dependencies"""
        logger.info("🔍 Checking dependencies for vulnerabilities...")
        
        try:
            # Run safety check
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            if result.returncode == 0:
                self.audit_results["checks"]["dependencies"] = {
                    "status": "PASS",
                    "message": "No vulnerable dependencies found"
                }
            else:
                try:
                    vulnerabilities = json.loads(result.stdout) if result.stdout else []
                except json.JSONDecodeError:
                    # Safety sometimes outputs non-JSON format, parse as text
                    vulnerabilities = []
                    if result.stdout and "vulnerability" in result.stdout.lower():
                        # Count vulnerabilities by counting lines with "vulnerability"
                        vulnerabilities = [{"package": "unknown", "vulnerability": "found"}] * result.stdout.count("vulnerability")
                
                self.audit_results["vulnerabilities"].extend(vulnerabilities)
                self.audit_results["checks"]["dependencies"] = {
                    "status": "FAIL",
                    "message": f"Found {len(vulnerabilities)} vulnerable dependencies"
                }
                
        except FileNotFoundError:
            self.audit_results["checks"]["dependencies"] = {
                "status": "WARNING",
                "message": "Safety tool not installed. Install with: pip install safety"
            }
            self.audit_results["recommendations"].append(
                "Install safety tool for dependency vulnerability scanning"
            )
    
    async def check_authentication_security(self):
        """Check authentication security implementation"""
        logger.info("🔍 Checking authentication security...")
        
        issues = []
        
        # Check JWT implementation
        jwt_file = Path(__file__).parent.parent / "auth" / "jwt_handler.py"
        if jwt_file.exists():
            with open(jwt_file, 'r') as f:
                content = f.read()
                if "HS256" in content and "RS256" not in content:
                    issues.append("Using weak HS256 algorithm instead of RS256")
                if "exp" not in content:
                    issues.append("JWT tokens may not have expiration")
        else:
            issues.append("JWT handler not found")
        
        # Check password hashing
        auth_file = Path(__file__).parent.parent / "auth" / "password_handler.py"
        if auth_file.exists():
            with open(auth_file, 'r') as f:
                content = f.read()
                if "bcrypt" not in content.lower():
                    issues.append("Not using bcrypt for password hashing")
        else:
            issues.append("Password handler not found")
        
        if issues:
            self.audit_results["checks"]["authentication"] = {
                "status": "FAIL",
                "issues": issues
            }
            self.audit_results["vulnerabilities"].extend(issues)
        else:
            self.audit_results["checks"]["authentication"] = {
                "status": "PASS",
                "message": "Authentication security looks good"
            }
    
    async def check_input_validation(self):
        """Check input validation implementation"""
        logger.info("🔍 Checking input validation...")
        
        issues = []
        
        # Check for SQL injection protection
        api_files = list(Path(__file__).parent.parent.glob("**/*.py"))
        for file_path in api_files:
            if "api" in str(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                    if "execute(" in content and "parameterized" not in content:
                        issues.append(f"Potential SQL injection in {file_path}")
        
        # Check for XSS protection
        if not any("escape" in str(file_path) for file_path in api_files):
            issues.append("No XSS protection found")
        
        if issues:
            self.audit_results["checks"]["input_validation"] = {
                "status": "FAIL",
                "issues": issues
            }
            self.audit_results["vulnerabilities"].extend(issues)
        else:
            self.audit_results["checks"]["input_validation"] = {
                "status": "PASS",
                "message": "Input validation looks good"
            }
    
    async def check_file_upload_security(self):
        """Check file upload security"""
        logger.info("🔍 Checking file upload security...")
        
        issues = []
        
        # Check file type validation
        upload_files = list(Path(__file__).parent.parent.glob("**/upload*.py"))
        for file_path in upload_files:
            with open(file_path, 'r') as f:
                content = f.read()
                if "content_type" not in content.lower():
                    issues.append(f"File type validation missing in {file_path}")
                if "file_size" not in content.lower():
                    issues.append(f"File size validation missing in {file_path}")
        
        if issues:
            self.audit_results["checks"]["file_upload"] = {
                "status": "FAIL",
                "issues": issues
            }
            self.audit_results["vulnerabilities"].extend(issues)
        else:
            self.audit_results["checks"]["file_upload"] = {
                "status": "PASS",
                "message": "File upload security looks good"
            }
    
    async def check_database_security(self):
        """Check database security configuration"""
        logger.info("🔍 Checking database security...")
        
        issues = []
        
        # Check database configuration
        config_file = Path(__file__).parent.parent / "database" / "config.py"
        if config_file.exists():
            with open(config_file, 'r') as f:
                content = f.read()
                if "ssl" not in content.lower():
                    issues.append("Database SSL not configured")
                if "password" in content and "os.getenv" not in content:
                    issues.append("Database password may be hardcoded")
        
        if issues:
            self.audit_results["checks"]["database"] = {
                "status": "FAIL",
                "issues": issues
            }
            self.audit_results["vulnerabilities"].extend(issues)
        else:
            self.audit_results["checks"]["database"] = {
                "status": "PASS",
                "message": "Database security looks good"
            }
    
    async def check_api_security(self):
        """Check API security implementation"""
        logger.info("🔍 Checking API security...")
        
        issues = []
        
        # Check for rate limiting
        middleware_files = list(Path(__file__).parent.parent.glob("**/middleware*.py"))
        rate_limiting_found = False
        for file_path in middleware_files:
            with open(file_path, 'r') as f:
                content = f.read()
                if "rate" in content.lower() and "limit" in content.lower():
                    rate_limiting_found = True
                    break
        
        if not rate_limiting_found:
            issues.append("Rate limiting not implemented")
        
        # Check for CORS configuration
        main_file = Path(__file__).parent.parent / "main_enhanced.py"
        if main_file.exists():
            with open(main_file, 'r') as f:
                content = f.read()
                if "cors" in content.lower():
                    if "allow_origins" in content and "*" in content:
                        issues.append("CORS allows all origins (*)")
                else:
                    issues.append("CORS not configured")
        
        if issues:
            self.audit_results["checks"]["api_security"] = {
                "status": "FAIL",
                "issues": issues
            }
            self.audit_results["vulnerabilities"].extend(issues)
        else:
            self.audit_results["checks"]["api_security"] = {
                "status": "PASS",
                "message": "API security looks good"
            }
    
    async def check_environment_security(self):
        """Check environment and configuration security"""
        logger.info("🔍 Checking environment security...")
        
        issues = []
        
        # Check for .env file security
        env_file = Path(__file__).parent.parent.parent / ".env"
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
                if "password" in content.lower() and "secret" in content.lower():
                    if not any(line.startswith("#") for line in content.split('\n') if "password" in line.lower()):
                        issues.append("Sensitive data in .env file without proper comments")
        else:
            issues.append(".env file not found - using environment variables")
        
        # Check for debug mode
        main_file = Path(__file__).parent.parent / "main_enhanced.py"
        if main_file.exists():
            with open(main_file, 'r') as f:
                content = f.read()
                if "debug=true" in content.lower():
                    issues.append("Debug mode enabled in production")
        
        if issues:
            self.audit_results["checks"]["environment"] = {
                "status": "FAIL",
                "issues": issues
            }
            self.audit_results["vulnerabilities"].extend(issues)
        else:
            self.audit_results["checks"]["environment"] = {
                "status": "PASS",
                "message": "Environment security looks good"
            }
    
    async def check_headers_security(self):
        """Check security headers implementation"""
        logger.info("🔍 Checking security headers...")
        
        issues = []
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy"
        ]
        
        # Check if security headers middleware exists
        middleware_files = list(Path(__file__).parent.parent.glob("**/middleware*.py"))
        security_headers_found = False
        
        for file_path in middleware_files:
            with open(file_path, 'r') as f:
                content = f.read()
                if any(header.lower().replace("-", "_") in content.lower() for header in required_headers):
                    security_headers_found = True
                    break
        
        if not security_headers_found:
            issues.append("Security headers not implemented")
        
        if issues:
            self.audit_results["checks"]["security_headers"] = {
                "status": "FAIL",
                "issues": issues
            }
            self.audit_results["vulnerabilities"].extend(issues)
        else:
            self.audit_results["checks"]["security_headers"] = {
                "status": "PASS",
                "message": "Security headers implemented"
            }
    
    def _calculate_security_score(self) -> int:
        """Calculate overall security score"""
        total_checks = len(self.audit_results["checks"])
        passed_checks = sum(1 for check in self.audit_results["checks"].values() 
                           if check["status"] == "PASS")
        
        if total_checks == 0:
            return 0
        
        base_score = (passed_checks / total_checks) * 100
        
        # Deduct points for vulnerabilities
        vulnerability_penalty = min(len(self.audit_results["vulnerabilities"]) * 5, 30)
        
        return max(int(base_score - vulnerability_penalty), 0)
    
    def generate_report(self) -> str:
        """Generate human-readable security report"""
        report = f"""
# 🔒 Security Audit Report
**Generated:** {self.audit_results['timestamp']}
**Security Score:** {self.audit_results['security_score']}/100

## 📊 Check Results
"""
        
        for check_name, result in self.audit_results["checks"].items():
            status_emoji = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            report += f"\n### {status_emoji} {check_name.replace('_', ' ').title()}\n"
            report += f"**Status:** {result['status']}\n"
            report += f"**Message:** {result.get('message', 'N/A')}\n"
            
            if 'issues' in result:
                report += "**Issues:**\n"
                for issue in result['issues']:
                    report += f"- {issue}\n"
        
        if self.audit_results["vulnerabilities"]:
            report += "\n## 🚨 Vulnerabilities Found\n"
            for vuln in self.audit_results["vulnerabilities"]:
                report += f"- {vuln}\n"
        
        if self.audit_results["recommendations"]:
            report += "\n## 💡 Recommendations\n"
            for rec in self.audit_results["recommendations"]:
                report += f"- {rec}\n"
        
        return report

# CLI interface
async def main():
    """Run security audit from command line"""
    auditor = SecurityAuditor()
    results = await auditor.run_comprehensive_audit()
    
    # Print results
    print(auditor.generate_report())
    
    # Save results to file
    report_file = Path(__file__).parent / "security_audit_report.md"
    with open(report_file, 'w') as f:
        f.write(auditor.generate_report())
    
    print(f"\n📄 Full report saved to: {report_file}")

if __name__ == "__main__":
    asyncio.run(main())

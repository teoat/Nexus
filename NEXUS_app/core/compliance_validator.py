#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔍 Compliance Validator for Nexus Platform
Automatically validates file organization, naming conventions, and structural compliance.
"""

import asyncio
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Any
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComplianceValidator:
    """Validates compliance with Nexus Platform standards."""
    
    def __init__(self, workspace_path: str):
        """
          Init  
        
        
        Args:
            workspace_path: Description of workspace_path
    
        Example:
            TBD: Add usage example
        """
        self.workspace_path = Path(workspace_path)
        self.validation_results = {}
        self.compliance_score = 0.0
        
        # Required directories and files
        self.required_dirs = [
            "NEXUS_app/core", "NEXUS_app/frontend", "NEXUS_app/api",
            "NEXUS_app/ai", "NEXUS_app/monitoring", "NEXUS_app/automation",
            "docs", "config", "scripts", "tools", "assets", "backups"
        ]
        
        self.required_files = [
            "README.md", "nexus_platform_launcher.py", "nexus_platform_config.json",
            "requirements.txt", "docker-compose.yml", "NEXUS_app/core/__init__.py"
        ]
        
        logger.info("✅ Compliance Validator initialized")
    
    async def validate_compliance(self) -> Dict[str, Any]:
        """Perform comprehensive compliance validation."""
        logger.info("🔍 Starting compliance validation...")
        
        try:
            # Validate file organization
            org_results = await self._validate_file_organization()
            self.validation_results["file_organization"] = org_results
            
            # Validate naming conventions
            naming_results = await self._validate_naming_conventions()
            self.validation_results["naming_conventions"] = naming_results
            
            # Calculate compliance score
            self.compliance_score = self._calculate_compliance_score()
            
            logger.info(f"✅ Compliance validation completed. Score: {self.compliance_score:.1f}%")
            
            return {
                "success": True,
                "compliance_score": self.compliance_score,
                "results": self.validation_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Compliance validation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _validate_file_organization(self) -> Dict[str, Any]:
        """Validate file and directory organization."""
        logger.info("📁 Validating file organization...")
        
        results = {"valid": True, "errors": [], "details": {}}
        
        # Check required directories
        missing_dirs = []
        for required_dir in self.required_dirs:
            dir_path = self.workspace_path / required_dir
            if not dir_path.exists():
                missing_dirs.append(required_dir)
                results["errors"].append(f"Missing directory: {required_dir}")
        
        # Check required files
        missing_files = []
        for required_file in self.required_files:
            file_path = self.workspace_path / required_file
            if not file_path.exists():
                missing_files.append(required_file)
                results["errors"].append(f"Missing file: {required_file}")
        
        if missing_dirs or missing_files:
            results["valid"] = False
        
        results["details"] = {
            "missing_directories": missing_dirs,
            "missing_files": missing_files
        }
        
        return results
    
    async def _validate_naming_conventions(self) -> Dict[str, Any]:
        """Validate naming conventions."""
        logger.info("📝 Validating naming conventions...")
        
        results = {"valid": True, "errors": [], "details": {}}
        
        violations = []
        
        # Check Python files
        for root, dirs, files in os.walk(self.workspace_path):
            for file_name in files:
                if file_name.endswith('.py'):
                    if not re.match(r"^[a-z][a-z0-9_]*\.py$", file_name):
                        violations.append(f"Python file naming: {file_name}")
        
        if violations:
            results["valid"] = False
            results["errors"].extend(violations)
        
        results["details"]["naming_violations"] = violations
        
        return results
    
    def _calculate_compliance_score(self) -> float:
        """Calculate compliance score."""
        if not self.validation_results:
            return 0.0
        
        total_checks = len(self.validation_results)
        passed_checks = sum(1 for r in self.validation_results.values() if r.get("valid", False))
        
        return (passed_checks / total_checks) * 100.0 if total_checks > 0 else 0.0
    
    def get_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report."""
        return {
            "compliance_score": self.compliance_score,
            "validation_results": self.validation_results,
            "timestamp": datetime.now().isoformat()
        }

async def main():
    validator = ComplianceValidator("/Users/Arief/Desktop/Nexus")
    
    # Run compliance validation
    result = await validator.validate_compliance()
    print(f"Validation Result: {result}")
    
    # Generate report
    report = validator.get_compliance_report()
    print(f"\nCompliance Score: {report['compliance_score']:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())

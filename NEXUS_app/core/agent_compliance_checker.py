#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Agent Compliance Checker
Validates all agent actions against the single source of truth and unified file organization.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ComplianceViolation:
    """Record of a compliance violation"""
    timestamp: str
    agent_id: str
    action: str
    target: str
    violation_type: str
    severity: str
    description: str
    recommendations: List[str]
    resolved: bool = False

@dataclass
class ComplianceReport:
    """Comprehensive compliance report"""
    timestamp: str
    total_checks: int
    violations: int
    compliance_rate: float
    violations_by_agent: Dict[str, int]
    violations_by_type: Dict[str, int]
    recent_violations: List[ComplianceViolation]

class AgentComplianceChecker:
    """Checks agent compliance with single source of truth"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.violations_file = self.workspace_path / ".mcp" / "compliance_violations.json"
        self.compliance_log = self.workspace_path / ".mcp" / "compliance.log"
        
        # Ensure MCP directory exists
        self.violations_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing violations
        self.violations: List[ComplianceViolation] = []
        self.load_violations()
        
        # Single source of truth files
        self.sot_files = {
            "file_organization": "docs/UNIFIED_FILE_ORGANIZATION.md",
            "structure_analysis": "docs/FILE_STRUCTURE_ANALYSIS.md",
            "implementation_roadmap": "docs/IMPLEMENTATION_ROADMAP.md"
        }
        
        # Compliance rules
        self.compliance_rules = self._load_compliance_rules()
    
    def load_violations(self):
        """Load existing compliance violations"""
        try:
            if self.violations_file.exists():
                with open(self.violations_file, 'r') as f:
                    data = json.load(f)
                    for violation_data in data.get('violations', []):
                        self.violations.append(ComplianceViolation(**violation_data))
                logger.info(f"Loaded {len(self.violations)} existing violations")
        except Exception as e:
            logger.error(f"Error loading violations: {e}")
    
    def save_violations(self):
        """Save compliance violations to file"""
        try:
            data = {
                'violations': [asdict(violation) for violation in self.violations],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.violations_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving violations: {e}")
    
    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load compliance rules from single source of truth"""
        rules = {
            "file_naming": {
                "pattern": "lowercase_with_underscores",
                "description": "All files and directories must use lowercase with underscores",
            },
            "directory_structure": {
                "pattern": "unified_organization",
                "description": "Files must be placed in appropriate directories according to unified organization",
            },
            "documentation_standards": {
                "pattern": "single_source_of_truth",
                "description": "All documentation must reference the single source of truth",
            },
            "agent_communication": {
                "pattern": "mcp_protocol",
                "description": "All agents must communicate via MCP protocol",
            }
        }
        
        # Try to load from SOT files
        sot_content = self.get_single_source_of_truth("file_organization")
        if sot_content:
            # Extract rules from content
            if "lowercase with underscores" in sot_content.lower():
                rules["file_naming"]["enforced"] = True
            if "unified file organization" in sot_content.lower():
                rules["directory_structure"]["enforced"] = True
        
        return rules
    
    def get_single_source_of_truth(self, file_type: str) -> Optional[str]:
        """Get content from single source of truth files"""
        if file_type in self.sot_files:
            file_path = self.workspace_path / self.sot_files[file_type]
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        return f.read()
                except Exception as e:
                    logger.error(f"Error reading SOT file {file_path}: {e}")
        return None
    
    def check_file_naming_compliance(self, file_path: str) -> Dict[str, Any]:
        """Check if file naming follows conventions"""
        path_obj = Path(file_path)
        violations = []
        
        for part in path_obj.parts:
            # Check for lowercase
            if not part.islower():
                violations.append(f"Directory/file '{part}' should be lowercase")
            
            # Check for valid characters
            if not all(c.islower() or c.isdigit() or c in ['_', '-'] for c in part):
                violations.append(f"Directory/file '{part}' contains invalid characters")
            
            # Check for no spaces
            if ' ' in part:
                violations.append(f"Directory/file '{part}' contains spaces")
            
            if any(c in part for c in ['(', ')', '[', ']', '{', '}', '&', '+', '=']):
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "recommendations": [
                "Use lowercase letters only",
                "Use underscores instead of spaces",
                "Use hyphens only when necessary"
            ]
        }
    
    def check_directory_structure_compliance(self, file_path: str) -> Dict[str, Any]:
        """Check if file is in correct directory according to unified organization"""
        try:
            relative_path = Path(file_path).relative_to(self.workspace_path)
        except ValueError:
            return {
                "compliant": False,
                "violations": ["File is outside workspace"],
                "recommendations": ["Move file to workspace directory"]
            }
        
        path_str = str(relative_path)
        violations = []
        
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
        
        # Check if file is in appropriate directory
        if not any(pattern in path_str for pattern in valid_patterns):
            violations.append(f"File '{relative_path}' is not in appropriate directory")
            violations.append("Review UNIFIED_FILE_ORGANIZATION.md for correct placement")
        
        file_extension = relative_path.suffix.lower()
        if file_extension == '.md' and 'docs/' not in path_str:
            violations.append("Documentation files should be in docs/ directory")
        
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "recommendations": [
                "Move file to appropriate directory according to unified organization",
                "Review UNIFIED_FILE_ORGANIZATION.md for correct placement",
                "Follow the established directory structure"
            ]
        }
    
    def check_agent_action_compliance(self, agent_id: str, action: str, target: str) -> Dict[str, Any]:
        """Check if an agent action is compliant with SOT rules"""
        violations = []
        recommendations = []
        
        # Check file operations
        if target and Path(target).exists():
            # Check naming compliance
            naming_check = self.check_file_naming_compliance(target)
            if not naming_check["compliant"]:
                violations.extend(naming_check["violations"])
                recommendations.extend(naming_check["recommendations"])
            
            # Check directory structure compliance
            structure_check = self.check_directory_structure_compliance(target)
            if not structure_check["compliant"]:
                violations.extend(structure_check["violations"])
                recommendations.extend(structure_check["recommendations"])
        
        # Check action compliance
        if action in ["create_file", "move_file", "rename_file"]:
            if not self._is_action_compliant(action, target):
                violations.append(f"Action '{action}' may violate SOT rules")
                recommendations.append("Review UNIFIED_FILE_ORGANIZATION.md before proceeding")
        
        # Determine severity
        severity = "high" if len(violations) > 2 else "medium" if len(violations) > 0 else "low"
        
        # Record violation if any
        if violations:
            violation = ComplianceViolation(
                timestamp=datetime.now().isoformat(),
                agent_id=agent_id,
                action=action,
                target=target,
                violation_type="file_organization",
                severity=severity,
                description="; ".join(violations),
                recommendations=recommendations
            )
            self.violations.append(violation)
            self.save_violations()
            
            # Log violation
            self.log_compliance_event("violation", f"Agent {agent_id} action '{action}' on '{target}' - {len(violations)} violations")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "recommendations": recommendations,
            "severity": severity
        }
    
    def _is_action_compliant(self, action: str, target: str) -> bool:
        """Check if an action is compliant with SOT rules"""
        # Basic compliance checks
        if action == "create_file":
            return self._is_valid_creation_location(target)
        elif action == "move_file":
            return self._is_valid_move_operation(target)
        elif action == "rename_file":
            return self._is_valid_filename(target)
        
        return True
    
    def _is_valid_creation_location(self, target: str) -> bool:
        """Check if file creation location is valid"""
        target_path = Path(target)
        structure_check = self.check_directory_structure_compliance(str(target_path))
        return structure_check["compliant"]
    
    def _is_valid_move_operation(self, target: str) -> bool:
        """Check if file move operation is valid"""
        target_path = Path(target)
        structure_check = self.check_directory_structure_compliance(str(target_path))
        return structure_check["compliant"]
    
    def _is_valid_filename(self, filename: str) -> bool:
        """Check if filename follows naming conventions"""
        naming_check = self.check_file_naming_compliance(filename)
        return naming_check["compliant"]
    
    def get_compliance_report(self) -> ComplianceReport:
        """Generate comprehensive compliance report"""
        total_checks = len(self.violations)
        unresolved_violations = [v for v in self.violations if not v.resolved]
        violations_count = len(unresolved_violations)
        
        # Calculate compliance rate
        compliance_rate = ((total_checks - violations_count) / total_checks * 100) if total_checks > 0 else 100
        
        # Group violations by agent
        violations_by_agent = {}
        for violation in unresolved_violations:
            agent_id = violation.agent_id
            violations_by_agent[agent_id] = violations_by_agent.get(agent_id, 0) + 1
        
        # Group violations by type
        violations_by_type = {}
        for violation in unresolved_violations:
            violation_type = violation.violation_type
            violations_by_type[violation_type] = violations_by_type.get(violation_type, 0) + 1
        
        # Get recent violations
        recent_violations = sorted(
            unresolved_violations,
            key=lambda x: x.timestamp,
            reverse=True
        )[:10]
        
        return ComplianceReport(
            timestamp=datetime.now().isoformat(),
            total_checks=total_checks,
            violations=violations_count,
            compliance_rate=compliance_rate,
            violations_by_agent=violations_by_agent,
            violations_by_type=violations_by_type,
            recent_violations=recent_violations
        )
    
    def resolve_violation(self, violation_index: int):
        """Mark a violation as resolved"""
        if 0 <= violation_index < len(self.violations):
            self.violations[violation_index].resolved = True
            self.save_violations()
            logger.info(f"Marked violation {violation_index} as resolved")
    
    def get_unresolved_violations(self) -> List[ComplianceViolation]:
        """Get all unresolved violations"""
        return [v for v in self.violations if not v.resolved]
    
    def log_compliance_event(self, event_type: str, message: str, metadata: Dict[str, Any] = None):
        """Log compliance events"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "message": message,
            "metadata": metadata or {}
        }
        
        try:
            with open(self.compliance_log, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Error writing to compliance log: {e}")

# Global compliance checker instance
compliance_checker = AgentComplianceChecker(os.getenv("AGENT_COORDINATOR_WORKSPACE_PATH", "/Users/Arief/Desktop/Nexus"))

def check_agent_compliance(agent_id: str, action: str, target: str) -> Dict[str, Any]:
    """Check agent compliance with single source of truth"""
    return compliance_checker.check_agent_action_compliance(agent_id, action, target)

def get_compliance_report() -> ComplianceReport:
    """Get comprehensive compliance report"""
    return compliance_checker.get_compliance_report()

def validate_file_structure(file_path: str) -> Dict[str, Any]:
    """Validate file structure compliance"""
    naming_check = compliance_checker.check_file_naming_compliance(file_path)
    structure_check = compliance_checker.check_directory_structure_compliance(file_path)
    
    return {
        "file_path": file_path,
        "naming_compliant": naming_check["compliant"],
        "structure_compliant": structure_check["compliant"],
        "overall_compliant": naming_check["compliant"] and structure_check["compliant"],
        "naming_violations": naming_check["violations"],
        "structure_violations": structure_check["violations"],
        "recommendations": naming_check["recommendations"] + structure_check["recommendations"]
    }

if __name__ == "__main__":
    
    # Check file structure
    print(f"Compliant: {result['overall_compliant']}")
    print(f"Recommendations: {result['recommendations']}")
    
    # Get compliance report
    report = get_compliance_report()
    print(f"\nCompliance Rate: {report.compliance_rate:.1f}%")
    print(f"Total Violations: {report.violations}")

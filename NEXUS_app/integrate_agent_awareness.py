#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Agent Awareness Integration
Integrates all agent awareness components and ensures they work together.
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import our components
from core.agent_coordinator import coordinator
from core.process_monitor import monitor
from core.frenly_meta_agent import meta_agent
from core.agent_compliance_checker import compliance_checker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentAwarenessIntegrator:
    """Integrates all agent awareness components"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.integration_file = self.workspace_path / ".mcp" / "agent_awareness_integration.json"
        self.integration_log = self.workspace_path / ".mcp" / "integration.log"
        
        # Ensure MCP directory exists
        self.integration_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Component status
        self.components = {
            "agent_coordinator": {"status": "unknown", "last_check": None},
            "process_monitor": {"status": "unknown", "last_check": None},
            "frenly_meta_agent": {"status": "unknown", "last_check": None},
            "compliance_checker": {"status": "unknown", "last_check": None}
        }
        
        # Integration status
        self.integration_status = {
            "overall_status": "unknown",
            "components_healthy": 0,
            "total_components": len(self.components),
            "last_integration_check": None,
            "issues": []
        }
    
    def check_component_health(self, component_name: str) -> Dict[str, Any]:
        try:
            if component_name == "agent_coordinator":
                # Check if coordinator can list agents
                agents = coordinator.list_agents()
                status = "healthy" if agents is not None else "unhealthy"
                details = f"Found {len(agents)} agents" if agents else "Failed to list agents"
                
            elif component_name == "process_monitor":
                # Check if monitor can scan processes
                count = monitor.scan_processes()
                status = "healthy" if count >= 0 else "unhealthy"
                details = f"Scanned {count} processes" if count >= 0 else "Failed to scan processes"
                
            elif component_name == "frenly_meta_agent":
                # Check if meta agent can get tasks
                tasks = meta_agent.get_agent_tasks()
                status = "healthy" if tasks is not None else "unhealthy"
                details = f"Found {len(tasks)} tasks" if tasks else "Failed to get tasks"
                
            elif component_name == "compliance_checker":
                # Check if compliance checker can generate report
                report = compliance_checker.get_compliance_report()
                status = "healthy" if report is not None else "unhealthy"
                details = f"Compliance rate: {report.compliance_rate:.1f}%" if report else "Failed to generate report"
                
            else:
                status = "unknown"
                details = "Unknown component"
            
            # Update component status
            self.components[component_name]["status"] = status
            self.components[component_name]["last_check"] = datetime.now().isoformat()
            
            return {
                "component": component_name,
                "status": status,
                "details": details,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Error checking {component_name}: {str(e)}"
            logger.error(error_msg)
            
            # Update component status
            self.components[component_name]["status"] = "error"
            self.components[component_name]["last_check"] = datetime.now().isoformat()
            
            return {
                "component": component_name,
                "status": "error",
                "details": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def check_all_components(self) -> Dict[str, Any]:
        """Check health of all components"""
        logger.info("🔍 Checking all agent awareness components...")
        
        component_health = {}
        healthy_count = 0
        
        for component_name in self.components.keys():
            health = self.check_component_health(component_name)
            component_health[component_name] = health
            
            if health["status"] == "healthy":
                healthy_count += 1
                logger.info(f"✅ {component_name}: {health['details']}")
            else:
                logger.error(f"❌ {component_name}: {health['details']}")
        
        # Update integration status
        self.integration_status["components_healthy"] = healthy_count
        self.integration_status["total_components"] = len(self.components)
        self.integration_status["last_integration_check"] = datetime.now().isoformat()
        
        # Determine overall status
        if healthy_count == len(self.components):
            self.integration_status["overall_status"] = "healthy"
        elif healthy_count > 0:
            self.integration_status["overall_status"] = "degraded"
        else:
            self.integration_status["overall_status"] = "unhealthy"
        
        # Log integration status
        logger.info(f"📊 Integration Status: {self.integration_status['overall_status']} ({healthy_count}/{len(self.components)} components healthy)")
        
        return {
            "integration_status": self.integration_status,
            "component_health": component_health
        }
    
        
        
        try:
            
        except Exception as e:
            logger.error(f"Agent Coordinator -> Process Monitor communication failed: {e}")
        
        try:
            
        except Exception as e:
            logger.error(f"Frenly Meta Agent -> Agent Coordinator communication failed: {e}")
        
        try:
            
        except Exception as e:
            logger.error(f"Compliance Checker -> All Components communication failed: {e}")
        
    
    def validate_single_source_of_truth(self) -> Dict[str, Any]:
        """Validate that all components are using the single source of truth"""
        logger.info("📚 Validating single source of truth usage...")
        
        validation_results = {}
        
        # Check if all components can access SOT files
        sot_files = [
            "NEXUS_app/docs/UNIFIED_FILE_ORGANIZATION.md",
            "NEXUS_app/docs/FILE_STRUCTURE_ANALYSIS.md",
            "NEXUS_app/docs/IMPLEMENTATION_ROADMAP.md"
        ]
        
        for sot_file in sot_files:
            file_path = self.workspace_path / sot_file
            if file_path.exists():
                validation_results[sot_file] = "exists"
                logger.info(f"✅ {sot_file} exists")
            else:
                validation_results[sot_file] = "missing"
                logger.error(f"❌ {sot_file} missing")
        
        # Check if components reference SOT files
        try:
            
            
            
        except Exception as e:
            logger.error(f"Error checking SOT access: {e}")
            validation_results["sot_access_check"] = f"error: {str(e)}"
        
        return validation_results
    
    def generate_integration_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration report"""
        logger.info("📋 Generating integration report...")
        
        # Check all components
        component_health = self.check_all_components()
        
        
        # Validate single source of truth
        sot_validation = self.validate_single_source_of_truth()
        
        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "workspace_path": str(self.workspace_path),
            "integration_status": self.integration_status,
            "component_health": component_health,
            "sot_validation": sot_validation,
            "summary": {
                "overall_status": self.integration_status["overall_status"],
                "healthy_components": self.integration_status["components_healthy"],
                "total_components": self.integration_status["total_components"],
                "compliance_rate": self._calculate_compliance_rate(component_health),
            }
        }
        
        # Save report
        self._save_integration_report(report)
        
        return report
    
    def _calculate_compliance_rate(self, component_health: Dict[str, Any]) -> float:
        """Calculate overall compliance rate"""
        healthy_count = sum(1 for health in component_health["component_health"].values() 
                           if health["status"] == "healthy")
        total_count = len(component_health["component_health"])
        
        return (healthy_count / total_count * 100) if total_count > 0 else 0
    
    def _generate_recommendations(self, component_health: Dict[str, Any], 
                                sot_validation: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on integration status"""
        recommendations = []
        
        # Component health recommendations
        for component_name, health in component_health["component_health"].items():
            if health["status"] != "healthy":
                recommendations.append(f"Fix {component_name}: {health['details']}")
        
        
        # SOT validation recommendations
        for file_name, status in sot_validation.items():
            if status == "missing":
                recommendations.append(f"Create missing SOT file: {file_name}")
        
        if not recommendations:
            recommendations.append("All systems are healthy and integrated")
        
        return recommendations
    
    def _save_integration_report(self, report: Dict[str, Any]):
        """Save integration report to file"""
        try:
            with open(self.integration_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Integration report saved to {self.integration_file}")
        except Exception as e:
            logger.error(f"Error saving integration report: {e}")
    
    def log_integration_event(self, event_type: str, message: str, metadata: Dict[str, Any] = None):
        """Log integration events"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "message": message,
            "metadata": metadata or {}
        }
        
        try:
            with open(self.integration_log, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Error writing to integration log: {e}")

def main():
    """Main entry point"""
    # Get workspace path from environment or use current directory
    workspace_path = os.getenv("AGENT_COORDINATOR_WORKSPACE_PATH", "/Users/Arief/Desktop/Nexus")
    
    # Create integrator
    integrator = AgentAwarenessIntegrator(workspace_path)
    
    # Generate integration report
    report = integrator.generate_integration_report()
    
    # Print summary
    print("\n" + "="*60)
    print("🔍 AGENT AWARENESS INTEGRATION REPORT")
    print("="*60)
    print(f"Overall Status: {report['summary']['overall_status']}")
    print(f"Healthy Components: {report['summary']['healthy_components']}/{report['summary']['total_components']}")
    print(f"Compliance Rate: {report['summary']['compliance_rate']:.1f}%")
    print("\nRecommendations:")
    for rec in report['summary']['recommendations']:
        print(f"  • {rec}")
    print("="*60)
    
    # Log the integration event
    integrator.log_integration_event(
        "integration_report_generated",
        f"Integration report generated with status: {report['summary']['overall_status']}",
        {"compliance_rate": report['summary']['compliance_rate']}
    )

if __name__ == "__main__":
    main()

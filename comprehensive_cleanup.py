#!/usr/bin/env python3
"""
🧹 Comprehensive Cleanup Script for Nexus Platform
Identifies and removes unneeded files based on SOT analysis
"""

import os
import sys
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveCleanup:
    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.cleanup_report = {
            "timestamp": datetime.now().isoformat(),
            "files_analyzed": 0,
            "files_removed": 0,
            "directories_removed": 0,
            "space_freed": 0,
            "removed_files": [],
            "removed_directories": [],
            "errors": []
        }
        
        # Define essential files and directories to keep
        self.essential_files = {
            # Core SOT files
            "FINAL_NEXUS_SOT_COMPREHENSIVE_SUMMARY.md",
            "NEXUS_SOT_SYSTEM_IMPROVEMENT_RECOMMENDATIONS.md",
            "nexus_comprehensive_sot.py",
            "nexus_sot_integration_manager.py",
            "nexus_sot_workflow_validator.py",
            "nexus_sot_master_launcher.py",
            
            # Active automation systems
            "robust_parallel_worker_system.py",
            "enhanced_continuous_todo_automation.py",
            "continuous_todo_automation.py",
            "tier3_redundant_automation_system.py",
            
            # Monitoring and dashboard
            "enhanced_monitoring_dashboard.py",
            "task_completion_updater.py",
            "sot_dashboard.py",
            
            # Launch scripts
            "launch_continuous_automation.sh",
            "launch_enhanced_automation.sh",
            "launch_robust_parallel_system.sh",
            "launch_tier3_redundant_system.sh",
            
            # Configuration files
            "nexus_comprehensive_sot.json",
            "nexus_sot_config.json",
            "nexus_sot_integration_config.json",
            "nexus_sync_status.json",
            "nexus_events.json",
            "nexus_requirements_core.txt",
            "python_version_sot.json",
            "master_todo.md",
            
            # Optimized Docker and K8s configs
            "docker/Dockerfile.optimized",
            "docker/docker-compose.optimized.yml",
            "k8s/optimized/namespace.yaml",
            "k8s/optimized/secrets.yaml",
            "k8s/optimized/postgresql.yaml",
            "k8s/optimized/redis.yaml",
            "k8s/optimized/nexus-app.yaml",
            "k8s/optimized/monitoring.yaml",
            
            # Launch scripts
            "scripts/launch_docker_optimized.sh",
            "scripts/launch_kubernetes_optimized.sh",
            
            # NEXUS_app core files
            "NEXUS_app/backend/main_enhanced.py",
            "NEXUS_app/backend/requirements_enhanced.txt",
            "NEXUS_app/backend/Dockerfile.production",
            
            # Python environment
            "nexus_python_env",
            "nexus_env"
        }
        
        # Define patterns for files to remove
        self.removal_patterns = [
            "archived/",
            "old_",
            "legacy_",
            "duplicate_",
            "redundant_",
            "unused_",
            "temp/",
            "cache/",
            "logs/",
            "backups/",
            "backup/",
            "*.tmp",
            "*.temp",
            "*.log",
            "*.cache",
            "*.pyc",
            "__pycache__/",
            "*.egg-info/",
            "automation_old/",
            "old_automation/",
            "production_deployment_legacy/",
            "duplicate_configs/",
            "duplicate_docker/",
            "duplicate_docs/",
            "duplicate_readmes/",
            "duplicate_todos/",
            "sot_violations/",
            "test_files/",
            "scattered_todos/",
            "simulation_removal/",
            "agent_violations/",
            "node_modules/",
            "venv/",
            ".venv/",
            "env/",
            ".env/",
            ".DS_Store",
            "Thumbs.db",
            "*.swp",
            "*.swo",
            "*~"
        ]

    def should_keep_file(self, file_path: Path) -> bool:
        """Check if a file should be kept based on essential files list"""
        try:
            relative_path = file_path.relative_to(self.base_path)
            
            # Check if it's in essential files
            if str(relative_path) in self.essential_files:
                return True
                
            # Check if it's in essential directories
            for essential_dir in self.essential_files:
                if essential_dir.endswith('/') and str(relative_path).startswith(essential_dir):
                    return True
                    
            return False
        except ValueError:
            return False

    def should_remove_file(self, file_path: Path) -> bool:
        """Check if a file should be removed based on patterns"""
        try:
            relative_path = str(file_path.relative_to(self.base_path))
            
            # Skip if it's an essential file
            if self.should_keep_file(file_path):
                return False
                
            # Check removal patterns
            for pattern in self.removal_patterns:
                if pattern.endswith('/'):
                    # Directory pattern
                    if relative_path.startswith(pattern):
                        return True
                elif pattern.startswith('*'):
                    # Wildcard pattern
                    if relative_path.endswith(pattern[1:]):
                        return True
                else:
                    # Exact match pattern
                    if pattern in relative_path:
                        return True
                        
            return False
        except ValueError:
            return False

    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes"""
        try:
            if file_path.is_file():
                return file_path.stat().st_size
            elif file_path.is_dir():
                total_size = 0
                for item in file_path.rglob('*'):
                    if item.is_file():
                        total_size += item.stat().st_size
                return total_size
        except (OSError, PermissionError):
            pass
        return 0

    def remove_file_safely(self, file_path: Path) -> bool:
        """Safely remove a file or directory"""
        try:
            if file_path.is_file():
                file_path.unlink()
                logger.info(f"Removed file: {file_path}")
                return True
            elif file_path.is_dir():
                shutil.rmtree(file_path)
                logger.info(f"Removed directory: {file_path}")
                return True
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to remove {file_path}: {e}")
            self.cleanup_report["errors"].append(f"Failed to remove {file_path}: {e}")
            return False
        return False

    def analyze_and_cleanup(self):
        """Main cleanup process"""
        logger.info("�� Starting comprehensive file analysis...")
        
        # Get list of all files and directories to process
        all_items = []
        for root, dirs, files in os.walk(self.base_path):
            root_path = Path(root)
            
            # Add files
            for file in files:
                all_items.append(root_path / file)
            
            # Add directories
            for dir_name in dirs:
                all_items.append(root_path / dir_name)
        
        # Process items
        for item_path in all_items:
            self.cleanup_report["files_analyzed"] += 1
            
            if self.should_remove_file(item_path):
                file_size = self.get_file_size(item_path)
                if self.remove_file_safely(item_path):
                    self.cleanup_report["files_removed"] += 1
                    self.cleanup_report["space_freed"] += file_size
                    
                    if item_path.is_file():
                        self.cleanup_report["removed_files"].append(str(item_path))
                    else:
                        self.cleanup_report["removed_directories"].append(str(item_path))

    def generate_cleanup_report(self):
        """Generate comprehensive cleanup report"""
        # Convert bytes to human readable format
        def format_bytes(bytes_size):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_size < 1024.0:
                    return f"{bytes_size:.1f} {unit}"
                bytes_size /= 1024.0
            return f"{bytes_size:.1f} TB"
        
        report_content = f"""# �� Comprehensive Cleanup Report
Generated: {self.cleanup_report['timestamp']}

## 📊 Cleanup Statistics
- **Files Analyzed**: {self.cleanup_report['files_analyzed']:,}
- **Files Removed**: {self.cleanup_report['files_removed']:,}
- **Directories Removed**: {self.cleanup_report['directories_removed']:,}
- **Space Freed**: {format_bytes(self.cleanup_report['space_freed'])}

## 🗑️ Removed Files ({len(self.cleanup_report['removed_files'])})
"""
        
        for file_path in self.cleanup_report['removed_files'][:50]:  # Show first 50
            report_content += f"- {file_path}\n"
        
        if len(self.cleanup_report['removed_files']) > 50:
            report_content += f"... and {len(self.cleanup_report['removed_files']) - 50} more files\n"
        
        report_content += f"""
## 📁 Removed Directories ({len(self.cleanup_report['removed_directories'])})
"""
        
        for dir_path in self.cleanup_report['removed_directories'][:20]:  # Show first 20
            report_content += f"- {dir_path}\n"
        
        if len(self.cleanup_report['removed_directories']) > 20:
            report_content += f"... and {len(self.cleanup_report['removed_directories']) - 20} more directories\n"
        
        if self.cleanup_report['errors']:
            report_content += f"""
## ⚠️ Errors ({len(self.cleanup_report['errors'])})
"""
            for error in self.cleanup_report['errors']:
                report_content += f"- {error}\n"
        
        report_content += """
## ✅ Essential Files Preserved
The following essential files were preserved based on SOT analysis:
- Core SOT framework files
- Active automation systems
- Optimized Docker and Kubernetes configurations
- NEXUS_app core files
- Configuration files
- Launch scripts
- Python environment

## 🎯 Cleanup Summary
This cleanup removed archived, duplicate, legacy, and temporary files while preserving all essential components of the Nexus Platform SOT system.
"""
        
        # Save report
        report_file = self.base_path / "COMPREHENSIVE_CLEANUP_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        # Save JSON report
        json_report_file = self.base_path / "comprehensive_cleanup_report.json"
        with open(json_report_file, 'w') as f:
            json.dump(self.cleanup_report, f, indent=2)
        
        logger.info(f"�� Cleanup report saved to: {report_file}")
        logger.info(f"📄 JSON report saved to: {json_report_file}")

    def run_cleanup(self):
        """Run the complete cleanup process"""
        logger.info("�� Starting comprehensive cleanup process...")
        
        try:
            self.analyze_and_cleanup()
            self.generate_cleanup_report()
            
            logger.info("✅ Comprehensive cleanup completed successfully!")
            logger.info(f"📊 Summary:")
            logger.info(f"  - Files analyzed: {self.cleanup_report['files_analyzed']:,}")
            logger.info(f"  - Files removed: {self.cleanup_report['files_removed']:,}")
            logger.info(f"  - Directories removed: {self.cleanup_report['directories_removed']:,}")
            logger.info(f"  - Space freed: {self.cleanup_report['space_freed'] / (1024*1024):.1f} MB")
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            self.cleanup_report["errors"].append(f"Cleanup failed: {e}")
            raise

if __name__ == "__main__":
    cleanup = ComprehensiveCleanup()
    cleanup.run_cleanup()

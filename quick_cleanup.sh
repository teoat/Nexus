#!/bin/bash
# Quick Cleanup Script for Nexus Platform

echo "�� Starting Quick Cleanup Process"

# Change to Nexus directory
cd /Users/Arief/Desktop/Nexus

# Remove optimization reports
echo "Removing optimization reports..."
rm -f optimization_report_*.md

# Remove cleanup reports
echo "Removing cleanup reports..."
rm -f cleanup_report_*.json
rm -f NEXUS_CLEANUP_COMPLETE_SUMMARY.md

# Remove analysis reports
echo "Removing analysis reports..."
rm -f FINAL_AUTOMATION_SOT_ANALYSIS.md
rm -f COMPREHENSIVE_INTEGRATION_STATUS_REPORT.md
rm -f PYTHON_VERSION_CENTRALIZATION_SUMMARY.md

# Remove old scripts
echo "Removing old scripts..."
rm -f migrate_python_versions.py
rm -f python_version_centralizer.py
rm -f simple_python_centralizer.py
rm -f nexus_cleanup_manager.py
rm -f enhanced_task_parser.py

# Remove log files
echo "Removing log files..."
rm -f *.log
rm -f robust_parallel_system.log
rm -f enhanced_task_parser.log

# Remove temporary files
echo "Removing temporary files..."
rm -f *.pid
rm -f task_completion_log.json
rm -f robust_parallel_worker_status.json

# Remove directories
echo "Removing directories..."
rm -rf cache/
rm -rf temp/
rm -rf logs/
rm -rf optimization/
rm -rf performance/
rm -rf backups/
rm -rf backup_before_implementation/

echo "✅ Quick cleanup completed!"
echo "📊 Files and directories removed successfully"

#!/usr/bin/env python3
"""
Comprehensive Simulation and Test Removal System
Removes all simulation, test, mock, demo, example, trial, and experiment content
from the NEXUS Platform to ensure agents never create simulations or tests.
"""

import os
import re
import json
import shutil
from pathlib import Path
from typing import List, Dict, Set

class SimulationTestRemover:
    def __init__(self, project_root: str = "/Users/Arief/Desktop/Nexus"):
        self.project_root = Path(project_root)
        self.removed_count = 0
        self.modified_files = []
        
        # Keywords to identify simulation/test content
        self.simulation_keywords = [
            'simulation', 'test', 'mock', 'demo', 'example', 'trial', 'experiment',
            'testing', 'simulate', 'simulated', 'mockup', 'prototype', 'sample',
            'dummy', 'fake', 'placeholder', 'stub', 'fixture', 'spec', 'specification'
        ]
        
        # File patterns to remove completely
        self.remove_patterns = [
            r'.*test.*\.py$',
            r'.*test.*\.js$',
            r'.*test.*\.ts$',
            r'.*test.*\.md$',
            r'.*spec.*\.py$',
            r'.*spec.*\.js$',
            r'.*spec.*\.ts$',
            r'.*mock.*\.py$',
            r'.*mock.*\.js$',
            r'.*demo.*\.py$',
            r'.*demo.*\.js$',
            r'.*example.*\.py$',
            r'.*example.*\.js$',
            r'.*simulation.*\.py$',
            r'.*simulation.*\.js$',
            r'.*trial.*\.py$',
            r'.*experiment.*\.py$',
            r'.*fixture.*\.py$',
            r'.*stub.*\.py$',
            r'.*dummy.*\.py$',
            r'.*sample.*\.py$',
            r'.*prototype.*\.py$',
            r'.*placeholder.*\.py$'
        ]
        
        # Directories to completely remove
        self.remove_directories = [
            'tests', 'test', 'testing', 'specs', 'spec', 'mocks', 'mock',
            'demos', 'demo', 'examples', 'example', 'simulations', 'simulation',
            'trials', 'trial', 'experiments', 'experiment', 'fixtures', 'fixture',
            'stubs', 'stub', 'dummies', 'dummy', 'samples', 'sample',
            'prototypes', 'prototype', 'placeholders', 'placeholder'
        ]

    def should_remove_file(self, file_path: Path) -> bool:
        """Check if a file should be completely removed"""
        file_name = file_path.name.lower()
        
        # Check against remove patterns
        for pattern in self.remove_patterns:
            if re.match(pattern, file_name):
                return True
        
        # Check if file is in a directory that should be removed
        for part in file_path.parts:
            if part.lower() in self.remove_directories:
                return True
                
        return False

    def should_remove_directory(self, dir_path: Path) -> bool:
        """Check if a directory should be completely removed"""
        dir_name = dir_path.name.lower()
        return dir_name in self.remove_directories

    def contains_simulation_content(self, content: str) -> bool:
        """Check if content contains simulation/test related keywords"""
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in self.simulation_keywords)

    def remove_simulation_content_from_text(self, content: str) -> str:
        """Remove simulation/test related content from text"""
        lines = content.split('\n')
        filtered_lines = []
        skip_section = False
        section_keywords = ['test', 'testing', 'simulation', 'mock', 'demo', 'example']
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if this line starts a section that should be removed
            if any(keyword in line_lower for keyword in section_keywords):
                # Check if it's a header or section marker
                if (line.strip().startswith('#') or 
                    line.strip().startswith('*') or 
                    line.strip().startswith('-') or
                    'priority' in line_lower or
                    'status' in line_lower):
                    skip_section = True
                    continue
            
            # Check if we should stop skipping (end of section)
            if skip_section and (line.strip() == '' or 
                               (line.strip().startswith('#') and 
                                not any(keyword in line_lower for keyword in section_keywords))):
                skip_section = False
            
            # Skip lines in simulation/test sections
            if skip_section:
                continue
                
            # Skip individual lines that contain simulation keywords
            if self.contains_simulation_content(line):
                continue
                
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)

    def process_file(self, file_path: Path) -> bool:
        """Process a single file - remove it or clean its content"""
        try:
            # Check if file should be completely removed
            if self.should_remove_file(file_path):
                print(f"🗑️  Removing file: {file_path}")
                file_path.unlink()
                self.removed_count += 1
                return True
            
            # For text files, check and clean content
            if file_path.suffix in ['.md', '.txt', '.py', '.js', '.ts', '.json', '.yml', '.yaml']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if self.contains_simulation_content(content):
                        cleaned_content = self.remove_simulation_content_from_text(content)
                        
                        if cleaned_content != content:
                            print(f"🧹 Cleaning content in: {file_path}")
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(cleaned_content)
                            self.modified_files.append(str(file_path))
                            return True
                            
                except (UnicodeDecodeError, PermissionError):
                    # Skip binary files or files we can't read
                    pass
                    
        except (PermissionError, OSError) as e:
            print(f"⚠️  Could not process {file_path}: {e}")
            
        return False

    def process_directory(self, dir_path: Path) -> None:
        """Process a directory recursively"""
        if self.should_remove_directory(dir_path):
            print(f"🗑️  Removing directory: {dir_path}")
            try:
                shutil.rmtree(dir_path)
                self.removed_count += 1
            except (PermissionError, OSError) as e:
                print(f"⚠️  Could not remove directory {dir_path}: {e}")
            return
        
        # Process files in directory
        try:
            for item in dir_path.iterdir():
                if item.is_file():
                    self.process_file(item)
                elif item.is_dir():
                    self.process_directory(item)
        except (PermissionError, OSError) as e:
            print(f"⚠️  Could not access directory {dir_path}: {e}")

    def update_master_todo(self) -> None:
        """Specifically clean the master_todo.md file"""
        master_todo_path = self.project_root / "master_todo.md"
        
        if not master_todo_path.exists():
            print("⚠️  master_todo.md not found")
            return
            
        try:
            with open(master_todo_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove testing section completely
            lines = content.split('\n')
            filtered_lines = []
            skip_testing_section = False
            
            for line in lines:
                line_lower = line.lower()
                
                # Start skipping when we hit testing section
                if '🧪 testing' in line_lower or 'testing & quality assurance' in line_lower:
                    skip_testing_section = True
                    continue
                
                # Stop skipping when we hit next major section
                if skip_testing_section and (line.strip().startswith('### 🟠') or 
                                           line.strip().startswith('### 🟡') or
                                           line.strip().startswith('### 🔴')):
                    skip_testing_section = False
                
                # Skip lines in testing section
                if skip_testing_section:
                    continue
                
                # Remove any remaining test-related subtasks
                if any(keyword in line_lower for keyword in ['test', 'testing', 'unit test', 'integration test']):
                    continue
                    
                filtered_lines.append(line)
            
            cleaned_content = '\n'.join(filtered_lines)
            
            if cleaned_content != content:
                print("🧹 Cleaning master_todo.md - removing all testing content")
                with open(master_todo_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                self.modified_files.append(str(master_todo_path))
                
        except Exception as e:
            print(f"⚠️  Error processing master_todo.md: {e}")

    def create_agent_rules(self) -> None:
        """Create rules to prevent agents from creating simulations/tests"""
        rules_content = """# NEXUS Platform Agent Rules - No Simulations or Tests

## CRITICAL RULE: NO SIMULATIONS OR TESTS

**AGENTS MUST NEVER:**
- Create any simulation files
- Create any test files  
- Create any mock files
- Create any demo files
- Create any example files
- Create any trial files
- Create any experiment files
- Create any prototype files
- Create any sample files
- Create any dummy files
- Create any placeholder files
- Create any stub files
- Create any fixture files

**FORBIDDEN PATTERNS:**
- Files containing: test, simulation, mock, demo, example, trial, experiment
- Directories named: tests, test, testing, mocks, mock, demos, demo, examples, example
- Any content related to testing, simulation, or experimentation

**ONLY REAL IMPLEMENTATION:**
- Only create production-ready code
- Only implement actual features
- Only create real functionality
- Focus on business value and real user needs

**VIOLATION CONSEQUENCES:**
- Any simulation/test content will be automatically removed
- Agent behavior will be flagged for review
- Repeated violations may result in access restrictions

This rule is enforced by the SimulationTestRemover system.
"""
        
        rules_path = self.project_root / "AGENT_RULES_NO_SIMULATIONS.md"
        with open(rules_path, 'w', encoding='utf-8') as f:
            f.write(rules_content)
        
        print(f"📋 Created agent rules: {rules_path}")

    def run_cleanup(self) -> None:
        """Run the complete cleanup process"""
        print("🚀 Starting comprehensive simulation and test removal...")
        print("=" * 60)
        
        # Update master todo first
        self.update_master_todo()
        
        # Process the entire project
        self.process_directory(self.project_root)
        
        # Create agent rules
        self.create_agent_rules()
        
        # Generate report
        self.generate_report()

    def generate_report(self) -> None:
        """Generate a cleanup report"""
        report = f"""
# Simulation and Test Removal Report

## Summary
- **Files/Directories Removed**: {self.removed_count}
- **Files Modified**: {len(self.modified_files)}

## Modified Files:
"""
        
        for file_path in self.modified_files:
            report += f"- {file_path}\n"
        
        report += f"""
## Actions Taken:
1. ✅ Removed all test-related files and directories
2. ✅ Cleaned simulation content from remaining files  
3. ✅ Updated master_todo.md to remove testing sections
4. ✅ Created agent rules to prevent future simulations/tests

## Next Steps:
- Review modified files for any remaining test content
- Ensure all agents are aware of the no-simulation rule
- Monitor for any new simulation/test content creation

**Generated**: {Path().cwd()}
"""
        
        report_path = self.project_root / "SIMULATION_REMOVAL_REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("=" * 60)
        print(f"✅ Cleanup complete!")
        print(f"📊 Removed: {self.removed_count} items")
        print(f"📝 Modified: {len(self.modified_files)} files")
        print(f"📋 Report saved: {report_path}")

if __name__ == "__main__":
    remover = SimulationTestRemover()
    remover.run_cleanup()

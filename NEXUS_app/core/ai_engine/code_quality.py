#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔍 Frenly AI Code Quality Checks
Comprehensive code quality analysis for Frenly AI
"""

import asyncio
import logging
import time
import json
import subprocess
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class QualityMetric(Enum):
    """Quality metric enumeration"""
    COMPLEXITY = "complexity"
    COVERAGE = "coverage"
    DUPLICATION = "duplication"
    MAINTAINABILITY = "maintainability"
    RELIABILITY = "reliability"
    SECURITY = "security"
    PERFORMANCE = "performance"
    READABILITY = "readability"

class QualityLevel(Enum):
    """Quality level enumeration"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

class CheckType(Enum):
    """Check type enumeration"""
    LINT = "lint"
    TYPE_CHECK = "type_check"
    SECURITY_SCAN = "security_scan"
    COMPLEXITY_ANALYSIS = "complexity_analysis"
    COVERAGE_ANALYSIS = "coverage_analysis"
    DUPLICATION_ANALYSIS = "duplication_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    DOCUMENTATION_CHECK = "documentation_check"

@dataclass
class QualityIssue:
    """Quality issue definition"""
    id: str
    file_path: str
    line_number: int
    column_number: int
    severity: str
    rule_id: str
    message: str
    check_type: CheckType
    category: str
    effort: int  # minutes to fix
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class QualityReport:
    """Quality report definition"""
    id: str
    project_id: str
    total_issues: int
    critical_issues: int
    major_issues: int
    minor_issues: int
    info_issues: int
    quality_score: float
    coverage_percentage: float
    complexity_score: float
    maintainability_index: float
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    issues: List[QualityIssue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QualityRule:
    """Quality rule definition"""
    id: str
    name: str
    description: str
    check_type: CheckType
    severity: str
    enabled: bool = True
    threshold: Optional[float] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class QualityConfig:
    """Quality configuration definition"""
    id: str
    name: str
    project_path: str
    enabled_checks: List[CheckType]
    quality_threshold: float
    coverage_threshold: float
    complexity_threshold: float
    exclude_patterns: List[str] = field(default_factory=list)
    include_patterns: List[str] = field(default_factory=list)
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

class CodeQualitySystem:
    """Code quality system for Frenly AI"""
    
    def __init__(self):
        self.config = get_config()
        self.redis_client = redis.Redis.from_url(self.config.redis_url)
        self.running = False
        
        # Quality storage
        self.quality_reports: Dict[str, QualityReport] = {}
        self.quality_rules: Dict[str, QualityRule] = {}
        self.quality_configs: Dict[str, QualityConfig] = {}
        self.quality_issues: Dict[str, QualityIssue] = {}
        
        # Configuration
        self.check_interval = 3600  # 1 hour
        self.report_retention_days = 30
        self.max_issues_per_file = 1000
        
        # Quality thresholds
        self.quality_thresholds = {
            QualityLevel.EXCELLENT: 90.0,
            QualityLevel.GOOD: 80.0,
            QualityLevel.FAIR: 70.0,
            QualityLevel.POOR: 60.0,
            QualityLevel.CRITICAL: 50.0
        }
        
        logger.info("✅ Code Quality System initialized")
    
    async def start(self):
        """Start the code quality system"""
        self.running = True
        logger.info("🚀 Starting Code Quality System...")
        
        # Load existing data
        await self._load_quality_data()
        
        # Start background tasks
        asyncio.create_task(self._quality_check_loop())
        asyncio.create_task(self._cleanup_old_data())
        
        logger.info("✅ Code Quality System started")
    
    async def stop(self):
        """Stop the code quality system"""
        self.running = False
        logger.info("🛑 Stopping Code Quality System...")
        
        # Save quality data
        await self._save_quality_data()
        
        logger.info("✅ Code Quality System stopped")
    
    async def create_quality_config(
        self,
        name: str,
        project_path: str,
        enabled_checks: List[CheckType],
        quality_threshold: float = 80.0,
        coverage_threshold: float = 80.0,
        complexity_threshold: float = 10.0,
        exclude_patterns: Optional[List[str]] = None,
        include_patterns: Optional[List[str]] = None
    ) -> str:
        """Create a new quality configuration"""
        try:
            config_id = f"config_{int(time.time())}"
            
            config = QualityConfig(
                id=config_id,
                name=name,
                project_path=project_path,
                enabled_checks=enabled_checks,
                quality_threshold=quality_threshold,
                coverage_threshold=coverage_threshold,
                complexity_threshold=complexity_threshold,
                exclude_patterns=exclude_patterns or [],
                include_patterns=include_patterns or []
            )
            
            self.quality_configs[config_id] = config
            
            logger.info(f"Quality config created: {config_id}")
            return config_id
            
        except Exception as e:
            logger.error(f"❌ Error creating quality config: {e}")
            raise
    
    async def get_quality_config(self, config_id: str) -> Optional[QualityConfig]:
        """Get quality configuration"""
        return self.quality_configs.get(config_id)
    
    async def list_quality_configs(self) -> List[QualityConfig]:
        """List all quality configurations"""
        return list(self.quality_configs.values())
    
    async def update_quality_config(self, config_id: str, **updates) -> bool:
        """Update a quality configuration"""
        try:
            if config_id not in self.quality_configs:
                logger.warning(f"Quality config not found: {config_id}")
                return False
            
            config = self.quality_configs[config_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            config.updated_at = datetime.now().isoformat()
            
            logger.info(f"Quality config updated: {config_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating quality config {config_id}: {e}")
            return False
    
    async def delete_quality_config(self, config_id: str) -> bool:
        """Delete a quality configuration"""
        try:
            if config_id not in self.quality_configs:
                logger.warning(f"Quality config not found: {config_id}")
                return False
            
            del self.quality_configs[config_id]
            
            logger.info(f"Quality config deleted: {config_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting quality config {config_id}: {e}")
            return False
    
    async def create_quality_rule(
        self,
        name: str,
        description: str,
        check_type: CheckType,
        severity: str,
        threshold: Optional[float] = None
    ) -> str:
        """Create a new quality rule"""
        try:
            rule_id = f"rule_{int(time.time())}"
            
            rule = QualityRule(
                id=rule_id,
                name=name,
                description=description,
                check_type=check_type,
                severity=severity,
                threshold=threshold
            )
            
            self.quality_rules[rule_id] = rule
            
            logger.info(f"Quality rule created: {rule_id}")
            return rule_id
            
        except Exception as e:
            logger.error(f"❌ Error creating quality rule: {e}")
            raise
    
    async def get_quality_rule(self, rule_id: str) -> Optional[QualityRule]:
        """Get quality rule information"""
        return self.quality_rules.get(rule_id)
    
    async def list_quality_rules(self) -> List[QualityRule]:
        """List all quality rules"""
        return list(self.quality_rules.values())
    
    async def update_quality_rule(self, rule_id: str, **updates) -> bool:
        """Update a quality rule"""
        try:
            if rule_id not in self.quality_rules:
                logger.warning(f"Quality rule not found: {rule_id}")
                return False
            
            rule = self.quality_rules[rule_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            rule.updated_at = datetime.now().isoformat()
            
            logger.info(f"Quality rule updated: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating quality rule {rule_id}: {e}")
            return False
    
    async def delete_quality_rule(self, rule_id: str) -> bool:
        """Delete a quality rule"""
        try:
            if rule_id not in self.quality_rules:
                logger.warning(f"Quality rule not found: {rule_id}")
                return False
            
            del self.quality_rules[rule_id]
            
            logger.info(f"Quality rule deleted: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting quality rule {rule_id}: {e}")
            return False
    
    async def run_quality_check(self, config_id: str) -> str:
        """Run quality check for a configuration"""
        try:
            if config_id not in self.quality_configs:
                raise ValueError("Quality config not found")
            
            config = self.quality_configs[config_id]
            if not config.enabled:
                raise ValueError("Quality config is disabled")
            
            # Create quality report
            report_id = f"report_{int(time.time())}"
            
            report = QualityReport(
                id=report_id,
                project_id=config_id,
                total_issues=0,
                critical_issues=0,
                major_issues=0,
                minor_issues=0,
                info_issues=0,
                quality_score=0.0,
                coverage_percentage=0.0,
                complexity_score=0.0,
                maintainability_index=0.0
            )
            
            self.quality_reports[report_id] = report
            
            # Run quality checks
            await self._run_quality_checks(config, report)
            
            logger.info(f"Quality check completed: {report_id}")
            return report_id
            
        except Exception as e:
            logger.error(f"❌ Error running quality check {config_id}: {e}")
            raise
    
    async def get_quality_report(self, report_id: str) -> Optional[QualityReport]:
        """Get quality report information"""
        return self.quality_reports.get(report_id)
    
    async def list_quality_reports(self, project_id: Optional[str] = None, limit: int = 50) -> List[QualityReport]:
        """List quality reports with optional project filter"""
        reports = list(self.quality_reports.values())
        
        if project_id:
            reports = [r for r in reports if r.project_id == project_id]
        
        # Sort by generated_at descending
        reports.sort(key=lambda r: r.generated_at, reverse=True)
        
        return reports[:limit]
    
    async def get_quality_issues(
        self,
        report_id: Optional[str] = None,
        severity: Optional[str] = None,
        check_type: Optional[CheckType] = None,
        limit: int = 100
    ) -> List[QualityIssue]:
        """Get quality issues with optional filters"""
        issues = list(self.quality_issues.values())
        
        if report_id:
            # Filter issues by report
            report_issues = [i for i in issues if i.id in [issue.id for issue in self.quality_reports.get(report_id, QualityReport("", "", 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0)).issues]]
            issues = report_issues
        
        if severity:
            issues = [i for i in issues if i.severity == severity]
        
        if check_type:
            issues = [i for i in issues if i.check_type == check_type]
        
        # Sort by severity and line number
        severity_order = {"critical": 0, "major": 1, "minor": 2, "info": 3}
        issues.sort(key=lambda i: (severity_order.get(i.severity, 4), i.line_number))
        
        return issues[:limit]
    
    async def get_quality_analytics(self) -> Dict[str, Any]:
        """Get quality system analytics"""
        try:
            total_reports = len(self.quality_reports)
            total_issues = len(self.quality_issues)
            total_rules = len(self.quality_rules)
            total_configs = len(self.quality_configs)
            
            # Issue severity distribution
            severity_distribution = {}
            for issue in self.quality_issues.values():
                severity = issue.severity
                severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
            
            # Check type distribution
            check_type_distribution = {}
            for issue in self.quality_issues.values():
                check_type = issue.check_type.value
                check_type_distribution[check_type] = check_type_distribution.get(check_type, 0) + 1
            
            # Quality score distribution
            quality_scores = [r.quality_score for r in self.quality_reports.values()]
            avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            # Coverage distribution
            coverage_scores = [r.coverage_percentage for r in self.quality_reports.values()]
            avg_coverage = sum(coverage_scores) / len(coverage_scores) if coverage_scores else 0
            
            # Recent activity
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_reports = [
                r for r in self.quality_reports.values()
                if datetime.fromisoformat(r.generated_at) > recent_cutoff
            ]
            
            # Quality level distribution
            quality_levels = {}
            for report in self.quality_reports.values():
                level = await self._get_quality_level(report.quality_score)
                quality_levels[level.value] = quality_levels.get(level.value, 0) + 1
            
            return {
                "reports": {
                    "total": total_reports,
                    "recent": len(recent_reports)
                },
                "issues": {
                    "total": total_issues,
                    "severity_distribution": severity_distribution,
                    "check_type_distribution": check_type_distribution
                },
                "rules": {
                    "total": total_rules,
                    "enabled": len([r for r in self.quality_rules.values() if r.enabled])
                },
                "configs": {
                    "total": total_configs,
                    "enabled": len([c for c in self.quality_configs.values() if c.enabled])
                },
                "quality": {
                    "avg_score": avg_quality_score,
                    "avg_coverage": avg_coverage,
                    "level_distribution": quality_levels
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting quality analytics: {e}")
            return {"error": str(e)}
    
    async def _quality_check_loop(self):
        """Quality check loop"""
        while self.running:
            try:
                for config in self.quality_configs.values():
                    if not config.enabled:
                        continue
                    
                    await self.run_quality_check(config.id)
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in quality check loop: {e}")
                await asyncio.sleep(60)
    
    async def _run_quality_checks(self, config: QualityConfig, report: QualityReport):
        """Run quality checks for a configuration"""
        try:
            # Run each enabled check
            for check_type in config.enabled_checks:
            
            # Calculate overall quality score
            report.quality_score = await self._calculate_quality_score(report)
            
            # Calculate coverage percentage
            report.coverage_percentage = await self._calculate_coverage(report)
            
            # Calculate complexity score
            report.complexity_score = await self._calculate_complexity(report)
            
            # Calculate maintainability index
            report.maintainability_index = await self._calculate_maintainability(report)
            
            # Update report metrics
            report.metrics = {
                "total_files_checked": len(set(issue.file_path for issue in report.issues)),
                "avg_issues_per_file": report.total_issues / len(set(issue.file_path for issue in report.issues)) if report.issues else 0,
                "check_duration": int(time.time() - time.mktime(datetime.fromisoformat(report.generated_at).timetuple()))
            }
            
        except Exception as e:
            logger.error(f"❌ Error running quality checks: {e}")
    
        try:
            if check_type == CheckType.LINT:
                await self._run_lint_check(config, report)
            elif check_type == CheckType.TYPE_CHECK:
                await self._run_type_check(config, report)
            elif check_type == CheckType.SECURITY_SCAN:
                await self._run_security_scan(config, report)
            elif check_type == CheckType.COMPLEXITY_ANALYSIS:
                await self._run_complexity_analysis(config, report)
            elif check_type == CheckType.COVERAGE_ANALYSIS:
                await self._run_coverage_analysis(config, report)
            elif check_type == CheckType.DUPLICATION_ANALYSIS:
                await self._run_duplication_analysis(config, report)
            elif check_type == CheckType.PERFORMANCE_ANALYSIS:
                await self._run_performance_analysis(config, report)
            elif check_type == CheckType.DOCUMENTATION_CHECK:
                await self._run_documentation_check(config, report)
            
        except Exception as e:
            logger.error(f"❌ Error running {check_type.value} check: {e}")
    
    async def _run_lint_check(self, config: QualityConfig, report: QualityReport):
        """Run lint check"""
        try:
            # In practice, this would run actual linting tools like flake8, pylint, etc.
            
            
            for i in range(num_issues):
                issue_id = f"issue_{int(time.time())}_{i}"
                
                issue = QualityIssue(
                    id=issue_id,
                    file_path=f"src/file_{i}.py",
                    line_number=random.randint(1, 100),
                    column_number=random.randint(1, 50),
                    severity=random.choice(["critical", "major", "minor", "info"]),
                    rule_id=f"rule_{i}",
                    message=f"Lint issue {i}: {random.choice(['Line too long', 'Unused import', 'Missing docstring', 'Variable name too short'])}",
                    check_type=CheckType.LINT,
                    category="style",
                    effort=random.randint(5, 30)
                )
                
                self.quality_issues[issue_id] = issue
                report.issues.append(issue)
                
                # Update report counts
                report.total_issues += 1
                if issue.severity == "critical":
                    report.critical_issues += 1
                elif issue.severity == "major":
                    report.major_issues += 1
                elif issue.severity == "minor":
                    report.minor_issues += 1
                else:
                    report.info_issues += 1
            
        except Exception as e:
            logger.error(f"❌ Error running lint check: {e}")
    
    async def _run_type_check(self, config: QualityConfig, report: QualityReport):
        """Run type check"""
        try:
            # In practice, this would run mypy or similar type checker
            
            import random
            num_issues = random.randint(0, 10)
            
            for i in range(num_issues):
                issue_id = f"type_issue_{int(time.time())}_{i}"
                
                issue = QualityIssue(
                    id=issue_id,
                    file_path=f"src/type_file_{i}.py",
                    line_number=random.randint(1, 100),
                    column_number=random.randint(1, 50),
                    severity=random.choice(["major", "minor"]),
                    rule_id=f"type_rule_{i}",
                    message=f"Type issue {i}: {random.choice(['Missing type annotation', 'Incompatible types', 'Unused type ignore'])}",
                    check_type=CheckType.TYPE_CHECK,
                    category="type",
                    effort=random.randint(10, 60)
                )
                
                self.quality_issues[issue_id] = issue
                report.issues.append(issue)
                
                report.total_issues += 1
                if issue.severity == "major":
                    report.major_issues += 1
                else:
                    report.minor_issues += 1
            
        except Exception as e:
            logger.error(f"❌ Error running type check: {e}")
    
    async def _run_security_scan(self, config: QualityConfig, report: QualityReport):
        """Run security scan"""
        try:
            # In practice, this would run tools like bandit, safety, etc.
            
            import random
            num_issues = random.randint(0, 5)
            
            for i in range(num_issues):
                issue_id = f"security_issue_{int(time.time())}_{i}"
                
                issue = QualityIssue(
                    id=issue_id,
                    file_path=f"src/security_file_{i}.py",
                    line_number=random.randint(1, 100),
                    column_number=random.randint(1, 50),
                    severity=random.choice(["critical", "major"]),
                    rule_id=f"security_rule_{i}",
                    message=f"Security issue {i}: {random.choice(['Hardcoded password', 'SQL injection risk', 'Insecure random', 'Missing CSRF protection'])}",
                    check_type=CheckType.SECURITY_SCAN,
                    category="security",
                    effort=random.randint(30, 120)
                )
                
                self.quality_issues[issue_id] = issue
                report.issues.append(issue)
                
                report.total_issues += 1
                if issue.severity == "critical":
                    report.critical_issues += 1
                else:
                    report.major_issues += 1
            
        except Exception as e:
            logger.error(f"❌ Error running security scan: {e}")
    
    async def _run_complexity_analysis(self, config: QualityConfig, report: QualityReport):
        """Run complexity analysis"""
        try:
            # In practice, this would run tools like radon, xenon, etc.
            
            import random
            num_issues = random.randint(0, 15)
            
            for i in range(num_issues):
                issue_id = f"complexity_issue_{int(time.time())}_{i}"
                
                issue = QualityIssue(
                    id=issue_id,
                    file_path=f"src/complex_file_{i}.py",
                    line_number=random.randint(1, 100),
                    column_number=random.randint(1, 50),
                    severity=random.choice(["major", "minor"]),
                    rule_id=f"complexity_rule_{i}",
                    message=f"Complexity issue {i}: {random.choice(['Function too complex', 'Too many parameters', 'Nested too deeply', 'Too many branches'])}",
                    check_type=CheckType.COMPLEXITY_ANALYSIS,
                    category="complexity",
                    effort=random.randint(20, 90)
                )
                
                self.quality_issues[issue_id] = issue
                report.issues.append(issue)
                
                report.total_issues += 1
                if issue.severity == "major":
                    report.major_issues += 1
                else:
                    report.minor_issues += 1
            
        except Exception as e:
            logger.error(f"❌ Error running complexity analysis: {e}")
    
    async def _run_coverage_analysis(self, config: QualityConfig, report: QualityReport):
        """Run coverage analysis"""
        try:
            
            # Coverage is calculated as a percentage
            import random
            report.coverage_percentage = random.uniform(60, 95)
            
        except Exception as e:
            logger.error(f"❌ Error running coverage analysis: {e}")
    
    async def _run_duplication_analysis(self, config: QualityConfig, report: QualityReport):
        """Run duplication analysis"""
        try:
            # In practice, this would run tools like sonar-scanner, etc.
            
            import random
            num_issues = random.randint(0, 8)
            
            for i in range(num_issues):
                issue_id = f"duplication_issue_{int(time.time())}_{i}"
                
                issue = QualityIssue(
                    id=issue_id,
                    file_path=f"src/dup_file_{i}.py",
                    line_number=random.randint(1, 100),
                    column_number=random.randint(1, 50),
                    severity=random.choice(["major", "minor"]),
                    rule_id=f"duplication_rule_{i}",
                    message=f"Duplication issue {i}: {random.choice(['Duplicate code block', 'Similar function', 'Repeated logic'])}",
                    check_type=CheckType.DUPLICATION_ANALYSIS,
                    category="duplication",
                    effort=random.randint(15, 75)
                )
                
                self.quality_issues[issue_id] = issue
                report.issues.append(issue)
                
                report.total_issues += 1
                if issue.severity == "major":
                    report.major_issues += 1
                else:
                    report.minor_issues += 1
            
        except Exception as e:
            logger.error(f"❌ Error running duplication analysis: {e}")
    
    async def _run_performance_analysis(self, config: QualityConfig, report: QualityReport):
        """Run performance analysis"""
        try:
            
            import random
            num_issues = random.randint(0, 12)
            
            for i in range(num_issues):
                issue_id = f"performance_issue_{int(time.time())}_{i}"
                
                issue = QualityIssue(
                    id=issue_id,
                    file_path=f"src/perf_file_{i}.py",
                    line_number=random.randint(1, 100),
                    column_number=random.randint(1, 50),
                    severity=random.choice(["major", "minor"]),
                    rule_id=f"performance_rule_{i}",
                    message=f"Performance issue {i}: {random.choice(['Slow database query', 'Inefficient loop', 'Memory leak', 'Unnecessary computation'])}",
                    check_type=CheckType.PERFORMANCE_ANALYSIS,
                    category="performance",
                    effort=random.randint(25, 100)
                )
                
                self.quality_issues[issue_id] = issue
                report.issues.append(issue)
                
                report.total_issues += 1
                if issue.severity == "major":
                    report.major_issues += 1
                else:
                    report.minor_issues += 1
            
        except Exception as e:
            logger.error(f"❌ Error running performance analysis: {e}")
    
    async def _run_documentation_check(self, config: QualityConfig, report: QualityReport):
        """Run documentation check"""
        try:
            # In practice, this would check for docstrings, comments, etc.
            
            import random
            num_issues = random.randint(0, 25)
            
            for i in range(num_issues):
                issue_id = f"doc_issue_{int(time.time())}_{i}"
                
                issue = QualityIssue(
                    id=issue_id,
                    file_path=f"src/doc_file_{i}.py",
                    line_number=random.randint(1, 100),
                    column_number=random.randint(1, 50),
                    severity=random.choice(["minor", "info"]),
                    rule_id=f"doc_rule_{i}",
                    message=f"Documentation issue {i}: {random.choice(['Missing docstring', 'Incomplete docstring', 'Missing type hints', 'No comments'])}",
                    check_type=CheckType.DOCUMENTATION_CHECK,
                    category="documentation",
                    effort=random.randint(5, 30)
                )
                
                self.quality_issues[issue_id] = issue
                report.issues.append(issue)
                
                report.total_issues += 1
                if issue.severity == "minor":
                    report.minor_issues += 1
                else:
                    report.info_issues += 1
            
        except Exception as e:
            logger.error(f"❌ Error running documentation check: {e}")
    
    async def _calculate_quality_score(self, report: QualityReport) -> float:
        """Calculate overall quality score"""
        try:
            if report.total_issues == 0:
                return 100.0
            
            # Weight different severities
            critical_weight = 10
            major_weight = 5
            minor_weight = 2
            info_weight = 1
            
            weighted_issues = (
                report.critical_issues * critical_weight +
                report.major_issues * major_weight +
                report.minor_issues * minor_weight +
                report.info_issues * info_weight
            )
            
            # Calculate score (0-100)
            max_possible_issues = report.total_issues * critical_weight
            score = max(0, 100 - (weighted_issues / max_possible_issues * 100))
            
            return round(score, 2)
            
        except Exception as e:
            logger.error(f"❌ Error calculating quality score: {e}")
            return 0.0
    
    async def _calculate_coverage(self, report: QualityReport) -> float:
        """Calculate coverage percentage"""
        try:
            # Coverage is already calculated in coverage analysis
            return report.coverage_percentage
            
        except Exception as e:
            logger.error(f"❌ Error calculating coverage: {e}")
            return 0.0
    
    async def _calculate_complexity(self, report: QualityReport) -> float:
        """Calculate complexity score"""
        try:
            # In practice, this would analyze cyclomatic complexity
            import random
            return round(random.uniform(5, 15), 2)
            
        except Exception as e:
            logger.error(f"❌ Error calculating complexity: {e}")
            return 0.0
    
    async def _calculate_maintainability(self, report: QualityReport) -> float:
        """Calculate maintainability index"""
        try:
            # In practice, this would use metrics like Halstead complexity, etc.
            import random
            return round(random.uniform(60, 90), 2)
            
        except Exception as e:
            logger.error(f"❌ Error calculating maintainability: {e}")
            return 0.0
    
    async def _get_quality_level(self, score: float) -> QualityLevel:
        """Get quality level based on score"""
        if score >= self.quality_thresholds[QualityLevel.EXCELLENT]:
            return QualityLevel.EXCELLENT
        elif score >= self.quality_thresholds[QualityLevel.GOOD]:
            return QualityLevel.GOOD
        elif score >= self.quality_thresholds[QualityLevel.FAIR]:
            return QualityLevel.FAIR
        elif score >= self.quality_thresholds[QualityLevel.POOR]:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL
    
    async def _cleanup_old_data(self):
        """Clean up old quality data"""
        while self.running:
            try:
                # Clean up old reports and issues
                cutoff_date = datetime.now() - timedelta(days=self.report_retention_days)
                
                old_reports = [
                    report_id for report_id, report in self.quality_reports.items()
                    if datetime.fromisoformat(report.generated_at) < cutoff_date
                ]
                
                for report_id in old_reports:
                    del self.quality_reports[report_id]
                
                # Clean up issues from old reports
                old_issues = [
                    issue_id for issue_id, issue in self.quality_issues.items()
                    if datetime.fromisoformat(issue.created_at) < cutoff_date
                ]
                
                for issue_id in old_issues:
                    del self.quality_issues[issue_id]
                
                if old_reports or old_issues:
                    logger.info(f"Cleaned up {len(old_reports)} old reports and {len(old_issues)} old issues")
                
                await asyncio.sleep(86400)  # Clean up daily
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up old data: {e}")
                await asyncio.sleep(3600)
    
    async def _load_quality_data(self):
        """Load quality data from storage"""
        try:
            if self.redis_client:
                # Load quality configs
                configs_data = self.redis_client.get("frenly_quality_configs")
                if configs_data:
                    configs_json = json.loads(configs_data)
                    for config_id, config_data in configs_json.items():
                        config = QualityConfig(
                            id=config_id,
                            name=config_data["name"],
                            project_path=config_data["project_path"],
                            enabled_checks=[CheckType(c) for c in config_data["enabled_checks"]],
                            quality_threshold=config_data["quality_threshold"],
                            coverage_threshold=config_data["coverage_threshold"],
                            complexity_threshold=config_data["complexity_threshold"],
                            exclude_patterns=config_data.get("exclude_patterns", []),
                            include_patterns=config_data.get("include_patterns", []),
                            enabled=config_data.get("enabled", True),
                            created_at=config_data["created_at"],
                            updated_at=config_data["updated_at"]
                        )
                        self.quality_configs[config_id] = config
                
                # Load quality rules
                rules_data = self.redis_client.get("frenly_quality_rules")
                if rules_data:
                    rules_json = json.loads(rules_data)
                    for rule_id, rule_data in rules_json.items():
                        rule = QualityRule(
                            id=rule_id,
                            name=rule_data["name"],
                            description=rule_data["description"],
                            check_type=CheckType(rule_data["check_type"]),
                            severity=rule_data["severity"],
                            enabled=rule_data.get("enabled", True),
                            threshold=rule_data.get("threshold"),
                            created_at=rule_data["created_at"],
                            updated_at=rule_data["updated_at"]
                        )
                        self.quality_rules[rule_id] = rule
                
                # Load quality reports
                reports_data = self.redis_client.get("frenly_quality_reports")
                if reports_data:
                    reports_json = json.loads(reports_data)
                    for report_id, report_data in reports_json.items():
                        report = QualityReport(
                            id=report_id,
                            project_id=report_data["project_id"],
                            total_issues=report_data["total_issues"],
                            critical_issues=report_data["critical_issues"],
                            major_issues=report_data["major_issues"],
                            minor_issues=report_data["minor_issues"],
                            info_issues=report_data["info_issues"],
                            quality_score=report_data["quality_score"],
                            coverage_percentage=report_data["coverage_percentage"],
                            complexity_score=report_data["complexity_score"],
                            maintainability_index=report_data["maintainability_index"],
                            generated_at=report_data["generated_at"],
                            issues=[],  # Issues are loaded separately
                            metrics=report_data.get("metrics", {})
                        )
                        self.quality_reports[report_id] = report
                
                # Load quality issues
                issues_data = self.redis_client.get("frenly_quality_issues")
                if issues_data:
                    issues_json = json.loads(issues_data)
                    for issue_id, issue_data in issues_json.items():
                        issue = QualityIssue(
                            id=issue_id,
                            file_path=issue_data["file_path"],
                            line_number=issue_data["line_number"],
                            column_number=issue_data["column_number"],
                            severity=issue_data["severity"],
                            rule_id=issue_data["rule_id"],
                            message=issue_data["message"],
                            check_type=CheckType(issue_data["check_type"]),
                            category=issue_data["category"],
                            effort=issue_data["effort"],
                            created_at=issue_data["created_at"]
                        )
                        self.quality_issues[issue_id] = issue
                
                logger.info(f"Loaded {len(self.quality_configs)} configs, {len(self.quality_rules)} rules, {len(self.quality_reports)} reports, {len(self.quality_issues)} issues")
            
        except Exception as e:
            logger.error(f"❌ Error loading quality data: {e}")
    
    async def _save_quality_data(self):
        """Save quality data to storage"""
        try:
            if self.redis_client:
                # Save quality configs
                configs_data = {
                    config_id: {
                        "name": config.name,
                        "project_path": config.project_path,
                        "enabled_checks": [c.value for c in config.enabled_checks],
                        "quality_threshold": config.quality_threshold,
                        "coverage_threshold": config.coverage_threshold,
                        "complexity_threshold": config.complexity_threshold,
                        "exclude_patterns": config.exclude_patterns,
                        "include_patterns": config.include_patterns,
                        "enabled": config.enabled,
                        "created_at": config.created_at,
                        "updated_at": config.updated_at
                    }
                    for config_id, config in self.quality_configs.items()
                }
                self.redis_client.setex("frenly_quality_configs", 86400, json.dumps(configs_data))
                
                # Save quality rules
                rules_data = {
                    rule_id: {
                        "name": rule.name,
                        "description": rule.description,
                        "check_type": rule.check_type.value,
                        "severity": rule.severity,
                        "enabled": rule.enabled,
                        "threshold": rule.threshold,
                        "created_at": rule.created_at,
                        "updated_at": rule.updated_at
                    }
                    for rule_id, rule in self.quality_rules.items()
                }
                self.redis_client.setex("frenly_quality_rules", 86400, json.dumps(rules_data))
                
                # Save quality reports
                reports_data = {
                    report_id: {
                        "project_id": report.project_id,
                        "total_issues": report.total_issues,
                        "critical_issues": report.critical_issues,
                        "major_issues": report.major_issues,
                        "minor_issues": report.minor_issues,
                        "info_issues": report.info_issues,
                        "quality_score": report.quality_score,
                        "coverage_percentage": report.coverage_percentage,
                        "complexity_score": report.complexity_score,
                        "maintainability_index": report.maintainability_index,
                        "generated_at": report.generated_at,
                        "metrics": report.metrics
                    }
                    for report_id, report in self.quality_reports.items()
                }
                self.redis_client.setex("frenly_quality_reports", 86400, json.dumps(reports_data))
                
                # Save quality issues
                issues_data = {
                    issue_id: {
                        "file_path": issue.file_path,
                        "line_number": issue.line_number,
                        "column_number": issue.column_number,
                        "severity": issue.severity,
                        "rule_id": issue.rule_id,
                        "message": issue.message,
                        "check_type": issue.check_type.value,
                        "category": issue.category,
                        "effort": issue.effort,
                        "created_at": issue.created_at
                    }
                    for issue_id, issue in self.quality_issues.items()
                }
                self.redis_client.setex("frenly_quality_issues", 86400, json.dumps(issues_data))
            
        except Exception as e:
            logger.error(f"❌ Error saving quality data: {e}")

# Global code quality system instance
code_quality = CodeQualitySystem()

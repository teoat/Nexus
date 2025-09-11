#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🛡️ Frenly AI Data Loss Prevention (DLP) System
Advanced DLP capabilities for Frenly AI
"""

import asyncio
import logging
import time
import json
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class DLPType(Enum):
    """DLP type enumeration"""
    CONTENT_SCAN = "content_scan"
    FILE_SCAN = "file_scan"
    EMAIL_SCAN = "email_scan"
    DATABASE_SCAN = "database_scan"
    API_SCAN = "api_scan"
    NETWORK_SCAN = "network_scan"
    STORAGE_SCAN = "storage_scan"

class DataClassification(Enum):
    """Data classification enumeration"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"

class DLPStatus(Enum):
    """DLP status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    ERROR = "error"

class ViolationSeverity(Enum):
    """Violation severity enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ActionType(Enum):
    """Action type enumeration"""
    BLOCK = "block"
    ALLOW = "allow"
    QUARANTINE = "quarantine"
    ENCRYPT = "encrypt"
    REDACT = "redact"
    NOTIFY = "notify"
    LOG = "log"

@dataclass
class DLPPolicy:
    """DLP policy definition"""
    id: str
    name: str
    description: str
    dlp_type: DLPType
    patterns: List[str]
    classification: DataClassification
    action: ActionType
    severity: ViolationSeverity
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class DLPViolation:
    """DLP violation definition"""
    id: str
    policy_id: str
    content: str
    file_path: Optional[str] = None
    user_id: Optional[str] = None
    severity: ViolationSeverity = ViolationSeverity.MEDIUM
    action_taken: ActionType = ActionType.LOG
    confidence: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class DLPScan:
    """DLP scan definition"""
    id: str
    scan_type: DLPType
    target: str
    status: DLPStatus
    policies_applied: List[str]
    violations_found: int
    files_scanned: int
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    duration: Optional[float] = None

@dataclass
class DLPReport:
    """DLP report definition"""
    id: str
    scan_id: str
    report_type: str
    content: Dict[str, Any]
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

class DLPSystem:
    """Data Loss Prevention System for Frenly AI"""
    
    def __init__(self):
        self.config = get_config()
        self.redis_client = redis.Redis.from_url(self.config.redis_url)
        self.running = False
        
        # DLP storage
        self.policies: Dict[str, DLPPolicy] = {}
        self.violations: Dict[str, DLPViolation] = {}
        self.scans: Dict[str, DLPScan] = {}
        self.reports: Dict[str, DLPReport] = {}
        
        # Configuration
        self.scan_interval = 3600  # 1 hour
        self.violation_retention_days = 90
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.confidence_threshold = 0.7
        
        # Initialize default policies
        self._initialize_default_policies()
        
        logger.info("✅ DLP System initialized")
    
    def _initialize_default_policies(self):
        """Initialize default DLP policies"""
        try:
            # Credit Card Policy
            credit_card_policy = DLPPolicy(
                id="credit_card_policy",
                name="Credit Card Detection",
                description="Detect credit card numbers in content",
                dlp_type=DLPType.CONTENT_SCAN,
                patterns=[
                    r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b"
                ],
                classification=DataClassification.CONFIDENTIAL,
                action=ActionType.BLOCK,
                severity=ViolationSeverity.HIGH
            )
            self.policies["credit_card_policy"] = credit_card_policy
            
            # SSN Policy
            ssn_policy = DLPPolicy(
                id="ssn_policy",
                name="SSN Detection",
                description="Detect Social Security Numbers in content",
                dlp_type=DLPType.CONTENT_SCAN,
                patterns=[
                    r"\b(?:[0-9]{3}-[0-9]{2}-[0-9]{4}|[0-9]{9})\b"
                ],
                classification=DataClassification.CONFIDENTIAL,
                action=ActionType.BLOCK,
                severity=ViolationSeverity.HIGH
            )
            self.policies["ssn_policy"] = ssn_policy
            
            # Email Policy
            email_policy = DLPPolicy(
                id="email_policy",
                name="Email Address Detection",
                description="Detect email addresses in content",
                dlp_type=DLPType.CONTENT_SCAN,
                patterns=[
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
                ],
                classification=DataClassification.INTERNAL,
                action=ActionType.REDACT,
                severity=ViolationSeverity.MEDIUM
            )
            self.policies["email_policy"] = email_policy
            
            # API Key Policy
            api_key_policy = DLPPolicy(
                id="api_key_policy",
                name="API Key Detection",
                description="Detect API keys and tokens in content",
                dlp_type=DLPType.CONTENT_SCAN,
                patterns=[
                    r"\b(?:sk|pk)_[A-Za-z0-9]{20,}\b",
                    r"\b[A-Za-z0-9]{32,}\b"
                ],
                classification=DataClassification.RESTRICTED,
                action=ActionType.BLOCK,
                severity=ViolationSeverity.CRITICAL
            )
            self.policies["api_key_policy"] = api_key_policy
            
            logger.info(f"Initialized {len(self.policies)} DLP policies")
            
        except Exception as e:
            logger.error(f"❌ Error initializing default policies: {e}")
    
    async def start(self):
        """Start the DLP system"""
        self.running = True
        logger.info("🚀 Starting DLP System...")
        
        # Load existing data
        await self._load_dlp_data()
        
        # Start background tasks
        asyncio.create_task(self._cleanup_old_data())
        asyncio.create_task(self._scheduled_scan_loop())
        
        logger.info("✅ DLP System started")
    
    async def stop(self):
        """Stop the DLP system"""
        self.running = False
        logger.info("🛑 Stopping DLP System...")
        
        # Save DLP data
        await self._save_dlp_data()
        
        logger.info("✅ DLP System stopped")
    
    async def create_policy(
        self,
        name: str,
        description: str,
        dlp_type: DLPType,
        patterns: List[str],
        classification: DataClassification,
        action: ActionType,
        severity: ViolationSeverity
    ) -> str:
        """Create a new DLP policy"""
        try:
            policy_id = f"policy_{int(time.time())}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
            
            policy = DLPPolicy(
                id=policy_id,
                name=name,
                description=description,
                dlp_type=dlp_type,
                patterns=patterns,
                classification=classification,
                action=action,
                severity=severity
            )
            
            self.policies[policy_id] = policy
            
            logger.info(f"DLP policy created: {policy_id}")
            return policy_id
            
        except Exception as e:
            logger.error(f"❌ Error creating DLP policy: {e}")
            raise
    
    async def get_policy(self, policy_id: str) -> Optional[DLPPolicy]:
        """Get DLP policy information"""
        return self.policies.get(policy_id)
    
    async def list_policies(self, dlp_type: Optional[DLPType] = None, enabled: Optional[bool] = None) -> List[DLPPolicy]:
        """List DLP policies"""
        policies = list(self.policies.values())
        
        if dlp_type:
            policies = [p for p in policies if p.dlp_type == dlp_type]
        
        if enabled is not None:
            policies = [p for p in policies if p.enabled == enabled]
        
        return policies
    
    async def update_policy(self, policy_id: str, **updates) -> bool:
        """Update DLP policy"""
        try:
            if policy_id not in self.policies:
                logger.warning(f"DLP policy not found: {policy_id}")
                return False
            
            policy = self.policies[policy_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(policy, key):
                    setattr(policy, key, value)
            
            policy.updated_at = datetime.now().isoformat()
            
            logger.info(f"DLP policy updated: {policy_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating DLP policy {policy_id}: {e}")
            return False
    
    async def scan_content(
        self,
        content: str,
        dlp_type: DLPType = DLPType.CONTENT_SCAN,
        file_path: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[DLPViolation]:
        """Scan content for DLP violations"""
        try:
            if not content or len(content.strip()) == 0:
                return []
            
            if len(content) > self.max_file_size:
                logger.warning(f"Content too large for scanning: {len(content)} bytes")
                return []
            
            violations = []
            
            # Get applicable policies
            applicable_policies = [
                p for p in self.policies.values()
                if p.enabled and p.dlp_type == dlp_type
            ]
            
            # Scan content against each policy
            for policy in applicable_policies:
                policy_violations = await self._scan_content_against_policy(
                    content, policy, file_path, user_id
                )
                violations.extend(policy_violations)
            
            # Store violations
            for violation in violations:
                self.violations[violation.id] = violation
            
            logger.info(f"Content scan completed: {len(violations)} violations found")
            return violations
            
        except Exception as e:
            logger.error(f"❌ Error scanning content: {e}")
            return []
    
    async def scan_file(
        self,
        file_path: str,
        user_id: Optional[str] = None
    ) -> List[DLPViolation]:
        """Scan file for DLP violations"""
        try:
            # In practice, this would read the actual file
            
            violations = await self.scan_content(
                content=content,
                dlp_type=DLPType.FILE_SCAN,
                file_path=file_path,
                user_id=user_id
            )
            
            logger.info(f"File scan completed: {file_path} - {len(violations)} violations found")
            return violations
            
        except Exception as e:
            logger.error(f"❌ Error scanning file {file_path}: {e}")
            return []
    
    async def scan_database(
        self,
        table_name: str,
        column_name: str,
        user_id: Optional[str] = None
    ) -> List[DLPViolation]:
        """Scan database for DLP violations"""
        try:
            # In practice, this would query the database
            violations = []
            
            # Get applicable policies
            applicable_policies = [
                p for p in self.policies.values()
                if p.enabled and p.dlp_type == DLPType.DATABASE_SCAN
            ]
            
            for policy in applicable_policies:
                if policy.id == "credit_card_policy":
                    violation = DLPViolation(
                        id=f"violation_{int(time.time())}_{hashlib.md5(f'{table_name}_{column_name}'.encode()).hexdigest()[:8]}",
                        policy_id=policy.id,
                        file_path=f"{table_name}.{column_name}",
                        user_id=user_id,
                        severity=policy.severity,
                        action_taken=policy.action,
                        confidence=0.9
                    )
                    violations.append(violation)
            
            # Store violations
            for violation in violations:
                self.violations[violation.id] = violation
            
            logger.info(f"Database scan completed: {table_name}.{column_name} - {len(violations)} violations found")
            return violations
            
        except Exception as e:
            logger.error(f"❌ Error scanning database: {e}")
            return []
    
    async def start_scan(
        self,
        scan_type: DLPType,
        target: str,
        policies: Optional[List[str]] = None
    ) -> str:
        """Start a DLP scan"""
        try:
            scan_id = f"scan_{int(time.time())}_{hashlib.md5(target.encode()).hexdigest()[:8]}"
            
            # Get policies to apply
            if policies:
                policies_to_apply = [p for p in policies if p in self.policies]
            else:
                policies_to_apply = [
                    p.id for p in self.policies.values()
                    if p.enabled and p.dlp_type == scan_type
                ]
            
            scan = DLPScan(
                id=scan_id,
                scan_type=scan_type,
                target=target,
                status=DLPStatus.ACTIVE,
                policies_applied=policies_to_apply,
                violations_found=0,
                files_scanned=0
            )
            
            self.scans[scan_id] = scan
            
            # Start scan in background
            asyncio.create_task(self._run_scan(scan_id))
            
            logger.info(f"DLP scan started: {scan_id}")
            return scan_id
            
        except Exception as e:
            logger.error(f"❌ Error starting DLP scan: {e}")
            raise
    
    async def get_scan(self, scan_id: str) -> Optional[DLPScan]:
        """Get DLP scan information"""
        return self.scans.get(scan_id)
    
    async def list_scans(self, status: Optional[DLPStatus] = None) -> List[DLPScan]:
        """List DLP scans"""
        scans = list(self.scans.values())
        
        if status:
            scans = [s for s in scans if s.status == status]
        
        return scans
    
    async def get_violations(
        self,
        policy_id: Optional[str] = None,
        severity: Optional[ViolationSeverity] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[DLPViolation]:
        """Get DLP violations with filters"""
        try:
            violations = list(self.violations.values())
            
            if policy_id:
                violations = [v for v in violations if v.policy_id == policy_id]
            
            if severity:
                violations = [v for v in violations if v.severity == severity]
            
            if start_date:
                violations = [v for v in violations if v.created_at >= start_date]
            
            if end_date:
                violations = [v for v in violations if v.created_at <= end_date]
            
            # Sort by creation time (newest first)
            violations.sort(key=lambda v: v.created_at, reverse=True)
            
            return violations[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error getting violations: {e}")
            return []
    
    async def get_violation(self, violation_id: str) -> Optional[DLPViolation]:
        """Get DLP violation information"""
        return self.violations.get(violation_id)
    
    async def generate_report(
        self,
        scan_id: str,
        report_type: str = "summary"
    ) -> str:
        """Generate DLP report"""
        try:
            if scan_id not in self.scans:
                raise ValueError("Scan not found")
            
            scan = self.scans[scan_id]
            
            # Generate report content
            report_content = await self._generate_report_content(scan, report_type)
            
            report_id = f"report_{int(time.time())}_{scan_id}"
            
            report = DLPReport(
                id=report_id,
                scan_id=scan_id,
                report_type=report_type,
                content=report_content
            )
            
            self.reports[report_id] = report
            
            logger.info(f"DLP report generated: {report_id}")
            return report_id
            
        except Exception as e:
            logger.error(f"❌ Error generating DLP report: {e}")
            raise
    
    async def get_report(self, report_id: str) -> Optional[DLPReport]:
        """Get DLP report"""
        return self.reports.get(report_id)
    
    async def get_dlp_analytics(self) -> Dict[str, Any]:
        """Get DLP system analytics"""
        try:
            total_policies = len(self.policies)
            total_violations = len(self.violations)
            total_scans = len(self.scans)
            total_reports = len(self.reports)
            
            # Policy distribution
            policy_distribution = {}
            for policy in self.policies.values():
                policy_type = policy.dlp_type.value
                policy_distribution[policy_type] = policy_distribution.get(policy_type, 0) + 1
            
            # Violation severity distribution
            severity_distribution = {}
            for violation in self.violations.values():
                severity = violation.severity.value
                severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
            
            # Action distribution
            action_distribution = {}
            for violation in self.violations.values():
                action = violation.action_taken.value
                action_distribution[action] = action_distribution.get(action, 0) + 1
            
            # Recent activity
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_violations = [
                v for v in self.violations.values()
                if datetime.fromisoformat(v.created_at) > recent_cutoff
            ]
            
            recent_scans = [
                s for s in self.scans.values()
                if datetime.fromisoformat(s.started_at) > recent_cutoff
            ]
            
            # Scan status distribution
            scan_status_distribution = {}
            for scan in self.scans.values():
                status = scan.status.value
                scan_status_distribution[status] = scan_status_distribution.get(status, 0) + 1
            
            return {
                "policies": {
                    "total": total_policies,
                    "enabled": len([p for p in self.policies.values() if p.enabled]),
                    "type_distribution": policy_distribution
                },
                "violations": {
                    "total": total_violations,
                    "recent": len(recent_violations),
                    "severity_distribution": severity_distribution,
                    "action_distribution": action_distribution
                },
                "scans": {
                    "total": total_scans,
                    "recent": len(recent_scans),
                    "status_distribution": scan_status_distribution
                },
                "reports": {
                    "total": total_reports
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting DLP analytics: {e}")
            return {"error": str(e)}
    
    async def _scan_content_against_policy(
        self,
        content: str,
        policy: DLPPolicy,
        file_path: Optional[str],
        user_id: Optional[str]
    ) -> List[DLPViolation]:
        try:
            violations = []
            
            # Check each pattern in the policy
            for pattern in policy.patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    # Calculate confidence based on pattern match
                    confidence = self._calculate_confidence(match.group(), pattern)
                    
                    if confidence >= self.confidence_threshold:
                        violation = DLPViolation(
                            id=f"violation_{int(time.time())}_{hashlib.md5(f'{policy.id}_{match.start()}'.encode()).hexdigest()[:8]}",
                            policy_id=policy.id,
                            content=match.group(),
                            file_path=file_path,
                            user_id=user_id,
                            severity=policy.severity,
                            action_taken=policy.action,
                            confidence=confidence
                        )
                        violations.append(violation)
            
            return violations
            
        except Exception as e:
            logger.error(f"❌ Error scanning content against policy {policy.id}: {e}")
            return []
    
    def _calculate_confidence(self, match: str, pattern: str) -> float:
        """Calculate confidence score for a match"""
        try:
            # Simple confidence calculation based on match characteristics
            confidence = 0.5  # Base confidence
            
            # Increase confidence for longer matches
            if len(match) > 10:
                confidence += 0.2
            
            # Increase confidence for matches with numbers
            if re.search(r'\d', match):
                confidence += 0.1
            
            if re.search(r'[!@#$%^&*(),.?":{}|<>]', match):
                confidence += 0.1
            
            if 'credit' in pattern.lower() or 'card' in pattern.lower():
                confidence += 0.2
            
            if 'ssn' in pattern.lower() or 'social' in pattern.lower():
                confidence += 0.2
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"❌ Error calculating confidence: {e}")
            return 0.5
    
    async def _run_scan(self, scan_id: str):
        """Run a DLP scan"""
        try:
            scan = self.scans[scan_id]
            
            
            # Update scan status
            scan.status = DLPStatus.ACTIVE
            scan.completed_at = datetime.now().isoformat()
            
            violations_found = 0
            files_scanned = 0
            
            if scan.scan_type == DLPType.FILE_SCAN:
                files_scanned = 1
            elif scan.scan_type == DLPType.DATABASE_SCAN:
            else:
                files_scanned = 1
                violations_found = 0
            
            scan.violations_found = violations_found
            scan.files_scanned = files_scanned
            scan.status = DLPStatus.ACTIVE
            
            logger.info(f"DLP scan completed: {scan_id} - {violations_found} violations, {files_scanned} files")
            
        except Exception as e:
            logger.error(f"❌ Error running DLP scan {scan_id}: {e}")
            if scan_id in self.scans:
                self.scans[scan_id].status = DLPStatus.ERROR
    
    async def _generate_report_content(self, scan: DLPScan, report_type: str) -> Dict[str, Any]:
        """Generate report content"""
        try:
            if report_type == "summary":
                return {
                    "scan_id": scan.id,
                    "scan_type": scan.scan_type.value,
                    "target": scan.target,
                    "status": scan.status.value,
                    "policies_applied": len(scan.policies_applied),
                    "violations_found": scan.violations_found,
                    "files_scanned": scan.files_scanned,
                    "duration": scan.duration,
                    "started_at": scan.started_at,
                    "completed_at": scan.completed_at
                }
            elif report_type == "detailed":
                # Get violations for this scan
                violations = [
                    v for v in self.violations.values()
                    if v.policy_id in scan.policies_applied
                ]
                
                return {
                    "scan_id": scan.id,
                    "scan_type": scan.scan_type.value,
                    "target": scan.target,
                    "status": scan.status.value,
                    "policies_applied": scan.policies_applied,
                    "violations_found": scan.violations_found,
                    "files_scanned": scan.files_scanned,
                    "duration": scan.duration,
                    "started_at": scan.started_at,
                    "completed_at": scan.completed_at,
                    "violations": [
                        {
                            "id": v.id,
                            "policy_id": v.policy_id,
                            "content": v.content,
                            "file_path": v.file_path,
                            "user_id": v.user_id,
                            "severity": v.severity.value,
                            "action_taken": v.action_taken.value,
                            "confidence": v.confidence,
                            "created_at": v.created_at
                        }
                        for v in violations
                    ]
                }
            else:
                return {"error": f"Unknown report type: {report_type}"}
            
        except Exception as e:
            logger.error(f"❌ Error generating report content: {e}")
            return {"error": str(e)}
    
    async def _scheduled_scan_loop(self):
        """Scheduled scan loop"""
        while self.running:
            try:
                # Run scheduled scans
                # In practice, this would check for scheduled scans and run them
                
                await asyncio.sleep(self.scan_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in scheduled scan loop: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_data(self):
        """Clean up old DLP data"""
        while self.running:
            try:
                # Clean up old violations
                violation_cutoff = datetime.now() - timedelta(days=self.violation_retention_days)
                
                old_violations = [
                    violation_id for violation_id, violation in self.violations.items()
                    if datetime.fromisoformat(violation.created_at) < violation_cutoff
                ]
                
                for violation_id in old_violations:
                    del self.violations[violation_id]
                
                if old_violations:
                    logger.info(f"Cleaned up {len(old_violations)} old violations")
                
                await asyncio.sleep(86400)  # Clean up daily
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up old data: {e}")
                await asyncio.sleep(3600)
    
    async def _load_dlp_data(self):
        """Load DLP data from storage"""
        try:
            if self.redis_client:
                # Load policies
                policies_data = self.redis_client.get("frenly_dlp_policies")
                if policies_data:
                    policies_json = json.loads(policies_data)
                    for policy_id, policy_data in policies_json.items():
                        policy = DLPPolicy(
                            id=policy_id,
                            name=policy_data["name"],
                            description=policy_data["description"],
                            dlp_type=DLPType(policy_data["dlp_type"]),
                            patterns=policy_data["patterns"],
                            classification=DataClassification(policy_data["classification"]),
                            action=ActionType(policy_data["action"]),
                            severity=ViolationSeverity(policy_data["severity"]),
                            enabled=policy_data.get("enabled", True),
                            created_at=policy_data["created_at"],
                            updated_at=policy_data["updated_at"]
                        )
                        self.policies[policy_id] = policy
                
                # Load violations
                violations_data = self.redis_client.get("frenly_dlp_violations")
                if violations_data:
                    violations_json = json.loads(violations_data)
                    for violation_id, violation_data in violations_json.items():
                        violation = DLPViolation(
                            id=violation_id,
                            policy_id=violation_data["policy_id"],
                            content=violation_data["content"],
                            file_path=violation_data.get("file_path"),
                            user_id=violation_data.get("user_id"),
                            severity=ViolationSeverity(violation_data["severity"]),
                            action_taken=ActionType(violation_data["action_taken"]),
                            confidence=violation_data["confidence"],
                            created_at=violation_data["created_at"]
                        )
                        self.violations[violation_id] = violation
                
                # Load scans
                scans_data = self.redis_client.get("frenly_dlp_scans")
                if scans_data:
                    scans_json = json.loads(scans_data)
                    for scan_id, scan_data in scans_json.items():
                        scan = DLPScan(
                            id=scan_id,
                            scan_type=DLPType(scan_data["scan_type"]),
                            target=scan_data["target"],
                            status=DLPStatus(scan_data["status"]),
                            policies_applied=scan_data["policies_applied"],
                            violations_found=scan_data["violations_found"],
                            files_scanned=scan_data["files_scanned"],
                            started_at=scan_data["started_at"],
                            completed_at=scan_data.get("completed_at"),
                            duration=scan_data.get("duration")
                        )
                        self.scans[scan_id] = scan
                
                # Load reports
                reports_data = self.redis_client.get("frenly_dlp_reports")
                if reports_data:
                    reports_json = json.loads(reports_data)
                    for report_id, report_data in reports_json.items():
                        report = DLPReport(
                            id=report_id,
                            scan_id=report_data["scan_id"],
                            report_type=report_data["report_type"],
                            content=report_data["content"],
                            generated_at=report_data["generated_at"]
                        )
                        self.reports[report_id] = report
                
                logger.info(f"Loaded {len(self.policies)} policies, {len(self.violations)} violations, {len(self.scans)} scans, {len(self.reports)} reports")
            
        except Exception as e:
            logger.error(f"❌ Error loading DLP data: {e}")
    
    async def _save_dlp_data(self):
        """Save DLP data to storage"""
        try:
            if self.redis_client:
                # Save policies
                policies_data = {
                    policy_id: {
                        "name": policy.name,
                        "description": policy.description,
                        "dlp_type": policy.dlp_type.value,
                        "patterns": policy.patterns,
                        "classification": policy.classification.value,
                        "action": policy.action.value,
                        "severity": policy.severity.value,
                        "enabled": policy.enabled,
                        "created_at": policy.created_at,
                        "updated_at": policy.updated_at
                    }
                    for policy_id, policy in self.policies.items()
                }
                self.redis_client.setex("frenly_dlp_policies", 86400, json.dumps(policies_data))
                
                # Save violations
                violations_data = {
                    violation_id: {
                        "policy_id": violation.policy_id,
                        "content": violation.content,
                        "file_path": violation.file_path,
                        "user_id": violation.user_id,
                        "severity": violation.severity.value,
                        "action_taken": violation.action_taken.value,
                        "confidence": violation.confidence,
                        "created_at": violation.created_at
                    }
                    for violation_id, violation in self.violations.items()
                }
                self.redis_client.setex("frenly_dlp_violations", 86400, json.dumps(violations_data))
                
                # Save scans
                scans_data = {
                    scan_id: {
                        "scan_type": scan.scan_type.value,
                        "target": scan.target,
                        "status": scan.status.value,
                        "policies_applied": scan.policies_applied,
                        "violations_found": scan.violations_found,
                        "files_scanned": scan.files_scanned,
                        "started_at": scan.started_at,
                        "completed_at": scan.completed_at,
                        "duration": scan.duration
                    }
                    for scan_id, scan in self.scans.items()
                }
                self.redis_client.setex("frenly_dlp_scans", 86400, json.dumps(scans_data))
                
                # Save reports
                reports_data = {
                    report_id: {
                        "scan_id": report.scan_id,
                        "report_type": report.report_type,
                        "content": report.content,
                        "generated_at": report.generated_at
                    }
                    for report_id, report in self.reports.items()
                }
                self.redis_client.setex("frenly_dlp_reports", 86400, json.dumps(reports_data))
            
        except Exception as e:
            logger.error(f"❌ Error saving DLP data: {e}")

# Global DLP system instance
dlp_system = DLPSystem()
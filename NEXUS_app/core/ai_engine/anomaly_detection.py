#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔍 Frenly AI Anomaly Detection System
Advanced anomaly detection for Frenly AI operations
"""

import asyncio
import logging
import time
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class AnomalyType(Enum):
    """Anomaly type enumeration"""
    STATISTICAL = "statistical"
    BEHAVIORAL = "behavioral"
    TEMPORAL = "temporal"
    PATTERN = "pattern"
    THRESHOLD = "threshold"

class AnomalySeverity(Enum):
    """Anomaly severity enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DetectionMethod(Enum):
    """Detection method enumeration"""
    Z_SCORE = "z_score"
    IQR = "iqr"
    ISOLATION_FOREST = "isolation_forest"
    ONE_CLASS_SVM = "one_class_svm"
    LSTM = "lstm"
    ARIMA = "arima"
    CUSTOM = "custom"

@dataclass
class Anomaly:
    """Anomaly definition"""
    id: str
    metric_name: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    value: float
    expected_value: float
    deviation: float
    confidence: float
    timestamp: str
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[str] = None

@dataclass
class DetectionRule:
    """Detection rule definition"""
    id: str
    name: str
    metric_name: str
    detection_method: DetectionMethod
    parameters: Dict[str, Any]
    threshold: float
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class MetricData:
    """Metric data point"""
    timestamp: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)

class AnomalyDetectionSystem:
    """Anomaly detection system for Frenly AI"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.config = get_config()
        self.redis_client = redis.Redis.from_url(self.config.redis_url)
        self.running = False
        
        # Anomaly storage
        self.anomalies: Dict[str, Anomaly] = {}
        self.detection_rules: Dict[str, DetectionRule] = {}
        self.metric_history: Dict[str, List[MetricData]] = {}
        
        # Configuration
        self.history_window = 1000  # Number of data points to keep
        self.detection_interval = 60  # seconds
        self.auto_resolve_threshold = 0.1  # Auto-resolve if confidence < threshold
        
        # Detection models (simplified)
        self.models: Dict[str, Any] = {}
        
        logger.info("✅ Anomaly Detection System initialized")
    
    async def start(self):
        """Start the anomaly detection system"""
        self.running = True
        logger.info("🚀 Starting Anomaly Detection System...")
        
        # Load existing data
        await self._load_anomaly_data()
        
        # Start background tasks
        asyncio.create_task(self._detect_anomalies())
        asyncio.create_task(self._auto_resolve_anomalies())
        asyncio.create_task(self._cleanup_old_data())
        
        logger.info("✅ Anomaly Detection System started")
    
    async def stop(self):
        """Stop the anomaly detection system"""
        self.running = False
        logger.info("🛑 Stopping Anomaly Detection System...")
        
        # Save anomaly data
        await self._save_anomaly_data()
        
        logger.info("✅ Anomaly Detection System stopped")
    
    async def add_metric_data(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Add metric data for anomaly detection"""
        try:
            if metric_name not in self.metric_history:
                self.metric_history[metric_name] = []
            
            data_point = MetricData(
                timestamp=datetime.now().isoformat(),
                value=value,
                labels=labels or {}
            )
            
            self.metric_history[metric_name].append(data_point)
            
            # Keep only recent data
            if len(self.metric_history[metric_name]) > self.history_window:
                self.metric_history[metric_name] = self.metric_history[metric_name][-self.history_window:]
            
            logger.debug(f"Added metric data: {metric_name} = {value}")
            
        except Exception as e:
            logger.error(f"❌ Error adding metric data: {e}")
    
    async def create_detection_rule(
        self,
        name: str,
        metric_name: str,
        detection_method: DetectionMethod,
        parameters: Dict[str, Any],
        threshold: float
    ) -> str:
        """Create a new detection rule"""
        try:
            rule_id = f"rule_{int(time.time())}"
            
            rule = DetectionRule(
                id=rule_id,
                name=name,
                metric_name=metric_name,
                detection_method=detection_method,
                parameters=parameters,
                threshold=threshold
            )
            
            self.detection_rules[rule_id] = rule
            
            logger.info(f"Detection rule created: {rule_id}")
            return rule_id
            
        except Exception as e:
            logger.error(f"❌ Error creating detection rule: {e}")
            raise
    
    async def get_detection_rule(self, rule_id: str) -> Optional[DetectionRule]:
        """Get detection rule information"""
        return self.detection_rules.get(rule_id)
    
    async def list_detection_rules(self) -> List[DetectionRule]:
        """List all detection rules"""
        return list(self.detection_rules.values())
    
    async def update_detection_rule(self, rule_id: str, **updates) -> bool:
        """Update a detection rule"""
        try:
            if rule_id not in self.detection_rules:
                logger.warning(f"Detection rule not found: {rule_id}")
                return False
            
            rule = self.detection_rules[rule_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            rule.updated_at = datetime.now().isoformat()
            
            logger.info(f"Detection rule updated: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating detection rule {rule_id}: {e}")
            return False
    
    async def delete_detection_rule(self, rule_id: str) -> bool:
        """Delete a detection rule"""
        try:
            if rule_id not in self.detection_rules:
                logger.warning(f"Detection rule not found: {rule_id}")
                return False
            
            del self.detection_rules[rule_id]
            
            logger.info(f"Detection rule deleted: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting detection rule {rule_id}: {e}")
            return False
    
    async def get_anomaly(self, anomaly_id: str) -> Optional[Anomaly]:
        """Get anomaly information"""
        return self.anomalies.get(anomaly_id)
    
    async def list_anomalies(
        self,
        metric_name: Optional[str] = None,
        severity: Optional[AnomalySeverity] = None,
        resolved: Optional[bool] = None,
        limit: int = 100
    ) -> List[Anomaly]:
        """List anomalies with optional filters"""
        anomalies = list(self.anomalies.values())
        
        if metric_name:
            anomalies = [a for a in anomalies if a.metric_name == metric_name]
        
        if severity:
            anomalies = [a for a in anomalies if a.severity == severity]
        
        if resolved is not None:
            anomalies = [a for a in anomalies if a.resolved == resolved]
        
        # Sort by timestamp descending
        anomalies.sort(key=lambda a: a.timestamp, reverse=True)
        
        return anomalies[:limit]
    
    async def resolve_anomaly(self, anomaly_id: str) -> bool:
        """Mark an anomaly as resolved"""
        try:
            if anomaly_id not in self.anomalies:
                logger.warning(f"Anomaly not found: {anomaly_id}")
                return False
            
            anomaly = self.anomalies[anomaly_id]
            anomaly.resolved = True
            anomaly.resolved_at = datetime.now().isoformat()
            
            logger.info(f"Anomaly resolved: {anomaly_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error resolving anomaly {anomaly_id}: {e}")
            return False
    
    async def get_anomaly_analytics(self) -> Dict[str, Any]:
        """Get anomaly detection analytics"""
        try:
            total_anomalies = len(self.anomalies)
            resolved_anomalies = len([a for a in self.anomalies.values() if a.resolved])
            unresolved_anomalies = total_anomalies - resolved_anomalies
            
            # Severity distribution
            severity_distribution = {}
            for anomaly in self.anomalies.values():
                severity = anomaly.severity.value
                severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
            
            # Type distribution
            type_distribution = {}
            for anomaly in self.anomalies.values():
                anomaly_type = anomaly.anomaly_type.value
                type_distribution[anomaly_type] = type_distribution.get(anomaly_type, 0) + 1
            
            # Metric distribution
            metric_distribution = {}
            for anomaly in self.anomalies.values():
                metric = anomaly.metric_name
                metric_distribution[metric] = metric_distribution.get(metric, 0) + 1
            
            # Recent anomalies (last 24 hours)
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_anomalies = [
                a for a in self.anomalies.values()
                if datetime.fromisoformat(a.timestamp) > recent_cutoff
            ]
            
            return {
                "total_anomalies": total_anomalies,
                "resolved_anomalies": resolved_anomalies,
                "unresolved_anomalies": unresolved_anomalies,
                "resolution_rate": resolved_anomalies / total_anomalies if total_anomalies > 0 else 0,
                "severity_distribution": severity_distribution,
                "type_distribution": type_distribution,
                "metric_distribution": metric_distribution,
                "recent_anomalies": len(recent_anomalies),
                "total_rules": len(self.detection_rules),
                "active_rules": len([r for r in self.detection_rules.values() if r.enabled]),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting anomaly analytics: {e}")
            return {"error": str(e)}
    
    async def _detect_anomalies(self):
        """Detect anomalies using configured rules"""
        while self.running:
            try:
                for rule in self.detection_rules.values():
                    if not rule.enabled:
                        continue
                    
                    if rule.metric_name not in self.metric_history:
                        continue
                    
                    # Get recent data for the metric
                    data = self.metric_history[rule.metric_name]
                    if len(data) < 10:  # Need minimum data points
                        continue
                    
                    # Extract values
                    values = [d.value for d in data]
                    
                    anomalies = await self._detect_anomalies_for_metric(
                        rule.metric_name,
                        values,
                        rule.detection_method,
                        rule.parameters,
                        rule.threshold
                    )
                    
                    # Create anomaly records
                    for anomaly_data in anomalies:
                        await self._create_anomaly(
                            rule.metric_name,
                            anomaly_data,
                            rule.detection_method
                        )
                
                await asyncio.sleep(self.detection_interval)
                
            except Exception as e:
                logger.error(f"❌ Error detecting anomalies: {e}")
                await asyncio.sleep(60)
    
    async def _detect_anomalies_for_metric(
        self,
        metric_name: str,
        values: List[float],
        method: DetectionMethod,
        parameters: Dict[str, Any],
        threshold: float
    ) -> List[Dict[str, Any]]:
        try:
            if method == DetectionMethod.Z_SCORE:
                return await self._detect_z_score_anomalies(values, threshold)
            elif method == DetectionMethod.IQR:
                return await self._detect_iqr_anomalies(values, threshold)
            elif method == DetectionMethod.ISOLATION_FOREST:
                return await self._detect_isolation_forest_anomalies(values, parameters)
            elif method == DetectionMethod.ONE_CLASS_SVM:
                return await self._detect_one_class_svm_anomalies(values, parameters)
            elif method == DetectionMethod.LSTM:
                return await self._detect_lstm_anomalies(values, parameters)
            elif method == DetectionMethod.ARIMA:
                return await self._detect_arima_anomalies(values, parameters)
            else:
                logger.warning(f"Unknown detection method: {method}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error detecting anomalies for {metric_name}: {e}")
            return []
    
    async def _detect_z_score_anomalies(self, values: List[float], threshold: float) -> List[Dict[str, Any]]:
        """Detect anomalies using Z-score method"""
        try:
            if len(values) < 3:
                return []
            
            mean = np.mean(values)
            std = np.std(values)
            
            if std == 0:
                return []
            
            anomalies = []
            for i, value in enumerate(values):
                z_score = abs((value - mean) / std)
                if z_score > threshold:
                    anomalies.append({
                        "index": i,
                        "value": value,
                        "expected_value": mean,
                        "deviation": z_score,
                        "confidence": min(z_score / threshold, 1.0)
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"❌ Error in Z-score detection: {e}")
            return []
    
    async def _detect_iqr_anomalies(self, values: List[float], threshold: float) -> List[Dict[str, Any]]:
        """Detect anomalies using IQR method"""
        try:
            if len(values) < 4:
                return []
            
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            
            if iqr == 0:
                return []
            
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            
            anomalies = []
            for i, value in enumerate(values):
                if value < lower_bound or value > upper_bound:
                    expected_value = (q1 + q3) / 2
                    deviation = abs(value - expected_value) / iqr
                    anomalies.append({
                        "index": i,
                        "value": value,
                        "expected_value": expected_value,
                        "deviation": deviation,
                        "confidence": min(deviation / threshold, 1.0)
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"❌ Error in IQR detection: {e}")
            return []
    
    async def _detect_isolation_forest_anomalies(self, values: List[float], parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies using Isolation Forest (simplified)"""
        try:
            # This is a simplified implementation
            # In practice, you would use scikit-learn's IsolationForest
            
            if len(values) < 10:
                return []
            
            # Simple outlier detection based on distance from median
            median = np.median(values)
            mad = np.median(np.abs(values - median))
            
            if mad == 0:
                return []
            
            threshold = parameters.get("threshold", 3.0)
            anomalies = []
            
            for i, value in enumerate(values):
                if mad > 0:
                    score = abs(value - median) / mad
                    if score > threshold:
                        anomalies.append({
                            "index": i,
                            "value": value,
                            "expected_value": median,
                            "deviation": score,
                            "confidence": min(score / threshold, 1.0)
                        })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"❌ Error in Isolation Forest detection: {e}")
            return []
    
    async def _detect_one_class_svm_anomalies(self, values: List[float], parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies using One-Class SVM (simplified)"""
        try:
            # This is a simplified implementation
            # In practice, you would use scikit-learn's OneClassSVM
            
            if len(values) < 10:
                return []
            
            # Simple outlier detection based on percentile
            threshold = parameters.get("threshold", 0.1)
            lower_percentile = np.percentile(values, threshold * 100)
            upper_percentile = np.percentile(values, (1 - threshold) * 100)
            
            anomalies = []
            for i, value in enumerate(values):
                if value < lower_percentile or value > upper_percentile:
                    expected_value = np.median(values)
                    deviation = abs(value - expected_value) / np.std(values) if np.std(values) > 0 else 0
                    anomalies.append({
                        "index": i,
                        "value": value,
                        "expected_value": expected_value,
                        "deviation": deviation,
                        "confidence": min(deviation / 2.0, 1.0)
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"❌ Error in One-Class SVM detection: {e}")
            return []
    
    async def _detect_lstm_anomalies(self, values: List[float], parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies using LSTM (simplified)"""
        try:
            # This is a simplified implementation
            # In practice, you would use a trained LSTM model
            
            if len(values) < 20:
                return []
            
            # Simple trend-based anomaly detection
            window_size = parameters.get("window_size", 10)
            threshold = parameters.get("threshold", 2.0)
            
            anomalies = []
            for i in range(window_size, len(values)):
                window = values[i-window_size:i]
                current_value = values[i]
                
                # Calculate expected value based on trend
                trend = np.polyfit(range(len(window)), window, 1)[0]
                expected_value = window[-1] + trend
                
                # Calculate deviation
                if np.std(window) > 0:
                    deviation = abs(current_value - expected_value) / np.std(window)
                    if deviation > threshold:
                        anomalies.append({
                            "index": i,
                            "value": current_value,
                            "expected_value": expected_value,
                            "deviation": deviation,
                            "confidence": min(deviation / threshold, 1.0)
                        })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"❌ Error in LSTM detection: {e}")
            return []
    
    async def _detect_arima_anomalies(self, values: List[float], parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies using ARIMA (simplified)"""
        try:
            # This is a simplified implementation
            # In practice, you would use statsmodels ARIMA
            
            if len(values) < 20:
                return []
            
            # Simple moving average based anomaly detection
            window_size = parameters.get("window_size", 10)
            threshold = parameters.get("threshold", 2.0)
            
            anomalies = []
            for i in range(window_size, len(values)):
                window = values[i-window_size:i]
                current_value = values[i]
                
                # Calculate moving average
                expected_value = np.mean(window)
                
                # Calculate deviation
                if np.std(window) > 0:
                    deviation = abs(current_value - expected_value) / np.std(window)
                    if deviation > threshold:
                        anomalies.append({
                            "index": i,
                            "value": current_value,
                            "expected_value": expected_value,
                            "deviation": deviation,
                            "confidence": min(deviation / threshold, 1.0)
                        })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"❌ Error in ARIMA detection: {e}")
            return []
    
    async def _create_anomaly(
        self,
        metric_name: str,
        anomaly_data: Dict[str, Any],
        detection_method: DetectionMethod
    ):
        """Create an anomaly record"""
        try:
            anomaly_id = f"anomaly_{int(time.time())}_{anomaly_data['index']}"
            
            # Determine anomaly type and severity
            anomaly_type = AnomalyType.STATISTICAL
            if detection_method in [DetectionMethod.LSTM, DetectionMethod.ARIMA]:
                anomaly_type = AnomalyType.TEMPORAL
            elif detection_method in [DetectionMethod.ISOLATION_FOREST, DetectionMethod.ONE_CLASS_SVM]:
                anomaly_type = AnomalyType.BEHAVIORAL
            
            # Determine severity based on deviation
            deviation = anomaly_data["deviation"]
            if deviation > 5.0:
                severity = AnomalySeverity.CRITICAL
            elif deviation > 3.0:
                severity = AnomalySeverity.HIGH
            elif deviation > 2.0:
                severity = AnomalySeverity.MEDIUM
            else:
                severity = AnomalySeverity.LOW
            
            anomaly = Anomaly(
                id=anomaly_id,
                metric_name=metric_name,
                anomaly_type=anomaly_type,
                severity=severity,
                value=anomaly_data["value"],
                expected_value=anomaly_data["expected_value"],
                deviation=deviation,
                confidence=anomaly_data["confidence"],
                timestamp=datetime.now().isoformat(),
                description=f"Anomaly detected in {metric_name} using {detection_method.value}",
                context={
                    "detection_method": detection_method.value,
                    "data_index": anomaly_data["index"]
                }
            )
            
            self.anomalies[anomaly_id] = anomaly
            
            logger.warning(f"Anomaly detected: {anomaly_id} - {metric_name} = {anomaly_data['value']} (expected: {anomaly_data['expected_value']})")
            
        except Exception as e:
            logger.error(f"❌ Error creating anomaly: {e}")
    
    async def _auto_resolve_anomalies(self):
        """Auto-resolve anomalies with low confidence"""
        while self.running:
            try:
                for anomaly in self.anomalies.values():
                    if not anomaly.resolved and anomaly.confidence < self.auto_resolve_threshold:
                        anomaly.resolved = True
                        anomaly.resolved_at = datetime.now().isoformat()
                        logger.info(f"Auto-resolved anomaly: {anomaly.id}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error auto-resolving anomalies: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_old_data(self):
        """Clean up old data"""
        while self.running:
            try:
                # Clean up old anomalies (older than 30 days)
                cutoff_date = datetime.now() - timedelta(days=30)
                old_anomalies = [
                    anomaly_id for anomaly_id, anomaly in self.anomalies.items()
                    if datetime.fromisoformat(anomaly.timestamp) < cutoff_date
                ]
                
                for anomaly_id in old_anomalies:
                    del self.anomalies[anomaly_id]
                
                # Clean up old metric history (keep only recent data)
                for metric_name in list(self.metric_history.keys()):
                    if len(self.metric_history[metric_name]) > self.history_window:
                        self.metric_history[metric_name] = self.metric_history[metric_name][-self.history_window:]
                
                if old_anomalies:
                    logger.info(f"Cleaned up {len(old_anomalies)} old anomalies")
                
                await asyncio.sleep(86400)  # Clean up daily
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up old data: {e}")
                await asyncio.sleep(3600)
    
    async def _load_anomaly_data(self):
        """Load anomaly data from storage"""
        try:
            if self.redis_client:
                # Load anomalies
                anomalies_data = self.redis_client.get("frenly_anomalies")
                if anomalies_data:
                    anomalies_json = json.loads(anomalies_data)
                    for anomaly_id, anomaly_data in anomalies_json.items():
                        anomaly = Anomaly(
                            id=anomaly_id,
                            metric_name=anomaly_data["metric_name"],
                            anomaly_type=AnomalyType(anomaly_data["anomaly_type"]),
                            severity=AnomalySeverity(anomaly_data["severity"]),
                            value=anomaly_data["value"],
                            expected_value=anomaly_data["expected_value"],
                            deviation=anomaly_data["deviation"],
                            confidence=anomaly_data["confidence"],
                            timestamp=anomaly_data["timestamp"],
                            description=anomaly_data["description"],
                            context=anomaly_data.get("context", {}),
                            resolved=anomaly_data.get("resolved", False),
                            resolved_at=anomaly_data.get("resolved_at")
                        )
                        self.anomalies[anomaly_id] = anomaly
                
                # Load detection rules
                rules_data = self.redis_client.get("frenly_detection_rules")
                if rules_data:
                    rules_json = json.loads(rules_data)
                    for rule_id, rule_data in rules_json.items():
                        rule = DetectionRule(
                            id=rule_id,
                            name=rule_data["name"],
                            metric_name=rule_data["metric_name"],
                            detection_method=DetectionMethod(rule_data["detection_method"]),
                            parameters=rule_data["parameters"],
                            threshold=rule_data["threshold"],
                            enabled=rule_data.get("enabled", True),
                            created_at=rule_data["created_at"],
                            updated_at=rule_data["updated_at"]
                        )
                        self.detection_rules[rule_id] = rule
                
                logger.info(f"Loaded {len(self.anomalies)} anomalies and {len(self.detection_rules)} detection rules")
            
        except Exception as e:
            logger.error(f"❌ Error loading anomaly data: {e}")
    
    async def _save_anomaly_data(self):
        """Save anomaly data to storage"""
        try:
            if self.redis_client:
                # Save anomalies
                anomalies_data = {
                    anomaly_id: {
                        "metric_name": anomaly.metric_name,
                        "anomaly_type": anomaly.anomaly_type.value,
                        "severity": anomaly.severity.value,
                        "value": anomaly.value,
                        "expected_value": anomaly.expected_value,
                        "deviation": anomaly.deviation,
                        "confidence": anomaly.confidence,
                        "timestamp": anomaly.timestamp,
                        "description": anomaly.description,
                        "context": anomaly.context,
                        "resolved": anomaly.resolved,
                        "resolved_at": anomaly.resolved_at
                    }
                    for anomaly_id, anomaly in self.anomalies.items()
                }
                self.redis_client.setex("frenly_anomalies", 86400, json.dumps(anomalies_data))
                
                # Save detection rules
                rules_data = {
                    rule_id: {
                        "name": rule.name,
                        "metric_name": rule.metric_name,
                        "detection_method": rule.detection_method.value,
                        "parameters": rule.parameters,
                        "threshold": rule.threshold,
                        "enabled": rule.enabled,
                        "created_at": rule.created_at,
                        "updated_at": rule.updated_at
                    }
                    for rule_id, rule in self.detection_rules.items()
                }
                self.redis_client.setex("frenly_detection_rules", 86400, json.dumps(rules_data))
            
        except Exception as e:
            logger.error(f"❌ Error saving anomaly data: {e}")

# Global anomaly detection system instance
anomaly_detection = AnomalyDetectionSystem()

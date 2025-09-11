#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
⚡ Frenly AI Auto-scaling System
Intelligent auto-scaling based on demand patterns
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

class ScalingPolicy(Enum):
    """Scaling policy enumeration"""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"

class ScalingTrigger(Enum):
    """Scaling trigger enumeration"""
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    REQUEST_RATE = "request_rate"
    RESPONSE_TIME = "response_time"
    QUEUE_LENGTH = "queue_length"
    CUSTOM_METRIC = "custom_metric"

class ScalingDirection(Enum):
    """Scaling direction enumeration"""
    SCALE_OUT = "scale_out"
    SCALE_IN = "scale_in"
    NO_SCALE = "no_scale"

@dataclass
class ScalingTarget:
    """Scaling target definition"""
    id: str
    name: str
    service_type: str
    current_instances: int
    min_instances: int
    max_instances: int
    desired_instances: int
    target_cpu: float
    target_memory: float
    target_response_time: float
    scaling_policy: ScalingPolicy
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ScalingTrigger:
    """Scaling trigger definition"""
    id: str
    target_id: str
    trigger_type: ScalingTrigger
    metric_name: str
    scale_out_threshold: float
    scale_in_threshold: float
    scale_out_cooldown: int  # seconds
    scale_in_cooldown: int  # seconds
    scale_out_step: int
    scale_in_step: int
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ScalingDecision:
    """Scaling decision definition"""
    id: str
    target_id: str
    direction: ScalingDirection
    current_instances: int
    desired_instances: int
    reason: str
    confidence: float
    triggered_by: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    executed: bool = False
    execution_time: Optional[int] = None

@dataclass
class ScalingMetrics:
    """Scaling metrics definition"""
    target_id: str
    timestamp: str
    cpu_utilization: float
    memory_utilization: float
    request_rate: float
    response_time: float
    queue_length: int
    active_instances: int
    custom_metrics: Dict[str, float] = field(default_factory=dict)

class AutoScalingSystem:
    """Auto-scaling system for Frenly AI"""
    
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
        
        # Auto-scaling storage
        self.scaling_targets: Dict[str, ScalingTarget] = {}
        self.scaling_triggers: Dict[str, ScalingTrigger] = {}
        self.scaling_decisions: List[ScalingDecision] = {}
        self.scaling_metrics: Dict[str, List[ScalingMetrics]] = {}
        
        # Configuration
        self.metrics_collection_interval = 30  # seconds
        self.scaling_evaluation_interval = 60  # seconds
        self.metrics_retention_hours = 24
        self.max_scaling_decisions = 1000
        
        # Cooldown tracking
        self.scaling_cooldowns: Dict[str, datetime] = {}
        
        logger.info("✅ Auto-scaling System initialized")
    
    async def start(self):
        """Start the auto-scaling system"""
        self.running = True
        logger.info("🚀 Starting Auto-scaling System...")
        
        # Load existing data
        await self._load_auto_scaling_data()
        
        # Start background tasks
        asyncio.create_task(self._collect_metrics())
        asyncio.create_task(self._evaluate_scaling())
        asyncio.create_task(self._execute_scaling_decisions())
        asyncio.create_task(self._cleanup_old_data())
        
        logger.info("✅ Auto-scaling System started")
    
    async def stop(self):
        """Stop the auto-scaling system"""
        self.running = False
        logger.info("🛑 Stopping Auto-scaling System...")
        
        # Save auto-scaling data
        await self._save_auto_scaling_data()
        
        logger.info("✅ Auto-scaling System stopped")
    
    async def create_scaling_target(
        self,
        name: str,
        service_type: str,
        min_instances: int,
        max_instances: int,
        target_cpu: float = 70.0,
        target_memory: float = 80.0,
        target_response_time: float = 1000.0,
        scaling_policy: ScalingPolicy = ScalingPolicy.BALANCED
    ) -> str:
        """Create a new scaling target"""
        try:
            target_id = f"target_{int(time.time())}"
            
            target = ScalingTarget(
                id=target_id,
                name=name,
                service_type=service_type,
                current_instances=min_instances,
                min_instances=min_instances,
                max_instances=max_instances,
                desired_instances=min_instances,
                target_cpu=target_cpu,
                target_memory=target_memory,
                target_response_time=target_response_time,
                scaling_policy=scaling_policy
            )
            
            self.scaling_targets[target_id] = target
            self.scaling_metrics[target_id] = []
            
            logger.info(f"Scaling target created: {target_id}")
            return target_id
            
        except Exception as e:
            logger.error(f"❌ Error creating scaling target: {e}")
            raise
    
    async def get_scaling_target(self, target_id: str) -> Optional[ScalingTarget]:
        """Get scaling target information"""
        return self.scaling_targets.get(target_id)
    
    async def list_scaling_targets(self) -> List[ScalingTarget]:
        """List all scaling targets"""
        return list(self.scaling_targets.values())
    
    async def update_scaling_target(self, target_id: str, **updates) -> bool:
        """Update a scaling target"""
        try:
            if target_id not in self.scaling_targets:
                logger.warning(f"Scaling target not found: {target_id}")
                return False
            
            target = self.scaling_targets[target_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(target, key):
                    setattr(target, key, value)
            
            target.updated_at = datetime.now().isoformat()
            
            logger.info(f"Scaling target updated: {target_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating scaling target {target_id}: {e}")
            return False
    
    async def delete_scaling_target(self, target_id: str) -> bool:
        """Delete a scaling target"""
        try:
            if target_id not in self.scaling_targets:
                logger.warning(f"Scaling target not found: {target_id}")
                return False
            
            # Delete associated triggers
            triggers_to_delete = [
                trigger_id for trigger_id, trigger in self.scaling_triggers.items()
                if trigger.target_id == target_id
            ]
            
            for trigger_id in triggers_to_delete:
                del self.scaling_triggers[trigger_id]
            
            # Delete target
            del self.scaling_targets[target_id]
            
            # Clear metrics
            if target_id in self.scaling_metrics:
                del self.scaling_metrics[target_id]
            
            logger.info(f"Scaling target deleted: {target_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting scaling target {target_id}: {e}")
            return False
    
    async def create_scaling_trigger(
        self,
        target_id: str,
        trigger_type: ScalingTrigger,
        metric_name: str,
        scale_out_threshold: float,
        scale_in_threshold: float,
        scale_out_cooldown: int = 300,
        scale_in_cooldown: int = 600,
        scale_out_step: int = 1,
        scale_in_step: int = 1
    ) -> str:
        """Create a new scaling trigger"""
        try:
            if target_id not in self.scaling_targets:
                raise ValueError("Scaling target not found")
            
            trigger_id = f"trigger_{int(time.time())}"
            
            trigger = ScalingTrigger(
                id=trigger_id,
                target_id=target_id,
                trigger_type=trigger_type,
                metric_name=metric_name,
                scale_out_threshold=scale_out_threshold,
                scale_in_threshold=scale_in_threshold,
                scale_out_cooldown=scale_out_cooldown,
                scale_in_cooldown=scale_in_cooldown,
                scale_out_step=scale_out_step,
                scale_in_step=scale_in_step
            )
            
            self.scaling_triggers[trigger_id] = trigger
            
            logger.info(f"Scaling trigger created: {trigger_id}")
            return trigger_id
            
        except Exception as e:
            logger.error(f"❌ Error creating scaling trigger: {e}")
            raise
    
    async def get_scaling_trigger(self, trigger_id: str) -> Optional[ScalingTrigger]:
        """Get scaling trigger information"""
        return self.scaling_triggers.get(trigger_id)
    
    async def list_scaling_triggers(self, target_id: Optional[str] = None) -> List[ScalingTrigger]:
        """List scaling triggers with optional target filter"""
        triggers = list(self.scaling_triggers.values())
        
        if target_id:
            triggers = [t for t in triggers if t.target_id == target_id]
        
        return triggers
    
    async def update_scaling_trigger(self, trigger_id: str, **updates) -> bool:
        """Update a scaling trigger"""
        try:
            if trigger_id not in self.scaling_triggers:
                logger.warning(f"Scaling trigger not found: {trigger_id}")
                return False
            
            trigger = self.scaling_triggers[trigger_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(trigger, key):
                    setattr(trigger, key, value)
            
            logger.info(f"Scaling trigger updated: {trigger_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating scaling trigger {trigger_id}: {e}")
            return False
    
    async def delete_scaling_trigger(self, trigger_id: str) -> bool:
        """Delete a scaling trigger"""
        try:
            if trigger_id not in self.scaling_triggers:
                logger.warning(f"Scaling trigger not found: {trigger_id}")
                return False
            
            del self.scaling_triggers[trigger_id]
            
            logger.info(f"Scaling trigger deleted: {trigger_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting scaling trigger {trigger_id}: {e}")
            return False
    
    async def add_scaling_metrics(
        self,
        target_id: str,
        cpu_utilization: float,
        memory_utilization: float,
        request_rate: float,
        response_time: float,
        queue_length: int,
        active_instances: int,
        custom_metrics: Optional[Dict[str, float]] = None
    ) -> bool:
        """Add scaling metrics for a target"""
        try:
            if target_id not in self.scaling_targets:
                logger.warning(f"Scaling target not found: {target_id}")
                return False
            
            metrics = ScalingMetrics(
                target_id=target_id,
                timestamp=datetime.now().isoformat(),
                cpu_utilization=cpu_utilization,
                memory_utilization=memory_utilization,
                request_rate=request_rate,
                response_time=response_time,
                queue_length=queue_length,
                active_instances=active_instances,
                custom_metrics=custom_metrics or {}
            )
            
            self.scaling_metrics[target_id].append(metrics)
            
            # Keep only recent metrics
            cutoff_time = datetime.now() - timedelta(hours=self.metrics_retention_hours)
            self.scaling_metrics[target_id] = [
                m for m in self.scaling_metrics[target_id]
                if datetime.fromisoformat(m.timestamp) > cutoff_time
            ]
            
            logger.debug(f"Scaling metrics added for target: {target_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding scaling metrics: {e}")
            return False
    
    async def get_scaling_metrics(self, target_id: str, hours: int = 1) -> List[ScalingMetrics]:
        """Get scaling metrics for a target"""
        if target_id not in self.scaling_metrics:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            m for m in self.scaling_metrics[target_id]
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]
    
    async def get_scaling_decisions(self, target_id: Optional[str] = None, limit: int = 100) -> List[ScalingDecision]:
        """Get scaling decisions with optional target filter"""
        decisions = list(self.scaling_decisions.values())
        
        if target_id:
            decisions = [d for d in decisions if d.target_id == target_id]
        
        # Sort by timestamp descending
        decisions.sort(key=lambda d: d.timestamp, reverse=True)
        
        return decisions[:limit]
    
    async def get_auto_scaling_analytics(self) -> Dict[str, Any]:
        """Get auto-scaling analytics"""
        try:
            total_targets = len(self.scaling_targets)
            enabled_targets = len([t for t in self.scaling_targets.values() if t.enabled])
            total_triggers = len(self.scaling_triggers)
            enabled_triggers = len([t for t in self.scaling_triggers.values() if t.enabled])
            
            # Scaling decisions
            total_decisions = len(self.scaling_decisions)
            executed_decisions = len([d for d in self.scaling_decisions.values() if d.executed])
            scale_out_decisions = len([d for d in self.scaling_decisions.values() if d.direction == ScalingDirection.SCALE_OUT])
            scale_in_decisions = len([d for d in self.scaling_decisions.values() if d.direction == ScalingDirection.SCALE_IN])
            
            # Recent activity
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_decisions = [
                d for d in self.scaling_decisions.values()
                if datetime.fromisoformat(d.timestamp) > recent_cutoff
            ]
            
            # Target distribution by policy
            policy_distribution = {}
            for target in self.scaling_targets.values():
                policy = target.scaling_policy.value
                policy_distribution[policy] = policy_distribution.get(policy, 0) + 1
            
            # Average metrics across all targets
            all_metrics = []
            for metrics_list in self.scaling_metrics.values():
                all_metrics.extend(metrics_list)
            
            if all_metrics:
                avg_cpu = sum(m.cpu_utilization for m in all_metrics) / len(all_metrics)
                avg_memory = sum(m.memory_utilization for m in all_metrics) / len(all_metrics)
                avg_response_time = sum(m.response_time for m in all_metrics) / len(all_metrics)
            else:
                avg_cpu = avg_memory = avg_response_time = 0.0
            
            return {
                "targets": {
                    "total": total_targets,
                    "enabled": enabled_targets,
                    "policy_distribution": policy_distribution
                },
                "triggers": {
                    "total": total_triggers,
                    "enabled": enabled_triggers
                },
                "decisions": {
                    "total": total_decisions,
                    "executed": executed_decisions,
                    "scale_out": scale_out_decisions,
                    "scale_in": scale_in_decisions,
                    "execution_rate": executed_decisions / total_decisions if total_decisions > 0 else 0,
                    "recent": len(recent_decisions)
                },
                "metrics": {
                    "avg_cpu_utilization": avg_cpu,
                    "avg_memory_utilization": avg_memory,
                    "avg_response_time": avg_response_time
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting auto-scaling analytics: {e}")
            return {"error": str(e)}
    
    async def _collect_metrics(self):
        """Collect metrics for all targets"""
        while self.running:
            try:
                for target in self.scaling_targets.values():
                    if not target.enabled:
                        continue
                    
                    # In practice, this would collect real metrics from monitoring systems
                    await self._collect_target_metrics(target)
                
                await asyncio.sleep(self.metrics_collection_interval)
                
            except Exception as e:
                logger.error(f"❌ Error collecting metrics: {e}")
                await asyncio.sleep(60)
    
    async def _collect_target_metrics(self, target: ScalingTarget):
        try:
            # In practice, this would query actual monitoring systems
            
            # Generate realistic metrics based on current load
            base_load = 0.5  # Base load level
            variation = 0.2  # Random variation
            
            cpu_utilization = max(0, min(100, base_load * 100 + np.random.normal(0, variation * 100)))
            memory_utilization = max(0, min(100, base_load * 100 + np.random.normal(0, variation * 100)))
            request_rate = max(0, base_load * 1000 + np.random.normal(0, variation * 1000))
            response_time = max(0, base_load * 1000 + np.random.normal(0, variation * 1000))
            queue_length = max(0, int(base_load * 100 + np.random.normal(0, variation * 100)))
            
            await self.add_scaling_metrics(
                target.id,
                cpu_utilization,
                memory_utilization,
                request_rate,
                response_time,
                queue_length,
                target.current_instances
            )
            
        except Exception as e:
            logger.error(f"❌ Error collecting metrics for target {target.id}: {e}")
    
    async def _evaluate_scaling(self):
        """Evaluate scaling decisions for all targets"""
        while self.running:
            try:
                for target in self.scaling_targets.values():
                    if not target.enabled:
                        continue
                    
                    await self._evaluate_target_scaling(target)
                
                await asyncio.sleep(self.scaling_evaluation_interval)
                
            except Exception as e:
                logger.error(f"❌ Error evaluating scaling: {e}")
                await asyncio.sleep(60)
    
    async def _evaluate_target_scaling(self, target: ScalingTarget):
        try:
            # Get recent metrics
            recent_metrics = await self.get_scaling_metrics(target.id, hours=1)
            if not recent_metrics:
                return
            
            # Get triggers for this target
            triggers = [t for t in self.scaling_triggers.values() if t.target_id == target.id and t.enabled]
            if not triggers:
                return
            
            # Check cooldown
            cooldown_key = f"target_{target.id}"
            if cooldown_key in self.scaling_cooldowns:
                if datetime.now() < self.scaling_cooldowns[cooldown_key]:
                    return  # Still in cooldown
            
            # Evaluate each trigger
            scale_out_triggers = []
            scale_in_triggers = []
            
            for trigger in triggers:
                # Calculate average metric value
                metric_values = []
                for metrics in recent_metrics:
                    if trigger.metric_name == "cpu_utilization":
                        metric_values.append(metrics.cpu_utilization)
                    elif trigger.metric_name == "memory_utilization":
                        metric_values.append(metrics.memory_utilization)
                    elif trigger.metric_name == "request_rate":
                        metric_values.append(metrics.request_rate)
                    elif trigger.metric_name == "response_time":
                        metric_values.append(metrics.response_time)
                    elif trigger.metric_name == "queue_length":
                        metric_values.append(metrics.queue_length)
                    elif trigger.metric_name in metrics.custom_metrics:
                        metric_values.append(metrics.custom_metrics[trigger.metric_name])
                
                if not metric_values:
                    continue
                
                avg_metric = sum(metric_values) / len(metric_values)
                
                # Check scaling conditions
                if avg_metric > trigger.scale_out_threshold and target.current_instances < target.max_instances:
                    scale_out_triggers.append((trigger, avg_metric))
                elif avg_metric < trigger.scale_in_threshold and target.current_instances > target.min_instances:
                    scale_in_triggers.append((trigger, avg_metric))
            
            # Make scaling decision
            if scale_out_triggers:
                await self._make_scaling_decision(target, ScalingDirection.SCALE_OUT, scale_out_triggers)
            elif scale_in_triggers:
                await self._make_scaling_decision(target, ScalingDirection.SCALE_IN, scale_in_triggers)
            
        except Exception as e:
            logger.error(f"❌ Error evaluating scaling for target {target.id}: {e}")
    
    async def _make_scaling_decision(self, target: ScalingTarget, direction: ScalingDirection, triggers: List[Tuple[ScalingTrigger, float]]):
        """Make a scaling decision"""
        try:
            decision_id = f"decision_{int(time.time())}"
            
            # Calculate desired instances
            if direction == ScalingDirection.SCALE_OUT:
                # Use the most aggressive trigger
                max_step = max(trigger[0].scale_out_step for trigger in triggers)
                desired_instances = min(target.current_instances + max_step, target.max_instances)
            else:
                # Use the most conservative trigger
                min_step = min(trigger[0].scale_in_step for trigger in triggers)
                desired_instances = max(target.current_instances - min_step, target.min_instances)
            
            # Calculate confidence based on number of triggers and metric values
            confidence = min(1.0, len(triggers) * 0.3 + 0.4)
            
            # Generate reason
            trigger_names = [trigger[0].metric_name for trigger in triggers]
            reason = f"Scaling {direction.value} triggered by: {', '.join(trigger_names)}"
            
            decision = ScalingDecision(
                id=decision_id,
                target_id=target.id,
                direction=direction,
                current_instances=target.current_instances,
                desired_instances=desired_instances,
                reason=reason,
                confidence=confidence,
                triggered_by=trigger_names
            )
            
            self.scaling_decisions[decision_id] = decision
            
            # Set cooldown
            cooldown_duration = max(trigger[0].scale_out_cooldown if direction == ScalingDirection.SCALE_OUT else trigger[0].scale_in_cooldown for trigger in triggers)
            self.scaling_cooldowns[f"target_{target.id}"] = datetime.now() + timedelta(seconds=cooldown_duration)
            
            logger.info(f"Scaling decision made: {decision_id} - {target.name} {direction.value} {target.current_instances} -> {desired_instances}")
            
        except Exception as e:
            logger.error(f"❌ Error making scaling decision: {e}")
    
    async def _execute_scaling_decisions(self):
        """Execute pending scaling decisions"""
        while self.running:
            try:
                pending_decisions = [
                    d for d in self.scaling_decisions.values()
                    if not d.executed
                ]
                
                for decision in pending_decisions:
                    await self._execute_scaling_decision(decision)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error executing scaling decisions: {e}")
                await asyncio.sleep(60)
    
    async def _execute_scaling_decision(self, decision: ScalingDecision):
        """Execute a scaling decision"""
        try:
            if decision.target_id not in self.scaling_targets:
                decision.executed = True
                return
            
            target = self.scaling_targets[decision.target_id]
            
            # In practice, this would create/destroy actual instances
            start_time = time.time()
            
            # Update target instances
            target.current_instances = decision.desired_instances
            target.desired_instances = decision.desired_instances
            
            
            execution_time = int((time.time() - start_time) * 1000)  # milliseconds
            
            # Mark as executed
            decision.executed = True
            decision.execution_time = execution_time
            
            logger.info(f"Scaling decision executed: {decision.id} - {target.name} scaled to {decision.desired_instances} instances")
            
        except Exception as e:
            logger.error(f"❌ Error executing scaling decision {decision.id}: {e}")
            decision.executed = True
    
    async def _cleanup_old_data(self):
        """Clean up old data"""
        while self.running:
            try:
                # Clean up old scaling decisions
                cutoff_date = datetime.now() - timedelta(days=7)
                old_decisions = [
                    decision_id for decision_id, decision in self.scaling_decisions.items()
                    if datetime.fromisoformat(decision.timestamp) < cutoff_date
                ]
                
                for decision_id in old_decisions:
                    del self.scaling_decisions[decision_id]
                
                # Clean up old metrics
                for target_id in self.scaling_metrics:
                    cutoff_time = datetime.now() - timedelta(hours=self.metrics_retention_hours)
                    self.scaling_metrics[target_id] = [
                        m for m in self.scaling_metrics[target_id]
                        if datetime.fromisoformat(m.timestamp) > cutoff_time
                    ]
                
                if old_decisions:
                    logger.info(f"Cleaned up {len(old_decisions)} old scaling decisions")
                
                await asyncio.sleep(86400)  # Clean up daily
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up old data: {e}")
                await asyncio.sleep(3600)
    
    async def _load_auto_scaling_data(self):
        """Load auto-scaling data from storage"""
        try:
            if self.redis_client:
                # Load scaling targets
                targets_data = self.redis_client.get("frenly_auto_scaling_targets")
                if targets_data:
                    targets_json = json.loads(targets_data)
                    for target_id, target_data in targets_json.items():
                        target = ScalingTarget(
                            id=target_id,
                            name=target_data["name"],
                            service_type=target_data["service_type"],
                            current_instances=target_data["current_instances"],
                            min_instances=target_data["min_instances"],
                            max_instances=target_data["max_instances"],
                            desired_instances=target_data["desired_instances"],
                            target_cpu=target_data["target_cpu"],
                            target_memory=target_data["target_memory"],
                            target_response_time=target_data["target_response_time"],
                            scaling_policy=ScalingPolicy(target_data["scaling_policy"]),
                            enabled=target_data.get("enabled", True),
                            created_at=target_data["created_at"],
                            updated_at=target_data["updated_at"]
                        )
                        self.scaling_targets[target_id] = target
                        self.scaling_metrics[target_id] = []
                
                # Load scaling triggers
                triggers_data = self.redis_client.get("frenly_auto_scaling_triggers")
                if triggers_data:
                    triggers_json = json.loads(triggers_data)
                    for trigger_id, trigger_data in triggers_json.items():
                        trigger = ScalingTrigger(
                            id=trigger_id,
                            target_id=trigger_data["target_id"],
                            trigger_type=ScalingTrigger(trigger_data["trigger_type"]),
                            metric_name=trigger_data["metric_name"],
                            scale_out_threshold=trigger_data["scale_out_threshold"],
                            scale_in_threshold=trigger_data["scale_in_threshold"],
                            scale_out_cooldown=trigger_data["scale_out_cooldown"],
                            scale_in_cooldown=trigger_data["scale_in_cooldown"],
                            scale_out_step=trigger_data["scale_out_step"],
                            scale_in_step=trigger_data["scale_in_step"],
                            enabled=trigger_data.get("enabled", True),
                            created_at=trigger_data["created_at"]
                        )
                        self.scaling_triggers[trigger_id] = trigger
                
                # Load scaling decisions
                decisions_data = self.redis_client.get("frenly_auto_scaling_decisions")
                if decisions_data:
                    decisions_json = json.loads(decisions_data)
                    for decision_id, decision_data in decisions_json.items():
                        decision = ScalingDecision(
                            id=decision_id,
                            target_id=decision_data["target_id"],
                            direction=ScalingDirection(decision_data["direction"]),
                            current_instances=decision_data["current_instances"],
                            desired_instances=decision_data["desired_instances"],
                            reason=decision_data["reason"],
                            confidence=decision_data["confidence"],
                            triggered_by=decision_data.get("triggered_by", []),
                            timestamp=decision_data["timestamp"],
                            executed=decision_data.get("executed", False),
                            execution_time=decision_data.get("execution_time")
                        )
                        self.scaling_decisions[decision_id] = decision
                
                logger.info(f"Loaded {len(self.scaling_targets)} targets, {len(self.scaling_triggers)} triggers, {len(self.scaling_decisions)} decisions")
            
        except Exception as e:
            logger.error(f"❌ Error loading auto-scaling data: {e}")
    
    async def _save_auto_scaling_data(self):
        """Save auto-scaling data to storage"""
        try:
            if self.redis_client:
                # Save scaling targets
                targets_data = {
                    target_id: {
                        "name": target.name,
                        "service_type": target.service_type,
                        "current_instances": target.current_instances,
                        "min_instances": target.min_instances,
                        "max_instances": target.max_instances,
                        "desired_instances": target.desired_instances,
                        "target_cpu": target.target_cpu,
                        "target_memory": target.target_memory,
                        "target_response_time": target.target_response_time,
                        "scaling_policy": target.scaling_policy.value,
                        "enabled": target.enabled,
                        "created_at": target.created_at,
                        "updated_at": target.updated_at
                    }
                    for target_id, target in self.scaling_targets.items()
                }
                self.redis_client.setex("frenly_auto_scaling_targets", 86400, json.dumps(targets_data))
                
                # Save scaling triggers
                triggers_data = {
                    trigger_id: {
                        "target_id": trigger.target_id,
                        "trigger_type": trigger.trigger_type.value,
                        "metric_name": trigger.metric_name,
                        "scale_out_threshold": trigger.scale_out_threshold,
                        "scale_in_threshold": trigger.scale_in_threshold,
                        "scale_out_cooldown": trigger.scale_out_cooldown,
                        "scale_in_cooldown": trigger.scale_in_cooldown,
                        "scale_out_step": trigger.scale_out_step,
                        "scale_in_step": trigger.scale_in_step,
                        "enabled": trigger.enabled,
                        "created_at": trigger.created_at
                    }
                    for trigger_id, trigger in self.scaling_triggers.items()
                }
                self.redis_client.setex("frenly_auto_scaling_triggers", 86400, json.dumps(triggers_data))
                
                # Save scaling decisions
                decisions_data = {
                    decision_id: {
                        "target_id": decision.target_id,
                        "direction": decision.direction.value,
                        "current_instances": decision.current_instances,
                        "desired_instances": decision.desired_instances,
                        "reason": decision.reason,
                        "confidence": decision.confidence,
                        "triggered_by": decision.triggered_by,
                        "timestamp": decision.timestamp,
                        "executed": decision.executed,
                        "execution_time": decision.execution_time
                    }
                    for decision_id, decision in self.scaling_decisions.items()
                }
                self.redis_client.setex("frenly_auto_scaling_decisions", 86400, json.dumps(decisions_data))
            
        except Exception as e:
            logger.error(f"❌ Error saving auto-scaling data: {e}")

# Global auto-scaling system instance
auto_scaling = AutoScalingSystem()

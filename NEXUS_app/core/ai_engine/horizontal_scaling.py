#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
📈 Frenly AI Horizontal Scaling System
Auto-scaling and load balancing for Frenly AI
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class ScalingAction(Enum):
    """Scaling action enumeration"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SCALE_OUT = "scale_out"
    SCALE_IN = "scale_in"
    NO_ACTION = "no_action"

class ServiceStatus(Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    SCALING = "scaling"

class LoadBalancerType(Enum):
    """Load balancer type enumeration"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"

@dataclass
class ServiceInstance:
    """Service instance definition"""
    id: str
    service_name: str
    host: str
    port: int
    status: ServiceStatus
    cpu_usage: float
    memory_usage: float
    active_connections: int
    response_time: float
    last_health_check: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScalingRule:
    """Scaling rule definition"""
    id: str
    service_name: str
    metric_name: str
    threshold: float
    scale_up_threshold: float
    scale_down_threshold: float
    min_instances: int
    max_instances: int
    scale_up_cooldown: int  # seconds
    scale_down_cooldown: int  # seconds
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ScalingEvent:
    """Scaling event definition"""
    id: str
    service_name: str
    action: ScalingAction
    instances_before: int
    instances_after: int
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration: Optional[int] = None
    success: bool = True

class HorizontalScalingSystem:
    """Horizontal scaling system for Frenly AI"""
    
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
        
        # Scaling storage
        self.service_instances: Dict[str, ServiceInstance] = {}
        self.scaling_rules: Dict[str, ScalingRule] = {}
        self.scaling_events: List[ScalingEvent] = []
        
        # Configuration
        self.health_check_interval = 30  # seconds
        self.scaling_check_interval = 60  # seconds
        self.load_balancer_type = LoadBalancerType.LEAST_CONNECTIONS
        self.max_scaling_events = 1000
        
        # Cooldown tracking
        self.scaling_cooldowns: Dict[str, datetime] = {}
        
        logger.info("✅ Horizontal Scaling System initialized")
    
    async def start(self):
        """Start the horizontal scaling system"""
        self.running = True
        logger.info("🚀 Starting Horizontal Scaling System...")
        
        # Load existing data
        await self._load_scaling_data()
        
        # Start background tasks
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._scaling_loop())
        asyncio.create_task(self._cleanup_old_events())
        
        logger.info("✅ Horizontal Scaling System started")
    
    async def stop(self):
        """Stop the horizontal scaling system"""
        self.running = False
        logger.info("🛑 Stopping Horizontal Scaling System...")
        
        # Save scaling data
        await self._save_scaling_data()
        
        logger.info("✅ Horizontal Scaling System stopped")
    
    async def register_service_instance(
        self,
        service_name: str,
        host: str,
        port: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register a new service instance"""
        try:
            instance_id = f"{service_name}_{int(time.time())}"
            
            instance = ServiceInstance(
                id=instance_id,
                service_name=service_name,
                host=host,
                port=port,
                status=ServiceStatus.STARTING,
                cpu_usage=0.0,
                memory_usage=0.0,
                active_connections=0,
                response_time=0.0,
                last_health_check=datetime.now().isoformat(),
                metadata=metadata or {}
            )
            
            self.service_instances[instance_id] = instance
            
            logger.info(f"Service instance registered: {instance_id}")
            return instance_id
            
        except Exception as e:
            logger.error(f"❌ Error registering service instance: {e}")
            raise
    
    async def unregister_service_instance(self, instance_id: str) -> bool:
        """Unregister a service instance"""
        try:
            if instance_id not in self.service_instances:
                logger.warning(f"Service instance not found: {instance_id}")
                return False
            
            del self.service_instances[instance_id]
            
            logger.info(f"Service instance unregistered: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error unregistering service instance {instance_id}: {e}")
            return False
    
    async def update_instance_metrics(
        self,
        instance_id: str,
        cpu_usage: float,
        memory_usage: float,
        active_connections: int,
        response_time: float
    ) -> bool:
        """Update service instance metrics"""
        try:
            if instance_id not in self.service_instances:
                logger.warning(f"Service instance not found: {instance_id}")
                return False
            
            instance = self.service_instances[instance_id]
            instance.cpu_usage = cpu_usage
            instance.memory_usage = memory_usage
            instance.active_connections = active_connections
            instance.response_time = response_time
            instance.last_health_check = datetime.now().isoformat()
            
            logger.debug(f"Instance metrics updated: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating instance metrics: {e}")
            return False
    
    async def get_service_instances(self, service_name: Optional[str] = None) -> List[ServiceInstance]:
        """Get service instances with optional service filter"""
        instances = list(self.service_instances.values())
        
        if service_name:
            instances = [i for i in instances if i.service_name == service_name]
        
        return instances
    
    async def create_scaling_rule(
        self,
        service_name: str,
        metric_name: str,
        threshold: float,
        scale_up_threshold: float,
        scale_down_threshold: float,
        min_instances: int,
        max_instances: int,
        scale_up_cooldown: int = 300,
        scale_down_cooldown: int = 600
    ) -> str:
        """Create a new scaling rule"""
        try:
            rule_id = f"rule_{int(time.time())}"
            
            rule = ScalingRule(
                id=rule_id,
                service_name=service_name,
                metric_name=metric_name,
                threshold=threshold,
                scale_up_threshold=scale_up_threshold,
                scale_down_threshold=scale_down_threshold,
                min_instances=min_instances,
                max_instances=max_instances,
                scale_up_cooldown=scale_up_cooldown,
                scale_down_cooldown=scale_down_cooldown
            )
            
            self.scaling_rules[rule_id] = rule
            
            logger.info(f"Scaling rule created: {rule_id}")
            return rule_id
            
        except Exception as e:
            logger.error(f"❌ Error creating scaling rule: {e}")
            raise
    
    async def get_scaling_rule(self, rule_id: str) -> Optional[ScalingRule]:
        """Get scaling rule information"""
        return self.scaling_rules.get(rule_id)
    
    async def list_scaling_rules(self) -> List[ScalingRule]:
        """List all scaling rules"""
        return list(self.scaling_rules.values())
    
    async def update_scaling_rule(self, rule_id: str, **updates) -> bool:
        """Update a scaling rule"""
        try:
            if rule_id not in self.scaling_rules:
                logger.warning(f"Scaling rule not found: {rule_id}")
                return False
            
            rule = self.scaling_rules[rule_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            logger.info(f"Scaling rule updated: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating scaling rule {rule_id}: {e}")
            return False
    
    async def delete_scaling_rule(self, rule_id: str) -> bool:
        """Delete a scaling rule"""
        try:
            if rule_id not in self.scaling_rules:
                logger.warning(f"Scaling rule not found: {rule_id}")
                return False
            
            del self.scaling_rules[rule_id]
            
            logger.info(f"Scaling rule deleted: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting scaling rule {rule_id}: {e}")
            return False
    
    async def get_scaling_events(self, service_name: Optional[str] = None, limit: int = 100) -> List[ScalingEvent]:
        """Get scaling events with optional service filter"""
        events = self.scaling_events
        
        if service_name:
            events = [e for e in events if e.service_name == service_name]
        
        # Sort by timestamp descending
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        return events[:limit]
    
    async def get_load_balancer_targets(self, service_name: str) -> List[ServiceInstance]:
        """Get load balancer targets for a service"""
        try:
            instances = await self.get_service_instances(service_name)
            
            # Filter healthy instances
            healthy_instances = [i for i in instances if i.status == ServiceStatus.HEALTHY]
            
            # Sort based on load balancer type
            if self.load_balancer_type == LoadBalancerType.LEAST_CONNECTIONS:
                healthy_instances.sort(key=lambda i: i.active_connections)
            elif self.load_balancer_type == LoadBalancerType.LEAST_RESPONSE_TIME:
                healthy_instances.sort(key=lambda i: i.response_time)
            # For round robin, no sorting needed
            
            return healthy_instances
            
        except Exception as e:
            logger.error(f"❌ Error getting load balancer targets: {e}")
            return []
    
    async def get_scaling_analytics(self) -> Dict[str, Any]:
        """Get scaling system analytics"""
        try:
            total_instances = len(self.service_instances)
            healthy_instances = len([i for i in self.service_instances.values() if i.status == ServiceStatus.HEALTHY])
            unhealthy_instances = len([i for i in self.service_instances.values() if i.status == ServiceStatus.UNHEALTHY])
            
            # Service distribution
            service_distribution = {}
            for instance in self.service_instances.values():
                service = instance.service_name
                service_distribution[service] = service_distribution.get(service, 0) + 1
            
            # Scaling events
            total_events = len(self.scaling_events)
            scale_up_events = len([e for e in self.scaling_events if e.action in [ScalingAction.SCALE_UP, ScalingAction.SCALE_OUT]])
            scale_down_events = len([e for e in self.scaling_events if e.action in [ScalingAction.SCALE_DOWN, ScalingAction.SCALE_IN]])
            
            # Recent activity
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_events = [
                e for e in self.scaling_events
                if datetime.fromisoformat(e.timestamp) > recent_cutoff
            ]
            
            # Average metrics
            if self.service_instances:
                avg_cpu = sum(i.cpu_usage for i in self.service_instances.values()) / len(self.service_instances)
                avg_memory = sum(i.memory_usage for i in self.service_instances.values()) / len(self.service_instances)
                avg_response_time = sum(i.response_time for i in self.service_instances.values()) / len(self.service_instances)
            else:
                avg_cpu = avg_memory = avg_response_time = 0.0
            
            return {
                "instances": {
                    "total": total_instances,
                    "healthy": healthy_instances,
                    "unhealthy": unhealthy_instances,
                    "health_rate": healthy_instances / total_instances if total_instances > 0 else 0
                },
                "services": {
                    "total": len(service_distribution),
                    "distribution": service_distribution
                },
                "scaling": {
                    "total_events": total_events,
                    "scale_up_events": scale_up_events,
                    "scale_down_events": scale_down_events,
                    "recent_events": len(recent_events)
                },
                "metrics": {
                    "avg_cpu_usage": avg_cpu,
                    "avg_memory_usage": avg_memory,
                    "avg_response_time": avg_response_time
                },
                "rules": {
                    "total": len(self.scaling_rules),
                    "enabled": len([r for r in self.scaling_rules.values() if r.enabled])
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting scaling analytics: {e}")
            return {"error": str(e)}
    
    async def _health_check_loop(self):
        """Health check loop for service instances"""
        while self.running:
            try:
                for instance in self.service_instances.values():
                    await self._perform_health_check(instance)
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in health check loop: {e}")
                await asyncio.sleep(60)
    
    async def _perform_health_check(self, instance: ServiceInstance):
        """Perform health check on a service instance"""
        try:
            # In practice, this would make actual HTTP requests
            
            # Check if instance is responsive
            is_healthy = (
                instance.cpu_usage < 90.0 and
                instance.memory_usage < 90.0 and
                instance.response_time < 5000.0  # 5 seconds
            )
            
            if is_healthy:
                instance.status = ServiceStatus.HEALTHY
            else:
                instance.status = ServiceStatus.UNHEALTHY
                logger.warning(f"Instance {instance.id} is unhealthy")
            
            instance.last_health_check = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"❌ Error performing health check on {instance.id}: {e}")
            instance.status = ServiceStatus.UNHEALTHY
    
    async def _scaling_loop(self):
        """Scaling decision loop"""
        while self.running:
            try:
                for rule in self.scaling_rules.values():
                    if not rule.enabled:
                        continue
                    
                    await self._evaluate_scaling_rule(rule)
                
                await asyncio.sleep(self.scaling_check_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in scaling loop: {e}")
                await asyncio.sleep(60)
    
    async def _evaluate_scaling_rule(self, rule: ScalingRule):
        """Evaluate a scaling rule and take action if needed"""
        try:
            # Get current instances for the service
            current_instances = await self.get_service_instances(rule.service_name)
            healthy_instances = [i for i in current_instances if i.status == ServiceStatus.HEALTHY]
            current_count = len(healthy_instances)
            
            # Check cooldown
            cooldown_key = f"{rule.service_name}_{rule.id}"
            if cooldown_key in self.scaling_cooldowns:
                if datetime.now() < self.scaling_cooldowns[cooldown_key]:
                    return  # Still in cooldown
            
            # Calculate average metric value
            if not healthy_instances:
                return  # No instances to evaluate
            
            metric_values = []
            for instance in healthy_instances:
                if rule.metric_name == "cpu_usage":
                    metric_values.append(instance.cpu_usage)
                elif rule.metric_name == "memory_usage":
                    metric_values.append(instance.memory_usage)
                elif rule.metric_name == "response_time":
                    metric_values.append(instance.response_time)
                elif rule.metric_name == "active_connections":
                    metric_values.append(instance.active_connections)
            
            if not metric_values:
                return
            
            avg_metric = sum(metric_values) / len(metric_values)
            
            # Determine scaling action
            action = ScalingAction.NO_ACTION
            reason = ""
            
            if avg_metric > rule.scale_up_threshold and current_count < rule.max_instances:
                action = ScalingAction.SCALE_OUT
                reason = f"Metric {rule.metric_name} ({avg_metric:.2f}) exceeds scale-up threshold ({rule.scale_up_threshold})"
            elif avg_metric < rule.scale_down_threshold and current_count > rule.min_instances:
                action = ScalingAction.SCALE_IN
                reason = f"Metric {rule.metric_name} ({avg_metric:.2f}) below scale-down threshold ({rule.scale_down_threshold})"
            
            # Execute scaling action
            if action != ScalingAction.NO_ACTION:
                await self._execute_scaling_action(rule, action, current_count, reason)
                
                # Set cooldown
                cooldown_duration = rule.scale_up_cooldown if action in [ScalingAction.SCALE_UP, ScalingAction.SCALE_OUT] else rule.scale_down_cooldown
                self.scaling_cooldowns[cooldown_key] = datetime.now() + timedelta(seconds=cooldown_duration)
            
        except Exception as e:
            logger.error(f"❌ Error evaluating scaling rule {rule.id}: {e}")
    
    async def _execute_scaling_action(self, rule: ScalingRule, action: ScalingAction, current_count: int, reason: str):
        """Execute a scaling action"""
        try:
            event_id = f"event_{int(time.time())}"
            
            # Calculate target count
            if action in [ScalingAction.SCALE_UP, ScalingAction.SCALE_OUT]:
                target_count = min(current_count + 1, rule.max_instances)
            else:
                target_count = max(current_count - 1, rule.min_instances)
            
            # Create scaling event
            event = ScalingEvent(
                id=event_id,
                service_name=rule.service_name,
                action=action,
                instances_before=current_count,
                instances_after=target_count,
                reason=reason
            )
            
            self.scaling_events.append(event)
            
            # In practice, this would create/destroy actual instances
            if action in [ScalingAction.SCALE_UP, ScalingAction.SCALE_OUT]:
                # Create new instance
                new_instance_id = await self.register_service_instance(
                    rule.service_name,
                    f"host-{int(time.time())}",
                    8080
                )
                logger.info(f"Scaled out {rule.service_name}: {current_count} -> {target_count}")
            else:
                # Remove an instance
                instances = await self.get_service_instances(rule.service_name)
                if instances:
                    await self.unregister_service_instance(instances[0].id)
                logger.info(f"Scaled in {rule.service_name}: {current_count} -> {target_count}")
            
            # Keep only recent events
            if len(self.scaling_events) > self.max_scaling_events:
                self.scaling_events = self.scaling_events[-self.max_scaling_events:]
            
        except Exception as e:
            logger.error(f"❌ Error executing scaling action: {e}")
    
    async def _cleanup_old_events(self):
        """Clean up old scaling events"""
        while self.running:
            try:
                # Keep only events from last 30 days
                cutoff_date = datetime.now() - timedelta(days=30)
                old_events = [
                    e for e in self.scaling_events
                    if datetime.fromisoformat(e.timestamp) < cutoff_date
                ]
                
                for event in old_events:
                    self.scaling_events.remove(event)
                
                if old_events:
                    logger.info(f"Cleaned up {len(old_events)} old scaling events")
                
                await asyncio.sleep(86400)  # Clean up daily
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up old events: {e}")
                await asyncio.sleep(3600)
    
    async def _load_scaling_data(self):
        """Load scaling data from storage"""
        try:
            if self.redis_client:
                # Load service instances
                instances_data = self.redis_client.get("frenly_scaling_instances")
                if instances_data:
                    instances_json = json.loads(instances_data)
                    for instance_id, instance_data in instances_json.items():
                        instance = ServiceInstance(
                            id=instance_id,
                            service_name=instance_data["service_name"],
                            host=instance_data["host"],
                            port=instance_data["port"],
                            status=ServiceStatus(instance_data["status"]),
                            cpu_usage=instance_data["cpu_usage"],
                            memory_usage=instance_data["memory_usage"],
                            active_connections=instance_data["active_connections"],
                            response_time=instance_data["response_time"],
                            last_health_check=instance_data["last_health_check"],
                            created_at=instance_data["created_at"],
                            metadata=instance_data.get("metadata", {})
                        )
                        self.service_instances[instance_id] = instance
                
                # Load scaling rules
                rules_data = self.redis_client.get("frenly_scaling_rules")
                if rules_data:
                    rules_json = json.loads(rules_data)
                    for rule_id, rule_data in rules_json.items():
                        rule = ScalingRule(
                            id=rule_id,
                            service_name=rule_data["service_name"],
                            metric_name=rule_data["metric_name"],
                            threshold=rule_data["threshold"],
                            scale_up_threshold=rule_data["scale_up_threshold"],
                            scale_down_threshold=rule_data["scale_down_threshold"],
                            min_instances=rule_data["min_instances"],
                            max_instances=rule_data["max_instances"],
                            scale_up_cooldown=rule_data["scale_up_cooldown"],
                            scale_down_cooldown=rule_data["scale_down_cooldown"],
                            enabled=rule_data.get("enabled", True),
                            created_at=rule_data["created_at"]
                        )
                        self.scaling_rules[rule_id] = rule
                
                # Load scaling events
                events_data = self.redis_client.get("frenly_scaling_events")
                if events_data:
                    events_json = json.loads(events_data)
                    for event_data in events_json:
                        event = ScalingEvent(
                            id=event_data["id"],
                            service_name=event_data["service_name"],
                            action=ScalingAction(event_data["action"]),
                            instances_before=event_data["instances_before"],
                            instances_after=event_data["instances_after"],
                            reason=event_data["reason"],
                            timestamp=event_data["timestamp"],
                            duration=event_data.get("duration"),
                            success=event_data.get("success", True)
                        )
                        self.scaling_events.append(event)
                
                logger.info(f"Loaded {len(self.service_instances)} instances, {len(self.scaling_rules)} rules, {len(self.scaling_events)} events")
            
        except Exception as e:
            logger.error(f"❌ Error loading scaling data: {e}")
    
    async def _save_scaling_data(self):
        """Save scaling data to storage"""
        try:
            if self.redis_client:
                # Save service instances
                instances_data = {
                    instance_id: {
                        "service_name": instance.service_name,
                        "host": instance.host,
                        "port": instance.port,
                        "status": instance.status.value,
                        "cpu_usage": instance.cpu_usage,
                        "memory_usage": instance.memory_usage,
                        "active_connections": instance.active_connections,
                        "response_time": instance.response_time,
                        "last_health_check": instance.last_health_check,
                        "created_at": instance.created_at,
                        "metadata": instance.metadata
                    }
                    for instance_id, instance in self.service_instances.items()
                }
                self.redis_client.setex("frenly_scaling_instances", 86400, json.dumps(instances_data))
                
                # Save scaling rules
                rules_data = {
                    rule_id: {
                        "service_name": rule.service_name,
                        "metric_name": rule.metric_name,
                        "threshold": rule.threshold,
                        "scale_up_threshold": rule.scale_up_threshold,
                        "scale_down_threshold": rule.scale_down_threshold,
                        "min_instances": rule.min_instances,
                        "max_instances": rule.max_instances,
                        "scale_up_cooldown": rule.scale_up_cooldown,
                        "scale_down_cooldown": rule.scale_down_cooldown,
                        "enabled": rule.enabled,
                        "created_at": rule.created_at
                    }
                    for rule_id, rule in self.scaling_rules.items()
                }
                self.redis_client.setex("frenly_scaling_rules", 86400, json.dumps(rules_data))
                
                # Save scaling events
                events_data = [
                    {
                        "id": event.id,
                        "service_name": event.service_name,
                        "action": event.action.value,
                        "instances_before": event.instances_before,
                        "instances_after": event.instances_after,
                        "reason": event.reason,
                        "timestamp": event.timestamp,
                        "duration": event.duration,
                        "success": event.success
                    }
                    for event in self.scaling_events
                ]
                self.redis_client.setex("frenly_scaling_events", 86400, json.dumps(events_data))
            
        except Exception as e:
            logger.error(f"❌ Error saving scaling data: {e}")

# Global horizontal scaling system instance
horizontal_scaling = HorizontalScalingSystem()

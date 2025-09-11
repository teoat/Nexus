#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔄 Frenly AI Failover System
Comprehensive failover and disaster recovery for Frenly AI
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

class FailoverType(Enum):
    """Failover type enumeration"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EMERGENCY = "emergency"

class FailoverStatus(Enum):
    """Failover status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLBACK = "rollback"

class ServiceType(Enum):
    """Service type enumeration"""
    DATABASE = "database"
    CACHE = "cache"
    API = "api"
    WORKER = "worker"
    SCHEDULER = "scheduler"
    MONITORING = "monitoring"

class HealthStatus(Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class ServiceInstance:
    """Service instance definition"""
    id: str
    name: str
    service_type: ServiceType
    host: str
    port: int
    health_status: HealthStatus
    priority: int
    weight: float
    last_health_check: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class FailoverGroup:
    """Failover group definition"""
    id: str
    name: str
    service_type: ServiceType
    primary_instance: str
    secondary_instances: List[str]
    failover_type: FailoverType
    health_check_interval: int  # seconds
    failover_threshold: int  # consecutive failures
    recovery_timeout: int  # seconds
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class FailoverEvent:
    """Failover event definition"""
    id: str
    group_id: str
    failover_type: FailoverType
    status: FailoverStatus
    from_instance: str
    to_instance: str
    reason: str
    started_at: str
    completed_at: Optional[str] = None
    duration: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HealthCheck:
    """Health check definition"""
    id: str
    instance_id: str
    check_type: str
    endpoint: str
    timeout: int
    interval: int
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

class FailoverSystem:
    """Failover system for Frenly AI"""
    
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
        
        # Failover storage
        self.service_instances: Dict[str, ServiceInstance] = {}
        self.failover_groups: Dict[str, FailoverGroup] = {}
        self.failover_events: List[FailoverEvent] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        
        # Configuration
        self.health_check_interval = 10  # seconds
        self.failover_evaluation_interval = 30  # seconds
        self.max_failover_events = 1000
        self.health_check_timeout = 5  # seconds
        
        # Health tracking
        self.health_failures: Dict[str, int] = {}
        
        logger.info("✅ Failover System initialized")
    
    async def start(self):
        """Start the failover system"""
        self.running = True
        logger.info("🚀 Starting Failover System...")
        
        # Load existing data
        await self._load_failover_data()
        
        # Start background tasks
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._failover_evaluation_loop())
        asyncio.create_task(self._cleanup_old_events())
        
        logger.info("✅ Failover System started")
    
    async def stop(self):
        """Stop the failover system"""
        self.running = False
        logger.info("🛑 Stopping Failover System...")
        
        # Save failover data
        await self._save_failover_data()
        
        logger.info("✅ Failover System stopped")
    
    async def register_service_instance(
        self,
        name: str,
        service_type: ServiceType,
        host: str,
        port: int,
        priority: int = 1,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register a new service instance"""
        try:
            instance_id = f"instance_{int(time.time())}"
            
            instance = ServiceInstance(
                id=instance_id,
                name=name,
                service_type=service_type,
                host=host,
                port=port,
                health_status=HealthStatus.UNKNOWN,
                priority=priority,
                weight=weight,
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
            
            # Check if instance is part of any failover group
            for group in self.failover_groups.values():
                if instance_id == group.primary_instance or instance_id in group.secondary_instances:
                    logger.warning(f"Cannot unregister instance {instance_id} - it's part of failover group {group.id}")
                    return False
            
            del self.service_instances[instance_id]
            
            # Remove health failures tracking
            if instance_id in self.health_failures:
                del self.health_failures[instance_id]
            
            logger.info(f"Service instance unregistered: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error unregistering service instance {instance_id}: {e}")
            return False
    
    async def get_service_instance(self, instance_id: str) -> Optional[ServiceInstance]:
        """Get service instance information"""
        return self.service_instances.get(instance_id)
    
    async def list_service_instances(self, service_type: Optional[ServiceType] = None) -> List[ServiceInstance]:
        """List service instances with optional type filter"""
        instances = list(self.service_instances.values())
        
        if service_type:
            instances = [i for i in instances if i.service_type == service_type]
        
        return instances
    
    async def create_failover_group(
        self,
        name: str,
        service_type: ServiceType,
        primary_instance: str,
        secondary_instances: List[str],
        failover_type: FailoverType = FailoverType.AUTOMATIC,
        health_check_interval: int = 10,
        failover_threshold: int = 3,
        recovery_timeout: int = 300
    ) -> str:
        """Create a new failover group"""
        try:
            # Validate primary instance
            if primary_instance not in self.service_instances:
                raise ValueError("Primary instance not found")
            
            primary = self.service_instances[primary_instance]
            if primary.service_type != service_type:
                raise ValueError("Primary instance service type mismatch")
            
            # Validate secondary instances
            for secondary_id in secondary_instances:
                if secondary_id not in self.service_instances:
                    raise ValueError(f"Secondary instance {secondary_id} not found")
                
                secondary = self.service_instances[secondary_id]
                if secondary.service_type != service_type:
                    raise ValueError(f"Secondary instance {secondary_id} service type mismatch")
            
            group_id = f"group_{int(time.time())}"
            
            group = FailoverGroup(
                id=group_id,
                name=name,
                service_type=service_type,
                primary_instance=primary_instance,
                secondary_instances=secondary_instances,
                failover_type=failover_type,
                health_check_interval=health_check_interval,
                failover_threshold=failover_threshold,
                recovery_timeout=recovery_timeout
            )
            
            self.failover_groups[group_id] = group
            
            logger.info(f"Failover group created: {group_id}")
            return group_id
            
        except Exception as e:
            logger.error(f"❌ Error creating failover group: {e}")
            raise
    
    async def get_failover_group(self, group_id: str) -> Optional[FailoverGroup]:
        """Get failover group information"""
        return self.failover_groups.get(group_id)
    
    async def list_failover_groups(self) -> List[FailoverGroup]:
        """List all failover groups"""
        return list(self.failover_groups.values())
    
    async def update_failover_group(self, group_id: str, **updates) -> bool:
        """Update a failover group"""
        try:
            if group_id not in self.failover_groups:
                logger.warning(f"Failover group not found: {group_id}")
                return False
            
            group = self.failover_groups[group_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(group, key):
                    setattr(group, key, value)
            
            group.updated_at = datetime.now().isoformat()
            
            logger.info(f"Failover group updated: {group_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating failover group {group_id}: {e}")
            return False
    
    async def delete_failover_group(self, group_id: str) -> bool:
        """Delete a failover group"""
        try:
            if group_id not in self.failover_groups:
                logger.warning(f"Failover group not found: {group_id}")
                return False
            
            del self.failover_groups[group_id]
            
            logger.info(f"Failover group deleted: {group_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting failover group {group_id}: {e}")
            return False
    
    async def create_health_check(
        self,
        instance_id: str,
        check_type: str,
        endpoint: str,
        timeout: int = 5,
        interval: int = 10
    ) -> str:
        """Create a health check for an instance"""
        try:
            if instance_id not in self.service_instances:
                raise ValueError("Service instance not found")
            
            check_id = f"check_{int(time.time())}"
            
            health_check = HealthCheck(
                id=check_id,
                instance_id=instance_id,
                check_type=check_type,
                endpoint=endpoint,
                timeout=timeout,
                interval=interval
            )
            
            self.health_checks[check_id] = health_check
            
            logger.info(f"Health check created: {check_id}")
            return check_id
            
        except Exception as e:
            logger.error(f"❌ Error creating health check: {e}")
            raise
    
    async def get_health_check(self, check_id: str) -> Optional[HealthCheck]:
        """Get health check information"""
        return self.health_checks.get(check_id)
    
    async def list_health_checks(self, instance_id: Optional[str] = None) -> List[HealthCheck]:
        """List health checks with optional instance filter"""
        checks = list(self.health_checks.values())
        
        if instance_id:
            checks = [c for c in checks if c.instance_id == instance_id]
        
        return checks
    
    async def trigger_failover(self, group_id: str, failover_type: FailoverType = FailoverType.MANUAL) -> str:
        """Manually trigger a failover"""
        try:
            if group_id not in self.failover_groups:
                raise ValueError("Failover group not found")
            
            group = self.failover_groups[group_id]
            
            # Find the best secondary instance
            best_secondary = await self._find_best_secondary_instance(group)
            if not best_secondary:
                raise ValueError("No suitable secondary instance found")
            
            # Create failover event
            event_id = f"failover_{int(time.time())}"
            
            event = FailoverEvent(
                id=event_id,
                group_id=group_id,
                failover_type=failover_type,
                status=FailoverStatus.PENDING,
                from_instance=group.primary_instance,
                to_instance=best_secondary.id,
                reason="Manual failover triggered",
                started_at=datetime.now().isoformat()
            )
            
            self.failover_events[event_id] = event
            
            # Execute failover
            await self._execute_failover(event)
            
            logger.info(f"Failover triggered: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"❌ Error triggering failover: {e}")
            raise
    
    async def get_failover_event(self, event_id: str) -> Optional[FailoverEvent]:
        """Get failover event information"""
        return self.failover_events.get(event_id)
    
    async def list_failover_events(self, group_id: Optional[str] = None, limit: int = 100) -> List[FailoverEvent]:
        """List failover events with optional group filter"""
        events = list(self.failover_events.values())
        
        if group_id:
            events = [e for e in events if e.group_id == group_id]
        
        # Sort by started_at descending
        events.sort(key=lambda e: e.started_at, reverse=True)
        
        return events[:limit]
    
    async def get_failover_analytics(self) -> Dict[str, Any]:
        """Get failover system analytics"""
        try:
            total_instances = len(self.service_instances)
            healthy_instances = len([i for i in self.service_instances.values() if i.health_status == HealthStatus.HEALTHY])
            unhealthy_instances = len([i for i in self.service_instances.values() if i.health_status == HealthStatus.UNHEALTHY])
            critical_instances = len([i for i in self.service_instances.values() if i.health_status == HealthStatus.CRITICAL])
            
            total_groups = len(self.failover_groups)
            enabled_groups = len([g for g in self.failover_groups.values() if g.enabled])
            
            total_events = len(self.failover_events)
            successful_events = len([e for e in self.failover_events.values() if e.success])
            failed_events = len([e for e in self.failover_events.values() if not e.success])
            
            # Recent activity
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_events = [
                e for e in self.failover_events.values()
                if datetime.fromisoformat(e.started_at) > recent_cutoff
            ]
            
            # Service type distribution
            service_distribution = {}
            for instance in self.service_instances.values():
                service_type = instance.service_type.value
                service_distribution[service_type] = service_distribution.get(service_type, 0) + 1
            
            # Health status distribution
            health_distribution = {}
            for instance in self.service_instances.values():
                health_status = instance.health_status.value
                health_distribution[health_status] = health_distribution.get(health_status, 0) + 1
            
            return {
                "instances": {
                    "total": total_instances,
                    "healthy": healthy_instances,
                    "unhealthy": unhealthy_instances,
                    "critical": critical_instances,
                    "health_rate": healthy_instances / total_instances if total_instances > 0 else 0
                },
                "groups": {
                    "total": total_groups,
                    "enabled": enabled_groups
                },
                "events": {
                    "total": total_events,
                    "successful": successful_events,
                    "failed": failed_events,
                    "success_rate": successful_events / total_events if total_events > 0 else 0,
                    "recent": len(recent_events)
                },
                "service_distribution": service_distribution,
                "health_distribution": health_distribution,
                "health_checks": {
                    "total": len(self.health_checks),
                    "enabled": len([c for c in self.health_checks.values() if c.enabled])
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting failover analytics: {e}")
            return {"error": str(e)}
    
    async def _health_check_loop(self):
        """Health check loop for all instances"""
        while self.running:
            try:
                for instance in self.service_instances.values():
                    await self._perform_health_check(instance)
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in health check loop: {e}")
                await asyncio.sleep(60)
    
    async def _perform_health_check(self, instance: ServiceInstance):
        """Perform health check on an instance"""
        try:
            # Get health checks for this instance
            instance_checks = [c for c in self.health_checks.values() if c.instance_id == instance.id and c.enabled]
            
            if not instance_checks:
                # No health checks configured, assume healthy
                instance.health_status = HealthStatus.HEALTHY
                instance.last_health_check = datetime.now().isoformat()
                return
            
            # Perform all health checks
            all_healthy = True
            for check in instance_checks:
                is_healthy = await self._execute_health_check(check)
                if not is_healthy:
                    all_healthy = False
                    break
            
            # Update instance health status
            if all_healthy:
                if instance.health_status != HealthStatus.HEALTHY:
                    instance.health_status = HealthStatus.HEALTHY
                    # Reset failure count
                    if instance.id in self.health_failures:
                        del self.health_failures[instance.id]
            else:
                # Increment failure count
                self.health_failures[instance.id] = self.health_failures.get(instance.id, 0) + 1
                
                # Update health status based on failure count
                failure_count = self.health_failures[instance.id]
                if failure_count >= 5:
                    instance.health_status = HealthStatus.CRITICAL
                elif failure_count >= 3:
                    instance.health_status = HealthStatus.UNHEALTHY
                else:
                    instance.health_status = HealthStatus.DEGRADED
            
            instance.last_health_check = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"❌ Error performing health check on {instance.id}: {e}")
            instance.health_status = HealthStatus.UNKNOWN
    
    async def _execute_health_check(self, check: HealthCheck) -> bool:
        try:
            # In practice, this would make actual HTTP requests or other checks
            
            if check.check_type == "http":
                success_rate = 0.95  # 95% success rate
            elif check.check_type == "tcp":
                success_rate = 0.98  # 98% success rate
            elif check.check_type == "ping":
                success_rate = 0.99  # 99% success rate
            else:
                success_rate = 0.90  # Default 90% success rate
            
            import random
            return random.random() < success_rate
            
        except Exception as e:
            logger.error(f"❌ Error executing health check {check.id}: {e}")
            return False
    
    async def _failover_evaluation_loop(self):
        """Failover evaluation loop"""
        while self.running:
            try:
                for group in self.failover_groups.values():
                    if not group.enabled:
                        continue
                    
                    await self._evaluate_failover_group(group)
                
                await asyncio.sleep(self.failover_evaluation_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in failover evaluation loop: {e}")
                await asyncio.sleep(60)
    
    async def _evaluate_failover_group(self, group: FailoverGroup):
        """Evaluate a failover group for potential failover"""
        try:
            # Check if failover is automatic
            if group.failover_type != FailoverType.AUTOMATIC:
                return
            
            # Get primary instance
            primary = self.service_instances.get(group.primary_instance)
            if not primary:
                return
            
            # Check if primary is healthy
            if primary.health_status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]:
                return
            
            # Check failure threshold
            failure_count = self.health_failures.get(group.primary_instance, 0)
            if failure_count < group.failover_threshold:
                return
            
            # Trigger automatic failover
            await self._trigger_automatic_failover(group)
            
        except Exception as e:
            logger.error(f"❌ Error evaluating failover group {group.id}: {e}")
    
    async def _trigger_automatic_failover(self, group: FailoverGroup):
        """Trigger automatic failover for a group"""
        try:
            # Find the best secondary instance
            best_secondary = await self._find_best_secondary_instance(group)
            if not best_secondary:
                logger.warning(f"No suitable secondary instance found for group {group.id}")
                return
            
            # Create failover event
            event_id = f"failover_{int(time.time())}"
            
            event = FailoverEvent(
                id=event_id,
                group_id=group.id,
                failover_type=FailoverType.AUTOMATIC,
                status=FailoverStatus.PENDING,
                from_instance=group.primary_instance,
                to_instance=best_secondary.id,
                reason=f"Primary instance unhealthy (failures: {self.health_failures.get(group.primary_instance, 0)})",
                started_at=datetime.now().isoformat()
            )
            
            self.failover_events[event_id] = event
            
            # Execute failover
            await self._execute_failover(event)
            
            logger.warning(f"Automatic failover triggered: {event_id}")
            
        except Exception as e:
            logger.error(f"❌ Error triggering automatic failover: {e}")
    
    async def _find_best_secondary_instance(self, group: FailoverGroup) -> Optional[ServiceInstance]:
        """Find the best secondary instance for failover"""
        try:
            best_instance = None
            best_score = -1
            
            for secondary_id in group.secondary_instances:
                secondary = self.service_instances.get(secondary_id)
                if not secondary or secondary.health_status != HealthStatus.HEALTHY:
                    continue
                
                # Calculate score based on priority and weight
                score = secondary.priority * secondary.weight
                
                if score > best_score:
                    best_score = score
                    best_instance = secondary
            
            return best_instance
            
        except Exception as e:
            logger.error(f"❌ Error finding best secondary instance: {e}")
            return None
    
    async def _execute_failover(self, event: FailoverEvent):
        """Execute a failover event"""
        try:
            event.status = FailoverStatus.IN_PROGRESS
            
            # Get failover group
            group = self.failover_groups.get(event.group_id)
            if not group:
                event.status = FailoverStatus.FAILED
                event.error_message = "Failover group not found"
                return
            
            # In practice, this would:
            # 1. Stop traffic to primary instance
            # 2. Promote secondary instance to primary
            # 3. Update load balancer configuration
            # 4. Verify new primary is working
            # 5. Update DNS/configuration
            
            start_time = time.time()
            
            
            # Update failover group
            group.primary_instance = event.to_instance
            group.secondary_instances = [i for i in group.secondary_instances if i != event.to_instance]
            group.secondary_instances.append(event.from_instance)
            
            # Update instance roles
            old_primary = self.service_instances[event.from_instance]
            new_primary = self.service_instances[event.to_instance]
            
            # Reset health failures for new primary
            if event.to_instance in self.health_failures:
                del self.health_failures[event.to_instance]
            
            # Mark as completed
            event.status = FailoverStatus.COMPLETED
            event.completed_at = datetime.now().isoformat()
            event.duration = int((time.time() - start_time) * 1000)  # milliseconds
            event.success = True
            
            logger.info(f"Failover completed: {event.id} - {old_primary.name} -> {new_primary.name}")
            
        except Exception as e:
            logger.error(f"❌ Error executing failover {event.id}: {e}")
            event.status = FailoverStatus.FAILED
            event.error_message = str(e)
            event.completed_at = datetime.now().isoformat()
            event.success = False
    
    async def _cleanup_old_events(self):
        """Clean up old failover events"""
        while self.running:
            try:
                # Keep only recent events
                if len(self.failover_events) > self.max_failover_events:
                    # Sort by started_at and keep only recent ones
                    sorted_events = sorted(
                        self.failover_events.items(),
                        key=lambda x: x[1].started_at,
                        reverse=True
                    )
                    
                    # Keep only the most recent events
                    events_to_keep = dict(sorted_events[:self.max_failover_events])
                    self.failover_events = events_to_keep
                
                await asyncio.sleep(86400)  # Clean up daily
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up old events: {e}")
                await asyncio.sleep(3600)
    
    async def _load_failover_data(self):
        """Load failover data from storage"""
        try:
            if self.redis_client:
                # Load service instances
                instances_data = self.redis_client.get("frenly_failover_instances")
                if instances_data:
                    instances_json = json.loads(instances_data)
                    for instance_id, instance_data in instances_json.items():
                        instance = ServiceInstance(
                            id=instance_id,
                            name=instance_data["name"],
                            service_type=ServiceType(instance_data["service_type"]),
                            host=instance_data["host"],
                            port=instance_data["port"],
                            health_status=HealthStatus(instance_data["health_status"]),
                            priority=instance_data["priority"],
                            weight=instance_data["weight"],
                            last_health_check=instance_data["last_health_check"],
                            metadata=instance_data.get("metadata", {}),
                            created_at=instance_data["created_at"]
                        )
                        self.service_instances[instance_id] = instance
                
                # Load failover groups
                groups_data = self.redis_client.get("frenly_failover_groups")
                if groups_data:
                    groups_json = json.loads(groups_data)
                    for group_id, group_data in groups_json.items():
                        group = FailoverGroup(
                            id=group_id,
                            name=group_data["name"],
                            service_type=ServiceType(group_data["service_type"]),
                            primary_instance=group_data["primary_instance"],
                            secondary_instances=group_data["secondary_instances"],
                            failover_type=FailoverType(group_data["failover_type"]),
                            health_check_interval=group_data["health_check_interval"],
                            failover_threshold=group_data["failover_threshold"],
                            recovery_timeout=group_data["recovery_timeout"],
                            enabled=group_data.get("enabled", True),
                            created_at=group_data["created_at"],
                            updated_at=group_data["updated_at"]
                        )
                        self.failover_groups[group_id] = group
                
                # Load failover events
                events_data = self.redis_client.get("frenly_failover_events")
                if events_data:
                    events_json = json.loads(events_data)
                    for event_id, event_data in events_json.items():
                        event = FailoverEvent(
                            id=event_id,
                            group_id=event_data["group_id"],
                            failover_type=FailoverType(event_data["failover_type"]),
                            status=FailoverStatus(event_data["status"]),
                            from_instance=event_data["from_instance"],
                            to_instance=event_data["to_instance"],
                            reason=event_data["reason"],
                            started_at=event_data["started_at"],
                            completed_at=event_data.get("completed_at"),
                            duration=event_data.get("duration"),
                            success=event_data.get("success", True),
                            error_message=event_data.get("error_message"),
                            metadata=event_data.get("metadata", {})
                        )
                        self.failover_events[event_id] = event
                
                # Load health checks
                checks_data = self.redis_client.get("frenly_health_checks")
                if checks_data:
                    checks_json = json.loads(checks_data)
                    for check_id, check_data in checks_json.items():
                        check = HealthCheck(
                            id=check_id,
                            instance_id=check_data["instance_id"],
                            check_type=check_data["check_type"],
                            endpoint=check_data["endpoint"],
                            timeout=check_data["timeout"],
                            interval=check_data["interval"],
                            enabled=check_data.get("enabled", True),
                            created_at=check_data["created_at"]
                        )
                        self.health_checks[check_id] = check
                
                logger.info(f"Loaded {len(self.service_instances)} instances, {len(self.failover_groups)} groups, {len(self.failover_events)} events, {len(self.health_checks)} health checks")
            
        except Exception as e:
            logger.error(f"❌ Error loading failover data: {e}")
    
    async def _save_failover_data(self):
        """Save failover data to storage"""
        try:
            if self.redis_client:
                # Save service instances
                instances_data = {
                    instance_id: {
                        "name": instance.name,
                        "service_type": instance.service_type.value,
                        "host": instance.host,
                        "port": instance.port,
                        "health_status": instance.health_status.value,
                        "priority": instance.priority,
                        "weight": instance.weight,
                        "last_health_check": instance.last_health_check,
                        "metadata": instance.metadata,
                        "created_at": instance.created_at
                    }
                    for instance_id, instance in self.service_instances.items()
                }
                self.redis_client.setex("frenly_failover_instances", 86400, json.dumps(instances_data))
                
                # Save failover groups
                groups_data = {
                    group_id: {
                        "name": group.name,
                        "service_type": group.service_type.value,
                        "primary_instance": group.primary_instance,
                        "secondary_instances": group.secondary_instances,
                        "failover_type": group.failover_type.value,
                        "health_check_interval": group.health_check_interval,
                        "failover_threshold": group.failover_threshold,
                        "recovery_timeout": group.recovery_timeout,
                        "enabled": group.enabled,
                        "created_at": group.created_at,
                        "updated_at": group.updated_at
                    }
                    for group_id, group in self.failover_groups.items()
                }
                self.redis_client.setex("frenly_failover_groups", 86400, json.dumps(groups_data))
                
                # Save failover events
                events_data = {
                    event_id: {
                        "group_id": event.group_id,
                        "failover_type": event.failover_type.value,
                        "status": event.status.value,
                        "from_instance": event.from_instance,
                        "to_instance": event.to_instance,
                        "reason": event.reason,
                        "started_at": event.started_at,
                        "completed_at": event.completed_at,
                        "duration": event.duration,
                        "success": event.success,
                        "error_message": event.error_message,
                        "metadata": event.metadata
                    }
                    for event_id, event in self.failover_events.items()
                }
                self.redis_client.setex("frenly_failover_events", 86400, json.dumps(events_data))
                
                # Save health checks
                checks_data = {
                    check_id: {
                        "instance_id": check.instance_id,
                        "check_type": check.check_type,
                        "endpoint": check.endpoint,
                        "timeout": check.timeout,
                        "interval": check.interval,
                        "enabled": check.enabled,
                        "created_at": check.created_at
                    }
                    for check_id, check in self.health_checks.items()
                }
                self.redis_client.setex("frenly_health_checks", 86400, json.dumps(checks_data))
            
        except Exception as e:
            logger.error(f"❌ Error saving failover data: {e}")

# Global failover system instance
failover_system = FailoverSystem()

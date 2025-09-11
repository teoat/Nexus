#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔗 Frenly AI Webhook System
Webhook management for external integrations
"""

import asyncio
import logging
import time
import json
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class WebhookStatus(Enum):
    """Webhook status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    SUSPENDED = "suspended"

class WebhookEvent(Enum):
    """Webhook event types"""
    AGENT_CREATED = "agent.created"
    AGENT_UPDATED = "agent.updated"
    AGENT_DELETED = "agent.deleted"
    AGENT_STARTED = "agent.started"
    AGENT_STOPPED = "agent.stopped"
    AGENT_ERROR = "agent.error"
    TASK_CREATED = "task.created"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    ALERT_TRIGGERED = "alert.triggered"
    METRIC_UPDATED = "metric.updated"
    SYSTEM_HEALTH = "system.health"
    CUSTOM = "custom"

class WebhookMethod(Enum):
    """HTTP methods for webhooks"""
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"

@dataclass
class Webhook:
    """Webhook definition"""
    id: str
    name: str
    url: str
    events: List[WebhookEvent]
    method: WebhookMethod = WebhookMethod.POST
    status: WebhookStatus = WebhookStatus.ACTIVE
    secret: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry_count: int = 3
    retry_delay: int = 5
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_triggered: Optional[str] = None
    success_count: int = 0
    failure_count: int = 0
    enabled: bool = True

@dataclass
class WebhookPayload:
    """Webhook payload structure"""
    event: str
    timestamp: str
    data: Dict[str, Any]
    webhook_id: str
    signature: Optional[str] = None

@dataclass
class WebhookDelivery:
    """Webhook delivery record"""
    id: str
    webhook_id: str
    event: str
    payload: Dict[str, Any]
    status: str
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    delivered_at: Optional[str] = None
    retry_count: int = 0

class WebhookSystem:
    """Webhook system for Frenly AI"""
    
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
        
        # Webhook storage
        self.webhooks: Dict[str, Webhook] = {}
        self.deliveries: List[WebhookDelivery] = []
        
        # Delivery queue
        self.delivery_queue = asyncio.Queue()
        self.max_deliveries = 1000
        
        # Rate limiting
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        self.max_requests_per_minute = 60
        
        logger.info("✅ Webhook System initialized")
    
    async def start(self):
        """Start the webhook system"""
        self.running = True
        logger.info("🚀 Starting Webhook System...")
        
        # Load existing webhooks
        await self._load_webhooks()
        
        # Start delivery workers
        for i in range(3):  # 3 delivery workers
            asyncio.create_task(self._delivery_worker(f"worker-{i}"))
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_deliveries())
        
        logger.info("✅ Webhook System started")
    
    async def stop(self):
        """Stop the webhook system"""
        self.running = False
        logger.info("🛑 Stopping Webhook System...")
        
        # Save webhook state
        await self._save_webhooks()
        
        logger.info("✅ Webhook System stopped")
    
    async def create_webhook(
        self,
        name: str,
        url: str,
        events: List[WebhookEvent],
        method: WebhookMethod = WebhookMethod.POST,
        secret: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        retry_count: int = 3,
        retry_delay: int = 5
    ) -> str:
        """Create a new webhook"""
        try:
            webhook_id = f"webhook_{int(time.time())}"
            
            webhook = Webhook(
                id=webhook_id,
                name=name,
                url=url,
                events=events,
                method=method,
                secret=secret,
                headers=headers or {},
                timeout=timeout,
                retry_count=retry_count,
                retry_delay=retry_delay
            )
            
            self.webhooks[webhook_id] = webhook
            
            logger.info(f"Webhook created: {webhook_id}")
            return webhook_id
            
        except Exception as e:
            logger.error(f"❌ Error creating webhook: {e}")
            raise
    
    async def update_webhook(
        self,
        webhook_id: str,
        **updates
    ) -> bool:
        """Update a webhook"""
        try:
            if webhook_id not in self.webhooks:
                logger.warning(f"Webhook not found: {webhook_id}")
                return False
            
            webhook = self.webhooks[webhook_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(webhook, key):
                    setattr(webhook, key, value)
            
            webhook.updated_at = datetime.now().isoformat()
            
            logger.info(f"Webhook updated: {webhook_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating webhook {webhook_id}: {e}")
            return False
    
    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook"""
        try:
            if webhook_id not in self.webhooks:
                logger.warning(f"Webhook not found: {webhook_id}")
                return False
            
            del self.webhooks[webhook_id]
            
            logger.info(f"Webhook deleted: {webhook_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting webhook {webhook_id}: {e}")
            return False
    
    async def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """Get webhook information"""
        return self.webhooks.get(webhook_id)
    
    async def list_webhooks(self, status: Optional[WebhookStatus] = None) -> List[Webhook]:
        """List all webhooks with optional status filter"""
        webhooks = list(self.webhooks.values())
        
        if status:
            webhooks = [w for w in webhooks if w.status == status]
        
        return webhooks
    
    async def trigger_webhook(
        self,
        event: WebhookEvent,
        data: Dict[str, Any],
        webhook_id: Optional[str] = None
    ) -> List[str]:
        """Trigger webhooks for an event"""
        try:
            triggered_webhooks = []
            
            # Find webhooks for this event
            target_webhooks = []
            
            if webhook_id:
                if webhook_id in self.webhooks:
                    webhook = self.webhooks[webhook_id]
                    if event in webhook.events and webhook.enabled:
                        target_webhooks.append(webhook)
            else:
                for webhook in self.webhooks.values():
                    if event in webhook.events and webhook.enabled:
                        target_webhooks.append(webhook)
            
            # Trigger each webhook
            for webhook in target_webhooks:
                try:
                    # Check rate limits
                    if not await self._check_rate_limit(webhook.id):
                        logger.warning(f"Rate limit exceeded for webhook {webhook.id}")
                        continue
                    
                    # Create payload
                    payload = WebhookPayload(
                        event=event.value,
                        timestamp=datetime.now().isoformat(),
                        data=data,
                        webhook_id=webhook.id
                    )
                    
                    # Add signature if secret is provided
                    if webhook.secret:
                        payload.signature = self._generate_signature(
                            webhook.secret,
                            json.dumps(payload.data, sort_keys=True)
                        )
                    
                    # Queue for delivery
                    await self.delivery_queue.put((webhook, payload))
                    triggered_webhooks.append(webhook.id)
                    
                except Exception as e:
                    logger.error(f"❌ Error triggering webhook {webhook.id}: {e}")
            
            return triggered_webhooks
            
        except Exception as e:
            logger.error(f"❌ Error triggering webhooks: {e}")
            return []
    
        try:
            if webhook_id not in self.webhooks:
                logger.warning(f"Webhook not found: {webhook_id}")
                return False
            
            webhook = self.webhooks[webhook_id]
            
            
            # Trigger webhook
            triggered = await self.trigger_webhook(
                WebhookEvent.CUSTOM,
                webhook_id
            )
            
            return webhook_id in triggered
            
        except Exception as e:
            return False
    
    async def get_webhook_analytics(self) -> Dict[str, Any]:
        """Get webhook system analytics"""
        try:
            total_webhooks = len(self.webhooks)
            active_webhooks = len([w for w in self.webhooks.values() if w.status == WebhookStatus.ACTIVE])
            inactive_webhooks = len([w for w in self.webhooks.values() if w.status == WebhookStatus.INACTIVE])
            error_webhooks = len([w for w in self.webhooks.values() if w.status == WebhookStatus.ERROR])
            
            # Event distribution
            event_distribution = {}
            for webhook in self.webhooks.values():
                for event in webhook.events:
                    event_distribution[event.value] = event_distribution.get(event.value, 0) + 1
            
            # Delivery statistics
            total_deliveries = len(self.deliveries)
            successful_deliveries = len([d for d in self.deliveries if d.status == "success"])
            failed_deliveries = len([d for d in self.deliveries if d.status == "failed"])
            
            # Recent activity
            recent_deliveries = [
                d for d in self.deliveries
                if d.delivered_at and datetime.fromisoformat(d.delivered_at) > datetime.now() - timedelta(hours=24)
            ]
            
            return {
                "total_webhooks": total_webhooks,
                "active_webhooks": active_webhooks,
                "inactive_webhooks": inactive_webhooks,
                "error_webhooks": error_webhooks,
                "event_distribution": event_distribution,
                "total_deliveries": total_deliveries,
                "successful_deliveries": successful_deliveries,
                "failed_deliveries": failed_deliveries,
                "recent_deliveries": len(recent_deliveries),
                "queue_size": self.delivery_queue.qsize(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting webhook analytics: {e}")
            return {"error": str(e)}
    
    async def _delivery_worker(self, worker_id: str):
        """Webhook delivery worker"""
        logger.info(f"Delivery worker {worker_id} started")
        
        while self.running:
            try:
                # Get webhook from queue
                webhook, payload = await asyncio.wait_for(
                    self.delivery_queue.get(),
                    timeout=1.0
                )
                
                # Deliver webhook
                await self._deliver_webhook(webhook, payload)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Error in delivery worker {worker_id}: {e}")
                await asyncio.sleep(1)
    
    async def _deliver_webhook(self, webhook: Webhook, payload: WebhookPayload):
        """Deliver a webhook"""
        try:
            delivery_id = f"delivery_{int(time.time())}_{webhook.id}"
            
            # Create delivery record
            delivery = WebhookDelivery(
                id=delivery_id,
                webhook_id=webhook.id,
                event=payload.event,
                payload=payload.data,
                status="pending"
            )
            
            self.deliveries.append(delivery)
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Frenly-AI-Webhook/1.0",
                "X-Webhook-Event": payload.event,
                "X-Webhook-ID": webhook.id,
                "X-Webhook-Timestamp": payload.timestamp
            }
            
            # Add custom headers
            headers.update(webhook.headers)
            
            # Add signature header
            if payload.signature:
                headers["X-Webhook-Signature"] = f"sha256={payload.signature}"
            
            # Prepare request data
            request_data = {
                "event": payload.event,
                "timestamp": payload.timestamp,
                "data": payload.data,
                "webhook_id": webhook.id
            }
            
            # Make HTTP request
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=webhook.timeout)) as session:
                async with session.request(
                    webhook.method.value,
                    webhook.url,
                    json=request_data,
                    headers=headers
                ) as response:
                    delivery.response_code = response.status
                    delivery.response_body = await response.text()
                    
                    if response.status >= 200 and response.status < 300:
                        delivery.status = "success"
                        webhook.success_count += 1
                        webhook.last_triggered = datetime.now().isoformat()
                    else:
                        delivery.status = "failed"
                        delivery.error_message = f"HTTP {response.status}"
                        webhook.failure_count += 1
                    
                    delivery.delivered_at = datetime.now().isoformat()
            
        except asyncio.TimeoutError:
            delivery.status = "failed"
            delivery.error_message = "Request timeout"
            webhook.failure_count += 1
            
        except Exception as e:
            delivery.status = "failed"
            delivery.error_message = str(e)
            webhook.failure_count += 1
            logger.error(f"❌ Error delivering webhook {webhook.id}: {e}")
        
        finally:
            # Update webhook status based on failure rate
            if webhook.failure_count > 0:
                failure_rate = webhook.failure_count / (webhook.success_count + webhook.failure_count)
                if failure_rate > 0.5:  # More than 50% failures
                    webhook.status = WebhookStatus.ERROR
                elif failure_rate > 0.2:  # More than 20% failures
                    webhook.status = WebhookStatus.SUSPENDED
    
    def _generate_signature(self, secret: str, payload: str) -> str:
        """Generate webhook signature"""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def _check_rate_limit(self, webhook_id: str) -> bool:
        """Check rate limit for webhook"""
        try:
            now = datetime.now()
            minute_key = now.strftime("%Y-%m-%d-%H-%M")
            rate_key = f"webhook_rate_{webhook_id}_{minute_key}"
            
            if webhook_id not in self.rate_limits:
                self.rate_limits[webhook_id] = {}
            
            if minute_key not in self.rate_limits[webhook_id]:
                self.rate_limits[webhook_id][minute_key] = 0
            
            current_count = self.rate_limits[webhook_id][minute_key]
            
            if current_count >= self.max_requests_per_minute:
                return False
            
            self.rate_limits[webhook_id][minute_key] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking rate limit: {e}")
            return True  # Allow on error
    
    async def _cleanup_deliveries(self):
        """Clean up old delivery records"""
        while self.running:
            try:
                # Keep only last 1000 deliveries
                if len(self.deliveries) > self.max_deliveries:
                    self.deliveries = self.deliveries[-self.max_deliveries:]
                
                # Clean up old rate limit data
                now = datetime.now()
                for webhook_id in list(self.rate_limits.keys()):
                    for minute_key in list(self.rate_limits[webhook_id].keys()):
                        try:
                            minute_time = datetime.strptime(minute_key, "%Y-%m-%d-%H-%M")
                            if now - minute_time > timedelta(hours=1):
                                del self.rate_limits[webhook_id][minute_key]
                        except:
                            del self.rate_limits[webhook_id][minute_key]
                    
                    if not self.rate_limits[webhook_id]:
                        del self.rate_limits[webhook_id]
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up deliveries: {e}")
                await asyncio.sleep(60)
    
    async def _load_webhooks(self):
        """Load webhooks from storage"""
        try:
            if self.redis_client:
                data = self.redis_client.get("frenly_webhooks")
                if data:
                    webhooks_data = json.loads(data)
                    
                    for webhook_id, webhook_data in webhooks_data.items():
                        webhook = Webhook(
                            id=webhook_id,
                            name=webhook_data["name"],
                            url=webhook_data["url"],
                            events=[WebhookEvent(e) for e in webhook_data["events"]],
                            method=WebhookMethod(webhook_data["method"]),
                            status=WebhookStatus(webhook_data["status"]),
                            secret=webhook_data.get("secret"),
                            headers=webhook_data.get("headers", {}),
                            timeout=webhook_data.get("timeout", 30),
                            retry_count=webhook_data.get("retry_count", 3),
                            retry_delay=webhook_data.get("retry_delay", 5),
                            created_at=webhook_data["created_at"],
                            updated_at=webhook_data["updated_at"],
                            last_triggered=webhook_data.get("last_triggered"),
                            success_count=webhook_data.get("success_count", 0),
                            failure_count=webhook_data.get("failure_count", 0),
                            enabled=webhook_data.get("enabled", True)
                        )
                        
                        self.webhooks[webhook_id] = webhook
                    
                    logger.info(f"Loaded {len(self.webhooks)} webhooks")
            
        except Exception as e:
            logger.error(f"❌ Error loading webhooks: {e}")
    
    async def _save_webhooks(self):
        """Save webhooks to storage"""
        try:
            if self.redis_client:
                webhooks_data = {
                    webhook_id: {
                        "name": webhook.name,
                        "url": webhook.url,
                        "events": [e.value for e in webhook.events],
                        "method": webhook.method.value,
                        "status": webhook.status.value,
                        "secret": webhook.secret,
                        "headers": webhook.headers,
                        "timeout": webhook.timeout,
                        "retry_count": webhook.retry_count,
                        "retry_delay": webhook.retry_delay,
                        "created_at": webhook.created_at,
                        "updated_at": webhook.updated_at,
                        "last_triggered": webhook.last_triggered,
                        "success_count": webhook.success_count,
                        "failure_count": webhook.failure_count,
                        "enabled": webhook.enabled
                    }
                    for webhook_id, webhook in self.webhooks.items()
                }
                
                self.redis_client.setex(
                    "frenly_webhooks",
                    86400,  # 24 hours TTL
                    json.dumps(webhooks_data, default=str)
                )
            
        except Exception as e:
            logger.error(f"❌ Error saving webhooks: {e}")

# Global webhook system instance
webhook_system = WebhookSystem()

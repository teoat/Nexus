#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🏢 Frenly AI Multi-tenancy System
Advanced multi-tenancy capabilities for Frenly AI
"""

import asyncio
import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class TenantStatus(Enum):
    """Tenant status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    EXPIRED = "expired"

class TenantTier(Enum):
    """Tenant tier enumeration"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class ResourceType(Enum):
    """Resource type enumeration"""
    COMPUTE = "compute"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"
    API_CALLS = "api_calls"
    USERS = "users"
    PROJECTS = "projects"
    FEATURES = "features"

class BillingCycle(Enum):
    """Billing cycle enumeration"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

@dataclass
class Tenant:
    """Tenant definition"""
    id: str
    name: str
    domain: str
    tier: TenantTier
    status: TenantStatus
    owner_id: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TenantResource:
    """Tenant resource definition"""
    id: str
    tenant_id: str
    resource_type: ResourceType
    allocated: float
    used: float
    limit: float
    unit: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class TenantUser:
    """Tenant user definition"""
    id: str
    tenant_id: str
    user_id: str
    role: str
    permissions: List[str]
    joined_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_active: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class TenantConfiguration:
    """Tenant configuration definition"""
    id: str
    tenant_id: str
    key: str
    value: Any
    data_type: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class TenantBilling:
    """Tenant billing definition"""
    id: str
    tenant_id: str
    tier: TenantTier
    billing_cycle: BillingCycle
    amount: float
    currency: str
    due_date: str
    paid: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class TenantUsage:
    """Tenant usage definition"""
    id: str
    tenant_id: str
    resource_type: ResourceType
    usage: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class MultiTenancySystem:
    """Multi-tenancy System for Frenly AI"""
    
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
        
        # Multi-tenancy storage
        self.tenants: Dict[str, Tenant] = {}
        self.tenant_resources: Dict[str, TenantResource] = {}
        self.tenant_users: Dict[str, TenantUser] = {}
        self.tenant_configurations: Dict[str, TenantConfiguration] = {}
        self.tenant_billing: Dict[str, TenantBilling] = {}
        self.tenant_usage: Dict[str, TenantUsage] = {}
        
        # Configuration
        self.usage_retention_days = 90
        self.billing_retention_days = 365
        self.resource_check_interval = 3600  # 1 hour
        
        # Tier configurations
        self._initialize_tier_configurations()
        
        logger.info("✅ Multi-tenancy System initialized")
    
    def _initialize_tier_configurations(self):
        """Initialize tier configurations"""
        try:
            self.tier_configs = {
                TenantTier.FREE: {
                    "max_users": 5,
                    "max_projects": 3,
                    "max_storage_gb": 1,
                    "max_api_calls_per_month": 1000,
                    "max_compute_hours_per_month": 10,
                    "features": ["basic_ai", "basic_analytics"]
                },
                TenantTier.BASIC: {
                    "max_users": 25,
                    "max_projects": 10,
                    "max_storage_gb": 10,
                    "max_api_calls_per_month": 10000,
                    "max_compute_hours_per_month": 100,
                    "features": ["basic_ai", "advanced_analytics", "api_access"]
                },
                TenantTier.PROFESSIONAL: {
                    "max_users": 100,
                    "max_projects": 50,
                    "max_storage_gb": 100,
                    "max_api_calls_per_month": 100000,
                    "max_compute_hours_per_month": 1000,
                    "features": ["advanced_ai", "advanced_analytics", "api_access", "custom_models", "priority_support"]
                },
                TenantTier.ENTERPRISE: {
                    "max_users": -1,  # Unlimited
                    "max_projects": -1,  # Unlimited
                    "max_storage_gb": -1,  # Unlimited
                    "max_api_calls_per_month": -1,  # Unlimited
                    "max_compute_hours_per_month": -1,  # Unlimited
                    "features": ["all_features", "custom_integrations", "dedicated_support", "sla_guarantee"]
                }
            }
            
            logger.info("Tier configurations initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing tier configurations: {e}")
    
    async def start(self):
        """Start the multi-tenancy system"""
        self.running = True
        logger.info("🚀 Starting Multi-tenancy System...")
        
        # Load existing data
        await self._load_tenancy_data()
        
        # Start background tasks
        asyncio.create_task(self._cleanup_old_data())
        asyncio.create_task(self._resource_monitoring_loop())
        asyncio.create_task(self._billing_processing_loop())
        
        logger.info("✅ Multi-tenancy System started")
    
    async def stop(self):
        """Stop the multi-tenancy system"""
        self.running = False
        logger.info("🛑 Stopping Multi-tenancy System...")
        
        # Save tenancy data
        await self._save_tenancy_data()
        
        logger.info("✅ Multi-tenancy System stopped")
    
    async def create_tenant(
        self,
        name: str,
        domain: str,
        tier: TenantTier,
        owner_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new tenant"""
        try:
            # Validate domain uniqueness
            if await self._domain_exists(domain):
                raise ValueError("Domain already exists")
            
            tenant_id = f"tenant_{int(time.time())}_{hashlib.md5(domain.encode()).hexdigest()[:8]}"
            
            tenant = Tenant(
                id=tenant_id,
                name=name,
                domain=domain,
                tier=tier,
                status=TenantStatus.PENDING,
                owner_id=owner_id,
                metadata=metadata or {}
            )
            
            self.tenants[tenant_id] = tenant
            
            # Initialize tenant resources
            await self._initialize_tenant_resources(tenant_id, tier)
            
            # Add owner as tenant user
            await self._add_tenant_user(tenant_id, owner_id, "owner", ["all"])
            
            logger.info(f"Tenant created: {tenant_id}")
            return tenant_id
            
        except Exception as e:
            logger.error(f"❌ Error creating tenant: {e}")
            raise
    
    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant information"""
        return self.tenants.get(tenant_id)
    
    async def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by domain"""
        for tenant in self.tenants.values():
            if tenant.domain == domain:
                return tenant
        return None
    
    async def list_tenants(self, status: Optional[TenantStatus] = None, tier: Optional[TenantTier] = None) -> List[Tenant]:
        """List tenants with optional filters"""
        tenants = list(self.tenants.values())
        
        if status:
            tenants = [t for t in tenants if t.status == status]
        
        if tier:
            tenants = [t for t in tenants if t.tier == tier]
        
        return tenants
    
    async def update_tenant(self, tenant_id: str, **updates) -> bool:
        """Update tenant information"""
        try:
            if tenant_id not in self.tenants:
                logger.warning(f"Tenant not found: {tenant_id}")
                return False
            
            tenant = self.tenants[tenant_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(tenant, key):
                    setattr(tenant, key, value)
            
            tenant.updated_at = datetime.now().isoformat()
            
            logger.info(f"Tenant updated: {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating tenant {tenant_id}: {e}")
            return False
    
    async def activate_tenant(self, tenant_id: str) -> bool:
        """Activate tenant"""
        try:
            if tenant_id not in self.tenants:
                raise ValueError("Tenant not found")
            
            tenant = self.tenants[tenant_id]
            tenant.status = TenantStatus.ACTIVE
            tenant.updated_at = datetime.now().isoformat()
            
            logger.info(f"Tenant activated: {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error activating tenant {tenant_id}: {e}")
            return False
    
    async def suspend_tenant(self, tenant_id: str) -> bool:
        """Suspend tenant"""
        try:
            if tenant_id not in self.tenants:
                raise ValueError("Tenant not found")
            
            tenant = self.tenants[tenant_id]
            tenant.status = TenantStatus.SUSPENDED
            tenant.updated_at = datetime.now().isoformat()
            
            logger.info(f"Tenant suspended: {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error suspending tenant {tenant_id}: {e}")
            return False
    
    async def add_tenant_user(
        self,
        tenant_id: str,
        user_id: str,
        role: str,
        permissions: List[str],
        added_by: str
    ) -> bool:
        """Add user to tenant"""
        try:
            if tenant_id not in self.tenants:
                raise ValueError("Tenant not found")
            
            # Check if user already exists
            existing_user = await self._get_tenant_user(tenant_id, user_id)
            if existing_user:
                raise ValueError("User already exists in tenant")
            
            await self._add_tenant_user(tenant_id, user_id, role, permissions)
            
            logger.info(f"User added to tenant: {user_id} -> {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding tenant user: {e}")
            return False
    
    async def remove_tenant_user(self, tenant_id: str, user_id: str) -> bool:
        """Remove user from tenant"""
        try:
            if tenant_id not in self.tenants:
                raise ValueError("Tenant not found")
            
            # Find and remove user
            user_key = f"{tenant_id}_{user_id}"
            if user_key in self.tenant_users:
                del self.tenant_users[user_key]
                logger.info(f"User removed from tenant: {user_id} -> {tenant_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error removing tenant user: {e}")
            return False
    
    async def get_tenant_users(self, tenant_id: str) -> List[TenantUser]:
        """Get tenant users"""
        try:
            users = [u for u in self.tenant_users.values() if u.tenant_id == tenant_id]
            return users
            
        except Exception as e:
            logger.error(f"❌ Error getting tenant users: {e}")
            return []
    
    async def get_tenant_resources(self, tenant_id: str) -> List[TenantResource]:
        """Get tenant resources"""
        try:
            resources = [r for r in self.tenant_resources.values() if r.tenant_id == tenant_id]
            return resources
            
        except Exception as e:
            logger.error(f"❌ Error getting tenant resources: {e}")
            return []
    
    async def update_tenant_resource(
        self,
        tenant_id: str,
        resource_type: ResourceType,
        used: float
    ) -> bool:
        """Update tenant resource usage"""
        try:
            resource_key = f"{tenant_id}_{resource_type.value}"
            
            if resource_key not in self.tenant_resources:
                logger.warning(f"Resource not found: {resource_key}")
                return False
            
            resource = self.tenant_resources[resource_key]
            resource.used = used
            resource.updated_at = datetime.now().isoformat()
            
            # Record usage
            await self._record_usage(tenant_id, resource_type, used)
            
            # Check if limit exceeded
            if resource.limit > 0 and used > resource.limit:
                await self._handle_resource_limit_exceeded(tenant_id, resource_type, used, resource.limit)
            
            logger.info(f"Resource updated: {resource_key} -> {used}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating tenant resource: {e}")
            return False
    
    async def get_tenant_configuration(self, tenant_id: str, key: str) -> Optional[Any]:
        """Get tenant configuration value"""
        try:
            config_key = f"{tenant_id}_{key}"
            
            if config_key in self.tenant_configurations:
                config = self.tenant_configurations[config_key]
                return config.value
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting tenant configuration: {e}")
            return None
    
    async def set_tenant_configuration(
        self,
        tenant_id: str,
        key: str,
        value: Any,
        data_type: str = "string"
    ) -> bool:
        """Set tenant configuration value"""
        try:
            if tenant_id not in self.tenants:
                raise ValueError("Tenant not found")
            
            config_key = f"{tenant_id}_{key}"
            
            config = TenantConfiguration(
                id=config_key,
                tenant_id=tenant_id,
                key=key,
                value=value,
                data_type=data_type
            )
            
            self.tenant_configurations[config_key] = config
            
            logger.info(f"Tenant configuration set: {config_key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting tenant configuration: {e}")
            return False
    
    async def get_tenant_usage(
        self,
        tenant_id: str,
        resource_type: Optional[ResourceType] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[TenantUsage]:
        """Get tenant usage data"""
        try:
            usage = [u for u in self.tenant_usage.values() if u.tenant_id == tenant_id]
            
            if resource_type:
                usage = [u for u in usage if u.resource_type == resource_type]
            
            if start_date:
                usage = [u for u in usage if u.timestamp >= start_date]
            
            if end_date:
                usage = [u for u in usage if u.timestamp <= end_date]
            
            # Sort by timestamp
            usage.sort(key=lambda u: u.timestamp)
            
            return usage
            
        except Exception as e:
            logger.error(f"❌ Error getting tenant usage: {e}")
            return []
    
    async def get_tenant_billing(self, tenant_id: str) -> List[TenantBilling]:
        """Get tenant billing information"""
        try:
            billing = [b for b in self.tenant_billing.values() if b.tenant_id == tenant_id]
            
            # Sort by due date
            billing.sort(key=lambda b: b.due_date)
            
            return billing
            
        except Exception as e:
            logger.error(f"❌ Error getting tenant billing: {e}")
            return []
    
    async def create_billing_record(
        self,
        tenant_id: str,
        tier: TenantTier,
        billing_cycle: BillingCycle,
        amount: float,
        currency: str = "USD"
    ) -> str:
        """Create billing record for tenant"""
        try:
            if tenant_id not in self.tenants:
                raise ValueError("Tenant not found")
            
            billing_id = f"billing_{int(time.time())}_{tenant_id}"
            
            # Calculate due date based on billing cycle
            due_date = self._calculate_due_date(billing_cycle)
            
            billing = TenantBilling(
                id=billing_id,
                tenant_id=tenant_id,
                tier=tier,
                billing_cycle=billing_cycle,
                amount=amount,
                currency=currency,
                due_date=due_date
            )
            
            self.tenant_billing[billing_id] = billing
            
            logger.info(f"Billing record created: {billing_id}")
            return billing_id
            
        except Exception as e:
            logger.error(f"❌ Error creating billing record: {e}")
            raise
    
    async def get_tenancy_analytics(self) -> Dict[str, Any]:
        """Get multi-tenancy system analytics"""
        try:
            total_tenants = len(self.tenants)
            total_users = len(self.tenant_users)
            total_resources = len(self.tenant_resources)
            total_billing = len(self.tenant_billing)
            
            # Status distribution
            status_distribution = {}
            for tenant in self.tenants.values():
                status = tenant.status.value
                status_distribution[status] = status_distribution.get(status, 0) + 1
            
            # Tier distribution
            tier_distribution = {}
            for tenant in self.tenants.values():
                tier = tenant.tier.value
                tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
            
            # Resource usage
            resource_usage = {}
            for resource in self.tenant_resources.values():
                resource_type = resource.resource_type.value
                if resource_type not in resource_usage:
                    resource_usage[resource_type] = {"total_allocated": 0, "total_used": 0}
                resource_usage[resource_type]["total_allocated"] += resource.allocated
                resource_usage[resource_type]["total_used"] += resource.used
            
            # Billing status
            billing_status = {
                "total": total_billing,
                "paid": len([b for b in self.tenant_billing.values() if b.paid]),
                "unpaid": len([b for b in self.tenant_billing.values() if not b.paid])
            }
            
            # Recent activity
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_tenants = [
                t for t in self.tenants.values()
                if datetime.fromisoformat(t.created_at) > recent_cutoff
            ]
            
            return {
                "tenants": {
                    "total": total_tenants,
                    "recent": len(recent_tenants),
                    "status_distribution": status_distribution,
                    "tier_distribution": tier_distribution
                },
                "users": {
                    "total": total_users
                },
                "resources": {
                    "total": total_resources,
                    "usage": resource_usage
                },
                "billing": billing_status,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting tenancy analytics: {e}")
            return {"error": str(e)}
    
    async def _domain_exists(self, domain: str) -> bool:
        """Check if domain already exists"""
        for tenant in self.tenants.values():
            if tenant.domain == domain:
                return True
        return False
    
    async def _initialize_tenant_resources(self, tenant_id: str, tier: TenantTier):
        """Initialize tenant resources based on tier"""
        try:
            tier_config = self.tier_configs[tier]
            
            # Initialize each resource type
            for resource_type in ResourceType:
                resource_key = f"{tenant_id}_{resource_type.value}"
                
                # Get limits from tier config
                if resource_type == ResourceType.USERS:
                    limit = tier_config["max_users"]
                elif resource_type == ResourceType.PROJECTS:
                    limit = tier_config["max_projects"]
                elif resource_type == ResourceType.STORAGE:
                    limit = tier_config["max_storage_gb"]
                elif resource_type == ResourceType.API_CALLS:
                    limit = tier_config["max_api_calls_per_month"]
                elif resource_type == ResourceType.COMPUTE:
                    limit = tier_config["max_compute_hours_per_month"]
                else:
                    limit = 0
                
                resource = TenantResource(
                    id=resource_key,
                    tenant_id=tenant_id,
                    resource_type=resource_type,
                    allocated=limit,
                    used=0,
                    limit=limit,
                    unit=self._get_resource_unit(resource_type)
                )
                
                self.tenant_resources[resource_key] = resource
            
        except Exception as e:
            logger.error(f"❌ Error initializing tenant resources: {e}")
    
    async def _add_tenant_user(self, tenant_id: str, user_id: str, role: str, permissions: List[str]):
        """Add user to tenant"""
        try:
            user_key = f"{tenant_id}_{user_id}"
            
            user = TenantUser(
                id=user_key,
                tenant_id=tenant_id,
                user_id=user_id,
                role=role,
                permissions=permissions
            )
            
            self.tenant_users[user_key] = user
            
        except Exception as e:
            logger.error(f"❌ Error adding tenant user: {e}")
    
    async def _get_tenant_user(self, tenant_id: str, user_id: str) -> Optional[TenantUser]:
        """Get tenant user"""
        user_key = f"{tenant_id}_{user_id}"
        return self.tenant_users.get(user_key)
    
    async def _record_usage(self, tenant_id: str, resource_type: ResourceType, usage: float):
        """Record resource usage"""
        try:
            usage_id = f"usage_{int(time.time())}_{tenant_id}_{resource_type.value}"
            
            usage_record = TenantUsage(
                id=usage_id,
                tenant_id=tenant_id,
                resource_type=resource_type,
                usage=usage
            )
            
            self.tenant_usage[usage_id] = usage_record
            
        except Exception as e:
            logger.error(f"❌ Error recording usage: {e}")
    
    async def _handle_resource_limit_exceeded(self, tenant_id: str, resource_type: ResourceType, used: float, limit: float):
        """Handle resource limit exceeded"""
        try:
            logger.warning(f"Resource limit exceeded: {tenant_id} - {resource_type.value} ({used}/{limit})")
            
            # In practice, this would trigger alerts, notifications, etc.
            # For now, just log the event
            
        except Exception as e:
            logger.error(f"❌ Error handling resource limit exceeded: {e}")
    
    def _get_resource_unit(self, resource_type: ResourceType) -> str:
        """Get resource unit"""
        units = {
            ResourceType.USERS: "users",
            ResourceType.PROJECTS: "projects",
            ResourceType.STORAGE: "GB",
            ResourceType.API_CALLS: "calls",
            ResourceType.COMPUTE: "hours",
            ResourceType.BANDWIDTH: "GB",
            ResourceType.FEATURES: "features"
        }
        return units.get(resource_type, "units")
    
    def _calculate_due_date(self, billing_cycle: BillingCycle) -> str:
        """Calculate billing due date"""
        now = datetime.now()
        
        if billing_cycle == BillingCycle.MONTHLY:
            due_date = now + timedelta(days=30)
        elif billing_cycle == BillingCycle.QUARTERLY:
            due_date = now + timedelta(days=90)
        elif billing_cycle == BillingCycle.YEARLY:
            due_date = now + timedelta(days=365)
        else:
            due_date = now + timedelta(days=30)
        
        return due_date.isoformat()
    
    async def _resource_monitoring_loop(self):
        """Resource monitoring loop"""
        while self.running:
            try:
                # Monitor resource usage and limits
                for resource in self.tenant_resources.values():
                    if resource.limit > 0 and resource.used > resource.limit:
                        await self._handle_resource_limit_exceeded(
                            resource.tenant_id,
                            resource.resource_type,
                            resource.used,
                            resource.limit
                        )
                
                await asyncio.sleep(self.resource_check_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in resource monitoring loop: {e}")
                await asyncio.sleep(3600)
    
    async def _billing_processing_loop(self):
        """Billing processing loop"""
        while self.running:
            try:
                # Process overdue billing
                current_date = datetime.now().isoformat()
                overdue_billing = [
                    b for b in self.tenant_billing.values()
                    if not b.paid and b.due_date < current_date
                ]
                
                for billing in overdue_billing:
                    # In practice, this would trigger payment collection, suspension, etc.
                    logger.warning(f"Overdue billing: {billing.id} for tenant {billing.tenant_id}")
                
                await asyncio.sleep(86400)  # Check daily
                
            except Exception as e:
                logger.error(f"❌ Error in billing processing loop: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_data(self):
        """Clean up old tenancy data"""
        while self.running:
            try:
                # Clean up old usage data
                usage_cutoff = datetime.now() - timedelta(days=self.usage_retention_days)
                
                old_usage = [
                    usage_id for usage_id, usage in self.tenant_usage.items()
                    if datetime.fromisoformat(usage.timestamp) < usage_cutoff
                ]
                
                for usage_id in old_usage:
                    del self.tenant_usage[usage_id]
                
                # Clean up old billing data
                billing_cutoff = datetime.now() - timedelta(days=self.billing_retention_days)
                
                old_billing = [
                    billing_id for billing_id, billing in self.tenant_billing.items()
                    if datetime.fromisoformat(billing.created_at) < billing_cutoff
                ]
                
                for billing_id in old_billing:
                    del self.tenant_billing[billing_id]
                
                if old_usage or old_billing:
                    logger.info(f"Cleaned up {len(old_usage)} old usage records and {len(old_billing)} old billing records")
                
                await asyncio.sleep(86400)  # Clean up daily
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up old data: {e}")
                await asyncio.sleep(3600)
    
    async def _load_tenancy_data(self):
        """Load tenancy data from storage"""
        try:
            if self.redis_client:
                # Load tenants
                tenants_data = self.redis_client.get("frenly_tenants")
                if tenants_data:
                    tenants_json = json.loads(tenants_data)
                    for tenant_id, tenant_data in tenants_json.items():
                        tenant = Tenant(
                            id=tenant_id,
                            name=tenant_data["name"],
                            domain=tenant_data["domain"],
                            tier=TenantTier(tenant_data["tier"]),
                            status=TenantStatus(tenant_data["status"]),
                            owner_id=tenant_data["owner_id"],
                            created_at=tenant_data["created_at"],
                            updated_at=tenant_data["updated_at"],
                            metadata=tenant_data.get("metadata", {})
                        )
                        self.tenants[tenant_id] = tenant
                
                # Load tenant resources
                resources_data = self.redis_client.get("frenly_tenant_resources")
                if resources_data:
                    resources_json = json.loads(resources_data)
                    for resource_id, resource_data in resources_json.items():
                        resource = TenantResource(
                            id=resource_id,
                            tenant_id=resource_data["tenant_id"],
                            resource_type=ResourceType(resource_data["resource_type"]),
                            allocated=resource_data["allocated"],
                            used=resource_data["used"],
                            limit=resource_data["limit"],
                            unit=resource_data["unit"],
                            created_at=resource_data["created_at"],
                            updated_at=resource_data["updated_at"]
                        )
                        self.tenant_resources[resource_id] = resource
                
                # Load tenant users
                users_data = self.redis_client.get("frenly_tenant_users")
                if users_data:
                    users_json = json.loads(users_data)
                    for user_id, user_data in users_json.items():
                        user = TenantUser(
                            id=user_id,
                            tenant_id=user_data["tenant_id"],
                            user_id=user_data["user_id"],
                            role=user_data["role"],
                            permissions=user_data["permissions"],
                            joined_at=user_data["joined_at"],
                            last_active=user_data["last_active"]
                        )
                        self.tenant_users[user_id] = user
                
                # Load tenant configurations
                configs_data = self.redis_client.get("frenly_tenant_configurations")
                if configs_data:
                    configs_json = json.loads(configs_data)
                    for config_id, config_data in configs_json.items():
                        config = TenantConfiguration(
                            id=config_id,
                            tenant_id=config_data["tenant_id"],
                            key=config_data["key"],
                            value=config_data["value"],
                            data_type=config_data["data_type"],
                            created_at=config_data["created_at"],
                            updated_at=config_data["updated_at"]
                        )
                        self.tenant_configurations[config_id] = config
                
                # Load tenant billing
                billing_data = self.redis_client.get("frenly_tenant_billing")
                if billing_data:
                    billing_json = json.loads(billing_data)
                    for billing_id, billing_data in billing_json.items():
                        billing = TenantBilling(
                            id=billing_id,
                            tenant_id=billing_data["tenant_id"],
                            tier=TenantTier(billing_data["tier"]),
                            billing_cycle=BillingCycle(billing_data["billing_cycle"]),
                            amount=billing_data["amount"],
                            currency=billing_data["currency"],
                            due_date=billing_data["due_date"],
                            paid=billing_data.get("paid", False),
                            created_at=billing_data["created_at"]
                        )
                        self.tenant_billing[billing_id] = billing
                
                # Load tenant usage
                usage_data = self.redis_client.get("frenly_tenant_usage")
                if usage_data:
                    usage_json = json.loads(usage_data)
                    for usage_id, usage_data in usage_json.items():
                        usage = TenantUsage(
                            id=usage_id,
                            tenant_id=usage_data["tenant_id"],
                            resource_type=ResourceType(usage_data["resource_type"]),
                            usage=usage_data["usage"],
                            timestamp=usage_data["timestamp"]
                        )
                        self.tenant_usage[usage_id] = usage
                
                logger.info(f"Loaded {len(self.tenants)} tenants, {len(self.tenant_resources)} resources, {len(self.tenant_users)} users, {len(self.tenant_configurations)} configurations, {len(self.tenant_billing)} billing records, {len(self.tenant_usage)} usage records")
            
        except Exception as e:
            logger.error(f"❌ Error loading tenancy data: {e}")
    
    async def _save_tenancy_data(self):
        """Save tenancy data to storage"""
        try:
            if self.redis_client:
                # Save tenants
                tenants_data = {
                    tenant_id: {
                        "name": tenant.name,
                        "domain": tenant.domain,
                        "tier": tenant.tier.value,
                        "status": tenant.status.value,
                        "owner_id": tenant.owner_id,
                        "created_at": tenant.created_at,
                        "updated_at": tenant.updated_at,
                        "metadata": tenant.metadata
                    }
                    for tenant_id, tenant in self.tenants.items()
                }
                self.redis_client.setex("frenly_tenants", 86400, json.dumps(tenants_data))
                
                # Save tenant resources
                resources_data = {
                    resource_id: {
                        "tenant_id": resource.tenant_id,
                        "resource_type": resource.resource_type.value,
                        "allocated": resource.allocated,
                        "used": resource.used,
                        "limit": resource.limit,
                        "unit": resource.unit,
                        "created_at": resource.created_at,
                        "updated_at": resource.updated_at
                    }
                    for resource_id, resource in self.tenant_resources.items()
                }
                self.redis_client.setex("frenly_tenant_resources", 86400, json.dumps(resources_data))
                
                # Save tenant users
                users_data = {
                    user_id: {
                        "tenant_id": user.tenant_id,
                        "user_id": user.user_id,
                        "role": user.role,
                        "permissions": user.permissions,
                        "joined_at": user.joined_at,
                        "last_active": user.last_active
                    }
                    for user_id, user in self.tenant_users.items()
                }
                self.redis_client.setex("frenly_tenant_users", 86400, json.dumps(users_data))
                
                # Save tenant configurations
                configs_data = {
                    config_id: {
                        "tenant_id": config.tenant_id,
                        "key": config.key,
                        "value": config.value,
                        "data_type": config.data_type,
                        "created_at": config.created_at,
                        "updated_at": config.updated_at
                    }
                    for config_id, config in self.tenant_configurations.items()
                }
                self.redis_client.setex("frenly_tenant_configurations", 86400, json.dumps(configs_data))
                
                # Save tenant billing
                billing_data = {
                    billing_id: {
                        "tenant_id": billing.tenant_id,
                        "tier": billing.tier.value,
                        "billing_cycle": billing.billing_cycle.value,
                        "amount": billing.amount,
                        "currency": billing.currency,
                        "due_date": billing.due_date,
                        "paid": billing.paid,
                        "created_at": billing.created_at
                    }
                    for billing_id, billing in self.tenant_billing.items()
                }
                self.redis_client.setex("frenly_tenant_billing", 86400, json.dumps(billing_data))
                
                # Save tenant usage
                usage_data = {
                    usage_id: {
                        "tenant_id": usage.tenant_id,
                        "resource_type": usage.resource_type.value,
                        "usage": usage.usage,
                        "timestamp": usage.timestamp
                    }
                    for usage_id, usage in self.tenant_usage.items()
                }
                self.redis_client.setex("frenly_tenant_usage", 86400, json.dumps(usage_data))
            
        except Exception as e:
            logger.error(f"❌ Error saving tenancy data: {e}")

# Global multi-tenancy system instance
multi_tenancy = MultiTenancySystem()

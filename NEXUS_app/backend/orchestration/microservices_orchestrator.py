#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Advanced Microservices Orchestration Platform
Sophisticated service mesh with automatic scaling, circuit breakers, and intelligent load balancing
"""

import os
import sys
import json
import asyncio
import aiohttp
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import yaml
import kubernetes
from kubernetes import client, config
import docker
import requests
from concurrent.futures import ThreadPoolExecutor
import threading

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    SCALING = "scaling"
    MAINTENANCE = "maintenance"

class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class ServiceInstance:
    """Represents a service instance"""
    name: str
    namespace: str
    pod_name: str
    ip: str
    port: int
    status: ServiceStatus
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    response_time: float = 0.0
    error_rate: float = 0.0
    last_health_check: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str
    namespace: str
    image: str
    replicas: int
    min_replicas: int = 1
    max_replicas: int = 10
    cpu_limit: str = "500m"
    memory_limit: str = "512Mi"
    cpu_request: str = "100m"
    memory_request: str = "128Mi"
    health_check_path: str = "/health"
    health_check_interval: int = 30
    scaling_threshold_cpu: float = 70.0
    scaling_threshold_memory: float = 80.0
    scaling_cooldown: int = 300  # 5 minutes

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    success_threshold: int = 3
    timeout: int = 30

@dataclass
class LoadBalancerConfig:
    """Load balancer configuration"""
    algorithm: str = "round_robin"  # round_robin, least_connections, weighted, ip_hash
    health_check_enabled: bool = True
    sticky_sessions: bool = False
    max_retries: int = 3
    timeout: int = 30

class CircuitBreaker:
    """Circuit breaker implementation"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.lock = threading.Lock()
    
    def can_execute(self) -> bool:
        """Check if request can be executed"""
        with self.lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.OPEN:
                if (datetime.now() - self.last_failure_time).seconds >= self.config.recovery_timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.success_count = 0
                    return True
                return False
            else:  # HALF_OPEN
                return True
    
    def record_success(self):
        """Record successful execution"""
        with self.lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
            elif self.state == CircuitBreakerState.CLOSED:
                self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self):
        """Record failed execution"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitBreakerState.OPEN

class LoadBalancer:
    """Intelligent load balancer"""
    
    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.instances: List[ServiceInstance] = []
        self.current_index = 0
        self.connection_counts: Dict[str, int] = {}
        self.weights: Dict[str, float] = {}
        self.lock = threading.Lock()
    
    def add_instance(self, instance: ServiceInstance, weight: float = 1.0):
        """Add service instance to load balancer"""
        with self.lock:
            self.instances.append(instance)
            self.connection_counts[instance.pod_name] = 0
            self.weights[instance.pod_name] = weight
    
    def remove_instance(self, pod_name: str):
        """Remove service instance from load balancer"""
        with self.lock:
            self.instances = [i for i in self.instances if i.pod_name != pod_name]
            self.connection_counts.pop(pod_name, None)
            self.weights.pop(pod_name, None)
    
    def get_instance(self) -> Optional[ServiceInstance]:
        """Get next instance based on load balancing algorithm"""
        with self.lock:
            if not self.instances:
                return None
            
            # Filter healthy instances
            healthy_instances = [i for i in self.instances if i.status == ServiceStatus.HEALTHY]
            if not healthy_instances:
                return None
            
            if self.config.algorithm == "round_robin":
                instance = healthy_instances[self.current_index % len(healthy_instances)]
                self.current_index += 1
                return instance
            
            elif self.config.algorithm == "least_connections":
                return min(healthy_instances, key=lambda x: self.connection_counts.get(x.pod_name, 0))
            
            elif self.config.algorithm == "weighted":
                # Weighted round robin
                total_weight = sum(self.weights.get(i.pod_name, 1.0) for i in healthy_instances)
                if total_weight == 0:
                    return healthy_instances[0]
                
                # Simple weighted selection
                rand = time.time() % 1.0
                cumulative = 0.0
                for instance in healthy_instances:
                    weight = self.weights.get(instance.pod_name, 1.0)
                    cumulative += weight / total_weight
                    if rand <= cumulative:
                        return instance
                
                return healthy_instances[0]
            
            else:  # ip_hash
                # Simple hash-based selection
                hash_val = hash(str(time.time())) % len(healthy_instances)
                return healthy_instances[hash_val]
    
    def record_connection(self, pod_name: str):
        """Record new connection"""
        with self.lock:
            self.connection_counts[pod_name] = self.connection_counts.get(pod_name, 0) + 1
    
    def record_disconnection(self, pod_name: str):
        """Record connection closure"""
        with self.lock:
            self.connection_counts[pod_name] = max(0, self.connection_counts.get(pod_name, 0) - 1)

class AutoScaler:
    """Automatic scaling controller"""
    
    def __init__(self):
        self.scaling_history: Dict[str, datetime] = {}
        self.metrics_cache: Dict[str, Dict[str, float]] = {}
    
    def should_scale_up(self, service_config: ServiceConfig, instances: List[ServiceInstance]) -> bool:
        """Determine if service should scale up"""
        if len(instances) >= service_config.max_replicas:
            return False
        
        # Check cooldown period
        last_scale = self.scaling_history.get(service_config.name)
        if last_scale and (datetime.now() - last_scale).seconds < service_config.scaling_cooldown:
            return False
        
        # Check if any instance is overloaded
        for instance in instances:
            if (instance.cpu_usage > service_config.scaling_threshold_cpu or 
                instance.memory_usage > service_config.scaling_threshold_memory):
                return True
        
        return False
    
    def should_scale_down(self, service_config: ServiceConfig, instances: List[ServiceInstance]) -> bool:
        """Determine if service should scale down"""
        if len(instances) <= service_config.min_replicas:
            return False
        
        # Check cooldown period
        last_scale = self.scaling_history.get(service_config.name)
        if last_scale and (datetime.now() - last_scale).seconds < service_config.scaling_cooldown:
            return False
        
        # Check if all instances are underutilized
        for instance in instances:
            if (instance.cpu_usage > service_config.scaling_threshold_cpu * 0.5 or 
                instance.memory_usage > service_config.scaling_threshold_memory * 0.5):
                return False
        
        return True
    
    def record_scaling(self, service_name: str):
        """Record scaling event"""
        self.scaling_history[service_name] = datetime.now()

class MicroservicesOrchestrator:
    """Advanced Microservices Orchestration Platform"""
    
    def __init__(self, kubeconfig_path: Optional[str] = None):
        """Initialize the orchestrator"""
        self.kubeconfig_path = kubeconfig_path
        self.services: Dict[str, ServiceConfig] = {}
        self.instances: Dict[str, List[ServiceInstance]] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.load_balancers: Dict[str, LoadBalancer] = {}
        self.auto_scaler = AutoScaler()
        self.health_check_interval = 30
        self.metrics_interval = 10
        self.running = False
        
        # Initialize Kubernetes client
        self._init_kubernetes()
        
        # Initialize Docker client
        self._init_docker()
        
        logger.info("Microservices Orchestrator initialized")
    
    def _init_kubernetes(self):
        """Initialize Kubernetes client"""
        try:
            if self.kubeconfig_path:
                config.load_kube_config(config_file=self.kubeconfig_path)
            else:
                config.load_incluster_config()
            
            self.k8s_client = client.ApiClient()
            self.apps_v1 = client.AppsV1Api()
            self.core_v1 = client.CoreV1Api()
            self.autoscaling_v1 = client.AutoscalingV1Api()
            
            logger.info("Kubernetes client initialized")
        except Exception as e:
            logger.warning(f"Kubernetes client initialization failed: {e}")
            self.k8s_client = None
    
    def _init_docker(self):
        """Initialize Docker client"""
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.warning(f"Docker client initialization failed: {e}")
            self.docker_client = None
    
    def register_service(self, service_config: ServiceConfig):
        """Register a new service"""
        self.services[service_config.name] = service_config
        self.instances[service_config.name] = []
        
        # Create circuit breaker
        circuit_breaker_config = CircuitBreakerConfig()
        self.circuit_breakers[service_config.name] = CircuitBreaker(circuit_breaker_config)
        
        # Create load balancer
        load_balancer_config = LoadBalancerConfig()
        self.load_balancers[service_config.name] = LoadBalancer(load_balancer_config)
        
        logger.info(f"Service registered: {service_config.name}")
    
    async def deploy_service(self, service_config: ServiceConfig) -> bool:
        """Deploy a service to Kubernetes"""
        if not self.k8s_client:
            logger.error("Kubernetes client not available")
            return False
        
        try:
            # Create deployment
            deployment = self._create_deployment(service_config)
            self.apps_v1.create_namespaced_deployment(
                namespace=service_config.namespace,
                body=deployment
            )
            
            # Create service
            service = self._create_service(service_config)
            self.core_v1.create_namespaced_service(
                namespace=service_config.namespace,
                body=service
            )
            
            # Create HPA (Horizontal Pod Autoscaler)
            hpa = self._create_hpa(service_config)
            self.autoscaling_v1.create_namespaced_horizontal_pod_autoscaler(
                namespace=service_config.namespace,
                body=hpa
            )
            
            logger.info(f"Service deployed: {service_config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy service {service_config.name}: {e}")
            return False
    
    def _create_deployment(self, service_config: ServiceConfig) -> Dict[str, Any]:
        """Create Kubernetes deployment manifest"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": service_config.name,
                "namespace": service_config.namespace,
                "labels": {
                    "app": service_config.name,
                    "version": "v1"
                }
            },
                "replicas": service_config.replicas,
                "selector": {
                    "matchLabels": {
                        "app": service_config.name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": service_config.name,
                            "version": "v1"
                        }
                    },
                        "containers": [{
                            "name": service_config.name,
                            "image": service_config.image,
                            "ports": [{
                                "containerPort": 8080,
                                "protocol": "TCP"
                            }],
                            "resources": {
                                "limits": {
                                    "cpu": service_config.cpu_limit,
                                    "memory": service_config.memory_limit
                                },
                                "requests": {
                                    "cpu": service_config.cpu_request,
                                    "memory": service_config.memory_request
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": service_config.health_check_path,
                                    "port": 8080
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": service_config.health_check_interval
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": service_config.health_check_path,
                                    "port": 8080
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
    
    def _create_service(self, service_config: ServiceConfig) -> Dict[str, Any]:
        """Create Kubernetes service manifest"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": service_config.name,
                "namespace": service_config.namespace
            },
                "selector": {
                    "app": service_config.name
                },
                "ports": [{
                    "port": 80,
                    "targetPort": 8080,
                    "protocol": "TCP"
                }],
                "type": "ClusterIP"
            }
        }
    
    def _create_hpa(self, service_config: ServiceConfig) -> Dict[str, Any]:
        """Create Horizontal Pod Autoscaler manifest"""
        return {
            "apiVersion": "autoscaling/v1",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{service_config.name}-hpa",
                "namespace": service_config.namespace
            },
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": service_config.name
                },
                "minReplicas": service_config.min_replicas,
                "maxReplicas": service_config.max_replicas,
                "targetCPUUtilizationPercentage": int(service_config.scaling_threshold_cpu)
            }
        }
    
    async def health_check(self, instance: ServiceInstance) -> ServiceStatus:
        """Perform health check on service instance"""
        try:
            url = f"http://{instance.ip}:{instance.port}{self.services[instance.name].health_check_path}"
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        instance.status = ServiceStatus.HEALTHY
                        instance.last_health_check = datetime.now()
                        return ServiceStatus.HEALTHY
                    else:
                        instance.status = ServiceStatus.UNHEALTHY
                        return ServiceStatus.UNHEALTHY
        except Exception as e:
            logger.warning(f"Health check failed for {instance.name}: {e}")
            instance.status = ServiceStatus.UNHEALTHY
            return ServiceStatus.UNHEALTHY
    
    async def collect_metrics(self, instance: ServiceInstance):
        """Collect metrics from service instance"""
        try:
            
        except Exception as e:
            logger.warning(f"Metrics collection failed for {instance.name}: {e}")
    
    async def update_service_instances(self, service_name: str):
        """Update service instances from Kubernetes"""
        if not self.k8s_client:
            return
        
        try:
            service_config = self.services[service_name]
            
            # Get pods for the service
            pods = self.core_v1.list_namespaced_pod(
                namespace=service_config.namespace,
                label_selector=f"app={service_name}"
            )
            
            current_instances = []
            for pod in pods.items:
                if pod.status.phase == "Running":
                    instance = ServiceInstance(
                        name=service_name,
                        namespace=service_config.namespace,
                        pod_name=pod.metadata.name,
                        ip=pod.status.pod_ip,
                        port=8080,
                        status=ServiceStatus.HEALTHY
                    )
                    current_instances.append(instance)
            
            # Update instances
            self.instances[service_name] = current_instances
            
            # Update load balancer
            load_balancer = self.load_balancers[service_name]
            load_balancer.instances = current_instances
            
        except Exception as e:
            logger.error(f"Failed to update instances for {service_name}: {e}")
    
    async def auto_scale_service(self, service_name: str):
        """Perform auto-scaling for a service"""
        if service_name not in self.services:
            return
        
        service_config = self.services[service_name]
        instances = self.instances[service_name]
        
        # Collect metrics for all instances
        for instance in instances:
            await self.collect_metrics(instance)
        
        # Check if scaling is needed
        if self.auto_scaler.should_scale_up(service_config, instances):
            await self._scale_up(service_name)
        elif self.auto_scaler.should_scale_down(service_config, instances):
            await self._scale_down(service_name)
    
    async def _scale_up(self, service_name: str):
        """Scale up service"""
        if not self.k8s_client:
            return
        
        try:
            service_config = self.services[service_name]
            current_replicas = len(self.instances[service_name])
            new_replicas = min(current_replicas + 1, service_config.max_replicas)
            
            # Update deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=service_name,
                namespace=service_config.namespace
            )
            
            self.apps_v1.patch_namespaced_deployment_scale(
                name=service_name,
                namespace=service_config.namespace,
            )
            
            self.auto_scaler.record_scaling(service_name)
            logger.info(f"Scaled up {service_name} to {new_replicas} replicas")
            
        except Exception as e:
            logger.error(f"Failed to scale up {service_name}: {e}")
    
    async def _scale_down(self, service_name: str):
        """Scale down service"""
        if not self.k8s_client:
            return
        
        try:
            service_config = self.services[service_name]
            current_replicas = len(self.instances[service_name])
            new_replicas = max(current_replicas - 1, service_config.min_replicas)
            
            # Update deployment
            self.apps_v1.patch_namespaced_deployment_scale(
                name=service_name,
                namespace=service_config.namespace,
            )
            
            self.auto_scaler.record_scaling(service_name)
            logger.info(f"Scaled down {service_name} to {new_replicas} replicas")
            
        except Exception as e:
            logger.error(f"Failed to scale down {service_name}: {e}")
    
    async def route_request(self, service_name: str, path: str, method: str = "GET", 
                          data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Route request through load balancer and circuit breaker"""
        if service_name not in self.load_balancers:
            return None
        
        circuit_breaker = self.circuit_breakers[service_name]
        load_balancer = self.load_balancers[service_name]
        
        # Check circuit breaker
        if not circuit_breaker.can_execute():
            return {"error": "Circuit breaker is open", "status": 503}
        
        # Get instance from load balancer
        instance = load_balancer.get_instance()
        if not instance:
            return {"error": "No healthy instances available", "status": 503}
        
        try:
            # Record connection
            load_balancer.record_connection(instance.pod_name)
            
            # Make request
            url = f"http://{instance.ip}:{instance.port}{path}"
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                if method.upper() == "GET":
                    async with session.get(url) as response:
                        result = await response.json()
                        circuit_breaker.record_success()
                        return result
                elif method.upper() == "POST":
                    async with session.post(url, json=data) as response:
                        result = await response.json()
                        circuit_breaker.record_success()
                        return result
                else:
                    return {"error": f"Unsupported method: {method}", "status": 405}
        
        except Exception as e:
            circuit_breaker.record_failure()
            logger.error(f"Request failed for {service_name}: {e}")
            return {"error": str(e), "status": 500}
        
        finally:
            load_balancer.record_disconnection(instance.pod_name)
    
    async def start_monitoring(self):
        """Start monitoring loop"""
        self.running = True
        logger.info("Starting monitoring loop...")
        
        while self.running:
            try:
                # Update all service instances
                for service_name in self.services:
                    await self.update_service_instances(service_name)
                
                # Perform health checks
                for service_name, instances in self.instances.items():
                    for instance in instances:
                        await self.health_check(instance)
                
                # Auto-scale services
                for service_name in self.services:
                    await self.auto_scale_service(service_name)
                
                # Wait before next iteration
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    def stop_monitoring(self):
        """Stop monitoring loop"""
        self.running = False
        logger.info("Monitoring loop stopped")
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        if service_name not in self.services:
            return {"error": "Service not found"}
        
        instances = self.instances.get(service_name, [])
        healthy_instances = [i for i in instances if i.status == ServiceStatus.HEALTHY]
        
        return {
            "name": service_name,
            "total_instances": len(instances),
            "healthy_instances": len(healthy_instances),
            "circuit_breaker_state": self.circuit_breakers[service_name].state.value,
            "instances": [
                {
                    "pod_name": i.pod_name,
                    "ip": i.ip,
                    "status": i.status.value,
                    "cpu_usage": i.cpu_usage,
                    "memory_usage": i.memory_usage,
                    "response_time": i.response_time,
                    "error_rate": i.error_rate
                }
                for i in instances
            ]
        }
    
    def get_overall_status(self) -> Dict[str, Any]:
        """Get overall orchestrator status"""
        total_services = len(self.services)
        total_instances = sum(len(instances) for instances in self.instances.values())
        healthy_instances = sum(
            len([i for i in instances if i.status == ServiceStatus.HEALTHY])
            for instances in self.instances.values()
        )
        
        return {
            "total_services": total_services,
            "total_instances": total_instances,
            "healthy_instances": healthy_instances,
            "services": {
                name: self.get_service_status(name)
                for name in self.services
            }
        }

    
    # Initialize orchestrator
    orchestrator = MicroservicesOrchestrator()
    
    # Register services
    services = [
        ServiceConfig(
            name="nexus-app",
            namespace="default",
            replicas=3,
            min_replicas=2,
            max_replicas=10,
            scaling_threshold_cpu=70.0,
            scaling_threshold_memory=80.0
        ),
        ServiceConfig(
            name="ai-engine",
            namespace="default",
            replicas=2,
            min_replicas=1,
            max_replicas=5,
            scaling_threshold_cpu=60.0,
            scaling_threshold_memory=75.0
        ),
        ServiceConfig(
            name="frenly-ai",
            namespace="default",
            replicas=2,
            min_replicas=1,
            max_replicas=5,
            scaling_threshold_cpu=65.0,
            scaling_threshold_memory=70.0
        )
    ]
    
    for service in services:
        orchestrator.register_service(service)
        print(f"✅ Service registered: {service.name}")
    
    # Start monitoring in background
    monitoring_task = asyncio.create_task(orchestrator.start_monitoring())
    
    # Wait a bit for monitoring to start
    await asyncio.sleep(5)
    
    # Get status
    status = orchestrator.get_overall_status()
    print(f"\n📊 Orchestrator Status:")
    print(f"   Total Services: {status['total_services']}")
    print(f"   Total Instances: {status['total_instances']}")
    print(f"   Healthy Instances: {status['healthy_instances']}")
    
    
    # Stop monitoring
    orchestrator.stop_monitoring()
    monitoring_task.cancel()
    
    print(f"\n✅ Microservices Orchestration Platform ready!")

if __name__ == "__main__":
    asyncio.run(main())

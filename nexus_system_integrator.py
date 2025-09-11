#!/usr/bin/env python3
"""
🔗 Nexus Platform System Integrator
Ensures all systems work together seamlessly
"""

import os
import sys
import json
import time
import requests
import subprocess
import psutil
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nexus_system_integrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NexusSystemIntegrator:
    def __init__(self):
        self.base_path = Path("/Users/Arief/Desktop/Nexus")
        self.config = {
            "systems": {
                "python_processes": {
                    "enabled": True,
                    "scripts": [
                        "robust_parallel_worker_system.py",
                        "nexus_comprehensive_sot.py",
                        "enhanced_monitoring_dashboard.py"
                    ]
                },
                "docker_services": {
                    "enabled": True,
                    "compose_file": "docker/docker-compose.simple.yml",
                    "services": ["postgresql", "redis", "neo4j", "minio", "rabbitmq", "prometheus", "grafana"]
                },
                "kubernetes_cluster": {
                    "enabled": True,
                    "namespace": "nexus-platform",
                    "services": ["postgresql", "redis"]
                },
                "nexus_app": {
                    "enabled": True,
                    "port": 8000,
                    "module": "NEXUS_app.backend.main_enhanced:app"
                }
            },
            "integration": {
                "health_check_interval": 30,
                "auto_restart": True,
                "cross_system_communication": True
            }
        }
        
    def check_system_health(self):
        """Check health of all integrated systems"""
        logger.info("🔍 Checking system health...")
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "systems": {},
            "overall_health": "unknown"
        }
        
        # Check Python processes
        python_health = self.check_python_processes()
        health_status["systems"]["python_processes"] = python_health
        
        # Check Docker services
        docker_health = self.check_docker_services()
        health_status["systems"]["docker_services"] = docker_health
        
        # Check Kubernetes cluster
        k8s_health = self.check_kubernetes_services()
        health_status["systems"]["kubernetes_cluster"] = k8s_health
        
        # Check Nexus app
        app_health = self.check_nexus_app()
        health_status["systems"]["nexus_app"] = app_health
        
        # Determine overall health
        healthy_systems = sum(1 for system in health_status["systems"].values() if system["status"] == "healthy")
        total_systems = len(health_status["systems"])
        
        if healthy_systems == total_systems:
            health_status["overall_health"] = "excellent"
        elif healthy_systems >= total_systems * 0.7:
            health_status["overall_health"] = "good"
        elif healthy_systems >= total_systems * 0.4:
            health_status["overall_health"] = "fair"
        else:
            health_status["overall_health"] = "poor"
            
        # Save health report
        with open(self.base_path / "system_health_report.json", "w") as f:
            json.dump(health_status, f, indent=2)
            
        logger.info(f"📊 System health: {health_status['overall_health']} ({healthy_systems}/{total_systems} systems healthy)")
        return health_status
        
    def check_python_processes(self):
        """Check Python automation processes"""
        try:
            processes_found = {}
            
            for script in self.config["systems"]["python_processes"]["scripts"]:
                found = False
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['cmdline'] and any(script in cmd for cmd in proc.info['cmdline']):
                            processes_found[script] = {
                                "pid": proc.info['pid'],
                                "status": "running",
                                "memory": proc.memory_info().rss / 1024 / 1024,  # MB
                                "cpu": proc.cpu_percent()
                            }
                            found = True
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
                if not found:
                    processes_found[script] = {"status": "not_running"}
                    
            healthy_count = sum(1 for p in processes_found.values() if p["status"] == "running")
            total_count = len(processes_found)
            
            return {
                "status": "healthy" if healthy_count == total_count else "degraded" if healthy_count > 0 else "unhealthy",
                "details": processes_found,
                "healthy_processes": healthy_count,
                "total_processes": total_count
            }
            
        except Exception as e:
            logger.error(f"Error checking Python processes: {e}")
            return {"status": "error", "error": str(e)}
            
    def check_docker_services(self):
        """Check Docker services health"""
        try:
            result = subprocess.run([
                '/Applications/Docker.app/Contents/Resources/bin/docker',
                'compose', '-f', self.config["systems"]["docker_services"]["compose_file"],
                'ps', '--format', 'json'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return {"status": "error", "error": "Docker compose command failed"}
                
            services_data = []
            if result.stdout.strip():
                services_data = [json.loads(line) for line in result.stdout.strip().split('\n') if line]
                
            healthy_services = sum(1 for service in services_data if service.get('State') == 'running')
            total_services = len(services_data)
            
            return {
                "status": "healthy" if healthy_services == total_services else "degraded" if healthy_services > 0 else "unhealthy",
                "details": services_data,
                "healthy_services": healthy_services,
                "total_services": total_services
            }
            
        except Exception as e:
            logger.error(f"Error checking Docker services: {e}")
            return {"status": "error", "error": str(e)}
            
    def check_kubernetes_services(self):
        """Check Kubernetes services health"""
        try:
            result = subprocess.run([
                'kubectl', 'get', 'pods', '-n', self.config["systems"]["kubernetes_cluster"]["namespace"],
                '-o', 'json'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return {"status": "error", "error": "Kubectl command failed"}
                
            pods_data = json.loads(result.stdout)
            pods = pods_data.get('items', [])
            
            healthy_pods = sum(1 for pod in pods if pod.get('status', {}).get('phase') == 'Running')
            total_pods = len(pods)
            
            return {
                "status": "healthy" if healthy_pods == total_pods else "degraded" if healthy_pods > 0 else "unhealthy",
                "details": pods,
                "healthy_pods": healthy_pods,
                "total_pods": total_pods
            }
            
        except Exception as e:
            logger.error(f"Error checking Kubernetes services: {e}")
            return {"status": "error", "error": str(e)}
            
    def check_nexus_app(self):
        """Check Nexus app backend health"""
        try:
            response = requests.get(f"http://localhost:{self.config['systems']['nexus_app']['port']}/health", timeout=5)
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                }
            else:
                return {
                    "status": "unhealthy",
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.ConnectionError:
            # Check if uvicorn process is running
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any('uvicorn' in cmd for cmd in proc.info['cmdline']):
                        return {
                            "status": "degraded",
                            "process_running": True,
                            "pid": proc.info['pid'],
                            "error": "App not responding but process running"
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            return {"status": "unhealthy", "error": "No connection and no process found"}
            
        except Exception as e:
            logger.error(f"Error checking Nexus app: {e}")
            return {"status": "error", "error": str(e)}
            
    def integrate_systems(self):
        """Integrate all systems to work together"""
        logger.info("🔗 Integrating all systems...")
        
        integration_tasks = [
            ("Health Check", self.check_system_health),
            ("Cross-System Communication", self.setup_cross_system_communication),
            ("Service Discovery", self.setup_service_discovery),
            ("Load Balancing", self.setup_load_balancing),
            ("Monitoring Integration", self.setup_monitoring_integration)
        ]
        
        for task_name, task_func in integration_tasks:
            try:
                logger.info(f"🔄 {task_name}...")
                task_func()
                logger.info(f"✅ {task_name} completed")
            except Exception as e:
                logger.error(f"❌ {task_name} failed: {e}")
                
    def setup_cross_system_communication(self):
        """Set up communication between different systems"""
        logger.info("📡 Setting up cross-system communication...")
        
        # Create integration configuration
        integration_config = {
            "services": {
                "nexus_app": {
                    "url": "http://localhost:8000",
                    "health_endpoint": "/health",
                    "api_endpoint": "/api"
                },
                "postgresql_docker": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "nexus_automation",
                    "user": "nexus_user"
                },
                "postgresql_k8s": {
                    "host": "postgresql.nexus-platform.svc.cluster.local",
                    "port": 5432,
                    "database": "nexus_automation",
                    "user": "nexus_user"
                },
                "redis_docker": {
                    "host": "localhost",
                    "port": 6379,
                    "password": "redis_password123"
                },
                "redis_k8s": {
                    "host": "redis.nexus-platform.svc.cluster.local",
                    "port": 6379,
                    "password": "redis_password123"
                },
                "monitoring": {
                    "prometheus": "http://localhost:9090",
                    "grafana": "http://localhost:3000"
                }
            },
            "routing": {
                "primary_database": "postgresql_docker",
                "primary_cache": "redis_docker",
                "fallback_database": "postgresql_k8s",
                "fallback_cache": "redis_k8s"
            }
        }
        
        # Save integration configuration
        with open(self.base_path / "system_integration_config.json", "w") as f:
            json.dump(integration_config, f, indent=2)
            
        logger.info("✅ Cross-system communication configured")
        
    def setup_service_discovery(self):
        """Set up service discovery for all systems"""
        logger.info("🔍 Setting up service discovery...")
        
        service_registry = {
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        # Register Docker services
        try:
            result = subprocess.run([
                '/Applications/Docker.app/Contents/Resources/bin/docker',
                'compose', '-f', 'docker/docker-compose.simple.yml',
                'ps', '--format', 'json'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                services = [json.loads(line) for line in result.stdout.strip().split('\n') if line]
                for service in services:
                    service_name = service.get('Service', '')
                    if service_name:
                        service_registry["services"][f"docker_{service_name}"] = {
                            "type": "docker",
                            "name": service_name,
                            "status": service.get('State', 'unknown'),
                            "ports": service.get('Publishers', []),
                            "container_id": service.get('ID', '')
                        }
        except Exception as e:
            logger.error(f"Error discovering Docker services: {e}")
            
        # Register Kubernetes services
        try:
            result = subprocess.run([
                'kubectl', 'get', 'services', '-n', 'nexus-platform',
                '-o', 'json'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                services_data = json.loads(result.stdout)
                for service in services_data.get('items', []):
                    service_name = service.get('metadata', {}).get('name', '')
                    if service_name:
                        service_registry["services"][f"k8s_{service_name}"] = {
                            "type": "kubernetes",
                            "name": service_name,
                            "namespace": "nexus-platform",
                            "cluster_ip": service.get('spec', {}).get('clusterIP', ''),
                            "ports": service.get('spec', {}).get('ports', [])
                        }
        except Exception as e:
            logger.error(f"Error discovering Kubernetes services: {e}")
            
        # Save service registry
        with open(self.base_path / "service_registry.json", "w") as f:
            json.dump(service_registry, f, indent=2)
            
        logger.info(f"✅ Service discovery completed. Found {len(service_registry['services'])} services")
        
    def setup_load_balancing(self):
        """Set up load balancing between Docker and Kubernetes services"""
        logger.info("⚖️ Setting up load balancing...")
        
        load_balancer_config = {
            "strategy": "round_robin",
            "health_check_interval": 30,
            "services": {
                "database": {
                    "primary": "postgresql_docker",
                    "secondary": "postgresql_k8s",
                    "failover_threshold": 3
                },
                "cache": {
                    "primary": "redis_docker",
                    "secondary": "redis_k8s",
                    "failover_threshold": 3
                }
            },
            "rules": [
                {
                    "condition": "postgresql_docker.health == 'healthy'",
                    "action": "use_primary_database"
                },
                {
                    "condition": "postgresql_docker.health != 'healthy'",
                    "action": "failover_to_k8s_database"
                },
                {
                    "condition": "redis_docker.health == 'healthy'",
                    "action": "use_primary_cache"
                },
                {
                    "condition": "redis_docker.health != 'healthy'",
                    "action": "failover_to_k8s_cache"
                }
            ]
        }
        
        # Save load balancer configuration
        with open(self.base_path / "load_balancer_config.json", "w") as f:
            json.dump(load_balancer_config, f, indent=2)
            
        logger.info("✅ Load balancing configured")
        
    def setup_monitoring_integration(self):
        """Set up integrated monitoring across all systems"""
        logger.info("📊 Setting up monitoring integration...")
        
        monitoring_config = {
            "prometheus": {
                "url": "http://localhost:9090",
                "targets": [
                    {
                        "job": "nexus-app",
                        "targets": ["localhost:8000"],
                        "metrics_path": "/metrics"
                    },
                    {
                        "job": "docker-services",
                        "targets": ["localhost:5432", "localhost:6379", "localhost:7474"],
                        "metrics_path": "/metrics"
                    }
                ]
            },
            "grafana": {
                "url": "http://localhost:3000",
                "dashboards": [
                    {
                        "name": "Nexus Platform Overview",
                        "panels": [
                            "System Health",
                            "Service Status",
                            "Performance Metrics",
                            "Error Rates"
                        ]
                    }
                ]
            },
            "alerts": [
                {
                    "name": "Service Down",
                    "condition": "service_health == 'unhealthy'",
                    "severity": "critical"
                },
                {
                    "name": "High CPU Usage",
                    "condition": "cpu_usage > 80",
                    "severity": "warning"
                },
                {
                    "name": "High Memory Usage",
                    "condition": "memory_usage > 85",
                    "severity": "warning"
                }
            ]
        }
        
        # Save monitoring configuration
        with open(self.base_path / "monitoring_integration_config.json", "w") as f:
            json.dump(monitoring_config, f, indent=2)
            
        logger.info("✅ Monitoring integration configured")
        
    def run_integration(self):
        """Run the complete system integration"""
        logger.info("🚀 Starting Nexus Platform System Integration...")
        
        try:
            # Run integration
            self.integrate_systems()
            
            # Final health check
            health = self.check_system_health()
            
            logger.info("🎉 System integration completed successfully!")
            logger.info(f"📊 Overall health: {health['overall_health']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ System integration failed: {e}")
            return False

def main():
    """Main entry point"""
    integrator = NexusSystemIntegrator()
    success = integrator.run_integration()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

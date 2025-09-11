#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔄 Frenly AI CI/CD Integration
Continuous Integration and Deployment for Frenly AI
"""

import asyncio
import logging
import time
import json
import subprocess
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class BuildStatus(Enum):
    """Build status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DeploymentStatus(Enum):
    """Deployment status enumeration"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLBACK = "rollback"


@dataclass
class Build:
    """Build definition"""
    id: str
    branch: str
    commit: str
    status: BuildStatus
    started_at: str
    completed_at: Optional[str] = None
    duration: Optional[int] = None
    logs: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

@dataclass
    id: str
    name: str

@dataclass
class Deployment:
    """Deployment definition"""
    id: str
    build_id: str
    environment: str
    status: DeploymentStatus
    started_at: str
    completed_at: Optional[str] = None
    duration: Optional[int] = None
    logs: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

@dataclass
class Pipeline:
    """CI/CD pipeline definition"""
    id: str
    name: str
    triggers: List[str]  # git branches, tags, etc.
    environment: str
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

class CICDIntegration:
    """CI/CD integration for Frenly AI"""
    
    def __init__(self):
        self.config = get_config()
        self.redis_client = redis.Redis.from_url(self.config.redis_url)
        self.running = False
        
        # CI/CD storage
        self.builds: Dict[str, Build] = {}
        self.deployments: Dict[str, Deployment] = {}
        self.pipelines: Dict[str, Pipeline] = {}
        
        # Configuration
        self.build_timeout = 1800  # 30 minutes
        self.deployment_timeout = 1200  # 20 minutes
        self.max_concurrent_builds = 3
        
        # Webhook endpoints
        self.webhook_endpoints = {
            "github": "/webhooks/github",
            "gitlab": "/webhooks/gitlab",
            "bitbucket": "/webhooks/bitbucket"
        }
        
        logger.info("✅ CI/CD Integration initialized")
    
    async def start(self):
        """Start the CI/CD integration"""
        self.running = True
        logger.info("🚀 Starting CI/CD Integration...")
        
        # Load existing data
        await self._load_cicd_data()
        
        # Start background tasks
        asyncio.create_task(self._process_build_queue())
        asyncio.create_task(self._process_deployment_queue())
        asyncio.create_task(self._cleanup_old_data())
        
        logger.info("✅ CI/CD Integration started")
    
    async def stop(self):
        """Stop the CI/CD integration"""
        self.running = False
        logger.info("🛑 Stopping CI/CD Integration...")
        
        # Save CI/CD data
        await self._save_cicd_data()
        
        logger.info("✅ CI/CD Integration stopped")
    
    async def create_pipeline(
        self,
        name: str,
        triggers: List[str],
        stages: List[str],
        environment: str
    ) -> str:
        """Create a new CI/CD pipeline"""
        try:
            pipeline_id = f"pipeline_{int(time.time())}"
            
            pipeline = Pipeline(
                id=pipeline_id,
                name=name,
                triggers=triggers,
                stages=stages,
                environment=environment
            )
            
            self.pipelines[pipeline_id] = pipeline
            
            logger.info(f"Pipeline created: {pipeline_id}")
            return pipeline_id
            
        except Exception as e:
            logger.error(f"❌ Error creating pipeline: {e}")
            raise
    
    async def trigger_build(
        self,
        branch: str,
        commit: str,
        pipeline_id: Optional[str] = None
    ) -> str:
        """Trigger a new build"""
        try:
            build_id = f"build_{int(time.time())}"
            
            build = Build(
                id=build_id,
                branch=branch,
                commit=commit,
                status=BuildStatus.PENDING,
                started_at=datetime.now().isoformat()
            )
            
            self.builds[build_id] = build
            
            # Queue build for processing
            await self._queue_build(build_id)
            
            logger.info(f"Build triggered: {build_id}")
            return build_id
            
        except Exception as e:
            logger.error(f"❌ Error triggering build: {e}")
            raise
    
        self,
        build_id: str,
    ) -> List[str]:
        try:
            if build_id not in self.builds:
                raise ValueError("Build not found")
            
            build = self.builds[build_id]
            if build.status != BuildStatus.SUCCESS:
            
            
                
                
                
            
            
        except Exception as e:
            raise
    
    async def trigger_deployment(
        self,
        build_id: str,
        environment: str
    ) -> str:
        """Trigger deployment for a build"""
        try:
            if build_id not in self.builds:
                raise ValueError("Build not found")
            
            build = self.builds[build_id]
            if build.status != BuildStatus.SUCCESS:
                raise ValueError("Build must be successful to deploy")
            
            deployment_id = f"deployment_{int(time.time())}"
            
            deployment = Deployment(
                id=deployment_id,
                build_id=build_id,
                environment=environment,
                status=DeploymentStatus.PENDING,
                started_at=datetime.now().isoformat()
            )
            
            self.deployments[deployment_id] = deployment
            
            # Queue deployment for processing
            await self._queue_deployment(deployment_id)
            
            logger.info(f"Deployment triggered: {deployment_id}")
            return deployment_id
            
        except Exception as e:
            logger.error(f"❌ Error triggering deployment: {e}")
            raise
    
    async def get_build(self, build_id: str) -> Optional[Build]:
        """Get build information"""
        return self.builds.get(build_id)
    
    
    async def get_deployment(self, deployment_id: str) -> Optional[Deployment]:
        """Get deployment information"""
        return self.deployments.get(deployment_id)
    
    async def get_pipeline(self, pipeline_id: str) -> Optional[Pipeline]:
        """Get pipeline information"""
        return self.pipelines.get(pipeline_id)
    
    async def list_builds(
        self,
        status: Optional[BuildStatus] = None,
        branch: Optional[str] = None,
        limit: int = 50
    ) -> List[Build]:
        """List builds with optional filters"""
        builds = list(self.builds.values())
        
        if status:
            builds = [b for b in builds if b.status == status]
        
        if branch:
            builds = [b for b in builds if b.branch == branch]
        
        # Sort by started_at descending
        builds.sort(key=lambda b: b.started_at, reverse=True)
        
        return builds[:limit]
    
        self,
        
        if status:
        
        # Sort by started_at descending
        
    
    async def list_deployments(
        self,
        status: Optional[DeploymentStatus] = None,
        environment: Optional[str] = None,
        limit: int = 50
    ) -> List[Deployment]:
        """List deployments with optional filters"""
        deployments = list(self.deployments.values())
        
        if status:
            deployments = [d for d in deployments if d.status == status]
        
        if environment:
            deployments = [d for d in deployments if d.environment == environment]
        
        # Sort by started_at descending
        deployments.sort(key=lambda d: d.started_at, reverse=True)
        
        return deployments[:limit]
    
    async def cancel_build(self, build_id: str) -> bool:
        """Cancel a running build"""
        try:
            if build_id not in self.builds:
                logger.warning(f"Build not found: {build_id}")
                return False
            
            build = self.builds[build_id]
            
            if build.status not in [BuildStatus.PENDING, BuildStatus.RUNNING]:
                logger.warning(f"Build cannot be cancelled: {build_id}")
                return False
            
            build.status = BuildStatus.CANCELLED
            build.completed_at = datetime.now().isoformat()
            
            logger.info(f"Build cancelled: {build_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cancelling build {build_id}: {e}")
            return False
    
    async def rollback_deployment(self, deployment_id: str) -> bool:
        """Rollback a deployment"""
        try:
            if deployment_id not in self.deployments:
                logger.warning(f"Deployment not found: {deployment_id}")
                return False
            
            deployment = self.deployments[deployment_id]
            
            if deployment.status != DeploymentStatus.SUCCESS:
                logger.warning(f"Deployment cannot be rolled back: {deployment_id}")
                return False
            
            deployment.status = DeploymentStatus.ROLLBACK
            deployment.completed_at = datetime.now().isoformat()
            
            logger.info(f"Deployment rollback initiated: {deployment_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error rolling back deployment {deployment_id}: {e}")
            return False
    
    async def get_cicd_analytics(self) -> Dict[str, Any]:
        """Get CI/CD analytics"""
        try:
            # Build statistics
            total_builds = len(self.builds)
            successful_builds = len([b for b in self.builds.values() if b.status == BuildStatus.SUCCESS])
            failed_builds = len([b for b in self.builds.values() if b.status == BuildStatus.FAILED])
            running_builds = len([b for b in self.builds.values() if b.status == BuildStatus.RUNNING])
            
            
            # Deployment statistics
            total_deployments = len(self.deployments)
            successful_deployments = len([d for d in self.deployments.values() if d.status == DeploymentStatus.SUCCESS])
            failed_deployments = len([d for d in self.deployments.values() if d.status == DeploymentStatus.FAILED])
            running_deployments = len([d for d in self.deployments.values() if d.status == DeploymentStatus.DEPLOYING])
            
            # Pipeline statistics
            total_pipelines = len(self.pipelines)
            enabled_pipelines = len([p for p in self.pipelines.values() if p.enabled])
            
            # Recent activity
            recent_builds = [
                b for b in self.builds.values()
                if datetime.fromisoformat(b.started_at) > datetime.now() - timedelta(hours=24)
            ]
            
            return {
                "builds": {
                    "total": total_builds,
                    "successful": successful_builds,
                    "failed": failed_builds,
                    "running": running_builds,
                    "success_rate": successful_builds / total_builds if total_builds > 0 else 0
                },
                },
                "deployments": {
                    "total": total_deployments,
                    "successful": successful_deployments,
                    "failed": failed_deployments,
                    "running": running_deployments,
                    "success_rate": successful_deployments / total_deployments if total_deployments > 0 else 0
                },
                "pipelines": {
                    "total": total_pipelines,
                    "enabled": enabled_pipelines
                },
                "recent_activity": {
                    "builds_24h": len(recent_builds)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting CI/CD analytics: {e}")
            return {"error": str(e)}
    
    async def _queue_build(self, build_id: str):
        """Queue build for processing"""
        try:
            if self.redis_client:
                await self.redis_client.lpush("build_queue", build_id)
        except Exception as e:
            logger.error(f"❌ Error queuing build: {e}")
    
        try:
            if self.redis_client:
        except Exception as e:
    
    async def _queue_deployment(self, deployment_id: str):
        """Queue deployment for processing"""
        try:
            if self.redis_client:
                await self.redis_client.lpush("deployment_queue", deployment_id)
        except Exception as e:
            logger.error(f"❌ Error queuing deployment: {e}")
    
    async def _process_build_queue(self):
        """Process build queue"""
        while self.running:
            try:
                if self.redis_client:
                    # Get build from queue
                    build_id = await self.redis_client.brpop("build_queue", timeout=1)
                    if build_id:
                        build_id = build_id[1].decode()
                        await self._execute_build(build_id)
                else:
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"❌ Error processing build queue: {e}")
                await asyncio.sleep(5)
    
        while self.running:
            try:
                if self.redis_client:
    
    async def _process_deployment_queue(self):
        """Process deployment queue"""
        while self.running:
            try:
                if self.redis_client:
                    # Get deployment from queue
                    deployment_id = await self.redis_client.brpop("deployment_queue", timeout=1)
                    if deployment_id:
                        deployment_id = deployment_id[1].decode()
                        await self._execute_deployment(deployment_id)
                else:
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"❌ Error processing deployment queue: {e}")
                await asyncio.sleep(5)
    
    async def _execute_build(self, build_id: str):
        """Execute a build"""
        try:
            if build_id not in self.builds:
                return
            
            build = self.builds[build_id]
            build.status = BuildStatus.RUNNING
            
            logger.info(f"Executing build: {build_id}")
            
            start_time = time.time()
            
            # This would run actual build commands
            
            success = True  # In real implementation, this would be based on actual build results
            
            end_time = time.time()
            duration = int(end_time - start_time)
            
            if success:
                build.status = BuildStatus.SUCCESS
                build.logs.append("Build completed successfully")
            else:
                build.status = BuildStatus.FAILED
                build.error_message = "Build failed"
                build.logs.append("Build failed")
            
            build.completed_at = datetime.now().isoformat()
            build.duration = duration
            
            logger.info(f"Build completed: {build_id} - {build.status.value}")
            
        except Exception as e:
            logger.error(f"❌ Error executing build {build_id}: {e}")
            if build_id in self.builds:
                self.builds[build_id].status = BuildStatus.FAILED
                self.builds[build_id].error_message = str(e)
                self.builds[build_id].completed_at = datetime.now().isoformat()
    
        try:
                return
            
            
            
            
            
            
            end_time = time.time()
            duration = int(end_time - start_time)
            
            if success:
            
            
            
        except Exception as e:
    
    async def _execute_deployment(self, deployment_id: str):
        """Execute a deployment"""
        try:
            if deployment_id not in self.deployments:
                return
            
            deployment = self.deployments[deployment_id]
            deployment.status = DeploymentStatus.DEPLOYING
            
            logger.info(f"Executing deployment: {deployment_id}")
            
            start_time = time.time()
            
            # This would run actual deployment commands
            
            success = True  # In real implementation, this would be based on actual deployment results
            
            end_time = time.time()
            duration = int(end_time - start_time)
            
            if success:
                deployment.status = DeploymentStatus.SUCCESS
                deployment.logs.append("Deployment completed successfully")
            else:
                deployment.status = DeploymentStatus.FAILED
                deployment.error_message = "Deployment failed"
                deployment.logs.append("Deployment failed")
            
            deployment.completed_at = datetime.now().isoformat()
            deployment.duration = duration
            
            logger.info(f"Deployment completed: {deployment_id} - {deployment.status.value}")
            
        except Exception as e:
            logger.error(f"❌ Error executing deployment {deployment_id}: {e}")
            if deployment_id in self.deployments:
                self.deployments[deployment_id].status = DeploymentStatus.FAILED
                self.deployments[deployment_id].error_message = str(e)
                self.deployments[deployment_id].completed_at = datetime.now().isoformat()
    
    async def _cleanup_old_data(self):
        """Clean up old CI/CD data"""
        while self.running:
            try:
                # Clean up old builds (older than 30 days)
                cutoff_date = datetime.now() - timedelta(days=30)
                old_builds = [
                    build_id for build_id, build in self.builds.items()
                    if datetime.fromisoformat(build.started_at) < cutoff_date
                ]
                
                for build_id in old_builds:
                    del self.builds[build_id]
                
                
                
                # Clean up old deployments (older than 30 days)
                old_deployments = [
                    deployment_id for deployment_id, deployment in self.deployments.items()
                    if datetime.fromisoformat(deployment.started_at) < cutoff_date
                ]
                
                for deployment_id in old_deployments:
                    del self.deployments[deployment_id]
                
                
                await asyncio.sleep(86400)  # Clean up daily
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up old data: {e}")
                await asyncio.sleep(3600)
    
    async def _load_cicd_data(self):
        """Load CI/CD data from storage"""
        try:
            if self.redis_client:
                # Load builds
                builds_data = self.redis_client.get("frenly_cicd_builds")
                if builds_data:
                    builds_json = json.loads(builds_data)
                    for build_id, build_data in builds_json.items():
                        build = Build(
                            id=build_id,
                            branch=build_data["branch"],
                            commit=build_data["commit"],
                            status=BuildStatus(build_data["status"]),
                            started_at=build_data["started_at"],
                            completed_at=build_data.get("completed_at"),
                            duration=build_data.get("duration"),
                            logs=build_data.get("logs", []),
                            artifacts=build_data.get("artifacts", []),
                            error_message=build_data.get("error_message")
                        )
                        self.builds[build_id] = build
                
                
                # Load deployments
                deployments_data = self.redis_client.get("frenly_cicd_deployments")
                if deployments_data:
                    deployments_json = json.loads(deployments_data)
                    for deployment_id, deployment_data in deployments_json.items():
                        deployment = Deployment(
                            id=deployment_id,
                            build_id=deployment_data["build_id"],
                            environment=deployment_data["environment"],
                            status=DeploymentStatus(deployment_data["status"]),
                            started_at=deployment_data["started_at"],
                            completed_at=deployment_data.get("completed_at"),
                            duration=deployment_data.get("duration"),
                            logs=deployment_data.get("logs", []),
                            error_message=deployment_data.get("error_message")
                        )
                        self.deployments[deployment_id] = deployment
                
                # Load pipelines
                pipelines_data = self.redis_client.get("frenly_cicd_pipelines")
                if pipelines_data:
                    pipelines_json = json.loads(pipelines_data)
                    for pipeline_id, pipeline_data in pipelines_json.items():
                        pipeline = Pipeline(
                            id=pipeline_id,
                            name=pipeline_data["name"],
                            triggers=pipeline_data["triggers"],
                            stages=pipeline_data["stages"],
                            environment=pipeline_data["environment"],
                            enabled=pipeline_data.get("enabled", True),
                            created_at=pipeline_data["created_at"],
                            updated_at=pipeline_data["updated_at"]
                        )
                        self.pipelines[pipeline_id] = pipeline
                
            
        except Exception as e:
            logger.error(f"❌ Error loading CI/CD data: {e}")
    
    async def _save_cicd_data(self):
        """Save CI/CD data to storage"""
        try:
            if self.redis_client:
                # Save builds
                builds_data = {
                    build_id: {
                        "branch": build.branch,
                        "commit": build.commit,
                        "status": build.status.value,
                        "started_at": build.started_at,
                        "completed_at": build.completed_at,
                        "duration": build.duration,
                        "logs": build.logs,
                        "artifacts": build.artifacts,
                        "error_message": build.error_message
                    }
                    for build_id, build in self.builds.items()
                }
                self.redis_client.setex("frenly_cicd_builds", 86400, json.dumps(builds_data))
                
                
                # Save deployments
                deployments_data = {
                    deployment_id: {
                        "build_id": deployment.build_id,
                        "environment": deployment.environment,
                        "status": deployment.status.value,
                        "started_at": deployment.started_at,
                        "completed_at": deployment.completed_at,
                        "duration": deployment.duration,
                        "logs": deployment.logs,
                        "error_message": deployment.error_message
                    }
                    for deployment_id, deployment in self.deployments.items()
                }
                self.redis_client.setex("frenly_cicd_deployments", 86400, json.dumps(deployments_data))
                
                # Save pipelines
                pipelines_data = {
                    pipeline_id: {
                        "name": pipeline.name,
                        "triggers": pipeline.triggers,
                        "stages": pipeline.stages,
                        "environment": pipeline.environment,
                        "enabled": pipeline.enabled,
                        "created_at": pipeline.created_at,
                        "updated_at": pipeline.updated_at
                    }
                    for pipeline_id, pipeline in self.pipelines.items()
                }
                self.redis_client.setex("frenly_cicd_pipelines", 86400, json.dumps(pipelines_data))
            
        except Exception as e:
            logger.error(f"❌ Error saving CI/CD data: {e}")

# Global CI/CD integration instance
cicd_integration = CICDIntegration()

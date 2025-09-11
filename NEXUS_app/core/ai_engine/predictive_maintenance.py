#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔧 Frenly AI Predictive Maintenance System
Predictive maintenance for Frenly AI infrastructure
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

class MaintenanceType(Enum):
    """Maintenance type enumeration"""
    PREVENTIVE = "preventive"
    PREDICTIVE = "predictive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"

class MaintenanceStatus(Enum):
    """Maintenance status enumeration"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"

class ComponentType(Enum):
    """Component type enumeration"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"
    AGENT = "agent"
    SERVICE = "service"

@dataclass
class Component:
    """System component definition"""
    id: str
    name: str
    component_type: ComponentType
    health_score: float
    last_maintenance: str
    next_maintenance: str
    maintenance_interval: int  # days
    criticality: str  # low, medium, high, critical
    location: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MaintenanceTask:
    """Maintenance task definition"""
    id: str
    component_id: str
    maintenance_type: MaintenanceType
    status: MaintenanceStatus
    scheduled_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration: Optional[int] = None
    description: str = ""
    technician: Optional[str] = None
    notes: List[str] = field(default_factory=list)
    cost: Optional[float] = None

@dataclass
class MaintenancePrediction:
    """Maintenance prediction definition"""
    component_id: str
    predicted_failure_date: str
    confidence: float
    risk_level: str  # low, medium, high, critical
    recommended_actions: List[str] = field(default_factory=list)
    estimated_cost: Optional[float] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

class PredictiveMaintenanceSystem:
    """Predictive maintenance system for Frenly AI"""
    
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
        
        # Maintenance storage
        self.components: Dict[str, Component] = {}
        self.maintenance_tasks: Dict[str, MaintenanceTask] = {}
        self.predictions: Dict[str, MaintenancePrediction] = {}
        
        # Configuration
        self.prediction_horizon = 30  # days
        self.health_threshold = 0.7
        self.critical_health_threshold = 0.3
        self.maintenance_cost_per_hour = 100.0
        
        logger.info("✅ Predictive Maintenance System initialized")
    
    async def start(self):
        """Start the predictive maintenance system"""
        self.running = True
        logger.info("🚀 Starting Predictive Maintenance System...")
        
        # Load existing data
        await self._load_maintenance_data()
        
        # Start background tasks
        asyncio.create_task(self._monitor_components())
        asyncio.create_task(self._generate_predictions())
        asyncio.create_task(self._schedule_maintenance())
        asyncio.create_task(self._cleanup_old_data())
        
        logger.info("✅ Predictive Maintenance System started")
    
    async def stop(self):
        """Stop the predictive maintenance system"""
        self.running = False
        logger.info("🛑 Stopping Predictive Maintenance System...")
        
        # Save maintenance data
        await self._save_maintenance_data()
        
        logger.info("✅ Predictive Maintenance System stopped")
    
    async def add_component(
        self,
        name: str,
        component_type: ComponentType,
        criticality: str,
        location: str,
        maintenance_interval: int = 30,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a new component to monitor"""
        try:
            component_id = f"comp_{int(time.time())}"
            
            component = Component(
                id=component_id,
                name=name,
                component_type=component_type,
                health_score=1.0,
                last_maintenance=datetime.now().isoformat(),
                next_maintenance=(datetime.now() + timedelta(days=maintenance_interval)).isoformat(),
                maintenance_interval=maintenance_interval,
                criticality=criticality,
                location=location,
                metadata=metadata or {}
            )
            
            self.components[component_id] = component
            
            logger.info(f"Component added: {component_id}")
            return component_id
            
        except Exception as e:
            logger.error(f"❌ Error adding component: {e}")
            raise
    
    async def update_component_health(self, component_id: str, health_score: float) -> bool:
        """Update component health score"""
        try:
            if component_id not in self.components:
                logger.warning(f"Component not found: {component_id}")
                return False
            
            component = self.components[component_id]
            component.health_score = max(0.0, min(1.0, health_score))
            
            logger.debug(f"Component health updated: {component_id} = {health_score}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating component health: {e}")
            return False
    
    async def get_component(self, component_id: str) -> Optional[Component]:
        """Get component information"""
        return self.components.get(component_id)
    
    async def list_components(self, component_type: Optional[ComponentType] = None) -> List[Component]:
        """List components with optional type filter"""
        components = list(self.components.values())
        
        if component_type:
            components = [c for c in components if c.component_type == component_type]
        
        return components
    
    async def create_maintenance_task(
        self,
        component_id: str,
        maintenance_type: MaintenanceType,
        scheduled_at: str,
        description: str = "",
        technician: Optional[str] = None
    ) -> str:
        """Create a new maintenance task"""
        try:
            task_id = f"task_{int(time.time())}"
            
            task = MaintenanceTask(
                id=task_id,
                component_id=component_id,
                maintenance_type=maintenance_type,
                status=MaintenanceStatus.SCHEDULED,
                scheduled_at=scheduled_at,
                description=description,
                technician=technician
            )
            
            self.maintenance_tasks[task_id] = task
            
            logger.info(f"Maintenance task created: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"❌ Error creating maintenance task: {e}")
            raise
    
    async def start_maintenance_task(self, task_id: str) -> bool:
        """Start a maintenance task"""
        try:
            if task_id not in self.maintenance_tasks:
                logger.warning(f"Maintenance task not found: {task_id}")
                return False
            
            task = self.maintenance_tasks[task_id]
            
            if task.status != MaintenanceStatus.SCHEDULED:
                logger.warning(f"Task cannot be started: {task_id}")
                return False
            
            task.status = MaintenanceStatus.IN_PROGRESS
            task.started_at = datetime.now().isoformat()
            
            logger.info(f"Maintenance task started: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting maintenance task {task_id}: {e}")
            return False
    
    async def complete_maintenance_task(self, task_id: str, notes: Optional[List[str]] = None) -> bool:
        """Complete a maintenance task"""
        try:
            if task_id not in self.maintenance_tasks:
                logger.warning(f"Maintenance task not found: {task_id}")
                return False
            
            task = self.maintenance_tasks[task_id]
            
            if task.status != MaintenanceStatus.IN_PROGRESS:
                logger.warning(f"Task cannot be completed: {task_id}")
                return False
            
            task.status = MaintenanceStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            
            if task.started_at:
                start_time = datetime.fromisoformat(task.started_at)
                end_time = datetime.fromisoformat(task.completed_at)
                task.duration = int((end_time - start_time).total_seconds() / 3600)  # hours
                task.cost = task.duration * self.maintenance_cost_per_hour
            
            if notes:
                task.notes.extend(notes)
            
            # Update component
            if task.component_id in self.components:
                component = self.components[task.component_id]
                component.last_maintenance = task.completed_at
                component.next_maintenance = (datetime.fromisoformat(task.completed_at) + timedelta(days=component.maintenance_interval)).isoformat()
                component.health_score = 1.0  # Reset health after maintenance
            
            logger.info(f"Maintenance task completed: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error completing maintenance task {task_id}: {e}")
            return False
    
    async def get_maintenance_task(self, task_id: str) -> Optional[MaintenanceTask]:
        """Get maintenance task information"""
        return self.maintenance_tasks.get(task_id)
    
    async def list_maintenance_tasks(
        self,
        status: Optional[MaintenanceStatus] = None,
        component_id: Optional[str] = None
    ) -> List[MaintenanceTask]:
        """List maintenance tasks with optional filters"""
        tasks = list(self.maintenance_tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        if component_id:
            tasks = [t for t in tasks if t.component_id == component_id]
        
        # Sort by scheduled_at
        tasks.sort(key=lambda t: t.scheduled_at)
        
        return tasks
    
    async def get_maintenance_predictions(self) -> List[MaintenancePrediction]:
        """Get all maintenance predictions"""
        return list(self.predictions.values())
    
    async def get_maintenance_analytics(self) -> Dict[str, Any]:
        """Get maintenance analytics"""
        try:
            total_components = len(self.components)
            healthy_components = len([c for c in self.components.values() if c.health_score >= self.health_threshold])
            critical_components = len([c for c in self.components.values() if c.health_score < self.critical_health_threshold])
            
            total_tasks = len(self.maintenance_tasks)
            completed_tasks = len([t for t in self.maintenance_tasks.values() if t.status == MaintenanceStatus.COMPLETED])
            scheduled_tasks = len([t for t in self.maintenance_tasks.values() if t.status == MaintenanceStatus.SCHEDULED])
            in_progress_tasks = len([t for t in self.maintenance_tasks.values() if t.status == MaintenanceStatus.IN_PROGRESS])
            
            total_predictions = len(self.predictions)
            high_risk_predictions = len([p for p in self.predictions.values() if p.risk_level in ["high", "critical"]])
            
            # Component type distribution
            type_distribution = {}
            for component in self.components.values():
                comp_type = component.component_type.value
                type_distribution[comp_type] = type_distribution.get(comp_type, 0) + 1
            
            # Maintenance cost analysis
            total_cost = sum(task.cost for task in self.maintenance_tasks.values() if task.cost)
            avg_cost_per_task = total_cost / completed_tasks if completed_tasks > 0 else 0
            
            return {
                "components": {
                    "total": total_components,
                    "healthy": healthy_components,
                    "critical": critical_components,
                    "health_rate": healthy_components / total_components if total_components > 0 else 0
                },
                "tasks": {
                    "total": total_tasks,
                    "completed": completed_tasks,
                    "scheduled": scheduled_tasks,
                    "in_progress": in_progress_tasks,
                    "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0
                },
                "predictions": {
                    "total": total_predictions,
                    "high_risk": high_risk_predictions,
                    "risk_rate": high_risk_predictions / total_predictions if total_predictions > 0 else 0
                },
                "costs": {
                    "total_cost": total_cost,
                    "avg_cost_per_task": avg_cost_per_task
                },
                "type_distribution": type_distribution,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting maintenance analytics: {e}")
            return {"error": str(e)}
    
    async def _monitor_components(self):
        """Monitor component health"""
        while self.running:
            try:
                for component in self.components.values():
                    # In practice, this would collect real metrics
                    await self._update_component_health_metrics(component)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error monitoring components: {e}")
                await asyncio.sleep(60)
    
    async def _update_component_health_metrics(self, component: Component):
        """Update component health based on metrics"""
        try:
            # In practice, this would analyze real metrics
            degradation_rate = 0.001  # 0.1% per check
            component.health_score = max(0.0, component.health_score - degradation_rate)
            
            # Check if maintenance is overdue
            if datetime.fromisoformat(component.next_maintenance) < datetime.now():
                logger.warning(f"Component {component.id} maintenance overdue")
                
                # Create emergency maintenance task
                await self.create_maintenance_task(
                    component.id,
                    MaintenanceType.EMERGENCY,
                    datetime.now().isoformat(),
                    "Emergency maintenance - overdue"
                )
            
        except Exception as e:
            logger.error(f"❌ Error updating component health metrics: {e}")
    
    async def _generate_predictions(self):
        """Generate maintenance predictions"""
        while self.running:
            try:
                for component in self.components.values():
                    # Generate prediction based on health score and trends
                    prediction = await self._predict_component_failure(component)
                    if prediction:
                        self.predictions[component.id] = prediction
                
                await asyncio.sleep(3600)  # Generate predictions hourly
                
            except Exception as e:
                logger.error(f"❌ Error generating predictions: {e}")
                await asyncio.sleep(60)
    
    async def _predict_component_failure(self, component: Component) -> Optional[MaintenancePrediction]:
        """Predict component failure"""
        try:
            # Simple prediction based on health score
            # In practice, this would use ML models
            
            if component.health_score > 0.8:
                return None  # No prediction needed
            
            # Calculate days until failure based on health score
            health_deficit = 1.0 - component.health_score
            days_until_failure = int(health_deficit * 30)  # Rough estimate
            
            predicted_date = (datetime.now() + timedelta(days=days_until_failure)).isoformat()
            
            # Determine risk level
            if component.health_score < 0.3:
                risk_level = "critical"
            elif component.health_score < 0.5:
                risk_level = "high"
            elif component.health_score < 0.7:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            # Generate recommended actions
            recommended_actions = []
            if component.health_score < 0.5:
                recommended_actions.append("Schedule immediate maintenance")
            if component.health_score < 0.7:
                recommended_actions.append("Monitor closely")
            if component.criticality == "critical":
                recommended_actions.append("Prepare backup component")
            
            prediction = MaintenancePrediction(
                component_id=component.id,
                predicted_failure_date=predicted_date,
                confidence=1.0 - component.health_score,
                risk_level=risk_level,
                recommended_actions=recommended_actions,
                estimated_cost=1000.0 if risk_level in ["high", "critical"] else 500.0
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"❌ Error predicting component failure: {e}")
            return None
    
    async def _schedule_maintenance(self):
        """Schedule maintenance tasks based on predictions"""
        while self.running:
            try:
                for prediction in self.predictions.values():
                    if prediction.risk_level in ["high", "critical"]:
                        # Check if maintenance is already scheduled
                        existing_tasks = [
                            t for t in self.maintenance_tasks.values()
                            if t.component_id == prediction.component_id and t.status == MaintenanceStatus.SCHEDULED
                        ]
                        
                        if not existing_tasks:
                            # Schedule maintenance
                            scheduled_date = (datetime.now() + timedelta(days=1)).isoformat()
                            await self.create_maintenance_task(
                                prediction.component_id,
                                MaintenanceType.PREDICTIVE,
                                scheduled_date,
                                f"Predictive maintenance - {prediction.risk_level} risk"
                            )
                
                await asyncio.sleep(3600)  # Check hourly
                
            except Exception as e:
                logger.error(f"❌ Error scheduling maintenance: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_old_data(self):
        """Clean up old data"""
        while self.running:
            try:
                # Clean up old predictions (older than 7 days)
                cutoff_date = datetime.now() - timedelta(days=7)
                old_predictions = [
                    comp_id for comp_id, prediction in self.predictions.items()
                    if datetime.fromisoformat(prediction.created_at) < cutoff_date
                ]
                
                for comp_id in old_predictions:
                    del self.predictions[comp_id]
                
                # Clean up old completed tasks (older than 90 days)
                old_tasks = [
                    task_id for task_id, task in self.maintenance_tasks.items()
                    if task.status == MaintenanceStatus.COMPLETED and
                    task.completed_at and
                    datetime.fromisoformat(task.completed_at) < datetime.now() - timedelta(days=90)
                ]
                
                for task_id in old_tasks:
                    del self.maintenance_tasks[task_id]
                
                if old_predictions or old_tasks:
                    logger.info(f"Cleaned up {len(old_predictions)} old predictions and {len(old_tasks)} old tasks")
                
                await asyncio.sleep(86400)  # Clean up daily
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up old data: {e}")
                await asyncio.sleep(3600)
    
    async def _load_maintenance_data(self):
        """Load maintenance data from storage"""
        try:
            if self.redis_client:
                # Load components
                components_data = self.redis_client.get("frenly_maintenance_components")
                if components_data:
                    components_json = json.loads(components_data)
                    for comp_id, comp_data in components_json.items():
                        component = Component(
                            id=comp_id,
                            name=comp_data["name"],
                            component_type=ComponentType(comp_data["component_type"]),
                            health_score=comp_data["health_score"],
                            last_maintenance=comp_data["last_maintenance"],
                            next_maintenance=comp_data["next_maintenance"],
                            maintenance_interval=comp_data["maintenance_interval"],
                            criticality=comp_data["criticality"],
                            location=comp_data["location"],
                            metadata=comp_data.get("metadata", {})
                        )
                        self.components[comp_id] = component
                
                # Load maintenance tasks
                tasks_data = self.redis_client.get("frenly_maintenance_tasks")
                if tasks_data:
                    tasks_json = json.loads(tasks_data)
                    for task_id, task_data in tasks_json.items():
                        task = MaintenanceTask(
                            id=task_id,
                            component_id=task_data["component_id"],
                            maintenance_type=MaintenanceType(task_data["maintenance_type"]),
                            status=MaintenanceStatus(task_data["status"]),
                            scheduled_at=task_data["scheduled_at"],
                            started_at=task_data.get("started_at"),
                            completed_at=task_data.get("completed_at"),
                            duration=task_data.get("duration"),
                            description=task_data.get("description", ""),
                            technician=task_data.get("technician"),
                            notes=task_data.get("notes", []),
                            cost=task_data.get("cost")
                        )
                        self.maintenance_tasks[task_id] = task
                
                # Load predictions
                predictions_data = self.redis_client.get("frenly_maintenance_predictions")
                if predictions_data:
                    predictions_json = json.loads(predictions_data)
                    for comp_id, prediction_data in predictions_json.items():
                        prediction = MaintenancePrediction(
                            component_id=comp_id,
                            predicted_failure_date=prediction_data["predicted_failure_date"],
                            confidence=prediction_data["confidence"],
                            risk_level=prediction_data["risk_level"],
                            recommended_actions=prediction_data.get("recommended_actions", []),
                            estimated_cost=prediction_data.get("estimated_cost"),
                            created_at=prediction_data["created_at"]
                        )
                        self.predictions[comp_id] = prediction
                
                logger.info(f"Loaded {len(self.components)} components, {len(self.maintenance_tasks)} tasks, {len(self.predictions)} predictions")
            
        except Exception as e:
            logger.error(f"❌ Error loading maintenance data: {e}")
    
    async def _save_maintenance_data(self):
        """Save maintenance data to storage"""
        try:
            if self.redis_client:
                # Save components
                components_data = {
                    comp_id: {
                        "name": component.name,
                        "component_type": component.component_type.value,
                        "health_score": component.health_score,
                        "last_maintenance": component.last_maintenance,
                        "next_maintenance": component.next_maintenance,
                        "maintenance_interval": component.maintenance_interval,
                        "criticality": component.criticality,
                        "location": component.location,
                        "metadata": component.metadata
                    }
                    for comp_id, component in self.components.items()
                }
                self.redis_client.setex("frenly_maintenance_components", 86400, json.dumps(components_data))
                
                # Save maintenance tasks
                tasks_data = {
                    task_id: {
                        "component_id": task.component_id,
                        "maintenance_type": task.maintenance_type.value,
                        "status": task.status.value,
                        "scheduled_at": task.scheduled_at,
                        "started_at": task.started_at,
                        "completed_at": task.completed_at,
                        "duration": task.duration,
                        "description": task.description,
                        "technician": task.technician,
                        "notes": task.notes,
                        "cost": task.cost
                    }
                    for task_id, task in self.maintenance_tasks.items()
                }
                self.redis_client.setex("frenly_maintenance_tasks", 86400, json.dumps(tasks_data))
                
                # Save predictions
                predictions_data = {
                    comp_id: {
                        "predicted_failure_date": prediction.predicted_failure_date,
                        "confidence": prediction.confidence,
                        "risk_level": prediction.risk_level,
                        "recommended_actions": prediction.recommended_actions,
                        "estimated_cost": prediction.estimated_cost,
                        "created_at": prediction.created_at
                    }
                    for comp_id, prediction in self.predictions.items()
                }
                self.redis_client.setex("frenly_maintenance_predictions", 86400, json.dumps(predictions_data))
            
        except Exception as e:
            logger.error(f"❌ Error saving maintenance data: {e}")

# Global predictive maintenance system instance
predictive_maintenance = PredictiveMaintenanceSystem()

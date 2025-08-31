#!/usr/bin/env python3
"""
Orchestration Manager - Main Coordination Hub

This module implements the OrchestrationManager class that provides
the main coordination hub for all orchestration components in the
forensic platform.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

# from ..taskmaster.models.job import Job, JobPriority, JobStatus, JobType
from .agent_communication import AgentCommunication
from .agent_coordinator import AgentCoordinator
from .multi_agent_orchestrator import MultiAgentOrchestrator
from .workflow_orchestrator import WorkflowOrchestrator


class OrchestrationMode(Enum):
    """Orchestration modes for the platform."""

    AUTOMATED = "automated"  # Fully automated orchestration
    SEMI_AUTOMATED = "semi_automated"  # Semi-automated with human oversight
    MANUAL = "manual"  # Manual orchestration
    HYBRID = "hybrid"  # Hybrid approach


class SystemStatus(Enum):
    """Overall system status."""

    STARTING = "starting"  # System is starting up
    RUNNING = "running"  # System is running normally
    MAINTENANCE = "maintenance"  # System in maintenance mode
    DEGRADED = "degraded"  # System performance degraded
    ERROR = "error"  # System has errors
    STOPPING = "stopping"  # System is shutting down


@dataclass
class OrchestrationConfig:
    """Configuration for the orchestration system."""

    mode: OrchestrationMode
    max_concurrent_agents: int
    max_concurrent_workflows: int
    max_concurrent_sessions: int
    agent_timeout: int
    workflow_timeout: int
    message_timeout: int
    heartbeat_interval: int
    performance_update_interval: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """System-wide performance metrics."""

    total_agents: int
    active_agents: int
    total_workflows: int
    active_workflows: int
    total_sessions: int
    active_sessions: int
    total_messages: int
    system_uptime: float
    performance_score: float
    last_updated: datetime


class OrchestrationManager:
    """
    Main orchestration manager and coordination hub.

    The OrchestrationManager is responsible for:
    - Coordinating all orchestration components
    - Managing system-wide orchestration policies
    - Monitoring overall system health and performance
    - Providing unified interface for orchestration operations
    - Managing system configuration and scaling
    """

    def __init__(self, config: OrchestrationConfig):
        """Initialize the OrchestrationManager."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # System status
        self.system_status = SystemStatus.STARTING
        self.start_time = datetime.utcnow()

        # Orchestration components
        self.multi_agent_orchestrator: Optional[MultiAgentOrchestrator] = None
        self.agent_coordinator: Optional[AgentCoordinator] = None
        self.workflow_orchestrator: Optional[WorkflowOrchestrator] = None
        self.agent_communication: Optional[AgentCommunication] = None

        # Component status tracking
        self.component_status: Dict[str, str] = {}
        self.component_health: Dict[str, float] = {}

        # System metrics
        self.system_metrics = SystemMetrics(
            total_agents=0,
            active_agents=0,
            total_workflows=0,
            active_workflows=0,
            total_sessions=0,
            active_sessions=0,
            total_messages=0,
            system_uptime=0.0,
            performance_score=0.0,
            last_updated=datetime.utcnow(),
        )

        # Performance tracking
        self.performance_history: deque = deque(maxlen=1000)
        self.error_log: deque = deque(maxlen=1000)

        # Event loop
        self.loop = asyncio.get_event_loop()

        self.logger.info("OrchestrationManager initialized successfully")

    async def start(self):
        """Start the orchestration system."""
        try:
            self.logger.info("Starting orchestration system...")
            self.system_status = SystemStatus.STARTING

            # Initialize orchestration components
            await self._initialize_orchestration_components()

            # Start all components
            await self._start_all_components()

            # Start background tasks
            asyncio.create_task(self._monitor_system_health())
            asyncio.create_task(self._update_system_metrics())
            asyncio.create_task(self._performance_optimization())

            # Update system status
            self.system_status = SystemStatus.RUNNING
            self.logger.info("Orchestration system started successfully")

        except Exception as e:
            self.logger.error(f"Error starting orchestration system: {e}")
            self.system_status = SystemStatus.ERROR
            raise

    async def stop(self):
        """Stop the orchestration system."""
        try:
            self.logger.info("Stopping orchestration system...")
            self.system_status = SystemStatus.STOPPING

            # Stop all components
            await self._stop_all_components()

            self.logger.info("Orchestration system stopped")

        except Exception as e:
            self.logger.error(f"Error stopping orchestration system: {e}")
            raise

    async def _initialize_orchestration_components(self):
        """Initialize all orchestration components."""
        try:
            # Initialize Multi-Agent Orchestrator
            multi_agent_config = {
                "max_concurrent_workflows": self.config.max_concurrent_workflows,
                "agent_timeout": self.config.agent_timeout,
                "heartbeat_interval": self.config.heartbeat_interval,
            }
            self.multi_agent_orchestrator = MultiAgentOrchestrator(multi_agent_config)

            # Initialize Agent Coordinator
            agent_coord_config = {
                "max_concurrent_sessions": self.config.max_concurrent_sessions,
                "interaction_timeout": self.config.message_timeout,
                "coordination_interval": 5,
            }
            self.agent_coordinator = AgentCoordinator(agent_coord_config)

            # Initialize Workflow Orchestrator
            workflow_config = {
                "max_concurrent_workflows": self.config.max_concurrent_workflows,
                "workflow_timeout": self.config.workflow_timeout,
                "step_timeout": 300,
                "max_retries": 3,
            }
            self.workflow_orchestrator = WorkflowOrchestrator(workflow_config)

            # Initialize Agent Communication
            communication_config = {
                "max_message_size": 1048576,
                "message_timeout": self.config.message_timeout,
                "max_queue_size": 1000,
                "heartbeat_interval": self.config.heartbeat_interval,
            }
            self.agent_communication = AgentCommunication(communication_config)

            self.logger.info("All orchestration components initialized")

        except Exception as e:
            self.logger.error(f"Error initializing orchestration components: {e}")
            raise

    async def _start_all_components(self):
        """Start all orchestration components."""
        try:
            # Start components in order
            if self.multi_agent_orchestrator:
                await self.multi_agent_orchestrator.start()
                self.component_status["multi_agent_orchestrator"] = "running"

            if self.agent_coordinator:
                await self.agent_coordinator.start()
                self.component_status["agent_coordinator"] = "running"

            if self.workflow_orchestrator:
                await self.workflow_orchestrator.start()
                self.component_status["workflow_orchestrator"] = "running"

            if self.agent_communication:
                await self.agent_communication.start()
                self.component_status["agent_communication"] = "running"

            self.logger.info("All orchestration components started")

        except Exception as e:
            self.logger.error(f"Error starting orchestration components: {e}")
            raise

    async def _stop_all_components(self):
        """Stop all orchestration components."""
        try:
            # Stop components in reverse order
            if self.agent_communication:
                await self.agent_communication.stop()
                self.component_status["agent_communication"] = "stopped"

            if self.workflow_orchestrator:
                await self.workflow_orchestrator.stop()
                self.component_status["workflow_orchestrator"] = "stopped"

            if self.agent_coordinator:
                await self.agent_coordinator.stop()
                self.component_status["agent_coordinator"] = "stopped"

            if self.multi_agent_orchestrator:
                await self.multi_agent_orchestrator.stop()
                self.component_status["multi_agent_orchestrator"] = "stopped"

            self.logger.info("All orchestration components stopped")

        except Exception as e:
            self.logger.error(f"Error stopping orchestration components: {e}")
            raise

    async def register_agent(self, agent_info: Dict[str, Any]) -> bool:
        """Register an agent with the orchestration system."""
        try:
            agent_id = agent_info.get("id")
            if not agent_id:
                raise ValueError("Agent ID is required")

            # Register with all components
            success = True

            if self.multi_agent_orchestrator:
                success &= await self.multi_agent_orchestrator.register_agent(
                    agent_info
                )

            if self.agent_coordinator:
                capabilities = agent_info.get("capabilities", [])
                specializations = agent_info.get("specializations", [])
                success &= await self.agent_coordinator.register_agent_capabilities(
                    agent_id, capabilities, specializations
                )

            if self.agent_communication:
                success &= await self.agent_communication.register_agent(agent_id)

            if success:
                self.logger.info(
                    f"Agent {agent_id} registered successfully with all components"
                )
                return True
            else:
                self.logger.error(
                    f"Failed to register agent {agent_id} with all components"
                )
                return False

        except Exception as e:
            self.logger.error(f"Error registering agent: {e}")
            return False

    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the orchestration system."""
        try:
            # Unregister from all components
            success = True

            if self.multi_agent_orchestrator:
                success &= await self.multi_agent_orchestrator.unregister_agent(
                    agent_id
                )

            if self.agent_coordinator:
                # Note: AgentCoordinator doesn't have unregister method, so we'll skip it
                pass

            if self.agent_communication:
                success &= await self.agent_communication.unregister_agent(agent_id)

            if success:
                self.logger.info(
                    f"Agent {agent_id} unregistered successfully from all components"
                )
                return True
            else:
                self.logger.error(
                    f"Failed to unregister agent {agent_id} from all components"
                )
                return False

        except Exception as e:
            self.logger.error(f"Error unregistering agent {agent_id}: {e}")
            return False

    async def create_workflow(self, workflow_config: Dict[str, Any]) -> str:
        """Create a workflow through the workflow orchestrator."""
        try:
            if not self.workflow_orchestrator:
                raise RuntimeError("Workflow orchestrator not available")

            # Extract workflow parameters
            workflow_type = workflow_config.get("type")
            name = workflow_config.get("name")
            description = workflow_config.get("description")
            steps = workflow_config.get("steps", [])

            # Create workflow
            workflow_id = await self.workflow_orchestrator.create_workflow(
                workflow_type, name, description, steps
            )

            self.logger.info(f"Created workflow: {workflow_id}")
            return workflow_id

        except Exception as e:
            self.logger.error(f"Error creating workflow: {e}")
            raise

    async def send_message(self, message_config: Dict[str, Any]) -> str:
        """Send a message through the communication system."""
        try:
            if not self.agent_communication:
                raise RuntimeError("Agent communication not available")

            # Extract message parameters
            message_type = message_config.get("type")
            priority = message_config.get("priority")
            source_agent = message_config.get("source_agent")
            target_agents = message_config.get("target_agents", [])
            subject = message_config.get("subject")
            content = message_config.get("content", {})

            # Send message
            message_id = await self.agent_communication.send_message(
                message_type, priority, source_agent, target_agents, subject, content
            )

            self.logger.info(f"Sent message: {message_id}")
            return message_id

        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            raise

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            status = {
                "system_status": self.system_status.value,
                "start_time": self.start_time.isoformat(),
                "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
                "component_status": self.component_status.copy(),
                "component_health": self.component_health.copy(),
                "system_metrics": {
                    "total_agents": self.system_metrics.total_agents,
                    "active_agents": self.system_metrics.active_agents,
                    "total_workflows": self.system_metrics.total_workflows,
                    "active_workflows": self.system_metrics.active_workflows,
                    "total_sessions": self.system_metrics.total_sessions,
                    "active_sessions": self.system_metrics.active_sessions,
                    "total_messages": self.system_metrics.total_messages,
                    "performance_score": self.system_metrics.performance_score,
                },
                "configuration": {
                    "mode": self.config.mode.value,
                    "max_concurrent_agents": self.config.max_concurrent_agents,
                    "max_concurrent_workflows": self.config.max_concurrent_workflows,
                    "max_concurrent_sessions": self.config.max_concurrent_sessions,
                },
            }

            return status

        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}

    async def _monitor_system_health(self):
        """Monitor overall system health."""
        while True:
            try:
                if self.system_status == SystemStatus.RUNNING:
                    # Check component health
                    await self._check_component_health()

                    # Update system status based on component health
                    await self._update_system_status()

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Error monitoring system health: {e}")
                await asyncio.sleep(30)

    async def _check_component_health(self):
        """Check health of individual components."""
        try:
            # Check Multi-Agent Orchestrator
            if self.multi_agent_orchestrator:
                try:
                    metrics = self.multi_agent_orchestrator.get_performance_metrics()
                    self.component_health["multi_agent_orchestrator"] = 1.0
                except Exception:
                    logger.error(f"Error: {e}")
                    self.component_health["multi_agent_orchestrator"] = 0.0

            # Check Agent Coordinator
            if self.agent_coordinator:
                try:
                    metrics = self.agent_coordinator.get_performance_metrics()
                    self.component_health["agent_coordinator"] = 1.0
                except Exception:
                    logger.error(f"Error: {e}")
                    self.component_health["agent_coordinator"] = 0.0

            # Check Workflow Orchestrator
            if self.workflow_orchestrator:
                try:
                    metrics = self.workflow_orchestrator.get_performance_metrics()
                    self.component_health["workflow_orchestrator"] = 1.0
                except Exception:
                    logger.error(f"Error: {e}")
                    self.component_health["workflow_orchestrator"] = 0.0

            # Check Agent Communication
            if self.agent_communication:
                try:
                    metrics = self.agent_communication.get_performance_metrics()
                    self.component_health["agent_communication"] = 1.0
                except Exception:
                    logger.error(f"Error: {e}")
                    self.component_health["agent_communication"] = 0.0

        except Exception as e:
            self.logger.error(f"Error checking component health: {e}")

    async def _update_system_status(self):
        """Update system status based on component health."""
        try:
            # Calculate overall health score
            if self.component_health:
                overall_health = sum(self.component_health.values()) / len(
                    self.component_health
                )

                # Update system status based on health
                if overall_health >= 0.9:
                    self.system_status = SystemStatus.RUNNING
                elif overall_health >= 0.7:
                    self.system_status = SystemStatus.DEGRADED
                else:
                    self.system_status = SystemStatus.ERROR

        except Exception as e:
            self.logger.error(f"Error updating system status: {e}")

    async def _update_system_metrics(self):
        """Update system-wide metrics."""
        while True:
            try:
                if self.system_status == SystemStatus.RUNNING:
                    # Collect metrics from all components
                    await self._collect_component_metrics()

                    # Update system metrics
                    self.system_metrics.last_updated = datetime.utcnow()
                    self.system_metrics.system_uptime = (
                        datetime.utcnow() - self.start_time
                    ).total_seconds()

                    # Calculate performance score
                    if self.component_health:
                        self.system_metrics.performance_score = sum(
                            self.component_health.values()
                        ) / len(self.component_health)

                    # Store in history
                    self.performance_history.append(
                        {
                            "timestamp": datetime.utcnow().isoformat(),
                            "metrics": {
                                "total_agents": self.system_metrics.total_agents,
                                "active_workflows": self.system_metrics.active_workflows,
                                "performance_score": self.system_metrics.performance_score,
                            },
                        }
                    )

                await asyncio.sleep(self.config.performance_update_interval)

            except Exception as e:
                self.logger.error(f"Error updating system metrics: {e}")
                await asyncio.sleep(self.config.performance_update_interval)

    async def _collect_component_metrics(self):
        """Collect metrics from all components."""
        try:
            # Collect from Multi-Agent Orchestrator
            if self.multi_agent_orchestrator:
                try:
                    metrics = self.multi_agent_orchestrator.get_performance_metrics()
                    self.system_metrics.total_agents = metrics.get("total_agents", 0)
                    self.system_metrics.active_workflows = metrics.get(
                        "active_workflows", 0
                    )
                except Exception:
                    logger.error(f"Error: {e}")
                    pass

            # Collect from Agent Coordinator
            if self.agent_coordinator:
                try:
                    metrics = self.agent_coordinator.get_performance_metrics()
                    self.system_metrics.total_sessions = metrics.get(
                        "total_sessions", 0
                    )
                    self.system_metrics.active_sessions = metrics.get(
                        "active_sessions", 0
                    )
                except Exception:
                    logger.error(f"Error: {e}")
                    pass

            # Collect from Workflow Orchestrator
            if self.workflow_orchestrator:
                try:
                    metrics = self.workflow_orchestrator.get_performance_metrics()
                    self.system_metrics.total_workflows = metrics.get(
                        "total_workflows", 0
                    )
                    self.system_metrics.active_workflows = metrics.get(
                        "active_workflows", 0
                    )
                except Exception:
                    logger.error(f"Error: {e}")
                    pass

            # Collect from Agent Communication
            if self.agent_communication:
                try:
                    metrics = self.agent_communication.get_performance_metrics()
                    self.system_metrics.total_messages = metrics.get(
                        "total_messages", 0
                    )
                except Exception:
                    logger.error(f"Error: {e}")
                    pass

        except Exception as e:
            self.logger.error(f"Error collecting component metrics: {e}")

    async def _performance_optimization(self):
        """Perform performance optimization tasks."""
        while True:
            try:
                if self.system_status == SystemStatus.RUNNING:
                    # Check for performance issues
                    await self._check_performance_issues()

                    # Apply optimizations if needed
                    await self._apply_optimizations()

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                self.logger.error(f"Error in performance optimization: {e}")
                await asyncio.sleep(300)

    async def _check_performance_issues(self):
        """Check for performance issues."""
        try:
            # Check if any components are overloaded
            if (
                self.system_metrics.active_workflows
                > self.config.max_concurrent_workflows * 0.8
            ):
                self.logger.warning("Workflow orchestrator approaching capacity limit")

            if (
                self.system_metrics.active_sessions
                > self.config.max_concurrent_sessions * 0.8
            ):
                self.logger.warning("Agent coordinator approaching capacity limit")

            # Check for performance degradation
            if self.system_metrics.performance_score < 0.8:
                self.logger.warning("System performance degraded")

        except Exception as e:
            self.logger.error(f"Error checking performance issues: {e}")

    async def _apply_optimizations(self):
        """Apply performance optimizations."""
        try:
            # This would implement various optimization strategies
            # For now, just log that optimization is available
            pass

        except Exception as e:
            self.logger.error(f"Error applying optimizations: {e}")

    def get_performance_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get performance history."""
        try:
            return list(self.performance_history)[-limit:]
        except Exception as e:
            self.logger.error(f"Error getting performance history: {e}")
            return []

    def get_error_log(self, limit: int = 100) -> List[str]:
        """Get error log."""
        try:
            return list(self.error_log)[-limit:]
        except Exception as e:
            self.logger.error(f"Error getting error log: {e}")
            return []


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = OrchestrationConfig(
        mode=OrchestrationMode.AUTOMATED,
        max_concurrent_agents=50,
        max_concurrent_workflows=10,
        max_concurrent_sessions=20,
        agent_timeout=300,
        workflow_timeout=3600,
        message_timeout=300,
        heartbeat_interval=30,
        performance_update_interval=60,
    )

    # Initialize orchestration manager
    manager = OrchestrationManager(config)

    print("OrchestrationManager system initialized successfully!")

#!/usr/bin/env python3
"""
Workflow Integration Manager - Comprehensive Workflow Integration Hub

This module implements the WorkflowIntegrationManager class that provides
comprehensive integration between all workflow components in the Nexus Platform.

The WorkflowIntegrationManager serves as the central hub for:
- Orchestrating workflows across all system components
- Managing data flow between different services
- Coordinating security and compliance workflows
- Providing unified workflow control interface
- Monitoring and optimizing workflow performance
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from orchestration_manager import OrchestrationManager, OrchestrationMode, SystemStatus
from agent_coordinator import AgentCoordinator, CoordinationType, InteractionType
from message_queue_system import MessageQueueSystem, MessagePriority, MessageType
from workflow_orchestrator import WorkflowOrchestrator


class IntegrationStatus(Enum):
    """Status of integration components."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DEGRADED = "degraded"
    ERROR = "error"


class WorkflowType(Enum):
    """Types of workflows in the system."""

    SECURITY_AUDIT = "security_audit"
    COMPLIANCE_CHECK = "compliance_check"
    DATA_PROCESSING = "data_processing"
    AI_ANALYSIS = "ai_analysis"
    USER_WORKFLOW = "user_workflow"
    SYSTEM_MAINTENANCE = "system_maintenance"
    INTEGRATION_TEST = "integration_test"


@dataclass
class WorkflowIntegrationConfig:
    """Configuration for workflow integration."""

    # Integration settings
    enable_security_integration: bool = True
    enable_frontend_integration: bool = True
    enable_datastore_integration: bool = True
    enable_external_integration: bool = True

    # Performance settings
    max_concurrent_integrations: int = 50
    integration_timeout: int = 300  # 5 minutes
    heartbeat_interval: int = 30  # 30 seconds

    # Security settings
    security_policy_enforcement: bool = True
    compliance_monitoring: bool = True
    audit_logging: bool = True

    # Monitoring settings
    performance_monitoring: bool = True
    error_tracking: bool = True
    metrics_collection: bool = True


@dataclass
class IntegrationComponent:
    """Information about an integrated component."""

    component_id: str
    component_type: str
    integration_status: IntegrationStatus
    last_heartbeat: datetime
    performance_metrics: Dict[str, float]
    error_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowIntegration:
    """Information about a workflow integration."""

    integration_id: str
    workflow_type: WorkflowType
    source_component: str
    target_component: str
    integration_status: IntegrationStatus
    created_at: datetime
    last_updated: datetime
    performance_metrics: Dict[str, float]
    error_log: List[str] = field(default_factory=list)


class WorkflowIntegrationManager:
    """
    Comprehensive workflow integration manager.

    The WorkflowIntegrationManager is responsible for:
    - Managing integration between all system components
    - Coordinating workflow execution across components
    - Ensuring security and compliance integration
    - Monitoring integration health and performance
    - Providing unified workflow control interface
    """

    def __init__(self, config: WorkflowIntegrationConfig):
        """Initialize the WorkflowIntegrationManager."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Integration status
        self.integration_status = IntegrationStatus.DISCONNECTED
        self.start_time = datetime.utcnow()

        # Component tracking
        self.integrated_components: Dict[str, IntegrationComponent] = {}
        self.workflow_integrations: Dict[str, WorkflowIntegration] = {}

        # Orchestration components
        self.orchestration_manager: Optional[OrchestrationManager] = None
        self.agent_coordinator: Optional[AgentCoordinator] = None
        self.message_queue: Optional[MessageQueueSystem] = None
        self.workflow_orchestrator: Optional[WorkflowOrchestrator] = None

        # Performance tracking
        self.performance_metrics: Dict[str, float] = {}
        self.error_log: List[str] = []

        # Integration health monitoring
        self.health_check_task: Optional[asyncio.Task] = None
        self.performance_monitoring_task: Optional[asyncio.Task] = None

        self.logger.info("WorkflowIntegrationManager initialized")

    async def initialize_integration(self) -> bool:
        """Initialize all workflow integrations."""
        try:
            self.logger.info("Initializing workflow integration system...")

            # Initialize orchestration components
            await self._initialize_orchestration_components()

            # Initialize security integration
            if self.config.enable_security_integration:
                await self._initialize_security_integration()

            # Initialize frontend integration
            if self.config.enable_frontend_integration:
                await self._initialize_frontend_integration()

            # Initialize datastore integration
            if self.config.enable_datastore_integration:
                await self._initialize_datastore_integration()

            # Initialize external system integration
            if self.config.enable_external_integration:
                await self._initialize_external_integration()

            # Start monitoring tasks
            await self._start_monitoring_tasks()

            self.integration_status = IntegrationStatus.CONNECTED
            self.logger.info("Workflow integration system initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize workflow integration: {e}")
            self.integration_status = IntegrationStatus.ERROR
            return False

    async def _initialize_orchestration_components(self):
        """Initialize core orchestration components."""
        try:
            # Initialize orchestration manager
            orchestration_config = OrchestrationConfig(
                mode=OrchestrationMode.AUTOMATED,
                max_concurrent_agents=50,
                max_concurrent_workflows=100,
                max_concurrent_sessions=200,
                agent_timeout=600,
                workflow_timeout=1800,
                message_timeout=300,
                heartbeat_interval=30,
                performance_update_interval=60,
            )

            self.orchestration_manager = OrchestrationManager(orchestration_config)
            await self.orchestration_manager.initialize()

            # Initialize agent coordinator
            agent_config = {
                "max_concurrent_sessions": 50,
                "interaction_timeout": 600,
                "coordination_interval": 5,
            }
            self.agent_coordinator = AgentCoordinator(agent_config)
            await self.agent_coordinator.initialize()

            # Initialize message queue system
            queue_config = {
                "max_queues": 20,
                "max_messages_per_queue": 10000,
                "message_ttl": 3600,
                "retry_attempts": 3,
            }
            self.message_queue = MessageQueueSystem(queue_config)
            await self.message_queue.initialize()

            # Initialize workflow orchestrator
            workflow_config = {
                "max_concurrent_workflows": 100,
                "workflow_timeout": 1800,
                "retry_attempts": 3,
            }
            self.workflow_orchestrator = WorkflowOrchestrator(workflow_config)
            await self.workflow_orchestrator.initialize()

            self.logger.info("Orchestration components initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize orchestration components: {e}")
            raise

    async def _initialize_security_integration(self):
        """Initialize security system integration."""
        try:
            self.logger.info("Initializing security integration...")

            # Create security integration component
            security_component = IntegrationComponent(
                component_id="security_system",
                component_type="security",
                integration_status=IntegrationStatus.CONNECTING,
                last_heartbeat=datetime.utcnow(),
                performance_metrics={},
                error_count=0,
            )

            # Initialize security workflows
            await self._create_security_workflows()

            # Update component status
            security_component.integration_status = IntegrationStatus.CONNECTED
            self.integrated_components["security_system"] = security_component

            self.logger.info("Security integration initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize security integration: {e}")
            raise

    async def _initialize_frontend_integration(self):
        """Initialize frontend system integration."""
        try:
            self.logger.info("Initializing frontend integration...")

            # Create frontend integration component
            frontend_component = IntegrationComponent(
                component_id="frontend_system",
                component_type="frontend",
                integration_status=IntegrationStatus.CONNECTING,
                last_heartbeat=datetime.utcnow(),
                performance_metrics={},
                error_count=0,
            )

            # Initialize frontend workflows
            await self._create_frontend_workflows()

            # Update component status
            frontend_component.integration_status = IntegrationStatus.CONNECTED
            self.integrated_components["frontend_system"] = frontend_component

            self.logger.info("Frontend integration initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize frontend integration: {e}")
            raise

    async def _initialize_datastore_integration(self):
        """Initialize datastore system integration."""
        try:
            self.logger.info("Initializing datastore integration...")

            # Create datastore integration component
            datastore_component = IntegrationComponent(
                component_id="datastore_system",
                component_type="datastore",
                integration_status=IntegrationStatus.CONNECTING,
                last_heartbeat=datetime.utcnow(),
                performance_metrics={},
                error_count=0,
            )

            # Initialize datastore workflows
            await self._create_datastore_workflows()

            # Update component status
            datastore_component.integration_status = IntegrationStatus.CONNECTED
            self.integrated_components["datastore_system"] = datastore_component

            self.logger.info("Datastore integration initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize datastore integration: {e}")
            raise

    async def _initialize_external_integration(self):
        """Initialize external system integration."""
        try:
            self.logger.info("Initializing external system integration...")

            # Create external integration component
            external_component = IntegrationComponent(
                component_id="external_systems",
                component_type="external",
                integration_status=IntegrationStatus.CONNECTING,
                last_heartbeat=datetime.utcnow(),
                performance_metrics={},
                error_count=0,
            )

            # Initialize external system workflows
            await self._create_external_workflows()

            # Update component status
            external_component.integration_status = IntegrationStatus.CONNECTED
            self.integrated_components["external_systems"] = external_component

            self.logger.info("External system integration initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize external system integration: {e}")
            raise

    async def _create_security_workflows(self):
        """Create security-related workflows."""
        try:
            # Security audit workflow
            security_audit_workflow = {
                "workflow_id": f"security_audit_{uuid.uuid4().hex[:8]}",
                "workflow_type": WorkflowType.SECURITY_AUDIT,
                "steps": [
                    "security_policy_check",
                    "vulnerability_scan",
                    "compliance_validation",
                    "security_report_generation",
                ],
                "priority": MessagePriority.HIGH,
                "timeout": 1800,
            }

            # Compliance check workflow
            compliance_workflow = {
                "workflow_id": f"compliance_check_{uuid.uuid4().hex[:8]}",
                "workflow_type": WorkflowType.COMPLIANCE_CHECK,
                "steps": [
                    "gdpr_compliance_check",
                    "soc2_compliance_check",
                    "iso27001_compliance_check",
                    "compliance_report_generation",
                ],
                "priority": MessagePriority.HIGH,
                "timeout": 3600,
            }

            # Register workflows
            await self.workflow_orchestrator.register_workflow(security_audit_workflow)
            await self.workflow_orchestrator.register_workflow(compliance_workflow)

            self.logger.info("Security workflows created successfully")

        except Exception as e:
            self.logger.error(f"Failed to create security workflows: {e}")
            raise

    async def _create_frontend_workflows(self):
        """Create frontend-related workflows."""
        try:
            # User workflow management
            user_workflow = {
                "workflow_id": f"user_workflow_{uuid.uuid4().hex[:8]}",
                "workflow_type": WorkflowType.USER_WORKFLOW,
                "steps": [
                    "workflow_creation",
                    "step_execution",
                    "progress_tracking",
                    "completion_handling",
                ],
                "priority": MessagePriority.NORMAL,
                "timeout": 900,
            }

            # Register workflow
            await self.workflow_orchestrator.register_workflow(user_workflow)

            self.logger.info("Frontend workflows created successfully")

        except Exception as e:
            self.logger.error(f"Failed to create frontend workflows: {e}")
            raise

    async def _create_datastore_workflows(self):
        """Create datastore-related workflows."""
        try:
            # Data processing workflow
            data_processing_workflow = {
                "workflow_id": f"data_processing_{uuid.uuid4().hex[:8]}",
                "workflow_type": WorkflowType.DATA_PROCESSING,
                "steps": [
                    "data_validation",
                    "data_transformation",
                    "data_quality_check",
                    "data_storage",
                ],
                "priority": MessagePriority.NORMAL,
                "timeout": 1200,
            }

            # Register workflow
            await self.workflow_orchestrator.register_workflow(data_processing_workflow)

            self.logger.info("Datastore workflows created successfully")

        except Exception as e:
            self.logger.error(f"Failed to create datastore workflows: {e}")
            raise

    async def _create_external_workflows(self):
        """Create external system workflows."""
        try:
            # Integration test workflow
            integration_test_workflow = {
                "workflow_id": f"integration_test_{uuid.uuid4().hex[:8]}",
                "workflow_type": WorkflowType.INTEGRATION_TEST,
                "steps": [
                    "system_connectivity_test",
                    "api_endpoint_test",
                    "data_flow_test",
                    "performance_test",
                ],
                "priority": MessagePriority.NORMAL,
                "timeout": 600,
            }

            # Register workflow
            await self.workflow_orchestrator.register_workflow(
                integration_test_workflow
            )

            self.logger.info("External system workflows created successfully")

        except Exception as e:
            self.logger.error(f"Failed to create external system workflows: {e}")
            raise

    async def _start_monitoring_tasks(self):
        """Start monitoring and health check tasks."""
        try:
            # Start health check task
            self.health_check_task = asyncio.create_task(self._health_check_loop())

            # Start performance monitoring task
            self.performance_monitoring_task = asyncio.create_task(
                self._performance_monitoring_loop()
            )

            self.logger.info("Monitoring tasks started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start monitoring tasks: {e}")
            raise

    async def _health_check_loop(self):
        """Continuous health check loop."""
        while self.integration_status != IntegrationStatus.ERROR:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.config.heartbeat_interval)
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
                await asyncio.sleep(10)  # Shorter interval on error

    async def _performance_monitoring_loop(self):
        """Continuous performance monitoring loop."""
        while self.integration_status != IntegrationStatus.ERROR:
            try:
                await self._collect_performance_metrics()
                await asyncio.sleep(60)  # Collect metrics every minute
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(30)  # Shorter interval on error

    async def _perform_health_check(self):
        """Perform comprehensive health check."""
        try:
            # Check component health
            for component_id, component in self.integrated_components.items():
                # Update heartbeat
                component.last_heartbeat = datetime.utcnow()

                # Check for stale components
                if (
                    datetime.utcnow() - component.last_heartbeat
                ).seconds > self.config.integration_timeout:
                    component.integration_status = IntegrationStatus.DEGRADED
                    self.logger.warning(f"Component {component_id} heartbeat stale")

                # Check error count
                if component.error_count > 10:
                    component.integration_status = IntegrationStatus.ERROR
                    self.logger.error(f"Component {component_id} has too many errors")

            # Update overall integration status
            self._update_integration_status()

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")

    async def _collect_performance_metrics(self):
        """Collect performance metrics from all components."""
        try:
            # Collect orchestration metrics
            if self.orchestration_manager:
                orchestration_metrics = (
                    await self.orchestration_manager.get_system_metrics()
                )
                self.performance_metrics["orchestration"] = (
                    orchestration_metrics.performance_score
                )

            # Collect agent coordination metrics
            if self.agent_coordinator:
                agent_metrics = await self.agent_coordinator.get_performance_metrics()
                self.performance_metrics["agent_coordination"] = agent_metrics.get(
                    "performance_score", 0.0
                )

            # Collect message queue metrics
            if self.message_queue:
                queue_metrics = await self.message_queue.get_performance_metrics()
                self.performance_metrics["message_queue"] = queue_metrics.get(
                    "throughput", 0.0
                )

            # Calculate overall performance score
            if self.performance_metrics:
                overall_score = sum(self.performance_metrics.values()) / len(
                    self.performance_metrics
                )
                self.performance_metrics["overall"] = overall_score

        except Exception as e:
            self.logger.error(f"Performance metrics collection failed: {e}")

    def _update_integration_status(self):
        """Update overall integration status based on component health."""
        try:
            # Count component statuses
            status_counts = {
                IntegrationStatus.CONNECTED: 0,
                IntegrationStatus.DEGRADED: 0,
                IntegrationStatus.ERROR: 0,
                IntegrationStatus.DISCONNECTED: 0,
            }

            for component in self.integrated_components.values():
                status_counts[component.integration_status] += 1

            # Determine overall status
            if status_counts[IntegrationStatus.ERROR] > 0:
                self.integration_status = IntegrationStatus.ERROR
            elif status_counts[IntegrationStatus.DEGRADED] > 0:
                self.integration_status = IntegrationStatus.DEGRADED
            elif status_counts[IntegrationStatus.CONNECTED] == len(
                self.integrated_components
            ):
                self.integration_status = IntegrationStatus.CONNECTED
            else:
                self.integration_status = IntegrationStatus.DISCONNECTED

        except Exception as e:
            self.logger.error(f"Failed to update integration status: {e}")

    async def execute_workflow(
        self, workflow_type: WorkflowType, parameters: Dict[str, Any]
    ) -> str:
        """Execute a workflow of the specified type."""
        try:
            if not self.workflow_orchestrator:
                raise RuntimeError("Workflow orchestrator not initialized")

            # Create workflow execution
            execution_id = await self.workflow_orchestrator.create_workflow_execution(
                workflow_type=workflow_type.value, parameters=parameters
            )

            # Start workflow execution
            await self.workflow_orchestrator.start_workflow(execution_id)

            self.logger.info(f"Workflow execution started: {execution_id}")
            return execution_id

        except Exception as e:
            self.logger.error(f"Failed to execute workflow: {e}")
            raise

    async def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status."""
        try:
            return {
                "overall_status": self.integration_status.value,
                "start_time": self.start_time.isoformat(),
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "component_count": len(self.integrated_components),
                "workflow_count": len(self.workflow_integrations),
                "performance_metrics": self.performance_metrics,
                "component_status": {
                    component_id: {
                        "status": component.integration_status.value,
                        "last_heartbeat": component.last_heartbeat.isoformat(),
                        "error_count": component.error_count,
                        "performance_metrics": component.performance_metrics,
                    }
                    for component_id, component in self.integrated_components.items()
                },
            }

        except Exception as e:
            self.logger.error(f"Failed to get integration status: {e}")
            return {"error": str(e)}

    async def shutdown(self):
        """Shutdown the integration manager gracefully."""
        try:
            self.logger.info("Shutting down WorkflowIntegrationManager...")

            # Cancel monitoring tasks
            if self.health_check_task:
                self.health_check_task.cancel()
            if self.performance_monitoring_task:
                self.performance_monitoring_task.cancel()

            # Shutdown orchestration components
            if self.orchestration_manager:
                await self.orchestration_manager.shutdown()
            if self.agent_coordinator:
                await self.agent_coordinator.shutdown()
            if self.message_queue:
                await self.message_queue.shutdown()
            if self.workflow_orchestrator:
                await self.workflow_orchestrator.shutdown()

            self.integration_status = IntegrationStatus.DISCONNECTED
            self.logger.info("WorkflowIntegrationManager shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


if __name__ == "__main__":
    # Test the integration manager
    async def test_integration():
        config = WorkflowIntegrationConfig()
        manager = WorkflowIntegrationManager(config)

        try:
            success = await manager.initialize_integration()
            if success:
                print("✅ WorkflowIntegrationManager initialized successfully!")

                # Get status
                status = await manager.get_integration_status()
                print(f"📊 Integration Status: {status['overall_status']}")
                print(f"🔧 Components: {status['component_count']}")
                print(f"📋 Workflows: {status['workflow_count']}")

                # Shutdown
                await manager.shutdown()
                print("🛑 WorkflowIntegrationManager shutdown complete")
            else:
                print("❌ Failed to initialize WorkflowIntegrationManager")

        except Exception as e:
            print(f"❌ Error: {e}")

    # Run test
    asyncio.run(test_integration())

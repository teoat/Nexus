#!/usr/bin/env python3
"""
Agent Coordinator - Agent Interaction Management System

This module implements the AgentCoordinator class that provides
comprehensive coordination and interaction management between
different AI agents in the forensic platform.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Tuple

# from ..taskmaster.models.job import Job, JobPriority, JobStatus, JobType


class CoordinationType(Enum):
    """Types of agent coordination."""

    SEQUENTIAL = "sequential"  # Sequential coordination
    PARALLEL = "parallel"  # Parallel coordination
    PIPELINE = "pipeline"  # Pipeline coordination
    BROADCAST = "broadcast"  # Broadcast coordination
    HIERARCHICAL = "hierarchical"  # Hierarchical coordination


class InteractionType(Enum):
    """Types of agent interactions."""

    DATA_SHARING = "data_sharing"  # Share data between agents
    TASK_DELEGATION = "task_delegation"  # Delegate tasks to other agents
    RESULT_AGGREGATION = "result_aggregation"  # Aggregate results from agents
    CONFLICT_RESOLUTION = "conflict_resolution"  # Resolve conflicts between agents
    COLLABORATIVE_ANALYSIS = "collaborative_analysis"  # Collaborative analysis


class AgentRole(Enum):
    """Roles that agents can play in coordination."""

    COORDINATOR = "coordinator"  # Primary coordinator
    EXECUTOR = "executor"  # Task executor
    VALIDATOR = "validator"  # Result validator
    ANALYZER = "analyzer"  # Data analyzer
    REPORTER = "reporter"  # Result reporter


@dataclass
class AgentInteraction:
    """An interaction between agents."""

    id: str
    interaction_type: InteractionType
    source_agent: str
    target_agents: List[str]
    data: Dict[str, Any]
    timestamp: datetime
    status: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoordinationSession:
    """A coordination session between multiple agents."""

    id: str
    session_type: CoordinationType
    participating_agents: List[str]
    coordinator_agent: str
    start_time: datetime
    status: str
    interactions: List[AgentInteraction]
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentCapability:
    """Capability information for an agent."""

    agent_id: str
    capabilities: List[str]
    specializations: List[str]
    performance_metrics: Dict[str, float]
    availability: float
    trust_score: float
    last_updated: datetime


class AgentCoordinator:
    """
    Comprehensive agent coordination system.

    The AgentCoordinator is responsible for:
    - Managing agent interactions and communication
    - Coordinating multi-agent workflows
    - Handling data sharing between agents
    - Managing agent capabilities and specializations
    - Optimizing agent collaboration
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the AgentCoordinator."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.max_concurrent_sessions = config.get("max_concurrent_sessions", 20)
        self.interaction_timeout = config.get("interaction_timeout", 600)  # 10 minutes
        self.coordination_interval = config.get("coordination_interval", 5)  # 5 seconds

        # Agent management
        self.agent_capabilities: Dict[str, AgentCapability] = {}
        self.agent_sessions: Dict[str, List[str]] = defaultdict(list)

        # Coordination management
        self.coordination_sessions: Dict[str, CoordinationSession] = {}
        self.active_sessions: Dict[str, CoordinationSession] = {}
        self.session_queue: deque = deque()

        # Interaction tracking
        self.interactions: Dict[str, AgentInteraction] = {}
        self.interaction_history: Dict[str, List[str]] = defaultdict(list)

        # Performance tracking
        self.total_sessions = 0
        self.total_interactions = 0
        self.average_session_duration = 0.0

        # Event loop
        self.loop = asyncio.get_event_loop()

        self.logger.info("AgentCoordinator initialized successfully")

    async def start(self):
        """Start the AgentCoordinator."""
        self.logger.info("Starting AgentCoordinator...")

        # Initialize coordination components
        await self._initialize_coordination_components()

        # Start background tasks
        asyncio.create_task(self._process_session_queue())
        asyncio.create_task(self._monitor_interactions())
        asyncio.create_task(self._update_performance_metrics())

        self.logger.info("AgentCoordinator started successfully")

    async def stop(self):
        """Stop the AgentCoordinator."""
        self.logger.info("Stopping AgentCoordinator...")
        self.logger.info("AgentCoordinator stopped")

    async def register_agent_capabilities(
        self, agent_id: str, capabilities: List[str], specializations: List[str] = None
    ) -> bool:
        """Register agent capabilities and specializations."""
        try:
            agent_capability = AgentCapability(
                agent_id=agent_id,
                capabilities=capabilities,
                specializations=specializations or [],
                performance_metrics={},
                availability=1.0,
                trust_score=1.0,
                last_updated=datetime.utcnow(),
            )

            self.agent_capabilities[agent_id] = agent_capability

            self.logger.info(f"Registered capabilities for agent: {agent_id}")
            return True

        except Exception as e:
            self.logger.error(
                f"Error registering capabilities for agent {agent_id}: {e}"
            )
            return False

    async def update_agent_performance(
        self, agent_id: str, performance_metrics: Dict[str, float]
    ) -> bool:
        """Update agent performance metrics."""
        try:
            if agent_id in self.agent_capabilities:
                agent_cap = self.agent_capabilities[agent_id]
                agent_cap.performance_metrics.update(performance_metrics)
                agent_cap.last_updated = datetime.utcnow()

                self.logger.info(f"Updated performance for agent: {agent_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error updating performance for agent {agent_id}: {e}")
            return False

    async def create_coordination_session(
        self,
        session_type: CoordinationType,
        participating_agents: List[str],
        coordinator_agent: str,
    ) -> str:
        """Create a new coordination session."""
        try:
            # Validate agents
            if not all(
                agent in self.agent_capabilities for agent in participating_agents
            ):
                raise ValueError("Some participating agents not registered")

            # Create session
            session_id = str(uuid.uuid4())
            session = CoordinationSession(
                id=session_id,
                session_type=session_type,
                participating_agents=participating_agents,
                coordinator_agent=coordinator_agent,
                start_time=datetime.utcnow(),
                status="created",
                interactions=[],
            )

            # Store session
            self.coordination_sessions[session_id] = session

            # Add to queue
            self.session_queue.append(session_id)

            self.logger.info(f"Created coordination session: {session_id}")
            return session_id

        except Exception as e:
            self.logger.error(f"Error creating coordination session: {e}")
            raise

    async def start_coordination_session(self, session_id: str) -> bool:
        """Start a coordination session."""
        try:
            if session_id in self.coordination_sessions:
                session = self.coordination_sessions[session_id]

                # Check if we can start the session
                if len(self.active_sessions) >= self.max_concurrent_sessions:
                    return False

                # Update session status
                session.status = "active"
                self.active_sessions[session_id] = session

                # Update agent sessions
                for agent_id in session.participating_agents:
                    self.agent_sessions[agent_id].append(session_id)

                self.logger.info(f"Started coordination session: {session_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error starting coordination session {session_id}: {e}")
            return False

    async def end_coordination_session(self, session_id: str) -> bool:
        """End a coordination session."""
        try:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]

                # Update session status
                session.status = "completed"
                session.end_time = datetime.utcnow()

                # Remove from active sessions
                del self.active_sessions[session_id]

                # Update agent sessions
                for agent_id in session.participating_agents:
                    if session_id in self.agent_sessions[agent_id]:
                        self.agent_sessions[agent_id].remove(session_id)

                # Update statistics
                self.total_sessions += 1

                self.logger.info(f"Ended coordination session: {session_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error ending coordination session {session_id}: {e}")
            return False

    async def create_agent_interaction(
        self,
        interaction_type: InteractionType,
        source_agent: str,
        target_agents: List[str],
        data: Dict[str, Any],
    ) -> str:
        """Create an interaction between agents."""
        try:
            # Validate agents
            if source_agent not in self.agent_capabilities:
                raise ValueError(f"Source agent {source_agent} not registered")

            if not all(agent in self.agent_capabilities for agent in target_agents):
                raise ValueError("Some target agents not registered")

            # Create interaction
            interaction_id = str(uuid.uuid4())
            interaction = AgentInteraction(
                id=interaction_id,
                interaction_type=interaction_type,
                source_agent=source_agent,
                target_agents=target_agents,
                data=data,
                timestamp=datetime.utcnow(),
                status="created",
            )

            # Store interaction
            self.interactions[interaction_id] = interaction

            # Add to history
            self.interaction_history[source_agent].append(interaction_id)
            for target_agent in target_agents:
                self.interaction_history[target_agent].append(interaction_id)

            # Update statistics
            self.total_interactions += 1

            self.logger.info(
                f"Created interaction: {interaction_id} ({interaction_type.value})"
            )
            return interaction_id

        except Exception as e:
            self.logger.error(f"Error creating agent interaction: {e}")
            raise

    async def get_agent_interactions(
        self, agent_id: str, limit: int = 100
    ) -> List[AgentInteraction]:
        """Get interactions for a specific agent."""
        try:
            if agent_id in self.interaction_history:
                interaction_ids = self.interaction_history[agent_id][-limit:]
                return [
                    self.interactions[interaction_id]
                    for interaction_id in interaction_ids
                    if interaction_id in self.interactions
                ]

            return []

        except Exception as e:
            self.logger.error(f"Error getting interactions for agent {agent_id}: {e}")
            return []

    async def find_agents_by_capability(
        self, required_capabilities: List[str], min_trust_score: float = 0.5
    ) -> List[str]:
        """Find agents with specific capabilities."""
        try:
            matching_agents = []

            for agent_id, capability in self.agent_capabilities.items():
                # Check if agent has all required capabilities
                if all(cap in capability.capabilities for cap in required_capabilities):
                    # Check trust score
                    if capability.trust_score >= min_trust_score:
                        matching_agents.append(agent_id)

            # Sort by trust score and availability
            matching_agents.sort(
                key=lambda agent_id: (
                    self.agent_capabilities[agent_id].trust_score,
                    self.agent_capabilities[agent_id].availability,
                ),
                reverse=True,
            )

            return matching_agents

        except Exception as e:
            self.logger.error(f"Error finding agents by capability: {e}")
            return []

    async def get_agent_recommendations(
        self, task_description: str, required_capabilities: List[str]
    ) -> List[Tuple[str, float]]:
        """Get agent recommendations for a specific task."""
        try:
            recommendations = []

            # Find agents with required capabilities
            capable_agents = await self.find_agents_by_capability(required_capabilities)

            for agent_id in capable_agents:
                capability = self.agent_capabilities[agent_id]

                # Calculate recommendation score
                trust_score = capability.trust_score
                availability = capability.availability
                performance = (
                    np.mean(list(capability.performance_metrics.values()))
                    if capability.performance_metrics
                    else 0.5
                )

                # Combined score
                recommendation_score = (
                    trust_score * 0.4 + availability * 0.3 + performance * 0.3
                )

                recommendations.append((agent_id, recommendation_score))

            # Sort by recommendation score
            recommendations.sort(key=lambda x: x[1], reverse=True)

            return recommendations

        except Exception as e:
            self.logger.error(f"Error getting agent recommendations: {e}")
            return []

    async def _process_session_queue(self):
        """Process the session queue."""
        while True:
            try:
                if (
                    self.session_queue
                    and len(self.active_sessions) < self.max_concurrent_sessions
                ):
                    # Get next session
                    session_id = self.session_queue.popleft()

                    if session_id in self.coordination_sessions:
                        # Start session
                        await self.start_coordination_session(session_id)

                await asyncio.sleep(self.coordination_interval)

            except Exception as e:
                self.logger.error(f"Error processing session queue: {e}")
                await asyncio.sleep(self.coordination_interval)

    async def _monitor_interactions(self):
        """Monitor agent interactions for timeouts."""
        while True:
            try:
                current_time = datetime.utcnow()
                timed_out_interactions = []

                for interaction_id, interaction in self.interactions.items():
                    if interaction.status == "created":
                        # Check for timeout
                        time_since_creation = (
                            current_time - interaction.timestamp
                        ).total_seconds()

                        if time_since_creation > self.interaction_timeout:
                            interaction.status = "timeout"
                            timed_out_interactions.append(interaction_id)

                # Log timeout interactions
                if timed_out_interactions:
                    self.logger.warning(
                        f"Found {len(timed_out_interactions)} timed out interactions"
                    )

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error monitoring interactions: {e}")
                await asyncio.sleep(60)

    async def _update_performance_metrics(self):
        """Update performance metrics."""
        while True:
            try:
                # Calculate average session duration
                completed_sessions = [
                    session
                    for session in self.coordination_sessions.values()
                    if session.status == "completed" and session.end_time
                ]

                if completed_sessions:
                    durations = [
                        (session.end_time - session.start_time).total_seconds()
                        for session in completed_sessions
                    ]
                    self.average_session_duration = np.mean(durations)

                await asyncio.sleep(300)  # Update every 5 minutes

            except Exception as e:
                self.logger.error(f"Error updating performance metrics: {e}")
                await asyncio.sleep(300)

    async def _initialize_coordination_components(self):
        """Initialize coordination components."""
        try:
            # Initialize coordination protocols
            await self._initialize_coordination_protocols()

            self.logger.info("Coordination components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing coordination components: {e}")

    async def _initialize_coordination_protocols(self):
        """Initialize coordination protocols."""
        try:
            # This would initialize standard coordination protocols
            # For now, just log initialization
            self.logger.info("Coordination protocols initialized")

        except Exception as e:
            self.logger.error(f"Error initializing coordination protocols: {e}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            "total_sessions": self.total_sessions,
            "total_interactions": self.total_interactions,
            "average_session_duration": self.average_session_duration,
            "active_sessions": len(self.active_sessions),
            "queued_sessions": len(self.session_queue),
            "total_agents": len(self.agent_capabilities),
            "total_interactions_today": len(
                [
                    interaction
                    for interaction in self.interactions.values()
                    if (datetime.utcnow() - interaction.timestamp).days == 0
                ]
            ),
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "max_concurrent_sessions": 20,
        "interaction_timeout": 600,
        "coordination_interval": 5,
    }

    # Initialize agent coordinator
    coordinator = AgentCoordinator(config)

    print("AgentCoordinator system initialized successfully!")

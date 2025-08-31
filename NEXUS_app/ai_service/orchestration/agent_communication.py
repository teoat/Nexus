#!/usr/bin/env python3
"""
Agent Communication - Inter-Agent Messaging System

This module implements the AgentCommunication class that provides
comprehensive communication and messaging capabilities between
different AI agents in the forensic platform.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

# from ..taskmaster.models.job import Job, JobPriority, JobStatus, JobType


class MessageType(Enum):
    """Types of inter-agent messages."""

    TASK_REQUEST = "task_request"  # Request for task execution
    TASK_RESPONSE = "task_response"  # Response to task request
    DATA_REQUEST = "data_request"  # Request for data
    DATA_RESPONSE = "data_response"  # Response with data
    STATUS_UPDATE = "status_update"  # Status update message
    ERROR_REPORT = "error_report"  # Error reporting
    HEARTBEAT = "heartbeat"  # Health check message
    BROADCAST = "broadcast"  # Broadcast message


class MessagePriority(Enum):
    """Message priority levels."""

    LOW = "low"  # Low priority
    NORMAL = "normal"  # Normal priority
    HIGH = "high"  # High priority
    CRITICAL = "critical"  # Critical priority
    EMERGENCY = "emergency"  # Emergency priority


class MessageStatus(Enum):
    """Message delivery status."""

    PENDING = "pending"  # Message pending delivery
    SENT = "sent"  # Message sent
    DELIVERED = "delivered"  # Message delivered
    READ = "read"  # Message read
    FAILED = "failed"  # Message delivery failed
    EXPIRED = "expired"  # Message expired


@dataclass
class AgentMessage:
    """A message between agents."""

    id: str
    message_type: MessageType
    priority: MessagePriority
    source_agent: str
    target_agents: List[str]
    subject: str
    content: Dict[str, Any]
    timestamp: datetime
    expiration: Optional[datetime] = None
    status: MessageStatus = MessageStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MessageQueue:
    """Message queue for an agent."""

    agent_id: str
    incoming_queue: deque
    outgoing_queue: deque
    priority_queues: Dict[MessagePriority, deque]
    last_processed: datetime


@dataclass
class CommunicationChannel:
    """A communication channel between agents."""

    id: str
    source_agent: str
    target_agent: str
    channel_type: str
    status: str
    created_at: datetime
    last_activity: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentCommunication:
    """
    Comprehensive agent communication system.

    The AgentCommunication is responsible for:
    - Managing inter-agent messaging
    - Handling message routing and delivery
    - Managing communication channels
    - Message queuing and prioritization
    - Data exchange between agents
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the AgentCommunication."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.max_message_size = config.get("max_message_size", 1048576)  # 1MB
        self.message_timeout = config.get("message_timeout", 300)  # 5 minutes
        self.max_queue_size = config.get("max_queue_size", 1000)
        self.heartbeat_interval = config.get("heartbeat_interval", 30)  # 30 seconds

        # Message management
        self.messages: Dict[str, AgentMessage] = {}
        self.message_queues: Dict[str, MessageQueue] = {}
        self.communication_channels: Dict[str, CommunicationChannel] = {}

        # Routing and delivery
        self.message_routes: Dict[str, List[str]] = defaultdict(list)
        self.delivery_confirmations: Dict[str, List[str]] = defaultdict(list)

        # Performance tracking
        self.total_messages_sent = 0
        self.total_messages_delivered = 0
        self.average_delivery_time = 0.0
        self.message_success_rate = 0.0

        # Event loop
        self.loop = asyncio.get_event_loop()

        self.logger.info("AgentCommunication initialized successfully")

    async def start(self):
        """Start the AgentCommunication."""
        self.logger.info("Starting AgentCommunication...")

        # Initialize communication components
        await self._initialize_communication_components()

        # Start background tasks
        asyncio.create_task(self._process_message_queues())
        asyncio.create_task(self._monitor_message_timeouts())
        asyncio.create_task(self._send_heartbeats())
        asyncio.create_task(self._update_performance_metrics())

        self.logger.info("AgentCommunication started successfully")

    async def stop(self):
        """Stop the AgentCommunication."""
        self.logger.info("Stopping AgentCommunication...")
        self.logger.info("AgentCommunication stopped")

    async def register_agent(self, agent_id: str) -> bool:
        """Register an agent for communication."""
        try:
            # Create message queue for agent
            message_queue = MessageQueue(
                agent_id=agent_id,
                incoming_queue=deque(maxlen=self.max_queue_size),
                outgoing_queue=deque(maxlen=self.max_queue_size),
                priority_queues={
                    MessagePriority.LOW: deque(maxlen=self.max_queue_size),
                    MessagePriority.NORMAL: deque(maxlen=self.max_queue_size),
                    MessagePriority.HIGH: deque(maxlen=self.max_queue_size),
                    MessagePriority.CRITICAL: deque(maxlen=self.max_queue_size),
                    MessagePriority.EMERGENCY: deque(maxlen=self.max_queue_size),
                },
                last_processed=datetime.utcnow(),
            )

            self.message_queues[agent_id] = message_queue

            self.logger.info(f"Registered agent for communication: {agent_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error registering agent {agent_id}: {e}")
            return False

    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from communication."""
        try:
            if agent_id in self.message_queues:
                # Remove agent's message queue
                del self.message_queues[agent_id]

                # Remove agent from routing
                if agent_id in self.message_routes:
                    del self.message_routes[agent_id]

                # Remove communication channels
                channels_to_remove = [
                    channel_id
                    for channel_id, channel in self.communication_channels.items()
                    if channel.source_agent == agent_id
                    or channel.target_agent == agent_id
                ]

                for channel_id in channels_to_remove:
                    del self.communication_channels[channel_id]

                self.logger.info(f"Unregistered agent from communication: {agent_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error unregistering agent {agent_id}: {e}")
            return False

    async def send_message(
        self,
        message_type: MessageType,
        priority: MessagePriority,
        source_agent: str,
        target_agents: List[str],
        subject: str,
        content: Dict[str, Any],
        expiration: Optional[datetime] = None,
    ) -> str:
        """Send a message between agents."""
        try:
            # Validate message size
            message_size = len(json.dumps(content))
            if message_size > self.max_message_size:
                raise ValueError(
                    f"Message size {message_size} exceeds maximum {self.max_message_size}"
                )

            # Create message
            message_id = str(uuid.uuid4())
            message = AgentMessage(
                id=message_id,
                message_type=message_type,
                priority=priority,
                source_agent=source_agent,
                target_agents=target_agents,
                subject=subject,
                content=content,
                timestamp=datetime.utcnow(),
                expiration=expiration
                or (datetime.utcnow() + timedelta(seconds=self.message_timeout)),
            )

            # Store message
            self.messages[message_id] = message

            # Add to source agent's outgoing queue
            if source_agent in self.message_queues:
                self.message_queues[source_agent].outgoing_queue.append(message_id)
                self.message_queues[source_agent].priority_queues[priority].append(
                    message_id
                )

            # Add to target agents' incoming queues
            for target_agent in target_agents:
                if target_agent in self.message_queues:
                    self.message_queues[target_agent].incoming_queue.append(message_id)
                    self.message_queues[target_agent].priority_queues[priority].append(
                        message_id
                    )

            # Update statistics
            self.total_messages_sent += 1

            self.logger.info(
                f"Sent message: {message_id} from {source_agent} to {target_agents}"
            )
            return message_id

        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            raise

    async def get_messages(
        self,
        agent_id: str,
        limit: int = 100,
        priority: Optional[MessagePriority] = None,
    ) -> List[AgentMessage]:
        """Get messages for a specific agent."""
        try:
            if agent_id not in self.message_queues:
                return []

            message_queue = self.message_queues[agent_id]

            if priority:
                # Get messages from specific priority queue
                priority_queue = message_queue.priority_queues.get(priority, deque())
                message_ids = list(priority_queue)[-limit:]
            else:
                # Get messages from incoming queue
                message_ids = list(message_queue.incoming_queue)[-limit:]

            # Retrieve messages
            messages = []
            for message_id in message_ids:
                if message_id in self.messages:
                    message = self.messages[message_id]
                    if agent_id in message.target_agents:
                        messages.append(message)

            return messages

        except Exception as e:
            self.logger.error(f"Error getting messages for agent {agent_id}: {e}")
            return []

    async def mark_message_read(self, message_id: str, agent_id: str) -> bool:
        """Mark a message as read by an agent."""
        try:
            if message_id in self.messages:
                message = self.messages[message_id]

                if agent_id in message.target_agents:
                    message.status = MessageStatus.READ

                    # Update delivery confirmations
                    if message_id not in self.delivery_confirmations:
                        self.delivery_confirmations[message_id] = []

                    if agent_id not in self.delivery_confirmations[message_id]:
                        self.delivery_confirmations[message_id].append(agent_id)

                    self.logger.info(
                        f"Message {message_id} marked as read by {agent_id}"
                    )
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Error marking message {message_id} as read: {e}")
            return False

    async def create_communication_channel(
        self, source_agent: str, target_agent: str, channel_type: str = "direct"
    ) -> str:
        """Create a communication channel between agents."""
        try:
            # Validate agents
            if (
                source_agent not in self.message_queues
                or target_agent not in self.message_queues
            ):
                raise ValueError("One or both agents not registered")

            # Create channel
            channel_id = str(uuid.uuid4())
            channel = CommunicationChannel(
                id=channel_id,
                source_agent=source_agent,
                target_agent=target_agent,
                channel_type=channel_type,
                status="active",
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
            )

            self.communication_channels[channel_id] = channel

            # Update routing
            self.message_routes[source_agent].append(target_agent)

            self.logger.info(f"Created communication channel: {channel_id}")
            return channel_id

        except Exception as e:
            self.logger.error(f"Error creating communication channel: {e}")
            raise

    async def close_communication_channel(self, channel_id: str) -> bool:
        """Close a communication channel."""
        try:
            if channel_id in self.communication_channels:
                channel = self.communication_channels[channel_id]

                # Update status
                channel.status = "closed"

                # Remove from routing
                if channel.source_agent in self.message_routes:
                    if (
                        channel.target_agent
                        in self.message_routes[channel.source_agent]
                    ):
                        self.message_routes[channel.source_agent].remove(
                            channel.target_agent
                        )

                self.logger.info(f"Closed communication channel: {channel_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error closing communication channel {channel_id}: {e}")
            return False

    async def broadcast_message(
        self,
        source_agent: str,
        subject: str,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> str:
        """Broadcast a message to all registered agents."""
        try:
            # Get all registered agents
            target_agents = list(self.message_queues.keys())

            # Remove source agent from targets
            if source_agent in target_agents:
                target_agents.remove(source_agent)

            if not target_agents:
                raise ValueError("No target agents available for broadcast")

            # Send broadcast message
            message_id = await self.send_message(
                message_type=MessageType.BROADCAST,
                priority=priority,
                source_agent=source_agent,
                target_agents=target_agents,
                subject=subject,
                content=content,
            )

            self.logger.info(
                f"Broadcast message sent: {message_id} to {len(target_agents)} agents"
            )
            return message_id

        except Exception as e:
            self.logger.error(f"Error broadcasting message: {e}")
            raise

    async def _process_message_queues(self):
        """Process message queues for all agents."""
        while True:
            try:
                for agent_id, message_queue in self.message_queues.items():
                    # Process incoming messages by priority
                    for priority in [
                        MessagePriority.EMERGENCY,
                        MessagePriority.CRITICAL,
                        MessagePriority.HIGH,
                        MessagePriority.NORMAL,
                        MessagePriority.LOW,
                    ]:
                        priority_queue = message_queue.priority_queues[priority]

                        while priority_queue:
                            message_id = priority_queue.popleft()

                            if message_id in self.messages:
                                message = self.messages[message_id]

                                # Check if message is expired
                                if (
                                    message.expiration
                                    and datetime.utcnow() > message.expiration
                                ):
                                    message.status = MessageStatus.EXPIRED
                                    continue

                                # Process message
                                await self._process_message(message, agent_id)

                await asyncio.sleep(0.1)  # Process every 100ms

            except Exception as e:
                self.logger.error(f"Error processing message queues: {e}")
                await asyncio.sleep(1)

    async def _process_message(self, message: AgentMessage, agent_id: str):
        """Process a single message for an agent."""
        try:
            # Update message status
            if message.status == MessageStatus.PENDING:
                message.status = MessageStatus.SENT

            # Handle different message types
            if message.message_type == MessageType.TASK_REQUEST:
                await self._handle_task_request(message, agent_id)
            elif message.message_type == MessageType.DATA_REQUEST:
                await self._handle_data_request(message, agent_id)
            elif message.message_type == MessageType.STATUS_UPDATE:
                await self._handle_status_update(message, agent_id)
            elif message.message_type == MessageType.ERROR_REPORT:
                await self._handle_error_report(message, agent_id)
            elif message.message_type == MessageType.HEARTBEAT:
                await self._handle_heartbeat(message, agent_id)
            elif message.message_type == MessageType.BROADCAST:
                await self._handle_broadcast(message, agent_id)

            # Update delivery status
            if agent_id in message.target_agents:
                message.status = MessageStatus.DELIVERED

                # Update statistics
                self.total_messages_delivered += 1

        except Exception as e:
            self.logger.error(f"Error processing message {message.id}: {e}")
            message.status = MessageStatus.FAILED

    async def _handle_task_request(self, message: AgentMessage, agent_id: str):
        """Handle task request messages."""
        try:
            # This would trigger task execution
            self.logger.info(
                f"Processing task request: {message.subject} for agent {agent_id}"
            )

        except Exception as e:
            self.logger.error(f"Error handling task request: {e}")

    async def _handle_data_request(self, message: AgentMessage, agent_id: str):
        """Handle data request messages."""
        try:
            # This would trigger data retrieval
            self.logger.info(
                f"Processing data request: {message.subject} for agent {agent_id}"
            )

        except Exception as e:
            self.logger.error(f"Error handling data request: {e}")

    async def _handle_status_update(self, message: AgentMessage, agent_id: str):
        """Handle status update messages."""
        try:
            # This would update agent status
            self.logger.info(
                f"Processing status update: {message.subject} for agent {agent_id}"
            )

        except Exception as e:
            self.logger.error(f"Error handling status update: {e}")

    async def _handle_error_report(self, message: AgentMessage, agent_id: str):
        """Handle error report messages."""
        try:
            # This would log and process errors
            self.logger.info(
                f"Processing error report: {message.subject} for agent {agent_id}"
            )

        except Exception as e:
            self.logger.error(f"Error handling error report: {e}")

    async def _handle_heartbeat(self, message: AgentMessage, agent_id: str):
        """Handle heartbeat messages."""
        try:
            # This would update agent health status
            self.logger.debug(f"Processing heartbeat from agent {agent_id}")

        except Exception as e:
            self.logger.error(f"Error handling heartbeat: {e}")

    async def _handle_broadcast(self, message: AgentMessage, agent_id: str):
        """Handle broadcast messages."""
        try:
            # This would process broadcast content
            self.logger.info(
                f"Processing broadcast: {message.subject} for agent {agent_id}"
            )

        except Exception as e:
            self.logger.error(f"Error handling broadcast: {e}")

    async def _monitor_message_timeouts(self):
        """Monitor messages for timeouts."""
        while True:
            try:
                current_time = datetime.utcnow()
                expired_messages = []

                for message_id, message in self.messages.items():
                    if (
                        message.expiration
                        and current_time > message.expiration
                        and message.status == MessageStatus.PENDING
                    ):
                        message.status = MessageStatus.EXPIRED
                        expired_messages.append(message_id)

                if expired_messages:
                    self.logger.warning(
                        f"Found {len(expired_messages)} expired messages"
                    )

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error monitoring message timeouts: {e}")
                await asyncio.sleep(60)

    async def _send_heartbeats(self):
        """Send heartbeat messages to all agents."""
        while True:
            try:
                # Send heartbeat to all registered agents
                for agent_id in self.message_queues.keys():
                    await self.send_message(
                        message_type=MessageType.HEARTBEAT,
                        priority=MessagePriority.LOW,
                        source_agent="system",
                        target_agents=[agent_id],
                        subject="Heartbeat",
                        content={"timestamp": datetime.utcnow().isoformat()},
                    )

                await asyncio.sleep(self.heartbeat_interval)

            except Exception as e:
                self.logger.error(f"Error sending heartbeats: {e}")
                await asyncio.sleep(self.heartbeat_interval)

    async def _update_performance_metrics(self):
        """Update performance metrics."""
        while True:
            try:
                # Calculate success rate
                if self.total_messages_sent > 0:
                    self.message_success_rate = (
                        self.total_messages_delivered / self.total_messages_sent
                    )

                await asyncio.sleep(300)  # Update every 5 minutes

            except Exception as e:
                self.logger.error(f"Error updating performance metrics: {e}")
                await asyncio.sleep(300)

    async def _initialize_communication_components(self):
        """Initialize communication components."""
        try:
            # Initialize communication protocols
            await self._initialize_communication_protocols()

            self.logger.info("Communication components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing communication components: {e}")

    async def _initialize_communication_protocols(self):
        """Initialize communication protocols."""
        try:
            # This would initialize standard communication protocols
            # For now, just log initialization
            self.logger.info("Communication protocols initialized")

        except Exception as e:
            self.logger.error(f"Error initializing communication protocols: {e}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            "total_messages_sent": self.total_messages_sent,
            "total_messages_delivered": self.total_messages_delivered,
            "average_delivery_time": self.average_delivery_time,
            "message_success_rate": self.message_success_rate,
            "active_channels": len(self.communication_channels),
            "registered_agents": len(self.message_queues),
            "total_messages": len(self.messages),
            "message_types_supported": [msg_type.value for msg_type in MessageType],
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "max_message_size": 1048576,
        "message_timeout": 300,
        "max_queue_size": 1000,
        "heartbeat_interval": 30,
    }

    # Initialize agent communication
    communication = AgentCommunication(config)

    print("AgentCommunication system initialized successfully!")

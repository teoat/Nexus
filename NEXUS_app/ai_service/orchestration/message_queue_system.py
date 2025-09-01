#!/usr/bin/env python3
"""
Message Queue System - Priority-Based Messaging and Routing

This module implements the MessageQueueSystem class that provides
comprehensive message queuing capabilities for the forensic platform.
"""

import asyncio
import heapq
import json
import logging
import os
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Message queue libraries
try:
    import pika
    import redis

    RABBITMQ_AVAILABLE = True
    REDIS_AVAILABLE = True
except ImportError:
    RABBITMQ_AVAILABLE = False
    REDIS_AVAILABLE = False

# from ..taskmaster.models.job import Job, JobPriority, JobStatus, JobType


class MessagePriority(Enum):
    """Message priority levels."""

    CRITICAL = "critical"  # Highest priority - immediate processing
    HIGH = "high"  # High priority - process soon
    NORMAL = "normal"  # Normal priority - standard processing
    LOW = "low"  # Low priority - process when available
    BULK = "bulk"  # Bulk processing - lowest priority


class MessageType(Enum):
    """Types of messages in the queue."""

    TASK_ASSIGNMENT = "task_assignment"  # Task assignment messages
    WORKFLOW_UPDATE = "workflow_update"  # Workflow status updates
    AGENT_COMMUNICATION = "agent_communication"  # Inter-agent communication
    SYSTEM_NOTIFICATION = "system_notification"  # System notifications
    ERROR_REPORT = "error_report"  # Error reporting messages
    STATUS_UPDATE = "status_update"  # Status update messages
    DATA_SYNC = "data_sync"  # Data synchronization messages
    HEARTBEAT = "heartbeat"  # Agent heartbeat messages


class QueueType(Enum):
    """Types of message queues."""

    PRIORITY_QUEUE = "priority_queue"  # Priority-based queue
    WORK_QUEUE = "work_queue"  # Work distribution queue
    PUBLISH_SUBSCRIBE = "publish_subscribe"  # Publish-subscribe queue
    REQUEST_RESPONSE = "request_response"  # Request-response queue
    DEAD_LETTER = "dead_letter"  # Dead letter queue
    RETRY_QUEUE = "retry_queue"  # Retry queue for failed messages


class MessageStatus(Enum):
    """Status of messages in the queue."""

    PENDING = "pending"  # Message is pending processing
    PROCESSING = "processing"  # Message is being processed
    COMPLETED = "completed"  # Message processing completed
    FAILED = "failed"  # Message processing failed
    RETRYING = "retrying"  # Message is being retried
    DEAD_LETTER = "dead_letter"  # Message moved to dead letter queue
    EXPIRED = "expired"  # Message expired


@dataclass
class QueueMessage:
    """Message in the queue system.Message in the queue system."""

    message_id: str
    sender_id: str
    recipient_id: Optional[str]
    message_type: MessageType
    priority: MessagePriority
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    expiration_time: Optional[datetime]
    retry_count: int
    status: MessageStatus
    processing_start: Optional[datetime]
    processing_end: Optional[datetime]
    error_message: Optional[str]
    routing_key: str
    exchange: str
    queue_name: str


@dataclass
class QueueConfig:
    """Configuration for a message queue.Configuration for a message queue."""

    queue_name: str
    queue_type: QueueType
    durable: bool
    auto_delete: bool
    max_priority: int
    message_ttl: Optional[int]
    max_length: Optional[int]
    dead_letter_exchange: Optional[str]
    dead_letter_routing_key: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueueMetrics:
    """Metrics for a message queue.Metrics for a message queue."""

    queue_name: str
    message_count: int
    consumer_count: int
    pending_messages: int
    processing_messages: int
    completed_messages: int
    failed_messages: int
    retry_messages: int
    dead_letter_messages: int
    average_processing_time: float
    throughput_per_minute: float
    last_updated: datetime


class MessageQueueSystem:
    """
    Comprehensive message queue system.

    The MessageQueueSystem is responsible for:
    - Priority-based message queuing
    - Message routing and delivery
    - Dead letter queue management
    - Retry mechanisms and error handling
    - Queue monitoring and metrics
    - Load balancing and scaling
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the MessageQueueSystem."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.rabbitmq_host = config.get("rabbitmq_host", "localhost")
        self.rabbitmq_port = config.get("rabbitmq_port", 5672)
        self.rabbitmq_username = config.get("rabbitmq_username", "guest")
        self.rabbitmq_password = config.get("rabbitmq_password", "guest")
        self.redis_host = config.get("redis_host", "localhost")
        self.redis_port = config.get("redis_port", 6379)
        self.enable_priority_queues = config.get("enable_priority_queues", True)
        self.max_retry_attempts = config.get("max_retry_attempts", 3)
        self.message_ttl = config.get("message_ttl", 3600)  # 1 hour

        # Queue management
        self.queues: Dict[str, QueueConfig] = {}
        self.queue_messages: Dict[str, deque] = defaultdict(deque)
        self.priority_queues: Dict[str, List[Tuple[int, str, QueueMessage]]] = (
            defaultdict(list)
        )

        # Message management
        self.messages: Dict[str, QueueMessage] = {}
        self.message_status: Dict[str, MessageStatus] = {}
        self.message_history: Dict[str, List[str]] = defaultdict(list)

        # Connection management
        self.rabbitmq_connection = None
        self.redis_connection = None
        self.channel = None

        # Performance tracking
        self.total_messages = 0
        self.processed_messages = 0
        self.failed_messages = 0
        self.average_processing_time = 0.0

        # Event loop
        self.loop = asyncio.get_event_loop()

        # Check library availability
        self._check_library_availability()

        self.logger.info("MessageQueueSystem initialized successfully")

    def _check_library_availability(self):
        """Check if required libraries are available."""
        if not RABBITMQ_AVAILABLE:
            self.logger.warning(
                "RabbitMQ library not available - queue functionality will be limited",
            )

        if not REDIS_AVAILABLE:
            self.logger.warning(
                "Redis library not available - caching functionality will be limited",
            )

    async def start(self):
        """Start the MessageQueueSystem."""
        self.logger.info("Starting MessageQueueSystem...")

        # Initialize connections
        await self._initialize_connections()

        # Initialize default queues
        await self._initialize_default_queues()

        # Start background tasks
        asyncio.create_task(self._process_message_queues())
        asyncio.create_task(self._cleanup_expired_messages())
        asyncio.create_task(self._update_queue_metrics())

        self.logger.info("MessageQueueSystem started successfully")

    async def stop(self):
        """Stop the MessageQueueSystem."""
        self.logger.info("Stopping MessageQueueSystem...")

        # Close connections
        await self._close_connections()

        self.logger.info("MessageQueueSystem stopped")

    async def _initialize_connections(self):
        """Initialize RabbitMQ and Redis connections."""
        try:
            # Initialize RabbitMQ connection
            if RABBITMQ_AVAILABLE:
                try:
                    # Create connection parameters
                    credentials = pika.PlainCredentials(
                        self.rabbitmq_username, self.rabbitmq_password
                    )
                    parameters = pika.ConnectionParameters(
                        host=self.rabbitmq_host,
                        port=self.rabbitmq_port,
                        credentials=credentials,
                        heartbeat=600,
                        blocked_connection_timeout=300,
                    )

                    # Create connection
                    self.rabbitmq_connection = pika.BlockingConnection(parameters)
                    self.channel = self.rabbitmq_connection.channel()

                    self.logger.info("RabbitMQ connection established successfully")

                except Exception as e:
                    self.logger.warning(f"Could not establish RabbitMQ connection: {e}")

            # Initialize Redis connection
            if REDIS_AVAILABLE:
                try:
                    self.redis_connection = redis.Redis(
                        host=self.redis_host,
                        port=self.redis_port,
                        decode_responses=True,
                    )

                    # Test connection
                    self.redis_connection.ping()

                    self.logger.info("Redis connection established successfully")

                except Exception as e:
                    self.logger.warning(f"Could not establish Redis connection: {e}")

        except Exception as e:
            self.logger.error(f"Error initializing connections: {e}")

    async def _initialize_default_queues(self):
        """Initialize default message queues.Initialize default message queues."""
        try:
            # Priority queue for high-priority messages
            await self.create_queue(
                QueueConfig(
                    queue_name="priority_queue",
                    queue_type=QueueType.PRIORITY_QUEUE,
                    durable=True,
                    auto_delete=False,
                    max_priority=10,
                    message_ttl=self.message_ttl,
                    max_length=10000,
                    dead_letter_exchange="dlx",
                    dead_letter_routing_key="dlq",
                )
            )

            # Work queue for task distribution
            await self.create_queue(
                QueueConfig(
                    queue_name="work_queue",
                    queue_type=QueueType.WORK_QUEUE,
                    durable=True,
                    auto_delete=False,
                    max_priority=5,
                    message_ttl=self.message_ttl,
                    max_length=5000,
                    dead_letter_exchange="dlx",
                    dead_letter_routing_key="dlq",
                )
            )

            # Publish-subscribe queue for broadcasts
            await self.create_queue(
                QueueConfig(
                    queue_name="broadcast_queue",
                    queue_type=QueueType.PUBLISH_SUBSCRIBE,
                    durable=False,
                    auto_delete=True,
                    max_priority=3,
                    message_ttl=self.message_ttl,
                    max_length=1000,
                    dead_letter_exchange=None,
                    dead_letter_routing_key=None,
                )
            )

            # Dead letter queue for failed messages
            await self.create_queue(
                QueueConfig(
                    queue_name="dead_letter_queue",
                    queue_type=QueueType.DEAD_LETTER,
                    durable=True,
                    auto_delete=False,
                    max_priority=1,
                    message_ttl=86400,  # 24 hours
                    max_length=1000,
                    dead_letter_exchange=None,
                    dead_letter_routing_key=None,
                )
            )

            # Retry queue for failed messages
            await self.create_queue(
                QueueConfig(
                    queue_name="retry_queue",
                    queue_type=QueueType.RETRY_QUEUE,
                    durable=True,
                    auto_delete=False,
                    max_priority=2,
                    message_ttl=300,  # 5 minutes
                    max_length=1000,
                    dead_letter_exchange="dlx",
                    dead_letter_routing_key="dlq",
                )
            )

            self.logger.info("Default queues initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing default queues: {e}")

    async def create_queue(self, queue_config: QueueConfig) -> str:
        """Create a new message queue.Create a new message queue."""
        try:
            queue_name = queue_config.queue_name

            if queue_name in self.queues:
                raise ValueError(f"Queue already exists: {queue_name}")

            # Store queue configuration
            self.queues[queue_name] = queue_config

            # Initialize message storage
            self.queue_messages[queue_name] = deque()

            # Initialize priority queue if needed
            if queue_config.queue_type == QueueType.PRIORITY_QUEUE:
                self.priority_queues[queue_name] = []

            # Create RabbitMQ queue if available
            if RABBITMQ_AVAILABLE and self.channel:
                try:
                    # Declare exchange
                    exchange_name = f"{queue_name}_exchange"
                    self.channel.exchange_declare(
                        exchange=exchange_name,
                        exchange_type="direct",
                        durable=queue_config.durable,
                    )

                    # Declare queue
                    queue_args = {}
                    if queue_config.max_priority:
                        queue_args["x-max-priority"] = queue_config.max_priority
                    if queue_config.message_ttl:
                        queue_args["x-message-ttl"] = (
                            queue_config.message_ttl * 1000
                        )  # Convert to milliseconds
                    if queue_config.max_length:
                        queue_args["x-max-length"] = queue_config.max_length
                    if queue_config.dead_letter_exchange:
                        queue_args["x-dead-letter-exchange"] = (
                            queue_config.dead_letter_exchange
                        )
                    if queue_config.dead_letter_routing_key:
                        queue_args["x-dead-letter-routing-key"] = (
                            queue_config.dead_letter_routing_key
                        )

                    self.channel.queue_declare(
                        queue=queue_name,
                        durable=queue_config.durable,
                        auto_delete=queue_config.auto_delete,
                        arguments=queue_args,
                    )

                    # Bind queue to exchange
                    self.channel.queue_bind(
                        queue=queue_name, exchange=exchange_name, routing_key=queue_name
                    )

                except Exception as e:
                    self.logger.warning(
                        f"Could not create RabbitMQ queue {queue_name}: {e}",
                    )

            self.logger.info(f"Queue created successfully: {queue_name}")

            return queue_name

        except Exception as e:
            self.logger.error(f"Error creating queue: {e}")
            raise

    async def send_message(
        self,
        queue_name: str,
        sender_id: str,
        recipient_id: Optional[str],
        message_type: MessageType,
        priority: MessagePriority,
        content: str,
        metadata: Dict[str, Any] = None,
        routing_key: str = None,
    ) -> str:
        """Send a message to a queue.Send a message to a queue."""
        try:
            if queue_name not in self.queues:
                raise ValueError(f"Queue not found: {queue_name}")

            # Generate message ID
            message_id = str(uuid.uuid4())

            # Set expiration time
            expiration_time = None
            if self.queues[queue_name].message_ttl:
                expiration_time = datetime.utcnow() + timedelta(
                    seconds=self.queues[queue_name].message_ttl
                )

            # Create message
            message = QueueMessage(
                message_id=message_id,
                sender_id=sender_id,
                recipient_id=recipient_id,
                message_type=message_type,
                priority=priority,
                content=content,
                metadata=metadata or {},
                timestamp=datetime.utcnow(),
                expiration_time=expiration_time,
                retry_count=0,
                status=MessageStatus.PENDING,
                processing_start=None,
                processing_end=None,
                error_message=None,
                routing_key=routing_key or queue_name,
                exchange=f"{queue_name}_exchange",
                queue_name=queue_name,
            )

            # Store message
            self.messages[message_id] = message
            self.message_status[message_id] = MessageStatus.PENDING

            # Add to queue
            await self._add_message_to_queue(queue_name, message)

            # Send to RabbitMQ if available
            if RABBITMQ_AVAILABLE and self.channel:
                try:
                    # Prepare message properties
                    properties = pika.BasicProperties(
                        message_id=message_id,
                        priority=self._get_priority_value(priority),
                        timestamp=int(message.timestamp.timestamp()),
                        expiration=str(
                            self.queues[queue_name].message_ttl * 1000,
                        ),
                    )

                    # Publish message
                    self.channel.basic_publish(
                        exchange=message.exchange,
                        routing_key=message.routing_key,
                        body=json.dumps(
                            {
                                "message_id": message_id,
                                "sender_id": sender_id,
                                "recipient_id": recipient_id,
                                "message_type": message_type.value,
                                "priority": priority.value,
                                "content": content,
                                "metadata": metadata or {},
                                "timestamp": message.timestamp.isoformat(),
                            }
                        ),
                        properties=properties,
                    )

                except Exception as e:
                    self.logger.warning(f"Could not send message to RabbitMQ: {e}")

            # Update statistics
            self.total_messages += 1

            self.logger.info(f"Message sent successfully: {message_id} to {queue_name}")

            return message_id

        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            raise

    async def _add_message_to_queue(self, queue_name: str, message: QueueMessage):
        """Add a message to the appropriate queue.Add a message to the appropriate queue."""
        try:
            queue_config = self.queues[queue_name]

            if queue_config.queue_type == QueueType.PRIORITY_QUEUE:
                # Add to priority queue
                priority_value = self._get_priority_value(message.priority)
                heapq.heappush(
                    self.priority_queues[queue_name],
                    (priority_value, message.timestamp.isoformat(), message.message_id),
                )
            else:
                # Add to regular queue
                self.queue_messages[queue_name].append(message.message_id)

            # Update message history
            self.message_history[queue_name].append(message.message_id)

        except Exception as e:
            self.logger.error(f"Error adding message to queue: {e}")

    def _get_priority_value(self, priority: MessagePriority) -> int:
        """Get numeric priority value.Get numeric priority value."""
        priority_map = {
            MessagePriority.CRITICAL: 10,
            MessagePriority.HIGH: 8,
            MessagePriority.NORMAL: 5,
            MessagePriority.LOW: 2,
            MessagePriority.BULK: 1,
        }
        return priority_map.get(priority, 5)

    async def receive_message(
        self, queue_name: str, timeout: int = 30
    ) -> Optional[QueueMessage]:
        """Receive a message from a queue.Receive a message from a queue."""
        try:
            if queue_name not in self.queues:
                raise ValueError(f"Queue not found: {queue_name}")

            # Try to get message from queue
            message_id = await self._get_message_from_queue(queue_name, timeout)

            if not message_id:
                return None

            # Get message
            message = self.messages.get(message_id)
            if not message:
                return None

            # Update message status
            message.status = MessageStatus.PROCESSING
            message.processing_start = datetime.utcnow()

            self.logger.info(f"Message received: {message_id} from {queue_name}")

            return message

        except Exception as e:
            self.logger.error(f"Error receiving message: {e}")
            return None

    async def _get_message_from_queue(
        self, queue_name: str, timeout: int
    ) -> Optional[str]:
        """Get a message ID from the queue.Get a message ID from the queue."""
        try:
            queue_config = self.queues[queue_name]

            if queue_config.queue_type == QueueType.PRIORITY_QUEUE:
                # Get from priority queue
                if self.priority_queues[queue_name]:
                    priority, timestamp, message_id = heapq.heappop(
                        self.priority_queues[queue_name]
                    )
                    return message_id
            else:
                # Get from regular queue
                if self.queue_messages[queue_name]:
                    return self.queue_messages[queue_name].popleft()

            # Wait for message if timeout specified
            if timeout > 0:
                start_time = datetime.utcnow()
                while (datetime.utcnow() - start_time).total_seconds() < timeout:
                    await asyncio.sleep(0.1)

                    # Check again
                    if queue_config.queue_type == QueueType.PRIORITY_QUEUE:
                        if self.priority_queues[queue_name]:
                            priority, timestamp, message_id = heapq.heappop(
                                self.priority_queues[queue_name]
                            )
                            return message_id
                    else:
                        if self.queue_messages[queue_name]:
                            return self.queue_messages[queue_name].popleft()

            return None

        except Exception as e:
            self.logger.error(f"Error getting message from queue: {e}")
            return None

    async def acknowledge_message(self, message_id: str, success: bool = True):
        """Acknowledge message processing.Acknowledge message processing."""
        try:
            if message_id not in self.messages:
                raise ValueError(f"Message not found: {message_id}")

            message = self.messages[message_id]

            if success:
                # Mark as completed
                message.status = MessageStatus.COMPLETED
                message.processing_end = datetime.utcnow()

                # Update statistics
                self.processed_messages += 1

                self.logger.info(f"Message acknowledged successfully: {message_id}")
            else:
                # Handle failure
                await self._handle_message_failure(message)

            # Update message history
            self.message_history[message.queue_name].remove(message_id)

        except Exception as e:
            self.logger.error(f"Error acknowledging message: {e}")

    async def _handle_message_failure(self, message: QueueMessage):
        """Handle message processing failure.Handle message processing failure."""
        try:
            if message.retry_count < self.max_retry_attempts:
                # Retry message
                message.retry_count += 1
                message.status = MessageStatus.RETRYING

                # Add to retry queue
                await self._add_message_to_queue("retry_queue", message)

                self.logger.info(
                    f"Message queued for retry: {message.message_id} (attempt {message.retry_count})"
                )
            else:
                # Move to dead letter queue
                message.status = MessageStatus.DEAD_LETTER
                await self._add_message_to_queue("dead_letter_queue", message)

                # Update statistics
                self.failed_messages += 1

                self.logger.warning(
                    f"Message moved to dead letter queue: {message.message_id}",
                )

        except Exception as e:
            self.logger.error(f"Error handling message failure: {e}")

    async def get_queue_metrics(self, queue_name: str) -> Optional[QueueMetrics]:
        """Get metrics for a specific queue.Get metrics for a specific queue."""
        try:
            if queue_name not in self.queues:
                return None

            # Calculate metrics
            pending_messages = len(self.queue_messages[queue_name])
            if queue_name in self.priority_queues:
                pending_messages += len(self.priority_queues[queue_name])

            processing_messages = sum(
                1
                for msg in self.messages.values()
                if msg.queue_name == queue_name
                and msg.status == MessageStatus.PROCESSING
            )

            completed_messages = sum(
                1
                for msg in self.messages.values()
                if msg.queue_name == queue_name
                and msg.status == MessageStatus.COMPLETED
            )

            failed_messages = sum(
                1
                for msg in self.messages.values()
                if msg.queue_name == queue_name and msg.status == MessageStatus.FAILED
            )

            retry_messages = sum(
                1
                for msg in self.messages.values()
                if msg.queue_name == queue_name and msg.status == MessageStatus.RETRYING
            )

            dead_letter_messages = sum(
                1
                for msg in self.messages.values()
                if msg.queue_name == queue_name
                and msg.status == MessageStatus.DEAD_LETTER
            )

            # Calculate average processing time
            processing_times = []
            for msg in self.messages.values():
                if (
                    msg.queue_name == queue_name
                    and msg.status == MessageStatus.COMPLETED
                    and msg.processing_start
                    and msg.processing_end
                ):
                    processing_time = (
                        msg.processing_end - msg.processing_start
                    ).total_seconds()
                    processing_times.append(processing_time)

            average_processing_time = (
                sum(processing_times) / len(processing_times)
                if processing_times
                else 0.0
            )

            # Calculate throughput (messages per minute)
            recent_messages = [
                msg
                for msg in self.messages.values()
                if (
                    msg.queue_name == queue_name
                    and msg.status == MessageStatus.COMPLETED
                    and msg.processing_end
                    and (datetime.utcnow() - msg.processing_end).total_seconds() < 60
                )
            ]
            throughput_per_minute = len(recent_messages)

            metrics = QueueMetrics(
                queue_name=queue_name,
                message_count=pending_messages
                + processing_messages
                + completed_messages,
                consumer_count=1,  # Simplified for now
                pending_messages=pending_messages,
                processing_messages=processing_messages,
                completed_messages=completed_messages,
                failed_messages=failed_messages,
                retry_messages=retry_messages,
                dead_letter_messages=dead_letter_messages,
                average_processing_time=average_processing_time,
                throughput_per_minute=throughput_per_minute,
                last_updated=datetime.utcnow(),
            )

            return metrics

        except Exception as e:
            self.logger.error(f"Error getting queue metrics: {e}")
            return None

    async def _process_message_queues(self):
        """Process messages in all queues.Process messages in all queues."""
        while True:
            try:
                # Process each queue
                for queue_name in self.queues:
                    if queue_name in ["dead_letter_queue", "retry_queue"]:
                        continue  # Skip special queues

                    # Process messages in queue
                    await self._process_queue_messages(queue_name)

                await asyncio.sleep(1)  # Process every second

            except Exception as e:
                self.logger.error(f"Error processing message queues: {e}")
                await asyncio.sleep(5)

    async def _process_queue_messages(self, queue_name: str):
        """Process messages in a specific queue.Process messages in a specific queue."""
        try:
            # Get message from queue
            message = await self.receive_message(queue_name, timeout=0)

            if message:
                # Process message (simplified for now)
                await asyncio.sleep(0.1)  # Simulate processing

                # Acknowledge message
                await self.acknowledge_message(message.message_id, success=True)

        except Exception as e:
            self.logger.error(f"Error processing queue messages for {queue_name}: {e}")

    async def _cleanup_expired_messages(self):
        """Clean up expired messages.Clean up expired messages."""
        while True:
            try:
                current_time = datetime.utcnow()

                expired_messages = []
                for message_id, message in self.messages.items():
                    if (
                        message.expiration_time
                        and message.expiration_time < current_time
                        and message.status == MessageStatus.PENDING
                    ):
                        expired_messages.append(message_id)

                for message_id in expired_messages:
                    message = self.messages[message_id]
                    message.status = MessageStatus.EXPIRED

                    # Remove from queue
                    if message.message_id in self.queue_messages[message.queue_name]:
                        self.queue_messages[message.queue_name].remove(
                            message.message_id
                        )

                if expired_messages:
                    self.logger.info(
                        f"Cleaned up {len(expired_messages)} expired messages"
                    )

                await asyncio.sleep(60)  # Clean up every minute

            except Exception as e:
                self.logger.error(f"Error cleaning up expired messages: {e}")
                await asyncio.sleep(60)

    async def _update_queue_metrics(self):
        """Update queue metrics.Update queue metrics."""
        while True:
            try:
                # Update metrics for all queues
                for queue_name in self.queues:
                    await self.get_queue_metrics(queue_name)

                await asyncio.sleep(30)  # Update every 30 seconds

            except Exception as e:
                self.logger.error(f"Error updating queue metrics: {e}")
                await asyncio.sleep(30)

    async def _close_connections(self):
        """Close RabbitMQ and Redis connections.Close RabbitMQ and Redis connections."""
        try:
            if self.channel:
                self.channel.close()

            if self.rabbitmq_connection:
                self.rabbitmq_connection.close()

            if self.redis_connection:
                self.redis_connection.close()

            self.logger.info("Connections closed successfully")

        except Exception as e:
            self.logger.error(f"Error closing connections: {e}")

    def get_message(self, message_id: str) -> Optional[QueueMessage]:
        """Get message by ID.Get message by ID."""
        try:
            return self.messages.get(message_id)
        except Exception as e:
            self.logger.error(f"Error getting message: {e}")
            return None

    def get_queue_config(self, queue_name: str) -> Optional[QueueConfig]:
        """Get queue configuration by name.Get queue configuration by name."""
        try:
            return self.queues.get(queue_name)
        except Exception as e:
            self.logger.error(f"Error getting queue config: {e}")
            return None

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics.Get performance metrics."""
        return {
            "total_messages": self.total_messages,
            "processed_messages": self.processed_messages,
            "failed_messages": self.failed_messages,
            "average_processing_time": self.average_processing_time,
            "message_priorities_supported": [
                priority.value for priority in MessagePriority
            ],
            "message_types_supported": [msg_type.value for msg_type in MessageType],
            "queue_types_supported": [queue_type.value for queue_type in QueueType],
            "message_statuses_supported": [status.value for status in MessageStatus],
            "total_queues": len(self.queues),
            "total_messages_stored": len(self.messages),
            "max_retry_attempts": self.max_retry_attempts,
            "message_ttl": self.message_ttl,
            "enable_priority_queues": self.enable_priority_queues,
            "rabbitmq_available": RABBITMQ_AVAILABLE,
            "redis_available": REDIS_AVAILABLE,
            "rabbitmq_host": self.rabbitmq_host,
            "rabbitmq_port": self.rabbitmq_port,
            "redis_host": self.redis_host,
            "redis_port": self.redis_port,
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "rabbitmq_host": "localhost",
        "rabbitmq_port": 5672,
        "rabbitmq_username": "guest",
        "rabbitmq_password": "guest",
        "redis_host": "localhost",
        "redis_port": 6379,
        "enable_priority_queues": True,
        "max_retry_attempts": 3,
        "message_ttl": 3600,
    }

    # Initialize message queue system
    queue_system = MessageQueueSystem(config)

    print("MessageQueueSystem system initialized successfully!")

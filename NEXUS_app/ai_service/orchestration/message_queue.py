"""
Message Queue System - Priority-based Messaging and Routing

This module implements a message queue for inter-agent communication.
"""

import asyncio
import logging
from collections import deque
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class MessagePriority(Enum):
    """Enumeration for message priorities."""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0

@dataclass
class Message:
    """Represents a message in the queue."""
    message_id: str
    priority: MessagePriority
    payload: Any
    sender_id: str

class MessageQueue:
    """A simple in-memory priority message queue."""

    def __init__(self):
        """Initializes the MessageQueue."""
        self.queues: Dict[MessagePriority, deque] = {p: deque() for p in MessagePriority}
        self.logger = logging.getLogger(__name__)
        self.logger.info("MessageQueue initialized")

    async def send_message(self, priority: MessagePriority, payload: Any, sender_id: str):
        """Sends a message with a given priority."""
        message_id = f"msg_{len(self.queues[priority]) + 1}"
        message = Message(message_id=message_id, priority=priority, payload=payload, sender_id=sender_id)
        self.queues[priority].append(message)
        self.logger.info(f"Message {message_id} sent with priority {priority.name}")

    async def receive_message(self) -> Optional[Message]:
        """Receives a message, honoring priority."""
        for priority in sorted(self.queues.keys(), key=lambda p: p.value):
            if self.queues[priority]:
                message = self.queues[priority].popleft()
                self.logger.info(f"Message {message.message_id} received")
                return message
        return None

def test_message_queue():
    """Tests the MessageQueue system."""
    logging.basicConfig(level=logging.INFO)
    print("🧪 Testing Message Queue System")
    mq = MessageQueue()

    async def main():
        await mq.send_message(MessagePriority.NORMAL, {"task": "process_data"}, "agent1")
        await mq.send_message(MessagePriority.CRITICAL, {"task": "shutdown"}, "admin")

        msg1 = await mq.receive_message()
        if msg1:
            print(f"  Received 1: {msg1.payload} (Priority: {msg1.priority.name})")

        msg2 = await mq.receive_message()
        if msg2:
            print(f"  Received 2: {msg2.payload} (Priority: {msg2.priority.name})")

    asyncio.run(main())

if __name__ == "__main__":
    test_message_queue()

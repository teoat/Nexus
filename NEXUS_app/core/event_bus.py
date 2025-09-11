#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Event Bus System for Nexus Platform
Provides inter-component communication, event-driven architecture, and service discovery.
"""

import asyncio
import json
import logging
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
import queue

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Types of system events"""
    COMPONENT_STARTED = "component_started"
    COMPONENT_STOPPED = "component_stopped"
    COMPONENT_ERROR = "component_error"
    DATA_UPDATED = "data_updated"
    CONFIG_CHANGED = "config_changed"
    HEALTH_CHECK = "health_check"
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    AGENT_REGISTERED = "agent_registered"
    AGENT_UNREGISTERED = "agent_unregistered"
    SYSTEM_SHUTDOWN = "system_shutdown"
    CUSTOM = "custom"

@dataclass
class Event:
    """Event structure"""
    id: str
    type: EventType
    source: str
    data: Dict[str, Any]
    timestamp: str
    target: Optional[str] = None  # None for broadcast
    priority: int = 0  # Higher number = higher priority
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class ComponentInfo:
    """Component information"""
    id: str
    name: str
    type: str
    status: str
    started_at: str
    last_seen: str
    capabilities: List[str]
    dependencies: List[str]
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if not self.metadata:
            self.metadata = {}

class EventBus:
    """Central event bus for inter-component communication"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        
        # Event handling
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.event_queue = queue.PriorityQueue()
        self.event_history: List[Event] = []
        self.max_history = 1000
        
        # Component registry
        self.components: Dict[str, ComponentInfo] = {}
        self.component_locks: Dict[str, threading.Lock] = {}
        
        # Service discovery
        self.service_registry: Dict[str, Dict[str, Any]] = {}
        self.service_locks: Dict[str, threading.Lock] = {}
        
        # Event processing
        self.running = False
        self.event_thread = None
        self.health_thread = None
        
        # Initialize event handlers
        self._initialize_event_handlers()
        
        # Start event processing
        self.start()
    
    def _initialize_event_handlers(self):
        """Initialize default event handlers"""
        for event_type in EventType:
            self.event_handlers[event_type] = []
    
    def start(self):
        """Start the event bus"""
        self.running = True
        
        # Start event processing thread
        self.event_thread = threading.Thread(target=self._event_worker, daemon=True)
        self.event_thread.start()
        
        # Start health monitoring thread
        self.health_thread = threading.Thread(target=self._health_worker, daemon=True)
        self.health_thread.start()
        
        logger.info("Event bus started")
    
    def stop(self):
        """Stop the event bus"""
        self.running = False
        
        # Wait for threads to finish
        if self.event_thread:
            self.event_thread.join(timeout=5)
        if self.health_thread:
            self.health_thread.join(timeout=5)
        
        logger.info("Event bus stopped")
    
    def publish_event(self, event: Event):
        """Publish an event to the bus"""
        try:
            # Add to priority queue (negative priority for max-heap behavior)
            self.event_queue.put((-event.priority, time.time(), event))
            
            # Add to history
            self.event_history.append(event)
            if len(self.event_history) > self.max_history:
                self.event_history.pop(0)
            
            logger.debug(f"Published event: {event.type.value} from {event.source}")
            
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
    
    def subscribe(self, event_type: EventType, handler: Callable):
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.info(f"Subscribed handler to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, handler: Callable):
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
                logger.info(f"Unsubscribed handler from {event_type.value}")
            except ValueError:
                logger.warning(f"Handler not found for {event_type.value}")
    
    def _event_worker(self):
        """Background worker for processing events"""
        while self.running:
            try:
                if not self.event_queue.empty():
                    priority, timestamp, event = self.event_queue.get_nowait()
                    
                    # Process event
                    self._process_event(event)
                else:
                    time.sleep(0.01)  # Small delay when no events
                    
            except Exception as e:
                logger.error(f"Error in event worker: {e}")
                time.sleep(1)
    
    def _process_event(self, event: Event):
        """Process a single event"""
        try:
            # Get handlers for this event type
            handlers = self.event_handlers.get(event.type, [])
            
            # Call all handlers
            for handler in handlers:
                try:
                        # Async handler - create task
                        asyncio.create_task(handler(event))
                    else:
                        # Sync handler - call directly
                        handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")
            
            # Handle component events
            if event.type == EventType.COMPONENT_STARTED:
                self._handle_component_started(event)
            elif event.type == EventType.COMPONENT_STOPPED:
                self._handle_component_stopped(event)
            elif event.type == EventType.COMPONENT_ERROR:
                self._handle_component_error(event)
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")
    
    def _handle_component_started(self, event: Event):
        """Handle component started event"""
        component_id = event.data.get("component_id")
        if component_id:
            self._update_component_status(component_id, "running")
    
    def _handle_component_stopped(self, event: Event):
        """Handle component stopped event"""
        component_id = event.data.get("component_id")
        if component_id:
            self._update_component_status(component_id, "stopped")
    
    def _handle_component_error(self, event: Event):
        """Handle component error event"""
        component_id = event.data.get("component_id")
        error_message = event.data.get("error", "Unknown error")
        if component_id:
            self._update_component_status(component_id, "error")
            logger.error(f"Component {component_id} error: {error_message}")
    
    def register_component(self, component_info: ComponentInfo):
        """Register a component with the event bus"""
        component_id = component_info.id
        
        # Create lock for component
        if component_id not in self.component_locks:
            self.component_locks[component_id] = threading.Lock()
        
        with self.component_locks[component_id]:
            self.components[component_id] = component_info
        
        # Publish registration event
        event = Event(
            id=str(uuid.uuid4()),
            type=EventType.AGENT_REGISTERED,
            source="event_bus",
            data={
                "component_id": component_id,
                "component_name": component_info.name,
                "component_type": component_info.type
            },
            timestamp=datetime.now().isoformat()
        )
        self.publish_event(event)
        
        logger.info(f"Registered component: {component_info.name} ({component_id})")
    
    def unregister_component(self, component_id: str):
        """Unregister a component from the event bus"""
        if component_id in self.components:
            with self.component_locks[component_id]:
                component_info = self.components[component_id]
                del self.components[component_id]
            
            # Publish unregistration event
            event = Event(
                id=str(uuid.uuid4()),
                type=EventType.AGENT_UNREGISTERED,
                source="event_bus",
                data={
                    "component_id": component_id,
                    "component_name": component_info.name
                },
                timestamp=datetime.now().isoformat()
            )
            self.publish_event(event)
            
            logger.info(f"Unregistered component: {component_id}")
    
    def _update_component_status(self, component_id: str, status: str):
        """Update component status"""
        if component_id in self.components:
            with self.component_locks[component_id]:
                self.components[component_id].status = status
                self.components[component_id].last_seen = datetime.now().isoformat()
    
    def get_component(self, component_id: str) -> Optional[ComponentInfo]:
        """Get component information"""
        with self.component_locks.get(component_id, threading.Lock()):
            return self.components.get(component_id)
    
    def get_components_by_type(self, component_type: str) -> List[ComponentInfo]:
        components = []
        for component in self.components.values():
            if component.type == component_type:
                components.append(component)
        return components
    
    def discover_services(self, service_type: str) -> List[Dict[str, Any]]:
        services = []
        for component in self.components.values():
            if service_type in component.capabilities:
                services.append({
                    "component_id": component.id,
                    "name": component.name,
                    "type": component.type,
                    "status": component.status,
                    "capabilities": component.capabilities,
                    "metadata": component.metadata
                })
        return services
    
    def register_service(self, service_name: str, service_info: Dict[str, Any]):
        """Register a service for discovery"""
        if service_name not in self.service_locks:
            self.service_locks[service_name] = threading.Lock()
        
        with self.service_locks[service_name]:
            self.service_registry[service_name] = service_info
        
        logger.info(f"Registered service: {service_name}")
    
    def get_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get service information"""
        with self.service_locks.get(service_name, threading.Lock()):
            return self.service_registry.get(service_name)
    
    def _health_worker(self):
        """Background worker for health monitoring"""
        while self.running:
            try:
                # Check component health
                current_time = time.time()
                for component_id, component in self.components.items():
                    # Check if component is responsive
                    last_seen = datetime.fromisoformat(component.last_seen).timestamp()
                    if current_time - last_seen > 300:  # 5 minutes timeout
                        self._update_component_status(component_id, "unresponsive")
                
                # Publish health check event
                event = Event(
                    id=str(uuid.uuid4()),
                    type=EventType.HEALTH_CHECK,
                    source="event_bus",
                    data={
                        "total_components": len(self.components),
                        "active_components": len([c for c in self.components.values() if c.status == "running"]),
                        "timestamp": datetime.now().isoformat()
                    },
                    timestamp=datetime.now().isoformat()
                )
                self.publish_event(event)
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in health worker: {e}")
                time.sleep(60)
    
    def get_event_bus_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            "running": self.running,
            "total_events": len(self.event_history),
            "queue_size": self.event_queue.qsize(),
            "total_components": len(self.components),
            "active_components": len([c for c in self.components.values() if c.status == "running"]),
            "registered_services": len(self.service_registry),
            "event_handlers": {
                event_type.value: len(handlers)
                for event_type, handlers in self.event_handlers.items()
            }
        }
    
    def get_recent_events(self, limit: int = 100) -> List[Event]:
        """Get recent events"""
        return self.event_history[-limit:]
    
    def get_events_by_type(self, event_type: EventType, limit: int = 100) -> List[Event]:
        events = [e for e in self.event_history if e.type == event_type]
        return events[-limit:]

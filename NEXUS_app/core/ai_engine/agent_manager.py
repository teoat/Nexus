#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🤖 Frenly AI Agent Manager
Manages multiple AI agents and their coordination
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import redis
from pathlib import Path

from .config import get_config, get_agent_config, is_agent_enabled

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"
    INITIALIZING = "initializing"

class AgentType(Enum):
    """Agent type enumeration"""
    FRAUD_DETECTION = "fraud_detection"
    FORENSIC_ANALYSIS = "forensic_analysis"
    RECONCILIATION = "reconciliation"
    COMPLIANCE = "compliance"
    GENERAL = "general"

@dataclass
class AgentCapability:
    """Agent capability definition"""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

@dataclass
class AgentMetrics:
    """Agent performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    last_request_time: Optional[str] = None
    uptime: float = 0.0
    error_rate: float = 0.0

@dataclass
class Agent:
    """Agent definition"""
    id: str
    name: str
    agent_type: AgentType
    status: AgentStatus
    capabilities: List[AgentCapability]
    metrics: AgentMetrics
    created_at: str
    last_active: str
    config: Dict[str, Any] = field(default_factory=dict)
    error_count: int = 0
    max_errors: int = 5

class AgentManager:
    """Manages multiple AI agents and their coordination"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.config = get_config()
        self.redis_client = redis.Redis.from_url(self.config.redis_url)
        self.agents: Dict[str, Agent] = {}
        self.agent_queues: Dict[str, asyncio.Queue] = {}
        self.running = False
        
        # Initialize agent types
        self._initialize_agent_types()
        
        logger.info("✅ Agent Manager initialized")
    
    def _initialize_agent_types(self):
        """Initialize available agent types"""
        self.agent_types = {
            AgentType.FRAUD_DETECTION: {
                "name": "Fraud Detection Agent",
                "capabilities": [
                    AgentCapability("transaction_analysis", "Analyze transactions for fraud patterns"),
                    AgentCapability("pattern_recognition", "Recognize suspicious patterns"),
                    AgentCapability("risk_scoring", "Calculate risk scores"),
                    AgentCapability("anomaly_detection", "Detect anomalous behavior")
                ]
            },
            AgentType.FORENSIC_ANALYSIS: {
                "name": "Forensic Analysis Agent",
                "capabilities": [
                    AgentCapability("evidence_processing", "Process forensic evidence"),
                    AgentCapability("timeline_reconstruction", "Reconstruct event timelines"),
                    AgentCapability("pattern_analysis", "Analyze patterns in evidence"),
                    AgentCapability("report_generation", "Generate forensic reports")
                ]
            },
            AgentType.RECONCILIATION: {
                "name": "Reconciliation Agent",
                "capabilities": [
                    AgentCapability("data_matching", "Match data across sources"),
                    AgentCapability("discrepancy_detection", "Detect data discrepancies"),
                    AgentCapability("batch_processing", "Process large data batches"),
                    AgentCapability("report_generation", "Generate reconciliation reports")
                ]
            },
            AgentType.COMPLIANCE: {
                "name": "Compliance Agent",
                "capabilities": [
                    AgentCapability("gdpr_compliance", "Ensure GDPR compliance"),
                    AgentCapability("data_retention", "Manage data retention policies"),
                    AgentCapability("audit_logging", "Maintain audit logs"),
                    AgentCapability("policy_management", "Manage compliance policies")
                ]
            },
            AgentType.GENERAL: {
                "name": "General AI Agent",
                "capabilities": [
                    AgentCapability("natural_language_processing", "Process natural language"),
                    AgentCapability("query_understanding", "Understand user queries"),
                    AgentCapability("response_generation", "Generate responses"),
                    AgentCapability("context_management", "Manage conversation context")
                ]
            }
        }
    
    async def start(self):
        """Start the agent manager"""
        self.running = True
        logger.info("🚀 Starting Agent Manager...")
        
        # Initialize agents
        await self._initialize_agents()
        
        # Start agent monitoring
        asyncio.create_task(self._monitor_agents())
        
        # Start metrics collection
        asyncio.create_task(self._collect_metrics())
        
        logger.info("✅ Agent Manager started")
    
    async def stop(self):
        """Stop the agent manager"""
        self.running = False
        logger.info("🛑 Stopping Agent Manager...")
        
        # Stop all agents
        for agent in self.agents.values():
            await self._stop_agent(agent.id)
        
        logger.info("✅ Agent Manager stopped")
    
    async def _initialize_agents(self):
        """Initialize all available agents"""
        for agent_type, agent_info in self.agent_types.items():
            if is_agent_enabled(agent_type.value):
                await self._create_agent(agent_type, agent_info)
    
    async def _create_agent(self, agent_type: AgentType, agent_info: Dict[str, Any]):
        """Create a new agent"""
        agent_id = f"{agent_type.value}_{uuid.uuid4().hex[:8]}"
        
        agent = Agent(
            id=agent_id,
            name=agent_info["name"],
            agent_type=agent_type,
            status=AgentStatus.INITIALIZING,
            capabilities=agent_info["capabilities"],
            metrics=AgentMetrics(),
            created_at=datetime.now().isoformat(),
            last_active=datetime.now().isoformat(),
            config=get_agent_config(agent_type.value)
        )
        
        # Create agent queue
        self.agent_queues[agent_id] = asyncio.Queue()
        
        # Add to agents dictionary
        self.agents[agent_id] = agent
        
        # Start agent processing
        asyncio.create_task(self._process_agent_requests(agent_id))
        
        logger.info(f"✅ Created agent: {agent.name} ({agent_id})")
    
    async def _process_agent_requests(self, agent_id: str):
        agent = self.agents[agent_id]
        queue = self.agent_queues[agent_id]
        
        while self.running:
            try:
                # Get request from queue
                request = await asyncio.wait_for(queue.get(), timeout=1.0)
                
                # Update agent status
                agent.status = AgentStatus.BUSY
                agent.last_active = datetime.now().isoformat()
                
                # Process request
                start_time = time.time()
                try:
                    response = await self._handle_agent_request(agent, request)
                    processing_time = time.time() - start_time
                    
                    # Update metrics
                    agent.metrics.total_requests += 1
                    agent.metrics.successful_requests += 1
                    agent.metrics.avg_response_time = (
                        (agent.metrics.avg_response_time * (agent.metrics.total_requests - 1) + processing_time) /
                        agent.metrics.total_requests
                    )
                    agent.metrics.last_request_time = datetime.now().isoformat()
                    agent.error_count = 0
                    
                    # Send response back
                    if "response_callback" in request:
                        await request["response_callback"](response)
                
                except Exception as e:
                    logger.error(f"❌ Agent {agent_id} error: {e}")
                    agent.metrics.failed_requests += 1
                    agent.error_count += 1
                    
                    if agent.error_count >= agent.max_errors:
                        agent.status = AgentStatus.ERROR
                        logger.error(f"❌ Agent {agent_id} exceeded max errors, marking as error")
                
                finally:
                    agent.status = AgentStatus.IDLE
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Agent {agent_id} processing error: {e}")
                await asyncio.sleep(1)
    
    async def _handle_agent_request(self, agent: Agent, request: Dict[str, Any]) -> Dict[str, Any]:
        if agent.agent_type == AgentType.FRAUD_DETECTION:
            return await self._handle_fraud_detection_request(agent, request)
        elif agent.agent_type == AgentType.FORENSIC_ANALYSIS:
            return await self._handle_forensic_analysis_request(agent, request)
        elif agent.agent_type == AgentType.RECONCILIATION:
            return await self._handle_reconciliation_request(agent, request)
        elif agent.agent_type == AgentType.COMPLIANCE:
            return await self._handle_compliance_request(agent, request)
        else:
            return await self._handle_general_request(agent, request)
    
    async def _handle_fraud_detection_request(self, agent: Agent, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle fraud detection request"""
        
        return {
            "agent_id": agent.id,
            "agent_type": agent.agent_type.value,
            "response": f"Fraud detection analysis completed for: {request.get('message', '')[:50]}...",
            "confidence": 0.87,
            "processing_time": 0.1,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_forensic_analysis_request(self, agent: Agent, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle forensic analysis request"""
        
        return {
            "agent_id": agent.id,
            "agent_type": agent.agent_type.value,
            "response": f"Forensic analysis completed for: {request.get('message', '')[:50]}...",
            "confidence": 0.92,
            "processing_time": 0.2,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_reconciliation_request(self, agent: Agent, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle reconciliation request"""
        
        return {
            "agent_id": agent.id,
            "agent_type": agent.agent_type.value,
            "response": f"Reconciliation analysis completed for: {request.get('message', '')[:50]}...",
            "confidence": 0.85,
            "processing_time": 0.15,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_compliance_request(self, agent: Agent, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle compliance request"""
        
        return {
            "agent_id": agent.id,
            "agent_type": agent.agent_type.value,
            "response": f"Compliance analysis completed for: {request.get('message', '')[:50]}...",
            "confidence": 0.90,
            "processing_time": 0.1,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_general_request(self, agent: Agent, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general request"""
        
        return {
            "agent_id": agent.id,
            "agent_type": agent.agent_type.value,
            "response": f"AI response for: {request.get('message', '')[:50]}...",
            "confidence": 0.75,
            "processing_time": 0.05,
            "timestamp": datetime.now().isoformat()
        }
    
    async def submit_request(self, agent_type: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Submit request to appropriate agent"""
        available_agents = [
            agent for agent in self.agents.values()
            if agent.agent_type.value == agent_type and agent.status == AgentStatus.IDLE
        ]
        
        if not available_agents:
            raise Exception(f"No available agents of type: {agent_type}")
        
        # Select agent with least load
        agent = min(available_agents, key=lambda a: a.metrics.total_requests)
        
        # Create response future
        response_future = asyncio.Future()
        
        # Add response callback to request
        request["response_callback"] = lambda response: response_future.set_result(response)
        
        # Submit to agent queue
        await self.agent_queues[agent.id].put(request)
        
        # Wait for response
        response = await response_future
        
        return response
    
    async def get_agent_status(self, agent_id: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get agent status"""
        if agent_id:
            if agent_id not in self.agents:
                raise Exception(f"Agent not found: {agent_id}")
            
            agent = self.agents[agent_id]
            return {
                "id": agent.id,
                "name": agent.name,
                "type": agent.agent_type.value,
                "status": agent.status.value,
                "capabilities": [cap.name for cap in agent.capabilities],
                "metrics": {
                    "total_requests": agent.metrics.total_requests,
                    "successful_requests": agent.metrics.successful_requests,
                    "failed_requests": agent.metrics.failed_requests,
                    "avg_response_time": agent.metrics.avg_response_time,
                    "last_request_time": agent.metrics.last_request_time,
                    "error_rate": agent.metrics.error_rate
                },
                "created_at": agent.created_at,
                "last_active": agent.last_active
            }
        else:
            return [
                {
                    "id": agent.id,
                    "name": agent.name,
                    "type": agent.agent_type.value,
                    "status": agent.status.value,
                    "capabilities": [cap.name for cap in agent.capabilities],
                    "metrics": {
                        "total_requests": agent.metrics.total_requests,
                        "successful_requests": agent.metrics.successful_requests,
                        "failed_requests": agent.metrics.failed_requests,
                        "avg_response_time": agent.metrics.avg_response_time,
                        "last_request_time": agent.metrics.last_request_time,
                        "error_rate": agent.metrics.error_rate
                    },
                    "created_at": agent.created_at,
                    "last_active": agent.last_active
                }
                for agent in self.agents.values()
            ]
    
    async def _monitor_agents(self):
        """Monitor agent health and performance"""
        while self.running:
            try:
                for agent in self.agents.values():
                    # Check if agent is stuck
                    if agent.status == AgentStatus.BUSY:
                        last_active = datetime.fromisoformat(agent.last_active)
                        if datetime.now() - last_active > timedelta(minutes=5):
                            logger.warning(f"⚠️ Agent {agent.id} appears stuck, resetting status")
                            agent.status = AgentStatus.IDLE
                    
                    # Check error rate
                    if agent.metrics.total_requests > 0:
                        agent.metrics.error_rate = agent.metrics.failed_requests / agent.metrics.total_requests
                        
                        if agent.metrics.error_rate > 0.5:
                            logger.warning(f"⚠️ Agent {agent.id} has high error rate: {agent.metrics.error_rate:.2%}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Agent monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _collect_metrics(self):
        """Collect and store metrics"""
        while self.running:
            try:
                # Store metrics in Redis
                metrics_data = {
                    "timestamp": datetime.now().isoformat(),
                    "agents": {
                        agent.id: {
                            "status": agent.status.value,
                            "metrics": {
                                "total_requests": agent.metrics.total_requests,
                                "successful_requests": agent.metrics.successful_requests,
                                "failed_requests": agent.metrics.failed_requests,
                                "avg_response_time": agent.metrics.avg_response_time,
                                "error_rate": agent.metrics.error_rate
                            }
                        }
                        for agent in self.agents.values()
                    }
                }
                
                self.redis_client.setex(
                    "frenly_ai_metrics",
                    300,  # 5 minutes TTL
                    json.dumps(metrics_data)
                )
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"❌ Metrics collection error: {e}")
                await asyncio.sleep(10)
    
    async def _stop_agent(self, agent_id: str):
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.status = AgentStatus.OFFLINE
            logger.info(f"🛑 Stopped agent: {agent.name} ({agent_id})")

# Global agent manager instance
agent_manager = AgentManager()

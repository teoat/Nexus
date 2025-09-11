#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Collaborative Agent System
Enhanced agent coordination with advanced collaboration features including:
- Shared workspaces and collective decision making
- Task delegation and load balancing
- Real-time collaboration and conflict resolution
- Collective intelligence and knowledge sharing
- Workflow orchestration and parallel processing
"""

import asyncio
import json
import logging
import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import queue
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollaborationMode(Enum):
    """Different modes of agent collaboration"""
    INDIVIDUAL = "individual"           # Agents work independently
    COOPERATIVE = "cooperative"         # Agents share information
    COLLABORATIVE = "collaborative"     # Agents work together on tasks
    COLLECTIVE = "collective"           # Agents make collective decisions
    SWARM = "swarm"                     # Agents work in parallel with shared goals

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

class TaskStatus(Enum):
    """Task status states"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class CollaborativeTask:
    """Enhanced task with collaboration features"""
    id: str
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    assigned_agents: List[str]
    required_skills: List[str]
    dependencies: List[str]
    estimated_duration: int  # minutes
    actual_duration: Optional[int] = None
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: float = 0.0
    subtasks: List[str] = None
    collaboration_mode: CollaborationMode = CollaborationMode.COOPERATIVE
    shared_resources: List[str] = None
    collective_decisions: List[Dict[str, Any]] = None
    knowledge_artifacts: List[str] = None
    
    def __post_init__(self):
        """
          Post Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        if self.subtasks is None:
            self.subtasks = []
        if self.shared_resources is None:
            self.shared_resources = []
        if self.collective_decisions is None:
            self.collective_decisions = []
        if self.knowledge_artifacts is None:
            self.knowledge_artifacts = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

@dataclass
class SharedWorkspace:
    """Shared workspace for collaborative work"""
    id: str
    name: str
    description: str
    agents: List[str]
    tasks: List[str]
    resources: List[str]
    access_level: str  # read, write, admin
    created_at: str = ""
    last_accessed: str = ""
    
    def __post_init__(self):
        """
          Post Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

@dataclass
class CollectiveDecision:
    """Record of collective decision making"""
    id: str
    decision_type: str
    question: str
    options: List[str]
    agent_votes: Dict[str, str]
    final_decision: str
    reasoning: str
    created_at: str = ""
    resolved_at: Optional[str] = None
    
    def __post_init__(self):
        """
          Post Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

class CollaborativeAgentSystem:
    """Enhanced collaborative agent coordination system"""
    
    def __init__(self, workspace_path: str):
        """
          Init  
        
        
        Args:
            workspace_path: Description of workspace_path
    
        Example:
            TBD: Add usage example
        """
        self.workspace_path = Path(workspace_path)
        self.agents: Dict[str, Any] = {}
        self.tasks: Dict[str, CollaborativeTask] = {}
        self.workspaces: Dict[str, SharedWorkspace] = {}
        self.decisions: Dict[str, CollectiveDecision] = {}
        self.knowledge_base: Dict[str, Any] = {}
        
        # File paths
        self.data_dir = self.workspace_path / ".mcp" / "collaborative_system"
        self.agents_file = self.data_dir / "agents.json"
        self.tasks_file = self.data_dir / "tasks.json"
        self.workspaces_file = self.data_dir / "workspaces.json"
        self.decisions_file = self.data_dir / "decisions.json"
        self.knowledge_file = self.data_dir / "knowledge.json"
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Collaboration queues
        self.task_queue = queue.PriorityQueue()
        self.decision_queue = queue.Queue()
        self.knowledge_queue = queue.Queue()
        
        # Threading and async support
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running = True
        
        # Load existing data
        self.load_data()
        
        # Start background workers
        self.start_background_workers()
    
    def load_data(self):
        """Load all collaborative system data"""
        try:
            # Load agents
            if self.agents_file.exists():
                with open(self.agents_file, 'r') as f:
                    self.agents = json.load(f)
            
            # Load tasks
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r') as f:
                    data = json.load(f)
                    for task_id, task_data in data.items():
                        self.tasks[task_id] = CollaborativeTask(**task_data)
            
            # Load workspaces
            if self.workspaces_file.exists():
                with open(self.workspaces_file, 'r') as f:
                    data = json.load(f)
                    for ws_id, ws_data in data.items():
                        self.workspaces[ws_id] = SharedWorkspace(**ws_data)
            
            # Load decisions
            if self.decisions_file.exists():
                with open(self.decisions_file, 'r') as f:
                    data = json.load(f)
                    for dec_id, dec_data in data.items():
                        self.decisions[dec_id] = CollectiveDecision(**dec_data)
            
            # Load knowledge base
            if self.knowledge_file.exists():
                with open(self.knowledge_file, 'r') as f:
                    self.knowledge_base = json.load(f)
                    
            logger.info(f"Loaded collaborative system: {len(self.agents)} agents, {len(self.tasks)} tasks, {len(self.workspaces)} workspaces")
            
        except Exception as e:
            logger.error(f"Error loading collaborative system data: {e}")
    
    def save_data(self):
        """Save all collaborative system data"""
        try:
            # Save agents
            with open(self.agents_file, 'w') as f:
                json.dump(self.agents, f, indent=2)
            
            # Save tasks
            with open(self.tasks_file, 'w') as f:
                json.dump({tid: asdict(task) for tid, task in self.tasks.items()}, f, indent=2)
            
            # Save workspaces
            with open(self.workspaces_file, 'w') as f:
                json.dump({wid: asdict(ws) for wid, ws in self.workspaces.items()}, f, indent=2)
            
            # Save decisions
            with open(self.decisions_file, 'w') as f:
                json.dump({did: asdict(dec) for did, dec in self.decisions.items()}, f, indent=2)
            
            # Save knowledge base
            with open(self.knowledge_file, 'w') as f:
                json.dump(self.knowledge_base, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving collaborative system data: {e}")
    
    def start_background_workers(self):
        """Start background workers for collaboration"""
        def task_worker():
            """
            Task Worker
            
            
            Example:
                TBD: Add usage example
            """
            while self.running:
                try:
                    if not self.task_queue.empty():
                        priority, task_id = self.task_queue.get(timeout=1)
                        self.process_task(task_id)
                    time.sleep(0.1)
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Task worker error: {e}")
        
        def decision_worker():
            """
            Decision Worker
            
            
            Example:
                TBD: Add usage example
            """
            while self.running:
                try:
                    if not self.decision_queue.empty():
                        decision_data = self.decision_queue.get(timeout=1)
                        self.process_collective_decision(decision_data)
                    time.sleep(0.1)
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Decision worker error: {e}")
        
        def knowledge_worker():
            """
            Knowledge Worker
            
            
            Example:
                TBD: Add usage example
            """
            while self.running:
                try:
                    if not self.knowledge_queue.empty():
                        knowledge_data = self.knowledge_queue.get(timeout=1)
                        self.process_knowledge_update(knowledge_data)
                    time.sleep(0.1)
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Knowledge worker error: {e}")
        
        # Start worker threads
        threading.Thread(target=task_worker, daemon=True).start()
        threading.Thread(target=decision_worker, daemon=True).start()
        threading.Thread(target=knowledge_worker, daemon=True).start()
        
        logger.info("Started background collaboration workers")
    
    def create_collaborative_task(self, title: str, description: str, priority: TaskPriority,
                                 required_skills: List[str], collaboration_mode: CollaborationMode = CollaborationMode.COOPERATIVE) -> str:
        """Create a new collaborative task"""
        task_id = str(uuid.uuid4())
        
        task = CollaborativeTask(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
            status=TaskStatus.PENDING,
            assigned_agents=[],
            required_skills=required_skills,
            dependencies=[],
            estimated_duration=0,
            collaboration_mode=collaboration_mode
        )
        
        self.tasks[task_id] = task
        self.task_queue.put((priority.value, task_id))
        self.save_data()
        
        logger.info(f"Created collaborative task: {title} (ID: {task_id})")
        return task_id
    
    def assign_task_to_agents(self, task_id: str, agent_ids: List[str]) -> bool:
        """Assign a task to multiple agents for collaboration"""
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False
        
        task = self.tasks[task_id]
        
        # Validate agents exist
        for agent_id in agent_ids:
            if agent_id not in self.agents:
                logger.error(f"Agent {agent_id} not found")
                return False
        
        # Assign task
        task.assigned_agents = agent_ids
        task.status = TaskStatus.ASSIGNED
        task.started_at = datetime.now().isoformat()
        
        # Update agent statuses
        for agent_id in agent_ids:
            if agent_id in self.agents:
                self.agents[agent_id]["current_task"] = task_id
                self.agents[agent_id]["status"] = "collaborating"
        
        self.save_data()
        logger.info(f"Assigned task {task_id} to agents: {agent_ids}")
        return True
    
    def create_shared_workspace(self, name: str, description: str, agent_ids: List[str], access_level: str = "write") -> str:
        """Create a shared workspace for collaborative work"""
        workspace_id = str(uuid.uuid4())
        
        workspace = SharedWorkspace(
            id=workspace_id,
            name=name,
            description=description,
            agents=agent_ids,
            tasks=[],
            resources=[],
            access_level=access_level
        )
        
        self.workspaces[workspace_id] = workspace
        self.save_data()
        
        logger.info(f"Created shared workspace: {name} (ID: {workspace_id})")
        return workspace_id
    
    def add_task_to_workspace(self, workspace_id: str, task_id: str) -> bool:
        """Add a task to a shared workspace"""
        if workspace_id not in self.workspaces:
            logger.error(f"Workspace {workspace_id} not found")
            return False
        
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False
        
        workspace = self.workspaces[workspace_id]
        if task_id not in workspace.tasks:
            workspace.tasks.append(task_id)
            workspace.last_accessed = datetime.now().isoformat()
            self.save_data()
            
            logger.info(f"Added task {task_id} to workspace {workspace_id}")
            return True
        
        return False
    
    def propose_collective_decision(self, question: str, options: List[str], 
                                   participating_agents: List[str], decision_type: str = "general") -> str:
        """Propose a decision for collective voting"""
        decision_id = str(uuid.uuid4())
        
        decision = CollectiveDecision(
            id=decision_id,
            decision_type=decision_type,
            question=question,
            options=options,
            agent_votes={},
            final_decision="",
            reasoning=""
        )
        
        self.decisions[decision_id] = decision
        self.decision_queue.put({
            "decision_id": decision_id,
            "participating_agents": participating_agents
        })
        
        self.save_data()
        logger.info(f"Proposed collective decision: {question} (ID: {decision_id})")
        return decision_id
    
    def vote_on_decision(self, decision_id: str, agent_id: str, choice: str, reasoning: str = "") -> bool:
        """Vote on a collective decision"""
        if decision_id not in self.decisions:
            logger.error(f"Decision {decision_id} not found")
            return False
        
        if choice not in self.decisions[decision_id].options:
            logger.error(f"Invalid choice: {choice}")
            return False
        
        decision = self.decisions[decision_id]
        decision.agent_votes[agent_id] = choice
        
        # Check if all participating agents have voted
        if len(decision.agent_votes) >= len(decision.agent_votes):
            self.resolve_decision(decision_id)
        
        self.save_data()
        logger.info(f"Agent {agent_id} voted '{choice}' on decision {decision_id}")
        return True
    
    def resolve_decision(self, decision_id: str):
        """Resolve a decision based on collective voting"""
        if decision_id not in self.decisions:
            return
        
        decision = self.decisions[decision_id]
        
        # Count votes
        vote_counts = {}
        for choice in decision.options:
            vote_counts[choice] = 0
        
        for choice in decision.agent_votes.values():
            vote_counts[choice] += 1
        
        # Find winner (simple majority)
        winner = max(vote_counts, key=vote_counts.get)
        decision.final_decision = winner
        decision.resolved_at = datetime.now().isoformat()
        
        # Generate reasoning
        total_votes = len(decision.agent_votes)
        winner_votes = vote_counts[winner]
        decision.reasoning = f"Decision resolved with {winner_votes}/{total_votes} votes for '{winner}'"
        
        self.save_data()
        logger.info(f"Resolved decision {decision_id}: {winner}")
    
    def share_knowledge(self, agent_id: str, knowledge_type: str, content: str, 
                       tags: List[str] = None, priority: int = 1) -> str:
        """Share knowledge with the collective system"""
        knowledge_id = str(uuid.uuid4())
        
        knowledge_entry = {
            "id": knowledge_id,
            "agent_id": agent_id,
            "type": knowledge_type,
            "content": content,
            "tags": tags or [],
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "access_count": 0,
            "rating": 0.0
        }
        
        self.knowledge_base[knowledge_id] = knowledge_entry
        self.knowledge_queue.put(knowledge_entry)
        self.save_data()
        
        logger.info(f"Agent {agent_id} shared knowledge: {knowledge_type}")
        return knowledge_id
    
    def search_knowledge(self, query: str, tags: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search the collective knowledge base"""
        results = []
        
        for knowledge_id, knowledge in self.knowledge_base.items():
            # Simple text search (could be enhanced with vector search)
            if query.lower() in knowledge["content"].lower():
                if tags is None or any(tag in knowledge["tags"] for tag in tags):
                    results.append(knowledge)
        
        # Sort by priority and rating
        results.sort(key=lambda x: (x["priority"], x["rating"]), reverse=True)
        
        return results[:limit]
    
    def get_collaboration_status(self) -> Dict[str, Any]:
        """Get overall collaboration system status"""
        active_tasks = sum(1 for task in self.tasks.values() 
                          if task.status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS])
        
        pending_decisions = sum(1 for decision in self.decisions.values() 
                               if not decision.resolved_at)
        
        total_knowledge = len(self.knowledge_base)
        
        return {
            "total_agents": len(self.agents),
            "active_tasks": active_tasks,
            "total_tasks": len(self.tasks),
            "shared_workspaces": len(self.workspaces),
            "pending_decisions": pending_decisions,
            "total_knowledge": total_knowledge,
            "system_status": "healthy" if self.running else "stopped"
        }
    
    def process_task(self, task_id: str):
        """Process a task in the background"""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        logger.info(f"Processing collaborative task: {task.title}")
        
        # Task processing logic would go here
        # This could involve agent coordination, resource allocation, etc.
        
        # Update progress
        task.progress = min(task.progress + 10, 100)
        
        if task.progress >= 100:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
        
        self.save_data()
    
    def process_collective_decision(self, decision_data: Dict[str, Any]):
        """Process a collective decision in the background"""
        decision_id = decision_data["decision_id"]
        participating_agents = decision_data["participating_agents"]
        
        logger.info(f"Processing collective decision: {decision_id}")
        
        # Decision processing logic would go here
        # This could involve notification, deadline management, etc.
    
    def process_knowledge_update(self, knowledge_data: Dict[str, Any]):
        """Process a knowledge update in the background"""
        knowledge_id = knowledge_data["id"]
        logger.info(f"Processing knowledge update: {knowledge_id}")
        
        # Knowledge processing logic would go here
        # This could involve indexing, categorization, etc.
    
    def stop(self):
        """Stop the collaborative system"""
        self.running = False
        self.executor.shutdown(wait=True)
        self.save_data()
        logger.info("Collaborative agent system stopped")

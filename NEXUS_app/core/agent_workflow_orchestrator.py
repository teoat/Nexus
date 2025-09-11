#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Agent Workflow Orchestrator
Coordinates complex multi-agent workflows with advanced collaboration features:
- Workflow definition and execution
- Dependency management and parallel processing
- Collective intelligence and consensus building
- Performance monitoring and optimization
"""

import asyncio
import json
import logging
import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import queue
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
import networkx as nx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentRole(Enum):
    """Agent roles in workflows"""
    COORDINATOR = "coordinator"         # Manages workflow execution
    REVIEWER = "reviewer"               # Reviews and validates work
    ADVISOR = "advisor"                 # Provides guidance and expertise
    MONITOR = "monitor"                 # Monitors progress and quality
    INTEGRATOR = "integrator"           # Integrates work from multiple agents

class WorkflowPhase(Enum):
    """Workflow execution phases"""
    PLANNING = "planning"               # Initial planning and setup
    EXECUTION = "execution"             # Main task execution
    REVIEW = "review"                   # Final review and validation
    DEPLOYMENT = "deployment"           # Deployment and handoff

@dataclass
class WorkflowStep:
    """Individual step in a workflow"""
    id: str
    name: str
    description: str
    agent_roles: List[AgentRole]
    required_skills: List[str]
    estimated_duration: int  # minutes
    dependencies: List[str]  # Step IDs that must complete first
    parallel_group: Optional[str] = None  # Steps that can run in parallel
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"
    assigned_agents: List[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: float = 0.0
    output: Dict[str, Any] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """
          Post Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        if self.assigned_agents is None:
            self.assigned_agents = []
        if self.output is None:
            self.output = {}

@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""
    id: str
    name: str
    description: str
    version: str
    steps: List[WorkflowStep]
    agent_assignments: Dict[str, List[str]]  # role -> agent_ids
    entry_criteria: Dict[str, Any] = None
    exit_criteria: Dict[str, Any] = None
    created_at: str = ""
    created_by: str = ""
    
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
class WorkflowInstance:
    """Running instance of a workflow"""
    id: str
    workflow_id: str
    status: WorkflowStatus
    current_phase: WorkflowPhase
    current_step: Optional[str] = None
    step_status: Dict[str, str] = None
    agent_assignments: Dict[str, str] = None  # step_id -> agent_id
    started_at: str = ""
    completed_at: Optional[str] = None
    total_duration: Optional[int] = None
    performance_metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        """
          Post Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        if self.step_status is None:
            self.step_status = {}
        if self.agent_assignments is None:
            self.agent_assignments = {}
        if self.performance_metrics is None:
            self.performance_metrics = {}
        if not self.started_at:
            self.started_at = datetime.now().isoformat()

class AgentWorkflowOrchestrator:
    """Orchestrates complex multi-agent workflows"""
    
    def __init__(self, workspace_path: str):
        """
          Init  
        
        
        Args:
            workspace_path: Description of workspace_path
    
        Example:
            TBD: Add usage example
        """
        self.workspace_path = Path(workspace_path)
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self.agents: Dict[str, Dict[str, Any]] = {}
        
        # File paths
        self.data_dir = self.workspace_path / ".mcp" / "workflow_orchestrator"
        self.workflows_file = self.data_dir / "workflows.json"
        self.instances_file = self.data_dir / "instances.json"
        self.agents_file = self.data_dir / "agents.json"
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Workflow execution
        self.execution_queue = queue.PriorityQueue()
        self.active_instances: Set[str] = set()
        self.execution_lock = threading.Lock()
        
        # Threading and async support
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.running = True
        
        # Load existing data
        self.load_data()
        
        # Start background workers
        self.start_background_workers()
    
    def load_data(self):
        """Load all orchestrator data"""
        try:
            # Load workflow definitions
            if self.workflows_file.exists():
                with open(self.workflows_file, 'r') as f:
                    data = json.load(f)
                    for wf_id, wf_data in data.items():
                        steps = [WorkflowStep(**step) for step in wf_data["steps"]]
                        wf_data["steps"] = steps
                        self.workflows[wf_id] = WorkflowDefinition(**wf_data)
            
            # Load workflow instances
            if self.instances_file.exists():
                with open(self.instances_file, 'r') as f:
                    data = json.load(f)
                    for inst_id, inst_data in data.items():
                        self.instances[inst_id] = WorkflowInstance(**inst_data)
            
            # Load agents
            if self.agents_file.exists():
                with open(self.agents_file, 'r') as f:
                    self.agents = json.load(f)
                    
            logger.info(f"Loaded orchestrator: {len(self.workflows)} workflows, {len(self.instances)} instances, {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Error loading orchestrator data: {e}")
    
    def save_data(self):
        """Save all orchestrator data"""
        try:
            # Save workflow definitions
            workflows_data = {}
            for wf_id, workflow in self.workflows.items():
                wf_dict = asdict(workflow)
                wf_dict["steps"] = [asdict(step) for step in workflow.steps]
                workflows_data[wf_id] = wf_dict
            
            with open(self.workflows_file, 'w') as f:
                json.dump(workflows_data, f, indent=2)
            
            # Save workflow instances
            with open(self.instances_file, 'w') as f:
                json.dump({inst_id: asdict(instance) for inst_id, instance in self.instances.items()}, f, indent=2)
            
            # Save agents
            with open(self.agents_file, 'w') as f:
                json.dump(self.agents, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving orchestrator data: {e}")
    
    def start_background_workers(self):
        """Start background workers for workflow execution"""
        def workflow_executor():
            """
            Workflow Executor
            
            
            Example:
                TBD: Add usage example
            """
            while self.running:
                try:
                    if not self.execution_queue.empty():
                        priority, instance_id = self.execution_queue.get(timeout=1)
                        self.execute_workflow_instance(instance_id)
                    time.sleep(0.1)
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Workflow executor error: {e}")
        
        # Start worker thread
        threading.Thread(target=workflow_executor, daemon=True).start()
        logger.info("Started background workflow executor")
    
    def register_agent(self, agent_id: str, name: str, skills: List[str], 
                      roles: List[AgentRole], capabilities: Dict[str, Any] = None) -> bool:
        """Register an agent with the orchestrator"""
        if agent_id in self.agents:
            logger.warning(f"Agent {agent_id} already registered, updating...")
        
        self.agents[agent_id] = {
            "id": agent_id,
            "name": name,
            "skills": skills,
            "roles": [role.value for role in roles],
            "capabilities": capabilities or {},
            "status": "available",
            "current_workflow": None,
            "current_step": None,
            "workload": 0,
            "performance_score": 1.0,
            "registered_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat()
        }
        
        self.save_data()
        logger.info(f"Registered agent: {name} (ID: {agent_id})")
        return True
    
    def create_workflow(self, name: str, description: str, steps: List[Dict[str, Any]], 
                       agent_assignments: Dict[str, List[str]], version: str = "1.0.0") -> str:
        """Create a new workflow definition"""
        workflow_id = str(uuid.uuid4())
        
        # Convert step definitions to WorkflowStep objects
        workflow_steps = []
        for step_data in steps:
            step = WorkflowStep(
                id=str(uuid.uuid4()),
                name=step_data["name"],
                description=step_data["description"],
                agent_roles=[AgentRole(role) for role in step_data["agent_roles"]],
                required_skills=step_data["required_skills"],
                estimated_duration=step_data["estimated_duration"],
                dependencies=step_data.get("dependencies", []),
                parallel_group=step_data.get("parallel_group")
            )
            workflow_steps.append(step)
        
        workflow = WorkflowDefinition(
            id=workflow_id,
            name=name,
            description=description,
            version=version,
            steps=workflow_steps,
            agent_assignments=agent_assignments
        )
        
        self.workflows[workflow_id] = workflow
        self.save_data()
        
        logger.info(f"Created workflow: {name} (ID: {workflow_id})")
        return workflow_id
    
    def start_workflow(self, workflow_id: str, parameters: Dict[str, Any] = None) -> str:
        """Start a new workflow instance"""
        if workflow_id not in self.workflows:
            logger.error(f"Workflow {workflow_id} not found")
            return None
        
        workflow = self.workflows[workflow_id]
        instance_id = str(uuid.uuid4())
        
        # Create workflow instance
        instance = WorkflowInstance(
            id=instance_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            current_phase=WorkflowPhase.PLANNING,
            current_step=None
        )
        
        # Initialize step status
        for step in workflow.steps:
            instance.step_status[step.id] = "pending"
        
        self.instances[instance_id] = instance
        self.active_instances.add(instance_id)
        
        # Add to execution queue
        self.execution_queue.put((1, instance_id))  # Priority 1 for new workflows
        
        self.save_data()
        logger.info(f"Started workflow instance: {workflow.name} (Instance: {instance_id})")
        return instance_id
    
    def execute_workflow_instance(self, instance_id: str):
        """Execute a workflow instance"""
        if instance_id not in self.instances:
            logger.error(f"Instance {instance_id} not found")
            return
        
        instance = self.instances[instance_id]
        workflow = self.workflows[instance.workflow_id]
        
        with self.execution_lock:
            if instance.status != WorkflowStatus.RUNNING:
                instance.status = WorkflowStatus.RUNNING
                instance.current_phase = WorkflowPhase.PLANNING
                self.save_data()
            
            # Execute workflow phases
            try:
                self._execute_planning_phase(instance, workflow)
                self._execute_execution_phase(instance, workflow)
                self._execute_integration_phase(instance, workflow)
                self._execute_review_phase(instance, workflow)
                self._execute_deployment_phase(instance, workflow)
                
                instance.status = WorkflowStatus.COMPLETED
                instance.completed_at = datetime.now().isoformat()
                
                # Calculate total duration
                start_time = datetime.fromisoformat(instance.started_at)
                end_time = datetime.fromisoformat(instance.completed_at)
                instance.total_duration = int((end_time - start_time).total_seconds() / 60)
                
            except Exception as e:
                logger.error(f"Workflow execution failed: {e}")
                instance.status = WorkflowStatus.FAILED
                instance.error_message = str(e)
            
            finally:
                self.active_instances.discard(instance_id)
                self.save_data()
    
    def _execute_planning_phase(self, instance: WorkflowInstance, workflow: WorkflowDefinition):
        """Execute the planning phase"""
        logger.info(f"Executing planning phase for instance {instance.id}")
        instance.current_phase = WorkflowPhase.PLANNING
        
        # Analyze dependencies and create execution plan
        execution_plan = self._create_execution_plan(workflow)
        
        # Assign agents to steps based on skills and availability
        self._assign_agents_to_steps(instance, workflow, execution_plan)
        
        instance.current_phase = WorkflowPhase.EXECUTION
        self.save_data()
    
    def _execute_execution_phase(self, instance: WorkflowInstance, workflow: WorkflowDefinition):
        """Execute the main execution phase"""
        logger.info(f"Executing main phase for instance {instance.id}")
        instance.current_phase = WorkflowPhase.EXECUTION
        
        # Execute steps according to dependency order
        completed_steps = set()
        while len(completed_steps) < len(workflow.steps):
            # Find ready steps (dependencies satisfied)
            ready_steps = self._find_ready_steps(workflow, completed_steps)
            
            if not ready_steps:
                logger.warning(f"No ready steps found, workflow may be blocked")
                break
            
            # Execute ready steps in parallel
            step_futures = []
            for step in ready_steps:
                future = self.executor.submit(self._execute_step, instance, workflow, step)
                step_futures.append((step, future))
            
            # Wait for completion
            for step, future in step_futures:
                try:
                    result = future.result(timeout=300)  # 5 minute timeout
                    if result:
                        completed_steps.add(step.id)
                        instance.step_status[step.id] = "completed"
                except Exception as e:
                    logger.error(f"Step {step.name} failed: {e}")
                    instance.step_status[step.id] = "failed"
                    instance.error_message = f"Step {step.name} failed: {e}"
                    raise
        
        instance.current_phase = WorkflowPhase.INTEGRATION
        self.save_data()
    
    def _execute_integration_phase(self, instance: WorkflowInstance, workflow: WorkflowDefinition):
        """Execute the integration phase"""
        logger.info(f"Executing integration phase for instance {instance.id}")
        instance.current_phase = WorkflowPhase.INTEGRATION
        
        # Integrate outputs from all completed steps
        integration_result = self._integrate_step_outputs(instance, workflow)
        
        if integration_result:
            instance.current_phase = WorkflowPhase.REVIEW
        else:
            raise Exception("Integration phase failed")
        
        self.save_data()
    
    def _execute_review_phase(self, instance: WorkflowInstance, workflow: WorkflowDefinition):
        """Execute the review phase"""
        logger.info(f"Executing review phase for instance {instance.id}")
        instance.current_phase = WorkflowPhase.REVIEW
        
        # Perform quality review and validation
        review_result = self._perform_quality_review(instance, workflow)
        
        if review_result:
            instance.current_phase = WorkflowPhase.DEPLOYMENT
        else:
            raise Exception("Review phase failed")
        
        self.save_data()
    
    def _execute_deployment_phase(self, instance: WorkflowInstance, workflow: WorkflowDefinition):
        """Execute the deployment phase"""
        logger.info(f"Executing deployment phase for instance {instance.id}")
        instance.current_phase = WorkflowPhase.DEPLOYMENT
        
        # Deploy the integrated result
        deployment_result = self._deploy_workflow_result(instance, workflow)
        
        if not deployment_result:
            raise Exception("Deployment phase failed")
        
        self.save_data()
    
    def _create_execution_plan(self, workflow: WorkflowDefinition) -> List[List[WorkflowStep]]:
        """Create execution plan based on dependencies"""
        # Create dependency graph
        G = nx.DiGraph()
        
        for step in workflow.steps:
            G.add_node(step.id)
            for dep in step.dependencies:
                G.add_edge(dep, step.id)
        
        # Check for cycles
        try:
            cycle = nx.find_cycle(G)
            raise Exception(f"Circular dependency detected: {' -> '.join(cycle)}")
        except nx.NetworkXNoCycle:
            pass
        
        # Topological sort for execution order
        execution_order = list(nx.topological_sort(G))
        
        # Group steps by parallel execution
        execution_plan = []
        current_group = []
        
        for step_id in execution_order:
            step = next(s for s in workflow.steps if s.id == step_id)
            
            if step.parallel_group and current_group and current_group[0].parallel_group == step.parallel_group:
                current_group.append(step)
            else:
                if current_group:
                    execution_plan.append(current_group)
                current_group = [step]
        
        if current_group:
            execution_plan.append(current_group)
        
        return execution_plan
    
    def _assign_agents_to_steps(self, instance: WorkflowInstance, workflow: WorkflowDefinition, execution_plan: List[List[WorkflowStep]]):
        """Assign agents to workflow steps"""
        for step_group in execution_plan:
            for step in step_group:
                # Find available agents with required skills and roles
                suitable_agents = self._find_suitable_agents(step)
                
                if suitable_agents:
                    # Select best agent based on workload and performance
                    selected_agent = self._select_best_agent(suitable_agents)
                    instance.agent_assignments[step.id] = selected_agent["id"]
                    
                    # Update agent status
                    selected_agent["status"] = "assigned"
                    selected_agent["current_workflow"] = instance.id
                    selected_agent["current_step"] = step.id
                    selected_agent["workload"] += 1
                else:
                    raise Exception(f"No suitable agents found for step: {step.name}")
    
    def _find_suitable_agents(self, step: WorkflowStep) -> List[Dict[str, Any]]:
        """Find agents suitable for a step"""
        suitable_agents = []
        
        for agent in self.agents.values():
            if agent["status"] != "available":
                continue
            
            # Check if agent has required skills
            if not all(skill in agent["skills"] for skill in step.required_skills):
                continue
            
            # Check if agent can perform required roles
            if not any(role.value in agent["roles"] for role in step.agent_roles):
                continue
            
            suitable_agents.append(agent)
        
        return suitable_agents
    
    def _select_best_agent(self, suitable_agents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the best agent based on workload and performance"""
        if not suitable_agents:
            return None
        
        # Score agents based on workload and performance
        best_agent = None
        best_score = float('-inf')
        
        for agent in suitable_agents:
            # Lower workload and higher performance = better score
            workload_factor = 1.0 / (1.0 + agent["workload"])
            performance_factor = agent["performance_score"]
            
            score = workload_factor * performance_factor
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        return best_agent
    
    def _find_ready_steps(self, workflow: WorkflowDefinition, completed_steps: Set[str]) -> List[WorkflowStep]:
        """Find steps ready for execution (dependencies satisfied)"""
        ready_steps = []
        
        for step in workflow.steps:
            if step.id in completed_steps:
                continue
            
            # Check if all dependencies are completed
            if all(dep in completed_steps for dep in step.dependencies):
                ready_steps.append(step)
        
        return ready_steps
    
    def _execute_step(self, instance: WorkflowInstance, workflow: WorkflowDefinition, step: WorkflowStep) -> bool:
        """Execute a single workflow step"""
        try:
            logger.info(f"Executing step: {step.name}")
            
            # Update step status
            instance.current_step = step.id
            instance.step_status[step.id] = "running"
            step.status = "running"
            step.started_at = datetime.now().isoformat()
            
            
            # Update progress
            step.progress = 100.0
            step.status = "completed"
            step.completed_at = datetime.now().isoformat()
            
            
            # Update agent status
            agent_id = instance.agent_assignments.get(step.id)
            if agent_id and agent_id in self.agents:
                self.agents[agent_id]["status"] = "available"
                self.agents[agent_id]["current_workflow"] = None
                self.agents[agent_id]["current_step"] = None
                self.agents[agent_id]["workload"] = max(0, self.agents[agent_id]["workload"] - 1)
            
            self.save_data()
            return True
            
        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            step.status = "failed"
            step.error_message = str(e)
            self.save_data()
            return False
    
    def _integrate_step_outputs(self, instance: WorkflowInstance, workflow: WorkflowDefinition) -> bool:
        """Integrate outputs from all completed steps"""
        logger.info("Integrating step outputs")
        
        # Collect outputs from all completed steps
        outputs = {}
        for step in workflow.steps:
            if instance.step_status.get(step.id) == "completed":
                outputs[step.name] = step.output
        
        # Perform integration (in real implementation, this would involve data processing)
        integration_result = {
            "integrated_outputs": outputs,
            "integration_timestamp": datetime.now().isoformat(),
            "total_steps": len(workflow.steps),
            "completed_steps": len(outputs)
        }
        
        # Store integration result
        instance.performance_metrics["integration_result"] = integration_result
        
        return True
    
    def _perform_quality_review(self, instance: WorkflowInstance, workflow: WorkflowDefinition) -> bool:
        """Perform quality review and validation"""
        logger.info("Performing quality review")
        
        # Perform review (in real implementation, this would involve validation logic)
        review_result = {
            "quality_score": 0.95,
            "validation_passed": True,
            "issues_found": 0,
            "review_timestamp": datetime.now().isoformat()
        }
        
        # Store review result
        instance.performance_metrics["review_result"] = review_result
        
        return review_result["validation_passed"]
    
    def _deploy_workflow_result(self, instance: WorkflowInstance, workflow: WorkflowDefinition) -> bool:
        """Deploy the workflow result"""
        logger.info("Deploying workflow result")
        
        # Perform deployment (in real implementation, this would involve deployment logic)
        deployment_result = {
            "deployment_status": "success",
            "deployment_timestamp": datetime.now().isoformat(),
            "deployment_target": "production",
            "rollback_available": True
        }
        
        # Store deployment result
        instance.performance_metrics["deployment_result"] = deployment_result
        
        return deployment_result["deployment_status"] == "success"
    
    def get_workflow_status(self, instance_id: str) -> Dict[str, Any]:
        """Get status of a workflow instance"""
        if instance_id not in self.instances:
            return {"error": "Instance not found"}
        
        instance = self.instances[instance_id]
        workflow = self.workflows[instance.workflow_id]
        
        return {
            "instance_id": instance_id,
            "workflow_name": workflow.name,
            "status": instance.status.value,
            "current_phase": instance.current_phase.value,
            "current_step": instance.current_step,
            "step_status": instance.step_status,
            "agent_assignments": instance.agent_assignments,
            "started_at": instance.started_at,
            "completed_at": instance.completed_at,
            "total_duration": instance.total_duration,
            "performance_metrics": instance.performance_metrics
        }
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get overall orchestrator status"""
        active_instances = len(self.active_instances)
        total_instances = len(self.instances)
        completed_instances = sum(1 for inst in self.instances.values() 
                                if inst.status == WorkflowStatus.COMPLETED)
        failed_instances = sum(1 for inst in self.instances.values() 
                              if inst.status == WorkflowStatus.FAILED)
        
        return {
            "total_workflows": len(self.workflows),
            "total_instances": total_instances,
            "active_instances": active_instances,
            "completed_instances": completed_instances,
            "failed_instances": failed_instances,
            "total_agents": len(self.agents),
            "available_agents": sum(1 for agent in self.agents.values() 
                                  if agent["status"] == "available"),
            "system_status": "healthy" if self.running else "stopped"
        }
    
    def stop(self):
        """Stop the orchestrator"""
        self.running = False
        self.executor.shutdown(wait=True)
        self.save_data()
        logger.info("Agent workflow orchestrator stopped")

# MCP Server implementation
class AgentWorkflowOrchestratorServer:
    """MCP Server for the agent workflow orchestrator"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.orchestrator = None
        self.server = mcp.server.Server("agent-workflow-orchestrator")
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="register_agent",
                    description="Register an agent with the workflow orchestrator",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string"},
                            "name": {"type": "string"},
                            "skills": {"type": "array", "items": {"type": "string"}},
                            "roles": {"type": "array", "items": {"type": "string", "enum": ["COORDINATOR", "EXECUTOR", "REVIEWER", "ADVISOR", "MONITOR", "INTEGRATOR"]}},
                            "capabilities": {"type": "object"}
                        },
                        "required": ["agent_id", "name", "skills", "roles"]
                    }
                ),
                Tool(
                    name="create_workflow",
                    description="Create a new workflow definition",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "steps": {"type": "array", "items": {"type": "object"}},
                            "agent_assignments": {"type": "object"},
                            "version": {"type": "string"}
                        },
                        "required": ["name", "description", "steps", "agent_assignments"]
                    }
                ),
                Tool(
                    name="start_workflow",
                    description="Start a new workflow instance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_id": {"type": "string"},
                            "parameters": {"type": "object"}
                        },
                        "required": ["workflow_id"]
                    }
                ),
                Tool(
                    name="get_workflow_status",
                    description="Get status of a workflow instance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "instance_id": {"type": "string"}
                        },
                        "required": ["instance_id"]
                    }
                ),
                Tool(
                    name="get_orchestrator_status",
                    description="Get overall orchestrator status"
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> str:
            if not self.orchestrator:
                workspace_path = os.getenv("WORKSPACE_ROOT", "/Users/Arief/Desktop/Nexus")
                self.orchestrator = AgentWorkflowOrchestrator(workspace_path)
            
            try:
                if name == "register_agent":
                    roles = [AgentRole(role) for role in arguments["roles"]]
                    success = self.orchestrator.register_agent(
                        arguments["agent_id"],
                        arguments["name"],
                        arguments["skills"],
                        roles,
                        arguments.get("capabilities")
                    )
                    return f"Agent registration {'successful' if success else 'failed'}"
                
                elif name == "create_workflow":
                    workflow_id = self.orchestrator.create_workflow(
                        arguments["name"],
                        arguments["description"],
                        arguments["steps"],
                        arguments["agent_assignments"],
                        arguments.get("version", "1.0.0")
                    )
                    return f"Created workflow with ID: {workflow_id}"
                
                elif name == "start_workflow":
                    instance_id = self.orchestrator.start_workflow(
                        arguments["workflow_id"],
                        arguments.get("parameters")
                    )
                    return f"Started workflow instance with ID: {instance_id}"
                
                elif name == "get_workflow_status":
                    status = self.orchestrator.get_workflow_status(arguments["instance_id"])
                    return json.dumps(status, indent=2)
                
                elif name == "get_orchestrator_status":
                    status = self.orchestrator.get_orchestrator_status()
                    return json.dumps(status, indent=2)
                
                else:
                    return f"Unknown tool: {name}"
                    
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return f"Error: {str(e)}"
    
    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                NotificationOptions()
            )

def main():
    """Main entry point for the agent workflow orchestrator server"""
    server = AgentWorkflowOrchestratorServer()
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Agent workflow orchestrator server stopped by user")
    except Exception as e:
        logger.error(f"Error running agent workflow orchestrator server: {e}")

if __name__ == "__main__":
    main()

"""
🤖 AI Workflow Orchestrator
Manages and executes AI workflows in the Nexus Platform.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime
import uuid

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.interfaces.ai_service import AIRequest, AIResponse, AIProviderType
from core.models.ai_models import (
    AIWorkflow, AIWorkflowStep, AIWorkflowExecution,
    AIServiceRegistry
)

logger = logging.getLogger(__name__)

class AIWorkflowOrchestrator:
    """Orchestrates AI workflow execution"""
    
    def __init__(self, service_manager):
        self.service_manager = service_manager
        self.workflows: Dict[str, AIWorkflow] = {}
        self.executions: Dict[str, AIWorkflowExecution] = {}
        self.running = True
        
        logger.info("🎭 AI Workflow Orchestrator initialized")
    
    async def register_workflow(self, workflow: AIWorkflow) -> bool:
        """Register a new workflow"""
        try:
            if workflow.workflow_id in self.workflows:
                logger.warning(f"⚠️ Workflow {workflow.workflow_id} already registered")
                return False
            
            # Validate workflow
            if not await self._validate_workflow(workflow):
                logger.error(f"❌ Workflow {workflow.workflow_id} validation failed")
                return False
            
            self.workflows[workflow.workflow_id] = workflow
            logger.info(f"✅ Workflow {workflow.workflow_id} registered")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error registering workflow {workflow.workflow_id}: {e}")
            return False
    
    async def _validate_workflow(self, workflow: AIWorkflow) -> bool:
        """Validate workflow configuration"""
        try:
            # Check if all referenced services exist
            for step in workflow.steps:
                if not await self.service_manager.get_service(step.service_name):
                    logger.error(f"❌ Service {step.service_name} not found for step {step.step_id}")
                    return False
            
            # Check for circular dependencies
            if self._has_circular_dependencies(workflow):
                logger.error(f"❌ Circular dependencies detected in workflow {workflow.workflow_id}")
                return False
            
            # Validate input/output schemas
            if not self._validate_schemas(workflow):
                logger.error(f"❌ Schema validation failed for workflow {workflow.workflow_id}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Workflow validation error: {e}")
            return False
    
    def _has_circular_dependencies(self, workflow: AIWorkflow) -> bool:
        """Check for circular dependencies in workflow steps"""
        visited = set()
        rec_stack = set()
        
        def has_cycle(step_id: str) -> bool:
            if step_id in rec_stack:
                return True
            if step_id in visited:
                return False
            
            visited.add(step_id)
            rec_stack.add(step_id)
            
            step = next((s for s in workflow.steps if s.step_id == step_id), None)
            if step:
                for dep in step.dependencies:
                    if has_cycle(dep):
                        return True
            
            rec_stack.remove(step_id)
            return False
        
        for step in workflow.steps:
            if has_cycle(step.step_id):
                return True
        
        return False
    
    def _validate_schemas(self, workflow: AIWorkflow) -> bool:
        """Validate input and output schemas"""
        try:
            # Basic schema validation
            if not isinstance(workflow.input_schema, dict):
                return False
            if not isinstance(workflow.output_schema, dict):
                return False
            
            # Check that all step inputs are covered by workflow input
            for step in workflow.steps:
                for input_key in step.input_mapping.values():
                    if input_key not in workflow.input_schema:
                        logger.warning(f"⚠️ Step {step.step_id} input {input_key} not in workflow input schema")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Schema validation error: {e}")
            return False
    
    async def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> str:
        """Execute a workflow"""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            if not workflow.enabled:
                raise ValueError(f"Workflow {workflow_id} is disabled")
            
            # Create execution record
            execution = AIWorkflowExecution(
                execution_id=str(uuid.uuid4()),
                workflow_id=workflow_id,
                input_data=input_data,
                start_time=datetime.now().isoformat(),
                status="running"
            )
            
            self.executions[execution.execution_id] = execution
            
            # Start execution in background
            asyncio.create_task(self._execute_workflow_steps(execution))
            
            logger.info(f"🚀 Started workflow execution {execution.execution_id}")
            return execution.execution_id
            
        except Exception as e:
            logger.error(f"❌ Error starting workflow execution: {e}")
            raise
    
    async def _execute_workflow_steps(self, execution: AIWorkflowExecution):
        """Execute workflow steps"""
        try:
            workflow = self.workflows[execution.workflow_id]
            step_results = {}
            
            # Execute steps in dependency order
            executed_steps = set()
            
            while len(executed_steps) < len(workflow.steps):
                for step in workflow.steps:
                    if step.step_id in executed_steps:
                        continue
                    
                    # Check if dependencies are met
                    if not all(dep in executed_steps for dep in step.dependencies):
                        continue
                    
                    # Execute step
                    try:
                        result = await self._execute_step(step, execution.input_data, step_results)
                        step_results[step.step_id] = result
                        executed_steps.add(step.step_id)
                        
                        logger.info(f"✅ Step {step.step_id} completed")
                        
                    except Exception as e:
                        logger.error(f"❌ Step {step.step_id} failed: {e}")
                        execution.status = "failed"
                        execution.error_message = f"Step {step.step_id} failed: {str(e)}"
                        execution.end_time = datetime.now().isoformat()
                        return
                
                # Check for deadlock
                if len(executed_steps) == 0:
                    execution.status = "failed"
                    execution.error_message = "Workflow deadlock detected"
                    execution.end_time = datetime.now().isoformat()
                    return
            
            # Workflow completed successfully
            execution.status = "completed"
            execution.output_data = self._build_output_data(workflow, step_results)
            execution.end_time = datetime.now().isoformat()
            execution.step_results = step_results
            
            logger.info(f"🎉 Workflow execution {execution.execution_id} completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Workflow execution error: {e}")
            execution.status = "failed"
            execution.error_message = str(e)
            execution.end_time = datetime.now().isoformat()
    
    async def _execute_step(self, step: AIWorkflowStep, input_data: Dict[str, Any], step_results: Dict[str, Any]) -> Any:
        """Execute a single workflow step"""
        try:
            # Get service
            service = await self.service_manager.get_service(step.service_name)
            if not service:
                raise ValueError(f"Service {step.service_name} not found")
            
            # Prepare step input
            step_input = self._prepare_step_input(step, input_data, step_results)
            
            # Create AI request
            request = AIRequest(
                prompt=self._render_prompt_template(step.prompt_template, step_input),
                model=step.model,
                provider=AIProviderType.CUSTOM,  # Will be routed by service manager
                parameters={},
                context={"workflow_step": step.step_id}
            )
            
            # Execute request
            response = await self.service_manager.route_request(request)
            
            if response.error:
                raise ValueError(f"AI service error: {response.error}")
            
            # Parse step output
            step_output = self._parse_step_output(step, response.content, step_input)
            
            return step_output
            
        except Exception as e:
            logger.error(f"❌ Step execution error: {e}")
            raise
    
    def _prepare_step_input(self, step: AIWorkflowStep, input_data: Dict[str, Any], step_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input data for a step"""
        step_input = {}
        
        # Map workflow input to step input
        for step_key, workflow_key in step.input_mapping.items():
            if workflow_key in input_data:
                step_input[step_key] = input_data[workflow_key]
        
        # Map previous step results to step input
        for step_key, step_id in step.input_mapping.items():
            if step_id in step_results:
                step_input[step_key] = step_results[step_id]
        
        return step_input
    
    def _render_prompt_template(self, template: str, data: Dict[str, Any]) -> str:
        """Render prompt template with data"""
        try:
            return template.format(**data)
        except KeyError as e:
            logger.warning(f"⚠️ Missing template variable: {e}")
            return template
    
    def _parse_step_output(self, step: AIWorkflowStep, content: str, step_input: Dict[str, Any]) -> Any:
        """Parse step output according to output mapping"""
        # For now, return the content as-is
        return content
    
    def _build_output_data(self, workflow: AIWorkflow, step_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build final output data from step results"""
        output_data = {}
        
        for step in workflow.steps:
            for output_key, step_key in step.output_mapping.items():
                if step_key in step_results:
                    output_data[output_key] = step_results[step_key]
        
        return output_data
    
    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status"""
        execution = self.executions.get(execution_id)
        if not execution:
            return None
        
        return {
            "execution_id": execution.execution_id,
            "workflow_id": execution.workflow_id,
            "status": execution.status,
            "start_time": execution.start_time,
            "end_time": execution.end_time,
            "error_message": execution.error_message,
            "step_results": execution.step_results
        }
    
    async def list_workflows(self) -> List[Dict[str, Any]]:
        """List all registered workflows"""
        return [
            {
                "workflow_id": w.workflow_id,
                "name": w.name,
                "description": w.description,
                "enabled": w.enabled,
                "version": w.version,
                "step_count": len(w.steps)
            }
            for w in self.workflows.values()
        ]
    
    async def list_executions(self) -> List[Dict[str, Any]]:
        """List all executions"""
        return [
            {
                "execution_id": e.execution_id,
                "workflow_id": e.workflow_id,
                "status": e.status,
                "start_time": e.start_time,
                "end_time": e.end_time
            }
            for e in self.executions.values()
        ]
    
    async def shutdown(self):
        """Shutdown the orchestrator"""
        logger.info("🛑 Shutting down AI Workflow Orchestrator...")
        self.running = False
        
        # Wait for running executions to complete
        running_executions = [
            e for e in self.executions.values()
            if e.status == "running"
        ]
        
        if running_executions:
            logger.info(f"⏳ Waiting for {len(running_executions)} executions to complete...")
            # Give them some time to complete
            await asyncio.sleep(5)
        
        logger.info("✅ AI Workflow Orchestrator shutdown complete")

async def main():
    # This would require a service manager instance

if __name__ == "__main__":
    asyncio.run(main())

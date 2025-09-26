#!/usr/bin/env python
"""
Multidimensional Master Executor for NexusX
------------------------------------------
Implementation of the automation system that processes unimplemented todo items.

This extends the provided master executor to:
1. Scan for pending todos in the project
2. Process unimplemented tasks automatically
3. Update the todo list with progress and completion status
"""

import asyncio
import concurrent.futures
import json
import logging
import math
import os
import queue
import random
import string
import sys
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple
import re
import pathlib
import subprocess

try:
    import psutil
except ImportError:
    psutil = None

# ------------------------
# Logging / Utilities
# ------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "nexus_master_executor.log")),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("NexusMasterExecutor")


def now_str():
    return datetime.utcnow().isoformat() + "Z"


# ------------------------
# Task / Parser
# ------------------------
@dataclass
class Task:
    id: str
    raw: str
    command: str
    params: Dict[str, Any] = field(default_factory=dict)
    subtasks: List['Task'] = field(default_factory=list)
    status: str = "pending"  # pending, running, success, failed
    result: Any = None
    created_at: str = field(default_factory=now_str)
    started_at: Optional[str] = None
    finished_at: Optional[str] = None


class TaskParser:
    """
    TaskParser understands simplified master_todo 'codes' and produces Task objects.

    Supported forms (examples):
      - simple string: "task:fetch_report?src=bankA&days=7"
      - chained subtasks using '->': "task:A -> task:B -> task:C"
      - JSON payload: '{"task":"process", "params": {"file":"a.csv"}}'

    The parser is intentionally conservative: if it cannot parse JSON it treats input as a structured code.
    Extend this module to support richer DSLs, natural language parsing, or LLM-driven decomposition.
    """

    @staticmethod
    def gen_id(prefix: str = "T") -> str:
        return prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    @classmethod
    def parse(cls, raw: str) -> Task:
        raw = raw.strip()
        # Try JSON first
        if raw.startswith('{'):
            try:
                j = json.loads(raw)
                tid = j.get('id', cls.gen_id())
                cmd = j.get('task') or j.get('command') or j.get('action', 'noop')
                params = j.get('params', {})
                t = Task(id=tid, raw=raw, command=cmd, params=params)
                # optional nested tasks
                if 'subtasks' in j:
                    for s in j['subtasks']:
                        t.subtasks.append(cls.parse(json.dumps(s) if isinstance(s, dict) else s))
                return t
            except Exception:
                logger.debug("JSON parse failed, falling back to code parser")
        # Chained subtasks using '->'
        if '->' in raw:
            pieces = [p.strip() for p in raw.split('->') if p.strip()]
            root = None
            prev = None
            for p in pieces:
                cmd, params = cls._parse_code_piece(p)
                t = Task(id=cls.gen_id(), raw=p, command=cmd, params=params)
                if root is None:
                    root = t
                if prev is not None:
                    prev.subtasks.append(t)
                prev = t
            return root
        # Single code piece
        cmd, params = cls._parse_code_piece(raw)
        return Task(id=cls.gen_id(), raw=raw, command=cmd, params=params)

    @staticmethod
    def _parse_code_piece(piece: str) -> Tuple[str, Dict[str, Any]]:
        # format: "task:COMMAND?k=v&k2=v2"
        if ':' in piece:
            left, rest = piece.split(':', 1)
            if '?' in rest:
                cmd, q = rest.split('?', 1)
                params = TaskParser._parse_query(q)
                return cmd.strip(), params
            return rest.strip(), {}
        # fallback
        return piece, {}

    @staticmethod
    def _parse_query(q: str) -> Dict[str, Any]:
        params = {}
        for pair in q.split('&'):
            if '=' in pair:
                k, v = pair.split('=', 1)
                params[k.strip()] = TaskParser._coerce(v)
        return params

    @staticmethod
    def _coerce(value: str):
        # try to coerce ints, floats, bools
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except Exception:
            return value


# ------------------------
# Worker & Execution
# ------------------------
class Worker:
    """
    Basic worker that runs tasks. Uses asyncio to allow cooperative multitasking.
    Each Worker has: id, layer, primary_skills (set), secondary_skills (set), busy flag.
    """

    def __init__(self, wid: str, layer: str = 'default', primary_skills: Optional[List[str]] = None,
                 secondary_skills: Optional[List[str]] = None):
        self.id = wid
        self.layer = layer  # 'default' | 'backup' | 'swarm'
        self.primary_skills = set(primary_skills or [])
        self.secondary_skills = set(secondary_skills or [])
        self.busy = False
        self.current_task: Optional[Task] = None
        self.logger = logging.getLogger(f'Worker[{self.id}]')
        # health metrics
        self.tasks_completed = 0
        self.total_runtime = 0.0

    def can_handle(self, task: Task) -> int:
        """
        Return score: higher means more suitable. This allows soft skill matching.
        """
        # simple heuristic: match command keywords to skills
        cmd = task.command.lower()
        score = 0
        for s in self.primary_skills:
            if s.lower() in cmd:
                score += 10
        for s in self.secondary_skills:
            if s.lower() in cmd:
                score += 4
        # if task params request a specific skill
        need = task.params.get('require_skill')
        if need:
            if need in self.primary_skills:
                score += 20
            elif need in self.secondary_skills:
                score += 5
        return score

    async def execute(self, task: Task, ctx: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Execute a task. This is a placeholder for plugin integration; replace with real code.
        Execution simulates work using asyncio.sleep and returns success/failure + result.
        """
        self.busy = True
        self.current_task = task
        task.started_at = now_str()
        self.logger.info(f"Starting task {task.id} cmd={task.command}")
        t0 = time.time()
        
        # Modified to handle actual NexusX todo tasks
        if task.command.lower().startswith('nexus:'):
            # Extract real task name from command
            nexus_task = task.command.split(':', 1)[1] if ':' in task.command else task.command
            result = await self._handle_nexus_task(nexus_task, task.params)
            success = result.get('success', False)
        else:
            # Choose duration based on complexity
            base = float(task.params.get('duration', random.uniform(0.2, 1.5)))
            # Collaborative speedup if swarm
            if self.layer == 'swarm' and ctx.get('collaborators', 0) > 0:
                # Shorten time depending on collaborator count
                base = base / (1 + 0.5 * ctx.get('collaborators'))
            # Allow a deterministic failure mode if 'fail' param set
            if task.params.get('fail'):
                await asyncio.sleep(min(2.0, base))
                success = False
                result = {'error': 'simulated failure'}
            else:
                # Simulate I/O bound or CPU-bound work
                await asyncio.sleep(base)
                success = True
                result = {"output": f"Executed {task.command} by {self.id}", "duration": base}
        
        rt = time.time() - t0
        self.total_runtime += rt
        self.tasks_completed += 1
        self.busy = False
        task.finished_at = now_str()
        task.status = 'success' if success else 'failed'
        task.result = result
        self.logger.info(f"Finished task {task.id} in {rt:.2f}s")
        return success, result
        
    async def _handle_nexus_task(self, task_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle NexusX specific tasks
        """
        self.logger.info(f"Executing NexusX task: {task_name}")
        
        # Task implementations
        if task_name == 'update_todo_status':
            todo_id = params.get('todo_id')
            status = params.get('status', 'completed')
            if todo_id:
                # This is where we'd call code to update the todo status
                # For now, simulate the update
                success = await self._update_todo_status(todo_id, status)
                return {'success': success, 'todo_id': todo_id, 'status': status}
        
        elif task_name == 'setup_python_env':
            # Simulate setting up Python environment
            success = await self._setup_python_env()
            return {'success': success, 'env': 'nexus_env'}
            
        elif task_name == 'create_docker_service':
            service = params.get('service', '')
            if service:
                success = await self._create_docker_service(service)
                return {'success': success, 'service': service}
            
        elif task_name == 'implement_health_check':
            service = params.get('service', '')
            if service:
                success = await self._implement_health_check(service)
                return {'success': success, 'service': service}
                
        # Add more task implementations as needed
                
        # Default fallback
        return {'success': False, 'error': f'Unknown or unimplemented task: {task_name}'}

    async def _update_todo_status(self, todo_id: str, status: str) -> bool:
        """
        Update the status of a todo item in the project
        """
        try:
            # In a real implementation, this would update the todo in the project's todo system
            # For now, simulate success
            self.logger.info(f"Updated todo {todo_id} to {status}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update todo {todo_id}: {e}")
            return False
            
    async def _setup_python_env(self) -> bool:
        """
        Set up the Python environment for the project
        """
        try:
            # Simulate running the setup script
            self.logger.info("Setting up Python environment...")
            # In real implementation, this would execute the setup script
            await asyncio.sleep(2.0)  # Simulate work
            return True
        except Exception as e:
            self.logger.error(f"Failed to set up Python environment: {e}")
            return False
            
    async def _create_docker_service(self, service: str) -> bool:
        """
        Create a Docker service configuration
        """
        try:
            self.logger.info(f"Creating Docker service: {service}")
            # In real implementation, this would create the service files
            await asyncio.sleep(1.5)  # Simulate work
            return True
        except Exception as e:
            self.logger.error(f"Failed to create Docker service {service}: {e}")
            return False
            
    async def _implement_health_check(self, service: str) -> bool:
        """
        Implement health check for a service
        """
        try:
            self.logger.info(f"Implementing health check for {service}")
            # In real implementation, this would add health check code
            await asyncio.sleep(1.0)  # Simulate work
            return True
        except Exception as e:
            self.logger.error(f"Failed to implement health check for {service}: {e}")
            return False


# ------------------------
# WorkerPool & Scheduler
# ------------------------
class WorkerPool:
    """
    Maintains three layers of workers and a task queue. Provides best-worker selection logic
    and supports dynamic reassignment and collaborative runs.
    """

    def __init__(self):
        self.workers: Dict[str, Worker] = {}
        self.layers: Dict[str, List[str]] = {'default': [], 'backup': [], 'swarm': []}
        # Async queue for tasks
        self.task_q: asyncio.Queue = asyncio.Queue()
        # shutdown flag
        self.shutdown_flag = False
        # metrics
        self.metrics = defaultdict(int)
        # lock for worker modifications
        self._lock = threading.Lock()

    def add_worker(self, worker: Worker):
        with self._lock:
            self.workers[worker.id] = worker
            self.layers.setdefault(worker.layer, []).append(worker.id)
            logger.info(f"Added worker {worker.id} layer={worker.layer}")

    def remove_worker(self, wid: str):
        with self._lock:
            w = self.workers.pop(wid, None)
            if w and wid in self.layers.get(w.layer, []):
                self.layers[w.layer].remove(wid)
                logger.info(f"Removed worker {wid}")

    def get_candidates(self, task: Task) -> List[Worker]:
        # Rank workers by suitability score, prefer non-busy workers and lower layers first
        candidates = list(self.workers.values())
        scored = []
        for w in candidates:
            # skip busy workers, but allow swarm to collaborate (they will be involved differently)
            if w.busy:
                continue
            score = w.can_handle(task)
            # favor default and backup over swarm for single-worker tasks
            layer_bias = {'default': 3, 'backup': 2, 'swarm': 1}.get(w.layer, 1)
            scored.append((score * layer_bias, w))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [w for s, w in scored if s > 0]

    async def assign_task(self, task: Task, exec_ctx: Dict[str, Any]) -> Tuple[bool, Any]:
        # choose execution mode
        mode = exec_ctx.get('mode', 'auto')  # 'auto' | 'parallel' | 'sequential' | 'collaborative'
        # if task has subtasks and sequential flag, run sequentially
        if task.subtasks and exec_ctx.get('sequential', False):
            logger.debug(f"Sequential execution for {task.id}")
            return await self._run_sequential(task, exec_ctx)
        # if collaborative requested
        if mode == 'collaborative' or exec_ctx.get('collaborative'):
            return await self._run_collaborative(task, exec_ctx)
        # default: attempt to find best single worker
        candidates = self.get_candidates(task)
        if candidates:
            w = candidates[0]
            ok, res = await w.execute(task, exec_ctx)
            return ok, res
        # fallback: if no candidate, try swarm
        return await self._run_collaborative(task, exec_ctx)

    async def _run_sequential(self, task: Task, exec_ctx: Dict[str, Any]) -> Tuple[bool, Any]:
        all_results = []
        for st in task.subtasks:
            ok, res = await self.assign_task(st, exec_ctx)
            all_results.append({'id': st.id, 'ok': ok, 'res': res})
            if not ok and exec_ctx.get('stop_on_failure', True):
                return False, {'subtask_results': all_results}
        return True, {'subtask_results': all_results}

    async def _run_collaborative(self, task: Task, exec_ctx: Dict[str, Any]) -> Tuple[bool, Any]:
        # pick several available workers from swarm + backup
        with self._lock:
            candidate_ids = [wid for layer in ('default', 'backup', 'swarm') for wid in self.layers.get(layer, [])]
            available = [self.workers[wid] for wid in candidate_ids if not self.workers[wid].busy]
        if not available:
            # no available worker, wait a bit and retry
            await asyncio.sleep(0.2)
            with self._lock:
                available = [w for w in self.workers.values() if not w.busy]
            if not available:
                logger.warning("No available workers for collaborative mode; failing task")
                task.status = 'failed'
                return False, {'error': 'no-workers-available'}
        # choose up to N collaborators (bounded)
        collaborators = available[: min(len(available), exec_ctx.get('collab_max', 3))]
        # mark collaborators so they shorten runtime
        ctx = {'collaborators': len(collaborators)}
        # run all in parallel
        run_coros = [w.execute(task, ctx) for w in collaborators]
        results = await asyncio.gather(*run_coros, return_exceptions=True)
        # aggregate: success if any of them returned success
        success = any((not isinstance(r, Exception) and r[0]) for r in results)
        # choose the fastest success result if any
        final_res = None
        for r in results:
            if isinstance(r, Exception):
                continue
            ok, res = r
            if ok:
                final_res = res
                break
            if final_res is None:
                final_res = res
        task.status = 'success' if success else 'failed'
        task.result = final_res
        return success, final_res

    async def worker_loop(self, poll_interval: float = 0.05):
        while not self.shutdown_flag:
            try:
                task = await asyncio.wait_for(self.task_q.get(), timeout=poll_interval)
            except asyncio.TimeoutError:
                await asyncio.sleep(0)
                continue
            try:
                logger.info(f"Dequeued task {task.id}: {task.command}")
                task.status = 'running'
                ok, res = await self.assign_task(task, exec_ctx={})
                if ok:
                    logger.info(f"Task {task.id} succeeded")
                else:
                    logger.warning(f"Task {task.id} failed")
            except Exception as e:
                logger.exception("Unhandled exception processing task")
            finally:
                self.task_q.task_done()

    def enqueue(self, task: Task):
        self.metrics['enqueued'] += 1
        asyncio.get_event_loop().call_soon_threadsafe(self.task_q.put_nowait, task)


# ------------------------
# Autoscaler & Monitor
# ------------------------
class Autoscaler:
    """
    Monitors queue depth, worker utilization, and system capacity to scale workers across three layers.
    This simple autoscaler uses heuristics; replace with ML-based decisions in production.
    """

    def __init__(self, pool: WorkerPool, target_util=0.6, max_default_per_cpu=2, max_backup=8, max_swarm=20):
        self.pool = pool
        self.target_util = target_util
        self.max_default_per_cpu = max_default_per_cpu
        self.max_backup = max_backup
        self.max_swarm = max_swarm
        self.running = False
        self._task = None
        self.logger = logging.getLogger('Autoscaler')

    def _system_capacity(self):
        cpus = os.cpu_count() or 1
        mem = None
        if psutil:
            try:
                mem = psutil.virtual_memory().available
            except Exception:
                mem = None
        return {'cpus': cpus, 'avail_mem': mem}

    def _current_util(self):
        total = len(self.pool.workers)
        if total == 0:
            return 0.0
        busy = sum(1 for w in self.pool.workers.values() if w.busy)
        return busy / total

    async def run(self, interval: float = 1.0):
        self.running = True
        while self.running:
            try:
                qsize = self.pool.task_q.qsize()
                util = self._current_util()
                cap = self._system_capacity()
                desired_default = min(cap['cpus'] * self.max_default_per_cpu, max(1, math.ceil(qsize / 2)))
                # ensure some default workers exist
                current_default = len(self.pool.layers.get('default', []))
                if current_default < desired_default:
                    # spawn workers into default
                    to_add = desired_default - current_default
                    for _ in range(to_add):
                        wid = f'D-{TaskParser.gen_id()}'
                        # NexusX specific: Add NexusX related skills
                        w = Worker(wid, layer='default', 
                                  primary_skills=['io', 'fetch', 'nexus', 'python'],
                                  secondary_skills=['process', 'docker', 'health'])
                        self.pool.add_worker(w)
                # if queue is large and util high, add backup and swarm
                if qsize > 5 and util > self.target_util:
                    # add backup up to cap
                    cur_backup = len(self.pool.layers.get('backup', []))
                    if cur_backup < self.max_backup:
                        wid = f'B-{TaskParser.gen_id()}'
                        # NexusX specific: Diversify skills for different workers
                        w = Worker(wid, layer='backup', 
                                  primary_skills=['process', 'docker', 'frontend'], 
                                  secondary_skills=['io', 'nexus', 'health'])
                        self.pool.add_worker(w)
                # if qsize very high, spin up swarm workers for collaborative speed
                if qsize > 12 and util > self.target_util:
                    cur_swarm = len(self.pool.layers.get('swarm', []))
                    if cur_swarm < self.max_swarm:
                        wid = f'S-{TaskParser.gen_id()}'
                        # NexusX specific: Swarm workers can handle all skills but specialize in collaboration
                        w = Worker(wid, layer='swarm', 
                                  primary_skills=['collaborate', 'nexus'],
                                  secondary_skills=['process', 'io', 'python', 'docker', 'frontend', 'health'])
                        self.pool.add_worker(w)
                # trim idle backups if underutilized
                if util < (self.target_util / 2):
                    # remove some backup workers
                    backups = list(self.pool.layers.get('backup', []))
                    removed = 0
                    for wid in backups:
                        w = self.pool.workers.get(wid)
                        if w and not w.busy and removed < 2:
                            self.pool.remove_worker(wid)
                            removed += 1
                await asyncio.sleep(interval)
            except Exception:
                self.logger.exception("Autoscaler error")
                await asyncio.sleep(interval)

    def stop(self):
        self.running = False


# ------------------------
# Monitor / Health / Dashboard
# ------------------------
class Monitor:
    def __init__(self, pool: WorkerPool):
        self.pool = pool
        self.metrics_history = deque(maxlen=500)
        self.logger = logging.getLogger('Monitor')

    def capture(self):
        snapshot = {
            'ts': now_str(),
            'queue': self.pool.task_q.qsize(),
            'total_workers': len(self.pool.workers),
            'by_layer': {l: len(self.pool.layers.get(l, [])) for l in self.pool.layers},
            'busy': sum(1 for w in self.pool.workers.values() if w.busy),
        }
        self.metrics_history.append(snapshot)
        return snapshot

    def export_stats(self) -> Dict[str, Any]:
        hist = list(self.metrics_history)
        return {'history': hist, 'latest': hist[-1] if hist else None}


class DashboardExporter:
    """
    Exports simple visualizations to PNG files using matplotlib.
    """

    @staticmethod
    def export(monitor: Monitor, filename_prefix: str = 'dashboard'):
        try:
            import matplotlib.pyplot as plt
        except Exception as e:
            logger.warning("matplotlib not available, skipping dashboard export")
            return None
        hist = list(monitor.metrics_history)
        if not hist:
            logger.info("No metrics to plot")
            return None
        ts = [h['ts'] for h in hist]
        q = [h['queue'] for h in hist]
        total_w = [h['total_workers'] for h in hist]
        busy = [h['busy'] for h in hist]

        # Plot queue depth
        plt.figure()
        plt.plot(q)
        plt.title('Queue depth over time')
        plt.xlabel('sample')
        plt.ylabel('queue')
        qp = f"{filename_prefix}_queue.png"
        plt.savefig(qp)
        plt.close()

        # Plot workers & busy
        plt.figure()
        plt.plot(total_w, label='total_workers')
        plt.plot(busy, label='busy')
        plt.title('Workers: total vs busy')
        plt.legend()
        wp = f"{filename_prefix}_workers.png"
        plt.savefig(wp)
        plt.close()
        logger.info(f"Saved dashboard files: {qp}, {wp}")
        return [qp, wp]


# ------------------------
# NexusX Todo Scanner
# ------------------------
class TodoScanner:
    """
    Scans for todo items in the NexusX project and converts them to tasks
    """
    
    def __init__(self, project_dir=None):
        self.project_dir = project_dir or os.getcwd()
        self.logger = logging.getLogger('TodoScanner')
        
    async def scan_todo_list(self) -> List[Task]:
        """
        Scan the NexusX todo list for pending items and convert them to tasks
        """
        tasks = []
        try:
            # In real implementation, parse the todo file or API
            # For now, create tasks based on known structure
            todos = await self._get_todos()
            
            for todo in todos:
                if todo['status'] == 'pending':
                    task = self._convert_todo_to_task(todo)
                    if task:
                        tasks.append(task)
                        
            self.logger.info(f"Scanned todo list, found {len(tasks)} pending tasks")
        except Exception as e:
            self.logger.error(f"Error scanning todo list: {e}")
            
        return tasks
        
    async def _get_todos(self) -> List[Dict[str, Any]]:
        """
        Get the list of todos from the project
        """
        # Mock implementation - in real version this would parse the actual todo list
        todos = [
            {
                "id": "system-reliability",
                "content": "Fix system startup script with proper health checks and error handling",
                "status": "pending"
            },
            {
                "id": "health-checks", 
                "content": "Implement health check endpoints for all services",
                "status": "pending"
            },
            {
                "id": "error-handling",
                "content": "Implement structured logging with correlation IDs and error categorization",
                "status": "pending"
            },
            {
                "id": "python-environment",
                "content": "Set up unified Python 3.12 environment (nexus_env) with all dependencies",
                "status": "in_progress"
            },
            {
                "id": "docker-setup",
                "content": "Set up Docker infrastructure with Docker Compose for all services",
                "status": "in_progress"
            },
            {
                "id": "frontend-homepage", 
                "content": "Implement the homepage (index.html) with platform overview and user roles",
                "status": "completed"
            }
        ]
        return todos
        
    def _convert_todo_to_task(self, todo: Dict[str, Any]) -> Optional[Task]:
        """
        Convert a todo item to a Task
        """
        todo_id = todo['id']
        content = todo['content'].lower()
        
        # Map todos to specific task types based on content
        if 'python environment' in content:
            return Task(
                id=f"nexus-{todo_id}",
                raw=content,
                command="nexus:setup_python_env",
                params={"todo_id": todo_id}
            )
        elif 'health check' in content:
            services = ['api-gateway', 'ai-engine', 'fraud-detection', 'forensic-analysis', 'frenly-ai']
            subtasks = []
            for service in services:
                subtasks.append(Task(
                    id=f"nexus-health-{service}",
                    raw=f"Implement health check for {service}",
                    command="nexus:implement_health_check",
                    params={"service": service}
                ))
            
            task = Task(
                id=f"nexus-{todo_id}",
                raw=content,
                command="nexus:health_checks",
                params={"todo_id": todo_id}
            )
            task.subtasks = subtasks
            return task
        elif 'docker' in content:
            services = ['api-gateway', 'ai-engine', 'fraud-detection', 'forensic-analysis', 'frenly-ai']
            subtasks = []
            for service in services:
                subtasks.append(Task(
                    id=f"nexus-docker-{service}",
                    raw=f"Set up Docker for {service}",
                    command="nexus:create_docker_service",
                    params={"service": service}
                ))
            
            task = Task(
                id=f"nexus-{todo_id}",
                raw=content,
                command="nexus:docker_setup",
                params={"todo_id": todo_id}
            )
            task.subtasks = subtasks
            return task
        elif 'error handling' in content or 'logging' in content:
            return Task(
                id=f"nexus-{todo_id}",
                raw=content,
                command="nexus:setup_logging",
                params={"todo_id": todo_id, "correlation_ids": True}
            )
        else:
            # Generic task
            return Task(
                id=f"nexus-{todo_id}",
                raw=content,
                command="nexus:generic_task",
                params={"todo_id": todo_id, "description": content}
            )


# ------------------------
# Master Executor
# ------------------------
class NexusMasterExecutor:
    def __init__(self, project_dir=None):
        self.project_dir = project_dir or os.getcwd()
        self.pool = WorkerPool()
        self.autoscaler = Autoscaler(self.pool)
        self.monitor = Monitor(self.pool)
        self.todo_scanner = TodoScanner(self.project_dir)
        self._autoscaler_task = None
        self._pool_task = None
        self._scanner_task = None
        self.logger = logging.getLogger('NexusMaster')
        # persistent state placeholder (in-memory master_todo list)
        self.master_todo: Dict[str, Task] = {}

    def load_master_todo_from_list(self, lines: List[str]):
        for raw in lines:
            t = TaskParser.parse(raw)
            self.master_todo[t.id] = t
            self.pool.enqueue(t)
        self.logger.info(f"Loaded {len(lines)} master todos")

    def update_master_status(self, task_id: str, status: str):
        t = self.master_todo.get(task_id)
        if not t:
            return
        t.status = status
        self.logger.info(f"Master todo {task_id} status updated to {status}")

    async def start(self):
        loop = asyncio.get_event_loop()
        # start worker_loop
        self._pool_task = loop.create_task(self.pool.worker_loop())
        # start autoscaler
        self._autoscaler_task = loop.create_task(self.autoscaler.run())
        # start monitor
        loop.create_task(self._monitor_loop())
        # start todo scanner
        self._scanner_task = loop.create_task(self._scanner_loop())

    async def stop(self):
        self.autoscaler.stop()
        self.pool.shutdown_flag = True
        if self._autoscaler_task:
            await asyncio.sleep(0.1)
        if self._pool_task:
            # give time to clear
            await asyncio.sleep(0.1)

    async def _monitor_loop(self, interval: float = 1.0):
        while not self.pool.shutdown_flag:
            snapshot = self.monitor.capture()
            logger.info(f"Monitor: queue={snapshot['queue']} total_workers={snapshot['total_workers']} busy={snapshot['busy']}")
            await asyncio.sleep(interval)
            
    async def _scanner_loop(self, interval: float = 10.0):
        """
        Periodically scan for pending todos and convert them to tasks
        """
        while not self.pool.shutdown_flag:
            try:
                self.logger.info("Scanning for pending todos...")
                tasks = await self.todo_scanner.scan_todo_list()
                for task in tasks:
                    if task.id not in self.master_todo:
                        self.master_todo[task.id] = task
                        self.pool.enqueue(task)
                        self.logger.info(f"Added new todo task: {task.id} - {task.command}")
            except Exception as e:
                self.logger.error(f"Error in todo scanner loop: {e}")
            await asyncio.sleep(interval)

    def export_dashboard(self):
        return DashboardExporter.export(self.monitor)


# ------------------------
# Example / Demo
# ------------------------
NEXUS_SAMPLE_TODOS = [
    "nexus:setup_python_env?todo_id=python-environment",
    "nexus:implement_health_check?service=api-gateway&todo_id=health-checks",
    "nexus:create_docker_service?service=ai-engine&todo_id=docker-setup",
    "nexus:setup_logging?correlation_ids=true&todo_id=error-handling"
]


async def demo_runtime():
    master = NexusMasterExecutor()
    # pre-populate a couple of default workers so the autoscaler doesn't have to immediately
    for i in range(2):
        w = Worker(f'D-{i+1}', layer='default', 
                 primary_skills=['nexus', 'python', 'docker'], 
                 secondary_skills=['process', 'health', 'frontend'])
        master.pool.add_worker(w)
    master.load_master_todo_from_list(NEXUS_SAMPLE_TODOS)
    await master.start()
    # run for n seconds letting autoscaler adjust
    run_for = 30
    start = time.time()
    try:
        while time.time() - start < run_for:
            # capture metrics
            master.monitor.capture()
            await asyncio.sleep(1)
    finally:
        await master.stop()
        # export dashboard images (if matplotlib present)
        files = master.export_dashboard()
        logger.info("Demo finished. Dashboard files: %s", files)


def main():
    logger.info("Starting NexusMasterExecutor demo")
    asyncio.run(demo_runtime())


if __name__ == '__main__':
    main()

import asyncio
import logging
from graphviz import Digraph

from automation.core.automation_engine import AutomationEngine
from automation.core.task_manager import TaskType

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """
    Creates a set of tasks with dependencies and generates a visualization of the dependency graph.
    """
    engine = AutomationEngine()
    await engine.initialize()

    # Create tasks with dependencies
    task_a_id = await engine.task_manager.create_task(
        title="Task A", description="Task A", task_type=TaskType.GENERAL
    )
    task_b_id = await engine.task_manager.create_task(
        title="Task B", description="Task B", task_type=TaskType.GENERAL, dependencies=[task_a_id]
    )
    task_c_id = await engine.task_manager.create_task(
        title="Task C", description="Task C", task_type=TaskType.GENERAL, dependencies=[task_a_id]
    )
    task_d_id = await engine.task_manager.create_task(
        title="Task D", description="Task D", task_type=TaskType.GENERAL, dependencies=[task_b_id, task_c_id]
    )

    logger.info("Tasks created.")

    # Get dependency graph
    dependency_graph = engine.task_manager._dependency_graph
    tasks = engine.task_manager._tasks

    # Create visualization
    dot = Digraph(comment='Task Dependency Graph')
    for task_id, task in tasks.items():
        dot.node(task_id, f"{task.title}\n({task_id[:8]})")

    for task_id, dependencies in dependency_graph.items():
        for dep_id in dependencies:
            dot.edge(dep_id, task_id)

    # Save visualization
    output_filename = 'dependency_graph.gv'
    dot.render(output_filename, view=False)
    logger.info(f"Dependency graph saved to {output_filename}.pdf")

    await engine.shutdown()

if __name__ == "__main__":
    asyncio.run(main())

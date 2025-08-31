import asyncio
import logging
from automation.core.automation_engine import AutomationEngine, SystemState
from automation.core.task_manager import TaskType, TaskPriority

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    engine = AutomationEngine()

    # Run the engine in the background.
    # The engine's run method has a loop that waits for a shutdown event.
    # We need to run it as a background task.
    engine_task = asyncio.create_task(engine.run())

    # Wait for the engine to initialize
    logger.info("Waiting for engine to initialize...")
    await asyncio.sleep(10) # Give it some time to start up everything

    if engine.state != SystemState.RUNNING:
        logger.error(f"Engine failed to start. Current state: {engine.state.value}")
        engine.shutdown_event.set()
        await engine_task
        return

    logger.info("Engine is running. Scheduling tasks...")
    # Schedule some tasks
    task_ids = []
    task_ids.append(await engine.schedule_task("Test Workflow Task", "A test workflow task", TaskType.WORKFLOW))
    task_ids.append(await engine.schedule_task("Test ML Task", "A test ML task", TaskType.ML))
    task_ids.append(await engine.schedule_task("Test General Task", "A test general task", TaskType.GENERAL))
    task_ids.append(await engine.schedule_task("Test Frontend Task", "A test frontend task", TaskType.FRONTEND))

    # Let the system run for a while to process tasks
    logger.info("Tasks scheduled. Waiting for 30 seconds for them to complete...")
    await asyncio.sleep(30)

    # Check task statuses
    all_completed = True
    for task_id in task_ids:
        if task_id:
            status_info = await engine.task_manager.get_task_status(task_id)
            if status_info:
                logger.info(f"Task '{status_info['title']}' ({task_id}) status: {status_info['status']}")
                if status_info['status'] != 'completed':
                    all_completed = False
                    logger.error(f"Task {task_id} did not complete successfully. Final status: {status_info['status']}")
            else:
                all_completed = False
                logger.error(f"Could not retrieve status for task {task_id}")

    if all_completed:
        logger.info("✅ All scheduled tasks completed successfully.")
    else:
        logger.error("❌ Some tasks did not complete successfully.")

    # Shutdown the engine
    logger.info("Shutting down engine...")
    engine.shutdown_event.set()
    await engine_task
    logger.info("Engine shut down.")

if __name__ == "__main__":
    asyncio.run(main())

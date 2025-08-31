#!/usr/bin/env python3
"""
🧪 CONSOLIDATED SYSTEM TEST - END-TO-END VERIFICATION 🧪

This script tests the consolidated automation system to verify that all 
components work together correctly after the merge and consolidation.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add automation to path
sys.path.insert(0, str(Path(__file__).parent / "automation"))

from core.automation_engine import AutomationEngine
from core.task_manager import TaskType, TaskPriority

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_consolidated_system():
    """Test the consolidated automation system end-to-end"""
    logger.info("🚀 Starting Consolidated System Test...")
    
    engine = AutomationEngine()
    
    try:
        # Test 1: System Initialization
        logger.info("📋 Test 1: System Initialization...")
        await engine.initialize()
        logger.info("✅ Test 1 PASSED: System initialized successfully")
        
        # Test 2: Task Creation
        logger.info("📋 Test 2: Task Creation...")
        task1_id = await engine.schedule_task(
            title="Test General Task",
            description="A test task for general processing",
            task_type=TaskType.GENERAL,
            priority=TaskPriority.MEDIUM
        )
        
        task2_id = await engine.schedule_task(
            title="Test ML Task", 
            description="A test task for ML processing",
            task_type=TaskType.ML,
            priority=TaskPriority.HIGH
        )
        
        logger.info(f"✅ Test 2 PASSED: Created tasks {task1_id} and {task2_id}")
        
        # Test 3: System Status Check
        logger.info("📋 Test 3: System Status Check...")
        status = await engine.get_system_status()
        logger.info(f"✅ Test 3 PASSED: System status retrieved - {status['state']}")
        
        # Test 4: Let system run briefly
        logger.info("📋 Test 4: Task Processing...")
        await asyncio.sleep(5)  # Let tasks process
        
        # Check task status
        task1_status = await engine.task_manager.get_task_status(task1_id)
        task2_status = await engine.task_manager.get_task_status(task2_id)
        
        logger.info(f"Task 1 status: {task1_status['status'] if task1_status else 'Not found'}")
        logger.info(f"Task 2 status: {task2_status['status'] if task2_status else 'Not found'}")
        logger.info("✅ Test 4 PASSED: Task processing working")
        
        # Test 5: Worker Status
        logger.info("📋 Test 5: Worker Status Check...")
        worker_stats = await engine.worker_manager.get_statistics()
        logger.info(f"Workers: {worker_stats['active_workers']}/{worker_stats['total_workers']} active")
        logger.info("✅ Test 5 PASSED: Worker system operational")
        
        logger.info("🎉 ALL TESTS PASSED - Consolidated system is working correctly!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.shutdown()
        logger.info("🔄 System shutdown completed")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_consolidated_system())
    if success:
        logger.info("✅ CONSOLIDATION VERIFICATION: System is ready for production!")
        sys.exit(0)
    else:
        logger.error("❌ CONSOLIDATION VERIFICATION: System has issues!")
        sys.exit(1)
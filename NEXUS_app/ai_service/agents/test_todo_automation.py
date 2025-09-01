#!/usr/bin/env python3
"""
Test file for TODO Automation System
Demonstrates the system functionality and provides sample TODOs for testing.
"""

import asyncio
import time
from typing import List

# Import the TODO automation system
from todo_automation_enhanced import TodoAutomationSystem, TodoItem


async def test_basic_functionality():
    """Test basic functionality of the TODO automation system"""
    print("🧪 Testing Basic Functionality")
    print("=" * 50)

    # Create automation system with 3 agents
    automation = TodoAutomationSystem(max_concurrent_agents=3)

    # Add some test TODOs
    test_todos = [
        TodoItem(
            id="test_1",
            content="# TODO: Implement user authentication system",
            file_path="auth.py",
            line_number=15,
            priority=5,
            tags=["security", "auth"],
        ),
        TodoItem(
            id="test_2",
            content="# TODO: Add unit tests for login function",
            file_path="test_auth.py",
            line_number=23,
            priority=4,
            tags=["testing", "unit_tests"],
        ),
        TodoItem(
            id="test_3",
            content="# TODO: Update API documentation",
            file_path="README.md",
            line_number=45,
            priority=3,
            tags=["documentation", "api"],
        ),
        TodoItem(
            id="test_4",
            content="# TODO: Optimize database queries",
            file_path="database.py",
            line_number=67,
            priority=4,
            tags=["performance", "database"],
        ),
        TodoItem(
            id="test_5",
            content="# TODO: Setup Docker containerization",
            file_path="Dockerfile",
            line_number=12,
            priority=3,
            tags=["docker", "deployment"],
        ),
    ]

    # Add TODOs to queue
    automation.todo_queue.extend(test_todos)

    print(f"📋 Added {len(test_todos)} test TODOs")
    print(f"🤖 Using {len(automation.agents)} agents")

    # Run automation
    start_time = time.time()
    await automation.run_automation()
    total_time = time.time() - start_time

    print(f"\n⏱️  Total execution time: {total_time:.2f} seconds")

    # Show final statistics
    stats = automation.get_progress_report()
    print(f"\n📊 Final Statistics:")
    print(f"  - Total Processed: {stats['total']}")
    print(f"  - Completed: {stats['completed']}")
    print(f"  - Failed: {stats['failed']}")


async def test_priority_processing():
    """Test priority-based processing"""
    print("\n🧪 Testing Priority Processing")
    print("=" * 50)

    automation = TodoAutomationSystem(max_concurrent_agents=2)

    # Create TODOs with different priorities
    priority_todos = [
        TodoItem(
            id="p1",
            content="# TODO [low]: Add comments",
            file_path="file1.py",
            line_number=1,
            priority=1,
        ),
        TodoItem(
            id="p2",
            content="# TODO [medium]: Refactor function",
            file_path="file2.py",
            line_number=2,
            priority=3,
        ),
        TodoItem(
            id="p3",
            content="# TODO [high]: Fix critical bug",
            file_path="file3.py",
            line_number=3,
            priority=5,
        ),
        TodoItem(
            id="p4",
            content="# TODO [urgent]: Security patch",
            file_path="file4.py",
            line_number=4,
            priority=5,
        ),
        TodoItem(
            id="p5",
            content="# TODO: General improvement",
            file_path="file5.py",
            line_number=5,
            priority=2,
        ),
    ]

    automation.todo_queue.extend(priority_todos)

    print("📋 Priority-based TODOs added:")
    for todo in priority_todos:
        print(f"  - Priority {todo.priority}: {todo.content}")

    # Run automation
    await automation.run_automation()

    print("\n✅ Priority processing test completed")


async def test_error_handling():
    """Test error handling and retry logic"""
    print("\n🧪 Testing Error Handling")
    print("=" * 50)

    automation = TodoAutomationSystem(max_concurrent_agents=1)

    # Create a TODO that will fail
    error_todo = TodoItem(
        id="error_test",
        content="# TODO: This will fail for testing",
        file_path="error.py",
        line_number=1,
        priority=1,
    )

    automation.todo_queue.append(error_todo)

    print("📋 Added error-prone TODO for testing")

    # Run automation
    await automation.run_automation()

    print("\n✅ Error handling test completed")


async def test_concurrent_processing():
    """Test concurrent processing capabilities"""
    print("\n🧪 Testing Concurrent Processing")
    print("=" * 50)

    # Test with different numbers of agents
    for agent_count in [2, 5, 10]:
        print(f"\n🤖 Testing with {agent_count} agents...")

        automation = TodoAutomationSystem(max_concurrent_agents=agent_count)

        # Add multiple TODOs
        concurrent_todos = [
            TodoItem(
                id=f"concurrent_{i}",
                content=f"# TODO: Concurrent task {i}",
                file_path=f"task_{i}.py",
                line_number=i,
                priority=3,
            )
            for i in range(1, agent_count + 3)  # More TODOs than agents
        ]

        automation.todo_queue.extend(concurrent_todos)

        start_time = time.time()
        await automation.run_automation()
        total_time = time.time() - start_time

        print(f"  - {len(concurrent_todos)} TODOs processed in {total_time:.2f}s")
        print(f"  - Average time per TODO: {total_time/len(concurrent_todos):.2f}s")


async def main():
    """Run all tests"""
    print("🚀 TODO Automation System - Test Suite")
    print("=" * 60)

    try:
        # Run basic functionality test
        await test_basic_functionality()

        # Run priority processing test
        await test_priority_processing()

        # Run error handling test
        await test_error_handling()

        # Run concurrent processing test
        await test_concurrent_processing()

        print("\n🎉 All tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        raise


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())

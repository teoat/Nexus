#!/usr/bin/env python3


def main():
    print("=== RESETTING TODO STATUS ===")

    # Check current status
    print(f"Total TODOs: {len(task_registry.priority_todos)}")
    completed = [t for t in task_registry.priority_todos if t["status"] == "completed"]
    pending = [t for t in task_registry.priority_todos if t["status"] == "pending"]
    print(f"Before reset - Completed: {len(completed)}, Pending: {len(pending)}")

    # Reset all to pending
    for todo in task_registry.priority_todos:
        todo["status"] = "pending"
        todo["implementation_status"] = "unimplemented"
        todo["assigned_agent"] = None
        todo["progress"] = 0.0

        # Reset subtask progress
        if "subtask_progress" in todo:
            for subtask in todo["subtask_progress"]:
                todo["subtask_progress"][subtask] = 0.0

    # Check status after reset
    completed = [t for t in task_registry.priority_todos if t["status"] == "completed"]
    pending = [t for t in task_registry.priority_todos if t["status"] == "pending"]
    print(f"After reset - Completed: {len(completed)}, Pending: {len(pending)}")

    print("\n=== FIRST 5 PENDING TODOs ===")
    for todo in task_registry.priority_todos[:5]:
        print(f"{todo['id']}: {todo['name']} - {todo['priority']} priority")
        print(f"  Status: {todo['status']}")
        print(f"  Implementation: {todo['implementation_status']}")
        print()


if __name__ == "__main__":
    main()

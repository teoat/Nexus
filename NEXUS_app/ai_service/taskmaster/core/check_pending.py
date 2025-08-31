#!/usr/bin/env python3


def main():
    print("=== PENDING TODO STATUS ===")

    pending = [t for t in task_registry.priority_todos if t["status"] == "pending"]
    completed = [t for t in task_registry.priority_todos if t["status"] == "completed"]

    print(f"Total TODOs: {len(task_registry.priority_todos)}")
    print(f"Pending: {len(pending)}")
    print(f"Completed: {len(completed)}")

    print("\n=== PENDING TODOs ===")
    for todo in pending:
        print(f"{todo['id']}: {todo['name']} - {todo['priority']} priority")
        print(f"  Duration: {todo['estimated_duration']}")
        print(f"  Subtasks: {todo.get('subtask_count', 0)}")
        print()


if __name__ == "__main__":
    main()

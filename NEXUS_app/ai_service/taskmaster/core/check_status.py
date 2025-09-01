#!/usr/bin/env python3


def main():
    print("=== CURRENT TODO STATUS ===")
    print(f"Total TODOs: {len(task_registry.priority_todos)}")

    pending = [t for t in task_registry.priority_todos if t["status"] == "pending"]
    completed = [t for t in task_registry.priority_todos if t["status"] == "completed"]

    print(f"Pending: {len(pending)}")
    print(f"Completed: {len(completed)}")

    print("\n=== PENDING TODOs ===")
    for todo in pending[:5]:
        print(f"{todo['id']}: {todo['name']} - {todo['priority']} priority")

    print("\n=== COMPLETED TODOs ===")
    for todo in completed[:5]:
        print(f"{todo['id']}: {todo['name']} - {todo['implementation_status']}")


if __name__ == "__main__":
    main()

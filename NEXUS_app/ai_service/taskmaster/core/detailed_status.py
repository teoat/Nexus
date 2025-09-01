#!/usr/bin/env python3


def main():
    print("=== DETAILED TODO STATUS ===")

    for i, todo in enumerate(task_registry.priority_todos, 1):
        print(f"{i}. {todo['id']}: {todo['name']}")
        print(f"   Priority: {todo['priority']}")
        print(f"   Status: {todo['status']}")
        print(f"   Implementation: {todo['implementation_status']}")
        print(f"   Progress: {todo['progress']}%")
        print(f"   Agent: {todo.get('assigned_agent', 'Unassigned')}")
        print(f"   Duration: {todo['estimated_duration']}")
        print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import sys

# Add current directory to path
sys.path.append(str(Path(__file__).parent))


def test_reader():
    print("🧪 Testing Working TODO Reader")
    print("=" * 40)

    # Test with explicit path
    todo_path = Path(__file__).parent.parent.parent.parent / "TODO_MASTER.md"
    print(f"📁 TODO_MASTER.md path: {todo_path}")
    print(f"📁 Path exists: {todo_path.exists()}")

    if todo_path.exists():
        print("✅ Path exists, testing reader...")

        reader = WorkingTodoReader(str(todo_path))
        todos = reader.read_todo_master()

        print(f"📋 Found {len(todos)} TODOs")

        if todos:
            print("\n📝 First 3 TODOs:")
            for i, todo in enumerate(todos[:3], 1):
                print(f"  {i}. {todo['id']}: {todo['name']}")
                print(f"     Priority: {todo['priority']}")
                print(f"     Duration: {todo['estimated_duration']}")
                print(f"     Section: {todo['section']}")
                print()
        else:
            print("❌ No TODOs found")
    else:
        print("❌ Path does not exist")


if __name__ == "__main__":
    test_reader()

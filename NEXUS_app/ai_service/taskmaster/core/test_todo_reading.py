#!/usr/bin/env python3


def main():
    print("🧪 TESTING TODO MASTER READING...")
    print("=" * 40)

    # Test the reader
    reader = TodoMasterReader()

    # Read all TODOs
    todos = reader.read_todo_master()
    print(f"📋 Total TODOs found: {len(todos)}")

    # Get stats
    stats = reader.get_todo_stats()
    print(f"📊 Stats: {stats}")

    # Show pending TODOs
    pending = reader.get_pending_todos()
    print(f"⏳ Pending TODOs: {len(pending)}")

    for i, todo in enumerate(pending[:10]):  # Show first 10
        print(f"  {i+1}. {todo['name']} ({todo['priority']} priority)")

    # Test the registry interface
    print("\n🔍 TESTING REGISTRY INTERFACE...")
    try:

        if task_registry:
            print("✅ Task registry available")
            all_todos = task_registry.get_all_todos()
            print(f"📋 Registry TODOs: {len(all_todos)}")

            pending_todos = task_registry.get_pending_todos()
            print(f"⏳ Registry pending: {len(pending_todos)}")
        else:
            print("❌ Task registry not available")
    except Exception as e:
        print(f"❌ Error with task registry: {e}")

    print("\n✅ Test completed!")


if __name__ == "__main__":
    main()

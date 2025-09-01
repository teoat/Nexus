#!/usr/bin/env python3


def main():
    print("🔍 DEBUGGING BATCH LOADING...")
    print("=" * 50)

    # Initialize processor
    processor = CollectiveWorkerProcessor(max_workers=8)

    # Check the raw registry data
    print("📋 Raw registry data:")
    if hasattr(processor, "task_registry") and processor.task_registry:
        todos = processor.task_registry.get_all_todos()
        print(f"  - Total TODOs in registry: {len(todos)}")

        if todos:
            print("  - First TODO:")
            first = todos[0]
            for key, value in list(first.items())[:10]:
                print(f"    {key}: {value}")

            # Check if they're marked as assigned
            pending = [
                t for t in todos if not t.get("assigned_to_collective_processor")
            ]
            print(f"  - Pending (not assigned): {len(pending)}")

            if pending:
                print("  - First pending TODO:")
                first_pending = pending[0]
                print(f"    Name: {first_pending.get('name')}")
                print(f"    Status: {first_pending.get('status')}")
                print(
                    f"    Assigned: {first_pending.get('assigned_to_collective_processor')}"
                )
        else:
            print("  - No TODOs in registry")
    else:
        print("  ❌ No task registry available")

    # Check the batch loading method directly
    print("\n🔍 Checking batch loading method:")
    try:
        work_items = processor.load_work_items_batch()
        print(f"  - Batch loading returned: {len(work_items)} items")

        if work_items:
            print("  - First work item:")
            first_item = work_items[0]
            print(f"    Name: {first_item.name}")
            print(f"    Complexity: {first_item.complexity}")
            print(f"    Priority: {first_item.priority}")
        else:
            print("  - No work items returned from batch loading")

    except Exception as e:
        print(f"  ❌ Error in batch loading: {e}")

    # Check the scan and mark method
    print("\n🔍 Checking scan and mark method:")
    try:
        scan_results = processor.scan_and_mark_todo_master()
        print(f"  - Scan results: {scan_results}")

        # Try loading again after scan
        work_items_after_scan = processor.load_work_items_batch()
        print(f"  - Batch loading after scan: {len(work_items_after_scan)} items")

    except Exception as e:
        print(f"  ❌ Error in scan and mark: {e}")

    print("\n✅ Debug completed")


if __name__ == "__main__":
    main()

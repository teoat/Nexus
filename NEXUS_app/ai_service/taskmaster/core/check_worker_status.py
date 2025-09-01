#!/usr/bin/env python3


def main():
    print("🔍 CHECKING COLLECTIVE WORKER SYSTEM STATUS...")
    print("=" * 50)

    # Initialize processor
    processor = CollectiveWorkerProcessor(max_workers=8)

    # Check current status
    print("📊 Current System Status:")
    print(f"  - Max Workers: {processor.max_workers}")
    print(f"  - Active Workers: {len(processor.worker_assignments)}")
    print(f"  - Cache Size: {len(processor.worker_cache)}")

    # Check if processing loop is running
    print("\n🔄 Processing Loop Status:")
    try:
        # Try to get stats
        stats = processor.get_collective_processing_stats()
        print(f"  - Complex TODOs: {stats.get('total_complex_todos', 0)}")
        print(f"  - Active Workers: {stats.get('active_workers', 0)}")
        print(f"  - Cache Size: {stats.get('cache_stats', {}).get('size', 0)}")
        print(f"  - Total Processed: {stats.get('total_processed', 0)}")
        print(f"  - Total Successful: {stats.get('total_successful', 0)}")
        print(f"  - Total Failed: {stats.get('total_failed', 0)}")
    except Exception as e:
        print(f"  ❌ Error getting stats: {e}")

    # Check TODO master status
    print("\n📋 TODO Master Status:")
    try:
        scan_results = processor.scan_and_mark_todo_master()
        print(f"  - Scanned: {scan_results.get('scanned', 0)}")
        print(f"  - Marked: {scan_results.get('marked', 0)}")
        print(f"  - Errors: {scan_results.get('errors', 0)}")

        # Check batch loading
        batch_items = processor.load_work_items_batch()
        print(f"  - Batch Loaded: {len(batch_items)}")

        if batch_items:
            print("  - Work Items Available:")
            for i, item in enumerate(batch_items[:5]):  # Show first 5
                print(f"    {i+1}. {item.name} ({item.complexity})")
        else:
            print("  - No work items available for batch loading")

    except Exception as e:
        print(f"  ❌ Error checking TODO master: {e}")

    # Check if workers are actually processing
    print("\n👥 Worker Status:")
    if processor.worker_assignments:
        print(f"  - Active Assignments: {len(processor.worker_assignments)}")
        for todo_id, assignments in list(processor.worker_assignments.items())[
            :3
        ]:  # Show first 3
            print(f"    - {todo_id}: {len(assignments)} workers assigned")
    else:
        print("  - No active worker assignments")

    # Check cache status
    print("\n💾 Cache Status:")
    if processor.worker_cache:
        print(f"  - Cache Entries: {len(processor.worker_cache)}")
        print(
            f"  - Cache Keys: {list(processor.worker_cache.keys())[:5]}"
        )  # Show first 5
    else:
        print("  - Cache is empty")

    print("\n✅ Status check completed!")

    # Suggest next steps
    print("\n💡 RECOMMENDATIONS:")
    if not processor.worker_assignments:
        print("  - Workers are not assigned to tasks")
        print("  - Try starting the processing loop")
    else:
        print("  - Workers are assigned and should be processing")
        print("  - Check individual worker logs")

    return True


if __name__ == "__main__":
    main()

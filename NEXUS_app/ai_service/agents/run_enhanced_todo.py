#!/usr/bin/env python3
"""
Enhanced TODO Automation Launcher
Runs the enhanced system with 10 concurrent agents, MCP logging, and continuous processing.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Main launcher function"""
    print("🚀 Enhanced TODO Automation System Launcher")
    print("=" * 60)
    print("✨ Features:")
    print("   • 10 Concurrent Agents")
    print("   • MCP Logging (prevents overlapping)")
    print("   • Continuous Processing Loops")
    print("   • Batch Processing (10 TODOs at a time)")
    print("   • Priority-based Queue")
    print("   • Robust Error Handling")
    print("=" * 60)

    # Get directory to scan
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = (
            input("Enter directory to scan (or press Enter for current): ").strip()
            or "."
        )

    # Get number of agents (default 10)
    try:
        if len(sys.argv) > 2:
            max_agents = int(sys.argv[2])
        else:
            max_agents_input = input(
                "Enter number of concurrent agents (default 10): "
            ).strip()
            max_agents = int(max_agents_input) if max_agents_input else 10
    except ValueError:
        print("❌ Invalid number of agents, using default: 10")
        max_agents = 10

    # Validate directory
    target_path = Path(target_dir)
    if not target_path.exists():
        print(f"❌ Directory does not exist: {target_dir}")
        return 1

    if not target_path.is_dir():
        print(f"❌ Path is not a directory: {target_dir}")
        return 1

    print(f"\n📁 Scanning directory: {target_path.absolute()}")
    print(f"🤖 Using {max_agents} concurrent agents")
    print(f"🎯 Processing 10 TODOs at a time")
    print(f"🔄 Continuous looping until completion")
    print("=" * 60)

    # Initialize and run enhanced automation
    try:
        automation = TodoAutomationSystem(max_concurrent_agents=max_agents)

        # Load TODOs
        print("🔍 Loading TODOs from files...")
        automation.load_todos_from_files(str(target_path))

        if not automation.todo_queue:
            print("ℹ️  No TODOs found in the specified directory")
            return 0

        print(f"📋 Found {len(automation.todo_queue)} TODOs to process")
        print(f"🚀 Starting enhanced automation...")

        # Run enhanced automation
        asyncio.run(automation.run_automation())

        return 0

    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

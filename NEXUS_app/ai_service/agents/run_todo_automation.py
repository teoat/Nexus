#!/usr/bin/env python3
"""
Simple launcher for TODO Automation System
Provides an easy way to run the system with common configurations.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Main launcher function"""
    print("🚀 TODO Automation System Launcher")
    print("=" * 50)

    # Get directory to scan
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = (
            input("Enter directory to scan (or press Enter for current): ").strip()
            or "."
        )

    # Get number of agents
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
    print("=" * 50)

    # Initialize and run automation
    try:
        automation = TodoAutomationSystem(max_concurrent_agents=max_agents)

        # Load TODOs
        automation.load_todos_from_files(str(target_path))

        if not automation.todo_queue:
            print("ℹ️  No TODOs found in the specified directory")
            return 0

        print(f"📋 Found {len(automation.todo_queue)} TODOs to process")

        # Run automation
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

#!/usr/bin/env python3
"""
Resource monitoring script for Nexus Platform containers
"""

import subprocess
import json
import time
from datetime import datetime
import psutil


def get_container_stats():
    """Get Docker container resource usage statistics"""
    try:
        result = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        containers = [
            json.loads(line) for line in result.stdout.strip().split("\n") if line
        ]
        return containers
    except subprocess.CalledProcessError as e:
        print(f"Error getting container stats: {e}")
        return []


def get_system_stats():
    """Get system resource usage"""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "timestamp": datetime.now().isoformat(),
    }


def check_resource_limits(containers):
    """Check if containers are hitting resource limits"""
    warnings = []

    for container in containers:
        name = container.get("Name", "Unknown")
        cpu_percent = float(container.get("CPUPerc", "0%").rstrip("%"))
        mem_percent = float(container.get("MemPerc", "0%").rstrip("%"))

        if cpu_percent > 80:
            warnings.append(f"⚠️  {name}: High CPU usage ({cpu_percent:.1f}%)")
        if mem_percent > 80:
            warnings.append(f"⚠️  {name}: High memory usage ({mem_percent:.1f}%)")

    return warnings


def main():
    print("🔍 Nexus Platform Resource Monitor")
    print("=" * 50)

    while True:
        try:
            # Get container stats
            containers = get_container_stats()
            system_stats = get_system_stats()

            # Clear screen (Unix-like systems)
            print("\033[2J\033[H")

            print(f"📊 System Status - {system_stats['timestamp']}")
            print(
                f"CPU: {system_stats['cpu_percent']:.1f}% | "
                f"Memory: {system_stats['memory_percent']:.1f}% | "
                f"Disk: {system_stats['disk_percent']:.1f}%"
            )
            print("-" * 50)

            if containers:
                print("🔄 Container Resource Usage:")
                for container in containers:
                    name = container.get("Name", "Unknown")
                    cpu = container.get("CPUPerc", "N/A")
                    mem = container.get("MemPerc", "N/A")
                    net_io = container.get("NetIO", "N/A")
                    block_io = container.get("BlockIO", "N/A")

                    print(f"  {name}:")
                    print(f"    CPU: {cpu} | Memory: {mem}")
                    print(f"    Network: {net_io} | Disk: {block_io}")
                    print()

                # Check for warnings
                warnings = check_resource_limits(containers)
                if warnings:
                    print("🚨 Resource Warnings:")
                    for warning in warnings:
                        print(f"  {warning}")
                    print()

            print("Press Ctrl+C to stop monitoring...")
            time.sleep(5)

        except KeyboardInterrupt:
            print("\nMonitoring stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()

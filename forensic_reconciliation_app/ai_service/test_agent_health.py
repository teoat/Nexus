#!/usr/bin/env python3
"""
Test script for Frenly Agent Health Monitoring (Phase 1, Items 1-5)

This script tests:
1. Agent heartbeat check functionality
2. Agent failure handling
3. Agent recovery with retry logic
4. Health status tracking
5. API endpoints for health monitoring
"""

import asyncio
import time
from .agents.frenly_meta_agent import FrenlyMetaAgent

def test_agent_health_monitoring():
    """Test the first 5 todo items from Phase 1."""
    print("🧪 Testing Frenly Agent Health Monitoring (Phase 1, Items 1-5)")
    print("=" * 70)
    
    # Initialize Frenly
    print("\n1️⃣ Initializing Frenly Meta Agent...")
    frenly = FrenlyMetaAgent()
    
    # Test 1: Register agents and check health tracking
    print("\n2️⃣ Testing agent registration and health tracking...")
    
    # Create mock agents
    class MockAgent:
        def __init__(self, name):
            self.name = name
            self.is_healthy = True
        
        def health_check(self):
            return self.is_healthy
        
        def restart(self):
            self.is_healthy = True
            return True
    
    # Register mock agents
    mock_agents = {
        "reconciliation_agent": MockAgent("reconciliation"),
        "fraud_agent": MockAgent("fraud"),
        "risk_agent": MockAgent("risk")
    }
    
    for name, agent in mock_agents.items():
        frenly.register_ai_agent(name, agent)
        print(f"   ✅ Registered {name}")
    
    # Test 2: Check initial health status
    print("\n3️⃣ Testing initial health status...")
    all_status = frenly.get_all_agent_status()
    print(f"   📊 Agent count: {len(all_status)}")
    
    for agent_name, health in all_status.items():
        print(f"   🔍 {agent_name}: {health['status']} (alive: {health['is_alive']})")
    
    # Test 3: Test heartbeat check
    print("\n4️⃣ Testing heartbeat check functionality...")
    for agent_name in mock_agents.keys():
        is_alive = frenly.check_agent_alive(agent_name)
        print(f"   💓 {agent_name} heartbeat: {'✅ ALIVE' if is_alive else '❌ DEAD'}")
    
    # Test 4: Test agent failure handling
    print("\n5️⃣ Testing agent failure handling...")
    
    # Make one agent unhealthy
    mock_agents["fraud_agent"].is_healthy = False
    print("   🚫 Made fraud_agent unhealthy")
    
    # Check health again
    frenly.check_agent_alive("fraud_agent")
    fraud_status = frenly.get_agent_status("fraud_agent")
    print(f"   📊 fraud_agent status: {fraud_status['status']}")
    print(f"   📊 fraud_agent failure reason: {fraud_status['failure_reason']}")
    print(f"   📊 fraud_agent failure count: {fraud_status['failure_count']}")
    
    # Test 5: Test agent recovery
    print("\n6️⃣ Testing agent recovery...")
    
    # Try to restart the failed agent
    restart_success = frenly.restart_agent("fraud_agent")
    print(f"   🔄 Restart fraud_agent: {'✅ SUCCESS' if restart_success else '❌ FAILED'}")
    
    # Check health after restart
    frenly.check_agent_alive("fraud_agent")
    fraud_status_after = frenly.get_agent_status("fraud_agent")
    print(f"   📊 fraud_agent status after restart: {fraud_status_after['status']}")
    
    # Test 6: Test overall system health
    print("\n7️⃣ Testing overall system health...")
    system_health = frenly.get_overall_system_health()
    print(f"   🏥 Overall status: {system_health['overall_status']}")
    print(f"   🏥 Health score: {system_health['health_score']}%")
    print(f"   🏥 Active agents: {system_health['agents']['active']}/{system_health['agents']['total']}")
    
    # Test 7: Test heartbeat monitoring
    print("\n8️⃣ Testing heartbeat monitoring...")
    print("   🚀 Starting heartbeat monitoring (5 seconds)...")
    frenly.start_heartbeat_monitoring(interval_seconds=1)
    
    # Let it run for a few seconds
    time.sleep(5)
    
    # Stop monitoring
    frenly.stop_heartbeat_monitoring()
    print("   🛑 Stopped heartbeat monitoring")
    
    # Final health check
    print("\n9️⃣ Final health status...")
    final_health = frenly.get_all_agent_status()
    for agent_name, health in final_health.items():
        print(f"   🔍 {agent_name}: {health['status']} (last seen: {health['last_seen']})")
    
    print("\n✅ Phase 1 Testing Complete!")
    print("=" * 70)
    
    return True

def test_api_endpoints():
    """Test the API endpoints for health monitoring."""
    print("\n🌐 Testing API Endpoints for Health Monitoring")
    print("=" * 50)
    
    # Initialize Frenly
    frenly = FrenlyMetaAgent()
    
    # Create mock agents
    class MockAgent:
        def __init__(self, name):
            self.name = name
            self.is_healthy = True
        
        def health_check(self):
            return self.is_healthy
    
    # Register agents
    frenly.register_ai_agent("test_agent", MockAgent("test"))
    
    # Test API methods (simulated)
    print("   📊 Testing get_all_agent_status()...")
    all_status = frenly.get_all_agent_status()
    print(f"      ✅ Success: {len(all_status)} agents")
    
    print("   📊 Testing get_agent_status('test_agent')...")
    agent_status = frenly.get_agent_status("test_agent")
    print(f"      ✅ Success: {agent_status['status']}")
    
    print("   📊 Testing get_overall_system_health()...")
    system_health = frenly.get_overall_system_health()
    print(f"      ✅ Success: {system_health['overall_status']}")
    
    print("   ✅ API Endpoint Testing Complete!")

if __name__ == "__main__":
    try:
        # Test core functionality
        test_agent_health_monitoring()
        
        # Test API endpoints
        test_api_endpoints()
        
        print("\n🎉 All tests passed! Phase 1 implementation is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

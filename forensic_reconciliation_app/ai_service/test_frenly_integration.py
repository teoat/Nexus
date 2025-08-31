"""
Test Frenly Integration

This script tests the basic functionality of Frenly meta-agent integration.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from .agents.frenly_meta_agent import FrenlyMetaAgent, AppCommand


def test_frenly_basic_functionality():
    """Test basic Frenly functionality."""
    print("🧪 Testing Frenly Basic Functionality...")
    
    try:
        # Initialize Frenly
        frenly = FrenlyMetaAgent()
        print("✅ Frenly initialized successfully")
        
        # Test initial status
        status_response = frenly.manage_app(AppCommand(command_type="get_status"))
        print(f"✅ Status retrieved: {status_response.message}")
        
        # Test app mode switching
        mode_response = frenly.manage_app(AppCommand(
            command_type="switch_app_mode",
            target_mode="construction"
        ))
        print(f"✅ Mode switch: {mode_response.message}")
        
        # Test AI mode change
        ai_response = frenly.manage_app(AppCommand(
            command_type="change_ai_mode",
            target_ai_mode="extreme"
        ))
        print(f"✅ AI mode change: {ai_response.message}")
        
        # Test thinking perspective change
        perspective_response = frenly.manage_app(AppCommand(
            command_type="change_thinking_perspective",
            target_perspective="investigation"
        ))
        print(f"✅ Thinking perspective change: {perspective_response.message}")
        
        # Test mode intersection
        intersection_response = frenly.manage_app(AppCommand(command_type="get_mode_intersection"))
        print(f"✅ Mode intersection: {intersection_response.message}")
        
        print("\n🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


def test_frenly_mode_intersections():
    """Test Frenly mode intersections."""
    print("\n🧪 Testing Frenly Mode Intersections...")
    
    try:
        frenly = FrenlyMetaAgent()
        
        # Test construction + investigation + guided
        frenly.manage_app(AppCommand(command_type="switch_app_mode", target_mode="construction"))
        frenly.manage_app(AppCommand(command_type="change_thinking_perspective", target_perspective="investigation"))
        frenly.manage_app(AppCommand(command_type="change_ai_mode", target_ai_mode="guided"))
        
        intersection = frenly._get_current_mode_intersection()
        if intersection:
            print(f"✅ Mode intersection found: {intersection.description}")
            print(f"   Features: {len(intersection.features)}")
            print(f"   Agent priorities: {intersection.agent_priorities}")
        else:
            print("❌ No mode intersection found")
            return False
        
        # Test regular + litigation + extreme
        frenly.manage_app(AppCommand(command_type="switch_app_mode", target_mode="regular"))
        frenly.manage_app(AppCommand(command_type="change_thinking_perspective", target_perspective="litigation"))
        frenly.manage_app(AppCommand(command_type="change_ai_mode", target_ai_mode="extreme"))
        
        intersection = frenly._get_current_mode_intersection()
        if intersection:
            print(f"✅ Mode intersection found: {intersection.description}")
            print(f"   Features: {len(intersection.features)}")
            print(f"   Agent priorities: {intersection.agent_priorities}")
        else:
            print("❌ No mode intersection found")
            return False
        
        print("🎉 All mode intersection tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Mode intersection test failed: {str(e)}")
        return False


def test_frenly_agent_registration():
    """Test Frenly agent registration."""
    print("\n🧪 Testing Frenly Agent Registration...")
    
    try:
        frenly = FrenlyMetaAgent()
        
        # Test agent registration
        test_agent = {"name": "test_agent", "capabilities": ["test"]}
        frenly.register_ai_agent("test_agent", test_agent)
        
        # Test agent listing
        agents = frenly.list_ai_agents()
        if "test_agent" in agents:
            print("✅ Agent registration successful")
        else:
            print("❌ Agent registration failed")
            return False
        
        # Test agent retrieval
        retrieved_agent = frenly.get_ai_agent("test_agent")
        if retrieved_agent == test_agent:
            print("✅ Agent retrieval successful")
        else:
            print("❌ Agent retrieval failed")
            return False
        
        print("🎉 All agent registration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Agent registration test failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Frenly Integration Tests...\n")
    
    tests = [
        test_frenly_basic_functionality,
        test_frenly_mode_intersections,
        test_frenly_agent_registration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Frenly integration is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

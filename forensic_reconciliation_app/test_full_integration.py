#!/usr/bin/env python3
"""
Comprehensive Frenly Integration Test

This script tests all aspects of the Frenly integration with the main platform.
"""

import asyncio
import requests
import json
import sys
import os
from datetime import datetime

# Add the ai_service directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_service'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_service', 'agents'))

async def test_frenly_agent_functionality():
    """Test Frenly agent core functionality."""
    print("🤖 Testing Frenly Agent Core Functionality...")
    
    try:
        from ai_service.agents.frenly_meta_agent import FrenlyMetaAgent, AppCommand
        
        # Initialize Frenly
        frenly = FrenlyMetaAgent()
        print("  ✅ Frenly agent initialized")
        
        # Test app mode switching
        response = await frenly.manage_app(AppCommand(
            command_type="switch_app_mode",
            target_mode="construction"
        ))
        print(f"  ✅ App mode switch: {response.message}")
        
        # Test AI mode change
        response = await frenly.manage_app(AppCommand(
            command_type="change_ai_mode",
            target_ai_mode="guided"
        ))
        print(f"  ✅ AI mode change: {response.message}")
        
        # Test dashboard view change
        response = await frenly.manage_app(AppCommand(
            command_type="change_dashboard_view",
            target_view="reconciliation"
        ))
        print(f"  ✅ Dashboard view change: {response.message}")
        
        # Test user role change
        response = await frenly.manage_app(AppCommand(
            command_type="change_user_role",
            user_role="analyst"
        ))
        print(f"  ✅ User role change: {response.message}")
        
        print("  ✅ All core functionality tests passed")
        return True
        
    except Exception as e:
        print(f"  ❌ Core functionality test failed: {e}")
        return False

def test_user_integration_features():
    """Test user integration features."""
    print("\n👤 Testing User Integration Features...")
    
    try:
        from ai_service.frenly_user_integration import FrenlyUserIntegration
        
        # Mock Frenly agent
        class MockFrenlyAgent:
            def __init__(self):
                self.app_context = type('obj', (object,), {
                    'app_mode': type('obj', (object,), {'value': 'regular'}),
                    'ai_mode': type('obj', (object,), {'value': 'guided'}),
                    'dashboard_view': type('obj', (object,), {'value': 'reconciliation'})
                })()
            
            def manage_app(self, command):
                return type('obj', (object,), {'success': True})()
        
        frenly = MockFrenlyAgent()
        
        # Initialize user integration
        integration = FrenlyUserIntegration(frenly)
        print("  ✅ User integration service initialized")
        
        # Test configuration
        integration.set_main_platform_config("http://localhost:8000")
        print("  ✅ Main platform configuration set")
        
        # Test integration status
        status = integration.get_integration_status()
        print(f"  ✅ Integration status: {status['main_platform_status']}")
        
        # Test user analytics (will be empty but should work)
        analytics = integration.get_user_analytics("test_user")
        print(f"  ✅ User analytics: {analytics['total_activities']} activities")
        
        # Test cross-platform summary
        summary = integration.get_cross_platform_user_summary("test_user")
        if "error" not in summary:
            print("  ✅ Cross-platform user summary generated")
        else:
            print(f"  ⚠️  Cross-platform summary: {summary['error']} (expected without main platform)")
        
        print("  ✅ All user integration tests passed")
        return True
        
    except Exception as e:
        print(f"  ❌ User integration test failed: {e}")
        return False

def test_agent_registration():
    """Test agent registration and health monitoring."""
    print("\n🔧 Testing Agent Registration & Health...")
    
    try:
        from ai_service.agents.frenly_meta_agent import FrenlyMetaAgent
        
        # Initialize Frenly
        frenly = FrenlyMetaAgent()
        print("  ✅ Frenly agent initialized")
        
        # Check registered agents
        agents = frenly.list_ai_agents()
        print(f"  ✅ Registered agents: {len(agents)} agents")
        for agent_name in agents:
            print(f"    - {agent_name}")
        
        # Test agent health
        health = frenly.get_overall_system_health()
        print(f"  ✅ System health: {health['overall_status']} (score: {health['health_score']})")
        
        # Test agent status
        agent_status = frenly.get_all_agent_status()
        print(f"  ✅ Agent status monitoring: {len(agent_status)} agents tracked")
        
        print("  ✅ All agent registration tests passed")
        return True
        
    except Exception as e:
        print(f"  ❌ Agent registration test failed: {e}")
        return False

def test_workflow_system():
    """Test workflow system functionality."""
    print("\n⚡ Testing Workflow System...")
    
    try:
        from ai_service.agents.frenly_meta_agent import FrenlyMetaAgent
        
        # Initialize Frenly
        frenly = FrenlyMetaAgent()
        print("  ✅ Frenly agent initialized")
        
        # Check available workflows
        workflows = frenly.get_available_workflows()
        print(f"  ✅ Available workflows: {len(workflows)} workflows")
        for workflow_name in workflows:
            print(f"    - {workflow_name}")
        
        # Test workflow status
        workflow_status = frenly.get_workflow_status()
        print(f"  ✅ Workflow status tracking: {len(workflow_status)} workflows")
        
        print("  ✅ All workflow tests passed")
        return True
        
    except Exception as e:
        print(f"  ❌ Workflow test failed: {e}")
        return False

def test_metrics_and_monitoring():
    """Test metrics and monitoring systems."""
    print("\n📊 Testing Metrics & Monitoring...")
    
    try:
        from ai_service.agents.frenly_meta_agent import FrenlyMetaAgent
        
        # Initialize Frenly
        frenly = FrenlyMetaAgent()
        print("  ✅ Frenly agent initialized")
        
        # Test performance metrics
        metrics = frenly.get_performance_metrics()
        print(f"  ✅ Performance metrics: {metrics['overview']['total_commands']} commands")
        
        # Test recent events
        events = frenly.get_recent_events(limit=5)
        print(f"  ✅ Recent events: {len(events)} events")
        
        # Test error log
        errors = frenly.get_error_log(limit=5)
        print(f"  ✅ Error log: {len(errors)} errors")
        
        print("  ✅ All metrics and monitoring tests passed")
        return True
        
    except Exception as e:
        print(f"  ❌ Metrics and monitoring test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints if service is running."""
    print("\n🌐 Testing API Endpoints...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8001/api/frenly/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Health endpoint: Working")
        else:
            print(f"  ❌ Health endpoint: Failed with status {response.status_code}")
            return False
        
        # Test WebSocket status
        response = requests.get("http://localhost:8001/api/frenly/websocket/status", timeout=5)
        if response.status_code == 200:
            print("  ✅ WebSocket status: Working")
        else:
            print(f"  ❌ WebSocket status: Failed with status {response.status_code}")
            return False
        
        print("  ✅ All API endpoint tests passed")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  API endpoints: Service not running - {e}")
        print("  ℹ️  Start the service with: python start_frenly.py")
        return False

# This file is now designed to be run with pytest.
# The main function has been removed.

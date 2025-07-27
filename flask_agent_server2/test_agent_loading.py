#!/usr/bin/env python
"""
Test script to verify agent loading works correctly
"""

import os
import sys
from agent_manager import AgentManager

def test_agent_loading():
    """Test loading the Oracle Agent"""
    
    # Set agent path - adjust this to your actual path
    agent_paths_to_try = [
        "../oracle_agent",
        "./agents/oracle_agent",
        "oracle_agent"
    ]
    
    for agent_path in agent_paths_to_try:
        print(f"\n🔍 Testing agent path: {agent_path}")
        
        if os.path.exists(agent_path):
            print(f"✅ Path exists: {agent_path}")
            
            try:
                # Test loading the agent
                manager = AgentManager(agent_path=agent_path)
                
                if manager.is_agent_loaded():
                    print(f"✅ Agent loaded successfully!")
                    print(f"   Agent type: {manager.agent_type}")
                    print(f"   Agent info: {manager.get_agent_info()}")
                    return True
                else:
                    print(f"❌ Agent failed to load")
                    
            except Exception as e:
                print(f"❌ Error loading agent: {e}")
        else:
            print(f"❌ Path does not exist: {agent_path}")
    
    return False

if __name__ == "__main__":
    print("🚀 Testing Oracle Agent Loading")
    print("=" * 40)
    
    success = test_agent_loading()
    
    if success:
        print("\n🎉 Agent loading test PASSED!")
    else:
        print("\n💥 Agent loading test FAILED!")
        print("\nTroubleshooting:")
        print("1. Make sure oracle_agent is in the correct location")
        print("2. Check that oracle_agent/agent.py exists")
        print("3. Verify all __init__.py files are present")
        print("4. Update AGENT_PATH in .env file")
        
    sys.exit(0 if success else 1) 
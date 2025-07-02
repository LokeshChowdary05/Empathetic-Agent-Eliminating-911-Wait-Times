#!/usr/bin/env python3
"""
Test script for Emergency Response System
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import config
from agents import EmergencyOrchestrator

async def test_agents():
    """Test the emergency response agents"""
    print("🧪 Testing Emergency Response System Agents...")
    
    # Initialize configuration
    app_config = config['development']
    
    # Initialize orchestrator
    orchestrator = EmergencyOrchestrator(app_config.__dict__)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Critical Medical Emergency",
            "caller_info": {"phone": "123-456-7890", "address": "123 Main St"},
            "messages": [
                "Someone is unconscious and not breathing!",
                "Yes, they're not responding at all",
                "123 Main Street, apartment 2B",
                "He's about 45 years old"
            ]
        },
        {
            "name": "Fire Emergency",
            "caller_info": {"phone": "987-654-3210"},
            "messages": [
                "There's a fire in my kitchen!",
                "456 Oak Avenue",
                "The fire is spreading to the curtains"
            ]
        },
        {
            "name": "Chest Pain",
            "caller_info": None,
            "messages": [
                "I'm having severe chest pain",
                "It's about an 8 out of 10",
                "789 Elm Street"
            ]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🔄 Testing: {scenario['name']}")
        print("-" * 50)
        
        # Start session
        session_id = await orchestrator.start_session(scenario['caller_info'])
        print(f"✅ Session started: {session_id[:8]}...")
        
        # Process messages
        for i, message in enumerate(scenario['messages'], 1):
            print(f"\n👤 User (Turn {i}): {message}")
            
            response = await orchestrator.process_message(session_id, message)
            
            print(f"🤖 {response['agent_type'].title()} Agent: {response['message'][:100]}...")
            print(f"   Urgency: {response['urgency_level']}, Confidence: {response['confidence']:.2f}")
        
        # Get session status
        status = orchestrator.get_session_status(session_id)
        print(f"\n📊 Final Status:")
        print(f"   - Urgency: {status['urgency_level']}")
        print(f"   - Emergency Type: {status['emergency_type']}")
        print(f"   - Triage Complete: {status['triage_complete']}")
        print(f"   - Empathy Score: {status['empathy_score']:.2f}")
        
        # End session
        summary = orchestrator.end_session(session_id)
        print(f"✅ Session ended successfully")

def test_imports():
    """Test that all imports work correctly"""
    print("🔍 Testing imports...")
    
    try:
        from config.config import config
        print("✅ Config import successful")
        
        from agents import EmergencyOrchestrator, EmpathyAgent, TriageAgent, GuidanceAgent, DispatchAgent
        print("✅ All agent imports successful")
        
        from backend.models import create_database, EmergencyCall
        print("✅ Database model imports successful")
        
        import vaderSentiment
        print("✅ VaderSentiment import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚨 Emergency Response System - Test Suite")
    print("=" * 60)
    
    # Test imports first
    if not test_imports():
        print("\n❌ Import tests failed. Please install requirements first:")
        print("pip install -r requirements.txt")
        return
    
    print("\n✅ All imports successful!")
    
    # Test agents
    print("\n" + "=" * 60)
    asyncio.run(test_agents())
    
    print("\n🎉 All tests completed successfully!")
    print("\nNext steps:")
    print("1. Start the backend API: python backend/main.py")
    print("2. Start the Gradio interface: python frontend/main_gradio.py")

if __name__ == "__main__":
    main()

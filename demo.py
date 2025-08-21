#!/usr/bin/env python3
"""
ZENO Demo Script
Demonstrates key functionality without the web interface
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config import Config
from core.assistant import ZenoAssistant

async def demo_conversation():
    """Demo conversation mode"""
    print("\n🗣️  CONVERSATION MODE DEMO")
    print("=" * 40)
    
    zeno = ZenoAssistant()
    
    # Test conversations
    test_inputs = [
        "Hello ZENO, what can you do?",
        "What is machine learning?",
        "Tell me a joke",
        "Switch to control mode"
    ]
    
    for user_input in test_inputs:
        print(f"\n👤 User: {user_input}")
        response = await zeno.process_input(user_input, "text")
        print(f"🤖 ZENO: {response['content']}")
        print(f"   Mode: {response['mode']} | Type: {response['type']}")

async def demo_control():
    """Demo control mode"""
    print("\n🎮 CONTROL MODE DEMO")
    print("=" * 40)
    
    zeno = ZenoAssistant()
    zeno.set_mode("control")
    
    # Test control commands
    test_inputs = [
        "open notepad",  # Should require wake word
        "Zeno, open calculator",  # Should work
        "Zeno, set volume to 50",  # Should work
        "Zeno, search for Python tutorials",  # Should work
    ]
    
    for user_input in test_inputs:
        print(f"\n👤 User: {user_input}")
        response = await zeno.process_input(user_input, "text")
        print(f"🤖 ZENO: {response['content']}")
        print(f"   Success: {response.get('data', {}).get('success', 'N/A')}")

async def demo_memory():
    """Demo memory system"""
    print("\n🧠 MEMORY SYSTEM DEMO")
    print("=" * 40)
    
    zeno = ZenoAssistant()
    
    if zeno.memory:
        # Add some interactions
        await zeno.process_input("My name is John", "text")
        await zeno.process_input("I like Python programming", "text")
        await zeno.process_input("Zeno, open notepad", "text")
        
        # Check memory
        summary = zeno.memory.get_conversation_summary(hours=24)
        print(f"📊 Interactions today: {summary['total_interactions']}")
        print(f"📝 Text interactions: {summary['text_interactions']}")
        print(f"🎤 Voice interactions: {summary['voice_interactions']}")
        
        # Show frequently used items
        frequent_apps = zeno.memory.get_frequently_used("apps", 3)
        frequent_commands = zeno.memory.get_frequently_used("commands", 3)
        
        print(f"📱 Frequent apps: {frequent_apps}")
        print(f"⚡ Frequent commands: {frequent_commands}")
    else:
        print("Memory system is disabled")

async def demo_skills():
    """Demo skill system"""
    print("\n🛠️  SKILLS SYSTEM DEMO")
    print("=" * 40)
    
    from skills.skill_manager import SkillManager
    
    skill_manager = SkillManager()
    available_skills = skill_manager.get_available_skills()
    
    print(f"Available skills: {len(available_skills)}")
    for skill_name, skill_info in available_skills.items():
        print(f"  • {skill_info['name']}: {skill_info['description']}")

def demo_config():
    """Demo configuration system"""
    print("\n⚙️  CONFIGURATION DEMO")
    print("=" * 40)
    
    print(f"🏠 Base directory: {Config.BASE_DIR}")
    print(f"🧠 Default AI model: {Config.DEFAULT_LOCAL_MODEL}")
    print(f"🎤 Wake word: {Config.WAKE_WORD}")
    print(f"🎯 Default mode: {Config.DEFAULT_MODE}")
    print(f"💾 Memory enabled: {Config.ENABLE_MEMORY}")
    print(f"🎮 PC control enabled: {Config.ENABLE_PC_CONTROL}")
    
    # Check model status
    model_status = Config.get_model_status()
    print(f"🤖 Ollama available: {model_status['ollama_available']}")
    print(f"📦 Local models: {model_status['local_models']}")
    print(f"🔑 API keys configured: {model_status['api_keys']}")

async def main():
    """Main demo function"""
    print("🤖 ZENO Personal AI Assistant - Demo")
    print("=" * 50)
    print("This demo showcases ZENO's core functionality")
    print("For the full experience, run: python app.py")
    print("=" * 50)
    
    # Configuration demo (synchronous)
    demo_config()
    
    # Skills demo (synchronous)  
    demo_skills()
    
    # Memory demo (asynchronous)
    await demo_memory()
    
    # Conversation demo (asynchronous)
    await demo_conversation()
    
    # Control demo (asynchronous)
    await demo_control()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("💡 To start the full web interface:")
    print("   python app.py")
    print("   Then visit: http://localhost:5000")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
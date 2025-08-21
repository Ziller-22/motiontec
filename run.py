#!/usr/bin/env python3
"""
ZENO Personal AI Assistant - Launcher Script
Simple launcher with enhanced error handling and setup validation
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask', 'requests', 'pyttsx3', 'psutil', 'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_ollama():
    """Check if Ollama is available"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print(f"✅ Ollama is running with {len(models)} model(s)")
                return True
            else:
                print("⚠️  Ollama is running but no models are installed")
                print("💡 Install models with: ollama pull phi")
                return True
        else:
            print("⚠️  Ollama is not responding properly")
            return False
    except Exception:
        print("⚠️  Ollama is not running or not accessible")
        print("💡 Start Ollama with: ollama serve")
        return False

def setup_directories():
    """Create necessary directories"""
    directories = [
        "data", "data/models", "data/memory", "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def main():
    """Main launcher function"""
    print("🤖 ZENO Personal AI Assistant - Starting...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check dependencies
    print("📦 Checking dependencies...")
    if not check_dependencies():
        return 1
    
    # Setup directories
    print("📁 Setting up directories...")
    setup_directories()
    
    # Check Ollama
    print("🧠 Checking AI models...")
    ollama_available = check_ollama()
    
    # Environment check
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("💡 Copy .env.example to .env and customize if needed")
    
    print("=" * 50)
    
    if not ollama_available:
        print("⚠️  Warning: ZENO will run with limited AI capabilities")
        print("   Install and start Ollama for full functionality")
        print()
    
    # Start the application
    print("🚀 Starting ZENO...")
    try:
        from app import app
        from config import Config
        
        print(f"🌐 Web interface: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
        print(f"🎯 Default mode: {Config.DEFAULT_MODE}")
        print(f"🎤 Wake word: '{Config.WAKE_WORD}'")
        print()
        print("Press Ctrl+C to stop")
        print("=" * 50)
        
        app.run(
            host=Config.FLASK_HOST,
            port=Config.FLASK_PORT,
            debug=Config.FLASK_DEBUG
        )
        
    except KeyboardInterrupt:
        print("\n👋 ZENO shutting down...")
        return 0
    except Exception as e:
        print(f"❌ Error starting ZENO: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
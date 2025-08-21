#!/usr/bin/env python3
"""
Dance Motion Tracker - Main Application Entry Point

This script starts the Flask web application for the Dance Motion Tracker system.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app
from config.settings import config

def main():
    """Main application entry point"""
    
    # Get configuration from environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create Flask application
    app = create_app(config_name)
    
    # Get host and port from environment or use defaults
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = config_name == 'development'
    
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                  Dance Motion Tracker                        ║
    ║                                                              ║
    ║  A Python-based system for dance motion tracking and        ║
    ║  3D animation using MediaPipe and OpenCV                    ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  Server: http://{host}:{port:<45} ║
    ║  Mode:   {config_name:<49} ║
    ║  Debug:  {debug:<49} ║
    ╚══════════════════════════════════════════════════════════════╝
    
    🎬 Upload your dance videos to extract pose data
    🤖 AI-powered pose detection using MediaPipe
    🎯 Export data for Blender and 3D animation
    📊 Real-time processing with web interface
    
    Press Ctrl+C to stop the server
    """)
    
    try:
        # Start the Flask development server
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,
            use_reloader=debug
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
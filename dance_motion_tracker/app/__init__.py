"""
Flask application factory and configuration
"""
from flask import Flask
from flask_cors import CORS
import os
from pathlib import Path

def create_app(config_name='default'):
    """
    Application factory function
    
    Args:
        config_name: Configuration to use ('development', 'production', 'default')
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Enable CORS for cross-origin requests
    CORS(app)
    
    # Load configuration
    from config.settings import config
    app.config.from_object(config[config_name])
    
    # Ensure upload directory exists
    upload_dir = Path(app.config['UPLOAD_FOLDER'])
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Register blueprints/routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app
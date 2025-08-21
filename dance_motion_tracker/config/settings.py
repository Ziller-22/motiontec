"""
Application configuration settings
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Flask configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    UPLOAD_FOLDER = BASE_DIR / 'app' / 'static' / 'uploads'
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    
    # Video processing settings
    SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    DEFAULT_OUTPUT_FORMAT = 'mp4'
    DEFAULT_FPS = 30
    DEFAULT_RESOLUTION = (1920, 1080)
    
    # Pose detection settings
    POSE_CONFIDENCE_THRESHOLD = 0.5
    POSE_TRACKING_CONFIDENCE = 0.5
    
    # Export settings
    EXPORT_FORMATS = ['csv', 'json']
    DEFAULT_EXPORT_FORMAT = 'json'
    
    # GPU settings
    USE_GPU = os.environ.get('USE_GPU', 'false').lower() == 'true'
    CUDA_DEVICE = os.environ.get('CUDA_DEVICE', '0')

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
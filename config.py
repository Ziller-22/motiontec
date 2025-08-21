"""
ZENO Configuration Management
Centralized configuration for the AI assistant
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Main configuration class for ZENO"""
    
    # Project paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    MODELS_DIR = DATA_DIR / "models" 
    MEMORY_DIR = DATA_DIR / "memory"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Flask settings
    FLASK_HOST = "127.0.0.1"
    FLASK_PORT = 5000
    FLASK_DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY", "zeno-dev-key-change-in-production")
    
    # AI Model settings
    OLLAMA_BASE_URL = "http://localhost:11434"
    DEFAULT_LOCAL_MODEL = "phi"  # phi-2 model via Ollama
    FALLBACK_LOCAL_MODEL = "tinyllama"
    
    # API Keys (optional)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Speech settings
    STT_MODEL = "vosk-model-small-en-us-0.15"  # Vosk model
    TTS_ENGINE = "pyttsx3"  # or "coqui" for advanced TTS
    WAKE_WORD = "zeno"
    WAKE_WORD_THRESHOLD = 0.7
    
    # Assistant modes
    MODES = {
        "conversation": "Natural dialogue and Q&A",
        "control": "PC control with wake word enforcement", 
        "utility": "Multi-step workflows and tasks"
    }
    DEFAULT_MODE = "conversation"
    
    # PC Control settings
    ENABLE_PC_CONTROL = True
    ALLOWED_APPS = [
        "notepad", "calculator", "chrome", "firefox", 
        "explorer", "cmd", "powershell", "code"
    ]
    
    # Memory settings
    ENABLE_MEMORY = True
    MAX_MEMORY_ENTRIES = 1000
    MEMORY_FILE = "user_memory.json"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        for directory in [cls.DATA_DIR, cls.MODELS_DIR, cls.MEMORY_DIR, cls.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_model_status(cls):
        """Check which AI models are available"""
        status = {
            "ollama_available": False,
            "local_models": [],
            "api_keys": {
                "openai": bool(cls.OPENAI_API_KEY),
                "groq": bool(cls.GROQ_API_KEY)
            }
        }
        
        try:
            import requests
            response = requests.get(f"{cls.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                status["ollama_available"] = True
                models_data = response.json()
                status["local_models"] = [model["name"] for model in models_data.get("models", [])]
        except:
            pass
            
        return status
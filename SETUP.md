# 🚀 ZENO Setup Guide

This guide will walk you through setting up ZENO step by step, from basic installation to advanced configuration.

## 📋 Prerequisites

### System Requirements

**Minimum:**
- Windows 10/11 (recommended) or Linux/macOS
- Python 3.8 or higher
- 4GB RAM
- 2GB free disk space

**Recommended:**
- Windows 11
- Python 3.11
- 8GB+ RAM
- NVIDIA GTX 1050 or better (for faster AI models)
- SSD storage
- Microphone for voice input

### Software Dependencies

1. **Python 3.11** (recommended version)
2. **Git** (for cloning repository)
3. **Ollama** (for local AI models)

## 📦 Step 1: Install System Dependencies

### Windows Installation

```powershell
# Install Python 3.11
winget install -e --id Python.Python.3.11

# Install Git
winget install -e --id Git.Git

# Install Ollama
winget install ollama

# Verify installations
python --version
git --version
ollama --version
```

### Linux Installation (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip

# Install Git
sudo apt install git

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Install audio dependencies
sudo apt install portaudio19-dev python3-pyaudio
```

### macOS Installation

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11 git

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Install audio dependencies
brew install portaudio
```

## 📁 Step 2: Clone and Setup ZENO

### Clone Repository

```bash
# Clone the repository
git clone <repository-url> zeno
cd zeno

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### Install Python Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep flask
pip list | grep requests
```

## 🧠 Step 3: Setup AI Models

### Start Ollama Service

```bash
# Start Ollama (if not already running)
ollama serve
```

### Download Recommended Models

```bash
# Primary model: Phi-2 (2.7B parameters)
# Good balance of performance and resource usage
ollama pull phi

# Backup model: TinyLlama (1.1B parameters)  
# Very fast, good for testing
ollama pull tinyllama

# Optional: Larger models (if you have 8GB+ VRAM)
ollama pull llama2:7b
ollama pull codellama:7b
```

### Verify Model Installation

```bash
# List installed models
ollama list

# Test a model
ollama run phi "Hello, how are you?"
```

## 🎤 Step 4: Setup Speech Recognition (Optional)

### Download Vosk Model

1. Visit [Vosk Models](https://alphacephei.com/vosk/models)
2. Download `vosk-model-small-en-us-0.15.zip` (40MB)
3. Extract to `data/models/vosk-model-small-en-us-0.15/`

```bash
# Create directories
mkdir -p data/models

# Download and extract (Linux/macOS)
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip -d data/models/

# Windows PowerShell
Invoke-WebRequest -Uri "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip" -OutFile "vosk-model.zip"
Expand-Archive -Path "vosk-model.zip" -DestinationPath "data\models\"
```

### Test Audio Setup

```python
# Test microphone access
python -c "
import sounddevice as sd
import numpy as np
print('Recording for 2 seconds...')
audio = sd.rec(int(2 * 16000), samplerate=16000, channels=1)
sd.wait()
print('Audio recorded successfully!')
"
```

## ⚙️ Step 5: Configuration

### Create Environment File

Create `.env` file in project root:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000

# Optional: API Keys for fallback models
# OPENAI_API_KEY=sk-your-openai-key-here
# GROQ_API_KEY=your-groq-key-here

# Speech Settings
STT_MODEL=vosk-model-small-en-us-0.15
WAKE_WORD=zeno
WAKE_WORD_THRESHOLD=0.7

# AI Model Preferences
DEFAULT_LOCAL_MODEL=phi
FALLBACK_LOCAL_MODEL=tinyllama
```

### Customize Configuration

Edit `config.py` for advanced settings:

```python
# Modify allowed applications for security
ALLOWED_APPS = [
    "notepad", "calculator", "chrome", "firefox", 
    "explorer", "cmd", "powershell", "code",
    "your-custom-app"  # Add your apps here
]

# Adjust memory settings
MAX_MEMORY_ENTRIES = 1000
ENABLE_MEMORY = True

# Modify speech settings
TTS_ENGINE = "pyttsx3"  # or "coqui" for advanced TTS
```

## 🚀 Step 6: First Run

### Start ZENO

```bash
# Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# Start the application
python app.py
```

You should see output like:
```
🤖 ZENO Personal AI Assistant
🌐 Starting web interface at http://127.0.0.1:5000
📁 Data directory: /path/to/zeno/data
🎯 Current mode: conversation
🎤 Wake word: 'zeno'
```

### Access Web Interface

1. Open your browser
2. Navigate to `http://localhost:5000`
3. You should see the ZENO interface

### Test Basic Functionality

Try these commands:

1. **Text Chat**: "Hello ZENO, what can you do?"
2. **Mode Switch**: "Switch to control mode"
3. **PC Control**: "Zeno, open calculator" (in control mode)
4. **Voice**: Click microphone button and speak

## 🔧 Step 7: Advanced Configuration

### GPU Acceleration (NVIDIA)

If you have an NVIDIA GPU:

```bash
# Check GPU availability
nvidia-smi

# Install CUDA (download from NVIDIA website)
# Verify CUDA installation
nvcc --version

# Test GPU with Ollama
ollama run phi --gpu
```

### Custom Skills Development

Create a custom skill:

```python
# skills/weather_skill.py
from .skill_manager import BaseSkill
import requests

class WeatherSkill(BaseSkill):
    async def execute(self, command: str, parameters: dict):
        city = parameters.get("city", "London")
        # Your weather API integration here
        return self._create_result(True, f"Weather for {city}: Sunny, 22°C")
    
    def get_info(self):
        return {
            "name": "Weather",
            "description": "Get weather information",
            "commands": ["get_weather"],
            "examples": ["Get weather for London"]
        }
```

Register the skill in `skill_manager.py`:

```python
# In _load_skills method
from .weather_skill import WeatherSkill
self.skills["get_weather"] = WeatherSkill()
```

### Memory & Data Management

```python
# Access memory programmatically
from core.memory import MemoryManager

memory = MemoryManager()
summary = memory.get_conversation_summary(hours=24)
print(f"Interactions in last 24h: {summary['total_interactions']}")

# Export memory
exported_file = memory.export_memory()
print(f"Memory exported to: {exported_file}")

# Clear memory (keep preferences)
memory.clear_memory(keep_preferences=True)
```

## 🔍 Troubleshooting

### Common Issues and Solutions

**Issue**: Ollama connection failed
```bash
# Solution: Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it:
ollama serve
```

**Issue**: Speech recognition not working
```bash
# Solution: Install audio dependencies
# Windows:
pip install pyaudio

# Linux:
sudo apt install portaudio19-dev
pip install pyaudio

# macOS:
brew install portaudio
pip install pyaudio
```

**Issue**: PC control commands failing
```bash
# Solution: Install Windows-specific libraries
pip install pyautogui pycaw comtypes

# Run as Administrator for system commands
```

**Issue**: Memory/performance problems
```bash
# Solution: Use lighter models
ollama pull tinyllama
# Update config.py to use tinyllama as default
```

**Issue**: Flask app won't start
```bash
# Check for port conflicts
netstat -an | findstr :5000  # Windows
netstat -an | grep :5000     # Linux/macOS

# Use different port if needed
export FLASK_PORT=5001  # Linux/macOS
set FLASK_PORT=5001     # Windows
```

### Debug Mode

Enable detailed logging:

```python
# In config.py or .env
FLASK_DEBUG=True

# Or set logging level
import logging
logging.basicConfig(level=logging.DEBUG)
```

View application logs:
```bash
# Real-time log viewing
tail -f logs/zeno.log  # Linux/macOS
Get-Content logs\zeno.log -Tail 10 -Wait  # Windows PowerShell
```

### Performance Optimization

**For Low-End Hardware:**
```python
# Use smaller models
DEFAULT_LOCAL_MODEL = "tinyllama"
FALLBACK_LOCAL_MODEL = "tinyllama"

# Reduce memory usage
MAX_MEMORY_ENTRIES = 100
```

**For High-End Hardware:**
```python
# Use larger models
DEFAULT_LOCAL_MODEL = "llama2:7b"
FALLBACK_LOCAL_MODEL = "phi"

# Increase memory
MAX_MEMORY_ENTRIES = 5000
```

## 🔐 Security Considerations

### Production Deployment

```python
# In .env for production
FLASK_DEBUG=False
SECRET_KEY=your-very-secure-random-key-here

# Use environment variables for sensitive data
# Never commit .env files to version control
```

### Firewall Configuration

```bash
# Windows: Allow Python through firewall
netsh advfirewall firewall add rule name="ZENO" dir=in action=allow program="python.exe"

# Linux: Configure UFW
sudo ufw allow 5000/tcp
```

### Access Control

```python
# Restrict allowed applications in config.py
ALLOWED_APPS = [
    "notepad",     # Safe text editor
    "calculator",  # Safe calculator
    # "cmd",       # Comment out risky apps
    # "powershell" # Comment out risky apps
]
```

## ✅ Verification Checklist

After setup, verify these components:

- [ ] Python virtual environment activated
- [ ] All dependencies installed (`pip list`)
- [ ] Ollama service running (`curl http://localhost:11434/api/tags`)
- [ ] At least one AI model downloaded (`ollama list`)
- [ ] Flask app starts without errors
- [ ] Web interface accessible at `http://localhost:5000`
- [ ] Basic chat functionality works
- [ ] Mode switching works
- [ ] PC control commands work (if enabled)
- [ ] Speech recognition works (if configured)
- [ ] TTS works (if configured)

## 🎯 Next Steps

Once ZENO is running:

1. **Explore Modes**: Try conversation, control, and utility modes
2. **Test Voice**: Use the microphone button for voice commands
3. **Customize Skills**: Add your own custom functionality
4. **Configure Preferences**: Adjust settings via the web interface
5. **Monitor Memory**: Check conversation history and preferences
6. **Optimize Performance**: Adjust model settings for your hardware

## 📚 Additional Resources

- **Main Documentation**: `README.md`
- **API Reference**: Check `/api/` endpoints in the web interface
- **Code Examples**: Browse the `skills/` directory
- **Configuration Options**: Review `config.py`
- **Troubleshooting**: Check `logs/zeno.log`

---

**Need Help?** 
- Check the troubleshooting section above
- Review application logs in `logs/zeno.log`
- Ensure all prerequisites are properly installed
- Test each component individually

**Happy AI Assisting with ZENO! 🤖**
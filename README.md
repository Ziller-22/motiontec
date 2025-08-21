# 🤖 ZENO - Personal AI Assistant

**ZENO** is a modular, extensible personal AI assistant designed for Windows that combines the power of local AI models with comprehensive PC control capabilities. Built with Python and Flask, ZENO offers both voice and text interfaces for natural interaction.

![ZENO Screenshot](https://via.placeholder.com/800x400/007bff/ffffff?text=ZENO+Personal+AI+Assistant)

## ✨ Features

### 🎯 Three Operational Modes
- **Conversation Mode**: Natural dialogue and knowledge Q&A
- **Control Mode**: PC control with wake word enforcement ("Zeno")  
- **Utility Mode**: Multi-step workflows and complex tasks

### 🧠 AI Integration
- **Local Models**: Phi-2, TinyLlama via Ollama (privacy-focused)
- **API Fallback**: Optional OpenAI/Groq integration
- **Smart Routing**: Automatic model selection based on availability

### 🎤 Voice & Speech
- **Speech-to-Text**: Vosk-based local recognition
- **Text-to-Speech**: pyttsx3 with customizable voices
- **Wake Word**: "Zeno" activation for system commands

### 💻 PC Control Skills
- **Application Management**: Open/close applications
- **Volume Control**: Set levels, mute/unmute
- **Media Control**: Play, pause, next, previous
- **System Control**: Shutdown, restart, lock, sleep
- **File Operations**: Create, delete, open files/folders
- **Web Search**: Multi-engine search capabilities

### 🧩 Architecture
- **Modular Design**: Easy skill addition and customization
- **Memory System**: User preferences and conversation history
- **Security**: Sandboxed operations with safe directory restrictions
- **Modern UI**: Clean, responsive web interface
- **Cross-Platform**: Windows optimized, Linux/macOS compatible

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (3.11 recommended)
- **Windows 10/11** (for full PC control features)
- **NVIDIA GPU** (optional, for faster local models)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd zeno
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ollama for local AI models:**
   ```bash
   # Windows (using winget)
   winget install ollama
   
   # Or download from: https://ollama.ai
   ```

4. **Download AI models:**
   ```bash
   # Recommended models for GTX 1050
   ollama pull phi        # Phi-2 (2.7B) - balanced performance
   ollama pull tinyllama  # TinyLlama (1.1B) - fastest
   ```

5. **Optional: Download Vosk model for speech recognition:**
   ```bash
   # Download from: https://alphacephei.com/vosk/models
   # Extract to: data/models/vosk-model-small-en-us-0.15/
   ```

### Running ZENO

1. **Start the application:**
   ```bash
   python app.py
   ```

2. **Open your browser:**
   ```
   http://localhost:5000
   ```

3. **Start chatting with ZENO!**

## 📖 Usage Guide

### Basic Interaction

**Text Interface:**
- Type messages in the web interface
- Use natural language for questions and commands
- Switch modes using the dropdown menu

**Voice Interface:**
- Click the microphone button to start/stop recording
- Say "Zeno" before system commands in Control mode
- Voice responses are automatically generated

### Command Examples

**Conversation Mode:**
```
What is machine learning?
Tell me a joke
Explain quantum computing
Switch to control mode
```

**Control Mode (requires "Zeno" prefix):**
```
Zeno, open notepad
Zeno, set volume to 50
Zeno, search for Python tutorials
Zeno, close chrome
Zeno, lock screen
```

**Utility Mode:**
```
Create a project folder structure
Research and summarize AI trends
Set up development environment
Open browser and search for tutorials
```

### Available Skills

| Skill | Commands | Examples |
|-------|----------|----------|
| **PC Control** | open_app, close_app | "Zeno, open calculator" |
| **Volume Control** | volume_control | "Zeno, set volume to 75" |
| **Media Control** | media_control | "Zeno, play music" |
| **Web Search** | web_search | "Zeno, search for weather" |
| **File Operations** | file_operations | "Create file report.txt" |
| **System Control** | system_control | "Zeno, lock screen" |

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Optional API Keys
OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here

# Flask Settings
SECRET_KEY=your_secret_key_here
FLASK_DEBUG=True
```

### Configuration Options

Edit `config.py` to customize:

- **AI Models**: Change default local models
- **Wake Word**: Modify activation phrase
- **Allowed Apps**: Restrict PC control access
- **Memory Settings**: Adjust conversation history limits
- **Speech Settings**: Configure TTS/STT parameters

## 🔧 Advanced Setup

### GPU Acceleration

For NVIDIA GPUs, install CUDA support:

```bash
# Install CUDA toolkit (11.8 or 12.x)
# Download from: https://developer.nvidia.com/cuda-downloads

# Verify GPU access in Ollama
ollama run phi --gpu
```

### Custom Skills

Create new skills by extending `BaseSkill`:

```python
# skills/my_custom_skill.py
from .skill_manager import BaseSkill

class MyCustomSkill(BaseSkill):
    async def execute(self, command: str, parameters: dict):
        # Your custom logic here
        return self._create_result(True, "Custom skill executed")
    
    def get_info(self):
        return {
            "name": "My Custom Skill",
            "description": "Does custom things",
            "commands": ["my_command"],
            "examples": ["Execute my custom command"]
        }
```

Register in `skill_manager.py`:
```python
from .my_custom_skill import MyCustomSkill

# In _load_skills method:
self.skills["my_command"] = MyCustomSkill()
```

### Memory & Preferences

ZENO automatically learns from interactions:

- **Frequently Used Apps**: Tracks most-opened applications
- **Command Patterns**: Learns common command usage
- **User Preferences**: Stores settings and preferences
- **Conversation History**: Maintains context across sessions

Access memory via the web interface or API:
```bash
curl http://localhost:5000/api/memory/summary
```

## 🌐 API Reference

### Chat API
```http
POST /api/chat
Content-Type: application/json

{
    "message": "Hello ZENO"
}
```

### Mode Control
```http
POST /api/mode
Content-Type: application/json

{
    "mode": "conversation"
}
```

### Speech Control
```http
POST /api/speech/start  # Start listening
POST /api/speech/stop   # Stop listening
POST /api/speech/speak  # Text-to-speech
```

### System Status
```http
GET /api/status         # Get system status
GET /api/skills         # Get available skills
POST /api/models/refresh # Refresh AI models
```

## 🔒 Security & Privacy

### Local-First Architecture
- **AI Processing**: Runs locally via Ollama (no data sent to cloud)
- **Speech Recognition**: Local Vosk models (offline capable)
- **Data Storage**: All data stays on your machine

### Security Measures
- **Sandboxed File Operations**: Restricted to safe directories
- **App Control Whitelist**: Only allowed applications can be controlled
- **Wake Word Protection**: System commands require explicit activation
- **API Key Management**: Optional cloud services, never required

### Privacy Features
- **No Telemetry**: No usage data collection
- **Local Memory**: Conversation history stored locally
- **Offline Capable**: Core features work without internet
- **Data Encryption**: Sensitive data can be encrypted at rest

## 🛠️ Troubleshooting

### Common Issues

**Ollama Not Found:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service
ollama serve
```

**Speech Recognition Issues:**
```bash
# Install audio dependencies
pip install sounddevice vosk

# Download Vosk model
# Extract to: data/models/vosk-model-small-en-us-0.15/
```

**PC Control Not Working:**
```bash
# Install Windows-specific dependencies
pip install pyautogui pycaw comtypes

# Run as Administrator for system commands
```

**Memory/Performance Issues:**
```bash
# Use smaller models for limited hardware
ollama pull tinyllama    # 1.1B parameters
ollama pull phi:mini     # Smaller Phi variant
```

### Debug Mode

Enable detailed logging:

```python
# In config.py
FLASK_DEBUG = True
logging.basicConfig(level=logging.DEBUG)
```

View logs:
```bash
tail -f logs/zeno.log
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and test thoroughly
4. **Follow the coding style** (PEP 8 for Python)
5. **Add tests** for new functionality
6. **Update documentation** as needed
7. **Submit a pull request**

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Format code
black . --line-length 100
flake8 .

# Type checking
mypy core/ skills/
```

### Adding New Skills

1. Create skill class in `skills/`
2. Implement `execute()` and `get_info()` methods
3. Register in `skill_manager.py`
4. Add tests in `tests/skills/`
5. Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama** - Local AI model runtime
- **Vosk** - Speech recognition toolkit
- **Flask** - Web framework
- **Bootstrap** - UI components
- **Microsoft** - Phi-2 language model
- **TinyLlama Team** - TinyLlama model

## 📞 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join GitHub Discussions for questions
- **Wiki**: Additional guides and examples

---

**Built with ❤️ for privacy-focused AI assistance**

*ZENO - Your personal AI companion that respects your privacy and enhances your productivity.*
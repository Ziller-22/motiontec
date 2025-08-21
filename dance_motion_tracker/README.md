# 🕺 Dance Motion Tracker

A comprehensive Python-based system for dance motion tracking and 3D animation using MediaPipe, OpenCV, and Flask. Extract pose data from dance videos and create stunning 3D character animations in Blender.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.21-green)
![OpenCV](https://img.shields.io/badge/OpenCV-4.11.0%2B-red)
![Flask](https://img.shields.io/badge/Flask-2.3.0%2B-orange)
![Blender](https://img.shields.io/badge/Blender-3.6%2B-blue)

## ✨ Features

### 🎬 Video Processing
- **Multi-format Support**: MP4, AVI, MOV, MKV, WebM
- **Real-time Processing**: Live pose detection with progress tracking
- **GPU Acceleration**: NVIDIA GPU support for faster processing
- **Quality Optimization**: Automatic video enhancement and preprocessing

### 🤖 AI-Powered Pose Detection
- **MediaPipe Integration**: State-of-the-art pose detection
- **33 Body Landmarks**: Full body tracking including hands and face
- **High Accuracy**: Optimized for dance and performance movements
- **Confidence Scoring**: Quality assessment for each detected pose

### 📊 Data Processing & Export
- **Multiple Formats**: JSON, CSV, Blender-compatible exports
- **Smoothing Algorithms**: Kalman filters and Savitzky-Golay smoothing
- **Statistical Analysis**: Comprehensive motion analysis reports
- **Batch Processing**: Handle multiple videos efficiently

### 🌐 Web Interface
- **Modern UI**: Beautiful, responsive web interface
- **Real-time Feedback**: Live processing updates and progress bars
- **Drag & Drop**: Easy video upload with validation
- **Preview System**: Visualize results before download

### 🎭 3D Animation Integration
- **Blender Addon**: Direct import into Blender 3.6+
- **Rig Compatibility**: Mixamo, Rigify, UE4, and custom rigs
- **Auto-retargeting**: Automatic bone mapping and animation transfer
- **Animation Tools**: Smoothing, optimization, and enhancement utilities

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **NVIDIA GPU** (optional, for acceleration)
- **Blender 3.6+** (for 3D integration)
- **FFmpeg** (optional, for video conversion)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/dance-motion-tracker.git
   cd dance-motion-tracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # Basic installation
   pip install -r requirements.txt
   
   # GPU acceleration (optional)
   pip install -r requirements-gpu.txt
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 📖 Usage

### Web Interface

1. **Upload Video**: Drag and drop your dance video or click to browse
2. **Configure Options**: 
   - Enable pose smoothing for better results
   - Select export formats (JSON, CSV, Blender)
   - Choose to create overlay video
3. **Process**: Click "Start Processing" and monitor progress
4. **Download**: Get your processed data and visualization

### Command Line

```python
from core.pose_detector import PoseDetector
from core.data_exporter import DataExporter
from core.smoothing import PoseSmoothing

# Initialize components
detector = PoseDetector()
smoother = PoseSmoothing()
exporter = DataExporter()

# Process video
poses = detector.process_video('dance_video.mp4')
smoothed_poses = smoother.apply_combined_smoothing(poses)

# Export results
exporter.export_to_json(smoothed_poses, 'pose_data.json')
exporter.export_for_blender(smoothed_poses, 'blender_data.json')
```

### Blender Integration

1. **Install Addon**: Import `blender/import_pose_data.py` in Blender
2. **Import Data**: File → Import → Dance Motion Data
3. **Apply to Character**: Use automatic rig detection and retargeting
4. **Enhance**: Apply smoothing, constraints, and optimizations

## 🏗️ Architecture

```
dance_motion_tracker/
├── app/                    # Flask web application
│   ├── routes.py          # API endpoints
│   ├── templates/         # HTML templates
│   └── static/           # CSS, JS, uploads
├── core/                  # Core processing modules
│   ├── pose_detector.py  # MediaPipe integration
│   ├── video_processor.py # Video I/O and processing
│   ├── data_exporter.py  # Export functionality
│   ├── smoothing.py      # Filtering algorithms
│   └── visualizer.py     # Pose visualization
├── blender/              # Blender integration
│   ├── import_pose_data.py # Blender addon
│   ├── rig_mapper.py     # Rig compatibility
│   └── animation_utils.py # Animation tools
├── config/               # Configuration
├── docs/                 # Documentation
├── tests/                # Unit tests
└── examples/             # Sample files
```

## 🔧 Configuration

### Environment Variables

```bash
# Flask settings
FLASK_ENV=development
SECRET_KEY=your-secret-key

# GPU settings
USE_GPU=true
CUDA_DEVICE=0

# Processing settings
MAX_UPLOAD_SIZE=500MB
DEFAULT_FPS=30
```

### MediaPipe Settings

Customize pose detection in `config/mediapipe_config.py`:

```python
MEDIAPIPE_CONFIG = {
    'model_complexity': 1,  # 0-2, higher = more accurate
    'min_detection_confidence': 0.5,
    'min_tracking_confidence': 0.5,
    'enable_segmentation': False,
}
```

## 📚 Documentation

- **[Setup Guide](docs/setup.md)** - Complete installation instructions
- **[Usage Guide](docs/usage.md)** - Detailed usage examples
- **[API Documentation](docs/api.md)** - REST API reference
- **[Blender Integration](docs/blender_integration.md)** - 3D animation workflow

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python tests/run_tests.py

# Run specific test module
python tests/run_tests.py test_pose_detector

# Run with coverage
pip install pytest-cov
pytest --cov=core tests/
```

## 🎯 Use Cases

### 🎭 Dance & Performance
- **Choreography Analysis**: Study and analyze dance movements
- **Performance Capture**: Convert live performances to 3D animation
- **Training Tools**: Create educational content for dance instruction
- **Motion Studies**: Research human movement patterns

### 🎮 Game Development
- **Character Animation**: Create realistic character movements
- **Motion Libraries**: Build reusable animation assets
- **Procedural Animation**: Generate dynamic character behaviors
- **Mocap Alternative**: Cost-effective motion capture solution

### 🎬 Film & Media
- **Pre-visualization**: Plan complex scenes and sequences
- **Animation Reference**: Guide animators with real motion data
- **VFX Integration**: Combine real and digital performances
- **Content Creation**: Streamline animation production pipelines

### 🏥 Healthcare & Research
- **Movement Analysis**: Study human biomechanics and gait
- **Rehabilitation**: Track patient progress and movement quality
- **Sports Science**: Analyze athletic performance and technique
- **Ergonomics**: Evaluate workplace movements and postures

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `python tests/run_tests.py`
5. Submit a pull request

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write comprehensive docstrings
- Add unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MediaPipe Team** - For the incredible pose detection technology
- **OpenCV Community** - For computer vision tools and libraries  
- **Blender Foundation** - For the amazing 3D creation suite
- **Flask Team** - For the lightweight web framework
- **Dance Community** - For inspiration and feedback

## 📞 Support

- **Documentation**: Check our [comprehensive docs](docs/)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/dance-motion-tracker/issues)
- **Discussions**: Join our [community discussions](https://github.com/yourusername/dance-motion-tracker/discussions)
- **Email**: Contact us at support@dancemotiontracker.com

## 🗺️ Roadmap

### Version 2.0 (Coming Soon)
- [ ] Real-time camera input processing
- [ ] Multi-person pose tracking
- [ ] Advanced AI pose prediction
- [ ] Cloud processing capabilities
- [ ] Mobile app integration

### Version 2.1
- [ ] Hand and finger detail tracking
- [ ] Facial expression capture
- [ ] Custom ML model training
- [ ] Advanced physics simulation
- [ ] VR/AR integration

### Long-term Goals
- [ ] Real-time motion streaming
- [ ] Collaborative animation tools
- [ ] Advanced biomechanics analysis
- [ ] Integration with major 3D software
- [ ] Professional mocap studio features

---

<div align="center">

**⭐ Star this project if you find it useful!**

Made with ❤️ by the Dance Motion Tracker team

[Website](https://dancemotiontracker.com) • [Documentation](docs/) • [Examples](examples/) • [Community](https://github.com/yourusername/dance-motion-tracker/discussions)

</div>
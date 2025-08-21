# Dance Motion Tracker - Setup Guide

This guide will help you set up the Dance Motion Tracker system on your local machine.

## System Requirements

### Hardware Requirements
- **GPU**: NVIDIA GTX 1050 or better (recommended for optimal performance)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 5GB free space minimum
- **Camera**: Any USB webcam or video files (1080p recommended)

### Software Requirements
- **Python**: 3.9, 3.10, or 3.11
- **Operating System**: Windows 10/11, macOS 10.15+, or Ubuntu 18.04+
- **Blender**: 3.6+ (for 3D animation integration)
- **FFmpeg**: For video processing (optional but recommended)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd dance_motion_tracker
```

### 2. Create Virtual Environment

```bash
# Using venv (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

#### Basic Installation (CPU Only)
```bash
pip install -r requirements.txt
```

#### GPU Installation (NVIDIA GPU)
```bash
pip install -r requirements-gpu.txt
```

### 4. Verify Installation

Run the verification script to check if all dependencies are installed correctly:

```bash
python -c "
import cv2
import mediapipe
import flask
import numpy
import pandas
print('All dependencies installed successfully!')
print(f'OpenCV version: {cv2.__version__}')
print(f'MediaPipe version: {mediapipe.__version__}')
print(f'Flask version: {flask.__version__}')
"
```

### 5. Install FFmpeg (Optional but Recommended)

#### Windows
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH

#### macOS
```bash
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

### 6. GPU Setup (Optional)

If you have an NVIDIA GPU and want to use GPU acceleration:

#### Check CUDA Installation
```bash
nvidia-smi  # Should show GPU information
nvcc --version  # Should show CUDA version
```

#### Install CUDA (if not installed)
1. Visit https://developer.nvidia.com/cuda-downloads
2. Download and install CUDA 11.8 or 12.x
3. Restart your system

#### Verify GPU Setup
```bash
python -c "
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU device: {torch.cuda.get_device_name(0)}')
"
```

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
# Flask configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# GPU configuration
USE_GPU=true
CUDA_DEVICE=0

# Upload settings
MAX_UPLOAD_SIZE=500MB
UPLOAD_FOLDER=./uploads

# Processing settings
DEFAULT_FPS=30
DEFAULT_RESOLUTION=1920x1080
```

### 2. Application Settings

Edit `config/settings.py` to customize:

- Upload file size limits
- Supported video formats
- Processing parameters
- Export settings

## Running the Application

### 1. Start the Web Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

### 2. Development Mode

For development with auto-reload:

```bash
export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
python run.py
```

### 3. Production Deployment

For production deployment, consider using:

- **Gunicorn** (Linux/macOS):
  ```bash
  pip install gunicorn
  gunicorn -w 4 -b 0.0.0.0:5000 run:app
  ```

- **Waitress** (Windows):
  ```bash
  pip install waitress
  waitress-serve --host=0.0.0.0 --port=5000 run:app
  ```

## Blender Integration Setup

### 1. Install Blender Addon

1. Open Blender (3.6+)
2. Go to Edit → Preferences → Add-ons
3. Click "Install..." and select `blender/import_pose_data.py`
4. Enable the "Dance Motion Tracker Importer" addon

### 2. Verify Blender Integration

1. Go to File → Import → Dance Motion Data
2. The import dialog should appear
3. Test with sample pose data files

## Troubleshooting

### Common Issues

#### MediaPipe Installation Issues
```bash
# If MediaPipe fails to install
pip install --upgrade pip setuptools wheel
pip install mediapipe==0.10.21 --no-cache-dir
```

#### OpenCV Import Error
```bash
# If OpenCV import fails
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python>=4.11.0
```

#### GPU Not Detected
1. Verify NVIDIA drivers are installed
2. Check CUDA installation: `nvcc --version`
3. Reinstall PyTorch with CUDA support:
   ```bash
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

#### Memory Issues
- Reduce video resolution before processing
- Close other applications
- Increase virtual memory/swap space

#### Slow Processing
- Enable GPU acceleration
- Reduce MediaPipe model complexity
- Process shorter video segments

### Performance Optimization

#### For Better Performance
1. **Use GPU acceleration** when available
2. **Reduce video resolution** to 720p for faster processing
3. **Lower MediaPipe model complexity** in `config/mediapipe_config.py`
4. **Process videos in segments** for very long videos

#### Memory Management
- Monitor system memory usage during processing
- Clear browser cache regularly
- Restart the application if memory usage grows too high

### Getting Help

If you encounter issues:

1. Check the logs in the console output
2. Verify all dependencies are correctly installed
3. Test with the provided sample videos
4. Check the GitHub issues page for known problems

## Next Steps

Once setup is complete:

1. Read the [Usage Guide](usage.md) to learn how to use the system
2. Check the [API Documentation](api.md) for programmatic access
3. Review [Blender Integration](blender_integration.md) for 3D animation workflow

## System Architecture

```
dance_motion_tracker/
├── app/                    # Flask web application
├── core/                   # Core processing modules
├── blender/               # Blender integration scripts
├── config/                # Configuration files
├── docs/                  # Documentation
├── tests/                 # Test scripts
└── examples/              # Sample files
```

For detailed architecture information, see the project structure documentation.
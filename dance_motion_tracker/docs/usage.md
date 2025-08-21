# Dance Motion Tracker - Usage Guide

This guide explains how to use the Dance Motion Tracker system to extract pose data from dance videos and create 3D animations.

## Overview

The Dance Motion Tracker system provides:
1. **Video Upload**: Upload dance videos for analysis
2. **Pose Detection**: Extract body joint positions using MediaPipe
3. **Data Processing**: Apply smoothing and filtering to pose data
4. **Export Options**: Save data in multiple formats (JSON, CSV, Blender)
5. **Visualization**: Create videos with pose overlays
6. **3D Integration**: Import data into Blender for character animation

## Web Interface Usage

### 1. Starting the Application

```bash
python run.py
```

Open your web browser and navigate to `http://localhost:5000`

### 2. Upload Video

#### Supported Formats
- **MP4** (recommended)
- **AVI**
- **MOV**
- **MKV**
- **WebM**

#### Requirements
- **File size**: Up to 500MB
- **Resolution**: Any, but 1080p recommended for best results
- **Duration**: Any, but longer videos take more time to process
- **Content**: Clear visibility of the dancer, minimal background clutter

#### Upload Process
1. Click "Choose File" or drag and drop your video
2. The system will validate the file and show video information
3. Video details (resolution, duration, frame rate) will be displayed

### 3. Configure Processing Options

#### Smoothing Options
- **Apply Pose Smoothing**: Reduces jitter in tracking data
  - **Combined**: Uses both Kalman and Savitzky-Golay filters (recommended)
  - **Kalman Filter**: Good for real-time-like smoothing
  - **Savitzky-Golay**: Better for preserving motion details

#### Export Formats
- **JSON**: Complete pose data with metadata
- **CSV**: Spreadsheet-compatible format
- **Blender Compatible**: Optimized for 3D animation import

#### Video Options
- **Create Overlay Video**: Generates video with pose visualization
- **Include Statistics**: Creates analysis report

### 4. Process Video

1. Click "Start Processing"
2. Monitor progress in real-time
3. Processing time depends on:
   - Video length and resolution
   - Hardware capabilities (GPU vs CPU)
   - Selected options

#### Processing Stages
1. **Video Analysis**: Extracting frames and metadata
2. **Pose Detection**: MediaPipe analysis of each frame
3. **Data Smoothing**: Applying selected filters
4. **Export Generation**: Creating output files
5. **Visualization**: Generating overlay video (if selected)

### 5. Download Results

After processing completes, download:
- **JSON Data**: Complete pose information
- **CSV Data**: Tabular format for analysis
- **Blender Data**: Ready for 3D animation
- **Overlay Video**: Visualization of detected poses
- **Statistics**: Analysis report and metrics

## Command Line Usage

### Basic Processing

```bash
# Process a video with default settings
python -c "
from core.pose_detector import PoseDetector
from core.data_exporter import DataExporter

detector = PoseDetector()
exporter = DataExporter()

# Process video
poses = detector.process_video('input_video.mp4', 'output_with_overlay.mp4')

# Export data
exporter.export_to_json(poses, 'pose_data.json')
exporter.export_for_blender(poses, 'blender_data.json')
"
```

### Advanced Processing with Smoothing

```python
from core.pose_detector import PoseDetector
from core.smoothing import PoseSmoothing
from core.data_exporter import DataExporter

# Initialize components
detector = PoseDetector(model_complexity=2, min_detection_confidence=0.7)
smoother = PoseSmoothing()
exporter = DataExporter()

# Process video
print("Detecting poses...")
poses = detector.process_video('dance_video.mp4')

# Apply smoothing
print("Applying smoothing...")
smoothed_poses = smoother.apply_combined_smoothing(poses)

# Export results
print("Exporting data...")
exporter.export_to_json(smoothed_poses, 'smoothed_poses.json')
exporter.export_for_blender(smoothed_poses, 'blender_animation.json')
exporter.export_summary_stats(smoothed_poses, 'analysis_stats.json')

print("Processing complete!")
```

## Blender Integration

### 1. Install Blender Addon

1. Open Blender 3.6+
2. Edit → Preferences → Add-ons
3. Install → Select `blender/import_pose_data.py`
4. Enable "Dance Motion Tracker Importer"

### 2. Import Pose Data

1. File → Import → Dance Motion Data
2. Select your exported `.json` file
3. Choose import options:
   - **Create Armature**: Generate bone structure
   - **Create Visualization**: Add mesh representation

### 3. Working with Imported Data

#### Armature Animation
- The imported armature contains keyframe animation
- Use timeline to scrub through the motion
- Bones are named according to MediaPipe landmarks

#### Retargeting to Character Rigs
```python
# In Blender's Python console
import bpy
from rig_mapper import RigMapper

# Auto-detect rig type and retarget
mapper = RigMapper()
source_armature = bpy.data.objects['PoseArmature']
target_armature = bpy.data.objects['CharacterRig']

# Create retarget constraints
mapper.create_retarget_constraints(source_armature, target_armature, 'mixamo')

# Bake animation to target rig
mapper.bake_retargeted_animation(target_armature, 1, 250)
```

## Best Practices

### Video Recording Tips

#### Lighting
- Use even, bright lighting
- Avoid harsh shadows
- Ensure dancer is well-lit from front

#### Camera Setup
- Use tripod for stable recording
- Position camera to capture full body
- Maintain consistent distance from subject
- Record at 30+ FPS for smooth motion

#### Background
- Use plain, contrasting background
- Avoid busy patterns or moving objects
- Ensure good contrast with dancer's clothing

#### Performance
- Wear fitted clothing for better tracking
- Avoid loose, flowing garments when possible
- Ensure full body is visible in most frames
- Perform movements clearly and deliberately

### Processing Optimization

#### For Best Quality
- Use highest quality video available
- Enable all smoothing options
- Set MediaPipe model complexity to 2
- Process in segments for very long videos

#### For Speed
- Reduce video resolution to 720p
- Use model complexity 0 or 1
- Disable overlay video creation
- Process shorter segments

### Data Usage

#### JSON Format Structure
```json
{
  "format_version": "1.0",
  "total_frames": 1500,
  "metadata": {
    "fps": 30,
    "duration": 50.0,
    "image_width": 1920,
    "image_height": 1080
  },
  "pose_data": [
    {
      "frame_index": 0,
      "timestamp": 0.0,
      "landmarks": [
        {
          "name": "NOSE",
          "x": 960.5,
          "y": 200.3,
          "z": -50.2,
          "visibility": 0.98
        }
      ]
    }
  ]
}
```

#### CSV Format
- **Wide format**: One row per frame, columns for each landmark coordinate
- **Long format**: One row per landmark per frame

## Troubleshooting

### Common Issues

#### Poor Pose Detection
- **Cause**: Low lighting, cluttered background, or low video quality
- **Solution**: Improve video quality, use better lighting, try different MediaPipe settings

#### Jittery Animation
- **Cause**: Tracking noise or insufficient smoothing
- **Solution**: Enable smoothing, try different smoothing methods, increase smoothing strength

#### Missing Poses in Some Frames
- **Cause**: Occlusion, motion blur, or pose complexity
- **Solution**: Use interpolation, manual cleanup, or re-record problematic sections

#### Slow Processing
- **Cause**: Large video files, high resolution, or CPU-only processing
- **Solution**: Reduce video size, enable GPU acceleration, process in segments

### Performance Tips

#### Memory Management
- Close other applications during processing
- Process videos in shorter segments
- Reduce video resolution if needed
- Clear browser cache regularly

#### GPU Utilization
- Ensure CUDA is properly installed
- Check GPU memory usage
- Use appropriate model complexity for your hardware

## Advanced Features

### Custom Rig Mapping

Create custom bone mappings for specific character rigs:

```python
from blender.rig_mapper import RigMapper

mapper = RigMapper()

# Create custom mapping
custom_mapping = {
    'HEAD': 'MyRig_Head',
    'LEFT_SHOULDER': 'MyRig_L_Shoulder',
    # ... add more mappings
}

# Apply to armature
mapper.map_pose_to_rig(pose_data, armature, custom_mapping)
```

### Batch Processing

Process multiple videos automatically:

```python
import os
from pathlib import Path

video_folder = Path('input_videos')
output_folder = Path('output_data')

for video_file in video_folder.glob('*.mp4'):
    print(f"Processing {video_file.name}...")
    
    # Process video
    poses = detector.process_video(str(video_file))
    
    # Export results
    output_name = video_file.stem
    exporter.export_to_json(poses, output_folder / f'{output_name}.json')
    exporter.export_for_blender(poses, output_folder / f'{output_name}_blender.json')
```

### API Integration

Use the REST API for programmatic access:

```python
import requests

# Upload video
files = {'video': open('dance.mp4', 'rb')}
response = requests.post('http://localhost:5000/upload', files=files)
session_id = response.json()['session_id']

# Start processing
options = {
    'apply_smoothing': True,
    'export_formats': ['json', 'blender']
}
requests.post(f'http://localhost:5000/process/{session_id}', json=options)

# Check status
status = requests.get(f'http://localhost:5000/status/{session_id}').json()
```

## Next Steps

- Explore the [API Documentation](api.md) for programmatic usage
- Learn about [Blender Integration](blender_integration.md) for advanced 3D workflows
- Check out example projects and tutorials
- Join the community for tips and shared experiences
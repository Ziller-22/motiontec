# Dance Motion Tracking Project Structure

```
dance_motion_tracker/
├── app/                           # Flask web application
│   ├── __init__.py
│   ├── routes.py                  # Web routes and API endpoints
│   ├── templates/                 # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   └── results.html
│   ├── static/                    # CSS, JS, and uploaded files
│   │   ├── css/
│   │   ├── js/
│   │   └── uploads/
│   └── utils.py                   # Helper functions for web app
├── core/                          # Core processing modules
│   ├── __init__.py
│   ├── pose_detector.py           # MediaPipe pose detection
│   ├── video_processor.py         # Video I/O and processing
│   ├── data_exporter.py          # Export to CSV/JSON
│   ├── smoothing.py              # Kalman and Savitzky-Golay filters
│   └── visualizer.py             # Overlay joint visualization
├── blender/                       # Blender integration scripts
│   ├── import_pose_data.py        # Import and apply pose data
│   ├── rig_mapper.py             # Map poses to different rigs
│   └── animation_utils.py         # Animation helper functions
├── config/                        # Configuration files
│   ├── __init__.py
│   ├── settings.py               # Application settings
│   └── mediapipe_config.py       # MediaPipe configuration
├── tests/                         # Unit and integration tests
│   ├── __init__.py
│   ├── test_pose_detector.py
│   ├── test_video_processor.py
│   └── test_data_export.py
├── docs/                          # Documentation
│   ├── setup.md                  # Environment setup
│   ├── usage.md                  # Usage instructions
│   ├── api.md                    # API documentation
│   └── blender_integration.md    # Blender workflow
├── examples/                      # Example videos and outputs
│   ├── sample_videos/
│   └── sample_outputs/
├── requirements.txt               # Python dependencies
├── requirements-gpu.txt          # GPU-specific dependencies
├── setup.py                      # Package setup
├── run.py                        # Application entry point
└── README.md                     # Project overview
```
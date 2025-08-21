# Dance Motion Tracker - API Documentation

This document describes the REST API endpoints for the Dance Motion Tracker system.

## Base URL

```
http://localhost:5000
```

## Authentication

Currently, the API does not require authentication. For production deployment, consider implementing proper authentication mechanisms.

## API Endpoints

### Health Check

#### GET /health

Check if the API is running and get system status.

**Response:**
```json
{
  "status": "healthy",
  "active_sessions": 2
}
```

### Video Upload

#### POST /upload

Upload a video file for processing.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Form data with video file

**Form Parameters:**
- `video`: Video file (required)

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "video_info": {
    "width": 1920,
    "height": 1080,
    "fps": 30.0,
    "frame_count": 1500,
    "duration": 50.0,
    "format": ".mp4"
  },
  "message": "Video uploaded successfully"
}
```

**Error Responses:**
- `400`: No video file provided, invalid format, or file too large
- `500`: Server error during upload

### Start Processing

#### POST /process/{session_id}

Start pose detection and processing for an uploaded video.

**Path Parameters:**
- `session_id`: Session ID from upload response

**Request Body:**
```json
{
  "apply_smoothing": true,
  "smoothing_method": "combined",
  "create_overlay_video": true,
  "export_formats": ["json", "csv", "blender"]
}
```

**Request Parameters:**
- `apply_smoothing` (boolean): Whether to apply pose smoothing
- `smoothing_method` (string): Smoothing method ("combined", "kalman", "savgol")
- `create_overlay_video` (boolean): Whether to create overlay video
- `export_formats` (array): List of export formats

**Response:**
```json
{
  "message": "Processing completed successfully",
  "frames_processed": 1500,
  "output_files": ["json", "blender", "overlay_video", "statistics"]
}
```

**Error Responses:**
- `404`: Session not found
- `400`: Video not ready for processing or invalid options
- `500`: Processing error

### Get Status

#### GET /status/{session_id}

Get the current processing status for a session.

**Path Parameters:**
- `session_id`: Session ID

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "video_info": {
    "width": 1920,
    "height": 1080,
    "fps": 30.0,
    "frame_count": 1500,
    "duration": 50.0
  },
  "output_files": ["json", "blender", "overlay_video", "statistics"],
  "pose_stats": {
    "total_frames": 1500,
    "avg_confidence": 0.85,
    "duration": 50.0
  }
}
```

**Status Values:**
- `uploaded`: Video uploaded, ready for processing
- `processing`: Currently processing video
- `completed`: Processing completed successfully
- `failed`: Processing failed

**Error Responses:**
- `404`: Session not found

### Download Files

#### GET /download/{session_id}/{file_type}

Download processed files.

**Path Parameters:**
- `session_id`: Session ID
- `file_type`: Type of file to download

**File Types:**
- `json`: Complete pose data in JSON format
- `csv`: Pose data in CSV format
- `blender`: Blender-compatible animation data
- `overlay_video`: Video with pose overlays
- `statistics`: Analysis statistics

**Response:**
- Content-Type: Varies by file type
- Content-Disposition: attachment; filename="..."
- Body: File content

**Error Responses:**
- `404`: Session or file not found

### Get Preview

#### GET /preview/{session_id}

Get preview data for visualization.

**Path Parameters:**
- `session_id`: Session ID

**Response:**
```json
{
  "preview_data": [
    {
      "frame_index": 0,
      "timestamp": 0.0,
      "confidence": 0.95,
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
  ],
  "video_info": {
    "width": 1920,
    "height": 1080,
    "fps": 30.0
  },
  "total_frames": 1500
}
```

**Error Responses:**
- `404`: Session not found
- `400`: No data available for preview

### Cleanup Session

#### DELETE /cleanup/{session_id}

Clean up session files and data.

**Path Parameters:**
- `session_id`: Session ID

**Response:**
```json
{
  "message": "Session cleaned up successfully"
}
```

**Error Responses:**
- `404`: Session not found
- `500`: Cleanup failed

## Data Formats

### Pose Data JSON Format

```json
{
  "format_version": "1.0",
  "export_timestamp": "2024-01-15T10:30:00",
  "total_frames": 1500,
  "metadata": {
    "image_width": 1920,
    "image_height": 1080,
    "landmark_count": 33,
    "duration": 50.0,
    "fps": 30.0
  },
  "pose_data": [
    {
      "frame_index": 0,
      "timestamp": 0.0,
      "detection_confidence": 0.95,
      "landmarks": [
        {
          "name": "NOSE",
          "x": 960.5,
          "y": 200.3,
          "z": -50.2,
          "visibility": 0.98
        },
        {
          "name": "LEFT_EYE_INNER",
          "x": 945.2,
          "y": 185.7,
          "z": -48.1,
          "visibility": 0.92
        }
      ]
    }
  ]
}
```

### Blender Data Format

```json
{
  "format": "blender_pose_data",
  "version": "1.0",
  "rig_type": "mixamo",
  "export_info": {
    "timestamp": "2024-01-15T10:30:00",
    "total_frames": 1500,
    "fps": 30.0,
    "frame_start": 1,
    "frame_end": 1500
  },
  "bone_mapping": {
    "HEAD": "NOSE",
    "LEFT_SHOULDER": "LEFT_SHOULDER"
  },
  "animation_data": [
    {
      "frame": 1,
      "timestamp": 0.0,
      "bones": {
        "HEAD": {
          "location": [0.0, 0.0, 1.8],
          "rotation": [0.0, 0.0, 0.0],
          "scale": [1.0, 1.0, 1.0],
          "visibility": 0.98
        }
      }
    }
  ]
}
```

### CSV Format (Wide)

```csv
frame_index,timestamp,detection_confidence,NOSE_x,NOSE_y,NOSE_z,NOSE_visibility,LEFT_EYE_x,LEFT_EYE_y,LEFT_EYE_z,LEFT_EYE_visibility
0,0.0,0.95,960.5,200.3,-50.2,0.98,945.2,185.7,-48.1,0.92
1,0.033,0.94,961.1,201.0,-49.8,0.97,945.8,186.2,-47.9,0.91
```

### CSV Format (Long)

```csv
frame_index,timestamp,detection_confidence,landmark_name,x,y,z,visibility
0,0.0,0.95,NOSE,960.5,200.3,-50.2,0.98
0,0.0,0.95,LEFT_EYE,945.2,185.7,-48.1,0.92
1,0.033,0.94,NOSE,961.1,201.0,-49.8,0.97
1,0.033,0.94,LEFT_EYE,945.8,186.2,-47.9,0.91
```

## Python Client Example

```python
import requests
import json
import time

class DanceMotionTrackerClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def upload_video(self, video_path):
        """Upload a video file"""
        with open(video_path, 'rb') as f:
            files = {'video': f}
            response = requests.post(f"{self.base_url}/upload", files=files)
            response.raise_for_status()
            return response.json()
    
    def start_processing(self, session_id, options=None):
        """Start video processing"""
        if options is None:
            options = {
                'apply_smoothing': True,
                'smoothing_method': 'combined',
                'create_overlay_video': True,
                'export_formats': ['json', 'blender']
            }
        
        response = requests.post(
            f"{self.base_url}/process/{session_id}", 
            json=options
        )
        response.raise_for_status()
        return response.json()
    
    def get_status(self, session_id):
        """Get processing status"""
        response = requests.get(f"{self.base_url}/status/{session_id}")
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(self, session_id, poll_interval=2):
        """Wait for processing to complete"""
        while True:
            status = self.get_status(session_id)
            if status['status'] == 'completed':
                return status
            elif status['status'] == 'failed':
                raise Exception("Processing failed")
            time.sleep(poll_interval)
    
    def download_file(self, session_id, file_type, output_path):
        """Download a processed file"""
        response = requests.get(
            f"{self.base_url}/download/{session_id}/{file_type}"
        )
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
    
    def cleanup_session(self, session_id):
        """Clean up session"""
        response = requests.delete(f"{self.base_url}/cleanup/{session_id}")
        response.raise_for_status()
        return response.json()

# Usage example
client = DanceMotionTrackerClient()

# Upload video
upload_result = client.upload_video("dance_video.mp4")
session_id = upload_result['session_id']

# Start processing
processing_options = {
    'apply_smoothing': True,
    'smoothing_method': 'combined',
    'export_formats': ['json', 'blender']
}
client.start_processing(session_id, processing_options)

# Wait for completion
final_status = client.wait_for_completion(session_id)
print(f"Processing completed: {final_status}")

# Download results
client.download_file(session_id, 'json', 'pose_data.json')
client.download_file(session_id, 'blender', 'blender_data.json')

# Clean up
client.cleanup_session(session_id)
```

## JavaScript Client Example

```javascript
class DanceMotionTrackerClient {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
    }

    async uploadVideo(videoFile) {
        const formData = new FormData();
        formData.append('video', videoFile);

        const response = await fetch(`${this.baseUrl}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }

        return await response.json();
    }

    async startProcessing(sessionId, options = {}) {
        const defaultOptions = {
            apply_smoothing: true,
            smoothing_method: 'combined',
            create_overlay_video: true,
            export_formats: ['json', 'blender']
        };

        const response = await fetch(`${this.baseUrl}/process/${sessionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ...defaultOptions, ...options })
        });

        if (!response.ok) {
            throw new Error(`Processing failed: ${response.statusText}`);
        }

        return await response.json();
    }

    async getStatus(sessionId) {
        const response = await fetch(`${this.baseUrl}/status/${sessionId}`);
        
        if (!response.ok) {
            throw new Error(`Status check failed: ${response.statusText}`);
        }

        return await response.json();
    }

    async waitForCompletion(sessionId, pollInterval = 2000) {
        while (true) {
            const status = await this.getStatus(sessionId);
            
            if (status.status === 'completed') {
                return status;
            } else if (status.status === 'failed') {
                throw new Error('Processing failed');
            }
            
            await new Promise(resolve => setTimeout(resolve, pollInterval));
        }
    }

    getDownloadUrl(sessionId, fileType) {
        return `${this.baseUrl}/download/${sessionId}/${fileType}`;
    }

    async cleanupSession(sessionId) {
        const response = await fetch(`${this.baseUrl}/cleanup/${sessionId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`Cleanup failed: ${response.statusText}`);
        }

        return await response.json();
    }
}

// Usage example
const client = new DanceMotionTrackerClient();

async function processVideo(videoFile) {
    try {
        // Upload video
        const uploadResult = await client.uploadVideo(videoFile);
        const sessionId = uploadResult.session_id;

        // Start processing
        await client.startProcessing(sessionId, {
            apply_smoothing: true,
            export_formats: ['json', 'blender']
        });

        // Wait for completion
        const finalStatus = await client.waitForCompletion(sessionId);
        console.log('Processing completed:', finalStatus);

        // Create download links
        const downloadLinks = {
            json: client.getDownloadUrl(sessionId, 'json'),
            blender: client.getDownloadUrl(sessionId, 'blender')
        };

        return { sessionId, downloadLinks };

    } catch (error) {
        console.error('Error processing video:', error);
        throw error;
    }
}
```

## Error Handling

### Error Response Format

```json
{
  "error": "Error message description",
  "details": "Additional error details (optional)"
}
```

### Common Error Codes

- **400 Bad Request**: Invalid request parameters or data
- **404 Not Found**: Session or resource not found
- **413 Payload Too Large**: File size exceeds limit
- **415 Unsupported Media Type**: Invalid file format
- **500 Internal Server Error**: Server processing error

### Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing rate limiting based on:
- Requests per minute per IP
- Concurrent processing sessions per user
- File upload frequency

## Security Considerations

### Production Deployment

For production deployment, implement:

1. **Authentication**: User authentication and session management
2. **Authorization**: Role-based access control
3. **Input Validation**: Strict file type and size validation
4. **HTTPS**: Encrypted communication
5. **CORS**: Proper cross-origin resource sharing configuration
6. **File Scanning**: Malware scanning for uploaded files
7. **Resource Limits**: CPU and memory usage limits
8. **Logging**: Comprehensive request and error logging

### Configuration

```python
# config/settings.py - Production configuration
class ProductionConfig(Config):
    DEBUG = False
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB limit
    UPLOAD_FOLDER = '/secure/upload/path'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block'
    }
```
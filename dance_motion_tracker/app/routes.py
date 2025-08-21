"""
Flask routes for the dance motion tracking web application
"""
import os
import json
import uuid
from pathlib import Path
from flask import Blueprint, request, jsonify, render_template, send_file, current_app
from werkzeug.utils import secure_filename
import logging

from core.pose_detector import PoseDetector
from core.video_processor import VideoProcessor
from core.visualizer import PoseVisualizer
from core.data_exporter import DataExporter
from core.smoothing import PoseSmoothing
from app.utils import allowed_file, get_file_size, format_duration

logger = logging.getLogger(__name__)

# Create blueprint
main_bp = Blueprint('main', __name__)

# Global instances (in production, consider using application context)
pose_detector = PoseDetector()
video_processor = VideoProcessor()
visualizer = PoseVisualizer()
data_exporter = DataExporter()
pose_smoother = PoseSmoothing()

# Store processing sessions
processing_sessions = {}

@main_bp.route('/')
def index():
    """Main application page"""
    return render_template('index.html')

@main_bp.route('/upload', methods=['POST'])
def upload_video():
    """
    Handle video file upload
    """
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, current_app.config['SUPPORTED_VIDEO_FORMATS']):
            return jsonify({'error': 'Unsupported file format'}), 400
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = Path(current_app.config['UPLOAD_FOLDER']) / f"{session_id}_{filename}"
        file.save(str(file_path))
        
        # Validate video
        is_valid, error_msg = video_processor.validate_video(str(file_path))
        if not is_valid:
            os.remove(file_path)
            return jsonify({'error': f'Invalid video: {error_msg}'}), 400
        
        # Get video info
        video_info = video_processor.get_video_info(str(file_path))
        
        # Create session
        processing_sessions[session_id] = {
            'video_path': str(file_path),
            'original_filename': filename,
            'video_info': video_info,
            'status': 'uploaded',
            'pose_data': None,
            'output_files': {}
        }
        
        logger.info(f"Video uploaded successfully: {session_id}")
        
        return jsonify({
            'session_id': session_id,
            'video_info': video_info,
            'message': 'Video uploaded successfully'
        })
        
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        return jsonify({'error': 'Failed to upload video'}), 500

@main_bp.route('/process/<session_id>', methods=['POST'])
def process_video(session_id):
    """
    Process video to extract pose data
    """
    try:
        if session_id not in processing_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session = processing_sessions[session_id]
        
        if session['status'] != 'uploaded':
            return jsonify({'error': 'Video not ready for processing'}), 400
        
        # Get processing options
        options = request.get_json() or {}
        apply_smoothing = options.get('apply_smoothing', True)
        smoothing_method = options.get('smoothing_method', 'combined')
        create_overlay_video = options.get('create_overlay_video', True)
        export_formats = options.get('export_formats', ['json'])
        
        session['status'] = 'processing'
        
        # Process video
        logger.info(f"Starting pose detection for session {session_id}")
        
        def progress_callback(progress, current_frame, total_frames):
            # In a production app, you might use WebSockets or Server-Sent Events
            # to send real-time progress updates to the client
            logger.debug(f"Processing progress: {progress:.1%} ({current_frame}/{total_frames})")
        
        # Extract poses
        pose_sequence = pose_detector.process_video(
            session['video_path'],
            progress_callback=progress_callback
        )
        
        if not pose_sequence:
            session['status'] = 'failed'
            return jsonify({'error': 'No poses detected in video'}), 400
        
        logger.info(f"Detected poses in {len(pose_sequence)} frames")
        
        # Apply smoothing if requested
        if apply_smoothing and len(pose_sequence) > 5:
            logger.info(f"Applying {smoothing_method} smoothing")
            
            if smoothing_method == 'kalman':
                pose_sequence = pose_smoother.apply_kalman_smoothing(pose_sequence)
            elif smoothing_method == 'savgol':
                pose_sequence = pose_smoother.apply_savgol_smoothing(pose_sequence)
            elif smoothing_method == 'combined':
                pose_sequence = pose_smoother.apply_combined_smoothing(pose_sequence)
        
        session['pose_data'] = pose_sequence
        
        # Create output files
        output_dir = Path(current_app.config['UPLOAD_FOLDER']) / session_id
        output_dir.mkdir(exist_ok=True)
        
        # Export data in requested formats
        for format_name in export_formats:
            output_path = output_dir / f"pose_data.{format_name}"
            
            if format_name == 'json':
                success = data_exporter.export_to_json(pose_sequence, str(output_path))
            elif format_name == 'csv':
                success = data_exporter.export_to_csv(pose_sequence, str(output_path))
            elif format_name == 'blender':
                success = data_exporter.export_for_blender(pose_sequence, str(output_path))
            else:
                continue
            
            if success:
                session['output_files'][format_name] = str(output_path)
        
        # Create overlay video if requested
        if create_overlay_video:
            overlay_path = output_dir / "pose_overlay.mp4"
            success = visualizer.create_pose_video(
                session['video_path'],
                pose_sequence,
                str(overlay_path),
                progress_callback=progress_callback
            )
            
            if success:
                session['output_files']['overlay_video'] = str(overlay_path)
        
        # Create statistics
        stats_path = output_dir / "statistics.json"
        data_exporter.export_summary_stats(pose_sequence, str(stats_path))
        session['output_files']['statistics'] = str(stats_path)
        
        session['status'] = 'completed'
        
        logger.info(f"Processing completed for session {session_id}")
        
        return jsonify({
            'message': 'Processing completed successfully',
            'frames_processed': len(pose_sequence),
            'output_files': list(session['output_files'].keys())
        })
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        if session_id in processing_sessions:
            processing_sessions[session_id]['status'] = 'failed'
        return jsonify({'error': 'Failed to process video'}), 500

@main_bp.route('/status/<session_id>')
def get_status(session_id):
    """
    Get processing status for a session
    """
    if session_id not in processing_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = processing_sessions[session_id]
    
    response_data = {
        'session_id': session_id,
        'status': session['status'],
        'video_info': session['video_info']
    }
    
    if session['status'] == 'completed':
        response_data['output_files'] = list(session['output_files'].keys())
        
        # Add pose statistics
        if session['pose_data']:
            response_data['pose_stats'] = {
                'total_frames': len(session['pose_data']),
                'avg_confidence': sum(f.detection_confidence for f in session['pose_data']) / len(session['pose_data']),
                'duration': session['pose_data'][-1].timestamp if session['pose_data'] else 0
            }
    
    return jsonify(response_data)

@main_bp.route('/download/<session_id>/<file_type>')
def download_file(session_id, file_type):
    """
    Download processed files
    """
    try:
        if session_id not in processing_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session = processing_sessions[session_id]
        
        if file_type not in session['output_files']:
            return jsonify({'error': 'File not found'}), 404
        
        file_path = session['output_files'][file_type]
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File does not exist'}), 404
        
        # Determine download filename
        original_name = Path(session['original_filename']).stem
        
        if file_type == 'json':
            download_name = f"{original_name}_pose_data.json"
        elif file_type == 'csv':
            download_name = f"{original_name}_pose_data.csv"
        elif file_type == 'blender':
            download_name = f"{original_name}_blender_data.json"
        elif file_type == 'overlay_video':
            download_name = f"{original_name}_pose_overlay.mp4"
        elif file_type == 'statistics':
            download_name = f"{original_name}_statistics.json"
        else:
            download_name = f"{original_name}_{file_type}"
        
        return send_file(file_path, as_attachment=True, download_name=download_name)
        
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': 'Failed to download file'}), 500

@main_bp.route('/preview/<session_id>')
def preview_results(session_id):
    """
    Get preview data for results visualization
    """
    try:
        if session_id not in processing_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session = processing_sessions[session_id]
        
        if session['status'] != 'completed' or not session['pose_data']:
            return jsonify({'error': 'No data available for preview'}), 400
        
        pose_sequence = session['pose_data']
        
        # Sample frames for preview (every 10th frame)
        sample_frames = pose_sequence[::10]
        
        # Convert to preview format
        preview_data = []
        for pose_frame in sample_frames:
            frame_data = {
                'frame_index': pose_frame.frame_index,
                'timestamp': pose_frame.timestamp,
                'confidence': pose_frame.detection_confidence,
                'landmarks': []
            }
            
            for landmark in pose_frame.landmarks:
                if landmark.visibility > 0.5:  # Only include visible landmarks
                    frame_data['landmarks'].append({
                        'name': landmark.name,
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': landmark.visibility
                    })
            
            preview_data.append(frame_data)
        
        return jsonify({
            'preview_data': preview_data,
            'video_info': session['video_info'],
            'total_frames': len(pose_sequence)
        })
        
    except Exception as e:
        logger.error(f"Error generating preview: {str(e)}")
        return jsonify({'error': 'Failed to generate preview'}), 500

@main_bp.route('/cleanup/<session_id>', methods=['DELETE'])
def cleanup_session(session_id):
    """
    Clean up session files
    """
    try:
        if session_id not in processing_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session = processing_sessions[session_id]
        
        # Remove uploaded video
        if os.path.exists(session['video_path']):
            os.remove(session['video_path'])
        
        # Remove output directory
        output_dir = Path(current_app.config['UPLOAD_FOLDER']) / session_id
        if output_dir.exists():
            import shutil
            shutil.rmtree(output_dir)
        
        # Remove session
        del processing_sessions[session_id]
        
        logger.info(f"Session {session_id} cleaned up successfully")
        
        return jsonify({'message': 'Session cleaned up successfully'})
        
    except Exception as e:
        logger.error(f"Error cleaning up session: {str(e)}")
        return jsonify({'error': 'Failed to cleanup session'}), 500

@main_bp.route('/health')
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'active_sessions': len(processing_sessions)
    })

# Error handlers
@main_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@main_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500
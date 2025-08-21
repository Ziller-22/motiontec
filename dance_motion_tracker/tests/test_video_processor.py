"""
Unit tests for video processor module
"""
import unittest
import numpy as np
import cv2
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from core.video_processor import VideoProcessor

class TestVideoProcessor(unittest.TestCase):
    """Test cases for VideoProcessor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = VideoProcessor()
        self.test_video_path = None
        
        # Create a simple test video
        self.create_test_video()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.test_video_path and os.path.exists(self.test_video_path):
            os.unlink(self.test_video_path)
    
    def create_test_video(self):
        """Create a simple test video file"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            self.test_video_path = f.name
        
        # Create a simple test video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.test_video_path, fourcc, 10.0, (320, 240))
        
        # Write 30 frames (3 seconds at 10 FPS)
        for i in range(30):
            frame = np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)
            out.write(frame)
        
        out.release()
    
    def test_processor_initialization(self):
        """Test processor initialization"""
        self.assertEqual(len(self.processor.supported_formats), 7)
        self.assertIn('.mp4', self.processor.supported_formats)
        self.assertEqual(self.processor.default_codec, 'mp4v')
    
    def test_get_video_info(self):
        """Test getting video information"""
        info = self.processor.get_video_info(self.test_video_path)
        
        self.assertIsInstance(info, dict)
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertIn('fps', info)
        self.assertIn('frame_count', info)
        self.assertIn('duration', info)
        
        # Check expected values
        self.assertEqual(info['width'], 320)
        self.assertEqual(info['height'], 240)
        self.assertEqual(info['frame_count'], 30)
    
    def test_get_video_info_invalid_file(self):
        """Test getting video info for invalid file"""
        info = self.processor.get_video_info('nonexistent_file.mp4')
        self.assertEqual(info, {})
    
    def test_validate_video(self):
        """Test video validation"""
        # Test valid video
        is_valid, error_msg = self.processor.validate_video(self.test_video_path)
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "Video is valid")
        
        # Test non-existent file
        is_valid, error_msg = self.processor.validate_video('nonexistent.mp4')
        self.assertFalse(is_valid)
        self.assertIn("does not exist", error_msg)
        
        # Test unsupported format
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            txt_path = f.name
        
        try:
            is_valid, error_msg = self.processor.validate_video(txt_path)
            self.assertFalse(is_valid)
            self.assertIn("Unsupported format", error_msg)
        finally:
            os.unlink(txt_path)
    
    def test_resize_video(self):
        """Test video resizing"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            output_path = f.name
        
        try:
            # Test resizing
            success = self.processor.resize_video(
                self.test_video_path, 
                output_path, 
                (160, 120),
                maintain_aspect_ratio=False
            )
            
            self.assertTrue(success)
            self.assertTrue(os.path.exists(output_path))
            
            # Verify output video properties
            info = self.processor.get_video_info(output_path)
            self.assertEqual(info['width'], 160)
            self.assertEqual(info['height'], 120)
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_get_frame_at_time(self):
        """Test extracting frame at specific timestamp"""
        frame = self.processor.get_frame_at_time(self.test_video_path, 1.0)
        
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, (240, 320, 3))
        
        # Test invalid timestamp
        frame = self.processor.get_frame_at_time(self.test_video_path, 100.0)
        self.assertIsNone(frame)
    
    def test_create_thumbnail(self):
        """Test thumbnail creation"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            thumbnail_path = f.name
        
        try:
            success = self.processor.create_thumbnail(
                self.test_video_path,
                thumbnail_path,
                timestamp=0.5,
                size=(160, 120)
            )
            
            self.assertTrue(success)
            self.assertTrue(os.path.exists(thumbnail_path))
            
            # Verify thumbnail
            thumbnail = cv2.imread(thumbnail_path)
            self.assertIsNotNone(thumbnail)
            self.assertEqual(thumbnail.shape[:2], (120, 160))
            
        finally:
            if os.path.exists(thumbnail_path):
                os.unlink(thumbnail_path)
    
    def test_extract_frames(self):
        """Test frame extraction"""
        with tempfile.TemporaryDirectory() as temp_dir:
            frame_paths = self.processor.extract_frames(
                self.test_video_path,
                temp_dir,
                frame_interval=5,  # Extract every 5th frame
                max_frames=3
            )
            
            self.assertEqual(len(frame_paths), 3)
            
            # Verify frames exist
            for path in frame_paths:
                self.assertTrue(os.path.exists(path))
                
                # Verify frame is valid image
                frame = cv2.imread(path)
                self.assertIsNotNone(frame)
                self.assertEqual(frame.shape, (240, 320, 3))
    
    def test_create_video_from_frames(self):
        """Test creating video from frame images"""
        # First extract some frames
        with tempfile.TemporaryDirectory() as temp_dir:
            frame_paths = self.processor.extract_frames(
                self.test_video_path,
                temp_dir,
                frame_interval=10,
                max_frames=3
            )
            
            # Create video from frames
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
                output_path = f.name
            
            try:
                success = self.processor.create_video_from_frames(
                    frame_paths,
                    output_path,
                    fps=5.0
                )
                
                self.assertTrue(success)
                self.assertTrue(os.path.exists(output_path))
                
                # Verify output video
                info = self.processor.get_video_info(output_path)
                self.assertEqual(info['width'], 320)
                self.assertEqual(info['height'], 240)
                
            finally:
                if os.path.exists(output_path):
                    os.unlink(output_path)

class TestVideoProcessorEdgeCases(unittest.TestCase):
    """Test edge cases for VideoProcessor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = VideoProcessor()
    
    def test_empty_frame_list(self):
        """Test creating video from empty frame list"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            output_path = f.name
        
        try:
            success = self.processor.create_video_from_frames(
                [],
                output_path,
                fps=30.0
            )
            
            self.assertFalse(success)
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_invalid_video_path(self):
        """Test operations with invalid video path"""
        invalid_path = "nonexistent_video.mp4"
        
        # Test get_frame_at_time
        frame = self.processor.get_frame_at_time(invalid_path, 1.0)
        self.assertIsNone(frame)
        
        # Test create_thumbnail
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            thumbnail_path = f.name
        
        try:
            success = self.processor.create_thumbnail(invalid_path, thumbnail_path)
            self.assertFalse(success)
        finally:
            if os.path.exists(thumbnail_path):
                os.unlink(thumbnail_path)
    
    @patch('subprocess.run')
    def test_convert_video_format_success(self, mock_run):
        """Test successful video format conversion"""
        mock_run.return_value.returncode = 0
        
        success = self.processor.convert_video_format(
            'input.mp4',
            'output.avi',
            target_fps=30,
            target_resolution=(640, 480)
        )
        
        self.assertTrue(success)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_convert_video_format_failure(self, mock_run):
        """Test failed video format conversion"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "FFmpeg error"
        
        success = self.processor.convert_video_format(
            'input.mp4',
            'output.avi'
        )
        
        self.assertFalse(success)
    
    @patch('subprocess.run', side_effect=FileNotFoundError)
    def test_convert_video_format_no_ffmpeg(self, mock_run):
        """Test video conversion when FFmpeg is not available"""
        success = self.processor.convert_video_format(
            'input.mp4',
            'output.avi'
        )
        
        self.assertFalse(success)

if __name__ == '__main__':
    unittest.main()
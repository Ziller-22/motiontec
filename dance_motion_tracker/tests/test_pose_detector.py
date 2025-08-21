"""
Unit tests for pose detection module
"""
import unittest
import numpy as np
import cv2
from unittest.mock import Mock, patch
import tempfile
import os

from core.pose_detector import PoseDetector, PoseFrame, PoseLandmark

class TestPoseDetector(unittest.TestCase):
    """Test cases for PoseDetector class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = PoseDetector()
        
        # Create a test image
        self.test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Create test pose landmark
        self.test_landmark = PoseLandmark(
            x=320.0,
            y=240.0,
            z=-50.0,
            visibility=0.95,
            name="NOSE",
            frame_index=0
        )
        
        # Create test pose frame
        self.test_pose_frame = PoseFrame(
            frame_index=0,
            timestamp=0.0,
            landmarks=[self.test_landmark],
            image_width=640,
            image_height=480,
            detection_confidence=0.95
        )
    
    def test_detector_initialization(self):
        """Test detector initialization"""
        self.assertIsNotNone(self.detector.pose)
        self.assertEqual(self.detector.model_complexity, 1)
        self.assertEqual(self.detector.min_detection_confidence, 0.5)
        self.assertEqual(self.detector.current_frame_index, 0)
    
    def test_detect_pose_with_none_image(self):
        """Test pose detection with None image"""
        result = self.detector.detect_pose(None)
        self.assertIsNone(result)
    
    @patch('core.pose_detector.mp.solutions.pose.Pose.process')
    def test_detect_pose_no_landmarks(self, mock_process):
        """Test pose detection when no landmarks are detected"""
        # Mock MediaPipe to return no landmarks
        mock_result = Mock()
        mock_result.pose_landmarks = None
        mock_process.return_value = mock_result
        
        result = self.detector.detect_pose(self.test_image)
        self.assertIsNone(result)
    
    @patch('core.pose_detector.mp.solutions.pose.Pose.process')
    def test_detect_pose_with_landmarks(self, mock_process):
        """Test pose detection with valid landmarks"""
        # Mock MediaPipe to return landmarks
        mock_landmark = Mock()
        mock_landmark.x = 0.5
        mock_landmark.y = 0.5
        mock_landmark.z = -0.1
        mock_landmark.visibility = 0.95
        
        mock_result = Mock()
        mock_result.pose_landmarks = Mock()
        mock_result.pose_landmarks.landmark = [mock_landmark] * 33  # MediaPipe has 33 landmarks
        mock_process.return_value = mock_result
        
        result = self.detector.detect_pose(self.test_image)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, PoseFrame)
        self.assertEqual(len(result.landmarks), 33)
        self.assertEqual(result.image_width, 640)
        self.assertEqual(result.image_height, 480)
    
    def test_get_landmark_by_name(self):
        """Test getting landmark by name"""
        landmark = self.detector.get_landmark_by_name(self.test_pose_frame, "NOSE")
        self.assertIsNotNone(landmark)
        self.assertEqual(landmark.name, "NOSE")
        
        # Test non-existent landmark
        landmark = self.detector.get_landmark_by_name(self.test_pose_frame, "NON_EXISTENT")
        self.assertIsNone(landmark)
    
    def test_calculate_pose_confidence(self):
        """Test pose confidence calculation"""
        confidence = self.detector.calculate_pose_confidence(self.test_pose_frame)
        self.assertEqual(confidence, 0.95)
        
        # Test with empty landmarks
        empty_frame = PoseFrame(0, 0.0, [], 640, 480, 0.0)
        confidence = self.detector.calculate_pose_confidence(empty_frame)
        self.assertEqual(confidence, 0.0)
    
    def test_reset(self):
        """Test detector reset"""
        self.detector.pose_sequence = [self.test_pose_frame]
        self.detector.current_frame_index = 5
        
        self.detector.reset()
        
        self.assertEqual(len(self.detector.pose_sequence), 0)
        self.assertEqual(self.detector.current_frame_index, 0)

class TestPoseLandmark(unittest.TestCase):
    """Test cases for PoseLandmark class"""
    
    def test_pose_landmark_creation(self):
        """Test PoseLandmark creation"""
        landmark = PoseLandmark(
            x=100.0,
            y=200.0,
            z=-10.0,
            visibility=0.8,
            name="LEFT_EYE",
            frame_index=5
        )
        
        self.assertEqual(landmark.x, 100.0)
        self.assertEqual(landmark.y, 200.0)
        self.assertEqual(landmark.z, -10.0)
        self.assertEqual(landmark.visibility, 0.8)
        self.assertEqual(landmark.name, "LEFT_EYE")
        self.assertEqual(landmark.frame_index, 5)

class TestPoseFrame(unittest.TestCase):
    """Test cases for PoseFrame class"""
    
    def test_pose_frame_creation(self):
        """Test PoseFrame creation"""
        landmarks = [
            PoseLandmark(100, 200, -10, 0.8, "NOSE", 0),
            PoseLandmark(110, 190, -12, 0.9, "LEFT_EYE", 0)
        ]
        
        frame = PoseFrame(
            frame_index=10,
            timestamp=0.33,
            landmarks=landmarks,
            image_width=1920,
            image_height=1080,
            detection_confidence=0.85
        )
        
        self.assertEqual(frame.frame_index, 10)
        self.assertEqual(frame.timestamp, 0.33)
        self.assertEqual(len(frame.landmarks), 2)
        self.assertEqual(frame.image_width, 1920)
        self.assertEqual(frame.image_height, 1080)
        self.assertEqual(frame.detection_confidence, 0.85)

if __name__ == '__main__':
    unittest.main()
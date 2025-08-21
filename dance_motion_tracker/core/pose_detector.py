"""
MediaPipe-based pose detection module for dance motion tracking
"""
import cv2
import numpy as np
import mediapipe as mp
from typing import Optional, Dict, List, Tuple, Any
import logging
from dataclasses import dataclass
from pathlib import Path

from config.mediapipe_config import (
    POSE_LANDMARKS, MEDIAPIPE_CONFIG, LANDMARK_GROUPS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PoseLandmark:
    """Represents a single pose landmark with 3D coordinates and visibility"""
    x: float
    y: float
    z: float
    visibility: float
    name: str
    frame_index: int

@dataclass
class PoseFrame:
    """Represents all pose landmarks for a single frame"""
    frame_index: int
    timestamp: float
    landmarks: List[PoseLandmark]
    image_width: int
    image_height: int
    detection_confidence: float

class PoseDetector:
    """
    MediaPipe-based pose detection class for extracting dance motion data
    """
    
    def __init__(self, 
                 model_complexity: int = 1,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5,
                 enable_segmentation: bool = False):
        """
        Initialize the pose detector
        
        Args:
            model_complexity: Complexity of pose model (0, 1, or 2)
            min_detection_confidence: Minimum confidence for pose detection
            min_tracking_confidence: Minimum confidence for pose tracking
            enable_segmentation: Whether to enable background segmentation
        """
        self.model_complexity = model_complexity
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.enable_segmentation = enable_segmentation
        
        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialize pose detector
        self.pose = self.mp_pose.Pose(
            model_complexity=self.model_complexity,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
            enable_segmentation=self.enable_segmentation
        )
        
        # Storage for detected poses
        self.pose_sequence: List[PoseFrame] = []
        self.current_frame_index = 0
        
        logger.info(f"PoseDetector initialized with complexity={model_complexity}")
    
    def detect_pose(self, 
                   image: np.ndarray, 
                   timestamp: float = 0.0) -> Optional[PoseFrame]:
        """
        Detect pose landmarks in a single image
        
        Args:
            image: Input image as numpy array (BGR format)
            timestamp: Timestamp of the frame
            
        Returns:
            PoseFrame object with detected landmarks, or None if no pose detected
        """
        if image is None:
            logger.warning("Input image is None")
            return None
            
        # Convert BGR to RGB for MediaPipe
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        rgb_image.flags.writeable = False
        
        # Perform pose detection
        results = self.pose.process(rgb_image)
        
        if not results.pose_landmarks:
            logger.debug(f"No pose detected in frame {self.current_frame_index}")
            return None
        
        # Extract landmark data
        landmarks = []
        h, w = image.shape[:2]
        
        for i, landmark in enumerate(results.pose_landmarks.landmark):
            # Get landmark name from index
            landmark_name = next(
                (name for name, idx in POSE_LANDMARKS.items() if idx == i), 
                f"LANDMARK_{i}"
            )
            
            pose_landmark = PoseLandmark(
                x=landmark.x * w,  # Convert normalized to pixel coordinates
                y=landmark.y * h,
                z=landmark.z * w,  # Z is roughly in the same scale as X
                visibility=landmark.visibility,
                name=landmark_name,
                frame_index=self.current_frame_index
            )
            landmarks.append(pose_landmark)
        
        # Create PoseFrame
        pose_frame = PoseFrame(
            frame_index=self.current_frame_index,
            timestamp=timestamp,
            landmarks=landmarks,
            image_width=w,
            image_height=h,
            detection_confidence=min([lm.visibility for lm in landmarks])
        )
        
        self.current_frame_index += 1
        return pose_frame
    
    def process_video(self, 
                     video_path: str, 
                     output_path: Optional[str] = None,
                     progress_callback: Optional[callable] = None) -> List[PoseFrame]:
        """
        Process entire video and extract pose data from all frames
        
        Args:
            video_path: Path to input video file
            output_path: Optional path to save processed video with overlays
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of PoseFrame objects for all frames
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error(f"Could not open video file: {video_path}")
            return []
        
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        logger.info(f"Processing video: {total_frames} frames at {fps} FPS ({width}x{height})")
        
        # Initialize video writer if output path provided
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        self.pose_sequence = []
        frame_index = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                timestamp = frame_index / fps
                
                # Detect pose
                pose_frame = self.detect_pose(frame, timestamp)
                if pose_frame:
                    self.pose_sequence.append(pose_frame)
                    
                    # Draw pose overlay if saving output video
                    if writer:
                        annotated_frame = self.draw_pose_overlay(frame, pose_frame)
                        writer.write(annotated_frame)
                else:
                    # Write original frame if no pose detected
                    if writer:
                        writer.write(frame)
                
                # Progress callback
                if progress_callback:
                    progress = (frame_index + 1) / total_frames
                    progress_callback(progress, frame_index + 1, total_frames)
                
                frame_index += 1
                
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
        finally:
            cap.release()
            if writer:
                writer.release()
        
        logger.info(f"Processed {len(self.pose_sequence)} frames with pose data")
        return self.pose_sequence
    
    def draw_pose_overlay(self, 
                         image: np.ndarray, 
                         pose_frame: PoseFrame) -> np.ndarray:
        """
        Draw pose landmarks and connections on image
        
        Args:
            image: Input image
            pose_frame: PoseFrame with landmark data
            
        Returns:
            Image with pose overlay drawn
        """
        annotated_image = image.copy()
        
        # Convert landmarks to MediaPipe format for drawing
        landmark_list = []
        for landmark in pose_frame.landmarks:
            # Normalize coordinates back to [0, 1] range
            normalized_landmark = type('Landmark', (), {
                'x': landmark.x / pose_frame.image_width,
                'y': landmark.y / pose_frame.image_height,
                'z': landmark.z / pose_frame.image_width,
                'visibility': landmark.visibility
            })()
            landmark_list.append(normalized_landmark)
        
        # Create MediaPipe landmark list
        pose_landmarks = type('PoseLandmarks', (), {
            'landmark': landmark_list
        })()
        
        # Draw landmarks and connections
        self.mp_drawing.draw_landmarks(
            annotated_image,
            pose_landmarks,
            self.mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
        )
        
        # Add frame info
        cv2.putText(annotated_image, 
                   f"Frame: {pose_frame.frame_index}", 
                   (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   0.7, (0, 255, 0), 2)
        
        cv2.putText(annotated_image, 
                   f"Confidence: {pose_frame.detection_confidence:.2f}", 
                   (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   0.7, (0, 255, 0), 2)
        
        return annotated_image
    
    def get_landmark_by_name(self, 
                            pose_frame: PoseFrame, 
                            landmark_name: str) -> Optional[PoseLandmark]:
        """
        Get specific landmark by name from pose frame
        
        Args:
            pose_frame: PoseFrame to search
            landmark_name: Name of landmark to find
            
        Returns:
            PoseLandmark if found, None otherwise
        """
        for landmark in pose_frame.landmarks:
            if landmark.name == landmark_name:
                return landmark
        return None
    
    def get_landmarks_by_group(self, 
                              pose_frame: PoseFrame, 
                              group_name: str) -> List[PoseLandmark]:
        """
        Get landmarks belonging to a specific body part group
        
        Args:
            pose_frame: PoseFrame to search
            group_name: Name of landmark group ('face', 'upper_body', etc.)
            
        Returns:
            List of PoseLandmark objects in the group
        """
        if group_name not in LANDMARK_GROUPS:
            logger.warning(f"Unknown landmark group: {group_name}")
            return []
        
        group_landmarks = []
        group_names = LANDMARK_GROUPS[group_name]
        
        for landmark in pose_frame.landmarks:
            if landmark.name in group_names:
                group_landmarks.append(landmark)
        
        return group_landmarks
    
    def calculate_pose_confidence(self, pose_frame: PoseFrame) -> float:
        """
        Calculate overall pose confidence score
        
        Args:
            pose_frame: PoseFrame to analyze
            
        Returns:
            Average confidence score across all landmarks
        """
        if not pose_frame.landmarks:
            return 0.0
        
        total_confidence = sum(landmark.visibility for landmark in pose_frame.landmarks)
        return total_confidence / len(pose_frame.landmarks)
    
    def reset(self):
        """Reset the detector state"""
        self.pose_sequence = []
        self.current_frame_index = 0
        logger.info("PoseDetector reset")
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'pose'):
            self.pose.close()
"""
Visualization module for drawing pose overlays and creating output videos
"""
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import logging

from core.pose_detector import PoseFrame, PoseLandmark
from config.mediapipe_config import (
    POSE_CONNECTIONS, VISUALIZATION_COLORS, LANDMARK_GROUPS
)

logger = logging.getLogger(__name__)

class PoseVisualizer:
    """
    Handles visualization of pose data on video frames and creation of output videos
    """
    
    def __init__(self, 
                 joint_color: Tuple[int, int, int] = (0, 255, 0),
                 connection_color: Tuple[int, int, int] = (255, 0, 0),
                 joint_radius: int = 4,
                 connection_thickness: int = 2):
        """
        Initialize visualizer
        
        Args:
            joint_color: Color for joint points (BGR)
            connection_color: Color for connections (BGR)
            joint_radius: Radius of joint circles
            connection_thickness: Thickness of connection lines
        """
        self.joint_color = joint_color
        self.connection_color = connection_color
        self.joint_radius = joint_radius
        self.connection_thickness = connection_thickness
        
        # Color scheme for different body parts
        self.body_part_colors = {
            'face': (0, 255, 255),      # Yellow
            'upper_body': (0, 255, 0),   # Green
            'hands': (255, 0, 255),      # Magenta
            'lower_body': (255, 0, 0),   # Blue
        }
    
    def draw_pose_landmarks(self, 
                           image: np.ndarray, 
                           pose_frame: PoseFrame,
                           draw_connections: bool = True,
                           draw_landmarks: bool = True,
                           color_by_body_part: bool = False) -> np.ndarray:
        """
        Draw pose landmarks and connections on image
        
        Args:
            image: Input image
            pose_frame: PoseFrame with landmark data
            draw_connections: Whether to draw skeleton connections
            draw_landmarks: Whether to draw landmark points
            color_by_body_part: Whether to color by body part
            
        Returns:
            Image with pose overlay
        """
        annotated_image = image.copy()
        
        if not pose_frame.landmarks:
            return annotated_image
        
        # Create landmark lookup for connections
        landmark_dict = {lm.name: lm for lm in pose_frame.landmarks}
        
        # Draw connections first (so they appear behind landmarks)
        if draw_connections:
            for connection in POSE_CONNECTIONS:
                start_name, end_name = connection
                
                if start_name in landmark_dict and end_name in landmark_dict:
                    start_lm = landmark_dict[start_name]
                    end_lm = landmark_dict[end_name]
                    
                    # Only draw if both landmarks are visible enough
                    if start_lm.visibility > 0.5 and end_lm.visibility > 0.5:
                        start_point = (int(start_lm.x), int(start_lm.y))
                        end_point = (int(end_lm.x), int(end_lm.y))
                        
                        # Choose color
                        if color_by_body_part:
                            color = self._get_body_part_color(start_name)
                        else:
                            color = self.connection_color
                        
                        cv2.line(annotated_image, start_point, end_point, 
                                color, self.connection_thickness)
        
        # Draw landmarks
        if draw_landmarks:
            for landmark in pose_frame.landmarks:
                if landmark.visibility > 0.5:  # Only draw visible landmarks
                    center = (int(landmark.x), int(landmark.y))
                    
                    # Choose color
                    if color_by_body_part:
                        color = self._get_body_part_color(landmark.name)
                    else:
                        color = self.joint_color
                    
                    cv2.circle(annotated_image, center, self.joint_radius, color, -1)
                    
                    # Draw landmark name (optional, for debugging)
                    if False:  # Set to True for debugging
                        cv2.putText(annotated_image, landmark.name, 
                                  (center[0] + 5, center[1] - 5),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
        
        return annotated_image
    
    def create_pose_video(self, 
                         input_video_path: str,
                         pose_sequence: List[PoseFrame],
                         output_video_path: str,
                         show_info: bool = True,
                         progress_callback: Optional[callable] = None) -> bool:
        """
        Create output video with pose overlays
        
        Args:
            input_video_path: Path to original video
            pose_sequence: List of PoseFrame objects
            output_video_path: Path for output video
            show_info: Whether to show frame info
            progress_callback: Optional progress callback
            
        Returns:
            True if video created successfully
        """
        cap = cv2.VideoCapture(input_video_path)
        
        if not cap.isOpened():
            logger.error(f"Could not open input video: {input_video_path}")
            return False
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        
        if not writer.isOpened():
            logger.error("Could not initialize video writer")
            cap.release()
            return False
        
        # Create pose frame lookup
        pose_dict = {frame.frame_index: frame for frame in pose_sequence}
        
        frame_index = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Add pose overlay if available
                if frame_index in pose_dict:
                    pose_frame = pose_dict[frame_index]
                    annotated_frame = self.draw_pose_landmarks(
                        frame, pose_frame, color_by_body_part=True
                    )
                    
                    # Add frame info
                    if show_info:
                        annotated_frame = self._add_frame_info(annotated_frame, pose_frame)
                else:
                    annotated_frame = frame
                    
                    # Add "No pose detected" text
                    if show_info:
                        cv2.putText(annotated_frame, "No pose detected", 
                                  (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                  0.7, (0, 0, 255), 2)
                
                writer.write(annotated_frame)
                
                # Progress callback
                if progress_callback:
                    progress = (frame_index + 1) / total_frames
                    progress_callback(progress, frame_index + 1, total_frames)
                
                frame_index += 1
            
            cap.release()
            writer.release()
            
            logger.info(f"Pose video created successfully: {output_video_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating pose video: {str(e)}")
            cap.release()
            writer.release()
            return False
    
    def create_pose_comparison_video(self, 
                                   input_video_path: str,
                                   original_poses: List[PoseFrame],
                                   smoothed_poses: List[PoseFrame],
                                   output_video_path: str) -> bool:
        """
        Create side-by-side comparison video of original vs smoothed poses
        
        Args:
            input_video_path: Path to original video
            original_poses: Original pose sequence
            smoothed_poses: Smoothed pose sequence
            output_video_path: Output video path
            
        Returns:
            True if video created successfully
        """
        cap = cv2.VideoCapture(input_video_path)
        
        if not cap.isOpened():
            logger.error(f"Could not open input video: {input_video_path}")
            return False
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Output video will be twice as wide
        output_width = width * 2
        output_height = height
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_video_path, fourcc, fps, (output_width, output_height))
        
        if not writer.isOpened():
            logger.error("Could not initialize video writer")
            cap.release()
            return False
        
        # Create pose lookups
        original_dict = {frame.frame_index: frame for frame in original_poses}
        smoothed_dict = {frame.frame_index: frame for frame in smoothed_poses}
        
        frame_index = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Create left frame (original)
                left_frame = frame.copy()
                if frame_index in original_dict:
                    left_frame = self.draw_pose_landmarks(
                        left_frame, original_dict[frame_index]
                    )
                
                # Create right frame (smoothed)
                right_frame = frame.copy()
                if frame_index in smoothed_dict:
                    right_frame = self.draw_pose_landmarks(
                        right_frame, smoothed_dict[frame_index]
                    )
                
                # Add labels
                cv2.putText(left_frame, "Original", (10, 30), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(right_frame, "Smoothed", (10, 30), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                # Combine frames side by side
                combined_frame = np.hstack([left_frame, right_frame])
                writer.write(combined_frame)
                
                frame_index += 1
            
            cap.release()
            writer.release()
            
            logger.info(f"Comparison video created: {output_video_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating comparison video: {str(e)}")
            cap.release()
            writer.release()
            return False
    
    def create_pose_trajectory_plot(self, 
                                  pose_sequence: List[PoseFrame],
                                  landmark_names: List[str],
                                  output_path: str,
                                  plot_3d: bool = False) -> bool:
        """
        Create trajectory plot for specific landmarks
        
        Args:
            pose_sequence: List of PoseFrame objects
            landmark_names: Names of landmarks to plot
            output_path: Output image path
            plot_3d: Whether to create 3D plot
            
        Returns:
            True if plot created successfully
        """
        try:
            if plot_3d:
                fig = plt.figure(figsize=(12, 8))
                ax = fig.add_subplot(111, projection='3d')
            else:
                fig, ax = plt.subplots(figsize=(12, 8))
            
            colors = plt.cm.tab10(np.linspace(0, 1, len(landmark_names)))
            
            for i, landmark_name in enumerate(landmark_names):
                x_coords = []
                y_coords = []
                z_coords = []
                
                for pose_frame in pose_sequence:
                    landmark = next((lm for lm in pose_frame.landmarks 
                                   if lm.name == landmark_name), None)
                    if landmark and landmark.visibility > 0.5:
                        x_coords.append(landmark.x)
                        y_coords.append(landmark.y)
                        z_coords.append(landmark.z)
                    else:
                        # Add NaN for missing data
                        x_coords.append(np.nan)
                        y_coords.append(np.nan)
                        z_coords.append(np.nan)
                
                if plot_3d:
                    ax.plot(x_coords, y_coords, z_coords, 
                           color=colors[i], label=landmark_name, alpha=0.7)
                    ax.set_zlabel('Z')
                else:
                    ax.plot(x_coords, y_coords, 
                           color=colors[i], label=landmark_name, alpha=0.7)
            
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.legend()
            ax.set_title('Pose Landmark Trajectories')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Trajectory plot saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating trajectory plot: {str(e)}")
            return False
    
    def _get_body_part_color(self, landmark_name: str) -> Tuple[int, int, int]:
        """Get color for landmark based on body part"""
        for part, landmarks in LANDMARK_GROUPS.items():
            if landmark_name in landmarks:
                return self.body_part_colors.get(part, self.joint_color)
        return self.joint_color
    
    def _add_frame_info(self, image: np.ndarray, pose_frame: PoseFrame) -> np.ndarray:
        """Add frame information overlay"""
        info_text = [
            f"Frame: {pose_frame.frame_index}",
            f"Time: {pose_frame.timestamp:.2f}s",
            f"Confidence: {pose_frame.detection_confidence:.2f}",
            f"Landmarks: {len(pose_frame.landmarks)}"
        ]
        
        y_offset = 30
        for text in info_text:
            cv2.putText(image, text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            y_offset += 25
        
        return image
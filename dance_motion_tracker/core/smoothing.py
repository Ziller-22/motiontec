"""
Smoothing and filtering algorithms for pose data
Includes Kalman filters and Savitzky-Golay smoothing
"""
import numpy as np
from typing import List, Optional, Tuple, Dict, Any
from scipy.signal import savgol_filter
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise
import logging

from core.pose_detector import PoseFrame, PoseLandmark

logger = logging.getLogger(__name__)

class PoseSmoothing:
    """
    Class for applying various smoothing algorithms to pose data
    """
    
    def __init__(self):
        self.kalman_filters: Dict[str, KalmanFilter] = {}
        self.initialized_landmarks: set = set()
    
    def apply_savgol_smoothing(self, 
                              pose_sequence: List[PoseFrame],
                              window_length: int = 5,
                              polyorder: int = 2) -> List[PoseFrame]:
        """
        Apply Savitzky-Golay smoothing to pose sequence
        
        Args:
            pose_sequence: List of PoseFrame objects
            window_length: Length of smoothing window (must be odd)
            polyorder: Order of polynomial for fitting
            
        Returns:
            Smoothed pose sequence
        """
        if len(pose_sequence) < window_length:
            logger.warning(f"Sequence too short for smoothing (need {window_length}, got {len(pose_sequence)})")
            return pose_sequence
        
        # Ensure window_length is odd
        if window_length % 2 == 0:
            window_length += 1
        
        logger.info(f"Applying Savitzky-Golay smoothing (window={window_length}, poly={polyorder})")
        
        # Group landmarks by name for processing
        landmark_data = self._group_landmarks_by_name(pose_sequence)
        
        smoothed_sequence = []
        
        for frame_idx, pose_frame in enumerate(pose_sequence):
            smoothed_landmarks = []
            
            for landmark in pose_frame.landmarks:
                landmark_name = landmark.name
                
                if landmark_name in landmark_data and len(landmark_data[landmark_name]) >= window_length:
                    # Get coordinate arrays for this landmark
                    x_coords = np.array([lm.x for lm in landmark_data[landmark_name]])
                    y_coords = np.array([lm.y for lm in landmark_data[landmark_name]])
                    z_coords = np.array([lm.z for lm in landmark_data[landmark_name]])
                    
                    # Apply smoothing
                    x_smooth = savgol_filter(x_coords, window_length, polyorder)
                    y_smooth = savgol_filter(y_coords, window_length, polyorder)
                    z_smooth = savgol_filter(z_coords, window_length, polyorder)
                    
                    # Create smoothed landmark
                    smoothed_landmark = PoseLandmark(
                        x=x_smooth[frame_idx],
                        y=y_smooth[frame_idx],
                        z=z_smooth[frame_idx],
                        visibility=landmark.visibility,
                        name=landmark.name,
                        frame_index=landmark.frame_index
                    )
                else:
                    # Use original landmark if not enough data
                    smoothed_landmark = landmark
                
                smoothed_landmarks.append(smoothed_landmark)
            
            # Create smoothed frame
            smoothed_frame = PoseFrame(
                frame_index=pose_frame.frame_index,
                timestamp=pose_frame.timestamp,
                landmarks=smoothed_landmarks,
                image_width=pose_frame.image_width,
                image_height=pose_frame.image_height,
                detection_confidence=pose_frame.detection_confidence
            )
            
            smoothed_sequence.append(smoothed_frame)
        
        return smoothed_sequence
    
    def apply_kalman_smoothing(self, 
                              pose_sequence: List[PoseFrame],
                              process_variance: float = 1e-3,
                              measurement_variance: float = 1e-1) -> List[PoseFrame]:
        """
        Apply Kalman filtering to pose sequence
        
        Args:
            pose_sequence: List of PoseFrame objects
            process_variance: Process noise variance
            measurement_variance: Measurement noise variance
            
        Returns:
            Kalman-filtered pose sequence
        """
        logger.info(f"Applying Kalman filtering (proc_var={process_variance}, meas_var={measurement_variance})")
        
        filtered_sequence = []
        
        for frame_idx, pose_frame in enumerate(pose_sequence):
            filtered_landmarks = []
            
            for landmark in pose_frame.landmarks:
                landmark_name = landmark.name
                
                # Initialize Kalman filter for this landmark if not exists
                if landmark_name not in self.kalman_filters:
                    self.kalman_filters[landmark_name] = self._create_kalman_filter(
                        process_variance, measurement_variance
                    )
                    # Initialize with first measurement
                    self.kalman_filters[landmark_name].x = np.array([
                        landmark.x, 0, landmark.y, 0, landmark.z, 0
                    ])
                
                kf = self.kalman_filters[landmark_name]
                
                # Predict
                kf.predict()
                
                # Update with measurement
                measurement = np.array([landmark.x, landmark.y, landmark.z])
                kf.update(measurement)
                
                # Extract filtered position
                filtered_landmark = PoseLandmark(
                    x=kf.x[0],
                    y=kf.x[2],
                    z=kf.x[4],
                    visibility=landmark.visibility,
                    name=landmark.name,
                    frame_index=landmark.frame_index
                )
                
                filtered_landmarks.append(filtered_landmark)
            
            # Create filtered frame
            filtered_frame = PoseFrame(
                frame_index=pose_frame.frame_index,
                timestamp=pose_frame.timestamp,
                landmarks=filtered_landmarks,
                image_width=pose_frame.image_width,
                image_height=pose_frame.image_height,
                detection_confidence=pose_frame.detection_confidence
            )
            
            filtered_sequence.append(filtered_frame)
        
        return filtered_sequence
    
    def apply_combined_smoothing(self, 
                                pose_sequence: List[PoseFrame],
                                use_kalman: bool = True,
                                use_savgol: bool = True,
                                kalman_params: Optional[Dict] = None,
                                savgol_params: Optional[Dict] = None) -> List[PoseFrame]:
        """
        Apply combined Kalman and Savitzky-Golay smoothing
        
        Args:
            pose_sequence: Input pose sequence
            use_kalman: Whether to apply Kalman filtering
            use_savgol: Whether to apply Savitzky-Golay smoothing
            kalman_params: Parameters for Kalman filter
            savgol_params: Parameters for Savitzky-Golay filter
            
        Returns:
            Smoothed pose sequence
        """
        result_sequence = pose_sequence
        
        # Apply Kalman filtering first
        if use_kalman:
            kalman_params = kalman_params or {}
            result_sequence = self.apply_kalman_smoothing(result_sequence, **kalman_params)
        
        # Apply Savitzky-Golay smoothing second
        if use_savgol:
            savgol_params = savgol_params or {}
            result_sequence = self.apply_savgol_smoothing(result_sequence, **savgol_params)
        
        return result_sequence
    
    def interpolate_missing_frames(self, 
                                  pose_sequence: List[Optional[PoseFrame]],
                                  method: str = 'linear') -> List[PoseFrame]:
        """
        Interpolate missing pose frames
        
        Args:
            pose_sequence: Sequence with potential None values for missing frames
            method: Interpolation method ('linear', 'cubic')
            
        Returns:
            Complete pose sequence with interpolated frames
        """
        logger.info(f"Interpolating missing frames using {method} method")
        
        # Find valid frames
        valid_indices = []
        valid_frames = []
        
        for i, frame in enumerate(pose_sequence):
            if frame is not None:
                valid_indices.append(i)
                valid_frames.append(frame)
        
        if len(valid_frames) < 2:
            logger.warning("Not enough valid frames for interpolation")
            return [f for f in pose_sequence if f is not None]
        
        # Interpolate missing frames
        complete_sequence = []
        
        for i in range(len(pose_sequence)):
            if pose_sequence[i] is not None:
                complete_sequence.append(pose_sequence[i])
            else:
                # Find surrounding valid frames
                prev_idx = max([idx for idx in valid_indices if idx < i], default=None)
                next_idx = min([idx for idx in valid_indices if idx > i], default=None)
                
                if prev_idx is not None and next_idx is not None:
                    # Interpolate between frames
                    prev_frame = pose_sequence[prev_idx]
                    next_frame = pose_sequence[next_idx]
                    
                    alpha = (i - prev_idx) / (next_idx - prev_idx)
                    interpolated_frame = self._interpolate_frames(prev_frame, next_frame, alpha, i)
                    complete_sequence.append(interpolated_frame)
                elif prev_idx is not None:
                    # Use previous frame
                    complete_sequence.append(self._copy_frame_with_index(pose_sequence[prev_idx], i))
                elif next_idx is not None:
                    # Use next frame
                    complete_sequence.append(self._copy_frame_with_index(pose_sequence[next_idx], i))
        
        return complete_sequence
    
    def _create_kalman_filter(self, 
                             process_variance: float, 
                             measurement_variance: float) -> KalmanFilter:
        """Create a Kalman filter for 3D position tracking"""
        kf = KalmanFilter(dim_x=6, dim_z=3)  # 6 state variables, 3 measurements
        
        # State transition matrix (position and velocity for x, y, z)
        dt = 1.0  # Time step
        kf.F = np.array([
            [1, dt, 0, 0,  0, 0 ],
            [0, 1,  0, 0,  0, 0 ],
            [0, 0,  1, dt, 0, 0 ],
            [0, 0,  0, 1,  0, 0 ],
            [0, 0,  0, 0,  1, dt],
            [0, 0,  0, 0,  0, 1 ]
        ])
        
        # Measurement matrix (we observe position only)
        kf.H = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0]
        ])
        
        # Process noise
        kf.Q = Q_discrete_white_noise(dim=2, dt=dt, var=process_variance, block_size=3)
        
        # Measurement noise
        kf.R *= measurement_variance
        
        # Initial covariance
        kf.P *= 1000.0
        
        return kf
    
    def _group_landmarks_by_name(self, pose_sequence: List[PoseFrame]) -> Dict[str, List[PoseLandmark]]:
        """Group landmarks by name across all frames"""
        landmark_data = {}
        
        for pose_frame in pose_sequence:
            for landmark in pose_frame.landmarks:
                if landmark.name not in landmark_data:
                    landmark_data[landmark.name] = []
                landmark_data[landmark.name].append(landmark)
        
        return landmark_data
    
    def _interpolate_frames(self, 
                           frame1: PoseFrame, 
                           frame2: PoseFrame, 
                           alpha: float, 
                           new_index: int) -> PoseFrame:
        """Interpolate between two pose frames"""
        interpolated_landmarks = []
        
        # Create lookup for frame2 landmarks
        frame2_landmarks = {lm.name: lm for lm in frame2.landmarks}
        
        for landmark1 in frame1.landmarks:
            if landmark1.name in frame2_landmarks:
                landmark2 = frame2_landmarks[landmark1.name]
                
                # Linear interpolation
                interp_landmark = PoseLandmark(
                    x=landmark1.x + alpha * (landmark2.x - landmark1.x),
                    y=landmark1.y + alpha * (landmark2.y - landmark1.y),
                    z=landmark1.z + alpha * (landmark2.z - landmark1.z),
                    visibility=min(landmark1.visibility, landmark2.visibility),
                    name=landmark1.name,
                    frame_index=new_index
                )
                interpolated_landmarks.append(interp_landmark)
        
        # Create interpolated frame
        return PoseFrame(
            frame_index=new_index,
            timestamp=frame1.timestamp + alpha * (frame2.timestamp - frame1.timestamp),
            landmarks=interpolated_landmarks,
            image_width=frame1.image_width,
            image_height=frame1.image_height,
            detection_confidence=min(frame1.detection_confidence, frame2.detection_confidence)
        )
    
    def _copy_frame_with_index(self, frame: PoseFrame, new_index: int) -> PoseFrame:
        """Copy frame with new index"""
        new_landmarks = []
        for landmark in frame.landmarks:
            new_landmark = PoseLandmark(
                x=landmark.x,
                y=landmark.y,
                z=landmark.z,
                visibility=landmark.visibility,
                name=landmark.name,
                frame_index=new_index
            )
            new_landmarks.append(new_landmark)
        
        return PoseFrame(
            frame_index=new_index,
            timestamp=frame.timestamp,
            landmarks=new_landmarks,
            image_width=frame.image_width,
            image_height=frame.image_height,
            detection_confidence=frame.detection_confidence
        )
    
    def reset(self):
        """Reset all Kalman filters"""
        self.kalman_filters.clear()
        self.initialized_landmarks.clear()
        logger.info("Smoothing filters reset")
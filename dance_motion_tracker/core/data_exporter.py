"""
Data export module for saving pose data in various formats
Compatible with Blender and other 3D animation software
"""
import json
import csv
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import logging
from datetime import datetime

from core.pose_detector import PoseFrame, PoseLandmark
from config.mediapipe_config import BLENDER_BONE_MAPPING, POSE_LANDMARKS

logger = logging.getLogger(__name__)

class DataExporter:
    """
    Handles export of pose data to various formats for use in Blender and other applications
    """
    
    def __init__(self):
        self.supported_formats = ['json', 'csv', 'bvh', 'fbx_data']
        
    def export_to_json(self, 
                      pose_sequence: List[PoseFrame], 
                      output_path: str,
                      include_metadata: bool = True,
                      pretty_print: bool = True) -> bool:
        """
        Export pose sequence to JSON format
        
        Args:
            pose_sequence: List of PoseFrame objects
            output_path: Output JSON file path
            include_metadata: Whether to include metadata
            pretty_print: Whether to format JSON nicely
            
        Returns:
            True if export successful
        """
        try:
            export_data = {
                'format_version': '1.0',
                'export_timestamp': datetime.now().isoformat(),
                'total_frames': len(pose_sequence),
                'pose_data': []
            }
            
            if include_metadata and pose_sequence:
                first_frame = pose_sequence[0]
                export_data['metadata'] = {
                    'image_width': first_frame.image_width,
                    'image_height': first_frame.image_height,
                    'landmark_count': len(first_frame.landmarks),
                    'duration': pose_sequence[-1].timestamp if pose_sequence else 0,
                    'fps': len(pose_sequence) / pose_sequence[-1].timestamp if pose_sequence and pose_sequence[-1].timestamp > 0 else 0
                }
            
            # Convert pose frames to dictionaries
            for pose_frame in pose_sequence:
                frame_data = {
                    'frame_index': pose_frame.frame_index,
                    'timestamp': pose_frame.timestamp,
                    'detection_confidence': pose_frame.detection_confidence,
                    'landmarks': []
                }
                
                for landmark in pose_frame.landmarks:
                    landmark_data = {
                        'name': landmark.name,
                        'x': float(landmark.x),
                        'y': float(landmark.y),
                        'z': float(landmark.z),
                        'visibility': float(landmark.visibility)
                    }
                    frame_data['landmarks'].append(landmark_data)
                
                export_data['pose_data'].append(frame_data)
            
            # Write to file
            with open(output_path, 'w') as f:
                if pretty_print:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(export_data, f, ensure_ascii=False)
            
            logger.info(f"JSON export completed: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {str(e)}")
            return False
    
    def export_to_csv(self, 
                     pose_sequence: List[PoseFrame], 
                     output_path: str,
                     format_type: str = 'wide') -> bool:
        """
        Export pose sequence to CSV format
        
        Args:
            pose_sequence: List of PoseFrame objects
            output_path: Output CSV file path
            format_type: 'wide' (one row per frame) or 'long' (one row per landmark)
            
        Returns:
            True if export successful
        """
        try:
            if format_type == 'wide':
                return self._export_csv_wide(pose_sequence, output_path)
            else:
                return self._export_csv_long(pose_sequence, output_path)
                
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            return False
    
    def _export_csv_wide(self, pose_sequence: List[PoseFrame], output_path: str) -> bool:
        """Export CSV in wide format (one row per frame)"""
        if not pose_sequence:
            logger.warning("No pose data to export")
            return False
        
        # Create column headers
        headers = ['frame_index', 'timestamp', 'detection_confidence']
        
        # Add columns for each landmark (x, y, z, visibility)
        landmark_names = [lm.name for lm in pose_sequence[0].landmarks]
        for name in landmark_names:
            headers.extend([f'{name}_x', f'{name}_y', f'{name}_z', f'{name}_visibility'])
        
        # Prepare data rows
        rows = []
        for pose_frame in pose_sequence:
            row = [
                pose_frame.frame_index,
                pose_frame.timestamp,
                pose_frame.detection_confidence
            ]
            
            # Create landmark lookup
            landmark_dict = {lm.name: lm for lm in pose_frame.landmarks}
            
            # Add landmark data in consistent order
            for name in landmark_names:
                if name in landmark_dict:
                    lm = landmark_dict[name]
                    row.extend([lm.x, lm.y, lm.z, lm.visibility])
                else:
                    # Missing landmark
                    row.extend([np.nan, np.nan, np.nan, 0.0])
            
            rows.append(row)
        
        # Write CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        logger.info(f"CSV (wide) export completed: {output_path}")
        return True
    
    def _export_csv_long(self, pose_sequence: List[PoseFrame], output_path: str) -> bool:
        """Export CSV in long format (one row per landmark)"""
        headers = [
            'frame_index', 'timestamp', 'detection_confidence',
            'landmark_name', 'x', 'y', 'z', 'visibility'
        ]
        
        rows = []
        for pose_frame in pose_sequence:
            for landmark in pose_frame.landmarks:
                row = [
                    pose_frame.frame_index,
                    pose_frame.timestamp,
                    pose_frame.detection_confidence,
                    landmark.name,
                    landmark.x,
                    landmark.y,
                    landmark.z,
                    landmark.visibility
                ]
                rows.append(row)
        
        # Write CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        logger.info(f"CSV (long) export completed: {output_path}")
        return True
    
    def export_for_blender(self, 
                          pose_sequence: List[PoseFrame], 
                          output_path: str,
                          rig_type: str = 'mixamo') -> bool:
        """
        Export pose data specifically formatted for Blender import
        
        Args:
            pose_sequence: List of PoseFrame objects
            output_path: Output JSON file path
            rig_type: Type of rig ('mixamo', 'rigify', 'custom')
            
        Returns:
            True if export successful
        """
        try:
            blender_data = {
                'format': 'blender_pose_data',
                'version': '1.0',
                'rig_type': rig_type,
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'total_frames': len(pose_sequence),
                    'fps': 30.0,  # Default FPS, can be adjusted
                    'frame_start': 1,
                    'frame_end': len(pose_sequence)
                },
                'bone_mapping': self._get_bone_mapping(rig_type),
                'animation_data': []
            }
            
            # Process each frame
            for pose_frame in pose_sequence:
                frame_data = {
                    'frame': pose_frame.frame_index + 1,  # Blender frames start at 1
                    'timestamp': pose_frame.timestamp,
                    'bones': {}
                }
                
                # Convert landmarks to bone data
                landmark_dict = {lm.name: lm for lm in pose_frame.landmarks}
                
                for bone_name, landmark_name in BLENDER_BONE_MAPPING.items():
                    if landmark_name in landmark_dict:
                        landmark = landmark_dict[landmark_name]
                        
                        # Convert to Blender coordinate system (Y up, Z forward)
                        bone_data = {
                            'location': [
                                float(landmark.x),
                                float(-landmark.z),  # Convert Z to Y-up system
                                float(-landmark.y)   # Convert Y to Z-forward system
                            ],
                            'rotation': [0.0, 0.0, 0.0],  # Placeholder for rotation
                            'scale': [1.0, 1.0, 1.0],
                            'visibility': float(landmark.visibility)
                        }
                        
                        frame_data['bones'][bone_name] = bone_data
                
                blender_data['animation_data'].append(frame_data)
            
            # Write to file
            with open(output_path, 'w') as f:
                json.dump(blender_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Blender export completed: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting for Blender: {str(e)}")
            return False
    
    def export_bvh(self, 
                   pose_sequence: List[PoseFrame], 
                   output_path: str,
                   fps: float = 30.0) -> bool:
        """
        Export pose data as BVH (Biovision Hierarchy) format
        
        Args:
            pose_sequence: List of PoseFrame objects
            output_path: Output BVH file path
            fps: Frame rate for animation
            
        Returns:
            True if export successful
        """
        try:
            # BVH header
            bvh_content = self._generate_bvh_header()
            
            # Motion data
            frame_time = 1.0 / fps
            bvh_content += f"MOTION\n"
            bvh_content += f"Frames: {len(pose_sequence)}\n"
            bvh_content += f"Frame Time: {frame_time}\n"
            
            # Frame data
            for pose_frame in pose_sequence:
                frame_values = self._convert_pose_to_bvh_frame(pose_frame)
                bvh_content += " ".join(map(str, frame_values)) + "\n"
            
            # Write to file
            with open(output_path, 'w') as f:
                f.write(bvh_content)
            
            logger.info(f"BVH export completed: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting BVH: {str(e)}")
            return False
    
    def export_summary_stats(self, 
                           pose_sequence: List[PoseFrame], 
                           output_path: str) -> bool:
        """
        Export summary statistics about the pose data
        
        Args:
            pose_sequence: List of PoseFrame objects
            output_path: Output JSON file path
            
        Returns:
            True if export successful
        """
        try:
            if not pose_sequence:
                logger.warning("No pose data for statistics")
                return False
            
            # Calculate statistics
            stats = {
                'general': {
                    'total_frames': len(pose_sequence),
                    'duration': pose_sequence[-1].timestamp if pose_sequence else 0,
                    'avg_fps': len(pose_sequence) / pose_sequence[-1].timestamp if pose_sequence and pose_sequence[-1].timestamp > 0 else 0,
                    'image_dimensions': {
                        'width': pose_sequence[0].image_width,
                        'height': pose_sequence[0].image_height
                    }
                },
                'confidence': {
                    'mean': np.mean([frame.detection_confidence for frame in pose_sequence]),
                    'std': np.std([frame.detection_confidence for frame in pose_sequence]),
                    'min': np.min([frame.detection_confidence for frame in pose_sequence]),
                    'max': np.max([frame.detection_confidence for frame in pose_sequence])
                },
                'landmarks': {}
            }
            
            # Per-landmark statistics
            if pose_sequence[0].landmarks:
                landmark_names = [lm.name for lm in pose_sequence[0].landmarks]
                
                for name in landmark_names:
                    visibility_values = []
                    x_values = []
                    y_values = []
                    z_values = []
                    
                    for frame in pose_sequence:
                        landmark = next((lm for lm in frame.landmarks if lm.name == name), None)
                        if landmark:
                            visibility_values.append(landmark.visibility)
                            x_values.append(landmark.x)
                            y_values.append(landmark.y)
                            z_values.append(landmark.z)
                    
                    if visibility_values:
                        stats['landmarks'][name] = {
                            'visibility': {
                                'mean': np.mean(visibility_values),
                                'std': np.std(visibility_values),
                                'detection_rate': np.mean([v > 0.5 for v in visibility_values])
                            },
                            'position': {
                                'x_range': [np.min(x_values), np.max(x_values)],
                                'y_range': [np.min(y_values), np.max(y_values)],
                                'z_range': [np.min(z_values), np.max(z_values)],
                                'movement_distance': self._calculate_total_distance(x_values, y_values, z_values)
                            }
                        }
            
            # Write statistics
            with open(output_path, 'w') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False, default=float)
            
            logger.info(f"Statistics export completed: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting statistics: {str(e)}")
            return False
    
    def load_from_json(self, input_path: str) -> Optional[List[PoseFrame]]:
        """
        Load pose sequence from JSON file
        
        Args:
            input_path: Input JSON file path
            
        Returns:
            List of PoseFrame objects or None if failed
        """
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)
            
            pose_sequence = []
            
            for frame_data in data.get('pose_data', []):
                landmarks = []
                
                for lm_data in frame_data.get('landmarks', []):
                    landmark = PoseLandmark(
                        x=lm_data['x'],
                        y=lm_data['y'],
                        z=lm_data['z'],
                        visibility=lm_data['visibility'],
                        name=lm_data['name'],
                        frame_index=frame_data['frame_index']
                    )
                    landmarks.append(landmark)
                
                pose_frame = PoseFrame(
                    frame_index=frame_data['frame_index'],
                    timestamp=frame_data['timestamp'],
                    landmarks=landmarks,
                    image_width=data.get('metadata', {}).get('image_width', 1920),
                    image_height=data.get('metadata', {}).get('image_height', 1080),
                    detection_confidence=frame_data['detection_confidence']
                )
                
                pose_sequence.append(pose_frame)
            
            logger.info(f"Loaded {len(pose_sequence)} frames from {input_path}")
            return pose_sequence
            
        except Exception as e:
            logger.error(f"Error loading from JSON: {str(e)}")
            return None
    
    def _get_bone_mapping(self, rig_type: str) -> Dict[str, str]:
        """Get bone mapping for specific rig type"""
        if rig_type == 'mixamo':
            return BLENDER_BONE_MAPPING
        elif rig_type == 'rigify':
            # Rigify bone names (can be customized)
            return BLENDER_BONE_MAPPING  # Use same mapping for now
        else:
            return BLENDER_BONE_MAPPING
    
    def _generate_bvh_header(self) -> str:
        """Generate BVH file header with hierarchy"""
        header = """HIERARCHY
ROOT Hips
{
    OFFSET 0.0 0.0 0.0
    CHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation
    JOINT Spine
    {
        OFFSET 0.0 5.0 0.0
        CHANNELS 3 Zrotation Xrotation Yrotation
        JOINT Chest
        {
            OFFSET 0.0 10.0 0.0
            CHANNELS 3 Zrotation Xrotation Yrotation
            JOINT LeftShoulder
            {
                OFFSET 5.0 0.0 0.0
                CHANNELS 3 Zrotation Xrotation Yrotation
                JOINT LeftArm
                {
                    OFFSET 10.0 0.0 0.0
                    CHANNELS 3 Zrotation Xrotation Yrotation
                    End Site
                    {
                        OFFSET 10.0 0.0 0.0
                    }
                }
            }
            JOINT RightShoulder
            {
                OFFSET -5.0 0.0 0.0
                CHANNELS 3 Zrotation Xrotation Yrotation
                JOINT RightArm
                {
                    OFFSET -10.0 0.0 0.0
                    CHANNELS 3 Zrotation Xrotation Yrotation
                    End Site
                    {
                        OFFSET -10.0 0.0 0.0
                    }
                }
            }
        }
    }
    JOINT LeftHip
    {
        OFFSET 5.0 -5.0 0.0
        CHANNELS 3 Zrotation Xrotation Yrotation
        JOINT LeftKnee
        {
            OFFSET 0.0 -15.0 0.0
            CHANNELS 3 Zrotation Xrotation Yrotation
            End Site
            {
                OFFSET 0.0 -15.0 0.0
            }
        }
    }
    JOINT RightHip
    {
        OFFSET -5.0 -5.0 0.0
        CHANNELS 3 Zrotation Xrotation Yrotation
        JOINT RightKnee
        {
            OFFSET 0.0 -15.0 0.0
            CHANNELS 3 Zrotation Xrotation Yrotation
            End Site
            {
                OFFSET 0.0 -15.0 0.0
            }
        }
    }
}
"""
        return header
    
    def _convert_pose_to_bvh_frame(self, pose_frame: PoseFrame) -> List[float]:
        """Convert pose frame to BVH frame values"""
        # This is a simplified conversion - in practice, you'd need to
        # calculate proper joint rotations from the pose landmarks
        values = []
        
        # Root position (using hip center)
        left_hip = next((lm for lm in pose_frame.landmarks if lm.name == 'LEFT_HIP'), None)
        right_hip = next((lm for lm in pose_frame.landmarks if lm.name == 'RIGHT_HIP'), None)
        
        if left_hip and right_hip:
            hip_center_x = (left_hip.x + right_hip.x) / 2
            hip_center_y = (left_hip.y + right_hip.y) / 2
            hip_center_z = (left_hip.z + right_hip.z) / 2
            values.extend([hip_center_x, hip_center_y, hip_center_z, 0.0, 0.0, 0.0])
        else:
            values.extend([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        
        # Joint rotations (simplified - all zeros for now)
        # In a full implementation, these would be calculated from landmark positions
        num_joints = 8  # Number of joints in the hierarchy
        for _ in range(num_joints):
            values.extend([0.0, 0.0, 0.0])  # 3 rotation channels per joint
        
        return values
    
    def _calculate_total_distance(self, x_values: List[float], y_values: List[float], z_values: List[float]) -> float:
        """Calculate total movement distance for a landmark"""
        total_distance = 0.0
        
        for i in range(1, len(x_values)):
            dx = x_values[i] - x_values[i-1]
            dy = y_values[i] - y_values[i-1]
            dz = z_values[i] - z_values[i-1]
            distance = np.sqrt(dx*dx + dy*dy + dz*dz)
            total_distance += distance
        
        return total_distance
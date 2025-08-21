"""
Video processing module for handling input/output and format conversion
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any, Callable
import logging
import tempfile
import subprocess
import json

logger = logging.getLogger(__name__)

class VideoProcessor:
    """
    Handles video input/output, format conversion, and basic processing
    """
    
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
        self.default_codec = 'mp4v'
        
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a video file
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video properties
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            return {}
        
        info = {
            'path': video_path,
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS),
            'codec': int(cap.get(cv2.CAP_PROP_FOURCC)),
            'format': Path(video_path).suffix.lower()
        }
        
        # Convert codec to string
        codec_int = int(info['codec'])
        info['codec_str'] = ''.join([chr((codec_int >> 8 * i) & 0xFF) for i in range(4)])
        
        cap.release()
        
        logger.info(f"Video info: {info['width']}x{info['height']} @ {info['fps']} FPS, {info['frame_count']} frames")
        return info
    
    def validate_video(self, video_path: str) -> Tuple[bool, str]:
        """
        Validate if video file is readable and supported
        
        Args:
            video_path: Path to video file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not Path(video_path).exists():
            return False, f"File does not exist: {video_path}"
        
        if not Path(video_path).suffix.lower() in self.supported_formats:
            return False, f"Unsupported format: {Path(video_path).suffix}"
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False, "Could not open video file"
        
        # Try to read first frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return False, "Could not read video frames"
        
        return True, "Video is valid"
    
    def convert_video_format(self, 
                           input_path: str, 
                           output_path: str,
                           target_fps: Optional[float] = None,
                           target_resolution: Optional[Tuple[int, int]] = None,
                           quality: int = 23) -> bool:
        """
        Convert video to different format/settings using FFmpeg
        
        Args:
            input_path: Input video path
            output_path: Output video path
            target_fps: Target frame rate (None to keep original)
            target_resolution: Target resolution as (width, height)
            quality: Video quality (lower = better quality, 18-28 recommended)
            
        Returns:
            True if conversion successful
        """
        try:
            cmd = ['ffmpeg', '-i', input_path, '-y']  # -y to overwrite output
            
            # Set video codec
            cmd.extend(['-c:v', 'libx264'])
            
            # Set quality
            cmd.extend(['-crf', str(quality)])
            
            # Set frame rate if specified
            if target_fps:
                cmd.extend(['-r', str(target_fps)])
            
            # Set resolution if specified
            if target_resolution:
                cmd.extend(['-vf', f'scale={target_resolution[0]}:{target_resolution[1]}'])
            
            # Set audio codec
            cmd.extend(['-c:a', 'aac'])
            
            cmd.append(output_path)
            
            logger.info(f"Converting video: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Video converted successfully: {output_path}")
                return True
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("FFmpeg not found. Please install FFmpeg for video conversion.")
            return False
        except Exception as e:
            logger.error(f"Error converting video: {str(e)}")
            return False
    
    def extract_frames(self, 
                      video_path: str, 
                      output_dir: str,
                      frame_interval: int = 1,
                      max_frames: Optional[int] = None) -> List[str]:
        """
        Extract frames from video as image files
        
        Args:
            video_path: Input video path
            output_dir: Directory to save frames
            frame_interval: Extract every nth frame
            max_frames: Maximum number of frames to extract
            
        Returns:
            List of extracted frame file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            return []
        
        frame_paths = []
        frame_count = 0
        extracted_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Extract frame at specified interval
                if frame_count % frame_interval == 0:
                    frame_filename = f"frame_{frame_count:06d}.jpg"
                    frame_path = output_path / frame_filename
                    
                    cv2.imwrite(str(frame_path), frame)
                    frame_paths.append(str(frame_path))
                    extracted_count += 1
                    
                    if max_frames and extracted_count >= max_frames:
                        break
                
                frame_count += 1
                
        except Exception as e:
            logger.error(f"Error extracting frames: {str(e)}")
        finally:
            cap.release()
        
        logger.info(f"Extracted {len(frame_paths)} frames to {output_dir}")
        return frame_paths
    
    def create_video_from_frames(self, 
                                frame_paths: List[str], 
                                output_path: str,
                                fps: float = 30.0,
                                codec: str = 'mp4v') -> bool:
        """
        Create video from sequence of frame images
        
        Args:
            frame_paths: List of frame image paths
            output_path: Output video path
            fps: Frame rate for output video
            codec: Video codec to use
            
        Returns:
            True if video created successfully
        """
        if not frame_paths:
            logger.error("No frame paths provided")
            return False
        
        # Read first frame to get dimensions
        first_frame = cv2.imread(frame_paths[0])
        if first_frame is None:
            logger.error(f"Could not read first frame: {frame_paths[0]}")
            return False
        
        height, width = first_frame.shape[:2]
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*codec)
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not writer.isOpened():
            logger.error("Could not initialize video writer")
            return False
        
        try:
            for frame_path in frame_paths:
                frame = cv2.imread(frame_path)
                if frame is not None:
                    # Resize frame if dimensions don't match
                    if frame.shape[:2] != (height, width):
                        frame = cv2.resize(frame, (width, height))
                    writer.write(frame)
                else:
                    logger.warning(f"Could not read frame: {frame_path}")
            
            writer.release()
            logger.info(f"Video created successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating video: {str(e)}")
            writer.release()
            return False
    
    def resize_video(self, 
                    input_path: str, 
                    output_path: str,
                    target_resolution: Tuple[int, int],
                    maintain_aspect_ratio: bool = True) -> bool:
        """
        Resize video to target resolution
        
        Args:
            input_path: Input video path
            output_path: Output video path
            target_resolution: Target (width, height)
            maintain_aspect_ratio: Whether to maintain aspect ratio
            
        Returns:
            True if resize successful
        """
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            logger.error(f"Could not open input video: {input_path}")
            return False
        
        # Get original properties
        original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Calculate target dimensions
        target_width, target_height = target_resolution
        
        if maintain_aspect_ratio:
            # Calculate scaling factor
            scale_x = target_width / original_width
            scale_y = target_height / original_height
            scale = min(scale_x, scale_y)
            
            # Calculate new dimensions
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            # Center the video in target resolution
            pad_x = (target_width - new_width) // 2
            pad_y = (target_height - new_height) // 2
        else:
            new_width, new_height = target_width, target_height
            pad_x, pad_y = 0, 0
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (target_width, target_height))
        
        if not writer.isOpened():
            logger.error("Could not initialize video writer")
            cap.release()
            return False
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Resize frame
                if maintain_aspect_ratio:
                    resized_frame = cv2.resize(frame, (new_width, new_height))
                    
                    # Create padded frame
                    padded_frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)
                    padded_frame[pad_y:pad_y+new_height, pad_x:pad_x+new_width] = resized_frame
                    
                    writer.write(padded_frame)
                else:
                    resized_frame = cv2.resize(frame, (target_width, target_height))
                    writer.write(resized_frame)
            
            cap.release()
            writer.release()
            
            logger.info(f"Video resized successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error resizing video: {str(e)}")
            cap.release()
            writer.release()
            return False
    
    def trim_video(self, 
                  input_path: str, 
                  output_path: str,
                  start_time: float, 
                  end_time: float) -> bool:
        """
        Trim video to specified time range
        
        Args:
            input_path: Input video path
            output_path: Output video path
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            True if trim successful
        """
        try:
            cmd = [
                'ffmpeg', '-i', input_path,
                '-ss', str(start_time),
                '-t', str(end_time - start_time),
                '-c', 'copy',  # Copy without re-encoding for speed
                '-y', output_path
            ]
            
            logger.info(f"Trimming video: {start_time}s to {end_time}s")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Video trimmed successfully: {output_path}")
                return True
            else:
                logger.error(f"FFmpeg trim error: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error trimming video: {str(e)}")
            return False
    
    def get_frame_at_time(self, video_path: str, timestamp: float) -> Optional[np.ndarray]:
        """
        Extract single frame at specific timestamp
        
        Args:
            video_path: Input video path
            timestamp: Time in seconds
            
        Returns:
            Frame as numpy array or None if failed
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            return None
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(timestamp * fps)
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            return frame
        else:
            logger.error(f"Could not read frame at timestamp {timestamp}")
            return None
    
    def create_thumbnail(self, 
                        video_path: str, 
                        output_path: str,
                        timestamp: float = 1.0,
                        size: Tuple[int, int] = (320, 240)) -> bool:
        """
        Create thumbnail image from video
        
        Args:
            video_path: Input video path
            output_path: Output image path
            timestamp: Time to extract thumbnail (seconds)
            size: Thumbnail size (width, height)
            
        Returns:
            True if thumbnail created successfully
        """
        frame = self.get_frame_at_time(video_path, timestamp)
        
        if frame is None:
            return False
        
        # Resize to thumbnail size
        thumbnail = cv2.resize(frame, size)
        
        # Save thumbnail
        success = cv2.imwrite(output_path, thumbnail)
        
        if success:
            logger.info(f"Thumbnail created: {output_path}")
        else:
            logger.error(f"Failed to save thumbnail: {output_path}")
        
        return success
"""
Utility functions for the Flask web application
"""
import os
from pathlib import Path
from typing import List, Optional
import mimetypes

def allowed_file(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Check if uploaded file has allowed extension
    
    Args:
        filename: Name of the uploaded file
        allowed_extensions: List of allowed file extensions (with dots)
        
    Returns:
        True if file extension is allowed
    """
    if not filename:
        return False
    
    file_extension = Path(filename).suffix.lower()
    return file_extension in allowed_extensions

def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes, 0 if file doesn't exist
    """
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "2:30")
    """
    if seconds < 0:
        return "0:00"
    
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    
    if minutes >= 60:
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def get_mime_type(file_path: str) -> Optional[str]:
    """
    Get MIME type of file
    
    Args:
        file_path: Path to file
        
    Returns:
        MIME type string or None if unknown
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type

def safe_filename(filename: str, max_length: int = 255) -> str:
    """
    Create safe filename by removing/replacing problematic characters
    
    Args:
        filename: Original filename
        max_length: Maximum length for filename
        
    Returns:
        Safe filename
    """
    # Remove or replace problematic characters
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
    safe_name = ''.join(c if c in safe_chars else '_' for c in filename)
    
    # Ensure it's not too long
    if len(safe_name) > max_length:
        name_part = Path(safe_name).stem
        ext_part = Path(safe_name).suffix
        
        max_name_length = max_length - len(ext_part)
        if max_name_length > 0:
            safe_name = name_part[:max_name_length] + ext_part
        else:
            safe_name = safe_name[:max_length]
    
    return safe_name

def create_thumbnail_name(original_filename: str) -> str:
    """
    Create thumbnail filename from original filename
    
    Args:
        original_filename: Original file name
        
    Returns:
        Thumbnail filename
    """
    name_part = Path(original_filename).stem
    return f"{name_part}_thumbnail.jpg"

def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format
    
    Args:
        session_id: Session ID to validate
        
    Returns:
        True if valid UUID format
    """
    import re
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(session_id))

def cleanup_old_files(directory: str, max_age_hours: int = 24) -> int:
    """
    Clean up files older than specified age
    
    Args:
        directory: Directory to clean
        max_age_hours: Maximum age in hours
        
    Returns:
        Number of files deleted
    """
    import time
    
    if not os.path.exists(directory):
        return 0
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    deleted_count = 0
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                
                try:
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        deleted_count += 1
                except OSError:
                    continue  # Skip files that can't be accessed
            
            # Remove empty directories
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):  # Directory is empty
                        os.rmdir(dir_path)
                except OSError:
                    continue
    
    except Exception:
        pass  # Ignore cleanup errors
    
    return deleted_count
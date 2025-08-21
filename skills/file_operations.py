"""
ZENO File Operations Skill
Handles file and folder operations
"""
import os
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Dict, Any

from .skill_manager import BaseSkill

class FileOperationsSkill(BaseSkill):
    """Handles file and folder operations"""
    
    def __init__(self):
        super().__init__()
        self.is_windows = platform.system() == "Windows"
        
        # Safe base directories for file operations
        self.safe_directories = [
            Path.home() / "Documents",
            Path.home() / "Desktop",
            Path.home() / "Downloads",
            Path.cwd()  # Current working directory
        ]
    
    async def execute(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file operations command"""
        try:
            if command == "file_operations":
                return await self._file_operations(parameters)
            else:
                return self._create_result(False, f"Unknown file operations command: {command}")
                
        except Exception as e:
            return self._create_result(False, f"File operations error: {str(e)}")
    
    async def _file_operations(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform file operations"""
        action = parameters.get("action")
        path = parameters.get("path")
        name = parameters.get("name")
        
        if not action:
            return self._create_result(False, "File operation action is required")
        
        try:
            if action == "create_file":
                return await self._create_file(name, path)
            elif action == "create_folder":
                return await self._create_folder(name, path)
            elif action == "delete":
                return await self._delete_item(path or name)
            elif action == "open":
                return await self._open_item(path or name)
            elif action == "list":
                return await self._list_directory(path)
            else:
                return self._create_result(False, f"Unknown file operation: {action}")
                
        except Exception as e:
            return self._create_result(False, f"File operation error: {str(e)}")
    
    async def _create_file(self, name: str, path: str = None) -> Dict[str, Any]:
        """Create a new file"""
        if not name:
            return self._create_result(False, "File name is required")
        
        try:
            # Determine target directory
            if path:
                target_dir = Path(path)
            else:
                target_dir = Path.home() / "Documents"
            
            # Security check
            if not self._is_safe_path(target_dir):
                return self._create_result(False, "Access to this directory is not allowed")
            
            # Create directory if it doesn't exist
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Create file path
            file_path = target_dir / name
            
            # Check if file already exists
            if file_path.exists():
                return self._create_result(False, f"File already exists: {file_path}")
            
            # Create the file
            file_path.touch()
            
            return self._create_result(
                True, 
                f"Created file: {file_path}",
                {"path": str(file_path)}
            )
            
        except Exception as e:
            return self._create_result(False, f"Error creating file: {str(e)}")
    
    async def _create_folder(self, name: str, path: str = None) -> Dict[str, Any]:
        """Create a new folder"""
        if not name:
            return self._create_result(False, "Folder name is required")
        
        try:
            # Determine target directory
            if path:
                target_dir = Path(path)
            else:
                target_dir = Path.home() / "Documents"
            
            # Security check
            if not self._is_safe_path(target_dir):
                return self._create_result(False, "Access to this directory is not allowed")
            
            # Create folder path
            folder_path = target_dir / name
            
            # Check if folder already exists
            if folder_path.exists():
                return self._create_result(False, f"Folder already exists: {folder_path}")
            
            # Create the folder
            folder_path.mkdir(parents=True)
            
            return self._create_result(
                True, 
                f"Created folder: {folder_path}",
                {"path": str(folder_path)}
            )
            
        except Exception as e:
            return self._create_result(False, f"Error creating folder: {str(e)}")
    
    async def _delete_item(self, path: str) -> Dict[str, Any]:
        """Delete a file or folder"""
        if not path:
            return self._create_result(False, "Path is required for deletion")
        
        try:
            item_path = Path(path)
            
            # Security check
            if not self._is_safe_path(item_path.parent):
                return self._create_result(False, "Access to this directory is not allowed")
            
            # Check if item exists
            if not item_path.exists():
                return self._create_result(False, f"Item does not exist: {item_path}")
            
            # Confirm deletion for safety
            if item_path.is_file():
                item_path.unlink()
                return self._create_result(True, f"Deleted file: {item_path}")
            elif item_path.is_dir():
                shutil.rmtree(item_path)
                return self._create_result(True, f"Deleted folder: {item_path}")
            else:
                return self._create_result(False, f"Unknown item type: {item_path}")
                
        except Exception as e:
            return self._create_result(False, f"Error deleting item: {str(e)}")
    
    async def _open_item(self, path: str) -> Dict[str, Any]:
        """Open a file or folder"""
        if not path:
            return self._create_result(False, "Path is required")
        
        try:
            item_path = Path(path)
            
            # Check if item exists
            if not item_path.exists():
                return self._create_result(False, f"Item does not exist: {item_path}")
            
            # Open based on platform
            if self.is_windows:
                os.startfile(str(item_path))
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(item_path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(item_path)])
            
            return self._create_result(True, f"Opened: {item_path}")
            
        except Exception as e:
            return self._create_result(False, f"Error opening item: {str(e)}")
    
    async def _list_directory(self, path: str = None) -> Dict[str, Any]:
        """List directory contents"""
        try:
            if path:
                target_dir = Path(path)
            else:
                target_dir = Path.cwd()
            
            # Security check
            if not self._is_safe_path(target_dir):
                return self._create_result(False, "Access to this directory is not allowed")
            
            # Check if directory exists
            if not target_dir.exists() or not target_dir.is_dir():
                return self._create_result(False, f"Directory does not exist: {target_dir}")
            
            # List contents
            items = []
            for item in target_dir.iterdir():
                items.append({
                    "name": item.name,
                    "type": "folder" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "path": str(item)
                })
            
            return self._create_result(
                True, 
                f"Listed {len(items)} items in {target_dir}",
                {"items": items, "directory": str(target_dir)}
            )
            
        except Exception as e:
            return self._create_result(False, f"Error listing directory: {str(e)}")
    
    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is within safe directories"""
        try:
            path = path.resolve()
            
            # Check against safe directories
            for safe_dir in self.safe_directories:
                try:
                    safe_dir = safe_dir.resolve()
                    if path == safe_dir or safe_dir in path.parents:
                        return True
                except:
                    continue
            
            # Additional safety checks
            path_str = str(path).lower()
            
            # Block system directories
            dangerous_paths = [
                "system32", "windows", "/bin", "/sbin", "/usr/bin",
                "/etc", "/boot", "program files", "programdata"
            ]
            
            for dangerous in dangerous_paths:
                if dangerous in path_str:
                    return False
            
            return False
            
        except Exception:
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Get skill information"""
        return {
            "name": "File Operations",
            "description": "Create, delete, and manage files and folders",
            "commands": ["file_operations"],
            "parameters": {
                "file_operations": ["action", "name", "path"]
            },
            "examples": [
                "Create file test.txt",
                "Create folder MyProject",
                "Open Documents folder",
                "List current directory"
            ],
            "supported_actions": ["create_file", "create_folder", "delete", "open", "list"],
            "safety_note": "Operations are restricted to safe directories for security"
        }
"""
ZENO Media Control Skill
Handles media playback control
"""
import platform
import subprocess
from typing import Dict, Any

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None

from .skill_manager import BaseSkill

class MediaControlSkill(BaseSkill):
    """Handles media playback control operations"""
    
    def __init__(self):
        super().__init__()
        self.is_windows = platform.system() == "Windows"
        self.is_macos = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"
    
    async def execute(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute media control command"""
        try:
            if command == "media_control":
                return await self._media_control(parameters)
            else:
                return self._create_result(False, f"Unknown media control command: {command}")
                
        except Exception as e:
            return self._create_result(False, f"Media control error: {str(e)}")
    
    async def _media_control(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Control media playback"""
        action = parameters.get("action")
        
        if not action:
            return self._create_result(False, "Media action is required")
        
        try:
            success = False
            message = ""
            
            if action == "play":
                success = await self._send_media_key("play")
                message = "Play command sent"
                
            elif action == "pause":
                success = await self._send_media_key("pause")
                message = "Pause command sent"
                
            elif action == "stop":
                success = await self._send_media_key("stop")
                message = "Stop command sent"
                
            elif action == "next":
                success = await self._send_media_key("nexttrack")
                message = "Next track command sent"
                
            elif action == "previous":
                success = await self._send_media_key("prevtrack")
                message = "Previous track command sent"
                
            else:
                return self._create_result(False, f"Unknown media action: {action}")
            
            if success:
                return self._create_result(True, message)
            else:
                return self._create_result(False, f"Failed to execute media action: {action}")
                
        except Exception as e:
            return self._create_result(False, f"Media control error: {str(e)}")
    
    async def _send_media_key(self, key: str) -> bool:
        """Send media key command"""
        try:
            if self.is_windows:
                return await self._send_media_key_windows(key)
            elif self.is_macos:
                return await self._send_media_key_macos(key)
            elif self.is_linux:
                return await self._send_media_key_linux(key)
            else:
                self.logger.warning("Unsupported platform for media control")
                return False
                
        except Exception as e:
            self.logger.error(f"Media key error: {e}")
            return False
    
    async def _send_media_key_windows(self, key: str) -> bool:
        """Send media key on Windows"""
        if not PYAUTOGUI_AVAILABLE:
            self.logger.warning("pyautogui not available for media control")
            return False
        
        key_mapping = {
            "play": "playpause",
            "pause": "playpause",
            "stop": "stop",
            "nexttrack": "nexttrack",
            "prevtrack": "prevtrack"
        }
        
        mapped_key = key_mapping.get(key)
        if not mapped_key:
            return False
        
        try:
            pyautogui.press(mapped_key)
            return True
        except Exception as e:
            self.logger.error(f"Windows media key error: {e}")
            return False
    
    async def _send_media_key_macos(self, key: str) -> bool:
        """Send media key on macOS"""
        key_mapping = {
            "play": "tell application \"Music\" to play",
            "pause": "tell application \"Music\" to pause",
            "stop": "tell application \"Music\" to stop",
            "nexttrack": "tell application \"Music\" to next track",
            "prevtrack": "tell application \"Music\" to previous track"
        }
        
        command = key_mapping.get(key)
        if not command:
            return False
        
        try:
            subprocess.run(["osascript", "-e", command], check=True)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"macOS media control error: {e}")
            return False
    
    async def _send_media_key_linux(self, key: str) -> bool:
        """Send media key on Linux"""
        # Try playerctl first (most common)
        try:
            key_mapping = {
                "play": "play",
                "pause": "pause",
                "stop": "stop",
                "nexttrack": "next",
                "prevtrack": "previous"
            }
            
            mapped_key = key_mapping.get(key)
            if not mapped_key:
                return False
            
            subprocess.run(["playerctl", mapped_key], check=True)
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to xdotool if available
            try:
                key_mapping = {
                    "play": "XF86AudioPlay",
                    "pause": "XF86AudioPause",
                    "stop": "XF86AudioStop",
                    "nexttrack": "XF86AudioNext",
                    "prevtrack": "XF86AudioPrev"
                }
                
                mapped_key = key_mapping.get(key)
                if not mapped_key:
                    return False
                
                subprocess.run(["xdotool", "key", mapped_key], check=True)
                return True
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.logger.error("Neither playerctl nor xdotool available for media control")
                return False
    
    def get_info(self) -> Dict[str, Any]:
        """Get skill information"""
        return {
            "name": "Media Control",
            "description": "Control media playback (play, pause, next, previous)",
            "commands": ["media_control"],
            "parameters": {
                "media_control": ["action"]
            },
            "examples": [
                "Zeno, play music",
                "Zeno, pause",
                "Zeno, next song",
                "Zeno, previous track"
            ],
            "supported_actions": ["play", "pause", "stop", "next", "previous"],
            "platform_support": {
                "windows": "pyautogui required",
                "macos": "AppleScript (Music app)",
                "linux": "playerctl or xdotool required"
            }
        }
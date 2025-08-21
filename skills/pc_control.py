"""
ZENO PC Control Skill
Handles Windows PC control operations
"""
import os
import subprocess
import psutil
from typing import Dict, Any
import platform

# Windows-specific imports (will be handled gracefully on other platforms)
try:
    import pyautogui
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    from ctypes import cast, POINTER
    from comtypes import CoInitialize, CoUninitialize
    WINDOWS_LIBS_AVAILABLE = platform.system() == "Windows"
except ImportError:
    WINDOWS_LIBS_AVAILABLE = False
    pyautogui = None

from config import Config
from .skill_manager import BaseSkill

class PCControlSkill(BaseSkill):
    """Handles PC control operations like app launching, volume control, etc."""
    
    def __init__(self):
        super().__init__()
        self.is_windows = platform.system() == "Windows"
        
        if self.is_windows and WINDOWS_LIBS_AVAILABLE:
            try:
                CoInitialize()
                self._init_volume_control()
            except Exception as e:
                self.logger.warning(f"Could not initialize Windows audio control: {e}")
    
    def _init_volume_control(self):
        """Initialize Windows volume control"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            self.logger.error(f"Volume control initialization failed: {e}")
            self.volume = None
    
    async def execute(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute PC control command"""
        try:
            if command == "open_app":
                return await self._open_app(parameters.get("app_name"))
            elif command == "close_app":
                return await self._close_app(parameters.get("app_name"))
            elif command == "volume_control":
                return await self._volume_control(parameters)
            elif command == "system_control":
                return await self._system_control(parameters)
            else:
                return self._create_result(False, f"Unknown PC control command: {command}")
                
        except Exception as e:
            return self._create_result(False, f"PC control error: {str(e)}")
    
    async def _open_app(self, app_name: str) -> Dict[str, Any]:
        """Open an application"""
        if not app_name:
            return self._create_result(False, "App name is required")
        
        app_name = app_name.lower().strip()
        
        # Check if app is in allowed list
        if Config.ENABLE_PC_CONTROL and app_name not in Config.ALLOWED_APPS:
            return self._create_result(
                False, 
                f"App '{app_name}' is not in the allowed apps list for security"
            )
        
        try:
            if self.is_windows:
                success = await self._open_app_windows(app_name)
            else:
                success = await self._open_app_cross_platform(app_name)
            
            if success:
                return self._create_result(True, f"Successfully opened {app_name}")
            else:
                return self._create_result(False, f"Could not open {app_name}")
                
        except Exception as e:
            return self._create_result(False, f"Error opening {app_name}: {str(e)}")
    
    async def _open_app_windows(self, app_name: str) -> bool:
        """Open app on Windows"""
        app_commands = {
            "notepad": "notepad",
            "calculator": "calc",
            "chrome": "chrome",
            "firefox": "firefox",
            "explorer": "explorer",
            "cmd": "cmd",
            "powershell": "powershell",
            "code": "code",
            "paint": "mspaint",
            "wordpad": "wordpad"
        }
        
        command = app_commands.get(app_name, app_name)
        
        try:
            subprocess.Popen(command, shell=True)
            return True
        except Exception as e:
            self.logger.error(f"Windows app launch error: {e}")
            return False
    
    async def _open_app_cross_platform(self, app_name: str) -> bool:
        """Open app on non-Windows platforms"""
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", app_name])
            else:  # Linux and others
                subprocess.Popen([app_name])
            return True
        except Exception as e:
            self.logger.error(f"Cross-platform app launch error: {e}")
            return False
    
    async def _close_app(self, app_name: str) -> Dict[str, Any]:
        """Close an application"""
        if not app_name:
            return self._create_result(False, "App name is required")
        
        app_name = app_name.lower().strip()
        closed_processes = []
        
        try:
            # Find and terminate processes
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    if app_name in proc_name or proc_name.startswith(app_name):
                        proc.terminate()
                        closed_processes.append(proc_name)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if closed_processes:
                return self._create_result(
                    True, 
                    f"Closed {len(closed_processes)} process(es): {', '.join(closed_processes)}"
                )
            else:
                return self._create_result(False, f"No running processes found for '{app_name}'")
                
        except Exception as e:
            return self._create_result(False, f"Error closing {app_name}: {str(e)}")
    
    async def _volume_control(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Control system volume"""
        if not self.is_windows or not WINDOWS_LIBS_AVAILABLE:
            return self._create_result(False, "Volume control is only supported on Windows")
        
        if not self.volume:
            return self._create_result(False, "Volume control not initialized")
        
        try:
            action = parameters.get("action")
            level = parameters.get("level")
            
            if level is not None:
                # Set specific volume level (0-100)
                volume_scalar = max(0.0, min(1.0, level / 100.0))
                self.volume.SetMasterScalarVolume(volume_scalar, None)
                return self._create_result(True, f"Volume set to {level}%")
                
            elif action == "increase":
                current = self.volume.GetMasterScalarVolume()
                new_volume = min(1.0, current + 0.1)
                self.volume.SetMasterScalarVolume(new_volume, None)
                return self._create_result(True, f"Volume increased to {int(new_volume * 100)}%")
                
            elif action == "decrease":
                current = self.volume.GetMasterScalarVolume()
                new_volume = max(0.0, current - 0.1)
                self.volume.SetMasterScalarVolume(new_volume, None)
                return self._create_result(True, f"Volume decreased to {int(new_volume * 100)}%")
                
            elif action == "mute":
                self.volume.SetMute(1, None)
                return self._create_result(True, "Volume muted")
                
            elif action == "unmute":
                self.volume.SetMute(0, None)
                return self._create_result(True, "Volume unmuted")
                
            else:
                return self._create_result(False, "Invalid volume control action")
                
        except Exception as e:
            return self._create_result(False, f"Volume control error: {str(e)}")
    
    async def _system_control(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Control system operations"""
        action = parameters.get("action")
        
        if not action:
            return self._create_result(False, "System action is required")
        
        try:
            if action == "shutdown":
                if self.is_windows:
                    subprocess.run(["shutdown", "/s", "/t", "10"], check=True)
                    return self._create_result(True, "System will shutdown in 10 seconds")
                else:
                    subprocess.run(["sudo", "shutdown", "-h", "+1"], check=True)
                    return self._create_result(True, "System will shutdown in 1 minute")
                    
            elif action == "restart":
                if self.is_windows:
                    subprocess.run(["shutdown", "/r", "/t", "10"], check=True)
                    return self._create_result(True, "System will restart in 10 seconds")
                else:
                    subprocess.run(["sudo", "reboot"], check=True)
                    return self._create_result(True, "System will restart")
                    
            elif action == "sleep":
                if self.is_windows:
                    subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=True)
                    return self._create_result(True, "System entering sleep mode")
                else:
                    subprocess.run(["systemctl", "suspend"], check=True)
                    return self._create_result(True, "System entering sleep mode")
                    
            elif action == "lock":
                if self.is_windows:
                    subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
                    return self._create_result(True, "Screen locked")
                else:
                    # Try common lock commands for Linux
                    lock_commands = ["gnome-screensaver-command -l", "xdg-screensaver lock", "loginctl lock-session"]
                    for cmd in lock_commands:
                        try:
                            subprocess.run(cmd.split(), check=True)
                            return self._create_result(True, "Screen locked")
                        except:
                            continue
                    return self._create_result(False, "Could not lock screen")
                    
            elif action == "minimize":
                if WINDOWS_LIBS_AVAILABLE and pyautogui:
                    pyautogui.hotkey('win', 'm')
                    return self._create_result(True, "Windows minimized")
                else:
                    return self._create_result(False, "Window control not available")
                    
            elif action == "maximize":
                if WINDOWS_LIBS_AVAILABLE and pyautogui:
                    pyautogui.hotkey('win', 'up')
                    return self._create_result(True, "Window maximized")
                else:
                    return self._create_result(False, "Window control not available")
                    
            else:
                return self._create_result(False, f"Unknown system action: {action}")
                
        except subprocess.CalledProcessError as e:
            return self._create_result(False, f"System command failed: {e}")
        except Exception as e:
            return self._create_result(False, f"System control error: {str(e)}")
    
    def get_info(self) -> Dict[str, Any]:
        """Get skill information"""
        return {
            "name": "PC Control",
            "description": "Control PC operations like opening/closing apps, volume, system functions",
            "commands": ["open_app", "close_app", "volume_control", "system_control"],
            "parameters": {
                "open_app": ["app_name"],
                "close_app": ["app_name"],
                "volume_control": ["level", "action"],
                "system_control": ["action"]
            },
            "examples": [
                "Zeno, open notepad",
                "Zeno, close chrome",
                "Zeno, set volume to 50",
                "Zeno, lock screen"
            ],
            "platform_support": {
                "windows": True,
                "macos": "limited",
                "linux": "limited"
            }
        }
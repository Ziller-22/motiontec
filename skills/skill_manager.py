"""
ZENO Skill Manager
Manages and executes modular skills for PC control and utilities
"""
import logging
import importlib
from typing import Dict, Any, Optional
from pathlib import Path

class SkillManager:
    """Manages ZENO's modular skills"""
    
    def __init__(self):
        self.logger = logging.getLogger('ZENO.SkillManager')
        self.skills = {}
        self._load_skills()
    
    def _load_skills(self):
        """Load all available skills"""
        try:
            # Import skill modules
            from .pc_control import PCControlSkill
            from .web_search import WebSearchSkill
            from .media_control import MediaControlSkill
            from .file_operations import FileOperationsSkill
            
            # Register skills
            self.skills = {
                "open_app": PCControlSkill(),
                "close_app": PCControlSkill(),
                "volume_control": PCControlSkill(),
                "system_control": PCControlSkill(),
                "web_search": WebSearchSkill(),
                "media_control": MediaControlSkill(),
                "file_operations": FileOperationsSkill()
            }
            
            self.logger.info(f"Loaded {len(self.skills)} skills")
            
        except Exception as e:
            self.logger.error(f"Error loading skills: {e}")
    
    async def execute_skill(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a skill command
        
        Args:
            command: Command name (e.g., 'open_app', 'volume_control')
            parameters: Command parameters
            
        Returns:
            Execution result dictionary
        """
        try:
            if command not in self.skills:
                return {
                    "success": False,
                    "message": f"Unknown command: {command}",
                    "error": "COMMAND_NOT_FOUND"
                }
            
            skill = self.skills[command]
            result = await skill.execute(command, parameters)
            
            self.logger.info(f"Executed skill '{command}' with result: {result.get('success', False)}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing skill '{command}': {e}")
            return {
                "success": False,
                "message": f"Error executing {command}: {str(e)}",
                "error": "EXECUTION_ERROR"
            }
    
    def get_available_skills(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available skills"""
        skill_info = {}
        
        for command, skill in self.skills.items():
            try:
                info = skill.get_info()
                skill_info[command] = info
            except Exception as e:
                self.logger.error(f"Error getting info for skill '{command}': {e}")
                skill_info[command] = {
                    "name": command,
                    "description": "Error loading skill info",
                    "parameters": [],
                    "examples": []
                }
        
        return skill_info
    
    def reload_skills(self):
        """Reload all skills"""
        self.skills.clear()
        self._load_skills()
        self.logger.info("Skills reloaded")

# Base skill class for inheritance
class BaseSkill:
    """Base class for ZENO skills"""
    
    def __init__(self):
        self.logger = logging.getLogger(f'ZENO.Skill.{self.__class__.__name__}')
    
    async def execute(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the skill
        
        Args:
            command: Specific command within the skill
            parameters: Command parameters
            
        Returns:
            Execution result
        """
        raise NotImplementedError("Subclasses must implement execute method")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get skill information
        
        Returns:
            Dictionary with skill metadata
        """
        return {
            "name": self.__class__.__name__,
            "description": "Base skill class",
            "parameters": [],
            "examples": []
        }
    
    def _create_result(self, success: bool, message: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create standardized result format"""
        return {
            "success": success,
            "message": message,
            "data": data or {}
        }
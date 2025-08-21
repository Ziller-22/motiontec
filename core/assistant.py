"""
ZENO Core Assistant Class
Main orchestrator for the AI assistant functionality
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from config import Config
from .intent_parser import IntentParser
from .ai_handler import AIHandler
from .memory import MemoryManager
from .speech import SpeechHandler

class ZenoAssistant:
    """Main ZENO Assistant class that coordinates all components"""
    
    def __init__(self):
        self.config = Config
        self.current_mode = Config.DEFAULT_MODE
        self.is_active = True
        
        # Initialize core components
        self.intent_parser = IntentParser()
        self.ai_handler = AIHandler()
        self.memory = MemoryManager() if Config.ENABLE_MEMORY else None
        self.speech = SpeechHandler()
        
        # Setup logging
        self._setup_logging()
        self.logger.info("ZENO Assistant initialized")
        
    def _setup_logging(self):
        """Setup logging configuration"""
        Config.ensure_directories()
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(Config.LOGS_DIR / 'zeno.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('ZENO')
    
    async def process_input(self, user_input: str, input_type: str = "text") -> Dict[str, Any]:
        """
        Main method to process user input and generate response
        
        Args:
            user_input: The user's input (text or transcribed speech)
            input_type: "text" or "voice"
            
        Returns:
            Dictionary with response data
        """
        try:
            self.logger.info(f"Processing {input_type} input: {user_input[:100]}...")
            
            # Store interaction in memory
            if self.memory:
                self.memory.add_interaction(user_input, None, input_type)
            
            # Check for mode switching
            new_mode = self._check_mode_switch(user_input)
            if new_mode:
                self.current_mode = new_mode
                response = f"Switched to {new_mode} mode"
                return self._create_response(response, "mode_switch")
            
            # Parse intent
            intent_result = self.intent_parser.parse(user_input, self.current_mode)
            
            # Handle based on intent type
            if intent_result["type"] == "command":
                response = await self._handle_command(intent_result)
            elif intent_result["type"] == "conversation":
                response = await self._handle_conversation(user_input, intent_result)
            else:
                response = await self._handle_fallback(user_input)
            
            # Update memory with response
            if self.memory and response.get("content"):
                self.memory.update_last_interaction(response["content"])
            
            self.logger.info(f"Generated response: {response['content'][:100]}...")
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            return self._create_response(
                "I encountered an error processing your request. Please try again.",
                "error"
            )
    
    def _check_mode_switch(self, user_input: str) -> Optional[str]:
        """Check if user wants to switch modes"""
        lower_input = user_input.lower()
        
        for mode in Config.MODES.keys():
            if f"switch to {mode}" in lower_input or f"{mode} mode" in lower_input:
                return mode
        return None
    
    async def _handle_command(self, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle command-based intents"""
        command = intent_result.get("command")
        params = intent_result.get("parameters", {})
        
        # Import skills dynamically to avoid circular imports
        from skills.skill_manager import SkillManager
        skill_manager = SkillManager()
        
        result = await skill_manager.execute_skill(command, params)
        return self._create_response(result.get("message", "Command executed"), "command", result)
    
    async def _handle_conversation(self, user_input: str, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle conversational intents using AI"""
        context = {}
        
        # Add memory context if available
        if self.memory:
            context["recent_interactions"] = self.memory.get_recent_interactions(5)
            context["user_preferences"] = self.memory.get_preferences()
        
        # Add current mode context
        context["current_mode"] = self.current_mode
        context["intent"] = intent_result
        
        # Generate AI response
        ai_response = await self.ai_handler.generate_response(user_input, context)
        return self._create_response(ai_response, "conversation")
    
    async def _handle_fallback(self, user_input: str) -> Dict[str, Any]:
        """Fallback handler for unclear intents"""
        response = await self.ai_handler.generate_response(
            user_input, 
            {"current_mode": self.current_mode, "fallback": True}
        )
        return self._create_response(response, "fallback")
    
    def _create_response(self, content: str, response_type: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create standardized response format"""
        return {
            "content": content,
            "type": response_type,
            "mode": self.current_mode,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current assistant status"""
        return {
            "active": self.is_active,
            "mode": self.current_mode,
            "available_modes": list(Config.MODES.keys()),
            "model_status": Config.get_model_status(),
            "memory_enabled": Config.ENABLE_MEMORY,
            "pc_control_enabled": Config.ENABLE_PC_CONTROL
        }
    
    def set_mode(self, mode: str) -> bool:
        """Set assistant mode"""
        if mode in Config.MODES:
            self.current_mode = mode
            self.logger.info(f"Mode changed to: {mode}")
            return True
        return False
    
    def shutdown(self):
        """Gracefully shutdown the assistant"""
        self.logger.info("ZENO Assistant shutting down")
        self.is_active = False
        if self.speech:
            self.speech.cleanup()
        if self.memory:
            self.memory.save_to_disk()
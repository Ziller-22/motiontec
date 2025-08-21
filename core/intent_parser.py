"""
ZENO Intent Parser
Rule-based intent recognition for reliable command execution
"""
import re
from typing import Dict, Any, List, Optional
from config import Config

class IntentParser:
    """Rule-based intent parser for ZENO commands"""
    
    def __init__(self):
        self.wake_word = Config.WAKE_WORD.lower()
        self._load_intent_patterns()
    
    def _load_intent_patterns(self):
        """Load and compile intent recognition patterns"""
        self.patterns = {
            # PC Control Commands
            "open_app": [
                r"(?:open|launch|start|run)\s+(\w+)",
                r"(?:zeno,?\s+)?(?:open|launch|start)\s+(.+)",
            ],
            "close_app": [
                r"(?:close|quit|exit)\s+(\w+)",
                r"(?:zeno,?\s+)?(?:close|quit)\s+(.+)",
            ],
            "volume_control": [
                r"(?:set\s+)?volume\s+(?:to\s+)?(\d+)",
                r"(?:increase|raise|turn\s+up)\s+volume",
                r"(?:decrease|lower|turn\s+down)\s+volume",
                r"(?:mute|unmute)(?:\s+volume)?",
            ],
            "media_control": [
                r"(?:play|pause|stop|next|previous)\s+(?:music|song|track|media)?",
                r"(?:skip|next)\s+(?:song|track)",
                r"(?:previous|back)\s+(?:song|track)",
            ],
            "system_control": [
                r"(?:shutdown|restart|sleep|hibernate)\s+(?:computer|pc|system)?",
                r"(?:lock\s+)?(?:screen|computer)",
                r"(?:minimize|maximize)\s+(?:window|app)",
            ],
            "web_search": [
                r"(?:search|google|look\s+up)\s+(?:for\s+)?(.+)",
                r"(?:zeno,?\s+)?search\s+(?:for\s+)?(.+)",
            ],
            "file_operations": [
                r"(?:create|make|new)\s+(?:file|folder|directory)\s+(.+)",
                r"(?:delete|remove)\s+(?:file|folder)\s+(.+)",
                r"(?:open|show)\s+(?:file|folder)\s+(.+)",
            ],
            # Mode switching
            "mode_switch": [
                r"(?:switch\s+to|change\s+to|enter)\s+(conversation|control|utility)\s+mode",
                r"(conversation|control|utility)\s+mode",
            ],
            # Conversation starters
            "greeting": [
                r"(?:hello|hi|hey)\s+zeno",
                r"(?:good\s+)?(?:morning|afternoon|evening)\s+zeno",
                r"zeno(?:,?\s+)?(?:hello|hi|hey)",
            ],
            "question": [
                r"(?:what|how|why|when|where|who)\s+.+\?",
                r"(?:can\s+you|could\s+you|will\s+you)\s+.+\?",
                r"(?:do\s+you|are\s+you|is\s+it)\s+.+\?",
            ],
        }
        
        # Compile patterns for efficiency
        self.compiled_patterns = {}
        for intent, pattern_list in self.patterns.items():
            self.compiled_patterns[intent] = [
                re.compile(pattern, re.IGNORECASE) for pattern in pattern_list
            ]
    
    def parse(self, user_input: str, current_mode: str) -> Dict[str, Any]:
        """
        Parse user input and determine intent
        
        Args:
            user_input: Raw user input text
            current_mode: Current assistant mode
            
        Returns:
            Dictionary with intent information
        """
        user_input = user_input.strip()
        lower_input = user_input.lower()
        
        # Check if wake word is present for control mode
        has_wake_word = self._has_wake_word(lower_input)
        
        # In control mode, require wake word for system commands
        if current_mode == "control" and not has_wake_word:
            system_commands = ["open_app", "close_app", "volume_control", "media_control", "system_control"]
            for intent in system_commands:
                if self._match_intent(user_input, intent):
                    return {
                        "type": "wake_word_required",
                        "message": f"Wake word '{self.wake_word}' required for system commands in control mode",
                        "suggested_command": f"{self.wake_word}, {user_input}"
                    }
        
        # Try to match specific intents
        for intent, patterns in self.compiled_patterns.items():
            match_result = self._match_patterns(user_input, patterns)
            if match_result:
                return self._create_intent_result(intent, match_result, user_input, current_mode)
        
        # Default to conversation if no specific intent matched
        return {
            "type": "conversation",
            "intent": "general_query",
            "confidence": 0.5,
            "original_input": user_input,
            "mode": current_mode
        }
    
    def _has_wake_word(self, text: str) -> bool:
        """Check if wake word is present in text"""
        return self.wake_word in text.lower()
    
    def _match_intent(self, user_input: str, intent: str) -> bool:
        """Check if input matches a specific intent"""
        if intent not in self.compiled_patterns:
            return False
        
        patterns = self.compiled_patterns[intent]
        return any(pattern.search(user_input) for pattern in patterns)
    
    def _match_patterns(self, text: str, patterns: List[re.Pattern]) -> Optional[re.Match]:
        """Try to match text against a list of compiled patterns"""
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                return match
        return None
    
    def _create_intent_result(self, intent: str, match: re.Match, original_input: str, mode: str) -> Dict[str, Any]:
        """Create structured intent result"""
        result = {
            "type": "command" if self._is_command_intent(intent) else "conversation",
            "intent": intent,
            "confidence": 0.9,  # High confidence for rule-based matching
            "original_input": original_input,
            "mode": mode
        }
        
        # Extract parameters based on intent type
        if intent == "open_app" or intent == "close_app":
            result["command"] = intent
            result["parameters"] = {"app_name": match.group(1).strip()}
            
        elif intent == "volume_control":
            result["command"] = intent
            if match.group(1) and match.group(1).isdigit():
                result["parameters"] = {"level": int(match.group(1))}
            else:
                # Determine action from matched text
                text = match.group(0).lower()
                if "increase" in text or "raise" in text or "up" in text:
                    result["parameters"] = {"action": "increase"}
                elif "decrease" in text or "lower" in text or "down" in text:
                    result["parameters"] = {"action": "decrease"}
                elif "mute" in text:
                    result["parameters"] = {"action": "mute"}
                elif "unmute" in text:
                    result["parameters"] = {"action": "unmute"}
                    
        elif intent == "media_control":
            result["command"] = intent
            text = match.group(0).lower()
            if "play" in text:
                result["parameters"] = {"action": "play"}
            elif "pause" in text:
                result["parameters"] = {"action": "pause"}
            elif "stop" in text:
                result["parameters"] = {"action": "stop"}
            elif "next" in text or "skip" in text:
                result["parameters"] = {"action": "next"}
            elif "previous" in text or "back" in text:
                result["parameters"] = {"action": "previous"}
                
        elif intent == "web_search":
            result["command"] = intent
            search_query = match.group(1).strip() if match.group(1) else original_input
            result["parameters"] = {"query": search_query}
            
        elif intent == "system_control":
            result["command"] = intent
            text = match.group(0).lower()
            if "shutdown" in text:
                result["parameters"] = {"action": "shutdown"}
            elif "restart" in text:
                result["parameters"] = {"action": "restart"}
            elif "sleep" in text:
                result["parameters"] = {"action": "sleep"}
            elif "lock" in text:
                result["parameters"] = {"action": "lock"}
            elif "minimize" in text:
                result["parameters"] = {"action": "minimize"}
            elif "maximize" in text:
                result["parameters"] = {"action": "maximize"}
                
        return result
    
    def _is_command_intent(self, intent: str) -> bool:
        """Check if intent represents a system command"""
        command_intents = [
            "open_app", "close_app", "volume_control", "media_control", 
            "system_control", "web_search", "file_operations"
        ]
        return intent in command_intents
    
    def get_available_commands(self, mode: str) -> List[str]:
        """Get list of available commands for current mode"""
        if mode == "control":
            return [
                "Open applications (e.g., 'Zeno, open notepad')",
                "Close applications (e.g., 'Zeno, close chrome')",
                "Control volume (e.g., 'Zeno, set volume to 50')",
                "Media control (e.g., 'Zeno, play music')",
                "System control (e.g., 'Zeno, lock screen')",
                "Web search (e.g., 'Zeno, search for Python tutorials')"
            ]
        elif mode == "conversation":
            return [
                "Ask questions (e.g., 'What is machine learning?')",
                "Have conversations (e.g., 'Tell me a joke')",
                "Get information (e.g., 'Explain quantum computing')",
                "Switch modes (e.g., 'Switch to control mode')"
            ]
        elif mode == "utility":
            return [
                "Multi-step workflows (e.g., 'Research and summarize AI trends')",
                "Complex tasks (e.g., 'Create a presentation outline')",
                "File operations (e.g., 'Create project folder structure')",
                "Automated sequences (e.g., 'Set up development environment')"
            ]
        return []
"""
ZENO Memory Management
Handles user preferences, conversation history, and learning
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from config import Config

class MemoryManager:
    """Manages ZENO's memory and learning capabilities"""
    
    def __init__(self):
        self.config = Config
        self.logger = logging.getLogger('ZENO.Memory')
        
        # Ensure memory directory exists
        Config.ensure_directories()
        self.memory_file = Config.MEMORY_DIR / Config.MEMORY_FILE
        
        # Memory data structure
        self.memory = {
            "interactions": [],
            "preferences": {},
            "frequently_used": {
                "apps": {},
                "commands": {},
                "topics": {}
            },
            "user_context": {
                "name": None,
                "timezone": None,
                "preferred_mode": Config.DEFAULT_MODE
            },
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        # Load existing memory
        self._load_memory()
    
    def _load_memory(self):
        """Load memory from disk"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    loaded_memory = json.load(f)
                    self.memory.update(loaded_memory)
                self.logger.info("Memory loaded successfully")
            else:
                self.logger.info("No existing memory file, starting fresh")
        except Exception as e:
            self.logger.error(f"Error loading memory: {e}")
    
    def save_to_disk(self):
        """Save memory to disk"""
        try:
            self.memory["metadata"]["last_updated"] = datetime.now().isoformat()
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
            
            self.logger.debug("Memory saved to disk")
        except Exception as e:
            self.logger.error(f"Error saving memory: {e}")
    
    def add_interaction(self, user_input: str, response: Optional[str] = None, input_type: str = "text"):
        """Add a new interaction to memory"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "response": response,
            "input_type": input_type,
            "id": len(self.memory["interactions"])
        }
        
        self.memory["interactions"].append(interaction)
        
        # Keep only recent interactions to prevent memory bloat
        if len(self.memory["interactions"]) > Config.MAX_MEMORY_ENTRIES:
            self.memory["interactions"] = self.memory["interactions"][-Config.MAX_MEMORY_ENTRIES:]
        
        # Update usage statistics
        self._update_usage_stats(user_input)
        
        # Auto-save periodically
        if len(self.memory["interactions"]) % 10 == 0:
            self.save_to_disk()
    
    def update_last_interaction(self, response: str):
        """Update the response for the last interaction"""
        if self.memory["interactions"]:
            self.memory["interactions"][-1]["response"] = response
    
    def get_recent_interactions(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get recent interactions for context"""
        return self.memory["interactions"][-count:] if self.memory["interactions"] else []
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences"""
        return self.memory["preferences"].copy()
    
    def set_preference(self, key: str, value: Any):
        """Set a user preference"""
        self.memory["preferences"][key] = value
        self.save_to_disk()
        self.logger.info(f"Preference set: {key} = {value}")
    
    def get_user_context(self) -> Dict[str, Any]:
        """Get user context information"""
        return self.memory["user_context"].copy()
    
    def update_user_context(self, **kwargs):
        """Update user context"""
        self.memory["user_context"].update(kwargs)
        self.save_to_disk()
        self.logger.info(f"User context updated: {kwargs}")
    
    def _update_usage_stats(self, user_input: str):
        """Update usage statistics based on user input"""
        lower_input = user_input.lower()
        
        # Track app usage
        for app in Config.ALLOWED_APPS:
            if app in lower_input:
                if app not in self.memory["frequently_used"]["apps"]:
                    self.memory["frequently_used"]["apps"][app] = 0
                self.memory["frequently_used"]["apps"][app] += 1
        
        # Track command patterns
        command_patterns = [
            "open", "close", "search", "play", "pause", "volume", 
            "minimize", "maximize", "shutdown", "restart"
        ]
        
        for pattern in command_patterns:
            if pattern in lower_input:
                if pattern not in self.memory["frequently_used"]["commands"]:
                    self.memory["frequently_used"]["commands"][pattern] = 0
                self.memory["frequently_used"]["commands"][pattern] += 1
        
        # Extract and track topics (simple keyword extraction)
        words = lower_input.split()
        meaningful_words = [
            word for word in words 
            if len(word) > 3 and word not in ["what", "how", "when", "where", "why", "the", "and", "but", "for"]
        ]
        
        for word in meaningful_words[:3]:  # Track up to 3 meaningful words
            if word not in self.memory["frequently_used"]["topics"]:
                self.memory["frequently_used"]["topics"][word] = 0
            self.memory["frequently_used"]["topics"][word] += 1
    
    def get_frequently_used(self, category: str, limit: int = 5) -> List[tuple]:
        """Get frequently used items in a category"""
        if category not in self.memory["frequently_used"]:
            return []
        
        items = self.memory["frequently_used"][category]
        sorted_items = sorted(items.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:limit]
    
    def search_interactions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search through interaction history"""
        query_lower = query.lower()
        matching_interactions = []
        
        for interaction in reversed(self.memory["interactions"]):
            user_input = interaction.get("user_input", "").lower()
            response = interaction.get("response", "").lower()
            
            if query_lower in user_input or query_lower in response:
                matching_interactions.append(interaction)
                
                if len(matching_interactions) >= limit:
                    break
        
        return matching_interactions
    
    def get_conversation_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of recent conversations"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_interactions = []
        
        for interaction in self.memory["interactions"]:
            interaction_time = datetime.fromisoformat(interaction["timestamp"])
            if interaction_time > cutoff_time:
                recent_interactions.append(interaction)
        
        summary = {
            "total_interactions": len(recent_interactions),
            "text_interactions": len([i for i in recent_interactions if i.get("input_type") == "text"]),
            "voice_interactions": len([i for i in recent_interactions if i.get("input_type") == "voice"]),
            "time_range": f"Last {hours} hours",
            "most_common_apps": self.get_frequently_used("apps", 3),
            "most_common_commands": self.get_frequently_used("commands", 3)
        }
        
        return summary
    
    def clear_memory(self, keep_preferences: bool = True):
        """Clear memory data"""
        if keep_preferences:
            preferences = self.memory["preferences"].copy()
            user_context = self.memory["user_context"].copy()
        
        self.memory = {
            "interactions": [],
            "preferences": preferences if keep_preferences else {},
            "frequently_used": {
                "apps": {},
                "commands": {},
                "topics": {}
            },
            "user_context": user_context if keep_preferences else {
                "name": None,
                "timezone": None,
                "preferred_mode": Config.DEFAULT_MODE
            },
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        self.save_to_disk()
        self.logger.info("Memory cleared")
    
    def export_memory(self, filepath: Optional[Path] = None) -> Path:
        """Export memory to a file"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = Config.DATA_DIR / f"memory_export_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Memory exported to: {filepath}")
        return filepath
    
    def import_memory(self, filepath: Path, merge: bool = True):
        """Import memory from a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_memory = json.load(f)
            
            if merge:
                # Merge with existing memory
                self.memory["interactions"].extend(imported_memory.get("interactions", []))
                self.memory["preferences"].update(imported_memory.get("preferences", {}))
                
                # Merge frequently used data
                for category in ["apps", "commands", "topics"]:
                    imported_freq = imported_memory.get("frequently_used", {}).get(category, {})
                    for item, count in imported_freq.items():
                        if item in self.memory["frequently_used"][category]:
                            self.memory["frequently_used"][category][item] += count
                        else:
                            self.memory["frequently_used"][category][item] = count
            else:
                # Replace existing memory
                self.memory = imported_memory
            
            self.save_to_disk()
            self.logger.info(f"Memory imported from: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error importing memory: {e}")
            raise
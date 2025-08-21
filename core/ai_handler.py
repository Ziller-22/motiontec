"""
ZENO AI Handler
Manages local and remote AI model interactions
"""
import asyncio
import logging
from typing import Dict, Any, Optional
import requests
import json

from config import Config

class AIHandler:
    """Handles AI model interactions for ZENO"""
    
    def __init__(self):
        self.config = Config
        self.logger = logging.getLogger('ZENO.AIHandler')
        self.ollama_available = False
        self.available_models = []
        self._check_ollama_status()
        
    def _check_ollama_status(self):
        """Check if Ollama is running and what models are available"""
        try:
            response = requests.get(f"{self.config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                self.ollama_available = True
                models_data = response.json()
                self.available_models = [model["name"] for model in models_data.get("models", [])]
                self.logger.info(f"Ollama available with models: {self.available_models}")
            else:
                self.logger.warning("Ollama not responding")
        except Exception as e:
            self.logger.warning(f"Ollama not available: {e}")
    
    async def generate_response(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """
        Generate AI response using available models
        
        Args:
            user_input: User's input text
            context: Additional context for the response
            
        Returns:
            Generated response string
        """
        context = context or {}
        
        # Try local models first
        if self.ollama_available:
            response = await self._generate_ollama_response(user_input, context)
            if response:
                return response
        
        # Fallback to API if available
        if self.config.OPENAI_API_KEY:
            response = await self._generate_openai_response(user_input, context)
            if response:
                return response
                
        if self.config.GROQ_API_KEY:
            response = await self._generate_groq_response(user_input, context)
            if response:
                return response
        
        # Ultimate fallback
        return self._generate_fallback_response(user_input, context)
    
    async def _generate_ollama_response(self, user_input: str, context: Dict[str, Any]) -> Optional[str]:
        """Generate response using Ollama local models"""
        try:
            # Choose best available model
            model = self._select_best_local_model()
            if not model:
                return None
            
            # Build prompt with context
            prompt = self._build_prompt(user_input, context)
            
            # Make request to Ollama
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }
            
            response = requests.post(
                f"{self.config.OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
                
        except Exception as e:
            self.logger.error(f"Ollama generation error: {e}")
        
        return None
    
    async def _generate_openai_response(self, user_input: str, context: Dict[str, Any]) -> Optional[str]:
        """Generate response using OpenAI API"""
        try:
            import openai
            openai.api_key = self.config.OPENAI_API_KEY
            
            messages = self._build_openai_messages(user_input, context)
            
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"OpenAI generation error: {e}")
        
        return None
    
    async def _generate_groq_response(self, user_input: str, context: Dict[str, Any]) -> Optional[str]:
        """Generate response using Groq API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.config.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            messages = self._build_openai_messages(user_input, context)
            
            payload = {
                "model": "mixtral-8x7b-32768",
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
                
        except Exception as e:
            self.logger.error(f"Groq generation error: {e}")
        
        return None
    
    def _select_best_local_model(self) -> Optional[str]:
        """Select the best available local model"""
        preferred_order = [
            self.config.DEFAULT_LOCAL_MODEL,
            self.config.FALLBACK_LOCAL_MODEL,
            "phi",
            "tinyllama",
            "llama2"
        ]
        
        for model in preferred_order:
            if any(model in available for available in self.available_models):
                return next(available for available in self.available_models if model in available)
        
        # Return first available model if no preferred ones found
        return self.available_models[0] if self.available_models else None
    
    def _build_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        """Build prompt for local models"""
        system_context = self._get_system_context(context)
        
        prompt = f"{system_context}\n\nUser: {user_input}\nAssistant:"
        return prompt
    
    def _build_openai_messages(self, user_input: str, context: Dict[str, Any]) -> list:
        """Build messages array for OpenAI-compatible APIs"""
        system_context = self._get_system_context(context)
        
        messages = [
            {"role": "system", "content": system_context},
            {"role": "user", "content": user_input}
        ]
        
        # Add recent conversation history if available
        if context.get("recent_interactions"):
            for interaction in context["recent_interactions"][-3:]:  # Last 3 interactions
                if interaction.get("user_input") and interaction.get("response"):
                    messages.insert(-1, {"role": "user", "content": interaction["user_input"]})
                    messages.insert(-1, {"role": "assistant", "content": interaction["response"]})
        
        return messages
    
    def _get_system_context(self, context: Dict[str, Any]) -> str:
        """Build system context for AI responses"""
        mode = context.get("current_mode", "conversation")
        
        base_context = """You are ZENO, a helpful personal AI assistant. You are running locally on the user's Windows PC and can help with conversations, PC control, and utility tasks.

Key traits:
- Be concise but helpful
- Stay in character as a personal assistant
- Acknowledge your local nature when relevant
- Be friendly and professional"""
        
        mode_context = {
            "conversation": "You're in conversation mode. Focus on natural dialogue, answering questions, and general assistance.",
            "control": "You're in control mode. Help with PC control commands, but note that system commands require the wake word 'Zeno'.",
            "utility": "You're in utility mode. Help with multi-step tasks, workflows, and complex operations."
        }
        
        context_parts = [base_context, mode_context.get(mode, "")]
        
        # Add user preferences if available
        if context.get("user_preferences"):
            prefs = context["user_preferences"]
            context_parts.append(f"User preferences: {json.dumps(prefs, indent=2)}")
        
        # Add fallback context if this is a fallback request
        if context.get("fallback"):
            context_parts.append("The user's intent was unclear. Ask for clarification or provide general help.")
        
        return "\n\n".join(filter(None, context_parts))
    
    def _generate_fallback_response(self, user_input: str, context: Dict[str, Any]) -> str:
        """Generate a basic fallback response when no AI models are available"""
        mode = context.get("current_mode", "conversation")
        
        fallback_responses = {
            "conversation": "I'm currently running in offline mode. I can help with basic questions, but my responses may be limited without access to AI models.",
            "control": "I can help with PC control commands. Try commands like 'Zeno, open notepad' or 'Zeno, set volume to 50'.",
            "utility": "I can assist with utility tasks. What would you like me to help you with?"
        }
        
        base_response = fallback_responses.get(mode, "I'm here to help! What can I do for you?")
        
        # Add specific guidance based on input
        if "?" in user_input:
            base_response += " For questions, I work best when connected to AI models via Ollama or API keys."
        
        return base_response
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        return {
            "ollama_available": self.ollama_available,
            "local_models": self.available_models,
            "api_keys_configured": {
                "openai": bool(self.config.OPENAI_API_KEY),
                "groq": bool(self.config.GROQ_API_KEY)
            }
        }
    
    def refresh_models(self):
        """Refresh the list of available models"""
        self._check_ollama_status()
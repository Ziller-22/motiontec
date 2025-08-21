"""
ZENO Web Search Skill
Handles web search operations
"""
import webbrowser
import urllib.parse
from typing import Dict, Any

from .skill_manager import BaseSkill

class WebSearchSkill(BaseSkill):
    """Handles web search operations"""
    
    def __init__(self):
        super().__init__()
        self.search_engines = {
            "google": "https://www.google.com/search?q={}",
            "bing": "https://www.bing.com/search?q={}",
            "duckduckgo": "https://duckduckgo.com/?q={}",
            "youtube": "https://www.youtube.com/results?search_query={}",
            "github": "https://github.com/search?q={}"
        }
        self.default_engine = "google"
    
    async def execute(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web search command"""
        try:
            if command == "web_search":
                return await self._web_search(parameters)
            else:
                return self._create_result(False, f"Unknown web search command: {command}")
                
        except Exception as e:
            return self._create_result(False, f"Web search error: {str(e)}")
    
    async def _web_search(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform web search"""
        query = parameters.get("query")
        engine = parameters.get("engine", self.default_engine).lower()
        
        if not query:
            return self._create_result(False, "Search query is required")
        
        if engine not in self.search_engines:
            engine = self.default_engine
            self.logger.warning(f"Unknown search engine, using {engine}")
        
        try:
            # Encode the query for URL
            encoded_query = urllib.parse.quote_plus(query)
            search_url = self.search_engines[engine].format(encoded_query)
            
            # Open in default browser
            webbrowser.open(search_url)
            
            return self._create_result(
                True, 
                f"Opened {engine} search for '{query}' in browser",
                {"url": search_url, "query": query, "engine": engine}
            )
            
        except Exception as e:
            return self._create_result(False, f"Error opening browser: {str(e)}")
    
    def get_info(self) -> Dict[str, Any]:
        """Get skill information"""
        return {
            "name": "Web Search",
            "description": "Search the web using various search engines",
            "commands": ["web_search"],
            "parameters": {
                "web_search": ["query", "engine (optional)"]
            },
            "examples": [
                "Zeno, search for Python tutorials",
                "Zeno, search for weather forecast",
                "Search machine learning on YouTube"
            ],
            "supported_engines": list(self.search_engines.keys())
        }
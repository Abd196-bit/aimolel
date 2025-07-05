"""
DieAI Brain - Intelligent Response System
Combines web search with AI reasoning to provide intelligent responses
"""
import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .web_search import WebSearchService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DieAIBrain:
    def __init__(self):
        self.web_search = WebSearchService()
        self.conversation_memory = []
        
    def analyze_query(self, query: str) -> Dict:
        """Analyze the user's query to understand intent and context"""
        query_lower = query.lower().strip()
        
        analysis = {
            'needs_search': False,
            'query_type': 'general',
            'keywords': [],
            'entities': [],
            'intent': 'unknown'
        }
        
        # Check if query needs web search
        search_indicators = [
            'what is', 'who is', 'when did', 'where is', 'how to',
            'current', 'latest', 'recent', 'today', 'now', 'news',
            'weather', 'price', 'stock', 'market', 'rate',
            'definition', 'meaning', 'explain', 'tell me about'
        ]
        
        analysis['needs_search'] = any(indicator in query_lower for indicator in search_indicators)
        
        # Determine query type
        if any(word in query_lower for word in ['weather', 'temperature', 'forecast']):
            analysis['query_type'] = 'weather'
        elif any(word in query_lower for word in ['news', 'breaking', 'latest']):
            analysis['query_type'] = 'news'
        elif any(word in query_lower for word in ['price', 'cost', 'stock', 'market']):
            analysis['query_type'] = 'financial'
        elif any(word in query_lower for word in ['how to', 'tutorial', 'guide']):
            analysis['query_type'] = 'instructional'
        elif any(word in query_lower for word in ['what is', 'define', 'meaning']):
            analysis['query_type'] = 'definitional'
        elif any(word in query_lower for word in ['calculate', 'math', 'compute']):
            analysis['query_type'] = 'computational'
        
        # Extract keywords (simple approach)
        words = re.findall(r'\b[a-zA-Z]+\b', query)
        analysis['keywords'] = [word for word in words if len(word) > 2]
        
        return analysis
    
    def generate_search_query(self, user_query: str, analysis: Dict) -> str:
        """Generate an optimized search query based on user input"""
        if analysis['query_type'] == 'weather':
            return f"weather {user_query}"
        elif analysis['query_type'] == 'news':
            return f"latest news {user_query}"
        elif analysis['query_type'] == 'financial':
            return f"current price {user_query}"
        else:
            return user_query
    
    def synthesize_response(self, query: str, search_results: List[Dict]) -> str:
        """Synthesize an intelligent response using search results"""
        if not search_results:
            return self.generate_fallback_response(query)
        
        # Extract key information
        key_info = []
        sources = []
        
        for result in search_results:
            if result.get('content'):
                key_info.append(result['content'])
                if result.get('source'):
                    sources.append(result['source'])
        
        if not key_info:
            return self.generate_fallback_response(query)
        
        # Combine and summarize information
        combined_info = " ".join(key_info[:3])  # Top 3 most relevant
        
        # Generate response based on query type
        analysis = self.analyze_query(query)
        
        if analysis['query_type'] == 'definitional':
            response = self.format_definition_response(combined_info, sources)
        elif analysis['query_type'] == 'weather':
            response = self.format_weather_response(combined_info, sources)
        elif analysis['query_type'] == 'news':
            response = self.format_news_response(combined_info, sources)
        elif analysis['query_type'] == 'financial':
            response = self.format_financial_response(combined_info, sources)
        elif analysis['query_type'] == 'instructional':
            response = self.format_instructional_response(combined_info, sources)
        else:
            response = self.format_general_response(combined_info, sources)
        
        return response
    
    def format_definition_response(self, info: str, sources: List[str]) -> str:
        """Format a definition-style response"""
        return f"Based on current information:\n\n{info}\n\nSources: {', '.join(set(sources))}"
    
    def format_weather_response(self, info: str, sources: List[str]) -> str:
        """Format a weather-style response"""
        return f"Current weather information:\n\n{info}\n\nData from: {', '.join(set(sources))}"
    
    def format_news_response(self, info: str, sources: List[str]) -> str:
        """Format a news-style response"""
        return f"Latest news:\n\n{info}\n\nSources: {', '.join(set(sources))}"
    
    def format_financial_response(self, info: str, sources: List[str]) -> str:
        """Format a financial-style response"""
        return f"Current market information:\n\n{info}\n\nData from: {', '.join(set(sources))}"
    
    def format_instructional_response(self, info: str, sources: List[str]) -> str:
        """Format an instructional-style response"""
        return f"Here's how to do it:\n\n{info}\n\nBased on information from: {', '.join(set(sources))}"
    
    def format_general_response(self, info: str, sources: List[str]) -> str:
        """Format a general response"""
        return f"Based on my research:\n\n{info}\n\nSources: {', '.join(set(sources))}"
    
    def generate_fallback_response(self, query: str) -> str:
        """Generate a fallback response when no search results are available"""
        # Simple pattern matching for common questions
        query_lower = query.lower()
        
        if 'hello' in query_lower or 'hi' in query_lower:
            return "Hello! I'm DieAI, your intelligent assistant. I can help you find information, answer questions, and provide insights on a wide range of topics. What would you like to know?"
        
        if 'how are you' in query_lower:
            return "I'm functioning well and ready to help! I'm an AI assistant that can search the web for current information and provide intelligent responses. What can I help you with today?"
        
        if 'what can you do' in query_lower:
            return "I can help you with:\n• Finding current information on any topic\n• Answering questions using web search\n• Providing news and updates\n• Explaining concepts and definitions\n• Weather information\n• Financial data\n• How-to guides and tutorials\n\nJust ask me anything!"
        
        if 'thank you' in query_lower or 'thanks' in query_lower:
            return "You're welcome! I'm here to help whenever you need information or have questions. Feel free to ask me anything!"
        
        # For other queries, encourage asking specific questions
        return f"I'd be happy to help you with '{query}'. Let me search for the most current information on this topic. Could you be more specific about what you'd like to know?"
    
    def process_query(self, query: str, use_search: bool = True) -> str:
        """Main method to process user queries and generate responses"""
        if not query.strip():
            return "Please ask me a question or tell me what you'd like to know!"
        
        # Analyze the query
        analysis = self.analyze_query(query)
        
        # Store in conversation memory
        self.conversation_memory.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'analysis': analysis
        })
        
        # Keep only last 10 conversations in memory
        if len(self.conversation_memory) > 10:
            self.conversation_memory = self.conversation_memory[-10:]
        
        # Decide whether to search
        should_search = use_search and (analysis['needs_search'] or analysis['query_type'] != 'general')
        
        if should_search:
            try:
                # Generate search query
                search_query = self.generate_search_query(query, analysis)
                logger.info(f"Searching for: {search_query}")
                
                # Perform web search
                search_results = self.web_search.search_web(search_query, max_results=6)
                
                # Generate response
                response = self.synthesize_response(query, search_results)
                
                return response
                
            except Exception as e:
                logger.error(f"Search error: {e}")
                return self.generate_fallback_response(query)
        else:
            return self.generate_fallback_response(query)
    
    def get_conversation_context(self) -> List[Dict]:
        """Get recent conversation context"""
        return self.conversation_memory[-5:]  # Last 5 conversations
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
        
        # Simple questions that don't need search
        simple_patterns = [
            'what is your name', 'who are you', 'what are you',
            'hello', 'hi', 'hey', 'good morning', 'good afternoon',
            'how are you', 'what can you do', 'help',
            'thank you', 'thanks', 'bye', 'goodbye',
            'what is 1+1', 'what is 2+2', 'simple math',
            'tell me a joke', 'how old are you'
        ]
        
        # Check if it's a simple question first
        is_simple = any(pattern in query_lower for pattern in simple_patterns)
        
        if is_simple:
            analysis['needs_search'] = False
            analysis['query_type'] = 'simple'
            return analysis
        
        # Check if query needs web search for complex topics
        search_indicators = [
            'current weather', 'weather in', 'temperature in',
            'latest news', 'recent news', 'breaking news',
            'current price', 'stock price', 'market today',
            'what happened', 'when did', 'where is',
            'current events', 'today\'s', 'this week',
            'how to cook', 'how to make', 'recipe for',
            'definition of', 'explain complex'
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
        """Generate a simple, direct response for basic questions"""
        query_lower = query.lower().strip()
        
        # Math questions
        if 'what is 1+1' in query_lower or '1+1' in query_lower:
            return "1 + 1 = 2"
        if 'what is 2+2' in query_lower or '2+2' in query_lower:
            return "2 + 2 = 4"
        
        # Identity questions
        if 'what is your name' in query_lower or 'who are you' in query_lower:
            return "I'm DieAI, your intelligent assistant."
        
        if 'what are you' in query_lower:
            return "I'm DieAI, an AI assistant that can help you find information and answer questions."
        
        # Greetings
        if any(word in query_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! How can I help you today?"
        
        if 'good morning' in query_lower:
            return "Good morning! What can I help you with?"
        
        if 'good afternoon' in query_lower:
            return "Good afternoon! How can I assist you?"
        
        # Status questions
        if 'how are you' in query_lower:
            return "I'm working great! Ready to help you with any questions."
        
        if 'how old are you' in query_lower:
            return "I'm DieAI, a custom AI model. I don't have an age in the traditional sense."
        
        # Capability questions
        if 'what can you do' in query_lower or 'help' in query_lower:
            return "I can help you with questions, find current information, explain topics, and more. Just ask me anything!"
        
        # Gratitude
        if any(word in query_lower for word in ['thank you', 'thanks']):
            return "You're welcome! Happy to help."
        
        # Goodbyes
        if any(word in query_lower for word in ['bye', 'goodbye']):
            return "Goodbye! Feel free to ask me anything anytime."
        
        # Jokes
        if 'tell me a joke' in query_lower:
            return "Why don't scientists trust atoms? Because they make up everything!"
        
        # Default for unrecognized simple queries
        return f"I can help you with that! For more detailed information, I can search the web. What specifically would you like to know about '{query}'?"
    
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
        
        # Decide whether to search - don't search for simple queries
        should_search = use_search and analysis['needs_search'] and analysis['query_type'] != 'simple'
        
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
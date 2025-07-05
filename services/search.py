import requests
import json
import os
from typing import List, Dict, Optional
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        # Search API configuration
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID', 'default_engine_id')
        self.search_api_key = os.getenv('GOOGLE_SEARCH_API_KEY', 'default_api_key')
        self.bing_api_key = os.getenv('BING_SEARCH_API_KEY', 'default_bing_key')
        
        # Fallback search engines
        self.use_fallback = True
        self.fallback_engines = ['duckduckgo', 'wikipedia']
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # seconds
        
        # Cache
        self.search_cache = {}
        self.cache_duration = 3600  # 1 hour
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Main search function with multiple fallback options"""
        try:
            # Check cache first
            cached_result = self._get_cached_result(query)
            if cached_result:
                return cached_result[:max_results]
            
            # Try different search engines
            results = []
            
            # Try Google Custom Search first
            if self.search_api_key != 'default_api_key':
                results = self._google_search(query, max_results)
            
            # Try Bing search if Google fails
            if not results and self.bing_api_key != 'default_bing_key':
                results = self._bing_search(query, max_results)
            
            # Try fallback engines
            if not results and self.use_fallback:
                results = self._fallback_search(query, max_results)
            
            # Cache results
            if results:
                self._cache_result(query, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return self._fallback_search(query, max_results)
    
    def _google_search(self, query: str, max_results: int) -> List[Dict]:
        """Search using Google Custom Search API"""
        try:
            self._rate_limit()
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.search_api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(max_results, 10)  # Google API limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'google',
                    'timestamp': datetime.now().isoformat()
                })
            
            logger.info(f"Google search returned {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return []
    
    def _bing_search(self, query: str, max_results: int) -> List[Dict]:
        """Search using Bing Search API"""
        try:
            self._rate_limit()
            
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {
                'Ocp-Apim-Subscription-Key': self.bing_api_key
            }
            params = {
                'q': query,
                'count': min(max_results, 50),  # Bing API limit
                'offset': 0
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('webPages', {}).get('value', []):
                results.append({
                    'title': item.get('name', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'bing',
                    'timestamp': datetime.now().isoformat()
                })
            
            logger.info(f"Bing search returned {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Bing search error: {e}")
            return []
    
    def _fallback_search(self, query: str, max_results: int) -> List[Dict]:
        """Fallback search using free APIs"""
        results = []
        
        # Try DuckDuckGo
        if 'duckduckgo' in self.fallback_engines:
            duckduckgo_results = self._duckduckgo_search(query, max_results)
            results.extend(duckduckgo_results)
        
        # Try Wikipedia
        if 'wikipedia' in self.fallback_engines and len(results) < max_results:
            wikipedia_results = self._wikipedia_search(query, max_results - len(results))
            results.extend(wikipedia_results)
        
        return results[:max_results]
    
    def _duckduckgo_search(self, query: str, max_results: int) -> List[Dict]:
        """Search using DuckDuckGo Instant Answer API"""
        try:
            self._rate_limit()
            
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Get abstract
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', query),
                    'url': data.get('AbstractURL', ''),
                    'snippet': data.get('Abstract', ''),
                    'source': 'duckduckgo',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Get related topics
            for topic in data.get('RelatedTopics', [])[:max_results-1]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic.get('Text', '').split(' - ')[0],
                        'url': topic.get('FirstURL', ''),
                        'snippet': topic.get('Text', ''),
                        'source': 'duckduckgo',
                        'timestamp': datetime.now().isoformat()
                    })
            
            logger.info(f"DuckDuckGo search returned {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    def _wikipedia_search(self, query: str, max_results: int) -> List[Dict]:
        """Search using Wikipedia API"""
        try:
            self._rate_limit()
            
            # Search for articles
            search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
            
            # First, search for the term
            opensearch_url = "https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'opensearch',
                'search': query,
                'limit': max_results,
                'format': 'json',
                'redirects': 'resolve'
            }
            
            response = requests.get(opensearch_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if len(data) >= 4:
                titles = data[1]
                descriptions = data[2]
                urls = data[3]
                
                for i, title in enumerate(titles[:max_results]):
                    results.append({
                        'title': title,
                        'url': urls[i] if i < len(urls) else '',
                        'snippet': descriptions[i] if i < len(descriptions) else '',
                        'source': 'wikipedia',
                        'timestamp': datetime.now().isoformat()
                    })
            
            logger.info(f"Wikipedia search returned {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return []
    
    def _rate_limit(self):
        """Simple rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def _get_cached_result(self, query: str) -> Optional[List[Dict]]:
        """Get cached search result"""
        if query in self.search_cache:
            cached_data = self.search_cache[query]
            if time.time() - cached_data['timestamp'] < self.cache_duration:
                return cached_data['results']
            else:
                del self.search_cache[query]
        return None
    
    def _cache_result(self, query: str, results: List[Dict]):
        """Cache search result"""
        self.search_cache[query] = {
            'results': results,
            'timestamp': time.time()
        }
    
    def clear_cache(self):
        """Clear search cache"""
        self.search_cache.clear()
    
    def get_search_suggestions(self, query: str) -> List[str]:
        """Get search suggestions for a query"""
        try:
            # Use Google Suggest API
            url = "https://suggestqueries.google.com/complete/search"
            params = {
                'client': 'firefox',
                'q': query
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            suggestions = data[1] if len(data) > 1 else []
            
            return suggestions[:10]  # Return top 10 suggestions
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
            return []
    
    def search_news(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for news articles"""
        try:
            # Use Google News RSS (free)
            url = "https://news.google.com/rss/search"
            params = {
                'q': query,
                'hl': 'en',
                'gl': 'US',
                'ceid': 'US:en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse RSS feed (basic implementation)
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            results = []
            for item in root.findall('.//item')[:max_results]:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                description = item.find('description').text if item.find('description') is not None else ''
                
                results.append({
                    'title': title,
                    'url': link,
                    'snippet': description,
                    'source': 'google_news',
                    'timestamp': datetime.now().isoformat()
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching news: {e}")
            return []

"""
Web Search Service for DieAI
Provides real-time web search capabilities using multiple search engines
"""
import requests
import json
import re
import time
from typing import List, Dict, Optional
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search using DuckDuckGo API"""
        try:
            # DuckDuckGo Instant Answer API
            url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1&skip_disambig=1"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Get abstract if available
                if data.get('Abstract'):
                    results.append({
                        'title': data.get('Heading', query),
                        'content': data.get('Abstract'),
                        'url': data.get('AbstractURL', ''),
                        'source': 'DuckDuckGo'
                    })
                
                # Get related topics
                for topic in data.get('RelatedTopics', [])[:max_results-1]:
                    if isinstance(topic, dict) and topic.get('Text'):
                        results.append({
                            'title': topic.get('Text', '').split(' - ')[0],
                            'content': topic.get('Text', ''),
                            'url': topic.get('FirstURL', ''),
                            'source': 'DuckDuckGo'
                        })
                
                return results
                
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            
        return []
    
    def search_bing(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search using Bing without API key (web scraping)"""
        try:
            url = f"https://www.bing.com/search?q={quote(query)}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                # Find search results
                for result in soup.find_all('li', class_='b_algo')[:max_results]:
                    title_elem = result.find('h2')
                    snippet_elem = result.find('p')
                    
                    if title_elem and snippet_elem:
                        title = title_elem.get_text(strip=True)
                        content = snippet_elem.get_text(strip=True)
                        link_elem = title_elem.find('a')
                        url = link_elem.get('href', '') if link_elem else ''
                        
                        results.append({
                            'title': title,
                            'content': content,
                            'url': url,
                            'source': 'Bing'
                        })
                
                return results
                
        except Exception as e:
            logger.error(f"Bing search error: {e}")
            
        return []
    
    def search_google(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search using Google (web scraping)"""
        try:
            url = f"https://www.google.com/search?q={quote(query)}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                # Find search results
                for result in soup.find_all('div', class_='g')[:max_results]:
                    title_elem = result.find('h3')
                    snippet_elem = result.find('span', class_='st') or result.find('div', class_='VwiC3b')
                    
                    if title_elem and snippet_elem:
                        title = title_elem.get_text(strip=True)
                        content = snippet_elem.get_text(strip=True)
                        
                        # Find URL
                        link_elem = result.find('a')
                        url = link_elem.get('href', '') if link_elem else ''
                        
                        results.append({
                            'title': title,
                            'content': content,
                            'url': url,
                            'source': 'Google'
                        })
                
                return results
                
        except Exception as e:
            logger.error(f"Google search error: {e}")
            
        return []
    
    def search_wikipedia(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search Wikipedia for additional context"""
        try:
            # Wikipedia API search
            search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(query)}"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('extract'):
                    return [{
                        'title': data.get('title', query),
                        'content': data.get('extract', ''),
                        'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                        'source': 'Wikipedia'
                    }]
                    
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            
        return []
    
    def search_web(self, query: str, max_results: int = 8) -> List[Dict]:
        """Comprehensive web search using multiple engines"""
        all_results = []
        
        # Try multiple search engines
        engines = [
            self.search_duckduckgo,
            self.search_wikipedia,
            self.search_bing,
            self.search_google
        ]
        
        for engine in engines:
            try:
                results = engine(query, max_results // len(engines) + 1)
                all_results.extend(results)
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.error(f"Search engine error: {e}")
                continue
        
        # Remove duplicates and limit results
        seen_urls = set()
        unique_results = []
        
        for result in all_results:
            if result['url'] not in seen_urls and len(unique_results) < max_results:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        return unique_results
    
    def extract_key_info(self, results: List[Dict]) -> str:
        """Extract key information from search results"""
        if not results:
            return "No relevant information found on the web."
        
        # Combine information from multiple sources
        key_info = []
        
        for result in results:
            content = result.get('content', '').strip()
            if content and len(content) > 50:  # Only include substantial content
                source = result.get('source', 'Web')
                key_info.append(f"[{source}] {content}")
        
        return "\n\n".join(key_info[:5])  # Limit to top 5 most relevant pieces
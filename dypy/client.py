"""
DieAI API Client
"""

import requests
import json
import time
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urljoin

from .models import ChatCompletion, Message, Usage, Choice, SearchResponse, SearchResult, ModelInfo, UsageStats


class APIError(Exception):
    """Base exception for DieAI API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class AuthenticationError(APIError):
    """Exception for authentication errors"""
    pass


class RateLimitError(APIError):
    """Exception for rate limit errors"""
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        self.retry_after = retry_after
        super().__init__(message, **kwargs)


class DieAI:
    """
    DieAI API Client
    
    Usage:
        import dypy
        
        client = dypy.DieAI(api_key="your-api-key")
        
        # Chat completion
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello!"}]
        )
        
        # Search
        results = client.search.query("artificial intelligence")
    """
    
    def __init__(self, api_key: str, base_url: str = "http://localhost:5000"):
        """
        Initialize DieAI client
        
        Args:
            api_key: Your DieAI API key
            base_url: Base URL for the DieAI API (default: http://localhost:5000)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'dypy-client/1.0.0'
        })
        
        # Initialize sub-clients
        self.chat = ChatClient(self)
        self.search = SearchClient(self)
        self.models = ModelsClient(self)
        self.usage = UsageClient(self)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make HTTP request to DieAI API"""
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                raise RateLimitError(
                    "Rate limit exceeded",
                    status_code=429,
                    retry_after=retry_after,
                    response=response.json() if response.content else None
                )
            
            # Handle authentication errors
            if response.status_code == 401:
                raise AuthenticationError(
                    "Invalid API key",
                    status_code=401,
                    response=response.json() if response.content else None
                )
            
            # Handle other client errors
            if 400 <= response.status_code < 500:
                error_data = response.json() if response.content else {}
                raise APIError(
                    error_data.get('error', f'Client error: {response.status_code}'),
                    status_code=response.status_code,
                    response=error_data
                )
            
            # Handle server errors
            if response.status_code >= 500:
                raise APIError(
                    f"Server error: {response.status_code}",
                    status_code=response.status_code
                )
            
            return response.json()
            
        except requests.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")


class ChatClient:
    """Chat completion client"""
    
    def __init__(self, client: DieAI):
        self.client = client
        self.completions = ChatCompletionsClient(client)


class ChatCompletionsClient:
    """Chat completions endpoint client"""
    
    def __init__(self, client: DieAI):
        self.client = client
    
    def create(
        self,
        messages: List[Union[Message, Dict[str, str]]],
        model: str = "dieai-transformer",
        max_tokens: Optional[int] = None,
        temperature: float = 0.8,
        top_p: float = 0.95,
        top_k: int = 50,
        use_search: bool = False,
        stream: bool = False
    ) -> ChatCompletion:
        """
        Create a chat completion
        
        Args:
            messages: List of messages in the conversation
            model: Model to use (default: "dieai-transformer")
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            use_search: Whether to use search integration
            stream: Whether to stream the response (not implemented yet)
        
        Returns:
            ChatCompletion object with the generated response
        """
        # Convert Message objects to dicts if needed
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, Message):
                formatted_messages.append(msg.to_dict())
            else:
                formatted_messages.append(msg)
        
        # Use the latest message as the prompt for the current API
        latest_message = formatted_messages[-1]["content"]
        
        payload = {
            "message": latest_message,
            "use_search": use_search,
            "temperature": temperature,
            "max_tokens": max_tokens or 512,
            "top_p": top_p,
            "top_k": top_k
        }
        
        response_data = self.client._make_request('POST', '/api/chat', json=payload)
        
        # Transform response to match OpenAI format
        completion_id = f"chatcmpl-{int(time.time())}"
        
        choice = Choice(
            index=0,
            message=Message(role="assistant", content=response_data["response"]),
            finish_reason="stop"
        )
        
        usage = Usage(
            prompt_tokens=len(latest_message.split()),  # Rough estimate
            completion_tokens=len(response_data["response"].split()),  # Rough estimate
            total_tokens=len(latest_message.split()) + len(response_data["response"].split())
        )
        
        return ChatCompletion(
            id=completion_id,
            object="chat.completion",
            created=int(time.time()),
            model=model,
            choices=[choice],
            usage=usage
        )


class SearchClient:
    """Search functionality client"""
    
    def __init__(self, client: DieAI):
        self.client = client
    
    def query(self, query: str, max_results: int = 10) -> SearchResponse:
        """
        Search for information
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
        
        Returns:
            SearchResponse with search results
        """
        payload = {
            "query": query,
            "max_results": max_results
        }
        
        start_time = time.time()
        response_data = self.client._make_request('POST', '/api/search', json=payload)
        search_time = time.time() - start_time
        
        results = [
            SearchResult(
                title=result.get("title", ""),
                url=result.get("url", ""),
                snippet=result.get("snippet", ""),
                source=result.get("source"),
                relevance_score=result.get("relevance_score")
            )
            for result in response_data.get("results", [])
        ]
        
        return SearchResponse(
            query=query,
            results=results,
            total_results=len(results),
            search_time=search_time
        )


class ModelsClient:
    """Models information client"""
    
    def __init__(self, client: DieAI):
        self.client = client
    
    def list(self) -> List[ModelInfo]:
        """List available models"""
        response_data = self.client._make_request('GET', '/api/models')
        
        models = []
        for model_data in response_data.get("models", []):
            models.append(ModelInfo(
                id=model_data.get("id", "dieai-transformer"),
                name=model_data.get("name", "DieAI Transformer"),
                description=model_data.get("description", "Custom transformer model"),
                max_tokens=model_data.get("max_tokens", 1024),
                capabilities=model_data.get("capabilities", ["chat", "completion"])
            ))
        
        return models


class UsageClient:
    """Usage statistics client"""
    
    def __init__(self, client: DieAI):
        self.client = client
    
    def get(self) -> UsageStats:
        """Get usage statistics for the current API key"""
        response_data = self.client._make_request('GET', '/api/usage')
        
        return UsageStats(
            total_requests=response_data.get("total_requests", 0),
            total_tokens=response_data.get("total_tokens", 0),
            requests_today=response_data.get("requests_today", 0),
            tokens_today=response_data.get("tokens_today", 0),
            rate_limit_remaining=response_data.get("rate_limit_remaining", 0),
            rate_limit_reset=response_data.get("rate_limit_reset", time.time())
        )
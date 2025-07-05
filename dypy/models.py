"""
Data models for DieAI API responses
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Usage:
    """Token usage information for API requests"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class Message:
    """Chat message structure"""
    role: str  # 'system', 'user', or 'assistant'
    content: str
    name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result


@dataclass
class Choice:
    """Individual choice from chat completion"""
    index: int
    message: Message
    finish_reason: str
    

@dataclass
class ChatCompletion:
    """Chat completion response from DieAI API"""
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Usage
    
    def __post_init__(self):
        """Convert dict choices to Choice objects if needed"""
        if self.choices and isinstance(self.choices[0], dict):
            self.choices = [
                Choice(
                    index=choice["index"],
                    message=Message(**choice["message"]),
                    finish_reason=choice.get("finish_reason", "stop")
                )
                for choice in self.choices
            ]


@dataclass
class SearchResult:
    """Search result from DieAI search API"""
    title: str
    url: str
    snippet: str
    source: Optional[str] = None
    relevance_score: Optional[float] = None


@dataclass
class SearchResponse:
    """Search response containing multiple results"""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time: float


@dataclass
class ModelInfo:
    """Information about available models"""
    id: str
    name: str
    description: str
    max_tokens: int
    capabilities: List[str]


@dataclass
class UsageStats:
    """User usage statistics"""
    total_requests: int
    total_tokens: int
    requests_today: int
    tokens_today: int
    rate_limit_remaining: int
    rate_limit_reset: datetime


@dataclass
class APIKeyInfo:
    """API key information"""
    key_id: str
    created_at: datetime
    last_used: Optional[datetime]
    usage_count: int
    is_active: bool
    rate_limit_tier: str
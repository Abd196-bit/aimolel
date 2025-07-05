"""
DyPy - Python client library for DieAI API
A simple and intuitive interface for interacting with DieAI's custom transformer model.
"""

from .client import DieAI, APIError, RateLimitError, AuthenticationError
from .models import ChatCompletion, Message, Usage, SearchResult

__version__ = "1.0.0"
__author__ = "DieAI Team"
__email__ = "support@dieai.com"

__all__ = [
    "DieAI",
    "APIError", 
    "RateLimitError",
    "AuthenticationError",
    "ChatCompletion",
    "Message",
    "Usage",
    "SearchResult"
]
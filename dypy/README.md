# DyPy - DieAI Python Client Library

A simple and intuitive Python library for interacting with DieAI's custom transformer model API, designed to work similarly to the OpenAI Python library.

## Installation

```bash
pip install dypy
```

Or install from source:
```bash
git clone <repository-url>
cd dypy
pip install -e .
```

## Quick Start

### Basic Setup

```python
import dypy

# Initialize the client with your API key
client = dypy.DieAI(api_key="your-dieai-api-key")

# For local development (default)
client = dypy.DieAI(api_key="your-api-key", base_url="http://localhost:5000")
```

### Chat Completions

```python
# Simple chat completion
response = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

print(response.choices[0].message.content)
```

### Advanced Chat with Search

```python
# Chat with search integration
response = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "What are the latest developments in AI?"}
    ],
    use_search=True,
    temperature=0.7,
    max_tokens=500
)

print(response.choices[0].message.content)
```

### Conversation History

```python
# Multi-turn conversation
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is machine learning?"},
]

response = client.chat.completions.create(messages=messages)
messages.append({"role": "assistant", "content": response.choices[0].message.content})

# Continue the conversation
messages.append({"role": "user", "content": "Can you give me an example?"})
response = client.chat.completions.create(messages=messages)
```

### Search API

```python
# Search for information
search_results = client.search.query("artificial intelligence trends 2024")

for result in search_results.results:
    print(f"Title: {result.title}")
    print(f"URL: {result.url}")
    print(f"Snippet: {result.snippet}")
    print("---")
```

### Usage Statistics

```python
# Get usage statistics
usage = client.usage.get()
print(f"Total requests: {usage.total_requests}")
print(f"Requests today: {usage.requests_today}")
print(f"Rate limit remaining: {usage.rate_limit_remaining}")
```

### Available Models

```python
# List available models
models = client.models.list()
for model in models:
    print(f"Model: {model.name}")
    print(f"Description: {model.description}")
    print(f"Max tokens: {model.max_tokens}")
```

## API Reference

### DieAI Client

```python
client = dypy.DieAI(
    api_key="your-api-key",
    base_url="http://localhost:5000"  # Optional, defaults to localhost
)
```

### Chat Completions

```python
response = client.chat.completions.create(
    messages=[...],           # Required: List of message objects
    model="dieai-transformer", # Optional: Model to use
    max_tokens=512,           # Optional: Maximum tokens to generate
    temperature=0.8,          # Optional: Sampling temperature (0.0-2.0)
    top_p=0.95,              # Optional: Nucleus sampling parameter
    top_k=50,                # Optional: Top-k sampling parameter
    use_search=False,        # Optional: Enable search integration
    stream=False             # Optional: Stream response (not implemented)
)
```

### Search

```python
results = client.search.query(
    query="search term",      # Required: Search query
    max_results=10           # Optional: Maximum results to return
)
```

## Error Handling

```python
try:
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Hello!"}]
    )
except dypy.AuthenticationError:
    print("Invalid API key")
except dypy.RateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
except dypy.APIError as e:
    print(f"API error: {e.message}")
```

## Examples

### Simple Chatbot

```python
import dypy

def simple_chatbot():
    client = dypy.DieAI(api_key="your-api-key")
    
    print("DieAI Chatbot (type 'quit' to exit)")
    messages = []
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
            
        messages.append({"role": "user", "content": user_input})
        
        try:
            response = client.chat.completions.create(messages=messages)
            ai_response = response.choices[0].message.content
            print(f"AI: {ai_response}")
            
            messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    simple_chatbot()
```

### Search-Enhanced Assistant

```python
import dypy

def search_assistant():
    client = dypy.DieAI(api_key="your-api-key")
    
    query = input("Ask me anything: ")
    
    # First, search for relevant information
    search_results = client.search.query(query, max_results=3)
    
    # Use search results as context for the AI
    context = "Here's some relevant information:\\n"
    for result in search_results.results:
        context += f"- {result.title}: {result.snippet}\\n"
    
    messages = [
        {"role": "system", "content": "Use the provided context to answer the user's question accurately."},
        {"role": "user", "content": f"Context:\\n{context}\\n\\nQuestion: {query}"}
    ]
    
    response = client.chat.completions.create(
        messages=messages,
        use_search=True,
        temperature=0.7
    )
    
    print(f"Answer: {response.choices[0].message.content}")

if __name__ == "__main__":
    search_assistant()
```

## Configuration

### Environment Variables

You can set your API key using environment variables:

```bash
export DIEAI_API_KEY="your-api-key"
export DIEAI_BASE_URL="http://localhost:5000"  # Optional
```

```python
import os
import dypy

client = dypy.DieAI(
    api_key=os.getenv("DIEAI_API_KEY"),
    base_url=os.getenv("DIEAI_BASE_URL", "http://localhost:5000")
)
```

## Requirements

- Python 3.7+
- requests
- typing_extensions (for Python < 3.8)

## License

MIT License

## Support

For support and questions, please visit our documentation or contact support@dieai.com.
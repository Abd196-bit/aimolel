# DyPy Quick Start Guide

## Installation and Setup

### Step 1: Get Your API Key
1. Visit your DieAI application at `http://localhost:5000`
2. Create an account or log in
3. Go to the Dashboard
4. Click "Generate New Key" to create an API key
5. Copy the API key (it looks like: `dieai_abc123...`)

### Step 2: Install the Library
```bash
# From the dypy directory
pip install -e .

# Or directly use the library without installation
# Just make sure you're in the right directory
```

### Step 3: Basic Usage

```python
import dypy

# Initialize with your API key
client = dypy.DieAI(api_key="your-api-key-here")

# Simple chat
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

## Complete Example

```python
#!/usr/bin/env python3
import dypy

def main():
    # Replace with your actual API key
    api_key = "dieai_your_key_here"
    
    # Create client
    client = dypy.DieAI(api_key=api_key, base_url="http://localhost:5000")
    
    # Chat example
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is artificial intelligence?"}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        print("AI Response:")
        print(response.choices[0].message.content)
        print(f"\\nTokens used: {response.usage.total_tokens}")
        
    except dypy.AuthenticationError:
        print("Invalid API key. Please check your key.")
    except dypy.RateLimitError as e:
        print(f"Rate limit exceeded. Wait {e.retry_after} seconds.")
    except dypy.APIError as e:
        print(f"API Error: {e.message}")

if __name__ == "__main__":
    main()
```

## Testing the Library

Run the test script to verify everything works:

```bash
cd dypy
python test_dypy.py
```

This will:
- Test basic chat functionality
- Test search features
- Show usage statistics
- Demonstrate error handling

## API Compatibility

The DyPy library is designed to be similar to the OpenAI Python library:

| OpenAI | DyPy | Notes |
|--------|------|-------|
| `openai.ChatCompletion.create()` | `client.chat.completions.create()` | Similar interface |
| `openai.api_key` | `client.api_key` | Set during initialization |
| Message format | Same | `{"role": "user", "content": "..."}` |
| Response format | Similar | `.choices[0].message.content` |

## Error Handling

```python
import dypy

client = dypy.DieAI(api_key="your-key")

try:
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Hello"}]
    )
except dypy.AuthenticationError:
    print("Check your API key")
except dypy.RateLimitError as e:
    print(f"Rate limited, retry in {e.retry_after}s")
except dypy.APIError as e:
    print(f"API error: {e.message}")
```

## Advanced Features

### Search Integration
```python
# Enable search for better responses
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Latest AI news"}],
    use_search=True
)
```

### Direct Search
```python
results = client.search.query("machine learning trends")
for result in results.results:
    print(f"{result.title}: {result.snippet}")
```

### Usage Statistics
```python
usage = client.usage.get()
print(f"Requests today: {usage.requests_today}")
print(f"Rate limit remaining: {usage.rate_limit_remaining}")
```

## Tips

1. **API Key Security**: Never commit API keys to version control
2. **Rate Limits**: The library automatically handles rate limiting
3. **Error Handling**: Always wrap API calls in try-except blocks
4. **Temperature**: Use 0.1-0.3 for focused responses, 0.7-1.0 for creative responses
5. **Max Tokens**: Set reasonable limits to control response length

## Troubleshooting

### "Authentication failed"
- Check your API key is correct
- Ensure the DieAI server is running
- Verify the base_url is correct

### "Connection refused"
- Make sure DieAI server is running on localhost:5000
- Check if the port is correct

### "Rate limit exceeded"
- Wait for the specified retry time
- Consider reducing request frequency
- Check your usage limits in the dashboard

## Building Your Own Chatbot

```python
import dypy

def chatbot():
    client = dypy.DieAI(api_key="your-key")
    messages = []
    
    print("Chatbot ready! Type 'quit' to exit.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
            
        messages.append({"role": "user", "content": user_input})
        
        response = client.chat.completions.create(messages=messages)
        ai_response = response.choices[0].message.content
        
        print(f"AI: {ai_response}")
        messages.append({"role": "assistant", "content": ai_response})

if __name__ == "__main__":
    chatbot()
```

This creates a simple but functional chatbot using your DieAI API!
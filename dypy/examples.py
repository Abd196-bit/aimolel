"""
Example usage of the DyPy library
"""

import dypy
import os
import time


def simple_chat_example():
    """Simple chat completion example"""
    print("=== Simple Chat Example ===")
    
    # Initialize client (replace with your actual API key)
    client = dypy.DieAI(api_key="your-api-key-here")
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": "Hello! Can you tell me about transformers in AI?"}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        print(f"AI Response: {response.choices[0].message.content}")
        print(f"Tokens used: {response.usage.total_tokens}")
        
    except dypy.APIError as e:
        print(f"Error: {e.message}")


def conversation_example():
    """Multi-turn conversation example"""
    print("\\n=== Conversation Example ===")
    
    client = dypy.DieAI(api_key="your-api-key-here")
    
    # Start with system message
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant specializing in technology."},
        {"role": "user", "content": "What is machine learning?"}
    ]
    
    try:
        # First exchange
        response = client.chat.completions.create(messages=messages)
        ai_response = response.choices[0].message.content
        print(f"User: What is machine learning?")
        print(f"AI: {ai_response}")
        
        # Add AI response to conversation
        messages.append({"role": "assistant", "content": ai_response})
        
        # Continue conversation
        messages.append({"role": "user", "content": "Can you give me a practical example?"})
        
        response = client.chat.completions.create(messages=messages)
        ai_response = response.choices[0].message.content
        print(f"\\nUser: Can you give me a practical example?")
        print(f"AI: {ai_response}")
        
    except dypy.APIError as e:
        print(f"Error: {e.message}")


def search_enhanced_chat():
    """Search-enhanced chat example"""
    print("\\n=== Search-Enhanced Chat Example ===")
    
    client = dypy.DieAI(api_key="your-api-key-here")
    
    try:
        # Search for information first
        search_results = client.search.query("latest AI developments 2024", max_results=3)
        
        print(f"Found {len(search_results.results)} search results:")
        for i, result in enumerate(search_results.results, 1):
            print(f"{i}. {result.title}")
            print(f"   {result.url}")
            print(f"   {result.snippet[:100]}...")
            print()
        
        # Use search results in chat
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": "What are the latest developments in AI for 2024?"}
            ],
            use_search=True,
            temperature=0.8
        )
        
        print(f"AI Response with Search: {response.choices[0].message.content}")
        
    except dypy.APIError as e:
        print(f"Error: {e.message}")


def usage_statistics_example():
    """Usage statistics example"""
    print("\\n=== Usage Statistics Example ===")
    
    client = dypy.DieAI(api_key="your-api-key-here")
    
    try:
        usage = client.usage.get()
        print(f"Total requests: {usage.total_requests}")
        print(f"Total tokens: {usage.total_tokens}")
        print(f"Requests today: {usage.requests_today}")
        print(f"Tokens today: {usage.tokens_today}")
        print(f"Rate limit remaining: {usage.rate_limit_remaining}")
        
        # List available models
        models = client.models.list()
        print(f"\\nAvailable models: {len(models)}")
        for model in models:
            print(f"- {model.name}: {model.description}")
            
    except dypy.APIError as e:
        print(f"Error: {e.message}")


def interactive_chatbot():
    """Interactive chatbot example"""
    print("\\n=== Interactive Chatbot ===")
    print("Type 'quit' to exit, 'search:query' to search, 'clear' to clear history")
    
    client = dypy.DieAI(api_key="your-api-key-here")
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant. Be concise but informative."}
    ]
    
    while True:
        try:
            user_input = input("\\nYou: ").strip()
            
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            elif user_input.lower() == 'clear':
                messages = [messages[0]]  # Keep system message
                print("Conversation history cleared.")
                continue
            elif user_input.lower().startswith('search:'):
                query = user_input[7:].strip()
                if query:
                    search_results = client.search.query(query, max_results=3)
                    print(f"\\nSearch results for '{query}':")
                    for i, result in enumerate(search_results.results, 1):
                        print(f"{i}. {result.title}")
                        print(f"   {result.snippet[:150]}...")
                continue
            elif not user_input:
                continue
            
            messages.append({"role": "user", "content": user_input})
            
            response = client.chat.completions.create(
                messages=messages,
                temperature=0.8,
                max_tokens=300
            )
            
            ai_response = response.choices[0].message.content
            print(f"AI: {ai_response}")
            
            messages.append({"role": "assistant", "content": ai_response})
            
            # Show token usage
            print(f"[Tokens: {response.usage.total_tokens}]")
            
        except KeyboardInterrupt:
            print("\\nGoodbye!")
            break
        except dypy.RateLimitError as e:
            print(f"Rate limit exceeded. Please wait {e.retry_after} seconds.")
            time.sleep(e.retry_after)
        except dypy.AuthenticationError:
            print("Authentication failed. Please check your API key.")
            break
        except dypy.APIError as e:
            print(f"API Error: {e.message}")
        except Exception as e:
            print(f"Unexpected error: {e}")


def batch_processing_example():
    """Batch processing example"""
    print("\\n=== Batch Processing Example ===")
    
    client = dypy.DieAI(api_key="your-api-key-here")
    
    # List of questions to process
    questions = [
        "What is artificial intelligence?",
        "How does machine learning work?",
        "What are neural networks?",
        "Explain deep learning in simple terms.",
        "What is the difference between AI and ML?"
    ]
    
    print(f"Processing {len(questions)} questions...")
    
    for i, question in enumerate(questions, 1):
        try:
            print(f"\\n{i}. Question: {question}")
            
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": question}],
                temperature=0.7,
                max_tokens=150
            )
            
            answer = response.choices[0].message.content
            print(f"   Answer: {answer[:200]}{'...' if len(answer) > 200 else ''}")
            
            # Small delay to respect rate limits
            time.sleep(0.5)
            
        except dypy.RateLimitError as e:
            print(f"   Rate limit reached. Waiting {e.retry_after}s...")
            time.sleep(e.retry_after)
        except dypy.APIError as e:
            print(f"   Error: {e.message}")


def error_handling_example():
    """Error handling example"""
    print("\\n=== Error Handling Example ===")
    
    # Example with invalid API key
    try:
        client = dypy.DieAI(api_key="invalid-key")
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello"}]
        )
    except dypy.AuthenticationError as e:
        print(f"Authentication error (expected): {e.message}")
    
    # Example with proper error handling
    client = dypy.DieAI(api_key="your-api-key-here")
    
    for i in range(3):  # Try multiple requests to potentially hit rate limit
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": f"Test message {i+1}"}]
            )
            print(f"Request {i+1}: Success")
            
        except dypy.RateLimitError as e:
            print(f"Request {i+1}: Rate limited, retry after {e.retry_after}s")
            time.sleep(e.retry_after)
        except dypy.APIError as e:
            print(f"Request {i+1}: API error - {e.message}")
        except Exception as e:
            print(f"Request {i+1}: Unexpected error - {e}")


if __name__ == "__main__":
    # Set your API key here or via environment variable
    api_key = os.getenv("DIEAI_API_KEY", "your-api-key-here")
    
    if api_key == "your-api-key-here":
        print("Please set your API key in the DIEAI_API_KEY environment variable")
        print("or replace 'your-api-key-here' in the examples with your actual key.")
        print("\\nYou can get an API key by:")
        print("1. Visiting the DieAI web interface")
        print("2. Creating an account or logging in")
        print("3. Going to the dashboard")
        print("4. Generating a new API key")
        exit(1)
    
    # Update all examples to use the environment variable
    for func_name in globals():
        if func_name.endswith('_example') or func_name == 'interactive_chatbot':
            func = globals()[func_name]
            if callable(func):
                # Replace the API key in the function
                func.__code__ = func.__code__.replace(
                    co_consts=tuple(
                        api_key if const == "your-api-key-here" else const
                        for const in func.__code__.co_consts
                    )
                )
    
    print("DyPy Library Examples")
    print("=" * 50)
    
    # Run examples
    simple_chat_example()
    conversation_example()
    search_enhanced_chat()
    usage_statistics_example()
    batch_processing_example()
    error_handling_example()
    
    # Ask user if they want to try interactive chatbot
    try:
        choice = input("\\nWould you like to try the interactive chatbot? (y/n): ")
        if choice.lower().startswith('y'):
            interactive_chatbot()
    except KeyboardInterrupt:
        print("\\nExiting...")
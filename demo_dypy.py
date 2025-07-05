#!/usr/bin/env python3
"""
Simple demonstration of the DyPy library
This shows how to use the library to connect to your DieAI API
"""

import sys
import os
import requests

# Add the dypy directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dypy'))

# Now import the DyPy library
from client import DieAI, APIError, AuthenticationError, RateLimitError
from models import Message

def demo_dypy_library():
    """Demonstrate the DyPy library functionality"""
    print("DyPy Library Demo")
    print("=" * 50)
    
    # Check if DieAI server is running
    try:
        response = requests.get("http://localhost:5000", timeout=3)
        print("✓ DieAI server is running")
    except requests.exceptions.RequestException:
        print("✗ DieAI server is not running")
        print("  Please start your DieAI application first")
        return
    
    # Demo with a test API key (you'll need to replace this with a real one)
    api_key = "dieai_demo_key"  # Replace with actual key from dashboard
    
    print(f"\nInitializing DyPy client...")
    client = DieAI(api_key=api_key, base_url="http://localhost:5000")
    print("✓ Client created successfully")
    
    # Test 1: Simple chat
    print("\n1. Testing simple chat...")
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": "Hello! What is DieAI?"}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        print("✓ Chat response received:")
        print(f"  AI: {response.choices[0].message.content}")
        print(f"  Tokens: {response.usage.total_tokens}")
        
    except AuthenticationError:
        print("✗ Authentication failed")
        print("  To fix this:")
        print("  1. Go to http://localhost:5000")
        print("  2. Login or create account")
        print("  3. Go to Dashboard")
        print("  4. Generate new API key")
        print("  5. Replace 'dieai_demo_key' in this script with your real key")
        return
        
    except APIError as e:
        print(f"✗ API Error: {e.message}")
        return
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return
    
    # Test 2: Conversation
    print("\n2. Testing conversation...")
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is machine learning?"}
        ]
        
        response = client.chat.completions.create(messages=messages)
        ai_response = response.choices[0].message.content
        print(f"  User: What is machine learning?")
        print(f"  AI: {ai_response[:100]}...")
        
        # Continue conversation
        messages.append({"role": "assistant", "content": ai_response})
        messages.append({"role": "user", "content": "Give me an example."})
        
        response = client.chat.completions.create(messages=messages)
        print(f"  User: Give me an example.")
        print(f"  AI: {response.choices[0].message.content[:100]}...")
        
        print("✓ Conversation test successful")
        
    except Exception as e:
        print(f"✗ Conversation test failed: {e}")
    
    # Test 3: Search functionality  
    print("\n3. Testing search...")
    try:
        search_results = client.search.query("artificial intelligence", max_results=3)
        print(f"✓ Search completed: {len(search_results.results)} results")
        
        for i, result in enumerate(search_results.results[:2], 1):
            print(f"  {i}. {result.title[:50]}...")
            
    except Exception as e:
        print(f"✗ Search test failed: {e}")
    
    # Test 4: Usage stats
    print("\n4. Testing usage statistics...")
    try:
        usage = client.usage.get()
        print("✓ Usage statistics:")
        print(f"  Total requests: {usage.total_requests}")
        print(f"  Rate limit remaining: {usage.rate_limit_remaining}")
        
    except Exception as e:
        print(f"✗ Usage stats failed: {e}")
    
    print("\n" + "=" * 50)
    print("Demo completed!")
    print("\nTo use this library in your own projects:")
    print("1. Copy the 'dypy' folder to your project")
    print("2. Import: from dypy import DieAI")
    print("3. Initialize: client = DieAI(api_key='your-key')")
    print("4. Use: response = client.chat.completions.create(...)")


def interactive_chat():
    """Simple interactive chat demo"""
    print("\nInteractive Chat Demo")
    print("Type 'quit' to exit")
    
    # Get API key from user
    api_key = input("Enter your API key (from DieAI dashboard): ").strip()
    if not api_key:
        print("No API key provided, exiting.")
        return
    
    client = DieAI(api_key=api_key, base_url="http://localhost:5000")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
                
            if not user_input:
                continue
            
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": user_input}],
                temperature=0.8,
                max_tokens=200
            )
            
            print(f"DieAI: {response.choices[0].message.content}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except AuthenticationError:
            print("Authentication failed. Check your API key.")
            break
        except RateLimitError as e:
            print(f"Rate limit exceeded. Wait {e.retry_after} seconds.")
        except APIError as e:
            print(f"Error: {e.message}")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    demo_dypy_library()
    
    # Ask if user wants to try interactive chat
    try:
        choice = input("\nTry interactive chat? (y/n): ")
        if choice.lower().startswith('y'):
            interactive_chat()
    except KeyboardInterrupt:
        print("\nExiting...")
#!/usr/bin/env python3
"""
Test script for the DyPy library
This script demonstrates how to use the DyPy library to interact with your DieAI API
"""

import sys
import os

# Add the current directory to Python path to import dypy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dypy


def test_basic_functionality():
    """Test basic functionality of the DyPy library"""
    print("Testing DyPy Library with DieAI API")
    print("=" * 50)
    
    # You'll need to replace this with an actual API key from your DieAI dashboard
    api_key = "dieai_your_api_key_here"  # Replace with real API key
    
    # Initialize the client
    try:
        client = dypy.DieAI(api_key=api_key, base_url="http://localhost:5000")
        print("✓ Client initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize client: {e}")
        return False
    
    # Test 1: Simple chat completion
    print("\n1. Testing simple chat completion...")
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": "Hello! What is DieAI?"}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        print(f"✓ Response received: {response.choices[0].message.content[:100]}...")
        print(f"  Tokens used: {response.usage.total_tokens}")
        
    except dypy.AuthenticationError:
        print("✗ Authentication failed - please check your API key")
        print("  To get an API key:")
        print("  1. Visit http://localhost:5000")
        print("  2. Create an account or log in")
        print("  3. Go to the dashboard")
        print("  4. Generate a new API key")
        return False
    except dypy.APIError as e:
        print(f"✗ API Error: {e.message}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    # Test 2: Search functionality
    print("\n2. Testing search functionality...")
    try:
        search_results = client.search.query("artificial intelligence", max_results=3)
        print(f"✓ Search completed: {len(search_results.results)} results found")
        
        for i, result in enumerate(search_results.results[:2], 1):
            print(f"  {i}. {result.title[:60]}...")
            
    except dypy.APIError as e:
        print(f"✗ Search Error: {e.message}")
    except Exception as e:
        print(f"✗ Search failed: {e}")
    
    # Test 3: Usage statistics
    print("\n3. Testing usage statistics...")
    try:
        usage = client.usage.get()
        print(f"✓ Usage stats retrieved:")
        print(f"  Total requests: {usage.total_requests}")
        print(f"  Rate limit remaining: {usage.rate_limit_remaining}")
        
    except dypy.APIError as e:
        print(f"✗ Usage stats error: {e.message}")
    except Exception as e:
        print(f"✗ Usage stats failed: {e}")
    
    # Test 4: Model information
    print("\n4. Testing model information...")
    try:
        models = client.models.list()
        print(f"✓ Models retrieved: {len(models)} available")
        
        for model in models:
            print(f"  - {model.name}: {model.description}")
            
    except dypy.APIError as e:
        print(f"✗ Models error: {e.message}")
    except Exception as e:
        print(f"✗ Models failed: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed successfully! 🎉")
    print("\nNext steps:")
    print("1. Replace the API key with your actual key from the dashboard")
    print("2. Try the interactive examples in examples.py")
    print("3. Build your own chatbot using the library")
    
    return True


def interactive_demo():
    """Interactive demo of the DyPy library"""
    print("\nInteractive Demo")
    print("=" * 20)
    
    api_key = input("Enter your DieAI API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("Skipping interactive demo. Get an API key from http://localhost:5000")
        return
    
    client = dypy.DieAI(api_key=api_key, base_url="http://localhost:5000")
    
    print("\nType your message (or 'quit' to exit):")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
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
        except dypy.AuthenticationError:
            print("Authentication failed. Please check your API key.")
            break
        except dypy.RateLimitError as e:
            print(f"Rate limit exceeded. Please wait {e.retry_after} seconds.")
        except dypy.APIError as e:
            print(f"Error: {e.message}")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    print("DyPy Library Test Script")
    print("This script tests the DyPy library with your DieAI API")
    print()
    
    # Check if DieAI server is running
    import requests
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print("✓ DieAI server is running on http://localhost:5000")
    except requests.exceptions.RequestException:
        print("✗ DieAI server is not running on http://localhost:5000")
        print("  Please make sure your DieAI application is running first")
        sys.exit(1)
    
    # Run tests
    success = test_basic_functionality()
    
    if success:
        # Ask if user wants to try interactive demo
        try:
            choice = input("\nWould you like to try the interactive demo? (y/n): ")
            if choice.lower().startswith('y'):
                interactive_demo()
        except KeyboardInterrupt:
            print("\nExiting...")
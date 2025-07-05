#!/usr/bin/env python3
"""
Demo script for DieAI - OpenAI-like API for chatbots
Shows how to use the library to build AI applications
"""

try:
    from dieai_knowledge import DieAI
except ImportError:
    print("DieAI Library not installed. Install with: pip install dieai")
    print("For local development, run from the project directory:")
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from dieai_knowledge import DieAI

def demo_openai_style_api():
    """Demonstrate OpenAI-style chat completions API"""
    print("=== DieAI OPENAI-STYLE API DEMO ===")
    
    # Initialize client
    client = DieAI()
    
    # Math questions
    print("\n1. Math Problem Solving:")
    response = client.chat.completions.create(
        model="dieai-1.0",
        messages=[
            {"role": "user", "content": "What is 15 + 25?"}
        ]
    )
    print(f"User: What is 15 + 25?")
    print(f"DieAI: {response.choices[0].message.content}")
    
    # Geometry calculation
    print("\n2. Geometry Calculation:")
    response = client.chat.completions.create(
        model="dieai-1.0",
        messages=[
            {"role": "user", "content": "Calculate the area of a circle with radius 5"}
        ]
    )
    print(f"User: Calculate the area of a circle with radius 5")
    print(f"DieAI: {response.choices[0].message.content}")
    
    # Unit conversion
    print("\n3. Unit Conversion:")
    response = client.chat.completions.create(
        model="dieai-1.0",
        messages=[
            {"role": "user", "content": "Convert 100 meters to feet"}
        ]
    )
    print(f"User: Convert 100 meters to feet")
    print(f"DieAI: {response.choices[0].message.content}")
    
    # Science question
    print("\n4. Science Question:")
    response = client.chat.completions.create(
        model="dieai-1.0",
        messages=[
            {"role": "user", "content": "What is the speed of light?"}
        ]
    )
    print(f"User: What is the speed of light?")
    print(f"DieAI: {response.choices[0].message.content}")
    
    # Physics calculation
    print("\n5. Physics Calculation:")
    response = client.chat.completions.create(
        model="dieai-1.0",
        messages=[
            {"role": "user", "content": "Calculate force with mass 10 and acceleration 9.8"}
        ]
    )
    print(f"User: Calculate force with mass 10 and acceleration 9.8")
    print(f"DieAI: {response.choices[0].message.content}")

def demo_chatbot_conversation():
    """Demonstrate multi-turn conversation like a chatbot"""
    print("\n=== CHATBOT CONVERSATION DEMO ===")
    
    client = DieAI()
    
    # Multi-turn conversation
    messages = [
        {"role": "user", "content": "Hello! I need help with math."}
    ]
    
    print("User: Hello! I need help with math.")
    
    response = client.chat.completions.create(
        model="dieai-1.0",
        messages=messages
    )
    
    assistant_response = response.choices[0].message.content
    print(f"DieAI: {assistant_response}")
    
    # Add to conversation history
    messages.append({"role": "assistant", "content": assistant_response})
    messages.append({"role": "user", "content": "What's the quadratic formula?"})
    
    print("\nUser: What's the quadratic formula?")
    
    response = client.chat.completions.create(
        model="dieai-1.0",
        messages=messages
    )
    
    assistant_response = response.choices[0].message.content
    print(f"DieAI: {assistant_response}")
    
    # Continue conversation
    messages.append({"role": "assistant", "content": assistant_response})
    messages.append({"role": "user", "content": "Solve x² - 5x + 6 = 0"})
    
    print("\nUser: Solve x² - 5x + 6 = 0")
    
    response = client.chat.completions.create(
        model="dieai-1.0",
        messages=messages
    )
    
    assistant_response = response.choices[0].message.content
    print(f"DieAI: {assistant_response}")

def demo_streaming():
    """Demonstrate streaming responses (similar to OpenAI streaming)"""
    print("\n=== STREAMING DEMO ===")
    
    client = DieAI()
    
    print("User: Explain photosynthesis")
    print("DieAI: ", end="", flush=True)
    
    # Note: Streaming implementation is basic for demo purposes
    response = client.chat.completions.create(
        model="dieai-1.0",
        messages=[
            {"role": "user", "content": "Explain photosynthesis"}
        ],
        stream=True
    )
    
    # Simulate streaming output
    for chunk in response:
        if chunk['choices'][0]['delta'].get('content'):
            print(chunk['choices'][0]['delta']['content'], end="", flush=True)
    
    print()  # New line after streaming

def demo_usage_stats():
    """Demonstrate usage statistics like OpenAI's API"""
    print("\n=== USAGE STATISTICS DEMO ===")
    
    client = DieAI()
    
    response = client.chat.completions.create(
        model="dieai-1.0",
        messages=[
            {"role": "user", "content": "Calculate the volume of a sphere with radius 3"}
        ]
    )
    
    print(f"User: Calculate the volume of a sphere with radius 3")
    print(f"DieAI: {response.choices[0].message.content}")
    
    # Show usage statistics
    print(f"\nUsage Statistics:")
    print(f"  Prompt tokens: {response.usage['prompt_tokens']}")
    print(f"  Completion tokens: {response.usage['completion_tokens']}")
    print(f"  Total tokens: {response.usage['total_tokens']}")

def demo_error_handling():
    """Demonstrate error handling"""
    print("\n=== ERROR HANDLING DEMO ===")
    
    client = DieAI()
    
    # Test with unclear input
    print("Testing with unclear input:")
    response = client.chat.completions.create(
        model="dieai-1.0",
        messages=[
            {"role": "user", "content": "asdfghjkl"}
        ]
    )
    
    print(f"User: asdfghjkl")
    print(f"DieAI: {response.choices[0].message.content}")

def interactive_chatbot():
    """Interactive chatbot demo"""
    print("\n=== INTERACTIVE CHATBOT ===")
    print("Type 'quit' or 'exit' to stop the conversation")
    print("Try asking math, science, or conversion questions!")
    
    client = DieAI()
    messages = []
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("DieAI: Goodbye! Thanks for using DieAI!")
            break
        
        if not user_input:
            continue
        
        messages.append({"role": "user", "content": user_input})
        
        try:
            response = client.chat.completions.create(
                model="dieai-1.0",
                messages=messages
            )
            
            assistant_response = response.choices[0].message.content
            print(f"DieAI: {assistant_response}")
            
            messages.append({"role": "assistant", "content": assistant_response})
            
            # Keep conversation history manageable
            if len(messages) > 10:
                messages = messages[-8:]  # Keep last 8 messages
                
        except Exception as e:
            print(f"DieAI: I encountered an error: {e}")

def main():
    """Run all demos"""
    print("DieAI - OpenAI-like API Demo")
    print("=" * 40)
    
    try:
        demo_openai_style_api()
        demo_chatbot_conversation()
        demo_streaming()
        demo_usage_stats()
        demo_error_handling()
        
        print("\n" + "=" * 40)
        print("All demos completed successfully!")
        print("\nTo build your own chatbot:")
        print("1. Install: pip install dieai")
        print("2. Import: from dieai import DieAI")
        print("3. Use the OpenAI-style API as shown above")
        
        # Ask if user wants interactive demo
        try:
            choice = input("\nWould you like to try the interactive chatbot? (y/n): ").lower()
            if choice in ['y', 'yes']:
                interactive_chatbot()
        except KeyboardInterrupt:
            print("\nDemo ended by user.")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        print("Make sure the dieai package is properly installed.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Simple Chatbot Example using DieAI
Shows how to create a basic chatbot with math and science capabilities
"""

from dieai import ChatBot

def create_simple_chatbot():
    """Create a simple educational chatbot"""
    
    # Create a friendly educational chatbot
    bot = ChatBot(
        name="MathBot",
        personality="educational",
        knowledge_domains=["math", "science", "general"]
    )
    
    # Add some custom responses
    bot.add_custom_response("hello", "Hello! I'm MathBot, your friendly math and science assistant. What would you like to learn today?")
    bot.add_custom_response("bye", "Goodbye! Keep learning and exploring math and science!")
    
    return bot

def demo_chatbot_conversation():
    """Demonstrate chatbot conversation"""
    print("=== SIMPLE CHATBOT DEMO ===")
    
    bot = create_simple_chatbot()
    
    # Test conversations
    test_inputs = [
        "Hello!",
        "What is 25 + 17?",
        "Calculate the area of a circle with radius 4",
        "What is the speed of light?",
        "Convert 100 celsius to fahrenheit",
        "Solve 2x + 5 = 15",
        "What is photosynthesis?",
        "Bye!"
    ]
    
    print(f"Chatbot: {bot.name} is ready!\n")
    
    for user_input in test_inputs:
        print(f"User: {user_input}")
        response = bot.chat(user_input)
        print(f"Bot: {response}\n")
    
    # Show conversation summary
    summary = bot.get_conversation_summary()
    print("Conversation Summary:")
    print(f"  Total messages: {summary['total_messages']}")
    print(f"  User messages: {summary['user_messages']}")
    print(f"  Bot messages: {summary['bot_messages']}")

def interactive_chatbot():
    """Interactive chatbot session"""
    print("\n=== INTERACTIVE CHATBOT ===")
    print("Type 'quit' to exit")
    
    bot = create_simple_chatbot()
    
    print(f"\n{bot.name}: Hello! I'm your math and science assistant. What would you like to learn?")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            response = bot.chat(user_input)
            print(f"{bot.name}: {response}")
            break
        
        if not user_input:
            continue
        
        response = bot.chat(user_input)
        print(f"{bot.name}: {response}")

if __name__ == "__main__":
    print("DieAI Simple Chatbot Example")
    print("=" * 40)
    
    demo_chatbot_conversation()
    
    # Ask if user wants interactive demo
    try:
        choice = input("\nWould you like to try the interactive chatbot? (y/n): ").lower()
        if choice in ['y', 'yes']:
            interactive_chatbot()
    except KeyboardInterrupt:
        print("\nDemo ended.")
    
    print("\nTo use this in your projects:")
    print("1. pip install dieai")
    print("2. from dieai import ChatBot")
    print("3. Create your own chatbot with custom personality and domains!")
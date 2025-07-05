#!/usr/bin/env python3
"""
AI Robot Example using DieAI
Shows how to create an intelligent robot that can process voice commands,
make decisions, and interact with sensors
"""

import time
import random
from dieai import AIRobot

def simulate_sensor_data():
    """Simulate various sensor readings"""
    return {
        "temperature": round(random.uniform(18, 25), 1),
        "distance": random.randint(10, 200),
        "light": random.randint(100, 1000),
        "sound": random.randint(30, 80),
        "motion": random.choice([True, False])
    }

def movement_handler(command_data):
    """Handle movement commands"""
    print(f"🤖 Robot: Executing movement - {command_data}")
    return {"status": "moving", "action": "movement_executed"}

def speech_handler(text):
    """Handle text-to-speech"""
    print(f"🤖 Robot says: {text}")
    return {"status": "speaking", "text": text}

def create_educational_robot():
    """Create an educational robot with DieAI intelligence"""
    
    # Create robot with educational capabilities
    robot = AIRobot(
        robot_name="EduBot",
        capabilities=[
            "speech", "movement", "calculation", 
            "problem_solving", "teaching", "sensors"
        ]
    )
    
    # Register command handlers
    robot.register_command_handler("movement", movement_handler)
    
    # Register sensor processors
    def temperature_processor(temp_data):
        if temp_data > 23:
            return {"alert": "Room is warm", "suggested_action": "turn_on_fan"}
        elif temp_data < 20:
            return {"alert": "Room is cool", "suggested_action": "turn_on_heater"}
        return {"status": "comfortable", "temperature": temp_data}
    
    robot.register_sensor_processor("temperature", temperature_processor)
    
    return robot

def demo_voice_commands():
    """Demonstrate processing voice commands"""
    print("=== AI ROBOT VOICE COMMANDS DEMO ===")
    
    robot = create_educational_robot()
    
    # Test various voice commands
    voice_commands = [
        "Hello robot, what's your name?",
        "Calculate 25 multiplied by 8",
        "What is the formula for the area of a circle?",
        "Move forward 2 meters",
        "What is the speed of light?",
        "Convert 100 fahrenheit to celsius",
        "Explain photosynthesis",
        "Turn left and stop"
    ]
    
    print(f"Robot: {robot.robot_name} is online and ready!\n")
    
    for command in voice_commands:
        print(f"👤 Human: '{command}'")
        
        # Process the voice command
        response = robot.process_voice_command(command)
        
        # Handle the response
        speech_handler(response["speech_response"])
        
        if response["suggested_action"]:
            print(f"🔧 Action: {response['suggested_action']}")
        
        print(f"📊 Command type: {response['command_type']} (confidence: {response['confidence']:.1f})")
        print()
        
        # Small delay for realistic interaction
        time.sleep(0.5)

def demo_sensor_processing():
    """Demonstrate sensor data processing and decision making"""
    print("\n=== SENSOR PROCESSING DEMO ===")
    
    robot = create_educational_robot()
    
    # Simulate sensor readings over time
    for i in range(5):
        print(f"--- Sensor Reading {i+1} ---")
        
        # Get simulated sensor data
        sensors = simulate_sensor_data()
        
        # Process each sensor
        for sensor_type, data in sensors.items():
            result = robot.process_sensor_data(sensor_type, data)
            print(f"📡 {sensor_type.title()}: {data} -> {result.get('analysis', 'Processed')}")
            
            # Handle special alerts
            if "alert" in result:
                print(f"⚠️  Alert: {result['alert']}")
                if "suggested_action" in result:
                    print(f"💡 Suggestion: {result['suggested_action']}")
        
        print()
        time.sleep(1)

def demo_decision_making():
    """Demonstrate intelligent decision making"""
    print("\n=== DECISION MAKING DEMO ===")
    
    robot = create_educational_robot()
    
    # Test various decision scenarios
    scenarios = [
        {
            "situation": "Student is struggling with algebra homework",
            "options": ["provide step-by-step solution", "give hints", "explain concepts", "find similar examples"]
        },
        {
            "situation": "Detected obstacle 30cm ahead while moving",
            "options": ["stop immediately", "turn left", "turn right", "back up"]
        },
        {
            "situation": "Room temperature is 26°C and student looks uncomfortable",
            "options": ["suggest opening window", "turn on fan", "offer water", "continue lesson"]
        },
        {
            "situation": "Student asks advanced question beyond current curriculum",
            "options": ["simplify explanation", "provide basic overview", "suggest further reading", "defer to teacher"]
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"--- Decision Scenario {i} ---")
        print(f"🎯 Situation: {scenario['situation']}")
        print(f"🔀 Options: {', '.join(scenario['options'])}")
        
        decision = robot.make_decision(scenario["situation"], scenario["options"])
        
        print(f"🤖 Robot Decision: {decision['decision']}")
        print(f"📊 Confidence: {decision['confidence']:.1f}")
        print()

def demo_learning_assistance():
    """Demonstrate educational assistance capabilities"""
    print("\n=== LEARNING ASSISTANCE DEMO ===")
    
    robot = create_educational_robot()
    
    # Educational interaction scenarios
    learning_scenarios = [
        "Help me understand quadratic equations",
        "I'm confused about photosynthesis",
        "What's the difference between speed and velocity?",
        "Can you explain how to convert fractions to decimals?",
        "I need help with my chemistry homework about periodic table",
        "Show me how to calculate the volume of a sphere"
    ]
    
    for scenario in learning_scenarios:
        print(f"👨‍🎓 Student: {scenario}")
        
        response = robot.process_voice_command(scenario)
        
        # Educational robot provides structured learning support
        speech_handler(response["speech_response"])
        
        # Suggest follow-up activities
        follow_up = robot.make_decision(
            f"Student asked: {scenario}. How can I help them learn better?",
            ["provide practice problems", "suggest related topics", "check understanding", "offer visual aids"]
        )
        
        print(f"💡 Teaching strategy: {follow_up['decision']}")
        print()

def interactive_robot():
    """Interactive robot session"""
    print("\n=== INTERACTIVE AI ROBOT ===")
    print("Type 'quit' to exit, 'status' to see robot status")
    
    robot = create_educational_robot()
    
    print(f"\n🤖 {robot.robot_name}: Hello! I'm your intelligent educational robot.")
    print("I can help with math, science, movement, and learning!")
    
    while True:
        user_input = input("\n👤 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            speech_handler("Goodbye! Keep learning and exploring!")
            break
        
        if user_input.lower() == 'status':
            status = robot.get_robot_status()
            print(f"🤖 Robot Status:")
            print(f"  Name: {status['name']}")
            print(f"  Capabilities: {', '.join(status['capabilities'])}")
            print(f"  Memory items: {status['memory_items']}")
            print(f"  Active sensors: {', '.join(status['active_sensors']) if status['active_sensors'] else 'None'}")
            continue
        
        if not user_input:
            continue
        
        # Process command
        response = robot.process_voice_command(user_input)
        speech_handler(response["speech_response"])
        
        # Show action if any
        if response["suggested_action"]:
            print(f"🔧 Action: {response['suggested_action']}")

def demo_custom_robot():
    """Demonstrate creating a custom robot for specific tasks"""
    print("\n=== CUSTOM ROBOT DEMO ===")
    
    # Create a specialized math tutor robot
    math_robot = AIRobot(
        robot_name="AlgebraBot",
        capabilities=["calculation", "tutoring", "step_by_step_solving", "graphing"]
    )
    
    print(f"🤖 {math_robot.robot_name}: I'm specialized in mathematics!")
    
    math_problems = [
        "Solve for x: 3x + 7 = 22",
        "What's the derivative of x squared?",
        "Find the area under the curve y = x^2 from 0 to 2",
        "Explain the quadratic formula"
    ]
    
    for problem in math_problems:
        print(f"\n📚 Problem: {problem}")
        
        response = math_robot.process_voice_command(problem)
        speech_handler(response["speech_response"])
        
        # Make teaching decision
        teaching_decision = math_robot.make_decision(
            f"Student needs help with: {problem}",
            ["show step-by-step solution", "provide visual diagram", "give practice problems", "explain theory"]
        )
        
        print(f"📖 Teaching approach: {teaching_decision['decision']}")

if __name__ == "__main__":
    print("DieAI AI Robot Example")
    print("=" * 40)
    
    try:
        demo_voice_commands()
        demo_sensor_processing()
        demo_decision_making()
        demo_learning_assistance()
        demo_custom_robot()
        
        print("\n" + "=" * 40)
        print("All robot demos completed!")
        
        # Ask if user wants interactive demo
        choice = input("\nWould you like to try the interactive robot? (y/n): ").lower()
        if choice in ['y', 'yes']:
            interactive_robot()
        
    except KeyboardInterrupt:
        print("\nDemo ended.")
    
    print("\nTo create your own AI robot:")
    print("1. pip install dieai")
    print("2. from dieai import AIRobot")
    print("3. Define capabilities and command handlers")
    print("4. Build intelligent autonomous systems!")
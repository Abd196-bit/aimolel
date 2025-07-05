#!/usr/bin/env python3
"""
Advanced Applications using DieAI
Shows how to build sophisticated AI applications with DieAI
"""

import time
from dieai import DieAI, ChatBot, AIRobot, ConversationAnalyzer

def create_study_buddy_chatbot():
    """Create an intelligent study buddy chatbot"""
    
    # Create a patient, educational chatbot
    study_buddy = ChatBot(
        name="StudyBuddy",
        personality="patient",
        knowledge_domains=["math", "science", "general"]
    )
    
    # Add custom learning responses
    study_buddy.add_custom_response(
        "i don't understand", 
        "That's okay! Learning takes time. Let me break this down into smaller steps for you."
    )
    
    study_buddy.add_custom_response(
        "this is hard",
        "I understand it seems challenging. Let's approach this differently and take it step by step."
    )
    
    # Add a learning progress plugin
    def learning_progress_plugin(user_input, context):
        if "progress" in user_input.lower():
            return f"You're doing great! You've asked {context.get('questions_asked', 0)} questions today. Keep up the curiosity!"
        return None
    
    study_buddy.add_plugin(learning_progress_plugin)
    
    return study_buddy

def create_smart_home_robot():
    """Create a smart home management robot"""
    
    # Create a home automation robot
    home_robot = AIRobot(
        robot_name="HomeAI",
        capabilities=[
            "environmental_control", "security", "energy_management", 
            "calculation", "weather_analysis", "scheduling"
        ]
    )
    
    # Register home automation handlers
    def climate_handler(command_data):
        print(f"🏠 Climate System: {command_data}")
        return {"status": "climate_adjusted", "action": command_data}
    
    def security_handler(command_data):
        print(f"🔒 Security System: {command_data}")
        return {"status": "security_updated", "action": command_data}
    
    home_robot.register_command_handler("climate", climate_handler)
    home_robot.register_command_handler("security", security_handler)
    
    # Environmental sensor processor
    def environmental_processor(env_data):
        recommendations = []
        
        if env_data.get("temperature", 0) > 25:
            recommendations.append("Consider lowering air conditioning")
        if env_data.get("humidity", 0) > 70:
            recommendations.append("Run dehumidifier")
        if env_data.get("light_level", 0) < 100:
            recommendations.append("Turn on additional lighting")
            
        return {
            "status": "analyzed",
            "recommendations": recommendations,
            "data": env_data
        }
    
    home_robot.register_sensor_processor("environmental", environmental_processor)
    
    return home_robot

def demo_educational_tutoring_system():
    """Demonstrate an AI tutoring system"""
    print("=== AI TUTORING SYSTEM DEMO ===")
    
    # Create specialized tutoring bots
    math_tutor = ChatBot("MathGenius", "educational", ["math"])
    science_tutor = ChatBot("ScienceExplorer", "creative", ["science"])
    
    # Simulated tutoring session
    tutoring_scenarios = [
        {
            "student_question": "I'm struggling with quadratic equations",
            "tutor": math_tutor,
            "subject": "Mathematics"
        },
        {
            "student_question": "Can you explain how photosynthesis works?",
            "tutor": science_tutor,
            "subject": "Biology"
        },
        {
            "student_question": "What's the derivative of x^3?",
            "tutor": math_tutor,
            "subject": "Calculus"
        }
    ]
    
    for scenario in tutoring_scenarios:
        print(f"\n📚 {scenario['subject']} Tutoring Session")
        print(f"👨‍🎓 Student: {scenario['student_question']}")
        
        response = scenario['tutor'].chat(scenario['student_question'])
        print(f"🧑‍🏫 {scenario['tutor'].name}: {response}")
        
        # Follow-up assessment
        follow_up = scenario['tutor'].chat("Can you give me a practice problem?")
        print(f"📝 Practice: {follow_up}")

def demo_smart_assistant_ecosystem():
    """Demonstrate a complete smart assistant ecosystem"""
    print("\n=== SMART ASSISTANT ECOSYSTEM DEMO ===")
    
    # Create ecosystem components
    personal_assistant = ChatBot("Alex", "helpful", ["math", "science", "general"])
    home_robot = create_smart_home_robot()
    study_buddy = create_study_buddy_chatbot()
    
    # Conversation analyzer for insights
    analyzer = ConversationAnalyzer()
    
    # Simulate daily interactions
    daily_interactions = [
        {
            "time": "Morning",
            "assistant": personal_assistant,
            "query": "What's the weather like and should I adjust the thermostat?"
        },
        {
            "time": "Afternoon", 
            "assistant": study_buddy,
            "query": "Help me understand Newton's second law of motion"
        },
        {
            "time": "Evening",
            "assistant": home_robot,
            "query": "Optimize energy usage for tonight"
        }
    ]
    
    conversation_history = []
    
    for interaction in daily_interactions:
        print(f"\n🕐 {interaction['time']} Interaction")
        print(f"👤 User: {interaction['query']}")
        
        if isinstance(interaction['assistant'], ChatBot):
            response = interaction['assistant'].chat(interaction['query'])
            print(f"🤖 {interaction['assistant'].name}: {response}")
            
            # Add to conversation history
            conversation_history.extend([
                {"role": "user", "content": interaction['query']},
                {"role": "assistant", "content": response}
            ])
            
        elif isinstance(interaction['assistant'], AIRobot):
            response = interaction['assistant'].process_voice_command(interaction['query'])
            print(f"🤖 {interaction['assistant'].robot_name}: {response['speech_response']}")
            
            if response['suggested_action']:
                print(f"🔧 Action: {response['suggested_action']}")
    
    # Analyze the day's conversations
    if conversation_history:
        print(f"\n📊 Daily Conversation Analysis")
        analysis = analyzer.analyze_conversation(conversation_history)
        print(f"Insights: {analysis.get('insights', 'Analysis in progress...')}")

def demo_industrial_robot_control():
    """Demonstrate industrial robot control system"""
    print("\n=== INDUSTRIAL ROBOT CONTROL DEMO ===")
    
    # Create industrial robot with specific capabilities
    industrial_robot = AIRobot(
        robot_name="IndustrialBot-X1",
        capabilities=[
            "precision_movement", "quality_control", "safety_monitoring",
            "calculation", "process_optimization", "predictive_maintenance"
        ]
    )
    
    # Industrial scenarios
    industrial_tasks = [
        "Calculate optimal cutting parameters for steel plate thickness 5mm",
        "Analyze vibration sensor data showing 2.5mm displacement",
        "Determine if temperature reading of 185°C is within safe operating range",
        "Optimize production cycle time for 1000 units per hour target",
        "Process quality control data showing 0.02mm tolerance deviation"
    ]
    
    for task in industrial_tasks:
        print(f"\n🏭 Industrial Task: {task}")
        
        response = industrial_robot.process_voice_command(task)
        print(f"🤖 {industrial_robot.robot_name}: {response['speech_response']}")
        
        # Make operational decision
        decision = industrial_robot.make_decision(
            f"Task: {task}",
            ["continue operation", "adjust parameters", "alert supervisor", "initiate maintenance"]
        )
        
        print(f"⚙️ Decision: {decision['decision']}")

def demo_educational_robot_lab():
    """Demonstrate educational robot for laboratory work"""
    print("\n=== EDUCATIONAL LAB ROBOT DEMO ===")
    
    # Create lab assistant robot
    lab_robot = AIRobot(
        robot_name="LabAssistant",
        capabilities=[
            "experiment_guidance", "safety_monitoring", "calculation",
            "data_analysis", "procedure_explanation", "equipment_operation"
        ]
    )
    
    # Laboratory experiments
    lab_experiments = [
        {
            "experiment": "Measuring acceleration due to gravity",
            "data": "Time measurements: 0.45s, 0.47s, 0.46s, 0.48s, 0.45s",
            "question": "Calculate the average time and determine gravity"
        },
        {
            "experiment": "Chemical titration",
            "data": "Initial volume: 0.00mL, Final volume: 23.75mL, Concentration: 0.1M",
            "question": "Calculate the molarity of the unknown solution"
        },
        {
            "experiment": "Physics pendulum",
            "data": "Length: 1.0m, Period measurements: 2.01s, 2.00s, 1.99s",
            "question": "Compare experimental gravity with theoretical value"
        }
    ]
    
    for exp in lab_experiments:
        print(f"\n🧪 Experiment: {exp['experiment']}")
        print(f"📊 Data: {exp['data']}")
        print(f"❓ Question: {exp['question']}")
        
        # Get guidance from lab robot
        guidance_query = f"Help with {exp['experiment']}. Data: {exp['data']}. Question: {exp['question']}"
        response = lab_robot.process_voice_command(guidance_query)
        
        print(f"🤖 {lab_robot.robot_name}: {response['speech_response']}")
        
        # Safety and procedure check
        safety_decision = lab_robot.make_decision(
            f"Conducting {exp['experiment']} with given data",
            ["proceed with caution", "review procedure", "check safety protocols", "verify calculations"]
        )
        
        print(f"🔬 Lab Protocol: {safety_decision['decision']}")

def demo_custom_ai_applications():
    """Show how to build custom AI applications"""
    print("\n=== CUSTOM AI APPLICATIONS DEMO ===")
    
    # Example 1: Fitness Coach Bot
    fitness_coach = ChatBot("FitCoach", "encouraging", ["math", "science"])
    fitness_coach.add_custom_response("tired", "Rest is important for muscle recovery! Let's calculate your optimal rest period.")
    
    print("🏃‍♂️ Fitness Coach Application:")
    fitness_query = "I ran 5km in 25 minutes. What's my pace and how many calories did I burn?"
    print(f"User: {fitness_query}")
    response = fitness_coach.chat(fitness_query)
    print(f"FitCoach: {response}")
    
    # Example 2: Financial Advisor Bot
    finance_bot = ChatBot("MoneyWise", "professional", ["math"])
    finance_bot.add_custom_response("investment", "Let's calculate compound interest and analyze your investment potential.")
    
    print("\n💰 Financial Advisor Application:")
    finance_query = "If I invest $1000 at 7% annual interest compounded monthly, how much will I have in 10 years?"
    print(f"User: {finance_query}")
    response = finance_bot.chat(finance_query)
    print(f"MoneyWise: {response}")
    
    # Example 3: Engineering Assistant Robot
    engineering_robot = AIRobot("EngineerBot", ["structural_analysis", "calculation", "design_optimization"])
    
    print("\n🔧 Engineering Assistant Application:")
    engineering_query = "Calculate the moment of inertia for a rectangular beam 200mm x 300mm"
    print(f"Engineer: {engineering_query}")
    response = engineering_robot.process_voice_command(engineering_query)
    print(f"EngineerBot: {response['speech_response']}")

if __name__ == "__main__":
    print("DieAI Advanced Applications Demo")
    print("=" * 50)
    
    try:
        demo_educational_tutoring_system()
        demo_smart_assistant_ecosystem()
        demo_industrial_robot_control()
        demo_educational_robot_lab()
        demo_custom_ai_applications()
        
        print("\n" + "=" * 50)
        print("Advanced applications demo completed!")
        print("\nThese examples show how DieAI can be used to build:")
        print("• Educational tutoring systems")
        print("• Smart home automation")
        print("• Industrial robot control")
        print("• Laboratory assistants")
        print("• Custom AI applications")
        print("\nStart building your own intelligent applications with DieAI!")
        
    except KeyboardInterrupt:
        print("\nDemo ended.")
    
    print("\nNext steps:")
    print("1. pip install dieai")
    print("2. Choose your application type (chatbot/robot)")
    print("3. Customize personality and capabilities")
    print("4. Add domain-specific knowledge and handlers")
    print("5. Deploy your intelligent AI system!")
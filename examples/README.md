# DieAI Examples

This directory contains comprehensive examples showing how to build chatbots and AI robots using DieAI.

## Quick Start Examples

### 🤖 Simple Chatbot (`simple_chatbot.py`)
Basic educational chatbot with custom responses and conversation management.

```bash
python simple_chatbot.py
```

**What it demonstrates:**
- Creating chatbots with different personalities
- Adding custom responses and conversation flow
- Multi-turn conversations with context
- Educational math and science assistance

**Key features:**
- Personality customization (educational, friendly, professional)
- Knowledge domain specification (math, science, general)
- Custom response triggers
- Conversation history and analysis

### 🦾 AI Robot (`ai_robot.py`) 
Intelligent robot with voice commands, sensor processing, and decision making.

```bash
python ai_robot.py
```

**What it demonstrates:**
- Voice command processing and interpretation
- Sensor data analysis and intelligent responses
- Autonomous decision making with reasoning
- Educational assistance and tutoring capabilities

**Key features:**
- Command classification (movement, calculation, information)
- Sensor data processing with custom handlers
- Intelligent decision making for various scenarios
- Memory and learning from interactions

### 🚀 Advanced Applications (`advanced_applications.py`)
Complex AI systems for various industries and use cases.

```bash
python advanced_applications.py
```

**What it demonstrates:**
- Smart home automation systems
- Industrial robot control
- Educational laboratory assistants
- Custom AI applications for specific domains

## Real-World Applications

### Educational Systems
```python
# Math tutoring bot
math_tutor = ChatBot("MathGenius", "educational", ["math"])
response = math_tutor.chat("Explain the quadratic formula")

# Science lab assistant
lab_robot = AIRobot("LabBot", ["experiment_guidance", "safety_monitoring"])
guidance = lab_robot.process_voice_command("Help with titration experiment")
```

### Smart Home Automation
```python
# Home management robot
home_robot = AIRobot("HomeAI", ["environmental_control", "security", "energy_management"])

# Process environmental data
temp_analysis = home_robot.process_sensor_data("temperature", 26.5)

# Make energy decisions
energy_decision = home_robot.make_decision(
    "High energy usage detected", 
    ["reduce heating", "optimize lighting", "defer non-essential devices"]
)
```

### Industrial Automation
```python
# Industrial robot controller
industrial_bot = AIRobot("IndustrialBot", ["precision_movement", "quality_control"])

# Process quality control data
qc_result = industrial_bot.process_voice_command("Analyze part tolerance 0.02mm deviation")

# Safety decision making
safety_decision = industrial_bot.make_decision(
    "Temperature exceeds 85°C threshold",
    ["emergency stop", "reduce speed", "activate cooling", "alert supervisor"]
)
```

## Building Custom Applications

### 1. Choose Your Base Class

**For Conversational AI:**
```python
from dieai import ChatBot

bot = ChatBot(
    name="YourBot",
    personality="helpful|educational|friendly|professional|creative|patient",
    knowledge_domains=["math", "science", "general"]
)
```

**For Autonomous Systems:**
```python
from dieai import AIRobot

robot = AIRobot(
    robot_name="YourRobot",
    capabilities=["movement", "sensors", "calculation", "decision_making"]
)
```

### 2. Add Custom Functionality

**Custom Responses:**
```python
bot.add_custom_response("help", "I'm here to assist with math and science!")
```

**Plugin System:**
```python
def custom_plugin(user_input, context):
    if "special_command" in user_input:
        return "Custom functionality activated"
    return None

bot.add_plugin(custom_plugin)
```

**Command Handlers:**
```python
def movement_handler(command_data):
    print(f"Executing: {command_data}")
    return {"status": "completed"}

robot.register_command_handler("movement", movement_handler)
```

### 3. Implement Domain Logic

**Sensor Processing:**
```python
def temperature_processor(temp_data):
    if temp_data > 30:
        return {"alert": "High temperature", "action": "activate_cooling"}
    return {"status": "normal"}

robot.register_sensor_processor("temperature", temperature_processor)
```

## Integration Examples

### Web Application Integration
```python
from flask import Flask, request, jsonify
from dieai import ChatBot

app = Flask(__name__)
bot = ChatBot("WebBot", "helpful", ["math", "science"])

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    user_message = request.json['message']
    response = bot.chat(user_message)
    return jsonify({"response": response})
```

### IoT Device Integration
```python
import paho.mqtt.client as mqtt
from dieai import AIRobot

robot = AIRobot("IoTBot", ["sensor_processing", "automation"])

def on_message(client, userdata, message):
    sensor_data = json.loads(message.payload)
    result = robot.process_sensor_data(message.topic, sensor_data)
    # Act on result
    
client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883, 60)
```

### Voice Assistant Integration
```python
import speech_recognition as sr
import pyttsx3
from dieai import AIRobot

robot = AIRobot("VoiceBot", ["speech", "conversation"])
recognizer = sr.Recognizer()
tts = pyttsx3.init()

def voice_loop():
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        text = recognizer.recognize_google(audio)
        
        response = robot.process_voice_command(text)
        tts.say(response["speech_response"])
        tts.runAndWait()
```

## Performance Tips

1. **Memory Management**: Use conversation history limits for long-running bots
2. **Response Caching**: Cache common responses for frequently asked questions
3. **Batch Processing**: Process multiple sensor readings together when possible
4. **Context Optimization**: Keep conversation context relevant and focused

## Advanced Features

### Conversation Analysis
```python
from dieai import ConversationAnalyzer

analyzer = ConversationAnalyzer()
insights = analyzer.analyze_conversation(bot.conversation_history)
print(insights["insights"])
```

### Multi-Bot Orchestration
```python
# Create specialized bots
math_bot = ChatBot("MathExpert", "educational", ["math"])
science_bot = ChatBot("ScienceGuru", "creative", ["science"])

def route_question(question):
    if any(word in question.lower() for word in ["equation", "formula", "calculate"]):
        return math_bot.chat(question)
    elif any(word in question.lower() for word in ["physics", "chemistry", "biology"]):
        return science_bot.chat(question)
    else:
        return "Please specify if this is a math or science question."
```

## Getting Started

1. **Install DieAI:**
   ```bash
   pip install dieai
   ```

2. **Run an example:**
   ```bash
   python examples/simple_chatbot.py
   ```

3. **Customize for your needs:**
   - Modify personality and knowledge domains
   - Add custom responses and plugins
   - Implement domain-specific handlers

4. **Deploy your application:**
   - Integrate with web frameworks
   - Connect to databases and APIs
   - Add monitoring and analytics

## Support

For questions about these examples or building your own applications:
- Review the main README.md for API documentation
- Check the source code for implementation details
- Visit the GitHub repository for issues and discussions

Start building intelligent AI applications with DieAI today!
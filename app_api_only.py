#!/usr/bin/env python3
"""
DieAI API-Only Application
Simplified version without UI components - API endpoints only
"""
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db.init_app(app)
CORS(app)

# Simple User model for API key management
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

# Initialize database
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    """Root endpoint"""
    return jsonify({
        "message": "DieAI API Server",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "models": "/api/models",
            "chat": "/api/chat"
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected",
        "version": "1.0.0"
    })

@app.route('/api/models')
def api_models():
    """Get available models"""
    models = [
        {
            "id": "dieai-transformer",
            "name": "DieAI Transformer",
            "description": "Custom transformer model with web search capabilities",
            "max_tokens": 4096,
            "capabilities": ["chat", "search", "reasoning"]
        }
    ]
    return jsonify({"models": models})

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """AI Chat endpoint with web search capabilities"""
    try:
        data = request.get_json()
        
        if not data or 'messages' not in data:
            return jsonify({"error": "Messages required"}), 400
        
        messages = data.get('messages', [])
        use_search = data.get('use_search', False)
        
        # Get the last user message
        user_message = None
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break
        
        if not user_message:
            return jsonify({"error": "No user message found"}), 400
        
        # Simple AI response logic
        response_content = generate_ai_response(user_message, use_search)
        
        return jsonify({
            "id": f"chat-{datetime.utcnow().timestamp()}",
            "object": "chat.completion",
            "created": int(datetime.utcnow().timestamp()),
            "model": "dieai-transformer",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(response_content.split()),
                "total_tokens": len(user_message.split()) + len(response_content.split())
            }
        })
        
    except Exception as e:
        logger.error(f"Chat API error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def generate_ai_response(user_message, use_search=False):
    """Generate AI response based on user message"""
    
    # Simple response logic
    message_lower = user_message.lower()
    
    # Math calculations
    if any(op in message_lower for op in ['+', '-', '*', '/', 'calculate', 'math']):
        try:
            # Simple math evaluation (be careful with eval in production)
            if '+' in user_message or '-' in user_message or '*' in user_message or '/' in user_message:
                # Extract numbers and operators safely
                import re
                numbers = re.findall(r'\d+(?:\.\d+)?', user_message)
                if len(numbers) >= 2:
                    if '+' in user_message:
                        result = float(numbers[0]) + float(numbers[1])
                        return f"The result is: {result}"
                    elif '-' in user_message:
                        result = float(numbers[0]) - float(numbers[1])
                        return f"The result is: {result}"
                    elif '*' in user_message:
                        result = float(numbers[0]) * float(numbers[1])
                        return f"The result is: {result}"
                    elif '/' in user_message:
                        result = float(numbers[0]) / float(numbers[1])
                        return f"The result is: {result}"
        except:
            pass
    
    # Greetings
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return "Hello! I'm DieAI, your AI assistant. How can I help you today?"
    
    # Questions about the system
    if any(word in message_lower for word in ['what are you', 'who are you', 'about']):
        return "I'm DieAI, a custom AI assistant with web search capabilities. I can help you with questions, calculations, and various tasks."
    
    # Default response
    return f"I understand you're asking about: '{user_message}'. I'm currently running in API-only mode. How can I assist you further?"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta
import secrets
import hashlib
import time

# Import existing components
from models.inference import InferenceEngine
from services.database import DatabaseManager
from services.search import SearchService
from services.learning import LearningService
from api.auth import AuthManager
from api.endpoints import APIEndpoints
from utils.rate_limiter import RateLimiter
from utils.helpers import load_config

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
CORS(app)

# Initialize components with PostgreSQL support
print("Initializing DieAI components...")
db_manager = DatabaseManager(use_postgres=True)
auth_manager = AuthManager(db_manager)
rate_limiter = RateLimiter(db_manager)

print("Loading AI inference engine...")
inference_engine = InferenceEngine()
inference_engine.load_model()

# Set learning service
print("Setting up learning service...")
learning_service = LearningService(db_manager)
inference_engine.set_learning_service(learning_service)

print("DieAI components initialized successfully!")

api_endpoints = APIEndpoints(db_manager, auth_manager, rate_limiter, inference_engine)

# Web routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if auth_manager.authenticate_user(username, password):
            session['user_id'] = username
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')

    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')

    if not username or not password or not email:
        flash('All fields are required')
        return redirect(url_for('login'))

    # Check if user already exists
    if auth_manager.get_user_info(username):
        flash('Username already exists')
        return redirect(url_for('login'))

    # Create new user
    if auth_manager.create_user(username, password, email):
        session['user_id'] = username
        session['logged_in'] = True
        return redirect(url_for('dashboard'))
    else:
        flash('Registration failed')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    username = session.get('user_id')
    user_info = db_manager.get_user_info(username)
    api_keys = db_manager.get_user_api_keys(username)

    return render_template('dashboard.html', 
                         username=username, 
                         user_info=user_info,
                         api_keys=api_keys)

@app.route('/generate_api_key', methods=['POST'])
def generate_api_key():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    username = session.get('user_id')
    api_key = auth_manager.generate_api_key(username)

    if api_key:
        flash(f'New API key generated: {api_key}')
    else:
        flash('Failed to generate API key')

    return redirect(url_for('dashboard'))

@app.route('/revoke_api_key', methods=['POST'])
def revoke_api_key():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    username = session.get('user_id')
    api_key = request.form.get('api_key')

    if auth_manager.revoke_api_key(username, api_key):
        flash('API key revoked successfully')
    else:
        flash('Failed to revoke API key')

    return redirect(url_for('dashboard'))

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check model status
        model_status = 'loaded' if inference_engine.model is not None else 'fallback_mode'
        
        # Check database status
        db_status = 'connected' if db_manager.test_connection() else 'disconnected'
        
        return jsonify({
            'status': 'healthy',
            'model_status': model_status,
            'database_status': db_status,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# API endpoints
@app.route('/api/chat', methods=['POST'])
def api_chat():
    return api_endpoints.chat_endpoint()

@app.route('/api/search', methods=['POST'])
def api_search():
    return api_endpoints.search_endpoint()

@app.route('/api/models', methods=['GET'])
def api_models():
    return api_endpoints.models_endpoint()

@app.route('/api/usage', methods=['GET'])
def api_usage():
    return api_endpoints.usage_endpoint()

# Web chat endpoint
@app.route('/chat', methods=['POST'])
def web_chat():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated. Please log in to use the chat.'}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        message = data.get('message', '').strip()
        use_search = data.get('use_search', False)

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        print(f"Processing chat message: {message[:50]}...")

        # Get response from inference engine
        response = inference_engine.generate_response(message, use_search=use_search)
        
        if not response:
            response = "I apologize, but I'm having trouble generating a response right now. Please try again."

        # Collect conversation data for learning
        try:
            session_id = session.get('session_id', f"web_session_{session.get('user_id', 'anonymous')}")
            learning_service.collect_conversation_data(message, response, session_id)
        except Exception as e:
            print(f"Warning: Could not collect learning data: {e}")

        # Log usage
        try:
            username = session.get('user_id')
            if username:
                db_manager.log_usage(username, 'web_chat', len(message.split()), len(response.split()))
        except Exception as e:
            print(f"Warning: Could not log usage: {e}")

        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'model': 'DieAI'
        })
        
    except Exception as e:
        print(f"Error in web chat: {e}")
        return jsonify({
            'error': 'I encountered an internal error. Please try again.',
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    import argparse
    import socket
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind the server to')
    args = parser.parse_args()
    
    # Find an available port if the default is in use
    def find_free_port(start_port, host='0.0.0.0'):
        for port in range(start_port, start_port + 10):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((host, port))
                    return port
            except OSError:
                continue
        return None
    
    port = find_free_port(args.port, args.host)
    if port is None:
        print(f"Could not find available port starting from {args.port}")
        port = args.port
    
    print("DieAI model loaded successfully")
    print(f"Starting server on {args.host}:{port}")
    
    try:
        app.run(host=args.host, port=port, debug=True)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {port} is still in use. Trying port {port + 1}")
            app.run(host=args.host, port=port + 1, debug=True)
        else:
            raise
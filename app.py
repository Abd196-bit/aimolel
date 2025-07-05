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
db_manager = DatabaseManager(use_postgres=True)
auth_manager = AuthManager(db_manager)
rate_limiter = RateLimiter(db_manager)
inference_engine = InferenceEngine()

# Set learning service
learning_service = LearningService(db_manager)
inference_engine.set_learning_service(learning_service)

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
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    message = data.get('message', '')
    use_search = data.get('use_search', False)

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    try:
        # Get response from inference engine
        response = inference_engine.generate_response(message, use_search=use_search)

        # Log usage
        username = session.get('user_id')
        db_manager.log_usage(username, 'web_chat', len(message.split()), len(response.split()))

        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("DieAI model loaded successfully")
    app.run(host='0.0.0.0', port=5000, debug=True)
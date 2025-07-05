from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta
import secrets
import hashlib
from services.database import DatabaseManager
from api.auth import AuthManager
from api.endpoints import APIEndpoints
from models.inference import InferenceEngine
from utils.rate_limiter import RateLimiter
from utils.helpers import load_config

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
CORS(app)

# Initialize components
db_manager = DatabaseManager()
auth_manager = AuthManager(db_manager)
rate_limiter = RateLimiter(db_manager)
inference_engine = InferenceEngine()
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
    
    if auth_manager.create_user(username, password, email):
        flash('Registration successful')
        return redirect(url_for('login'))
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
    
    user_id = session['user_id']
    api_keys = db_manager.get_user_api_keys(user_id)
    usage_stats = db_manager.get_usage_stats(user_id)
    
    return render_template('dashboard.html', 
                         api_keys=api_keys, 
                         usage_stats=usage_stats)

@app.route('/generate_api_key', methods=['POST'])
def generate_api_key():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    api_key = auth_manager.generate_api_key(user_id)
    
    return jsonify({'api_key': api_key})

@app.route('/revoke_api_key', methods=['POST'])
def revoke_api_key():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    api_key = request.json.get('api_key')
    
    if auth_manager.revoke_api_key(user_id, api_key):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to revoke key'}), 400

# API routes
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

# Chat endpoint for web interface
@app.route('/chat', methods=['POST'])
def web_chat():
    try:
        data = request.json
        message = data.get('message', '')
        use_search = data.get('use_search', False)
        
        # Generate response using inference engine
        response = inference_engine.generate_response(message, use_search=use_search)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize database
    db_manager.initialize_database()
    
    # Load and initialize model if available
    try:
        inference_engine.load_model()
        print("DieAI model loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load model - {e}")
        print("You may need to train the model first")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

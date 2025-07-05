#!/usr/bin/env python3
"""
Main Flask application for DieAI
Lightweight version that works without heavy AI dependencies
"""
import os
import sys
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
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

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register page"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not all([username, email, password]):
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    return redirect(url_for('index'))

# API Routes
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'mode': 'flask',
        'server': 'flask-dev',
        'database': 'postgresql',
        'migration_status': 'completed'
    })

@app.route('/api/models')
def api_models():
    """Get available models"""
    return jsonify({
        'models': [{
            'id': 'dieai-transformer',
            'name': 'DieAI Transformer',
            'description': 'Custom transformer model (Development Phase)',
            'max_tokens': 4096,
            'capabilities': ['chat', 'search'],
            'status': 'development',
            'availability': 'pending_dependencies'
        }]
    })

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """AI Chat endpoint with web search capabilities"""
    try:
        data = request.get_json()
        if not data or 'messages' not in data:
            return jsonify({'error': 'Messages required'}), 400
        
        last_message = data['messages'][-1]['content']
        use_search = data.get('use_search', True)
        
        # Initialize AI brain
        from services.ai_brain import DieAIBrain
        ai_brain = DieAIBrain()
        
        # Get AI response with web search
        ai_response = ai_brain.process_query(last_message, use_search=use_search)
        
        # Calculate token usage (approximate)
        prompt_tokens = len(last_message.split())
        completion_tokens = len(ai_response.split())
        
        response_data = {
            'id': f'chat-{int(datetime.now().timestamp())}',
            'object': 'chat.completion',
            'created': int(datetime.now().timestamp()),
            'model': 'dieai-transformer',
            'choices': [{
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': ai_response
                },
                'finish_reason': 'stop'
            }],
            'usage': {
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': prompt_tokens + completion_tokens
            }
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return jsonify({'error': 'An error occurred processing your request'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"Starting DieAI Flask server on {host}:{port}")
    print("Running in development mode")
    
    app.run(host=host, port=port, debug=True)
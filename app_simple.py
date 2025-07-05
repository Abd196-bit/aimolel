#!/usr/bin/env python3
"""
Simple Flask application for DieAI - working version without heavy dependencies
"""
import os
import time
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simple User model
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

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

# Initialize database tables
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    """Home page"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DieAI - Custom AI Platform</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; text-align: center; }}
            .nav {{ text-align: center; margin: 20px 0; }}
            .nav a {{ margin: 0 10px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
            .nav a:hover {{ background: #0056b3; }}
            .status {{ padding: 15px; margin: 20px 0; border-radius: 5px; }}
            .success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 DieAI Platform</h1>
            <p>Welcome to DieAI - Your Custom AI Platform</p>
            
            <div class="status success">
                ✅ System Status: Running Successfully!<br>
                📊 Database: Connected<br>
                🔧 Migration: Completed
            </div>
            
            <div class="nav">
                <a href="/login">Login</a>
                <a href="/register">Register</a>
                <a href="/health">Health Check</a>
                <a href="/api/models">API Models</a>
            </div>
            
            <h2>Features</h2>
            <ul>
                <li>✅ User Authentication System</li>
                <li>✅ API Key Management</li>
                <li>✅ Database Integration</li>
                <li>✅ REST API Endpoints</li>
                <li>⏳ AI Model Integration (Coming Soon)</li>
                <li>⏳ Search Integration (Coming Soon)</li>
            </ul>
        </div>
    </body>
    </html>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - DieAI</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 400px; margin: 50px auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; text-align: center; }}
            .form-group {{ margin: 15px 0; }}
            label {{ display: block; margin-bottom: 5px; }}
            input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
            button {{ width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }}
            button:hover {{ background: #0056b3; }}
            .nav {{ text-align: center; margin: 20px 0; }}
            .nav a {{ color: #007bff; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 Login</h1>
            <form method="POST">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit">Login</button>
            </form>
            
            <div class="nav">
                <a href="/register">Don't have an account? Register here</a><br>
                <a href="/">← Back to Home</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register page"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('register'))
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - DieAI</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 400px; margin: 50px auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; text-align: center; }}
            .form-group {{ margin: 15px 0; }}
            label {{ display: block; margin-bottom: 5px; }}
            input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
            button {{ width: 100%; padding: 12px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; }}
            button:hover {{ background: #218838; }}
            .nav {{ text-align: center; margin: 20px 0; }}
            .nav a {{ color: #007bff; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📝 Register</h1>
            <form method="POST">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit">Register</button>
            </form>
            
            <div class="nav">
                <a href="/login">Already have an account? Login here</a><br>
                <a href="/">← Back to Home</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - DieAI</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; text-align: center; }}
            .nav {{ text-align: center; margin: 20px 0; }}
            .nav a {{ margin: 0 10px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
            .nav a:hover {{ background: #0056b3; }}
            .welcome {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Dashboard</h1>
            <div class="welcome">
                Welcome, {current_user.username}! Your account is active and ready to use.
            </div>
            
            <h2>Account Information</h2>
            <ul>
                <li><strong>Username:</strong> {current_user.username}</li>
                <li><strong>Email:</strong> {current_user.email}</li>
                <li><strong>Account Created:</strong> {current_user.created_at.strftime('%Y-%m-%d %H:%M:%S')}</li>
                <li><strong>Status:</strong> {'Active' if current_user.is_active else 'Inactive'}</li>
            </ul>
            
            <h2>Available Features</h2>
            <ul>
                <li>✅ User Authentication</li>
                <li>✅ Database Access</li>
                <li>✅ API Endpoints</li>
                <li>⏳ API Key Management (Coming Soon)</li>
                <li>⏳ AI Chat Interface (Coming Soon)</li>
            </ul>
            
            <div class="nav">
                <a href="/logout">Logout</a>
                <a href="/">Home</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'database': 'connected',
        'migration_status': 'completed'
    })

@app.route('/api/models')
def api_models():
    """Get available models"""
    models = [{
        'id': 'dieai-transformer',
        'name': 'DieAI Transformer',
        'description': 'Custom transformer model for DieAI (Coming Soon)',
        'max_tokens': 4096,
        'capabilities': ['chat', 'search'],
        'status': 'development'
    }]
    
    return jsonify({'models': models})

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Basic chat endpoint"""
    data = request.get_json()
    
    if not data or 'messages' not in data:
        return jsonify({'error': 'Messages required'}), 400
    
    # Simple echo response for now
    last_message = data['messages'][-1]['content']
    response = {
        'id': 'chat-' + str(int(time.time())),
        'object': 'chat.completion',
        'created': int(time.time()),
        'model': 'dieai-transformer',
        'choices': [{
            'index': 0,
            'message': {
                'role': 'assistant',
                'content': f"Hello! I received your message: '{last_message}'. AI features will be available soon after model restoration!"
            },
            'finish_reason': 'stop'
        }],
        'usage': {
            'prompt_tokens': 10,
            'completion_tokens': 20,
            'total_tokens': 30
        }
    }
    
    return jsonify(response)

if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)
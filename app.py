import os
import time
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

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

# Initialize database tables
with app.app_context():
    # Import models to ensure they're registered
    from models import User, APIKey, UsageStats, ConversationHistory, RateLimitEntry
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Web routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        from models import User
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('login.html')
        
        from models import User
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('login.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('login.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    from models import APIKey
    api_keys = APIKey.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', api_keys=api_keys)

@app.route('/generate_api_key', methods=['POST'])
@login_required
def generate_api_key():
    from models import APIKey
    
    name = request.form.get('name', 'Default Key')
    
    # Generate new API key
    api_key = APIKey(user_id=current_user.id, name=name)
    new_key = APIKey.generate_key()
    api_key.set_key(new_key)
    
    db.session.add(api_key)
    db.session.commit()
    
    flash(f'API Key generated: {new_key}', 'success')
    return redirect(url_for('dashboard'))

@app.route('/revoke_api_key', methods=['POST'])
@login_required
def revoke_api_key():
    from models import APIKey
    
    key_id = request.form.get('key_id')
    api_key = APIKey.query.filter_by(id=key_id, user_id=current_user.id).first()
    
    if api_key:
        api_key.is_active = False
        db.session.commit()
        flash('API key revoked successfully', 'success')
    else:
        flash('API key not found', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# API endpoints - simplified for now
@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Basic chat endpoint - will be enhanced with AI later"""
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
                'content': f"I received your message: {last_message}. AI features will be available soon!"
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

@app.route('/api/models')
def api_models():
    """Get available models"""
    models = [{
        'id': 'dieai-transformer',
        'name': 'DieAI Transformer',
        'description': 'Custom transformer model for DieAI',
        'max_tokens': 4096,
        'capabilities': ['chat', 'search']
    }]
    
    return jsonify({'models': models})

@app.route('/web_chat', methods=['POST'])
def web_chat():
    """Web chat endpoint for the frontend"""
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'Message required'}), 400
    
    # Simple response for now
    response = f"You said: {message}. AI features will be available soon!"
    
    return jsonify({
        'response': response,
        'timestamp': datetime.now().isoformat()
    })



if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import request, jsonify, g
from functools import wraps
import logging
from datetime import datetime
from typing import Dict, List, Optional

from services.database import DatabaseManager
from .auth import AuthManager
from utils.rate_limiter import RateLimiter
from models.inference import InferenceEngine

logger = logging.getLogger(__name__)

class APIEndpoints:
    def __init__(self, db_manager: DatabaseManager, auth_manager: AuthManager, 
                 rate_limiter: RateLimiter, inference_engine: InferenceEngine):
        self.db_manager = db_manager
        self.auth_manager = auth_manager
        self.rate_limiter = rate_limiter
        self.inference_engine = inference_engine
    
    def require_api_key(self, f):
        """Decorator to require API key authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get API key from headers
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                # Try to get from query parameters
                api_key = request.args.get('api_key')
            
            if not api_key:
                return jsonify({'error': 'API key required'}), 401
            
            # Validate API key
            user_info = self.auth_manager.validate_api_key(api_key)
            
            if not user_info:
                return jsonify({'error': 'Invalid API key'}), 401
            
            # Check rate limits
            if not self.rate_limiter.check_rate_limit(api_key):
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Store user info in request context
            g.user_info = user_info
            g.api_key = api_key
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def chat_endpoint(self):
        """Chat endpoint for AI model interaction"""
        @self.require_api_key
        def _chat():
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({'error': 'No JSON data provided'}), 400
                
                message = data.get('message')
                if not message:
                    return jsonify({'error': 'Message is required'}), 400
                
                # Optional parameters
                use_search = data.get('use_search', False)
                max_length = data.get('max_length', 512)
                temperature = data.get('temperature', 0.8)
                context = data.get('context')
                
                # Set generation parameters
                self.inference_engine.set_generation_parameters(
                    max_length=max_length,
                    temperature=temperature
                )
                
                # Generate response
                response = self.inference_engine.generate_response(
                    message, 
                    use_search=use_search, 
                    context=context
                )
                
                # Log the interaction
                self.db_manager.log_api_interaction(
                    api_key=g.api_key,
                    endpoint='chat',
                    input_data={'message': message, 'use_search': use_search},
                    output_data={'response': response},
                    timestamp=datetime.now().isoformat()
                )
                
                return jsonify({
                    'response': response,
                    'timestamp': datetime.now().isoformat(),
                    'model': 'DieAI',
                    'parameters': {
                        'max_length': max_length,
                        'temperature': temperature,
                        'use_search': use_search
                    }
                })
                
            except Exception as e:
                logger.error(f"Error in chat endpoint: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        return _chat()
    
    def search_endpoint(self):
        """Search endpoint for enhanced information retrieval"""
        @self.require_api_key
        def _search():
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({'error': 'No JSON data provided'}), 400
                
                query = data.get('query')
                if not query:
                    return jsonify({'error': 'Query is required'}), 400
                
                max_results = data.get('max_results', 10)
                
                # Perform search
                search_results = self.inference_engine.search_service.search(
                    query, max_results=max_results
                )
                
                # Log the interaction
                self.db_manager.log_api_interaction(
                    api_key=g.api_key,
                    endpoint='search',
                    input_data={'query': query, 'max_results': max_results},
                    output_data={'results_count': len(search_results)},
                    timestamp=datetime.now().isoformat()
                )
                
                return jsonify({
                    'results': search_results,
                    'query': query,
                    'timestamp': datetime.now().isoformat(),
                    'total_results': len(search_results)
                })
                
            except Exception as e:
                logger.error(f"Error in search endpoint: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        return _search()
    
    def models_endpoint(self):
        """Get available models and their information"""
        @self.require_api_key
        def _models():
            try:
                model_info = self.inference_engine.get_model_info()
                
                models = [{
                    'id': 'dieai-transformer',
                    'name': model_info.get('model_name', 'DieAI Transformer'),
                    'version': model_info.get('version', '1.0'),
                    'description': 'Custom transformer-based language model',
                    'parameters': model_info.get('parameters', 0),
                    'capabilities': [
                        'text_generation',
                        'conversation',
                        'search_integration'
                    ],
                    'context_length': 1024,
                    'pricing': {
                        'input_tokens': 0.0,  # Free for now
                        'output_tokens': 0.0
                    }
                }]
                
                return jsonify({
                    'models': models,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error in models endpoint: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        return _models()
    
    def usage_endpoint(self):
        """Get usage statistics for the API key"""
        @self.require_api_key
        def _usage():
            try:
                # Get usage statistics
                usage_stats = self.db_manager.get_api_key_usage_stats(g.api_key)
                
                # Get rate limit info
                rate_limit_info = self.rate_limiter.get_rate_limit_info(g.api_key)
                
                return jsonify({
                    'usage': usage_stats,
                    'rate_limits': rate_limit_info,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error in usage endpoint: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        return _usage()
    
    def batch_chat_endpoint(self):
        """Batch chat endpoint for multiple messages"""
        @self.require_api_key
        def _batch_chat():
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({'error': 'No JSON data provided'}), 400
                
                messages = data.get('messages')
                if not messages or not isinstance(messages, list):
                    return jsonify({'error': 'Messages array is required'}), 400
                
                if len(messages) > 10:  # Limit batch size
                    return jsonify({'error': 'Maximum 10 messages per batch'}), 400
                
                # Optional parameters
                use_search = data.get('use_search', False)
                max_length = data.get('max_length', 512)
                temperature = data.get('temperature', 0.8)
                
                # Set generation parameters
                self.inference_engine.set_generation_parameters(
                    max_length=max_length,
                    temperature=temperature
                )
                
                # Generate responses
                responses = []
                for message in messages:
                    try:
                        response = self.inference_engine.generate_response(
                            message, 
                            use_search=use_search
                        )
                        responses.append({
                            'message': message,
                            'response': response,
                            'status': 'success'
                        })
                    except Exception as e:
                        responses.append({
                            'message': message,
                            'response': None,
                            'error': str(e),
                            'status': 'error'
                        })
                
                # Log the batch interaction
                self.db_manager.log_api_interaction(
                    api_key=g.api_key,
                    endpoint='batch_chat',
                    input_data={'messages': messages, 'use_search': use_search},
                    output_data={'responses_count': len(responses)},
                    timestamp=datetime.now().isoformat()
                )
                
                return jsonify({
                    'responses': responses,
                    'timestamp': datetime.now().isoformat(),
                    'model': 'DieAI',
                    'batch_size': len(messages)
                })
                
            except Exception as e:
                logger.error(f"Error in batch chat endpoint: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        return _batch_chat()
    
    def health_endpoint(self):
        """Health check endpoint"""
        def _health():
            try:
                # Check model status
                model_status = 'loaded' if self.inference_engine.model is not None else 'not_loaded'
                
                # Check database status
                db_status = 'connected' if self.db_manager.test_connection() else 'disconnected'
                
                return jsonify({
                    'status': 'healthy',
                    'model_status': model_status,
                    'database_status': db_status,
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0'
                })
                
            except Exception as e:
                logger.error(f"Error in health endpoint: {e}")
                return jsonify({
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        return _health()
    
    def generate_embedding_endpoint(self):
        """Generate embeddings for text (future feature)"""
        @self.require_api_key
        def _generate_embedding():
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({'error': 'No JSON data provided'}), 400
                
                text = data.get('text')
                if not text:
                    return jsonify({'error': 'Text is required'}), 400
                
                # For now, return a placeholder
                # In future, implement actual embedding generation
                return jsonify({
                    'error': 'Embedding generation not yet implemented',
                    'message': 'This feature will be available in a future version'
                }), 501
                
            except Exception as e:
                logger.error(f"Error in embedding endpoint: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        return _generate_embedding()

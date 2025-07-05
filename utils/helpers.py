import json
import os
import re
import hashlib
import secrets
import string
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import logging
from functools import wraps
import urllib.parse

logger = logging.getLogger(__name__)

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file"""
    try:
        if not os.path.exists(config_path):
            logger.warning(f"Configuration file not found: {config_path}")
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.info(f"Configuration loaded from {config_path}")
        return config
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file {config_path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading configuration from {config_path}: {e}")
        return {}

def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """Save configuration to JSON file"""
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Configuration saved to {config_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving configuration to {config_path}: {e}")
        return False

def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)

def generate_api_key(prefix: str = "dieai", length: int = 32) -> str:
    """Generate a secure API key with prefix"""
    token = secrets.token_urlsafe(length)
    return f"{prefix}_{token}"

def hash_string(text: str, salt: str = None) -> tuple:
    """Hash a string with optional salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    combined = text + salt
    hash_object = hashlib.sha256(combined.encode())
    return hash_object.hexdigest(), salt

def verify_hash(text: str, hashed: str, salt: str) -> bool:
    """Verify a hashed string"""
    computed_hash, _ = hash_string(text, salt)
    return computed_hash == hashed

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username: str) -> bool:
    """Validate username format"""
    if not username or len(username) < 3 or len(username) > 32:
        return False
    
    # Only allow alphanumeric characters and underscores
    pattern = r'^[a-zA-Z0-9_]+$'
    return re.match(pattern, username) is not None

def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    validation = {
        'valid': True,
        'errors': [],
        'score': 0
    }
    
    if len(password) < 8:
        validation['valid'] = False
        validation['errors'].append('Password must be at least 8 characters long')
    else:
        validation['score'] += 1
    
    if not re.search(r'[a-z]', password):
        validation['valid'] = False
        validation['errors'].append('Password must contain at least one lowercase letter')
    else:
        validation['score'] += 1
    
    if not re.search(r'[A-Z]', password):
        validation['valid'] = False
        validation['errors'].append('Password must contain at least one uppercase letter')
    else:
        validation['score'] += 1
    
    if not re.search(r'\d', password):
        validation['valid'] = False
        validation['errors'].append('Password must contain at least one number')
    else:
        validation['score'] += 1
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        validation['errors'].append('Password should contain at least one special character')
    else:
        validation['score'] += 1
    
    return validation

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Strip whitespace
    text = text.strip()
    
    return text

def clean_text(text: str) -> str:
    """Clean text for processing"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Strip and normalize
    text = text.strip()
    
    return text

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def format_timestamp(timestamp: Union[str, datetime, float]) -> str:
    """Format timestamp for display"""
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        elif isinstance(timestamp, float):
            dt = datetime.fromtimestamp(timestamp)
        elif isinstance(timestamp, datetime):
            dt = timestamp
        else:
            return str(timestamp)
        
        return dt.strftime('%Y-%m-%d %H:%M:%S')
        
    except Exception as e:
        logger.error(f"Error formatting timestamp: {e}")
        return str(timestamp)

def time_ago(timestamp: Union[str, datetime, float]) -> str:
    """Get human-readable time ago string"""
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        elif isinstance(timestamp, float):
            dt = datetime.fromtimestamp(timestamp)
        elif isinstance(timestamp, datetime):
            dt = timestamp
        else:
            return "Unknown"
        
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
            
    except Exception as e:
        logger.error(f"Error calculating time ago: {e}")
        return "Unknown"

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"

def parse_query_params(query_string: str) -> Dict[str, Any]:
    """Parse URL query parameters"""
    try:
        return dict(urllib.parse.parse_qsl(query_string))
    except Exception as e:
        logger.error(f"Error parsing query parameters: {e}")
        return {}

def build_query_string(params: Dict[str, Any]) -> str:
    """Build URL query string from parameters"""
    try:
        return urllib.parse.urlencode(params)
    except Exception as e:
        logger.error(f"Error building query string: {e}")
        return ""

def mask_sensitive_data(data: str, mask_char: str = '*', show_chars: int = 4) -> str:
    """Mask sensitive data like API keys"""
    if not data or len(data) <= show_chars * 2:
        return data
    
    start = data[:show_chars]
    end = data[-show_chars:]
    middle = mask_char * (len(data) - show_chars * 2)
    
    return f"{start}{middle}{end}"

def validate_json(json_string: str) -> Dict[str, Any]:
    """Validate JSON string"""
    try:
        data = json.loads(json_string)
        return {'valid': True, 'data': data, 'error': None}
    except json.JSONDecodeError as e:
        return {'valid': False, 'data': None, 'error': str(e)}
    except Exception as e:
        return {'valid': False, 'data': None, 'error': str(e)}

def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def get_nested_value(data: Dict, path: str, default: Any = None) -> Any:
    """Get nested value from dictionary using dot notation"""
    try:
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
        
    except Exception as e:
        logger.error(f"Error getting nested value: {e}")
        return default

def set_nested_value(data: Dict, path: str, value: Any) -> Dict:
    """Set nested value in dictionary using dot notation"""
    try:
        keys = path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        return data
        
    except Exception as e:
        logger.error(f"Error setting nested value: {e}")
        return data

def retry_with_backoff(retries: int = 3, backoff_factor: float = 1.0, exceptions: tuple = (Exception,)):
    """Decorator to retry function with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == retries - 1:
                        raise
                    
                    wait_time = backoff_factor * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
            
            return None
        return wrapper
    return decorator

def timing_decorator(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
    return wrapper

def rate_limit(calls_per_second: float = 1.0):
    """Rate limiting decorator"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

def memoize(maxsize: int = 128, ttl: int = 3600):
    """Memoization decorator with TTL"""
    def decorator(func):
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = str(args) + str(sorted(kwargs.items()))
            current_time = time.time()
            
            # Check if cached result exists and is still valid
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < ttl:
                    return result
                else:
                    del cache[key]
            
            # Clean old entries if cache is full
            if len(cache) >= maxsize:
                oldest_key = min(cache.keys(), key=lambda k: cache[k][1])
                del cache[oldest_key]
            
            # Compute and cache result
            result = func(*args, **kwargs)
            cache[key] = (result, current_time)
            
            return result
        return wrapper
    return decorator

def ensure_directory_exists(path: str) -> bool:
    """Ensure directory exists, create if necessary"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return False

def safe_filename(filename: str) -> str:
    """Make filename safe for filesystem"""
    # Remove or replace unsafe characters
    safe_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in filename if c in safe_chars)
    
    # Remove multiple spaces and dots
    filename = re.sub(r'\s+', ' ', filename)
    filename = re.sub(r'\.+', '.', filename)
    
    # Trim and limit length
    filename = filename.strip()
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename

def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate basic text similarity using Jaccard similarity"""
    if not text1 or not text2:
        return 0.0
    
    # Convert to lowercase and split into words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    # Calculate Jaccard similarity
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text using simple frequency analysis"""
    if not text:
        return []
    
    # Common stop words
    stop_words = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'were', 'will', 'with', 'the', 'this', 'but', 'they',
        'have', 'had', 'what', 'said', 'each', 'which', 'she', 'do', 'how',
        'their', 'if', 'up', 'out', 'many', 'then', 'them', 'these', 'so'
    }
    
    # Clean and tokenize
    text = clean_text(text.lower())
    words = re.findall(r'\b[a-z]+\b', text)
    
    # Filter stop words and count frequency
    word_freq = {}
    for word in words:
        if word not in stop_words and len(word) > 2:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:max_keywords]]

def validate_model_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate model configuration"""
    validation = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    required_fields = ['vocab_size', 'd_model', 'n_heads', 'n_layers']
    for field in required_fields:
        if field not in config:
            validation['valid'] = False
            validation['errors'].append(f"Missing required field: {field}")
    
    # Validate numeric fields
    numeric_fields = {
        'vocab_size': (1000, 100000),
        'd_model': (128, 2048),
        'n_heads': (1, 32),
        'n_layers': (1, 48)
    }
    
    for field, (min_val, max_val) in numeric_fields.items():
        if field in config:
            try:
                value = int(config[field])
                if value < min_val or value > max_val:
                    validation['warnings'].append(f"{field} value {value} is outside recommended range [{min_val}, {max_val}]")
            except (ValueError, TypeError):
                validation['valid'] = False
                validation['errors'].append(f"{field} must be a valid integer")
    
    # Validate d_model is divisible by n_heads
    if 'd_model' in config and 'n_heads' in config:
        try:
            d_model = int(config['d_model'])
            n_heads = int(config['n_heads'])
            if d_model % n_heads != 0:
                validation['valid'] = False
                validation['errors'].append("d_model must be divisible by n_heads")
        except (ValueError, TypeError):
            pass
    
    return validation

def get_system_info() -> Dict[str, Any]:
    """Get system information"""
    import platform
    import psutil
    
    try:
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': psutil.disk_usage('/').percent if os.path.exists('/') else None
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {
            'platform': platform.system(),
            'python_version': platform.python_version(),
            'error': str(e)
        }

def health_check() -> Dict[str, Any]:
    """Perform basic health check"""
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }
    
    try:
        # Check file system
        status['checks']['filesystem'] = {
            'status': 'ok' if os.path.exists('.') else 'error',
            'writable': os.access('.', os.W_OK)
        }
        
        # Check memory usage
        import psutil
        memory = psutil.virtual_memory()
        status['checks']['memory'] = {
            'status': 'ok' if memory.percent < 90 else 'warning',
            'usage_percent': memory.percent,
            'available_gb': memory.available / (1024**3)
        }
        
        # Check disk usage
        disk = psutil.disk_usage('.')
        status['checks']['disk'] = {
            'status': 'ok' if disk.percent < 90 else 'warning',
            'usage_percent': disk.percent,
            'free_gb': disk.free / (1024**3)
        }
        
    except Exception as e:
        status['status'] = 'error'
        status['error'] = str(e)
    
    # Overall status
    if any(check.get('status') == 'error' for check in status['checks'].values()):
        status['status'] = 'error'
    elif any(check.get('status') == 'warning' for check in status['checks'].values()):
        status['status'] = 'warning'
    
    return status

# Environment helpers
def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable"""
    value = os.getenv(key, '').lower()
    return value in ('true', '1', 'yes', 'on')

def get_env_int(key: str, default: int = 0) -> int:
    """Get integer environment variable"""
    try:
        return int(os.getenv(key, default))
    except (ValueError, TypeError):
        return default

def get_env_float(key: str, default: float = 0.0) -> float:
    """Get float environment variable"""
    try:
        return float(os.getenv(key, default))
    except (ValueError, TypeError):
        return default

def get_env_list(key: str, default: List[str] = None, separator: str = ',') -> List[str]:
    """Get list environment variable"""
    if default is None:
        default = []
    
    value = os.getenv(key, '')
    if not value:
        return default
    
    return [item.strip() for item in value.split(separator) if item.strip()]

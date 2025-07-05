import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging
from collections import defaultdict
import threading

from services.database import DatabaseManager

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
        # In-memory rate limiting data (for performance)
        self.rate_data = defaultdict(lambda: defaultdict(list))
        self.lock = threading.Lock()
        
        # Rate limits configuration
        self.rate_limits = {
            'default': {
                'requests_per_minute': 60,
                'requests_per_hour': 1000,
                'requests_per_day': 10000
            },
            'premium': {
                'requests_per_minute': 120,
                'requests_per_hour': 5000,
                'requests_per_day': 50000
            }
        }
        
        # Endpoint-specific limits
        self.endpoint_limits = {
            'chat': {
                'requests_per_minute': 30,
                'requests_per_hour': 500
            },
            'search': {
                'requests_per_minute': 20,
                'requests_per_hour': 200
            },
            'batch_chat': {
                'requests_per_minute': 10,
                'requests_per_hour': 100
            }
        }
        
        # Burst limits
        self.burst_limits = {
            'max_concurrent_requests': 5,
            'burst_window_seconds': 10,
            'burst_max_requests': 10
        }
        
        # Cleanup interval
        self.cleanup_interval = 3600  # 1 hour
        self.last_cleanup = time.time()
    
    def check_rate_limit(self, api_key: str, endpoint: str = 'default') -> bool:
        """Check if request is within rate limits"""
        try:
            with self.lock:
                current_time = time.time()
                
                # Clean up old data periodically
                if current_time - self.last_cleanup > self.cleanup_interval:
                    self._cleanup_old_data()
                    self.last_cleanup = current_time
                
                # Check burst limits
                if not self._check_burst_limits(api_key, current_time):
                    logger.warning(f"Burst limit exceeded for API key: {api_key}")
                    return False
                
                # Check endpoint-specific limits
                if not self._check_endpoint_limits(api_key, endpoint, current_time):
                    logger.warning(f"Endpoint limit exceeded for API key: {api_key}, endpoint: {endpoint}")
                    return False
                
                # Check general rate limits
                if not self._check_general_limits(api_key, current_time):
                    logger.warning(f"General rate limit exceeded for API key: {api_key}")
                    return False
                
                # Record the request
                self._record_request(api_key, endpoint, current_time)
                
                return True
                
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Fail open - allow request if there's an error
            return True
    
    def _check_burst_limits(self, api_key: str, current_time: float) -> bool:
        """Check burst limits"""
        burst_window = self.burst_limits['burst_window_seconds']
        max_burst = self.burst_limits['burst_max_requests']
        
        # Get recent requests within burst window
        recent_requests = [
            req_time for req_time in self.rate_data[api_key]['requests']
            if current_time - req_time < burst_window
        ]
        
        return len(recent_requests) < max_burst
    
    def _check_endpoint_limits(self, api_key: str, endpoint: str, current_time: float) -> bool:
        """Check endpoint-specific limits"""
        if endpoint not in self.endpoint_limits:
            return True
        
        endpoint_config = self.endpoint_limits[endpoint]
        endpoint_requests = self.rate_data[api_key][f'endpoint_{endpoint}']
        
        # Check per-minute limit
        if 'requests_per_minute' in endpoint_config:
            minute_requests = [
                req_time for req_time in endpoint_requests
                if current_time - req_time < 60
            ]
            if len(minute_requests) >= endpoint_config['requests_per_minute']:
                return False
        
        # Check per-hour limit
        if 'requests_per_hour' in endpoint_config:
            hour_requests = [
                req_time for req_time in endpoint_requests
                if current_time - req_time < 3600
            ]
            if len(hour_requests) >= endpoint_config['requests_per_hour']:
                return False
        
        return True
    
    def _check_general_limits(self, api_key: str, current_time: float) -> bool:
        """Check general rate limits"""
        # Get user tier (default for now)
        user_tier = self._get_user_tier(api_key)
        limits = self.rate_limits.get(user_tier, self.rate_limits['default'])
        
        all_requests = self.rate_data[api_key]['requests']
        
        # Check per-minute limit
        minute_requests = [
            req_time for req_time in all_requests
            if current_time - req_time < 60
        ]
        if len(minute_requests) >= limits['requests_per_minute']:
            return False
        
        # Check per-hour limit
        hour_requests = [
            req_time for req_time in all_requests
            if current_time - req_time < 3600
        ]
        if len(hour_requests) >= limits['requests_per_hour']:
            return False
        
        # Check per-day limit
        day_requests = [
            req_time for req_time in all_requests
            if current_time - req_time < 86400
        ]
        if len(day_requests) >= limits['requests_per_day']:
            return False
        
        return True
    
    def _record_request(self, api_key: str, endpoint: str, current_time: float):
        """Record a request"""
        # Record in general requests
        self.rate_data[api_key]['requests'].append(current_time)
        
        # Record in endpoint-specific requests
        if endpoint in self.endpoint_limits:
            self.rate_data[api_key][f'endpoint_{endpoint}'].append(current_time)
        
        # Log to database (async to avoid blocking)
        try:
            self._log_rate_limit_event(api_key, endpoint, current_time)
        except Exception as e:
            logger.error(f"Error logging rate limit event: {e}")
    
    def _get_user_tier(self, api_key: str) -> str:
        """Get user tier for API key"""
        # For now, all users are on default tier
        # This can be extended to support premium tiers
        return 'default'
    
    def _cleanup_old_data(self):
        """Clean up old rate limiting data"""
        current_time = time.time()
        cutoff_time = current_time - 86400  # Keep data for 24 hours
        
        for api_key in list(self.rate_data.keys()):
            for request_type in list(self.rate_data[api_key].keys()):
                # Filter out old requests
                self.rate_data[api_key][request_type] = [
                    req_time for req_time in self.rate_data[api_key][request_type]
                    if req_time > cutoff_time
                ]
            
            # Remove empty entries
            if not any(self.rate_data[api_key].values()):
                del self.rate_data[api_key]
    
    def _log_rate_limit_event(self, api_key: str, endpoint: str, timestamp: float):
        """Log rate limit event to database"""
        try:
            # Update rate limit record in database
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if record exists for current window
                window_start = datetime.fromtimestamp(timestamp).replace(second=0, microsecond=0)
                
                cursor.execute('''
                    SELECT id, request_count FROM rate_limits 
                    WHERE api_key = ? AND endpoint = ? AND window_start = ?
                ''', (api_key, endpoint, window_start.isoformat()))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing record
                    cursor.execute('''
                        UPDATE rate_limits 
                        SET request_count = request_count + 1 
                        WHERE id = ?
                    ''', (existing[0],))
                else:
                    # Create new record
                    cursor.execute('''
                        INSERT INTO rate_limits (api_key, endpoint, request_count, window_start)
                        VALUES (?, ?, 1, ?)
                    ''', (api_key, endpoint, window_start.isoformat()))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error logging rate limit event: {e}")
    
    def get_rate_limit_info(self, api_key: str) -> Dict:
        """Get current rate limit status for API key"""
        try:
            with self.lock:
                current_time = time.time()
                user_tier = self._get_user_tier(api_key)
                limits = self.rate_limits.get(user_tier, self.rate_limits['default'])
                
                all_requests = self.rate_data[api_key]['requests']
                
                # Count requests in different time windows
                minute_requests = len([
                    req_time for req_time in all_requests
                    if current_time - req_time < 60
                ])
                
                hour_requests = len([
                    req_time for req_time in all_requests
                    if current_time - req_time < 3600
                ])
                
                day_requests = len([
                    req_time for req_time in all_requests
                    if current_time - req_time < 86400
                ])
                
                # Calculate time until reset
                if minute_requests > 0:
                    oldest_minute_request = min([
                        req_time for req_time in all_requests
                        if current_time - req_time < 60
                    ])
                    minute_reset = int(60 - (current_time - oldest_minute_request))
                else:
                    minute_reset = 0
                
                return {
                    'limits': limits,
                    'current_usage': {
                        'requests_per_minute': minute_requests,
                        'requests_per_hour': hour_requests,
                        'requests_per_day': day_requests
                    },
                    'remaining': {
                        'requests_per_minute': max(0, limits['requests_per_minute'] - minute_requests),
                        'requests_per_hour': max(0, limits['requests_per_hour'] - hour_requests),
                        'requests_per_day': max(0, limits['requests_per_day'] - day_requests)
                    },
                    'reset_time': {
                        'minute': minute_reset,
                        'hour': 3600 - (current_time % 3600),
                        'day': 86400 - (current_time % 86400)
                    },
                    'user_tier': user_tier
                }
                
        except Exception as e:
            logger.error(f"Error getting rate limit info: {e}")
            return {
                'error': 'Unable to retrieve rate limit information'
            }
    
    def reset_rate_limit(self, api_key: str):
        """Reset rate limit for API key (admin function)"""
        try:
            with self.lock:
                if api_key in self.rate_data:
                    del self.rate_data[api_key]
                logger.info(f"Rate limit reset for API key: {api_key}")
        except Exception as e:
            logger.error(f"Error resetting rate limit: {e}")
    
    def set_custom_limit(self, api_key: str, limits: Dict):
        """Set custom rate limits for API key"""
        try:
            # This would typically be stored in the database
            # For now, we'll use a simple in-memory approach
            if not hasattr(self, 'custom_limits'):
                self.custom_limits = {}
            
            self.custom_limits[api_key] = limits
            logger.info(f"Custom rate limits set for API key: {api_key}")
            
        except Exception as e:
            logger.error(f"Error setting custom rate limit: {e}")
    
    def get_usage_statistics(self, api_key: str, days: int = 7) -> Dict:
        """Get usage statistics for API key"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get usage over time
                cursor.execute('''
                    SELECT 
                        DATE(window_start) as date,
                        endpoint,
                        SUM(request_count) as total_requests
                    FROM rate_limits 
                    WHERE api_key = ? AND window_start > datetime('now', '-{} days')
                    GROUP BY DATE(window_start), endpoint
                    ORDER BY date DESC
                '''.format(days), (api_key,))
                
                usage_data = [dict(row) for row in cursor.fetchall()]
                
                # Get total requests
                cursor.execute('''
                    SELECT 
                        endpoint,
                        SUM(request_count) as total_requests
                    FROM rate_limits 
                    WHERE api_key = ? AND window_start > datetime('now', '-{} days')
                    GROUP BY endpoint
                '''.format(days), (api_key,))
                
                endpoint_totals = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'usage_over_time': usage_data,
                    'endpoint_totals': endpoint_totals,
                    'period_days': days
                }
                
        except Exception as e:
            logger.error(f"Error getting usage statistics: {e}")
            return {
                'error': 'Unable to retrieve usage statistics'
            }
    
    def is_rate_limited(self, api_key: str, endpoint: str = 'default') -> Tuple[bool, Dict]:
        """Check if API key is currently rate limited"""
        try:
            current_time = time.time()
            user_tier = self._get_user_tier(api_key)
            limits = self.rate_limits.get(user_tier, self.rate_limits['default'])
            
            all_requests = self.rate_data[api_key]['requests']
            
            # Check minute limit
            minute_requests = [
                req_time for req_time in all_requests
                if current_time - req_time < 60
            ]
            
            if len(minute_requests) >= limits['requests_per_minute']:
                return True, {
                    'reason': 'minute_limit_exceeded',
                    'current': len(minute_requests),
                    'limit': limits['requests_per_minute'],
                    'reset_in': 60 - (current_time - min(minute_requests))
                }
            
            # Check hour limit
            hour_requests = [
                req_time for req_time in all_requests
                if current_time - req_time < 3600
            ]
            
            if len(hour_requests) >= limits['requests_per_hour']:
                return True, {
                    'reason': 'hour_limit_exceeded',
                    'current': len(hour_requests),
                    'limit': limits['requests_per_hour'],
                    'reset_in': 3600 - (current_time - min(hour_requests))
                }
            
            # Check day limit
            day_requests = [
                req_time for req_time in all_requests
                if current_time - req_time < 86400
            ]
            
            if len(day_requests) >= limits['requests_per_day']:
                return True, {
                    'reason': 'day_limit_exceeded',
                    'current': len(day_requests),
                    'limit': limits['requests_per_day'],
                    'reset_in': 86400 - (current_time - min(day_requests))
                }
            
            return False, {}
            
        except Exception as e:
            logger.error(f"Error checking rate limit status: {e}")
            return False, {'error': str(e)}

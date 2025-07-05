import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "dieai.db"):
        self.db_path = db_path
        self.connection = None
        
    def initialize_database(self):
        """Initialize database with required tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        password_salt TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        created_at TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT 1
                    )
                ''')
                
                # API keys table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_keys (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        api_key TEXT UNIQUE NOT NULL,
                        username TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        usage_count INTEGER DEFAULT 0,
                        last_used TEXT,
                        FOREIGN KEY (username) REFERENCES users (username)
                    )
                ''')
                
                # API interactions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        api_key TEXT NOT NULL,
                        endpoint TEXT NOT NULL,
                        input_data TEXT,
                        output_data TEXT,
                        timestamp TEXT NOT NULL,
                        response_time REAL,
                        status_code INTEGER,
                        FOREIGN KEY (api_key) REFERENCES api_keys (api_key)
                    )
                ''')
                
                # Rate limiting table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS rate_limits (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        api_key TEXT NOT NULL,
                        endpoint TEXT NOT NULL,
                        request_count INTEGER DEFAULT 0,
                        window_start TEXT NOT NULL,
                        FOREIGN KEY (api_key) REFERENCES api_keys (api_key)
                    )
                ''')
                
                # Model training logs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS training_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_name TEXT NOT NULL,
                        epoch INTEGER,
                        train_loss REAL,
                        val_loss REAL,
                        learning_rate REAL,
                        timestamp TEXT NOT NULL,
                        metadata TEXT
                    )
                ''')
                
                # Conversations table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        user_message TEXT NOT NULL,
                        ai_response TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        api_key TEXT,
                        metadata TEXT
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    # User management methods
    def create_user(self, user_data: Dict) -> bool:
        """Create a new user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, password_hash, password_salt, email, created_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_data['username'],
                    user_data['password_hash'],
                    user_data['password_salt'],
                    user_data['email'],
                    user_data['created_at'],
                    user_data['is_active']
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def update_user_password(self, username: str, password_hash: str, password_salt: str) -> bool:
        """Update user password"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET password_hash = ?, password_salt = ? WHERE username = ?
                ''', (password_hash, password_salt, username))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating user password: {e}")
            return False
    
    def deactivate_user(self, username: str) -> bool:
        """Deactivate user account"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET is_active = 0 WHERE username = ?', (username,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            return False
    
    # API key management methods
    def create_api_key(self, api_key_data: Dict) -> bool:
        """Create a new API key"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO api_keys (api_key, username, created_at, is_active, usage_count, last_used)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    api_key_data['api_key'],
                    api_key_data['username'],
                    api_key_data['created_at'],
                    api_key_data['is_active'],
                    api_key_data['usage_count'],
                    api_key_data['last_used']
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error creating API key: {e}")
            return False
    
    def get_api_key(self, api_key: str) -> Optional[Dict]:
        """Get API key data"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM api_keys WHERE api_key = ?', (api_key,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting API key: {e}")
            return None
    
    def update_api_key_usage(self, api_key: str) -> bool:
        """Update API key usage statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE api_keys 
                    SET usage_count = usage_count + 1, last_used = ? 
                    WHERE api_key = ?
                ''', (datetime.now().isoformat(), api_key))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating API key usage: {e}")
            return False
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke API key"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE api_keys SET is_active = 0 WHERE api_key = ?', (api_key,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error revoking API key: {e}")
            return False
    
    def get_user_api_keys(self, username: str) -> List[Dict]:
        """Get all API keys for a user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT api_key, created_at, is_active, usage_count, last_used 
                    FROM api_keys 
                    WHERE username = ?
                    ORDER BY created_at DESC
                ''', (username,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting user API keys: {e}")
            return []
    
    def deactivate_user_api_keys(self, username: str) -> bool:
        """Deactivate all API keys for a user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE api_keys SET is_active = 0 WHERE username = ?', (username,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deactivating user API keys: {e}")
            return False
    
    # API interaction logging methods
    def log_api_interaction(self, api_key: str, endpoint: str, input_data: Dict, 
                           output_data: Dict, timestamp: str, response_time: float = None,
                           status_code: int = 200) -> bool:
        """Log API interaction"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO api_interactions 
                    (api_key, endpoint, input_data, output_data, timestamp, response_time, status_code)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    api_key,
                    endpoint,
                    json.dumps(input_data),
                    json.dumps(output_data),
                    timestamp,
                    response_time,
                    status_code
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging API interaction: {e}")
            return False
    
    def get_api_key_usage_stats(self, api_key: str) -> Dict:
        """Get usage statistics for an API key"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get overall stats
                cursor.execute('''
                    SELECT COUNT(*) as total_requests, 
                           COUNT(DISTINCT DATE(timestamp)) as active_days
                    FROM api_interactions 
                    WHERE api_key = ?
                ''', (api_key,))
                
                overall_stats = dict(cursor.fetchone())
                
                # Get endpoint stats
                cursor.execute('''
                    SELECT endpoint, COUNT(*) as request_count
                    FROM api_interactions 
                    WHERE api_key = ?
                    GROUP BY endpoint
                    ORDER BY request_count DESC
                ''', (api_key,))
                
                endpoint_stats = [dict(row) for row in cursor.fetchall()]
                
                # Get recent activity
                cursor.execute('''
                    SELECT endpoint, timestamp
                    FROM api_interactions 
                    WHERE api_key = ?
                    ORDER BY timestamp DESC
                    LIMIT 10
                ''', (api_key,))
                
                recent_activity = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'overall': overall_stats,
                    'by_endpoint': endpoint_stats,
                    'recent_activity': recent_activity
                }
                
        except Exception as e:
            logger.error(f"Error getting API key usage stats: {e}")
            return {}
    
    def get_usage_stats(self, username: str) -> Dict:
        """Get usage statistics for a user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get total requests across all API keys
                cursor.execute('''
                    SELECT COUNT(*) as total_requests
                    FROM api_interactions ai
                    JOIN api_keys ak ON ai.api_key = ak.api_key
                    WHERE ak.username = ?
                ''', (username,))
                
                total_requests = cursor.fetchone()[0]
                
                # Get requests by endpoint
                cursor.execute('''
                    SELECT ai.endpoint, COUNT(*) as request_count
                    FROM api_interactions ai
                    JOIN api_keys ak ON ai.api_key = ak.api_key
                    WHERE ak.username = ?
                    GROUP BY ai.endpoint
                    ORDER BY request_count DESC
                ''', (username,))
                
                endpoint_stats = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'total_requests': total_requests,
                    'by_endpoint': endpoint_stats
                }
                
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return {}
    
    # Training log methods
    def log_training_step(self, model_name: str, epoch: int, train_loss: float,
                         val_loss: float = None, learning_rate: float = None,
                         metadata: Dict = None) -> bool:
        """Log training step"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO training_logs 
                    (model_name, epoch, train_loss, val_loss, learning_rate, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    model_name,
                    epoch,
                    train_loss,
                    val_loss,
                    learning_rate,
                    datetime.now().isoformat(),
                    json.dumps(metadata) if metadata else None
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging training step: {e}")
            return False
    
    def get_training_history(self, model_name: str, limit: int = 100) -> List[Dict]:
        """Get training history for a model"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM training_logs 
                    WHERE model_name = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (model_name, limit))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting training history: {e}")
            return []
    
    # Conversation logging methods
    def log_conversation(self, session_id: str, user_message: str, ai_response: str,
                        api_key: str = None, metadata: Dict = None) -> bool:
        """Log conversation"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO conversations 
                    (session_id, user_message, ai_response, timestamp, api_key, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    user_message,
                    ai_response,
                    datetime.now().isoformat(),
                    api_key,
                    json.dumps(metadata) if metadata else None
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging conversation: {e}")
            return False
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM conversations 
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (session_id, limit))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

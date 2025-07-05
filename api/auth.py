import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
import os
import logging

from services.database import DatabaseManager

logger = logging.getLogger(__name__)

class AuthManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.secret_key = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
        self.api_key_length = 32
        self.password_salt_length = 16
        
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(self.password_salt_length)
        
        # Combine password and salt
        password_salt = password + salt
        
        # Hash using SHA-256
        hash_object = hashlib.sha256(password_salt.encode())
        password_hash = hash_object.hexdigest()
        
        return password_hash, salt
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify password against stored hash"""
        computed_hash, _ = self.hash_password(password, salt)
        return computed_hash == stored_hash
    
    def create_user(self, username: str, password: str, email: str) -> bool:
        """Create a new user"""
        try:
            # Check if user already exists
            if self.db_manager.get_user(username):
                logger.warning(f"User {username} already exists")
                return False
            
            # Hash password
            password_hash, salt = self.hash_password(password)
            
            # Create user in database
            user_data = {
                'username': username,
                'password_hash': password_hash,
                'password_salt': salt,
                'email': email,
                'created_at': datetime.now().isoformat(),
                'is_active': True
            }
            
            success = self.db_manager.create_user(user_data)
            
            if success:
                logger.info(f"User {username} created successfully")
            else:
                logger.error(f"Failed to create user {username}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user with username and password"""
        try:
            user = self.db_manager.get_user(username)
            
            if not user:
                logger.warning(f"User {username} not found")
                return False
            
            if not user.get('is_active', False):
                logger.warning(f"User {username} is not active")
                return False
            
            # Verify password
            stored_hash = user['password_hash']
            salt = user['password_salt']
            
            if self.verify_password(password, stored_hash, salt):
                logger.info(f"User {username} authenticated successfully")
                return True
            else:
                logger.warning(f"Invalid password for user {username}")
                return False
                
        except Exception as e:
            logger.error(f"Error authenticating user {username}: {e}")
            return False
    
    def generate_api_key(self, username: str) -> Optional[str]:
        """Generate a new API key for user"""
        try:
            # Check if user exists
            user = self.db_manager.get_user(username)
            if not user:
                logger.warning(f"User {username} not found")
                return None
            
            # Generate API key
            api_key = f"dieai_{secrets.token_urlsafe(self.api_key_length)}"
            
            # Store API key in database
            api_key_data = {
                'api_key': api_key,
                'username': username,
                'created_at': datetime.now().isoformat(),
                'is_active': True,
                'usage_count': 0,
                'last_used': None
            }
            
            success = self.db_manager.create_api_key(api_key_data)
            
            if success:
                logger.info(f"API key generated for user {username}")
                return api_key
            else:
                logger.error(f"Failed to generate API key for user {username}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating API key for user {username}: {e}")
            return None
    
    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """Validate API key and return user info"""
        try:
            api_key_data = self.db_manager.get_api_key(api_key)
            
            if not api_key_data:
                logger.warning(f"Invalid API key: {api_key}")
                return None
            
            if not api_key_data.get('is_active', False):
                logger.warning(f"Inactive API key: {api_key}")
                return None
            
            # Update usage statistics
            self.db_manager.update_api_key_usage(api_key)
            
            # Get user info
            user = self.db_manager.get_user(api_key_data['username'])
            
            if not user or not user.get('is_active', False):
                logger.warning(f"User not found or inactive for API key: {api_key}")
                return None
            
            return {
                'username': user['username'],
                'email': user['email'],
                'api_key': api_key,
                'usage_count': api_key_data.get('usage_count', 0)
            }
            
        except Exception as e:
            logger.error(f"Error validating API key {api_key}: {e}")
            return None
    
    def revoke_api_key(self, username: str, api_key: str) -> bool:
        """Revoke an API key"""
        try:
            # Verify the API key belongs to the user
            api_key_data = self.db_manager.get_api_key(api_key)
            
            if not api_key_data:
                logger.warning(f"API key not found: {api_key}")
                return False
            
            if api_key_data['username'] != username:
                logger.warning(f"API key {api_key} does not belong to user {username}")
                return False
            
            # Revoke the API key
            success = self.db_manager.revoke_api_key(api_key)
            
            if success:
                logger.info(f"API key revoked for user {username}")
            else:
                logger.error(f"Failed to revoke API key for user {username}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error revoking API key for user {username}: {e}")
            return False
    
    def generate_jwt_token(self, username: str, expires_hours: int = 24) -> str:
        """Generate JWT token for user"""
        try:
            payload = {
                'username': username,
                'exp': datetime.utcnow() + timedelta(hours=expires_hours),
                'iat': datetime.utcnow(),
                'type': 'access'
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            return token
            
        except Exception as e:
            logger.error(f"Error generating JWT token for user {username}: {e}")
            return None
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
        except Exception as e:
            logger.error(f"Error verifying JWT token: {e}")
            return None
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            # Authenticate with old password
            if not self.authenticate_user(username, old_password):
                logger.warning(f"Invalid old password for user {username}")
                return False
            
            # Hash new password
            new_hash, new_salt = self.hash_password(new_password)
            
            # Update password in database
            success = self.db_manager.update_user_password(username, new_hash, new_salt)
            
            if success:
                logger.info(f"Password changed for user {username}")
            else:
                logger.error(f"Failed to change password for user {username}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error changing password for user {username}: {e}")
            return False
    
    def deactivate_user(self, username: str) -> bool:
        """Deactivate user account"""
        try:
            success = self.db_manager.deactivate_user(username)
            
            if success:
                logger.info(f"User {username} deactivated")
                # Also deactivate all API keys for this user
                self.db_manager.deactivate_user_api_keys(username)
            else:
                logger.error(f"Failed to deactivate user {username}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deactivating user {username}: {e}")
            return False
    
    def get_user_api_keys(self, username: str) -> list:
        """Get all API keys for a user"""
        try:
            return self.db_manager.get_user_api_keys(username)
        except Exception as e:
            logger.error(f"Error getting API keys for user {username}: {e}")
            return []

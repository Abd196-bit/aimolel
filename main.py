#!/usr/bin/env python3
"""
Main entry point for DieAI application after migration to Replit
API-only version without UI components
"""
from app_api_only import app  # Import the Flask app from app_api_only.py

if __name__ == '__main__':
    app.run()
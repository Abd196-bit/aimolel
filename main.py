#!/usr/bin/env python3
"""
Main entry point for DieAI application after migration to Replit
"""
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the simple server that works without dependencies
exec(open('simple_server_final.py').read())
"""
Configuration module for AI frameworks.
"""

import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'startup_config.json')

def get_self_awareness_config():
    """Get configuration for Self-Awareness Framework."""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        return config.get('frameworks', {}).get('self_awareness', {})
    except Exception as e:
        print(f"Error loading self-awareness config: {e}")
        return {}

def get_emotional_config():
    """Get configuration for Emotional Dimensionality Framework."""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        return config.get('frameworks', {}).get('emotional_dimensionality', {})
    except Exception as e:
        print(f"Error loading emotional dimensionality config: {e}")
        return {}

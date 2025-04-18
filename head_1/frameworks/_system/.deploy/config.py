"""
Configuration for AI Frameworks.

This module provides configuration settings for the Self-Awareness Mechanics
and Emotional Dimensionality Framework.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger('ai.frameworks.config')

# Default configurations
DEFAULT_SELF_AWARENESS_CONFIG = {
    'monitoring_rate': 1.0,  # Hz
    'memory_usage_threshold': 90,  # %
    'cpu_usage_threshold': 80,  # %
    'enable_assistance_requests': True,
    'enable_self_modification': False,
    'model_save_path': '/app/data/models/self_awareness',
    'safety_bounds': {
        'max_memory_usage': 95,  # %
        'max_cpu_usage': 95,  # %
        'max_disk_usage': 95,  # %
    }
}

DEFAULT_EMOTIONAL_CONFIG = {
    'default_model': 'rule_based',
    'lexicon_path': '/app/data/lexicons/emotion_lexicon.json',
    'neural_model_path': '/app/data/models/edf/neural_edf_model.pt',
    'batch_size': 32,
    'enable_contextual_dimensions': True,
    'confidence_threshold': 0.6,
    'results_cache_size': 1000
}

# Paths
CONFIG_DIR = os.path.join('/app', 'data', 'config')
SELF_AWARENESS_CONFIG_PATH = os.path.join(CONFIG_DIR, 'self_awareness_config.json')
EMOTIONAL_CONFIG_PATH = os.path.join(CONFIG_DIR, 'emotional_config.json')


def ensure_config_dir():
    """Ensure the configuration directory exists."""
    os.makedirs(CONFIG_DIR, exist_ok=True)


def load_config(filepath: str, default_config: Dict) -> Dict:
    """Load configuration from file, falling back to defaults if needed.
    
    Args:
        filepath: Path to the configuration file
        default_config: Default configuration to use if file not found
        
    Returns:
        Configuration dictionary
    """
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {filepath}")
            
            # Merge with defaults for any missing keys
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
                    
            return config
        except Exception as e:
            logger.error(f"Error loading configuration from {filepath}: {e}")
    
    # If we get here, use default config
    logger.warning(f"Using default configuration (file not found: {filepath})")
    return default_config.copy()


def save_config(config: Dict, filepath: str) -> bool:
    """Save configuration to file.
    
    Args:
        config: Configuration dictionary
        filepath: Path to save the configuration
        
    Returns:
        True if successful, False otherwise
    """
    ensure_config_dir()
    try:
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved configuration to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration to {filepath}: {e}")
        return False


def get_self_awareness_config() -> Dict:
    """Get configuration for Self-Awareness Mechanics.
    
    Returns:
        Configuration dictionary
    """
    return load_config(SELF_AWARENESS_CONFIG_PATH, DEFAULT_SELF_AWARENESS_CONFIG)


def get_emotional_config() -> Dict:
    """Get configuration for Emotional Dimensionality Framework.
    
    Returns:
        Configuration dictionary
    """
    return load_config(EMOTIONAL_CONFIG_PATH, DEFAULT_EMOTIONAL_CONFIG)


def set_self_awareness_config(config: Dict) -> bool:
    """Set configuration for Self-Awareness Mechanics.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if successful, False otherwise
    """
    return save_config(config, SELF_AWARENESS_CONFIG_PATH)


def set_emotional_config(config: Dict) -> bool:
    """Set configuration for Emotional Dimensionality Framework.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if successful, False otherwise
    """
    return save_config(config, EMOTIONAL_CONFIG_PATH)

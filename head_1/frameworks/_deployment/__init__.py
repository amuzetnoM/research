"""
AI Frameworks Module for Advanced AI Research.

This module provides implementations of advanced AI frameworks:
- Self-Awareness Mechanics - For implementing self-awareness in AI systems
- Emotional Dimensionality Framework - For advanced sentiment analysis
"""

import logging
import os
import importlib.util

# Configure logging
logger = logging.getLogger('ai.frameworks')

# Dictionary to track framework availability
available_frameworks = {
    'self_awareness': False,
    'emotional_dimensionality': False,
}

# Try to import each framework
try:
    from ...frameworks.emotional_dimensionality.emotional_dimensionality import self_awareness
    available_frameworks['self_awareness'] = True
except ImportError as e:
    logger.warning(f"Self-Awareness Mechanics framework not available: {e}")

try:
    from ...frameworks.emotional_dimensionality import emotional_dimensionality
    available_frameworks['emotional_dimensionality'] = True
except ImportError as e:
    logger.warning(f"Emotional Dimensionality Framework not available: {e}")

# Define convenience functions
def get_self_awareness_framework(config=None):
    """
    Get an instance of the Self-Awareness Framework.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Instance of SelfAwarenessFramework or None if not available
    """
    if available_frameworks['self_awareness']:
        return self_awareness.SelfAwarenessFramework(config)
    else:
        logger.error("Self-Awareness Mechanics framework is not available")
        return None

def get_emotional_framework(config=None):
    """
    Get an instance of the Emotional Dimensionality Framework.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Instance of EmotionalDimensionalityFramework or None if not available
    """
    if available_frameworks['emotional_dimensionality']:
        return emotional_dimensionality.EmotionalDimensionalityFramework(config)
    else:
        logger.error("Emotional Dimensionality Framework is not available")
        return None

# Export public API
__all__ = [
    'self_awareness', 
    'emotional_dimensionality',
    'get_self_awareness_framework',
    'get_emotional_framework',
    'available_frameworks'
]

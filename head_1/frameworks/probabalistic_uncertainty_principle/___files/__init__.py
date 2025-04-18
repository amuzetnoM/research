"""
Probabilistic Uncertainty Principle (PUP) Framework

A framework for explicit uncertainty quantification, propagation,
and confidence-based execution in cognitive systems.
"""

__version__ = "0.1.0"

# Import main classes from core module
from .core import (
    # Main classes
    BeliefState,
    UncertaintyPropagator, 
    ConfidenceExecutor,
    
    # Utility functions
    combine_belief_states,
    calibrate_belief_state,
    create_ensemble_belief,
    variance_from_errors
)

# Define what's available when using "from pup import *"
__all__ = [
    'BeliefState',
    'UncertaintyPropagator',
    'ConfidenceExecutor',
    'combine_belief_states',
    'calibrate_belief_state',
    'create_ensemble_belief',
    'variance_from_errors'
]
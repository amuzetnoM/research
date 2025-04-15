"""
Utility functions for the PUP framework.

This module provides helper functions and utilities for working with 
probabilistic uncertainty.
"""

import numpy as np
from typing import Union, List, Dict, Any, Optional, Tuple, Callable
import math
import logging

from pup.core.belief_state import BeliefState

# Set up logging
logger = logging.getLogger(__name__)


def combine_belief_states(
    belief_states: List[BeliefState],
    weights: Optional[List[float]] = None
) -> BeliefState:
    """
    Combine multiple belief states into a single aggregated belief.
    
    Args:
        belief_states: List of belief states to combine
        weights: Optional weights for each belief state (must sum to 1.0)
                 If None, equal weights are assigned
    
    Returns:
        A new BeliefState representing the combined belief
    """
    if not belief_states:
        raise ValueError("Cannot combine empty list of belief states")
        
    # Check dimensions match
    mean_shape = belief_states[0].mean.shape
    if not all(bs.mean.shape == mean_shape for bs in belief_states):
        raise ValueError("All belief states must have the same shape")
    
    # Set default weights if none provided
    if weights is None:
        weights = [1.0 / len(belief_states)] * len(belief_states)
    else:
        # Normalize weights to sum to 1.0
        total = sum(weights)
        weights = [w / total for w in weights]
    
    if len(weights) != len(belief_states):
        raise ValueError("Number of weights must match number of belief states")
    
    # Weighted combination of means
    combined_mean = np.zeros_like(belief_states[0].mean)
    for bs, w in zip(belief_states, weights):
        combined_mean += w * bs.mean
    
    # Variance combination includes both within-belief variance and between-belief variance
    # This is based on the law of total variance
    combined_variance = np.zeros_like(belief_states[0].variance)
    
    # Add weighted within-belief variance
    for bs, w in zip(belief_states, weights):
        combined_variance += w * bs.variance
    
    # Add between-belief variance (if more than one belief state)
    if len(belief_states) > 1:
        for bs, w in zip(belief_states, weights):
            deviation = bs.mean - combined_mean
            combined_variance += w * deviation * deviation
    
    # Determine if the combined belief is epistemic or aleatoric
    # It's epistemic if any of the source beliefs are epistemic
    is_epistemic = any(bs.epistemic for bs in belief_states)
    
    # Merge metadata
    combined_metadata = {}
    for bs in belief_states:
        combined_metadata.update(bs.metadata)
    
    return BeliefState(
        mean=combined_mean,
        variance=combined_variance,
        epistemic=is_epistemic,
        metadata=combined_metadata
    )


def calibrate_belief_state(
    belief_state: BeliefState,
    calibration_data: Tuple[np.ndarray, np.ndarray]
) -> BeliefState:
    """
    Calibrate a belief state using empirical data.
    
    Args:
        belief_state: The belief state to calibrate
        calibration_data: Tuple of (predictions, actual_values) for calibration
    
    Returns:
        A calibrated BeliefState
    """
    predictions, actual_values = calibration_data
    
    # Calculate mean squared error between predictions and actual values
    mse = np.mean((predictions - actual_values) ** 2)
    
    # Scale variance based on empirical error
    scale_factor = mse / np.mean(belief_state.variance)
    calibrated_variance = belief_state.variance * scale_factor
    
    return BeliefState(
        mean=belief_state.mean,
        variance=calibrated_variance,
        epistemic=belief_state.epistemic,
        metadata={**belief_state.metadata, 'calibrated': True}
    )


def create_ensemble_belief(
    model_predictions: List[np.ndarray],
    model_weights: Optional[List[float]] = None
) -> BeliefState:
    """
    Create a belief state from ensemble model predictions.
    
    Args:
        model_predictions: List of predictions from different models
        model_weights: Optional weights for each model's prediction
    
    Returns:
        A BeliefState representing the ensemble belief
    """
    predictions = np.array(model_predictions)
    
    # Calculate weighted mean if weights provided
    if model_weights is not None:
        weights = np.array(model_weights)
        weights = weights / np.sum(weights)
        mean = np.sum(predictions * weights[:, np.newaxis], axis=0)
    else:
        mean = np.mean(predictions, axis=0)
    
    # Calculate variance across ensemble predictions
    variance = np.var(predictions, axis=0)
    
    return BeliefState(mean=mean, variance=variance, epistemic=True)


def variance_from_errors(
    errors: np.ndarray,
    window_size: int = 10,
    min_variance: float = 1e-6
) -> np.ndarray:
    """
    Estimate variance from a sequence of prediction errors.
    
    Args:
        errors: Array of prediction errors over time
        window_size: Number of recent errors to consider
        min_variance: Minimum variance to return
    
    Returns:
        Estimated variance
    """
    if len(errors) == 0:
        return np.array([min_variance])
    
    # Use the most recent errors up to window_size
    recent_errors = errors[-window_size:]
    
    # Calculate variance of recent errors
    if len(recent_errors) > 1:
        variance = np.var(recent_errors, axis=0)
    else:
        variance = np.ones_like(recent_errors) * min_variance
    
    # Ensure minimum variance
    variance = np.maximum(variance, min_variance)
    
    return variance
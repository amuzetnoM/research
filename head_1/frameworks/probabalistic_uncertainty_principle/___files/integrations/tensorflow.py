"""
TensorFlow integration for the PUP framework.

This module provides utilities for working with TensorFlow models
within the Probabilistic Uncertainty Principle framework.
"""

import numpy as np
from typing import Union, List, Dict, Any, Optional, Tuple, Callable
import logging

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

from ___files.core.belief_state import BeliefState
from ___files.core.uncertainty_propagator import UncertaintyPropagator

# Set up logging
logger = logging.getLogger(__name__)


def _check_tf_available():
    """Check if TensorFlow is available and raise an error if not."""
    if not TF_AVAILABLE:
        raise ImportError(
            "TensorFlow is not available. Please install TensorFlow to use this module."
        )


class MCDropoutModel:
    """
    Wrapper for TensorFlow models to enable Monte Carlo dropout at inference time.
    
    This class allows for multiple stochastic forward passes with dropout enabled
    to estimate epistemic uncertainty.
    """
    
    def __init__(self, model: tf.keras.Model, dropout_rate: Optional[float] = None):
        """
        Initialize MC Dropout wrapper.
        
        Args:
            model: TensorFlow model to wrap
            dropout_rate: Optional dropout rate to apply (or None to use existing rates)
        """
        _check_tf_available()
        self.model = model
        self.dropout_rate = dropout_rate
        
        # Set dropout rate if specified
        if dropout_rate is not None:
            self._set_dropout_rate(dropout_rate)
    
    def _set_dropout_rate(self, rate: float):
        """Set dropout rate for all dropout layers in the model."""
        for layer in self.model.layers:
            if isinstance(layer, tf.keras.layers.Dropout):
                layer.rate = rate
    
    def predict(self, x: Union[np.ndarray, tf.Tensor]) -> np.ndarray:
        """
        Make a single prediction with the model.
        
        Args:
            x: Input data
            
        Returns:
            Model prediction
        """
        return self.model(x, training=True).numpy()
    
    def predict_with_uncertainty(
        self, 
        x: Union[np.ndarray, tf.Tensor], 
        n_samples: int = 30
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions with uncertainty estimation.
        
        Args:
            x: Input data
            n_samples: Number of stochastic forward passes
            
        Returns:
            Tuple of (mean, variance) arrays
        """
        predictions = []
        
        for _ in range(n_samples):
            pred = self.model(x, training=True).numpy()
            predictions.append(pred)
        
        # Stack predictions
        predictions = np.stack(predictions, axis=0)
        
        # Calculate statistics
        mean = np.mean(predictions, axis=0)
        variance = np.var(predictions, axis=0)
        
        return mean, variance
    
    def predict_belief_state(
        self, 
        x: Union[np.ndarray, tf.Tensor],
        n_samples: int = 30
    ) -> BeliefState:
        """
        Generate a belief state from model predictions.
        
        Args:
            x: Input data
            n_samples: Number of stochastic forward passes
            
        Returns:
            BeliefState representing the prediction with uncertainty
        """
        mean, variance = self.predict_with_uncertainty(x, n_samples)
        
        return BeliefState(
            mean=mean,
            variance=variance,
            epistemic=True,
            metadata={'n_samples': n_samples}
        )


class ModelEnsemble:
    """
    Ensemble of TensorFlow models for uncertainty estimation.
    
    This class combines multiple models into an ensemble to estimate
    predictive uncertainty.
    """
    
    def __init__(self, models: List[tf.keras.Model]):
        """
        Initialize model ensemble.
        
        Args:
            models: List of TensorFlow models
        """
        _check_tf_available()
        self.models = models
    
    def predict(self, x: Union[np.ndarray, tf.Tensor]) -> np.ndarray:
        """
        Make a prediction using the ensemble's average.
        
        Args:
            x: Input data
            
        Returns:
            Ensemble's average prediction
        """
        predictions = []
        
        for model in self.models:
            pred = model(x, training=False).numpy()
            predictions.append(pred)
        
        # Stack and calculate mean
        predictions = np.stack(predictions, axis=0)
        mean = np.mean(predictions, axis=0)
        
        return mean
    
    def predict_with_uncertainty(
        self, 
        x: Union[np.ndarray, tf.Tensor]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions with uncertainty estimation.
        
        Args:
            x: Input data
            
        Returns:
            Tuple of (mean, variance) arrays
        """
        predictions = []
        
        for model in self.models:
            pred = model(x, training=False).numpy()
            predictions.append(pred)
        
        # Stack predictions
        predictions = np.stack(predictions, axis=0)
        
        # Calculate statistics
        mean = np.mean(predictions, axis=0)
        variance = np.var(predictions, axis=0)
        
        return mean, variance
    
    def predict_belief_state(
        self, 
        x: Union[np.ndarray, tf.Tensor]
    ) -> BeliefState:
        """
        Generate a belief state from model predictions.
        
        Args:
            x: Input data
            
        Returns:
            BeliefState representing the prediction with uncertainty
        """
        mean, variance = self.predict_with_uncertainty(x)
        
        return BeliefState(
            mean=mean,
            variance=variance,
            epistemic=True,
            metadata={'ensemble_size': len(self.models)}
        )


def create_dropout_model(
    base_model: tf.keras.Model,
    dropout_rate: float = 0.1, 
    return_variance: bool = True
) -> tf.keras.Model:
    """
    Create a Bayesian model from a regular model by adding dropout layers.
    
    Args:
        base_model: Base TensorFlow model
        dropout_rate: Dropout probability
        return_variance: Whether the model should output variance estimates
        
    Returns:
        Model with dropout for uncertainty estimation
    """
    _check_tf_available()
    
    # Get the input layer(s)
    inputs = base_model.inputs
    
    # Get the output tensor
    x = base_model.outputs[0]
    
    # Add dropout after the last layer
    x = tf.keras.layers.Dropout(dropout_rate)(x, training=True)
    
    if return_variance:
        # Create variance output
        variance = tf.keras.layers.Dense(
            x.shape[-1], activation='softplus', name='variance'
        )(x)
        
        # Create model with two outputs
        model = tf.keras.Model(inputs=inputs, outputs=[x, variance])
    else:
        model = tf.keras.Model(inputs=inputs, outputs=x)
    
    return model


def tf_to_belief_state(
    mean: Union[tf.Tensor, np.ndarray],
    variance: Optional[Union[tf.Tensor, np.ndarray]] = None,
    uncertainty_scale: float = 1.0,
    epistemic: bool = True
) -> BeliefState:
    """
    Convert TensorFlow tensors to a BeliefState.
    
    Args:
        mean: Mean tensor/array from TensorFlow model
        variance: Variance tensor/array (if None, uses a scaled identity variance)
        uncertainty_scale: Scale factor for variance when auto-generating
        epistemic: Whether this represents epistemic uncertainty
        
    Returns:
        BeliefState object
    """
    _check_tf_available()
    
    # Convert to numpy if needed
    if isinstance(mean, tf.Tensor):
        mean_np = mean.numpy()
    else:
        mean_np = mean
    
    # Handle variance
    if variance is not None:
        if isinstance(variance, tf.Tensor):
            variance_np = variance.numpy()
        else:
            variance_np = variance
    else:
        # Create a minimal variance scaled by uncertainty_scale
        variance_np = np.ones_like(mean_np) * 1e-6 * uncertainty_scale
    
    return BeliefState(
        mean=mean_np,
        variance=variance_np,
        epistemic=epistemic
    )


def belief_state_to_tf(
    belief_state: BeliefState
) -> Tuple[tf.Tensor, tf.Tensor]:
    """
    Convert a BeliefState to TensorFlow tensors.
    
    Args:
        belief_state: BeliefState to convert
        
    Returns:
        Tuple of (mean_tensor, variance_tensor)
    """
    _check_tf_available()
    
    mean_tensor = tf.convert_to_tensor(belief_state.mean, dtype=tf.float32)
    variance_tensor = tf.convert_to_tensor(belief_state.variance, dtype=tf.float32)
    
    return mean_tensor, variance_tensor
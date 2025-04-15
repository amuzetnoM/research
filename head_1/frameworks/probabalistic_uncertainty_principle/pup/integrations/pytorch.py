"""
PyTorch integration for the PUP framework.

This module provides utilities for working with PyTorch models
within the Probabilistic Uncertainty Principle framework.
"""

import numpy as np
from typing import Union, List, Dict, Any, Optional, Tuple, Callable
import logging

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from pup.core.belief_state import BeliefState
from pup.core.uncertainty_propagator import UncertaintyPropagator

# Set up logging
logger = logging.getLogger(__name__)


def _check_torch_available():
    """Check if PyTorch is available and raise an error if not."""
    if not TORCH_AVAILABLE:
        raise ImportError(
            "PyTorch is not available. Please install PyTorch to use this module."
        )


class MonteCarloDropout(nn.Module):
    """
    Module wrapper that enables Monte Carlo dropout at inference time.
    
    This wrapper ensures that dropout remains active during inference,
    allowing for epistemic uncertainty estimation through multiple forward passes.
    """
    
    def __init__(self, module: nn.Module, dropout_rate: float = 0.1):
        """
        Initialize Monte Carlo dropout wrapper.
        
        Args:
            module: PyTorch module to wrap
            dropout_rate: Dropout probability to apply
        """
        _check_torch_available()
        super().__init__()
        self.module = module
        self.dropout_rate = dropout_rate
        
        # Add dropout layer if not already present
        self._ensure_dropout_layers()
    
    def _ensure_dropout_layers(self):
        """Make sure the model has dropout layers with correct rates."""
        for name, module in self.module.named_modules():
            if isinstance(module, nn.Dropout):
                # Set existing dropout layers to our rate
                module.p = self.dropout_rate
    
    def forward(self, x):
        """Forward pass with dropout enabled."""
        self.module.train()  # Set to training mode to enable dropout
        return self.module(x)
    
    def predict_with_uncertainty(
        self, 
        x: torch.Tensor, 
        n_samples: int = 30
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Make predictions with uncertainty estimation.
        
        Args:
            x: Input tensor
            n_samples: Number of MC Dropout forward passes
            
        Returns:
            Tuple of (mean, variance) tensors
        """
        predictions = []
        with torch.no_grad():
            for _ in range(n_samples):
                predictions.append(self.forward(x))
                
        # Stack predictions along a new dimension
        predictions = torch.stack(predictions, dim=0)
        
        # Calculate mean and variance
        mean = torch.mean(predictions, dim=0)
        variance = torch.var(predictions, dim=0)
        
        return mean, variance
    
    def predict_belief_state(
        self, 
        x: torch.Tensor,
        n_samples: int = 30
    ) -> BeliefState:
        """
        Generate a belief state from model predictions.
        
        Args:
            x: Input tensor
            n_samples: Number of forward passes
            
        Returns:
            BeliefState representing the prediction with uncertainty
        """
        mean, variance = self.predict_with_uncertainty(x, n_samples)
        
        # Convert to numpy arrays for belief state
        mean_np = mean.cpu().numpy()
        variance_np = variance.cpu().numpy()
        
        return BeliefState(
            mean=mean_np,
            variance=variance_np,
            epistemic=True,
            metadata={'n_samples': n_samples}
        )


class EnsembleModel(nn.Module):
    """
    Ensemble of PyTorch models for uncertainty estimation.
    
    This class combines multiple models into an ensemble, allowing
    for uncertainty estimation through prediction variance.
    """
    
    def __init__(self, models: List[nn.Module], device: Optional[torch.device] = None):
        """
        Initialize model ensemble.
        
        Args:
            models: List of PyTorch models
            device: Device to run models on (if None, uses current device)
        """
        _check_torch_available()
        super().__init__()
        self.models = nn.ModuleList(models)
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.models.to(self.device)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass returns average prediction from all models.
        
        Args:
            x: Input tensor
            
        Returns:
            Mean prediction across all models
        """
        outputs = []
        x = x.to(self.device)
        
        with torch.no_grad():
            for model in self.models:
                model.eval()
                outputs.append(model(x))
        
        # Stack and average predictions
        outputs = torch.stack(outputs, dim=0)
        return torch.mean(outputs, dim=0)
    
    def predict_with_uncertainty(
        self, 
        x: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Make predictions with uncertainty estimation.
        
        Args:
            x: Input tensor
            
        Returns:
            Tuple of (mean, variance) tensors
        """
        outputs = []
        x = x.to(self.device)
        
        with torch.no_grad():
            for model in self.models:
                model.eval()
                outputs.append(model(x))
        
        # Stack predictions along model dimension
        outputs = torch.stack(outputs, dim=0)
        
        # Calculate mean and variance
        mean = torch.mean(outputs, dim=0)
        variance = torch.var(outputs, dim=0)
        
        return mean, variance
    
    def predict_belief_state(self, x: torch.Tensor) -> BeliefState:
        """
        Generate a belief state from model predictions.
        
        Args:
            x: Input tensor
            
        Returns:
            BeliefState representing the prediction with uncertainty
        """
        mean, variance = self.predict_with_uncertainty(x)
        
        # Convert to numpy arrays for belief state
        mean_np = mean.cpu().numpy()
        variance_np = variance.cpu().numpy()
        
        return BeliefState(
            mean=mean_np,
            variance=variance_np,
            epistemic=True,
            metadata={'ensemble_size': len(self.models)}
        )


def torch_to_belief_state(
    mean: torch.Tensor,
    variance: Optional[torch.Tensor] = None,
    uncertainty_scale: float = 1.0,
    epistemic: bool = True
) -> BeliefState:
    """
    Convert PyTorch tensors to a BeliefState.
    
    Args:
        mean: Mean tensor from PyTorch model
        variance: Variance tensor (if None, uses a scaled identity variance)
        uncertainty_scale: Scale factor for variance when auto-generating
        epistemic: Whether this represents epistemic uncertainty
        
    Returns:
        BeliefState object
    """
    _check_torch_available()
    
    # Convert mean to numpy
    mean_np = mean.detach().cpu().numpy()
    
    # Convert or generate variance
    if variance is not None:
        variance_np = variance.detach().cpu().numpy()
    else:
        # Create a minimal variance scaled by uncertainty_scale
        variance_np = np.ones_like(mean_np) * 1e-6 * uncertainty_scale
    
    return BeliefState(
        mean=mean_np,
        variance=variance_np,
        epistemic=epistemic
    )


def belief_state_to_torch(
    belief_state: BeliefState,
    device: Optional[torch.device] = None
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Convert a BeliefState to PyTorch tensors.
    
    Args:
        belief_state: BeliefState to convert
        device: Target device for the tensors
        
    Returns:
        Tuple of (mean_tensor, variance_tensor)
    """
    _check_torch_available()
    
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    mean_tensor = torch.tensor(belief_state.mean, device=device)
    variance_tensor = torch.tensor(belief_state.variance, device=device)
    
    return mean_tensor, variance_tensor
"""
BeliefState module for representing probabilistic beliefs with uncertainty.

This module provides the BeliefState class which encapsulates a probability
distribution over a variable or state.
"""

import numpy as np
from typing import Union, Tuple, List, Dict, Any, Optional
import math


class BeliefState:
    """
    Represents a belief about a state variable with associated uncertainty.
    
    A BeliefState captures both the expected value (mean) and the uncertainty
    (variance) about a variable or state. It can represent both epistemic 
    uncertainty (lack of knowledge) and aleatoric uncertainty (inherent 
    randomness or noise).
    
    Attributes:
        mean: The expected value of the state variable
        variance: The uncertainty about the mean value
        epistemic: Whether this represents epistemic (knowledge-based) uncertainty
        metadata: Optional dictionary for additional information about the belief
    """
    
    def __init__(
        self, 
        mean: Union[float, List[float], np.ndarray],
        variance: Union[float, List[float], np.ndarray],
        epistemic: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a belief state with a mean and variance.
        
        Args:
            mean: Expected value(s) of the state variable(s)
            variance: Uncertainty about the mean value(s)
            epistemic: If True, represents knowledge-based uncertainty that can
                       be reduced with more information. If False, represents
                       aleatoric uncertainty (inherent randomness)
            metadata: Additional information about this belief state
        """
        self.mean = np.atleast_1d(np.array(mean, dtype=np.float64))
        self.variance = np.atleast_1d(np.array(variance, dtype=np.float64))
        
        # Ensure variance is non-negative
        self.variance = np.maximum(self.variance, 1e-10)
        
        # Validate shapes match
        if self.mean.shape != self.variance.shape:
            raise ValueError("Mean and variance must have the same shape")
            
        self.epistemic = epistemic
        self.metadata = metadata or {}
    
    def confidence(self) -> Union[float, np.ndarray]:
        """
        Calculate the confidence level of this belief state.
        
        Returns:
            A value between 0 and 1 representing confidence level.
            Higher values indicate greater confidence.
        """
        # Simple inverse relationship with variance
        # Alternative approaches might use entropy or other metrics
        return 1.0 / (1.0 + self.variance)
    
    def update_with_evidence(
        self, 
        new_mean: Union[float, List[float], np.ndarray],
        new_variance: Union[float, List[float], np.ndarray],
        weight: float = 0.5
    ) -> 'BeliefState':
        """
        Update this belief state with new evidence using Bayesian updating.
        
        Args:
            new_mean: Mean value of the new evidence
            new_variance: Variance of the new evidence
            weight: Weight to assign to the new evidence (0-1)
                   Higher values give more importance to the new evidence
        
        Returns:
            A new BeliefState representing the updated belief
        """
        new_mean = np.atleast_1d(np.array(new_mean, dtype=np.float64))
        new_variance = np.atleast_1d(np.array(new_variance, dtype=np.float64))
        
        # Bayesian update formula for weighted combination
        updated_variance = 1.0 / ((1.0 / self.variance) + (weight / new_variance))
        updated_mean = (
            self.mean / self.variance + weight * new_mean / new_variance
        ) * updated_variance
        
        return BeliefState(
            mean=updated_mean,
            variance=updated_variance,
            epistemic=self.epistemic,
            metadata=self.metadata.copy()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this belief state to a dictionary representation.
        
        Returns:
            Dictionary representation of the belief state
        """
        return {
            "mean": self.mean.tolist(),
            "variance": self.variance.tolist(),
            "confidence": self.confidence().tolist() if isinstance(self.confidence(), np.ndarray) else self.confidence(),
            "epistemic": self.epistemic,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BeliefState':
        """
        Create a BeliefState from a dictionary representation.
        
        Args:
            data: Dictionary containing belief state data
            
        Returns:
            A new BeliefState object
        """
        return cls(
            mean=data["mean"],
            variance=data["variance"],
            epistemic=data["epistemic"],
            metadata=data.get("metadata", {})
        )
    
    def __repr__(self) -> str:
        """String representation of the belief state."""
        type_str = "Epistemic" if self.epistemic else "Aleatoric"
        conf = self.confidence()
        conf_str = f"{conf:.2f}" if isinstance(conf, float) else f"{np.mean(conf):.2f}"
        
        return f"<{type_str} BeliefState mean={self.mean}, variance={self.variance}, confidence={conf_str}>"
    
    def __eq__(self, other: object) -> bool:
        """Check if two belief states are equal."""
        if not isinstance(other, BeliefState):
            return False
        
        return (
            np.array_equal(self.mean, other.mean) and
            np.array_equal(self.variance, other.variance) and
            self.epistemic == other.epistemic
        )
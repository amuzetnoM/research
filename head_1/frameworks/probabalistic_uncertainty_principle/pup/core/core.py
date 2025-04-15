"""
Core module for the Probabilistic Uncertainty Principle (PUP) framework.

This module contains the fundamental components that enable uncertainty 
quantification, propagation, and confidence-based action execution.
"""

import numpy as np
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

# Type variables for generic types
T = TypeVar('T')  # Return type for action functions
U = TypeVar('U')  # Return type for fallback functions

class BeliefState:
    """
    Represents a probabilistic belief with explicit uncertainty.
    
    A BeliefState encapsulates a probability distribution over a variable or state,
    capturing both the expected value and the associated uncertainty.
    """
    
    def __init__(
        self, 
        mean: Union[float, List[float], np.ndarray],
        variance: Union[float, List[float], np.ndarray],
        epistemic: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a belief state.
        
        Args:
            mean: Expected value(s) of the state variable(s)
            variance: Uncertainty about the mean value(s)
            epistemic: If True, represents knowledge-based uncertainty that can be
                      reduced with more information. If False, represents aleatoric
                      uncertainty (inherent randomness)
            metadata: Additional information about this belief state
        """
        # Convert inputs to numpy arrays
        self.mean = np.array(mean)
        self.variance = np.array(variance)
        self.epistemic = epistemic
        self.metadata = metadata or {}
        
        # Calculate confidence based on uncertainty
        self._confidence = self._compute_confidence()
    
    def _compute_confidence(self) -> Union[float, np.ndarray]:
        """
        Calculate confidence level based on variance.
        
        Returns:
            Confidence level (0-1)
        """
        # Simple inverse function of variance
        # Higher variance = lower confidence
        return 1.0 / (1.0 + self.variance)
    
    @property
    def confidence(self) -> Union[float, np.ndarray]:
        """
        Get the confidence level of this belief state.
        
        Returns:
            A value between 0 and 1 representing confidence level
        """
        return self._confidence
    
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
        # Convert inputs to numpy arrays
        new_mean = np.array(new_mean)
        new_variance = np.array(new_variance)
        
        # Ensure weight is between 0 and 1
        weight = max(0.0, min(1.0, weight))
        
        # Bayesian update
        updated_mean = (1 - weight) * self.mean + weight * new_mean
        
        # Variance update incorporates both old and new variance
        # as well as the distance between means (disagreement)
        updated_variance = (1 - weight) * self.variance + weight * new_variance
        
        # Add a term for the disagreement between means
        mean_disagreement = (self.mean - new_mean) ** 2
        updated_variance += weight * (1 - weight) * mean_disagreement
        
        # Create a new belief state with the updated values
        return BeliefState(
            mean=updated_mean,
            variance=updated_variance,
            epistemic=self.epistemic,
            metadata={**self.metadata, "updated": True}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this belief state to a dictionary representation.
        
        Returns:
            Dictionary representation of the belief state
        """
        return {
            'mean': self.mean.tolist() if isinstance(self.mean, np.ndarray) else self.mean,
            'variance': self.variance.tolist() if isinstance(self.variance, np.ndarray) else self.variance,
            'epistemic': self.epistemic,
            'confidence': self._confidence.tolist() if isinstance(self._confidence, np.ndarray) else self._confidence,
            'metadata': self.metadata
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
            mean=data['mean'],
            variance=data['variance'],
            epistemic=data['epistemic'],
            metadata=data.get('metadata')
        )
    
    def __repr__(self) -> str:
        """String representation of the belief state."""
        type_str = "Epistemic" if self.epistemic else "Aleatoric"
        return f"<{type_str} BeliefState mean={self.mean}, variance={self.variance}, confidence={self._confidence}>"


class UncertaintyPropagator:
    """
    Propagates uncertainty through transformations of belief states.
    
    This class transforms belief states through arbitrary functions while
    correctly tracking and updating uncertainty.
    """
    
    def __init__(
        self,
        samples: int = 100,
        parallel: bool = False,
        n_jobs: Optional[int] = None
    ):
        """
        Initialize an uncertainty propagator.
        
        Args:
            samples: Number of Monte Carlo samples to use for propagation
            parallel: Whether to use parallel processing for Monte Carlo sampling
            n_jobs: Number of parallel processes to use (defaults to CPU count if None)
        """
        self.samples = samples
        self.parallel = parallel
        self.n_jobs = n_jobs
        
        # Set up parallel processing if requested
        if self.parallel:
            try:
                import joblib
                self._n_jobs = joblib.cpu_count() if n_jobs is None else n_jobs
            except ImportError:
                self.parallel = False
                self._n_jobs = None
    
    def propagate(
        self,
        belief_state: BeliefState,
        transformation_fn: Callable
    ) -> BeliefState:
        """
        Propagate a belief state through a transformation function.
        
        Args:
            belief_state: The initial belief state
            transformation_fn: Function to apply to the belief state 
                             (should accept inputs with the same shape as belief_state.mean)
                             
        Returns:
            A new BeliefState representing the transformed belief
        """
        # Generate Monte Carlo samples from the input distribution
        samples = np.random.normal(
            loc=belief_state.mean,
            scale=np.sqrt(belief_state.variance),
            size=(self.samples,) + belief_state.mean.shape
        )
        
        # Apply the transformation to each sample
        if self.parallel:
            import joblib
            transformed_samples = joblib.Parallel(n_jobs=self._n_jobs)(
                joblib.delayed(transformation_fn)(sample) for sample in samples
            )
            transformed_samples = np.array(transformed_samples)
        else:
            transformed_samples = np.array([transformation_fn(sample) for sample in samples])
        
        # Calculate the mean and variance of the transformed samples
        transformed_mean = np.mean(transformed_samples, axis=0)
        transformed_variance = np.var(transformed_samples, axis=0)
        
        # Create a new belief state with the transformed values
        return BeliefState(
            mean=transformed_mean,
            variance=transformed_variance,
            epistemic=belief_state.epistemic,
            metadata={**belief_state.metadata, "transformed": True}
        )
    
    def propagate_batch(
        self,
        belief_states: List[BeliefState],
        transformation_fn: Callable
    ) -> List[BeliefState]:
        """
        Propagate a batch of belief states through a transformation.
        
        Args:
            belief_states: List of belief states to transform
            transformation_fn: The transformation function
            
        Returns:
            List of transformed belief states
        """
        return [self.propagate(belief, transformation_fn) for belief in belief_states]
    
    def propagate_batch_parallel(
        self,
        belief_states: List[BeliefState],
        transformation_fn: Callable
    ) -> List[BeliefState]:
        """
        Propagate a batch of belief states through a transformation in parallel.
        
        Args:
            belief_states: List of belief states to transform
            transformation_fn: The transformation function
            
        Returns:
            List of transformed belief states
        """
        if not self.parallel:
            return self.propagate_batch(belief_states, transformation_fn)
        
        import joblib
        return joblib.Parallel(n_jobs=self._n_jobs)(
            joblib.delayed(self.propagate)(belief, transformation_fn) 
            for belief in belief_states
        )


class ConfidenceExecutor:
    """
    Gates actions based on confidence thresholds.
    
    This class executes functions only when belief confidence exceeds a threshold,
    which can be static or adapted based on context.
    """
    
    def __init__(
        self,
        threshold: float = 0.9,
        fallback_fn: Optional[Callable[[BeliefState], U]] = None,
        adaptive: bool = False,
        min_threshold: float = 0.1,
        max_threshold: float = 0.99
    ):
        """
        Initialize a confidence executor.
        
        Args:
            threshold: Confidence threshold for executing actions (0.0-1.0)
            fallback_fn: Function to call when confidence is below threshold
            adaptive: Whether to use adaptive thresholds based on context
            min_threshold: Minimum allowed threshold if using adaptive mode
            max_threshold: Maximum allowed threshold if using adaptive mode
        """
        self.base_threshold = threshold
        self.fallback_fn = fallback_fn
        self.adaptive = adaptive
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        
        # Statistics
        self.execution_count = 0
        self.fallback_count = 0
    
    def _get_adaptive_threshold(self, context: Dict[str, Any]) -> float:
        """
        Calculate an adaptive threshold based on context.
        
        Args:
            context: Dictionary with context information
            
        Returns:
            Adjusted threshold
        """
        # Base threshold
        threshold = self.base_threshold
        
        # Adjust based on risk level (higher risk = higher threshold)
        if 'risk_level' in context:
            risk_level = float(context['risk_level'])
            threshold += 0.2 * risk_level
        
        # Adjust based on criticality (higher criticality = higher threshold)
        if 'criticality' in context:
            criticality = float(context['criticality'])
            threshold += 0.1 * criticality
        
        # Ensure threshold is within bounds
        threshold = max(self.min_threshold, min(self.max_threshold, threshold))
        
        return threshold
    
    def execute(
        self,
        belief_state: BeliefState,
        action_fn: Callable[[Any], T],
        context: Optional[Dict[str, Any]] = None
    ) -> Union[T, U]:
        """
        Execute an action if belief confidence exceeds threshold.
        
        Args:
            belief_state: The belief state to check confidence against
            action_fn: Function to execute if confidence is sufficient
            context: Optional context information for adaptive thresholds
            
        Returns:
            Either the result of action_fn or fallback_fn
        """
        # Get the appropriate threshold
        if self.adaptive and context:
            threshold = self._get_adaptive_threshold(context)
        else:
            threshold = self.base_threshold
        
        # Get confidence (handle both scalar and array confidence)
        confidence = belief_state.confidence
        if isinstance(confidence, np.ndarray):
            # For array confidence, use the minimum confidence
            confidence_value = float(np.min(confidence))
        else:
            confidence_value = float(confidence)
        
        # Check if confidence exceeds threshold
        if confidence_value >= threshold:
            self.execution_count += 1
            return action_fn(belief_state.mean)
        else:
            self.fallback_count += 1
            if self.fallback_fn:
                return self.fallback_fn(belief_state)
            else:
                return {'action': 'deferred', 'confidence': confidence_value, 'threshold': threshold}
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get statistics about execution attempts.
        
        Returns:
            Dictionary with execution statistics
        """
        total = self.execution_count + self.fallback_count
        
        if total == 0:
            execution_rate = 0.0
            fallback_rate = 0.0
        else:
            execution_rate = self.execution_count / total
            fallback_rate = self.fallback_count / total
        
        return {
            'execution_count': self.execution_count,
            'fallback_count': self.fallback_count,
            'total_count': total,
            'execution_rate': execution_rate,
            'fallback_rate': fallback_rate
        }
    
    def adjust_threshold(self, adjustment: float) -> None:
        """
        Manually adjust the base threshold.
        
        Args:
            adjustment: Amount to adjust the threshold by (positive or negative)
        """
        self.base_threshold = max(self.min_threshold, 
                                 min(self.max_threshold, 
                                    self.base_threshold + adjustment))


# Utility functions

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
        raise ValueError("No belief states provided")
    
    n = len(belief_states)
    
    # Use equal weights if none provided
    if weights is None:
        weights = [1.0 / n] * n
    
    # Normalize weights to sum to 1
    if abs(sum(weights) - 1.0) > 1e-6:
        weights = [w / sum(weights) for w in weights]
    
    # Extract means and variances as arrays
    means = np.array([bs.mean for bs in belief_states])
    variances = np.array([bs.variance for bs in belief_states])
    weights_array = np.array(weights).reshape(-1, 1)
    
    # Calculate combined mean (weighted average)
    combined_mean = np.sum(means * weights_array, axis=0)
    
    # Calculate combined variance
    # 1. The weighted average of variances (within-belief uncertainty)
    within_variance = np.sum(variances * weights_array, axis=0)
    
    # 2. Add the variance from disagreement between means (between-belief uncertainty)
    mean_diffs = means - combined_mean
    between_variance = np.sum(weights_array * (mean_diffs ** 2), axis=0)
    
    combined_variance = within_variance + between_variance
    
    # Determine if the combined belief is epistemic
    # If any source belief is epistemic, the combined one is too
    is_epistemic = any(bs.epistemic for bs in belief_states)
    
    # Combine metadata
    combined_metadata = {
        "source": "combined_belief_states",
        "n_beliefs": n,
        "weights": weights,
        "source_confidence": [float(bs.confidence) for bs in belief_states]
    }
    for i, bs in enumerate(belief_states):
        if bs.metadata:
            for key, value in bs.metadata.items():
                combined_metadata[f"source_{i}_{key}"] = value
    
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
    
    # Calculate empirical error
    errors = predictions - actual_values
    empirical_variance = np.var(errors)
    
    # Calculate calibration factor
    # If model is underconfident (variance > empirical_variance), 
    # factor < 1, reducing variance
    # If model is overconfident (variance < empirical_variance), 
    # factor > 1, increasing variance
    calibration_factor = empirical_variance / (belief_state.variance + 1e-8)
    
    # Create a calibrated belief state
    return BeliefState(
        mean=belief_state.mean,
        variance=belief_state.variance * calibration_factor,
        epistemic=belief_state.epistemic,
        metadata={
            **belief_state.metadata,
            "calibrated": True,
            "calibration_factor": float(calibration_factor)
        }
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
    # Convert to numpy array
    predictions = np.array(model_predictions)
    
    # Calculate ensemble mean (possibly weighted)
    if model_weights is not None:
        weights = np.array(model_weights).reshape(-1, 1)
        # Normalize weights to sum to 1
        weights = weights / np.sum(weights)
        ensemble_mean = np.sum(predictions * weights, axis=0)
    else:
        ensemble_mean = np.mean(predictions, axis=0)
    
    # Calculate ensemble variance (disagreement between models)
    ensemble_variance = np.var(predictions, axis=0)
    
    return BeliefState(
        mean=ensemble_mean,
        variance=ensemble_variance,
        epistemic=True,  # Ensemble disagreement is epistemic
        metadata={
            "source": "ensemble",
            "n_models": len(model_predictions)
        }
    )


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
    # Ensure errors is a numpy array
    errors = np.array(errors)
    
    # Reshape if needed
    if len(errors.shape) == 1:
        errors = errors.reshape(-1, 1)
    
    # Calculate rolling variance with specified window
    n = len(errors)
    variances = []
    
    for i in range(n):
        # Get window of errors (use smaller window at the beginning)
        start_idx = max(0, i - window_size + 1)
        window = errors[start_idx:i+1]
        
        # Calculate variance of window
        var = np.var(window, axis=0)
        variances.append(var)
    
    # Ensure minimum variance
    return np.maximum(np.array(variances), min_variance)
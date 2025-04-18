"""
Confidence Executor module for gating actions based on belief confidence.

This module provides tools to execute actions only when the confidence level
of a belief state exceeds a specified threshold.
"""

import numpy as np
from typing import Callable, Union, Any, Optional, List, Dict, TypeVar, Generic
import logging

from ___files.core.belief_state import BeliefState

# Type variable for the action result
T = TypeVar('T')
U = TypeVar('U')

# Set up logging
logger = logging.getLogger(__name__)


class ConfidenceError(Exception):
    """Exception raised when confidence is below threshold."""
    pass


def defer_action(
    belief_state: BeliefState, 
    reason: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized response for deferred actions.
    
    Args:
        belief_state: The belief state that didn't meet the confidence threshold
        reason: Optional explanation for the deferral
        metadata: Additional information to include in the response
        
    Returns:
        A dictionary describing the deferral
    """
    meta = metadata or {}
    if reason:
        meta['reason'] = reason
        
    return {
        'action': 'deferred',
        'confidence': float(np.mean(belief_state.confidence())),
        'mean': belief_state.mean.tolist(),
        'variance': belief_state.variance.tolist(),
        'metadata': meta
    }


class ConfidenceExecutor(Generic[T, U]):
    """
    Executes actions only when belief confidence exceeds a threshold.
    
    This class provides a mechanism to gate actions based on the confidence
    level of a belief state, helping systems avoid taking actions when
    uncertainty is too high.
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
        Initialize a ConfidenceExecutor.
        
        Args:
            threshold: Confidence threshold for executing actions (0.0-1.0)
            fallback_fn: Function to call when confidence is below threshold
            adaptive: Whether to use adaptive thresholds based on context
            min_threshold: Minimum allowed threshold if using adaptive mode
            max_threshold: Maximum allowed threshold if using adaptive mode
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
            
        if not 0.0 <= min_threshold <= max_threshold <= 1.0:
            raise ValueError("Invalid min/max threshold range")
            
        self.threshold = threshold
        self.fallback_fn = fallback_fn or defer_action
        self.adaptive = adaptive
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self.execution_history = []
    
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
        context = context or {}
        threshold = self._get_threshold(context)
        confidence = np.mean(belief_state.confidence())
        
        # Store execution attempt in history
        self._record_execution_attempt(belief_state, confidence, threshold, context)
        
        # Check if confidence meets the threshold
        if confidence >= threshold:
            try:
                result = action_fn(belief_state.mean)
                return result
            except Exception as e:
                logger.error(f"Action execution failed: {e}")
                return self.fallback_fn(belief_state, reason=f"Action failed: {str(e)}")
        else:
            return self.fallback_fn(belief_state, reason="Confidence below threshold")
    
    def _get_threshold(self, context: Dict[str, Any]) -> float:
        """
        Determine the threshold to use based on context.
        
        Args:
            context: Context information for adaptive thresholds
            
        Returns:
            The threshold value to use
        """
        if not self.adaptive:
            return self.threshold
            
        # Adaptive threshold logic based on context
        # Some examples of factors that might influence the threshold:
        risk_level = context.get('risk_level', 0.5)  # Higher risk requires higher confidence
        criticality = context.get('criticality', 0.5)  # More critical actions require higher confidence
        
        # Simple weighted average for demonstration
        adaptive_factors = [
            self.threshold,  # Base threshold
            min(1.0, risk_level + 0.2),  # Adjust threshold based on risk
            min(1.0, criticality + 0.1)  # Adjust threshold based on criticality
        ]
        
        # Calculate adjusted threshold
        adjusted = sum(adaptive_factors) / len(adaptive_factors)
        
        # Ensure it stays within allowed range
        return max(self.min_threshold, min(self.max_threshold, adjusted))
    
    def _record_execution_attempt(
        self,
        belief_state: BeliefState,
        confidence: float,
        threshold: float,
        context: Dict[str, Any]
    ):
        """
        Record an execution attempt in the history.
        
        Args:
            belief_state: The belief state being evaluated
            confidence: The calculated confidence value
            threshold: The threshold being used
            context: The context for this execution attempt
        """
        # Limit history size to prevent memory issues
        if len(self.execution_history) >= 1000:
            self.execution_history = self.execution_history[-999:]
            
        entry = {
            'timestamp': np.datetime64('now'),
            'confidence': confidence,
            'threshold': threshold,
            'executed': confidence >= threshold,
            'context': context
        }
        
        self.execution_history.append(entry)
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get statistics about execution attempts.
        
        Returns:
            Dictionary with execution statistics
        """
        if not self.execution_history:
            return {
                'total_attempts': 0,
                'executed_ratio': 0.0,
                'avg_confidence': 0.0
            }
            
        executed = [e for e in self.execution_history if e['executed']]
        
        return {
            'total_attempts': len(self.execution_history),
            'executed_count': len(executed),
            'executed_ratio': len(executed) / len(self.execution_history),
            'avg_confidence': np.mean([e['confidence'] for e in self.execution_history]),
            'avg_threshold': np.mean([e['threshold'] for e in self.execution_history])
        }
    
    def adjust_threshold(self, adjustment: float):
        """
        Manually adjust the base threshold.
        
        Args:
            adjustment: Amount to adjust the threshold by (positive or negative)
        """
        new_threshold = self.threshold + adjustment
        self.threshold = max(self.min_threshold, min(self.max_threshold, new_threshold))
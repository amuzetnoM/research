"""
UncertaintyPropagator module for propagating belief states through transformations.

This module provides methods to transform belief states through functions
while properly tracking and updating uncertainty.
"""

import numpy as np
from typing import Callable, Union, List, Dict, Any, Optional, Tuple
import math
from multiprocessing import Pool, cpu_count
from functools import partial

from ___files.core.belief_state import BeliefState


class UncertaintyPropagator:
    """
    Propagates uncertainty through transformations applied to belief states.
    
    This class implements methods to apply transformations to belief states
    while properly accounting for how uncertainty changes through the
    transformation.
    """
    
    def __init__(self, samples: int = 100, parallel: bool = False, n_jobs: Optional[int] = None):
        """
        Initialize an UncertaintyPropagator.
        
        Args:
            samples: Number of Monte Carlo samples to use for propagation
            parallel: Whether to use parallel processing for Monte Carlo sampling
            n_jobs: Number of parallel processes to use (defaults to CPU count if None)
        """
        self.samples = max(10, samples)  # Ensure a minimum number of samples
        self.parallel = parallel
        self.n_jobs = n_jobs if n_jobs is not None else max(1, cpu_count() - 1)
    
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
                               Should accept inputs with the same shape as belief_state.mean
        
        Returns:
            A new BeliefState representing the transformed belief
        """
        # For scalar or simple functions, we can check if analytical solutions exist
        if self._has_analytical_solution(transformation_fn):
            return self._analytical_propagation(belief_state, transformation_fn)
        
        # Otherwise, use Monte Carlo sampling
        return self._monte_carlo_propagation(belief_state, transformation_fn)
    
    def _has_analytical_solution(self, fn: Callable) -> bool:
        """
        Check if analytical solution exists for this function.
        
        Currently only identifies simple functions like linear transformations.
        
        Args:
            fn: The transformation function
            
        Returns:
            True if an analytical solution is available, False otherwise
        """
        # This is a simple placeholder - would need more sophisticated analysis
        # of the function to determine if analytical solutions exist
        return False
    
    def _analytical_propagation(
        self, 
        belief_state: BeliefState,
        transformation_fn: Callable
    ) -> BeliefState:
        """
        Apply analytical propagation for functions with known solutions.
        
        Args:
            belief_state: The initial belief state
            transformation_fn: The transformation function
            
        Returns:
            Transformed belief state
        """
        # Placeholder for analytical solutions to common transformations
        # Example: For linear transformations y = ax + b:
        # transformed_mean = a * mean + b
        # transformed_variance = a^2 * variance
        
        # For now, fall back to Monte Carlo
        return self._monte_carlo_propagation(belief_state, transformation_fn)
    
    def _monte_carlo_propagation(
        self, 
        belief_state: BeliefState,
        transformation_fn: Callable
    ) -> BeliefState:
        """
        Propagate uncertainty using Monte Carlo sampling.
        
        Args:
            belief_state: The initial belief state
            transformation_fn: The transformation function
            
        Returns:
            Transformed belief state
        """
        # Generate samples from the belief state distribution
        samples = np.random.normal(
            loc=belief_state.mean,
            scale=np.sqrt(belief_state.variance),
            size=(self.samples,) + belief_state.mean.shape
        )
        
        # Apply transformation to samples
        if self.parallel and self.samples > 20:
            transformed_samples = self._parallel_transform(samples, transformation_fn)
        else:
            transformed_samples = np.array([transformation_fn(x) for x in samples])
        
        # Calculate statistics of transformed samples
        transformed_mean = np.mean(transformed_samples, axis=0)
        transformed_variance = np.var(transformed_samples, axis=0)
        
        # Create new belief state with propagated uncertainty
        return BeliefState(
            mean=transformed_mean,
            variance=transformed_variance,
            epistemic=belief_state.epistemic,
            metadata=belief_state.metadata.copy()
        )
    
    def _parallel_transform(
        self, 
        samples: np.ndarray,
        transformation_fn: Callable
    ) -> np.ndarray:
        """
        Apply transformation to samples in parallel.
        
        Args:
            samples: Array of sampled points
            transformation_fn: The transformation function
            
        Returns:
            Array of transformed samples
        """
        with Pool(processes=self.n_jobs) as pool:
            # Process in batches for better efficiency with shared memory
            results = pool.map(transformation_fn, samples)
        
        return np.array(results)
    
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
        return [self.propagate(bs, transformation_fn) for bs in belief_states]
    
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
        with Pool(processes=self.n_jobs) as pool:
            # Use partial to create a function that only takes a belief state
            propagate_fn = partial(self._propagate_single, transformation_fn=transformation_fn)
            results = pool.map(propagate_fn, belief_states)
        
        return results
    
    def _propagate_single(
        self, 
        belief_state: BeliefState,
        transformation_fn: Callable
    ) -> BeliefState:
        """
        Helper method for parallel batch processing.
        
        Args:
            belief_state: A belief state to transform
            transformation_fn: The transformation function
            
        Returns:
            Transformed belief state
        """
        return self.propagate(belief_state, transformation_fn)
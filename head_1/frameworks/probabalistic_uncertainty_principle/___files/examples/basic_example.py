"""
Basic example of using the PUP framework for uncertainty quantification and propagation.

This example demonstrates the core components of the PUP framework:
- BeliefState for representing uncertain knowledge
- UncertaintyPropagator for transforming uncertain beliefs
- ConfidenceExecutor for making decisions based on confidence
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Tuple

# Import PUP core components
from ___files.core import BeliefState, UncertaintyPropagator, ConfidenceExecutor


def main():
    """Run the basic PUP example."""
    print("Probabilistic Uncertainty Principle (PUP) - Basic Example")
    print("========================================================")
    
    # 1. Create uncertain belief states
    print("\n1. Creating belief states with different uncertainty levels...")
    
    # A high-confidence belief (low variance)
    belief_high_conf = BeliefState(mean=0.7, variance=0.05)
    
    # A low-confidence belief (high variance)
    belief_low_conf = BeliefState(mean=0.7, variance=0.25)
    
    print(f"High confidence belief: {belief_high_conf}")
    print(f"Low confidence belief: {belief_low_conf}")
    
    # 2. Propagate uncertainty through a non-linear transformation
    print("\n2. Propagating through a non-linear transformation (x^2)...")
    
    propagator = UncertaintyPropagator(samples=1000)
    
    # Define a non-linear transformation
    def square_function(x):
        return x ** 2
    
    # Transform both beliefs
    transformed_high_conf = propagator.propagate(belief_high_conf, square_function)
    transformed_low_conf = propagator.propagate(belief_low_conf, square_function)
    
    print(f"Transformed high confidence: {transformed_high_conf}")
    print(f"Transformed low confidence: {transformed_low_conf}")
    
    # 3. Make decisions using confidence-based execution
    print("\n3. Making decisions with confidence thresholds...")
    
    # Create a confidence executor with threshold 0.8
    executor = ConfidenceExecutor(threshold=0.8)
    
    # Define an action to take if confidence is sufficient
    def take_action(x):
        return f"Action taken with value: {x:.4f}"
    
    # Execute with different belief states
    high_conf_result = executor.execute(transformed_high_conf, take_action)
    low_conf_result = executor.execute(transformed_low_conf, take_action)
    
    print(f"Result with high confidence: {high_conf_result}")
    print(f"Result with low confidence: {low_conf_result}")
    
    # 4. Visualize the results
    print("\n4. Visualizing the belief states and transformations...")
    visualize_beliefs(
        [belief_high_conf, belief_low_conf],
        [transformed_high_conf, transformed_low_conf],
        square_function
    )


def visualize_beliefs(
    original_beliefs: List[BeliefState],
    transformed_beliefs: List[BeliefState],
    transform_fn
):
    """
    Visualize original and transformed beliefs.
    
    Args:
        original_beliefs: List of original belief states
        transformed_beliefs: List of transformed belief states
        transform_fn: The transformation function used
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot original beliefs
    x = np.linspace(0, 1, 1000)
    
    for i, belief in enumerate(original_beliefs):
        # Generate normal distribution for the belief
        mean, std = belief.mean[0], np.sqrt(belief.variance[0])
        y = np.exp(-0.5 * ((x - mean) / std) ** 2) / (std * np.sqrt(2 * np.pi))
        
        # Normalize for better visualization
        y = y / np.max(y)
        
        label = f"Belief {i+1} (conf={belief.confidence()[0]:.2f})"
        ax1.plot(x, y, label=label)
        
        # Mark the mean
        ax1.axvline(x=mean, linestyle='--', alpha=0.5, color=f'C{i}')
    
    ax1.set_title("Original Belief States")
    ax1.set_xlabel("Value")
    ax1.set_ylabel("Density (normalized)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot transformed beliefs
    x_transformed = np.linspace(0, 1, 1000)
    y_transformed = transform_fn(x_transformed)
    
    # Plot the transformation function
    ax2.plot(x_transformed, y_transformed, 'k--', alpha=0.5, label="y = x²")
    
    # Plot transformed beliefs
    for i, belief in enumerate(transformed_beliefs):
        # Generate normal distribution for the transformed belief
        mean, std = belief.mean[0], np.sqrt(belief.variance[0])
        
        # Adjusted x range for transformed beliefs
        x_range = np.linspace(max(0, mean - 3*std), mean + 3*std, 1000)
        y = np.exp(-0.5 * ((x_range - mean) / std) ** 2) / (std * np.sqrt(2 * np.pi))
        
        # Normalize for better visualization
        y = y / np.max(y)
        
        label = f"Transformed {i+1} (conf={belief.confidence()[0]:.2f})"
        ax2.plot(x_range, y, label=label)
        
        # Mark the mean
        ax2.axvline(x=mean, linestyle='--', alpha=0.5, color=f'C{i}')
    
    ax2.set_title("Transformed Belief States")
    ax2.set_xlabel("Value")
    ax2.set_ylabel("Density (normalized)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("belief_transformation_example.png")
    print("Visualization saved as 'belief_transformation_example.png'")
    plt.show()


if __name__ == "__main__":
    main()
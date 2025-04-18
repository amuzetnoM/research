# Getting Started with PUP

This guide will help you get started with the Probabilistic Uncertainty Principle (PUP) framework.

## Installation

You can install the PUP framework using pip:

```bash
# Basic installation with core functionality
pip install pup-framework

# With PyTorch integration
pip install pup-framework[pytorch]

# With TensorFlow integration
pip install pup-framework[tensorflow]

# With all features
pip install pup-framework[pytorch,tensorflow]
```

Alternatively, you can install from source:

```bash
git clone https://github.com/yourusername/pup.git
cd pup
pip install -e .
```

## Basic Usage

Here's a simple example of how to use the PUP framework:

```python
import numpy as np
from pup.core import BeliefState, UncertaintyPropagator, ConfidenceExecutor

# 1. Create a belief state with uncertainty
belief = BeliefState(mean=0.7, variance=0.1)
print(f"Initial belief: mean={belief.mean}, variance={belief.variance}")
print(f"Confidence: {belief.confidence()}")

# 2. Propagate through a non-linear transformation
propagator = UncertaintyPropagator(samples=1000)

def cubic_function(x):
    return x**3

transformed_belief = propagator.propagate(belief, cubic_function)
print(f"Transformed belief: mean={transformed_belief.mean}, variance={transformed_belief.variance}")
print(f"New confidence: {transformed_belief.confidence()}")

# 3. Make decisions based on confidence
executor = ConfidenceExecutor(threshold=0.8)

def take_action(value):
    return f"Action taken with value: {value}"

result = executor.execute(transformed_belief, take_action)
print(f"Result: {result}")
```

## Working with Multiple Belief States

You can combine multiple belief states:

```python
from pup.core.utils import combine_belief_states

# Create multiple belief states
belief1 = BeliefState(mean=0.7, variance=0.1)
belief2 = BeliefState(mean=0.8, variance=0.2)
belief3 = BeliefState(mean=0.6, variance=0.05)

# Combine them (optional weights)
combined_belief = combine_belief_states(
    [belief1, belief2, belief3],
    weights=[0.5, 0.3, 0.2]
)

print(f"Combined belief: mean={combined_belief.mean}, variance={combined_belief.variance}")
```

## PyTorch Integration

Here's how to use PUP with PyTorch:

```python
import torch
import torch.nn as nn
from pup.integrations.pytorch import MonteCarloDropout

# Create a PyTorch model
model = nn.Sequential(
    nn.Linear(10, 50),
    nn.ReLU(),
    nn.Dropout(0.1),
    nn.Linear(50, 1)
)

# Wrap with Monte Carlo Dropout
mc_model = MonteCarloDropout(model, dropout_rate=0.1)

# Generate input
x = torch.randn(5, 10)

# Get predictions with uncertainty
belief_state = mc_model.predict_belief_state(x, n_samples=30)

# Use the belief state for downstream tasks
executor = ConfidenceExecutor(threshold=0.9)
result = executor.execute(
    belief_state,
    action_fn=lambda x: f"Prediction: {x}"
)
```

## TensorFlow Integration

Here's how to use PUP with TensorFlow:

```python
import tensorflow as tf
import numpy as np
from pup.integrations.tensorflow import MCDropoutModel

# Create a TensorFlow model
inputs = tf.keras.Input(shape=(10,))
x = tf.keras.layers.Dense(50, activation='relu')(inputs)
x = tf.keras.layers.Dropout(0.1)(x)
outputs = tf.keras.layers.Dense(1)(x)
model = tf.keras.Model(inputs=inputs, outputs=outputs)

# Wrap with MC Dropout
mc_model = MCDropoutModel(model, dropout_rate=0.1)

# Generate input
x = np.random.randn(5, 10).astype(np.float32)

# Get predictions with uncertainty
belief_state = mc_model.predict_belief_state(x, n_samples=30)

# Use the belief state for downstream tasks
executor = ConfidenceExecutor(threshold=0.9)
result = executor.execute(
    belief_state,
    action_fn=lambda x: f"Prediction: {x}"
)
```

## Adaptive Decision-Making

You can use context-sensitive confidence thresholds for adaptive decision-making:

```python
# Create an adaptive confidence executor
executor = ConfidenceExecutor(
    threshold=0.7,
    adaptive=True,
    min_threshold=0.3,
    max_threshold=0.95
)

# Define a context with risk information
context = {
    'risk_level': 0.8,  # High risk situation
    'criticality': 0.7  # High importance decision
}

# Execute with context
result = executor.execute(belief_state, take_action, context)
```

## Next Steps

- Check out the [examples](../pup/examples/) directory for more detailed examples
- Read the [API Reference](api_reference.md) for detailed information on all classes and methods
- Explore the [research paper](../../Research_Papers/uncertainty_in_ai_systems.md) for theoretical background
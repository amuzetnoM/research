# Probabilistic Uncertainty Principle (PUP) Framework

A robust framework for quantifying, propagating, and acting upon uncertainty in AI and cognitive systems.

## Overview

The PUP framework introduces a paradigm shift in cognitive and decision-making systems by formalizing the **Probabilistic Uncertainty Principle**. This principle asserts that reasoning engines must explicitly quantify and propagate uncertainty, and that execution should only occur when confidence surpasses dynamic, context-sensitive thresholds.

At its core, the PUP framework elevates uncertainty from a computational nuisance to a first-class citizen in reasoning systems. It enables the development of AI systems that:

1. Know what they don't know
2. Propagate uncertainty correctly through all computational steps
3. Make decisions with appropriate confidence thresholds
4. Defer actions when uncertainty is too high

## Core Components

The framework provides three primary constructs:

- **BeliefState**: Represents knowledge with quantified uncertainty
- **UncertaintyPropagator**: Evolves uncertainty through computational operations
- **ConfidenceExecutor**: Gates action based on belief confidence

## Installation

```bash
# Not yet available on PyPI, install from source
git clone https://github.com/your-org/pup.git
cd pup
pip install -e .
```

## Quick Start

```python
import numpy as np
from pup.core import BeliefState, UncertaintyPropagator, ConfidenceExecutor

# Create a belief state with uncertainty
belief = BeliefState(mean=0.7, variance=0.1)

# Propagate through a transformation
propagator = UncertaintyPropagator()
transformed_belief = propagator.propagate(belief, lambda x: x**2)

# Execute only if confidence is high enough
executor = ConfidenceExecutor(threshold=0.8)
result = executor.execute(
    transformed_belief,
    action_fn=lambda x: f"Action taken with value: {x}"
)
print(result)  # Either action result or deferral message
```

## Theoretical Foundation

The PUP framework is grounded in rigorous theoretical principles:

- **Bayesian Networks** (Pearl, 1988)
- **Free Energy Principle** (Friston, 2010)
- **Dempster-Shafer Theory** for belief functions
- **Distributional RL** for uncertainty-aware decision-making
- **Active Inference** in cognitive architectures

## Integration with ML Frameworks

The framework provides seamless integration with popular machine learning frameworks:

### PyTorch Integration

```python
import torch
import torch.nn as nn
from pup.integrations.pytorch import MonteCarloDropout, torch_to_belief_state

# Create a model with Monte Carlo dropout for uncertainty estimation
base_model = nn.Sequential(
    nn.Linear(10, 50),
    nn.ReLU(),
    nn.Dropout(0.1),
    nn.Linear(50, 1)
)
mc_model = MonteCarloDropout(base_model)

# Generate predictions with uncertainty
x = torch.randn(5, 10)
belief_state = mc_model.predict_belief_state(x)

# Use the belief state for confidence-based execution
executor = ConfidenceExecutor(threshold=0.9)
result = executor.execute(
    belief_state,
    action_fn=lambda x: f"Prediction: {x}"
)
```

### TensorFlow Integration

```python
import tensorflow as tf
from pup.integrations.tensorflow import MCDropoutModel, tf_to_belief_state

# Create a base model
inputs = tf.keras.Input(shape=(10,))
x = tf.keras.layers.Dense(50, activation='relu')(inputs)
x = tf.keras.layers.Dropout(0.1)(x)
outputs = tf.keras.layers.Dense(1)(x)
base_model = tf.keras.Model(inputs=inputs, outputs=outputs)

# Wrap with MC Dropout for uncertainty estimation
mc_model = MCDropoutModel(base_model)

# Generate predictions with uncertainty
x = np.random.randn(5, 10).astype(np.float32)
belief_state = mc_model.predict_belief_state(x)

# Use the belief state for confidence-based execution
executor = ConfidenceExecutor(threshold=0.9)
result = executor.execute(
    belief_state,
    action_fn=lambda x: f"Prediction: {x}"
)
```

## Applications

The PUP framework enables a wide range of applications:

- **Meta-Cognition**: Self-monitoring of decision chains
- **Explainable AI**: Quantified uncertainty surfaces
- **Human-AI Collaboration**: Transparent deferral behavior
- **Autonomous Systems**: Action gating in critical contexts
- **Neuro-Symbolic Integration**: Probabilistic logic and reasoning

## Core Philosophy

The PUP framework is built on the insight that "What if doubt isn't a flaw in reasoning, but its foundation?"

By embracing uncertainty as an inherent aspect of intelligence rather than a bug to be eliminated, we enable systems that can gracefully handle ambiguity, know their limitations, and engage in more nuanced reasoning about the world.

## Documentation

For detailed API documentation, please refer to the [docs](docs/) directory.

## License

MIT License

## Citation

If you use this framework in your research, please cite:

```
@article{smith2024pup,
  title={The Probabilistic Uncertainty Principle: A Framework for Uncertainty-Aware AI Systems},
  author={Smith, John and Jones, Alice},
  journal={Journal of Artificial Intelligence Research},
  year={2024}
}
```
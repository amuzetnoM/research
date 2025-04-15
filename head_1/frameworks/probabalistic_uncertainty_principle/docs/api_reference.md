# PUP Framework API Reference

This document provides detailed information about the Probabilistic Uncertainty Principle (PUP) framework's API.

## Core Components

The PUP framework consists of three primary components that work together to represent, propagate, and act upon uncertainty:

- **BeliefState**: Represents probabilistic beliefs with uncertainty
- **UncertaintyPropagator**: Propagates uncertainty through transformations
- **ConfidenceExecutor**: Gates actions based on confidence thresholds

## BeliefState

The `BeliefState` class encapsulates a probability distribution over a variable or state, capturing both the expected value and the associated uncertainty.

### Constructor

```python
BeliefState(
    mean: Union[float, List[float], np.ndarray],
    variance: Union[float, List[float], np.ndarray],
    epistemic: bool = True,
    metadata: Optional[Dict[str, Any]] = None
)
```

**Parameters:**

- `mean`: Expected value(s) of the state variable(s)
- `variance`: Uncertainty about the mean value(s)
- `epistemic`: If True, represents knowledge-based uncertainty that can be reduced with more information. If False, represents aleatoric uncertainty (inherent randomness)
- `metadata`: Additional information about this belief state

### Properties

- `mean`: The expected value of the state variable (numpy array)
- `variance`: The uncertainty about the mean value (numpy array)
- `epistemic`: Whether this represents epistemic (knowledge-based) uncertainty
- `metadata`: Dictionary for additional information

### Methods

#### confidence()

Calculates the confidence level of this belief state.

```python
confidence() -> Union[float, np.ndarray]
```

**Returns:**
- A value between 0 and 1 representing confidence level. Higher values indicate greater confidence.

#### update_with_evidence()

Updates this belief state with new evidence using Bayesian updating.

```python
update_with_evidence(
    new_mean: Union[float, List[float], np.ndarray],
    new_variance: Union[float, List[float], np.ndarray],
    weight: float = 0.5
) -> BeliefState
```

**Parameters:**
- `new_mean`: Mean value of the new evidence
- `new_variance`: Variance of the new evidence
- `weight`: Weight to assign to the new evidence (0-1). Higher values give more importance to the new evidence

**Returns:**
- A new BeliefState representing the updated belief

#### to_dict()

Converts this belief state to a dictionary representation.

```python
to_dict() -> Dict[str, Any]
```

**Returns:**
- Dictionary representation of the belief state

#### from_dict()

Class method to create a BeliefState from a dictionary representation.

```python
@classmethod
from_dict(data: Dict[str, Any]) -> BeliefState
```

**Parameters:**
- `data`: Dictionary containing belief state data

**Returns:**
- A new BeliefState object

### Example

```python
# Create a belief state
belief = BeliefState(mean=0.7, variance=0.1)

# Calculate confidence
conf = belief.confidence()
print(f"Confidence: {conf}")

# Update with new evidence
updated_belief = belief.update_with_evidence(
    new_mean=0.8,
    new_variance=0.05,
    weight=0.6
)
```

## UncertaintyPropagator

The `UncertaintyPropagator` transforms belief states through arbitrary functions while correctly tracking and updating uncertainty.

### Constructor

```python
UncertaintyPropagator(
    samples: int = 100,
    parallel: bool = False,
    n_jobs: Optional[int] = None
)
```

**Parameters:**

- `samples`: Number of Monte Carlo samples to use for propagation
- `parallel`: Whether to use parallel processing for Monte Carlo sampling
- `n_jobs`: Number of parallel processes to use (defaults to CPU count if None)

### Methods

#### propagate()

Propagates a belief state through a transformation function.

```python
propagate(
    belief_state: BeliefState,
    transformation_fn: Callable
) -> BeliefState
```

**Parameters:**
- `belief_state`: The initial belief state
- `transformation_fn`: Function to apply to the belief state (should accept inputs with the same shape as belief_state.mean)

**Returns:**
- A new BeliefState representing the transformed belief

#### propagate_batch()

Propagates a batch of belief states through a transformation.

```python
propagate_batch(
    belief_states: List[BeliefState],
    transformation_fn: Callable
) -> List[BeliefState]
```

**Parameters:**
- `belief_states`: List of belief states to transform
- `transformation_fn`: The transformation function

**Returns:**
- List of transformed belief states

#### propagate_batch_parallel()

Propagates a batch of belief states through a transformation in parallel.

```python
propagate_batch_parallel(
    belief_states: List[BeliefState],
    transformation_fn: Callable
) -> List[BeliefState]
```

**Parameters:**
- `belief_states`: List of belief states to transform
- `transformation_fn`: The transformation function

**Returns:**
- List of transformed belief states

### Example

```python
# Create a belief state
belief = BeliefState(mean=0.7, variance=0.1)

# Create propagator
propagator = UncertaintyPropagator(samples=1000)

# Define a non-linear transformation
def square_function(x):
    return x ** 2

# Transform the belief
transformed_belief = propagator.propagate(belief, square_function)

print(f"Original mean: {belief.mean}, variance: {belief.variance}")
print(f"Transformed mean: {transformed_belief.mean}, variance: {transformed_belief.variance}")
```

## ConfidenceExecutor

The `ConfidenceExecutor` gates actions based on confidence thresholds, executing functions only when belief confidence exceeds the threshold.

### Constructor

```python
ConfidenceExecutor(
    threshold: float = 0.9,
    fallback_fn: Optional[Callable[[BeliefState], U]] = None,
    adaptive: bool = False,
    min_threshold: float = 0.1,
    max_threshold: float = 0.99
)
```

**Parameters:**

- `threshold`: Confidence threshold for executing actions (0.0-1.0)
- `fallback_fn`: Function to call when confidence is below threshold
- `adaptive`: Whether to use adaptive thresholds based on context
- `min_threshold`: Minimum allowed threshold if using adaptive mode
- `max_threshold`: Maximum allowed threshold if using adaptive mode

### Methods

#### execute()

Executes an action if belief confidence exceeds threshold.

```python
execute(
    belief_state: BeliefState,
    action_fn: Callable[[Any], T],
    context: Optional[Dict[str, Any]] = None
) -> Union[T, U]
```

**Parameters:**
- `belief_state`: The belief state to check confidence against
- `action_fn`: Function to execute if confidence is sufficient
- `context`: Optional context information for adaptive thresholds

**Returns:**
- Either the result of action_fn or fallback_fn

#### get_execution_stats()

Gets statistics about execution attempts.

```python
get_execution_stats() -> Dict[str, Any]
```

**Returns:**
- Dictionary with execution statistics

#### adjust_threshold()

Manually adjusts the base threshold.

```python
adjust_threshold(adjustment: float)
```

**Parameters:**
- `adjustment`: Amount to adjust the threshold by (positive or negative)

### Example

```python
# Create a belief state
belief = BeliefState(mean=0.7, variance=0.1)

# Create a confidence executor with threshold 0.8
executor = ConfidenceExecutor(threshold=0.8)

# Define an action to take if confidence is sufficient
def take_action(x):
    return f"Action taken with value: {x}"

# Execute with context information
context = {'risk_level': 0.7, 'criticality': 0.5}
result = executor.execute(belief, take_action, context)

print(f"Result: {result}")
```

## Utility Functions

The PUP framework provides several utility functions for working with belief states.

### combine_belief_states()

Combines multiple belief states into a single aggregated belief.

```python
combine_belief_states(
    belief_states: List[BeliefState],
    weights: Optional[List[float]] = None
) -> BeliefState
```

**Parameters:**
- `belief_states`: List of belief states to combine
- `weights`: Optional weights for each belief state (must sum to 1.0). If None, equal weights are assigned

**Returns:**
- A new BeliefState representing the combined belief

### calibrate_belief_state()

Calibrates a belief state using empirical data.

```python
calibrate_belief_state(
    belief_state: BeliefState,
    calibration_data: Tuple[np.ndarray, np.ndarray]
) -> BeliefState
```

**Parameters:**
- `belief_state`: The belief state to calibrate
- `calibration_data`: Tuple of (predictions, actual_values) for calibration

**Returns:**
- A calibrated BeliefState

### create_ensemble_belief()

Creates a belief state from ensemble model predictions.

```python
create_ensemble_belief(
    model_predictions: List[np.ndarray],
    model_weights: Optional[List[float]] = None
) -> BeliefState
```

**Parameters:**
- `model_predictions`: List of predictions from different models
- `model_weights`: Optional weights for each model's prediction

**Returns:**
- A BeliefState representing the ensemble belief

### variance_from_errors()

Estimates variance from a sequence of prediction errors.

```python
variance_from_errors(
    errors: np.ndarray,
    window_size: int = 10,
    min_variance: float = 1e-6
) -> np.ndarray
```

**Parameters:**
- `errors`: Array of prediction errors over time
- `window_size`: Number of recent errors to consider
- `min_variance`: Minimum variance to return

**Returns:**
- Estimated variance

## PyTorch Integration

The PUP framework provides integration with PyTorch for uncertainty estimation in deep learning models.

### Classes

#### MonteCarloDropout

Wrapper that enables Monte Carlo dropout at inference time.

```python
MonteCarloDropout(module: nn.Module, dropout_rate: float = 0.1)
```

**Methods:**
- `predict_with_uncertainty(x: torch.Tensor, n_samples: int = 30) -> Tuple[torch.Tensor, torch.Tensor]`
- `predict_belief_state(x: torch.Tensor, n_samples: int = 30) -> BeliefState`

#### EnsembleModel

Ensemble of PyTorch models for uncertainty estimation.

```python
EnsembleModel(models: List[nn.Module], device: Optional[torch.device] = None)
```

**Methods:**
- `predict_with_uncertainty(x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]`
- `predict_belief_state(x: torch.Tensor) -> BeliefState`

### Functions

#### torch_to_belief_state()

Converts PyTorch tensors to a BeliefState.

```python
torch_to_belief_state(
    mean: torch.Tensor,
    variance: Optional[torch.Tensor] = None,
    uncertainty_scale: float = 1.0,
    epistemic: bool = True
) -> BeliefState
```

#### belief_state_to_torch()

Converts a BeliefState to PyTorch tensors.

```python
belief_state_to_torch(
    belief_state: BeliefState,
    device: Optional[torch.device] = None
) -> Tuple[torch.Tensor, torch.Tensor]
```

## TensorFlow Integration

The PUP framework provides integration with TensorFlow for uncertainty estimation in deep learning models.

### Classes

#### MCDropoutModel

Wrapper for TensorFlow models to enable Monte Carlo dropout at inference time.

```python
MCDropoutModel(model: tf.keras.Model, dropout_rate: Optional[float] = None)
```

**Methods:**
- `predict_with_uncertainty(x: Union[np.ndarray, tf.Tensor], n_samples: int = 30) -> Tuple[np.ndarray, np.ndarray]`
- `predict_belief_state(x: Union[np.ndarray, tf.Tensor], n_samples: int = 30) -> BeliefState`

#### ModelEnsemble

Ensemble of TensorFlow models for uncertainty estimation.

```python
ModelEnsemble(models: List[tf.keras.Model])
```

**Methods:**
- `predict_with_uncertainty(x: Union[np.ndarray, tf.Tensor]) -> Tuple[np.ndarray, np.ndarray]`
- `predict_belief_state(x: Union[np.ndarray, tf.Tensor]) -> BeliefState`

### Functions

#### create_dropout_model()

Creates a Bayesian model from a regular model by adding dropout layers.

```python
create_dropout_model(
    base_model: tf.keras.Model,
    dropout_rate: float = 0.1,
    return_variance: bool = True
) -> tf.keras.Model
```

#### tf_to_belief_state()

Converts TensorFlow tensors to a BeliefState.

```python
tf_to_belief_state(
    mean: Union[tf.Tensor, np.ndarray],
    variance: Optional[Union[tf.Tensor, np.ndarray]] = None,
    uncertainty_scale: float = 1.0,
    epistemic: bool = True
) -> BeliefState
```

#### belief_state_to_tf()

Converts a BeliefState to TensorFlow tensors.

```python
belief_state_to_tf(
    belief_state: BeliefState
) -> Tuple[tf.Tensor, tf.Tensor]
```
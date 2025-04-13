# Advanced AI Research Frameworks

This directory contains the implementations of advanced AI research frameworks designed to explore artificial consciousness, self-awareness, and advanced reasoning capabilities.

## Frameworks Overview

### Self-Awareness Mechanics

The Self-Awareness Mechanics framework implements computational self-awareness through a modular architecture that enables AI systems to model their own capabilities, limitations, knowledge boundaries, and operational states.

Key components:
- **State Monitoring Module**: Collects real-time telemetry on system operations
- **Knowledge Modeling Module**: Maintains representations of system knowledge
- **Capability Assessment Module**: Models the system's abilities and limitations
- **Confidence Estimation Module**: Quantifies uncertainty across all predictions
- **Regulatory Control Module**: Modifies system behavior based on self-awareness

Usage example:
```python
from frameworks.self_awareness import SelfAwarenessFramework

# Initialize the framework
framework = SelfAwarenessFramework()
framework.start()

# Get the current self-model
self_model = framework.get_self_model()

# Save the self-model
framework.save_self_model('path/to/save/model.json')
```

### Emotional Dimensionality Framework (EDF)

The Emotional Dimensionality Framework moves beyond traditional sentiment analysis by modeling emotional expressions across multiple interrelated dimensions, providing a richer representation of emotional states.

Key features:
- **Multidimensional Emotional Modeling**: Represents emotions across 7 core dimensions
- **Contextual Integration**: Incorporates 5 contextual factors that modify emotional interpretation
- **Neural & Rule-Based Models**: Includes both rule-based and neural implementation options
- **Cross-Cultural Support**: Includes mechanisms for cultural adaptation of emotion interpretation

Usage example:
```python
from frameworks.emotional_dimensionality import EmotionalDimensionalityFramework

# Initialize the framework
edf = EmotionalDimensionalityFramework()

# Analyze text
emotional_state = edf.analyze("I'm really excited about this project!", 
                             context={"culture": "western"})

# Get the dominant emotion
emotion, confidence = edf.dominant_emotion(emotional_state)
```

## Installation

To install the frameworks and their dependencies:

```bash
# Basic installation
pip install -e .

# With development tools
pip install -e ".[dev]"

# With GPU support
pip install -e ".[gpu]"
```

## Visualization Tools

The frameworks include comprehensive visualization tools for understanding the system's self-model and emotional analysis:

1. **Self-Model Visualization**: Interactive tools for exploring the system's self-knowledge, capability boundaries, and confidence levels
2. **Temporal Evolution Tracker**: Visualization of how self-awareness metrics evolve over time
3. **Emotional Dimensionality Visualization**: Tools for visualizing emotional states in multidimensional space

These visualization tools can be found in the `notebooks` directory.

## Cross-Container Support

Both frameworks support cross-container operations, allowing for:
- Comparison of self-models between containers
- Synchronization of emotional analysis results
- Parallel experimentation with different configurations

## Implementation Status

According to our implementation checklist:
- ✅ Self-Awareness Metrics fully implemented
- ✅ Self-Model Representations complete
- ✅ Emotional Dimensionality Analysis implemented
- ✅ Parallel Experimentation Framework support added

See the `implementation_checklist.md` file for full status details.

## Architecture Documentation

For detailed architecture documentation:
- [Self-Awareness Mechanics Architecture](./self_awareness/README.md)
- [Emotional Dimensionality Framework Architecture](./emotional_dimensionality/README.md)

## Contributing

When contributing to these frameworks, please follow these guidelines:
1. Create a feature branch from `main`
2. Follow the coding style (use Black formatter)
3. Add tests for new functionality
4. Update documentation as needed
5. Submit a pull request

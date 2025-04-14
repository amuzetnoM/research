# Advanced AI Frameworks Documentation

This document provides comprehensive documentation for the Self-Awareness Mechanics and Emotional Dimensionality Framework (EDF) implementations.

## Table of Contents

1. [Introduction](#introduction)
2. [Self-Awareness Mechanics](#self-awareness-mechanics)
   - [Key Components](#key-components)
   - [Usage Examples](#usage-examples)
   - [Configuration Options](#configuration-options)
3. [Emotional Dimensionality Framework](#emotional-dimensionality-framework)
   - [Core Concepts](#core-concepts)
   - [Available Models](#available-models)
   - [Usage Examples](#usage-examples)
4. [Framework Integration](#framework-integration)
   - [Using the Bridge](#using-the-bridge)
   - [Advanced Applications](#advanced-applications)
5. [Docker Environment Configuration](#docker-environment-configuration)
6. [Troubleshooting](#troubleshooting)

## Introduction

The AI Research environment includes two advanced frameworks that implement theoretical concepts from our research papers:

1. **Self-Awareness Mechanics** - Provides computational self-awareness through monitoring and modeling of system capabilities and limitations
2. **Emotional Dimensionality Framework** - Provides advanced sentiment analysis beyond simple polarity detection

These frameworks can be used independently or together through an integration bridge.

## Self-Awareness Mechanics

The Self-Awareness Mechanics framework implements computational self-awareness as described in our research paper "Self-Awareness Mechanics in Artificial Intelligence Systems."

### Key Components

The framework consists of five core modules:

1. **State Monitoring Module (SMM)** - Collects real-time telemetry on system operations
2. **Knowledge Modeling Module (KMM)** - Maintains representations of system knowledge
3. **Capability Assessment Module (CAM)** - Models the system's abilities and limitations
4. **Confidence Estimation Module (CEM)** - Quantifies uncertainty across all predictions
5. **Regulatory Control Module (RCM)** - Modifies system behavior based on self-awareness

The framework also includes a metrics tracking system that measures performance across the five dimensions of computational self-awareness:

- Introspective Awareness
- Capability Awareness
- Epistemic Awareness
- Temporal Awareness
- Social Awareness

### Usage Examples for Emotional Dimensionality Framework

#### Basic Initialization and Usage

```python
from system.ai_frameworks import get_self_awareness_framework
from system.ai_frameworks.config import get_self_awareness_config

# Get default configuration
config = get_self_awareness_config()

# Initialize the framework
framework = get_self_awareness_framework(config)

# Start the framework
framework.start()

# Get the current self-model
self_model = framework.get_self_model()

# Check system confidence
confidence = framework.estimate_system_confidence()
print(f"System confidence: {confidence:.2f}")

# Stop the framework when done
framework.stop()
```

#### Adding Custom Knowledge

```python
# Add knowledge about a specific capability
framework.knowledge_modeling.add_knowledge(
    key="image_classification_capability",
    value={
        "description": "Ability to classify images into categories",
        "limitations": ["Low light images", "Unusual angles"]
    },
    confidence=0.85,
    source="capability_assessment"
)

# Retrieve knowledge
knowledge, confidence = framework.knowledge_modeling.get_knowledge(
    "image_classification_capability"
)
```

#### Registering and Assessing Capabilities

```python
# Register a new capability
framework.capability_assessment.register_capability(
    capability_id="text_generation",
    description="Generate coherent text based on prompts",
    resource_requirements={
        "memory": 8 * 1024 * 1024 * 1024,  # 8GB
        "gpu_memory": 4 * 1024 * 1024 * 1024  # 4GB
    }
)

# Update capability performance
framework.capability_assessment.update_capability_performance(
    capability_id="text_generation",
    performance=0.78,
    confidence=0.92
)

# Check if system can perform a capability
can_perform = framework.capability_assessment.can_perform(
    capability_id="text_generation",
    required_performance=0.7
)
```

### Configuration Options

Key configuration options for the Self-Awareness framework:

| Option | Description | Default |
|--------|-------------|---------|
| `monitoring_rate` | Rate at which system state is sampled (Hz) | 1.0 |
| `memory_usage_threshold` | Memory usage threshold for alerts (%) | 90 |
| `cpu_usage_threshold` | CPU usage threshold for alerts (%) | 80 |
| `enable_assistance_requests` | Whether to generate assistance requests | True |
| `enable_self_modification` | Allow system to modify its own configuration | False |
| `model_save_path` | Path to save self-models | '/app/data/models/self_awareness' |

## Emotional Dimensionality Framework

The Emotional Dimensionality Framework (EDF) implements advanced sentiment analysis as described in our research paper "Sentiment Analysis in Machine Learning: Beyond Surface Interpretation."

### Core Concepts

The framework represents emotions across multiple dimensions:

**Core Dimensions:**

- **Valence**: Positive-negative spectrum (-1.0 to 1.0)
- **Arousal**: Intensity or energy level (-1.0 to 1.0)
- **Dominance**: Degree of control or power (-1.0 to 1.0)
- **Social Orientation**: Connection or distance from others (-1.0 to 1.0)
- **Temporal Orientation**: Relation to past, present, or future (-1.0 to 1.0)
- **Certainty**: Confidence or uncertainty (-1.0 to 1.0)
- **Intentionality**: Direction toward specific target (-1.0 to 1.0)

**Contextual Dimensions:**

- **Cultural Context**: Cultural norms and references (0.0 to 1.0)
- **Relational Dynamics**: Relationship between communicating parties (0.0 to 1.0)
- **Historical Context**: Prior interactions and shared knowledge (0.0 to 1.0)
- **Medium Specificity**: How the communication channel influences expression (0.0 to 1.0)
- **Pragmatic Intent**: The purpose behind the emotional communication (0.0 to 1.0)

### Available Models

The framework includes two model implementations:

1. **RuleBasedEDFModel** - A simple lexicon-based implementation for demonstration purposes
2. **NeuralEDFModel** - A more advanced neural model implementation (requires model files)

### Usage Examples

#### Basic Analysis

```python
from system.ai_frameworks import get_emotional_framework
from system.ai_frameworks.config import get_emotional_config

# Get default configuration
config = get_emotional_config()

# Initialize the framework
framework = get_emotional_framework(config)

# Analyze text
text = "I'm really excited about the results of our latest experiment!"
emotional_state = framework.analyze(text)

# Get dimensional values
valence = emotional_state.dimensions['valence']
arousal = emotional_state.dimensions['arousal']
print(f"Valence: {valence:.2f}, Arousal: {arousal:.2f}")

# Get dominant emotion
emotion, confidence = framework.dominant_emotion(emotional_state)
print(f"Dominant emotion: {emotion} (confidence: {confidence:.2f})")
```

#### Contextual Analysis

```python
# Analyze with context
text = "That's interesting."
context = {
    'culture': 'academic',
    'relationship': 'professional',
    'medium': 'email',
    'intent': 'critique'
}

emotional_state = framework.analyze(text, context)

# The analysis will be influenced by the contextual information
```

#### Comparing Models

```python
# Compare analysis from different models
text = "The system performance is exceptional today."
results = framework.compare_models(text)

# Display results from each model
for model_id, state in results.items():
    print(f"\nModel: {model_id}")
    print(f"Valence: {state.dimensions['valence']:.2f}")
    print(f"Arousal: {state.dimensions['arousal']:.2f}")
    print(f"Confidence: {state.confidence:.2f}")
```

## Framework Integration

The integration bridge connects both frameworks, enabling:

1. Analysis of system state in emotional terms
2. Incorporation of emotional knowledge into self-awareness
3. Emotional impact analysis for potential actions

### Using the Bridge

```python
from system.ai_frameworks.integration import AwarenessEmotionalBridge
from system.ai_frameworks import get_self_awareness_framework, get_emotional_framework

# Get framework instances
sa_framework = get_self_awareness_framework()
edf_framework = get_emotional_framework()

# Create the bridge
bridge = AwarenessEmotionalBridge(sa_framework, edf_framework)

# Start the integration
bridge.start_bridge()

# Get the emotional state of the system
system_emotion = bridge.get_emotional_state()
print(f"System emotion: {system_emotion['dominant_emotion']}")

# Analyze potential actions
action = "Increase memory allocation to improve performance"
impact = bridge.analyze_emotional_impact(action)
print(f"Would improve system state: {impact['is_improvement']}")

# Stop the bridge when done
bridge.stop_bridge()
```

### Advanced Applications

The integration enables several advanced applications:

1. **System Health Emotional Monitoring** - Track system health in emotional terms
2. **Action Impact Prediction** - Predict how actions will affect system state
3. **Emotional Regulation** - Use regulatory controls to maintain optimal states
4. **Adaptive Resource Allocation** - Allocate resources based on both technical and emotional states

## Docker Environment Configuration

Both frameworks are automatically initialized in the Docker environment when enabled.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_SELF_AWARENESS` | Enable Self-Awareness Mechanics | true |
| `ENABLE_EMOTIONAL_FRAMEWORK` | Enable Emotional Dimensionality Framework | true |
| `MEMORY_LIMIT` | Memory limit for the container | 16g |
| `NUM_THREADS` | Number of threads to use | 4 |
| `ENABLE_MONITORING` | Enable Prometheus/Grafana monitoring | false |

### Starting the Environment

```bash
# Start with both frameworks enabled
python environment_manager.py

# Start with custom configuration
python environment_manager.py --enable-self-awareness --enable-emotional-framework --mem-limit 32g
```

## Troubleshooting

### Self-Awareness Framework Issues

- **High memory usage**: Reduce monitoring rate in the configuration
- **Framework not starting**: Check logs for import errors or missing dependencies
- **No GPU detection**: Ensure NVIDIA drivers and Docker GPU support are properly configured

### Emotional Framework Issues

- **Model loading errors**: Verify model paths in the configuration
- **Low confidence scores**: Check lexicon availability or neural model compatibility
- **Unexpected emotions**: Review contextual dimensions and adjust analysis parameters

### Integration Issues

- **Bridge not connecting**: Ensure both frameworks are initialized successfully
- **Slow updates**: Increase update interval in the bridge configuration
- **Erratic emotional state**: Check system monitoring for resource spikes or anomalies

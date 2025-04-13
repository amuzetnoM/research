# Emotional Dimensionality Framework (EDF)

## Overview

The Emotional Dimensionality Framework (EDF) moves beyond traditional sentiment analysis by modeling emotional expressions across multiple interrelated dimensions. This provides a richer, more nuanced representation of emotional states that can capture complexity that traditional positive/negative polarity analysis misses.

This implementation is based on the research paper "Sentiment Analysis in Machine Learning: Beyond Surface Interpretation" and provides a comprehensive framework for multidimensional emotional analysis.

## Core Dimensions

The EDF models emotions across seven core dimensions:

1. **Valence**: The positive-negative spectrum (-1.0 to 1.0)
2. **Arousal**: The intensity or energy level (-1.0 to 1.0)
3. **Dominance**: The degree of control or power (-1.0 to 1.0)
4. **Social Orientation**: Connection or distance from others (-1.0 to 1.0)
5. **Temporal Orientation**: Relation to past, present, or future (-1.0 to 1.0)
6. **Certainty**: Confidence or uncertainty in the expression (-1.0 to 1.0)
7. **Intentionality**: Direction toward a specific target (-1.0 to 1.0)

## Contextual Dimensions

In addition to core dimensions, EDF incorporates five contextual factors:

1. **Cultural Context**: Cultural norms and references (0.0 to 1.0)
2. **Relational Dynamics**: Relationship between communicating parties (0.0 to 1.0)
3. **Historical Context**: Prior interactions and shared knowledge (0.0 to 1.0)
4. **Medium Specificity**: How the communication channel influences expression (0.0 to 1.0)
5. **Pragmatic Intent**: The purpose behind the emotional communication (0.0 to 1.0)

## Implementation Models

The framework provides two implementation models:

### 1. RuleBasedEDFModel

A lexicon-based approach suitable for simple cases and scenarios where training data is limited:

```python
from frameworks.emotional_dimensionality import RuleBasedEDFModel

model = RuleBasedEDFModel()
emotional_state = model.analyze("I'm so excited about this project!")
```

### 2. NeuralEDFModel

A neural network-based approach for more sophisticated analysis:

```python
from frameworks.emotional_dimensionality import NeuralEDFModel

model = NeuralEDFModel('path/to/model.pt')
emotional_state = model.analyze("I'm feeling quite ambivalent about the changes.")
```

## EmotionalState Representation

The `EmotionalState` class represents a point in the multidimensional emotional space:

```python
# Creating an emotional state
state = EmotionalState()
state.set_dimension("valence", 0.8)  # Positive valence
state.set_dimension("arousal", 0.6)  # Moderate arousal
state.set_contextual("cultural", 0.9)  # Strong cultural context

# Calculating distance between states
distance = state1.emotional_distance(state2)

# Converting to vector representation
vector = state.to_vector()
```

## Framework Usage

The main `EmotionalDimensionalityFramework` class provides a unified interface:

```python
from frameworks.emotional_dimensionality import EmotionalDimensionalityFramework

# Initialize the framework
edf = EmotionalDimensionalityFramework()

# Add models
edf.add_model("rule_based", RuleBasedEDFModel())
edf.add_model("neural", NeuralEDFModel('path/to/model.pt'))
edf.set_default_model("neural")

# Analyze text
state = edf.analyze("I'm feeling optimistic about our prospects.", 
                   context={"medium": "email"})

# Compare analyses from different models
results = edf.compare_models("This new policy makes me uncomfortable.")

# Map to categorical emotion
emotion, confidence = edf.dominant_emotion(state)
print(f"Dominant emotion: {emotion} (confidence: {confidence})")
```

## Cross-Cultural Analysis

The EDF includes support for cross-cultural emotional interpretation:

```python
# Western cultural context
western_state = edf.analyze("That's interesting!", 
                           context={"culture": "western"})

# East Asian cultural context
eastern_state = edf.analyze("That's interesting!", 
                           context={"culture": "east_asian"})

# Compare interpretations
difference = western_state.emotional_distance(eastern_state)
```

## Visualization

The framework includes visualization tools to help understand emotional states:

1. **Dimension Radar Charts**: Visualize all dimensions for a single emotional state
2. **Emotional Trajectory Plots**: Track how emotions evolve over time
3. **Comparative Visualization**: Compare emotional states across different contexts or models
4. **Dimensional Projection**: Project high-dimensional emotional states onto 2D/3D spaces

Access these visualizations through the notebooks provided in the `notebooks` directory.

## Performance Tuning

- For faster processing of large text corpora, use batch processing:
  ```python
  states = edf.batch_analyze(text_list, contexts=context_list)
  ```
  
- For resource-constrained environments, use the rule-based model:
  ```python
  edf.set_default_model("rule_based")
  ```

## Training Custom Models

To train a custom neural EDF model:

1. Prepare multidimensional emotion annotations
2. Use the training utilities:
   ```python
   from frameworks.emotional_dimensionality.training import train_neural_model
   
   model = train_neural_model(
       training_data="path/to/data.csv",
       model_type="transformer",
       epochs=5
   )
   ```

## References

- Research paper: "Sentiment Analysis in Machine Learning: Beyond Surface Interpretation"
- [Implementation Checklist](../../implementation_checklist.md)
- [Visualization Notebook](../../notebooks/emotional_visualization.ipynb)

# Advanced Cognitive Simulation

This folder contains an advanced cognitive simulation that demonstrates adaptive behaviors, learning mechanisms, and integration with the Self-Awareness Framework to create a cognitively aware artificial system.

## Overview

The cognitive simulation implements an artificial lifeform that exists in a dynamic environment, makes decisions based on sensory input, adapts its behavior over time, and integrates with the self-awareness framework to gain introspective capabilities. This simulation serves as a sophisticated testing ground for AI self-awareness mechanisms.

## Features

### Core Simulation Infrastructure

- **Artificial Lifeform**: Sophisticated agent with sensing, decision-making, and adaptive capabilities
- **Dynamic Environment**: Simulates changing conditions with obstacles and rewards
- **Behavior System**: Utility-based decision model with five core behaviors (MOVE, CONSUME, AVOID, REST, EXPLORE)
- **Learning Mechanisms**: Adaptive behavior weights that evolve based on performance metrics
- **Self-Awareness Integration**: Interfaces with the self-awareness framework for introspective capabilities

### Advanced Visualization

- **Energy Tracking**: Visualize energy levels throughout the simulation
- **Environmental Monitoring**: Track environmental conditions and their impact
- **Performance Metrics**: Visualize efficiency, adaptability, and other core metrics
- **Behavior Adaptation**: See how behavior weights change over time
- **Summary Reporting**: Comprehensive reports on simulation outcomes

### Sophisticated Analysis

- **Survival Factor Analysis**: Identify what helps the entity survive
- **Behavior Adaptation Analysis**: Understand learning patterns and specialization
- **Environmental Impact Assessment**: See how context affects behavior
- **Cluster Analysis**: Identify distinct operational modes using machine learning
- **Learning Effectiveness Evaluation**: Measure adaptation rate and efficiency

## Running the Simulation

### Basic Execution

```bash
python cognitive_simulation.py
```

This will run the simulation with default parameters from the configuration file.

### Using Docker Compose

The simplest way to run the simulation with the self-awareness server:

```bash
docker-compose up
```

### Configuration

The simulation's behavior can be adjusted through the `config.json` file, which includes the following sections:

- **Simulation**: Controls iteration count, logging frequency, etc.
- **Lifeform**: Parameters for the artificial lifeform such as initial energy, sensor reliability, etc.
- **Behaviors**: Weights and energy costs for different behavior types
- **Environment**: Complexity, obstacle density, reward density, etc.
- **Self-Awareness**: Connection settings for the self-awareness framework
- **Visualization**: Options for plotting and visualization

## Analysis and Visualization

### Running the Visualizer

To visualize the results of the most recent simulation:

```bash
python simulation_visualizer.py
```

This will generate plots showing energy levels, environmental conditions, performance metrics, and behavior adaptation.

### Running Advanced Analysis

To perform in-depth analysis on the simulation results:

```bash
python cognitive_analysis.py
```

This will generate a comprehensive report including:
- Survival factors analysis
- Behavior adaptation patterns
- Environmental impact assessment
- Operational mode identification via cluster analysis
- Learning effectiveness evaluation

## Integration with Self-Awareness Framework

The cognitive simulation demonstrates how to:

1. Connect to the self-awareness framework
2. Register handlers for insights and alerts
3. Report metrics about decision-making processes
4. Adapt behavior based on self-awareness information

Key integration points:
- The `ArtificialLifeform` class connects to the `SelfAwarenessClient`
- Decision metrics are reported with `update_decision_metrics()`
- Insights are processed in the `handle_insight()` method
- Alerts are handled in the `handle_alert()` method

## Technical Details

For detailed information about the architecture and implementation of the cognitive simulation, please see [ARCHITECTURE.md](ARCHITECTURE.md).

## Example Output

Running the simulation produces log files in the `simulation_logs` directory:
- `sim_[timestamp]_[iteration].json`: State snapshots during the simulation
- `sim_[timestamp]_final.json`: Final state of the simulation

Example visualization outputs include:
- Energy level charts showing resource management over time
- Behavior weight charts showing adaptation patterns
- Performance metric charts showing efficiency, adaptability, etc.
- Environment condition charts showing external factors

## Future Development

Planned enhancements include:
- Multi-agent simulation support
- Integration with reinforcement learning techniques
- More complex environmental models
- Enhanced 3D visualization
- Real-time interactive control

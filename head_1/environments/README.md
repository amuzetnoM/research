# Artificial Lifeform Simulation Environment

## Description

This is a robust and versatile simulation environment designed to model and analyze artificial lifeforms and their interactions within a complex system. It is capable of:

* **Self-containment:** Operating independently with minimal external dependencies.
* **Metriculation:** Tracking and recording a wide range of performance metrics.
* **Analysis:** Providing tools and methods for analyzing the collected data.
* **Tracking:** Monitoring the state and behavior of all entities within the simulation.
* **Handling diverse complexities:** Supporting everything from simple on/off code to advanced cognitive intelligence.
* **Managing multiple interconnected programs:** Facilitating interactions between different AI systems.
* **Preventing logical failures:** Robust architecture to ensure continuous and reliable operation.

The environment includes intelligent systems for generating obstacles, rewards, and other dynamic elements, creating a challenging and engaging simulation for artificial lifeforms.

## Features

* **Initialization:** The environment can be initialized with a specified size, initial resources, and complexity level.
* **Entity Management:** Entities can be added, removed, and moved within the environment. Their positions can be tracked, and their neighbors can be queried.
* **Resource Management:** The environment's resources can be consumed and replenished.
* **Global Metrics:** The simulation tracks global metrics such as total energy consumption, average fitness, and entity count.
* **Dynamic Events:** The environment can introduce random dynamic events, such as resource influxes, environmental disasters, and the appearance of new entities.
* **Program Management:** The environment can manage and run multiple interconnected programs.
* **Grid-Based World:** The environment uses a grid-based system to represent the spatial relationships between entities and environmental elements.
* **Event Logging:** A comprehensive event logging system is included to track all significant events that occur during the simulation.

## How to Use

1.  **Import:** Import the `SimulationEnvironment` class.
2.  **Initialize:** Create an instance of the `SimulationEnvironment` class, specifying the desired size, initial resources, and complexity level.
3.  **Add Entities:** Create instances of your entity classes (inheriting from `BaseEntity`) and add them to the environment using the `add_entity()` method.
4.  **Run Simulation:** Call the `run_simulation()` method to start the simulation. You can specify the number of iterations and the time step.
5.  **Access Data:** Use the various methods to access simulation data, such as `get_grid_state()`, `get_global_metrics()`, and `get_event_log()`.
6.  **Add Programs:** Use `add_program()` to add programs, and `run_program()` to start them.

## Class Details

### `SimulationEnvironment`

```python
class Simulation
CT
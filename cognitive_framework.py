#!/usr/bin/env python3
"""
Unified Cognitive Framework

This module consolidates cognitive simulation and analysis functionality:
- Artificial lifeform simulation
- Behavioral systems modeling
- Learning and adaptation mechanisms
- Performance analysis and evaluation
- Integration with self-awareness framework
"""
# This implementation includes:
#    - A SimulationManager for running and controlling simulations
#    - A SimulationVisualizer for creating plots and summary reports
#    - A CognitiveAnalysis class for performing advanced statistical analysis
#    - Utility functions and a demonstration main function

import logging
import random
import time
import threading
import os
import sys
import gc
import numpy as np
import pandas as pd
import json
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("cognitive-framework")

# Try to import self_awareness_client, but don't fail if it's not available
sys.path.append(os.path.join(os.path.dirname(__file__), 'head_1', 'frameworks', 'self_awareness'))
try:
    from self_awareness_client import SelfAwarenessClient
    HAS_SELF_AWARENESS = True
except ImportError:
    logger.warning("Self-awareness client not found. Running without self-awareness capabilities.")
    HAS_SELF_AWARENESS = False

# ==========================================
# Data Structures and Enums
# ==========================================

class SensorType(Enum):
    """Types of sensors available to the artificial lifeform"""
    VISUAL = "visual"
    AUDIO = "audio"
    PROXIMITY = "proximity"
    ENERGY = "energy"
    INTERNAL = "internal"

class ActionType(Enum):
    """Types of actions available to the artificial lifeform"""
    MOVE = "move"
    OBSERVE = "observe"
    CONSUME = "consume"
    REST = "rest"
    EXPLORE = "explore"
    COMMUNICATE = "communicate"

@dataclass
class SensorReading:
    """Represents a reading from a sensor"""
    sensor_type: SensorType
    value: float
    uncertainty: float
    timestamp: float = field(default_factory=time.time)

@dataclass
class Action:
    """Represents an action taken by the artificial lifeform"""
    action_type: ActionType
    parameters: Dict[str, Any]
    energy_cost: float
    timestamp: float = field(default_factory=time.time)
    success: bool = True
    outcomes: Dict[str, Any] = field(default_factory=dict)

# ==========================================
# Core Simulation Classes
# ==========================================

class SensorSystem:
    """Manages sensors and sensor readings for the artificial lifeform"""
    
    def __init__(self, available_sensors: List[SensorType] = None):
        """Initialize the sensor system with available sensors."""
        self.available_sensors = available_sensors or list(SensorType)
        self.readings = []  # History of sensor readings
        self.current_values = {sensor: 0.0 for sensor in self.available_sensors}
        self.sensor_noise = {sensor: random.uniform(0.01, 0.05) for sensor in self.available_sensors}
    
    def read_sensor(self, sensor_type: SensorType) -> SensorReading:
        """Read a specific sensor and return the reading."""
        if sensor_type not in self.available_sensors:
            raise ValueError(f"Sensor {sensor_type} not available")
        
        # Simulate reading the sensor with some noise
        base_value = self.current_values[sensor_type]
        noise = random.gauss(0, self.sensor_noise[sensor_type])
        value = base_value + noise
        
        # Higher noise means higher uncertainty
        uncertainty = abs(noise) / base_value if base_value != 0 else self.sensor_noise[sensor_type]
        
        reading = SensorReading(
            sensor_type=sensor_type,
            value=value,
            uncertainty=uncertainty
        )
        
        self.readings.append(reading)
        return reading
    
    def read_all_sensors(self) -> List[SensorReading]:
        """Read all available sensors and return the readings."""
        return [self.read_sensor(sensor) for sensor in self.available_sensors]
    
    def update_environment(self, environment_state: Dict[str, Any]) -> None:
        """Update sensor values based on the environment state."""
        for sensor in self.available_sensors:
            # Map environment state to sensor values
            if sensor == SensorType.VISUAL and "visible_objects" in environment_state:
                self.current_values[sensor] = len(environment_state["visible_objects"])
            elif sensor == SensorType.AUDIO and "sound_level" in environment_state:
                self.current_values[sensor] = environment_state["sound_level"]
            elif sensor == SensorType.PROXIMITY and "nearest_object_distance" in environment_state:
                self.current_values[sensor] = environment_state["nearest_object_distance"]
            elif sensor == SensorType.ENERGY and "available_energy" in environment_state:
                self.current_values[sensor] = environment_state["available_energy"]
            elif sensor == SensorType.INTERNAL:
                # Internal sensors measure the lifeform's own state
                self.current_values[sensor] = random.uniform(0.7, 1.0)  # Simulating internal state

class BehaviorSystem:
    """Manages behaviors and decision-making for the artificial lifeform"""
    
    def __init__(self):
        """Initialize the behavior system."""
        self.action_history = []  # History of actions taken
        
        # Initial weights for different behaviors
        self.behavior_weights = {
            ActionType.MOVE: 0.8,
            ActionType.OBSERVE: 1.0,
            ActionType.CONSUME: 0.9,
            ActionType.REST: 0.5,
            ActionType.EXPLORE: 0.7,
            ActionType.COMMUNICATE: 0.4
        }
        
        # Energy costs for different actions
        self.energy_costs = {
            ActionType.MOVE: 2.0,
            ActionType.OBSERVE: 0.5,
            ActionType.CONSUME: 1.0,
            ActionType.REST: -3.0,  # Resting recovers energy
            ActionType.EXPLORE: 2.5,
            ActionType.COMMUNICATE: 1.5
        }
        
        # Uncertainty factors for different aspects of decision-making
        self.uncertainty_factors = {
            "action_selection": 0.1,
            "action_outcome": 0.15,
            "environment_model": 0.2
        }
    
    def select_action(self, sensor_readings: List[SensorReading], energy_level: float) -> Action:
        """Select the next action based on sensor readings and current state."""
        # Filter out actions that cost too much energy
        available_actions = [
            action for action in ActionType 
            if energy_level + self.energy_costs[action] >= 0
        ]
        
        if not available_actions:
            # If we're out of energy, force a rest action
            selected_action = ActionType.REST
        else:
            # Calculate a score for each action
            action_scores = {}
            for action in available_actions:
                base_score = self.behavior_weights[action]
                
                # Apply modifiers based on sensor readings
                for reading in sensor_readings:
                    if action == ActionType.CONSUME and reading.sensor_type == SensorType.ENERGY:
                        # Higher energy reading makes consumption more attractive
                        base_score *= (1.0 + reading.value * 0.1)
                    elif action == ActionType.OBSERVE and reading.sensor_type == SensorType.VISUAL:
                        # Higher visual activity makes observation more attractive
                        base_score *= (1.0 + reading.value * 0.05)
                    elif action == ActionType.REST and energy_level < 50:
                        # More rest when energy is low
                        base_score *= (2.0 - energy_level / 50)
                
                # Add some randomness to the decision
                noise = random.gauss(0, self.uncertainty_factors["action_selection"])
                action_scores[action] = base_score * (1.0 + noise)
            
            # Select the action with the highest score
            selected_action = max(action_scores, key=action_scores.get)
        
        # Generate parameters for the action
        parameters = self._generate_action_parameters(selected_action)
        
        # Create and return the action
        action = Action(
            action_type=selected_action,
            parameters=parameters,
            energy_cost=self.energy_costs[selected_action]
        )
        
        self.action_history.append(action)
        return action
    
    def _generate_action_parameters(self, action_type: ActionType) -> Dict[str, Any]:
        """Generate parameters for a specific action type."""
        parameters = {}
        
        if action_type == ActionType.MOVE:
            parameters["direction"] = random.choice(["north", "south", "east", "west"])
            parameters["speed"] = random.uniform(0.5, 1.5)
        elif action_type == ActionType.OBSERVE:
            parameters["focus"] = random.choice(["wide", "narrow"])
            parameters["duration"] = random.uniform(0.5, 2.0)
        elif action_type == ActionType.CONSUME:
            parameters["target"] = "energy_source"
            parameters["amount"] = random.uniform(0.5, 2.0)
        elif action_type == ActionType.EXPLORE:
            parameters["radius"] = random.uniform(1.0, 5.0)
            parameters["thoroughness"] = random.uniform(0.3, 0.9)
        elif action_type == ActionType.COMMUNICATE:
            parameters["message"] = "status_update"
            parameters["recipient"] = "all"
        
        return parameters
    
    def evaluate_action_success(self, action: Action, environment_state: Dict[str, Any]) -> bool:
        """Evaluate whether an action was successful given the environment state."""
        # Simulate success probability based on action type and environment
        base_probability = 0.8  # 80% success by default
        
        # Adjust based on action type
        if action.action_type == ActionType.MOVE:
            # Movement success depends on obstacles in environment
            if "obstacles" in environment_state:
                base_probability -= len(environment_state["obstacles"]) * 0.1
        elif action.action_type == ActionType.CONSUME:
            # Consumption success depends on available energy
            if "available_energy" in environment_state:
                if environment_state["available_energy"] < action.parameters.get("amount", 0):
                    base_probability *= 0.5  # Half as likely to succeed if not enough energy
        
        # Apply uncertainty
        adjusted_probability = base_probability * (1.0 - self.uncertainty_factors["action_outcome"])
        
        # Determine success
        return random.random() < adjusted_probability
    
    def adapt_behaviors(self, performance_metrics: Dict[str, float]) -> None:
        """Adapt behavior weights based on performance metrics."""
        # Get relevant metrics
        survival_performance = performance_metrics.get("survival", 0.5)
        efficiency_performance = performance_metrics.get("efficiency", 0.5)
        
        # Look at recent actions to see what's working
        recent_actions = self.action_history[-10:] if len(self.action_history) >= 10 else self.action_history
        action_counts = {}
        for action in recent_actions:
            action_type = action.action_type
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        # If we're doing well, reinforce current behavior
        if survival_performance > 0.7 and efficiency_performance > 0.7:
            for action_type, count in action_counts.items():
                proportion = count / len(recent_actions)
                # Reinforce actions that were used more frequently
                self.behavior_weights[action_type] *= (1.0 + proportion * 0.1)
                
        # If we're doing poorly, explore different actions
        elif survival_performance < 0.3 or efficiency_performance < 0.3:
            for action_type in ActionType:
                if action_type in action_counts:
                    proportion = action_counts[action_type] / len(recent_actions)
                    # Reduce weight for frequently used actions
                    self.behavior_weights[action_type] *= (1.0 - proportion * 0.1)
                else:
                    # Increase weight for unused actions
                    self.behavior_weights[action_type] *= 1.1
        
        # Update uncertainty based on performance
        performance_avg = (survival_performance + efficiency_performance) / 2
        uncertainty_modifier = 1.0 - performance_avg  # Lower performance means higher uncertainty
        
        for factor in self.uncertainty_factors:
            self.uncertainty_factors[factor] *= (0.9 + uncertainty_modifier * 0.2)
            # Keep uncertainty in reasonable bounds
            self.uncertainty_factors[factor] = max(0.05, min(0.5, self.uncertainty_factors[factor]))
        
        # Ensure weights stay in reasonable range
        for action_type in self.behavior_weights:
            self.behavior_weights[action_type] = max(0.1, min(2.0, self.behavior_weights[action_type]))

class ArtificialLifeform:
    """Represents an artificial lifeform with sensing, decision-making and adaptive capabilities"""
    
    def __init__(self, name: str, enable_self_awareness: bool = True):
        """Initialize the artificial lifeform."""
        self.name = name
        self.energy = 100.0  # Starting energy
        self.age = 0  # Age in time steps
        self.alive = True
        
        # Initialize subsystems
        self.sensors = SensorSystem()
        self.behaviors = BehaviorSystem()
        
        # Performance metrics
        self.performance_metrics = {
            "survival": 1.0,
            "efficiency": 0.5,
            "learning": 0.0,
            "adaptation": 0.0
        }
        
        # Environment state
        self.environment_state = self._generate_initial_environment()
        
        # State history for analysis
        self.state_history = []
        
        # Self-awareness integration
        self.enable_self_awareness = enable_self_awareness and HAS_SELF_AWARENESS
        self.awareness = None
        
        if self.enable_self_awareness:
            self.connect_to_awareness_framework()
    
    def _generate_initial_environment(self) -> Dict[str, Any]:
        """Generate an initial environment state."""
        return {
            "visible_objects": random.randint(1, 5),
            "sound_level": random.uniform(0.1, 0.5),
            "nearest_object_distance": random.uniform(1.0, 10.0),
            "available_energy": random.uniform(10.0, 50.0),
            "obstacles": random.randint(0, 3),
            "temperature": random.uniform(15.0, 25.0),
            "time_of_day": random.uniform(0.0, 1.0)  # 0.0 = midnight, 0.5 = noon, 1.0 = midnight
        }
    
    def update_environment(self) -> None:
        """Update the environment state."""
        # Gradually change the environment
        self.environment_state["visible_objects"] = max(0, min(10, 
            self.environment_state["visible_objects"] + random.randint(-1, 1)))
        
        self.environment_state["sound_level"] = max(0.0, min(1.0,
            self.environment_state["sound_level"] + random.uniform(-0.1, 0.1)))
        
        self.environment_state["nearest_object_distance"] = max(0.1, min(20.0,
            self.environment_state["nearest_object_distance"] + random.uniform(-0.5, 0.5)))
        
        self.environment_state["available_energy"] = max(0.0, min(100.0,
            self.environment_state["available_energy"] + random.uniform(-2.0, 1.0)))
        
        self.environment_state["obstacles"] = max(0, min(10,
            self.environment_state["obstacles"] + random.choice([-1, 0, 0, 0, 1])))
        
        self.environment_state["temperature"] = max(0.0, min(40.0,
            self.environment_state["temperature"] + random.uniform(-0.5, 0.5)))
        
        time_change = random.uniform(0.01, 0.05)  # Time passes
        self.environment_state["time_of_day"] = (self.environment_state["time_of_day"] + time_change) % 1.0
        
        # Update sensor system with new environment state
        self.sensors.update_environment(self.environment_state)
    
    def step(self) -> None:
        """Execute one time step in the lifeform's lifecycle."""
        if not self.alive:
            logger.warning(f"Lifeform {self.name} is no longer alive")
            return
        
        # Increase age
        self.age += 1
        
        # Consume base energy for staying alive
        self.energy -= 0.5
        
        # Update the environment
        self.update_environment()
        
        # Read sensors
        sensor_readings = self.sensors.read_all_sensors()
        
        # Select an action
        action = self.behaviors.select_action(sensor_readings, self.energy)
        
        # Apply energy cost
        self.energy += action.energy_cost
        
        # Evaluate success
        action.success = self.behaviors.evaluate_action_success(action, self.environment_state)
        
        # Handle action outcomes
        if action.action_type == ActionType.CONSUME and action.success:
            energy_gained = action.parameters.get("amount", 1.0) * self.environment_state["available_energy"] * 0.1
            self.energy += energy_gained
            self.environment_state["available_energy"] -= energy_gained
            action.outcomes["energy_gained"] = energy_gained
        
        # Update performance metrics
        self._update_performance_metrics()
        
        # Record state for history
        self._record_state(action)
        
        # Check if the lifeform is still alive
        if self.energy <= 0:
            self.alive = False
            logger.warning(f"Lifeform {self.name} has run out of energy and is no longer alive")
        
        # Every 10 steps, adapt behaviors based on performance
        if self.age % 10 == 0:
            self.behaviors.adapt_behaviors(self.performance_metrics)
        
        # Report metrics to self-awareness framework if enabled
        if self.enable_self_awareness and self.awareness and self.awareness.connected:
            decision_confidence = 1.0 - self.behaviors.uncertainty_factors["action_selection"]
            action_complexity = len(action.parameters) + 1.0
            
            self.awareness.update_decision_metrics(
                confidence=decision_confidence,
                complexity=action_complexity,
                execution_time=0.1  # Simulated execution time
            )
    
    def _update_performance_metrics(self) -> None:
        """Update the lifeform's performance metrics."""
        # Survival metric based on energy level
        self.performance_metrics["survival"] = self.energy / 100.0
        
        # Efficiency metric based on recent actions
        recent_actions = self.behaviors.action_history[-10:] if len(self.behaviors.action_history) >= 10 else self.behaviors.action_history
        if not recent_actions:
            return
            
        energy_balance = 0.0
        for action in recent_actions:
            energy_balance += action.energy_cost
            if action.action_type == ActionType.CONSUME and action.success:
                energy_balance += action.outcomes.get("energy_gained", 0.0)
        
        # Higher is better
        efficiency_score = 0.5 + (energy_balance / len(recent_actions)) / 10.0
        self.performance_metrics["efficiency"] = max(0.0, min(1.0, efficiency_score))
        
        # Learning metric increases slowly over time
        self.performance_metrics["learning"] = min(1.0, 0.5 + self.age / 1000.0)
        
        # Adaptation metric based on change in behavior weights
        # This is simplified; real adaptation would be more complex
        self.performance_metrics["adaptation"] = min(1.0, sum(self.behaviors.behavior_weights.values()) / 12.0)
    
    def _record_state(self, action: Action) -> None:
        """Record the current state in history."""
        state = {
            "age": self.age,
            "energy": self.energy,
            "action": {
                "type": action.action_type.value,
                "energy_cost": action.energy_cost,
                "success": action.success,
                "outcomes": action.outcomes
            },
            "environment": self.environment_state.copy(),
            "performance": self.performance_metrics.copy(),
            "timestamp": time.time()
        }
        self.state_history.append(state)
    
    def handle_insight(self, insight_data: Dict[str, Any]) -> None:
        """Process insights received from the self-awareness framework."""
        logger.info(f"Lifeform {self.name} received insight: {insight_data}")
        
        if "resource_efficiency" in insight_data:
            efficiency = insight_data["resource_efficiency"]["score"]
            if efficiency < 50:
                # Adjust behavior based on efficiency insights
                self.behaviors.behavior_weights[ActionType.REST] *= 1.2
                self.behaviors.behavior_weights[ActionType.EXPLORE] *= 0.8
                logger.info(f"Lifeform {self.name} adjusted behavior weights due to efficiency insights")
        
        if "decision_quality" in insight_data:
            decision_score = insight_data["decision_quality"]["score"]
            if decision_score < 0.6:
                # Reduce uncertainty if decision quality is low
                for factor in self.behaviors.uncertainty_factors:
                    self.behaviors.uncertainty_factors[factor] *= 0.9
                logger.info(f"Lifeform {self.name} reduced uncertainty factors due to decision quality insights")
    
    def handle_alert(self, alert_data: Dict[str, Any]) -> None:
        """Handle alerts from the self-awareness framework."""
        logger.warning(f"Lifeform {self.name} received alert: {alert_data['message']}")
        
        # React to high memory usage alert
        if alert_data.get("category") == "resource" and "memory" in alert_data.get("message", ""):
            logger.warning(f"Lifeform {self.name} performing memory optimization.")
            self.memory_optimization()
    
    def memory_optimization(self) -> None:
        """Optimize memory usage."""
        # Clear unnecessary sensor history
        if len(self.sensors.readings) > 100:
            self.sensors.readings = self.sensors.readings[-50:]
        
        # Clear behavior history if it's getting too large
        if len(self.behaviors.action_history) > 100:
            self.behaviors.action_history = self.behaviors.action_history[-50:]
        
        # Clear state history if it's getting too large
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-50:]
        
        # Run garbage collection
        gc.collect()
    
    def connect_to_awareness_framework(self) -> None:
        """Connect to the self-awareness framework."""
        if not HAS_SELF_AWARENESS:
            logger.warning("Self-awareness client not available")
            return
            
        try:
            # Create client and connect to the framework
            self.awareness = SelfAwarenessClient()
            self.awareness.connect()
            
            # Register handlers for insights and alerts
            self.awareness.add_insight_handler(self.handle_insight)
            self.awareness.add_alert_handler(self.handle_alert)
            
            logger.info(f"Lifeform {self.name} connected to self-awareness framework")
        except Exception as e:
            logger.error(f"Failed to connect to self-awareness framework: {e}")
            self.awareness = None
    
    def disconnect_from_awareness_framework(self) -> None:
        """Disconnect from the self-awareness framework."""
        if self.awareness and self.awareness.connected:
            self.awareness.disconnect()
            logger.info(f"Lifeform {self.name} disconnected from self-awareness framework")
    
    def save_state(self, filepath: str) -> None:
        """Save the lifeform's state and history to a file."""
        data = {
            "name": self.name,
            "energy": self.energy,
            "age": self.age,
            "alive": self.alive,
            "performance_metrics": self.performance_metrics,
            "behavior_weights": {k.value: v for k, v in self.behaviors.behavior_weights.items()},
            "uncertainty_factors": self.behaviors.uncertainty_factors,
            "state_history": self.state_history
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Lifeform {self.name} state saved to {filepath}")
    
    def load_state(self, filepath: str) -> bool:
        """Load the lifeform's state and history from a file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.name = data["name"]
            self.energy = data["energy"]
            self.age = data["age"]
            self.alive = data["alive"]
            self.performance_metrics = data["performance_metrics"]
            
            # Convert behavior weights back to enum keys
            self.behaviors.behavior_weights = {
                ActionType(k): v for k, v in data["behavior_weights"].items()
            }
            
            self.behaviors.uncertainty_factors = data["uncertainty_factors"]
            self.state_history = data["state_history"]
            
            logger.info(f"Lifeform {self.name} state loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to load lifeform state: {e}")
            return False

class Environment:
    """Simulates the environment in which the artificial lifeform exists"""
    
    def __init__(self, complexity: float = 0.5):
        """Initialize the environment with a specific complexity level."""
        self.complexity = complexity  # 0.0 to 1.0, higher means more complex/dynamic
        self.state = {
            "obstacles": int(complexity * 10),
            "rewards": int((1.0 - complexity) * 10),
            "environment": random.uniform(0.3, 0.7)
        }
        self.history = []
        self.timestamp = time.time()
    
    def update(self) -> Dict[str, Any]:
        """Update the environment state."""
        # Record current state in history
        self.history.append(self.state.copy())
        
        # Update the state based on complexity
        change_factor = self.complexity * 0.2
        
        # Obstacles change more in complex environments
        self.state["obstacles"] = max(0, min(20, 
            self.state["obstacles"] + random.randint(-1, 1) * change_factor * 10))
        
        # Rewards are less reliable in complex environments
        self.state["rewards"] = max(0, min(20,
            self.state["rewards"] + random.randint(-1, 1) * (1.0 - change_factor) * 5))
        
        # Environment conditions fluctuate based on complexity
        self.state["environment"] = max(0.0, min(1.0,
            self.state["environment"] + random.uniform(-0.1, 0.1) * change_factor))
        
        self.timestamp = time.time()
        return self.state
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the environment."""
        return self.state.copy()
    
    def get_analysis(self) -> Dict[str, Any]:
        """Analyze the environment history."""
        if not self.history:
            return {}

        # Calculate statistics about the environment
        obstacles = [state["obstacles"] for state in self.history]
        rewards = [state["rewards"] for state in self.history]
        conditions = [state["environment"] for state in self.history]

        return {
            "avg_obstacle_level": sum(obstacles) / len(obstacles),
            "avg_reward_level": sum(rewards) / len(rewards),
            "avg_environmental_condition": sum(conditions) / len(conditions),
            "environment_stability": 1.0 - np.std(conditions),
            "environment_complexity": self.complexity,
        }

# ==========================================
# Simulation Management Classes
# ==========================================

class SimulationManager:
    """Manages the simulation of artificial lifeforms in an environment"""
    
    def __init__(self, lifeform: ArtificialLifeform, environment: Environment):
        """Initialize the simulation manager."""
        self.lifeform = lifeform
        self.environment = environment
        self.running = False
        self.thread = None
        self.iteration = 0
        self.max_iterations = 0
        self.data = {
            "iterations": [],
            "energy_levels": [],
            "environment_conditions": [],
            "behavior_weights": {action_type.value: [] for action_type in ActionType},
            "performance_metrics": {metric: [] for metric in ["survival", "efficiency", "learning", "adaptation"]},
            "obstacles": [],
            "rewards": []
        }
        self.simulation_id = f"sim_{int(time.time())}"
        self.log_directory = "simulation_logs"
        os.makedirs(self.log_directory, exist_ok=True)
    
    def run_simulation(self, num_iterations: int, log_interval: int = 10) -> None:
        """Run the simulation for a specified number of iterations.
        
        Args:
            num_iterations: Number of iterations to run
            log_interval: How often to log data (every N iterations)
        """
        self.running = True
        self.max_iterations = num_iterations
        self.iteration = 0
        
        logger.info(f"Starting simulation {self.simulation_id} for {num_iterations} iterations")
        
        start_time = time.time()
        
        try:
            while self.running and self.iteration < num_iterations and self.lifeform.alive:
                # Update the environment
                env_state = self.environment.update()
                
                # Update the lifeform
                self.lifeform.step()
                
                # Record data at specified intervals
                if self.iteration % log_interval == 0:
                    self._record_data()
                
                self.iteration += 1
                
                # Save snapshot at regular intervals
                if self.iteration % 1000 == 0:
                    self._save_snapshot()
            
            # Final data recording
            self._record_data()
            
            # Save final state
            self._save_final_state()
            
            elapsed_time = time.time() - start_time
            logger.info(f"Simulation completed after {self.iteration} iterations in {elapsed_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error during simulation: {e}")
            raise
        finally:
            self.running = False
    
    def run_simulation_async(self, num_iterations: int, log_interval: int = 10) -> None:
        """Run the simulation asynchronously in a separate thread.
        
        Args:
            num_iterations: Number of iterations to run
            log_interval: How often to log data (every N iterations)
        """
        if self.running:
            logger.warning("Simulation is already running")
            return
        
        self.thread = threading.Thread(
            target=self.run_simulation, 
            args=(num_iterations, log_interval)
        )
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"Simulation {self.simulation_id} started in background thread")
    
    def stop_simulation(self) -> None:
        """Stop the simulation if it's running."""
        if not self.running:
            logger.info("No simulation is currently running")
            return
        
        logger.info("Stopping simulation...")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
            if self.thread.is_alive():
                logger.warning("Thread did not terminate gracefully")
        
        logger.info(f"Simulation stopped after {self.iteration} iterations")
    
    def _record_data(self) -> None:
        """Record current simulation data."""
        self.data["iterations"].append(self.iteration)
        self.data["energy_levels"].append(self.lifeform.energy)
        
        # Record environment conditions
        env_state = self.environment.get_state()
        self.data["environment_conditions"].append(env_state["environment"])
        self.data["obstacles"].append(env_state["obstacles"])
        self.data["rewards"].append(env_state["rewards"])
        
        # Record behavior weights
        for action_type in ActionType:
            weight = self.lifeform.behaviors.behavior_weights[action_type]
            self.data["behavior_weights"][action_type.value].append(weight)
        
        # Record performance metrics
        for metric, value in self.lifeform.performance_metrics.items():
            self.data["performance_metrics"][metric].append(value)
    
    def _save_snapshot(self) -> None:
        """Save a snapshot of the current simulation state."""
        snapshot_path = os.path.join(
            self.log_directory, 
            f"{self.simulation_id}_{self.iteration}.json"
        )
        
        with open(snapshot_path, 'w') as f:
            json.dump({
                "simulation_id": self.simulation_id,
                "iteration": self.iteration,
                "timestamp": time.time(),
                "lifeform": {
                    "name": self.lifeform.name,
                    "energy": self.lifeform.energy,
                    "age": self.lifeform.age,
                    "alive": self.lifeform.alive,
                    "behavior_weights": {k.value: v for k, v in self.lifeform.behaviors.behavior_weights.items()},
                    "uncertainty_factors": self.lifeform.behaviors.uncertainty_factors,
                    "performance_metrics": self.lifeform.performance_metrics
                },
                "environment": self.environment.get_state(),
                "data": self.data
            }, f, indent=2)
    
    def _save_final_state(self) -> None:
        """Save the final state of the simulation."""
        final_path = os.path.join(
            self.log_directory, 
            f"{self.simulation_id}_final.json"
        )
        
        with open(final_path, 'w') as f:
            json.dump({
                "simulation_id": self.simulation_id,
                "iterations_completed": self.iteration,
                "max_iterations": self.max_iterations,
                "ended_naturally": self.iteration >= self.max_iterations or not self.lifeform.alive,
                "lifeform_survived": self.lifeform.alive,
                "timestamp": time.time(),
                "lifeform": {
                    "name": self.lifeform.name,
                    "energy": self.lifeform.energy,
                    "age": self.lifeform.age,
                    "alive": self.lifeform.alive,
                    "behavior_weights": {k.value: v for k, v in self.lifeform.behaviors.behavior_weights.items()},
                    "uncertainty_factors": self.lifeform.behaviors.uncertainty_factors,
                    "performance_metrics": self.lifeform.performance_metrics
                },
                "environment": {
                    "current_state": self.environment.get_state(),
                    "analysis": self.environment.get_analysis()
                },
                "data": self.data
            }, f, indent=2)
        
        logger.info(f"Final simulation state saved to {final_path}")
    
    def save_simulation_data(self, filepath: str) -> None:
        """Save simulation data to a file.
        
        Args:
            filepath: Path to save the data
        """
        with open(filepath, 'w') as f:
            json.dump({
                "simulation_id": self.simulation_id,
                "iterations_completed": self.iteration,
                "timestamp": time.time(),
                "data": self.data
            }, f, indent=2)
        
        logger.info(f"Simulation data saved to {filepath}")
    
    def load_simulation_data(self, filepath: str) -> bool:
        """Load simulation data from a file.
        
        Args:
            filepath: Path to the data file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.simulation_id = data["simulation_id"]
            self.iteration = data["iterations_completed"]
            self.data = data["data"]
            
            logger.info(f"Simulation data loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to load simulation data: {e}")
            return False


class SimulationVisualizer:
    """Visualizes the results of cognitive simulations"""
    
    def __init__(self, log_directory: str = "simulation_logs"):
        """Initialize the visualization system.
        
        Args:
            log_directory: Directory containing simulation logs
        """
        self.log_directory = log_directory
        
        # Check if matplotlib is available
        try:
            import matplotlib.pyplot as plt
            self.plt = plt
            self.has_matplotlib = True
        except ImportError:
            logger.warning("Matplotlib not available. Visualization capabilities will be limited.")
            self.has_matplotlib = False
    
    def load_simulation_data(self, simulation_id: str) -> Dict[str, Any]:
        """Load data for a specific simulation.
        
        Args:
            simulation_id: ID of the simulation to load
            
        Returns:
            Dictionary containing simulation data
        """
        final_path = os.path.join(self.log_directory, f"{simulation_id}_final.json")
        
        if not os.path.exists(final_path):
            logger.error(f"Simulation data not found: {final_path}")
            return {}
        
        try:
            with open(final_path, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Loaded simulation data for {simulation_id}")
            return data
        except Exception as e:
            logger.error(f"Failed to load simulation data: {e}")
            return {}
    
    def get_latest_simulation_id(self) -> Optional[str]:
        """Get the ID of the most recent simulation.
        
        Returns:
            Simulation ID or None if no simulations are found
        """
        if not os.path.exists(self.log_directory):
            return None
        
        files = [f for f in os.listdir(self.log_directory) if f.endswith('_final.json')]
        if not files:
            return None
        
        # Sort by modification time, newest first
        files.sort(key=lambda x: os.path.getmtime(os.path.join(self.log_directory, x)), reverse=True)
        
        # Extract simulation ID from filename
        latest_file = files[0]
        simulation_id = latest_file.replace('_final.json', '')
        
        return simulation_id
    
    def plot_energy_levels(self, simulation_id: Optional[str] = None, show: bool = True) -> None:
        """Plot energy levels over time.
        
        Args:
            simulation_id: ID of the simulation to visualize (default: latest)
            show: Whether to display the plot
        """
        if not self.has_matplotlib:
            logger.error("Matplotlib is required for plotting")
            return
        
        if simulation_id is None:
            simulation_id = self.get_latest_simulation_id()
            if simulation_id is None:
                logger.error("No simulation data found")
                return
        
        data = self.load_simulation_data(simulation_id)
        if not data:
            return
        
        iterations = data["data"]["iterations"]
        energy_levels = data["data"]["energy_levels"]
        
        plt = self.plt
        plt.figure(figsize=(10, 6))
        plt.plot(iterations, energy_levels, label="Energy Level")
        plt.title(f"Energy Levels Over Time - {simulation_id}")
        plt.xlabel("Iteration")
        plt.ylabel("Energy")
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        if show:
            plt.show()
    
    def plot_environmental_conditions(self, simulation_id: Optional[str] = None, show: bool = True) -> None:
        """Plot environmental conditions over time.
        
        Args:
            simulation_id: ID of the simulation to visualize (default: latest)
            show: Whether to display the plot
        """
        if not self.has_matplotlib:
            logger.error("Matplotlib is required for plotting")
            return
        
        if simulation_id is None:
            simulation_id = self.get_latest_simulation_id()
            if simulation_id is None:
                logger.error("No simulation data found")
                return
        
        data = self.load_simulation_data(simulation_id)
        if not data:
            return
        
        iterations = data["data"]["iterations"]
        env_conditions = data["data"]["environment_conditions"]
        obstacles = data["data"]["obstacles"]
        rewards = data["data"]["rewards"]
        
        plt = self.plt
        plt.figure(figsize=(12, 8))
        
        plt.subplot(3, 1, 1)
        plt.plot(iterations, env_conditions, label="Environmental Condition", color="green")
        plt.title(f"Environmental Conditions - {simulation_id}")
        plt.ylabel("Condition Level")
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.subplot(3, 1, 2)
        plt.plot(iterations, obstacles, label="Obstacles", color="red")
        plt.ylabel("Obstacle Level")
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.subplot(3, 1, 3)
        plt.plot(iterations, rewards, label="Rewards", color="blue")
        plt.xlabel("Iteration")
        plt.ylabel("Reward Level")
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        
        if show:
            plt.show()
    
    def plot_performance_metrics(self, simulation_id: Optional[str] = None, show: bool = True) -> None:
        """Plot performance metrics over time.
        
        Args:
            simulation_id: ID of the simulation to visualize (default: latest)
            show: Whether to display the plot
        """
        if not self.has_matplotlib:
            logger.error("Matplotlib is required for plotting")
            return
        
        if simulation_id is None:
            simulation_id = self.get_latest_simulation_id()
            if simulation_id is None:
                logger.error("No simulation data found")
                return
        
        data = self.load_simulation_data(simulation_id)
        if not data:
            return
        
        iterations = data["data"]["iterations"]
        metrics = data["data"]["performance_metrics"]
        
        plt = self.plt
        plt.figure(figsize=(12, 8))
        
        colors = {
            "survival": "red",
            "efficiency": "blue",
            "learning": "green",
            "adaptation": "purple"
        }
        
        for i, (metric, values) in enumerate(metrics.items(), 1):
            plt.subplot(2, 2, i)
            plt.plot(iterations, values, label=metric.capitalize(), color=colors.get(metric, "black"))
            plt.title(f"{metric.capitalize()} Over Time")
            plt.xlabel("Iteration")
            plt.ylabel("Score")
            plt.ylim(0, 1.1)
            plt.grid(True, alpha=0.3)
            plt.legend()
        
        plt.tight_layout()
        plt.suptitle(f"Performance Metrics - {simulation_id}", y=1.02)
        
        if show:
            plt.show()
    
    def plot_behavior_weights(self, simulation_id: Optional[str] = None, show: bool = True) -> None:
        """Plot behavior weights evolution over time.
        
        Args:
            simulation_id: ID of the simulation to visualize (default: latest)
            show: Whether to display the plot
        """
        if not self.has_matplotlib:
            logger.error("Matplotlib is required for plotting")
            return
        
        if simulation_id is None:
            simulation_id = self.get_latest_simulation_id()
            if simulation_id is None:
                logger.error("No simulation data found")
                return
        
        data = self.load_simulation_data(simulation_id)
        if not data:
            return
        
        iterations = data["data"]["iterations"]
        behavior_weights = data["data"]["behavior_weights"]
        
        plt = self.plt
        plt.figure(figsize=(12, 6))
        
        colors = {
            "move": "blue",
            "observe": "green",
            "consume": "red",
            "rest": "purple",
            "explore": "orange",
            "communicate": "brown"
        }
        
        for behavior, weights in behavior_weights.items():
            plt.plot(iterations, weights, label=behavior.capitalize(), color=colors.get(behavior, "black"))
        
        plt.title(f"Behavior Weight Evolution - {simulation_id}")
        plt.xlabel("Iteration")
        plt.ylabel("Weight")
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        if show:
            plt.show()
    
    def generate_summary_report(self, simulation_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate a comprehensive summary report of the simulation.
        
        Args:
            simulation_id: ID of the simulation to summarize (default: latest)
            
        Returns:
            Dictionary containing summary data
        """
        if simulation_id is None:
            simulation_id = self.get_latest_simulation_id()
            if simulation_id is None:
                logger.error("No simulation data found")
                return {}
        
        data = self.load_simulation_data(simulation_id)
        if not data:
            return {}
        
        # Calculate summary statistics
        lifeform_data = data.get("lifeform", {})
        env_data = data.get("environment", {})
        sim_data = data.get("data", {})
        
        # Basic information
        summary = {
            "simulation_id": simulation_id,
            "iterations": data.get("iterations_completed", 0),
            "lifeform_survived": data.get("lifeform_survived", False),
            "timestamp": data.get("timestamp", 0),
            "run_date": datetime.fromtimestamp(data.get("timestamp", 0)).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Lifeform final state
        summary["final_energy"] = lifeform_data.get("energy", 0)
        summary["age"] = lifeform_data.get("age", 0)
        summary["final_performance"] = lifeform_data.get("performance_metrics", {})
        
        # Environment statistics
        summary["environment"] = env_data.get("analysis", {})
        
        # Calculate averages for metrics
        metrics = sim_data.get("performance_metrics", {})
        summary["average_metrics"] = {}
        for metric, values in metrics.items():
            if values:
                summary["average_metrics"][metric] = sum(values) / len(values)
        
        # Calculate behavior weight changes
        behavior_weights = sim_data.get("behavior_weights", {})
        summary["behavior_changes"] = {}
        for behavior, weights in behavior_weights.items():
            if weights and len(weights) >= 2:
                initial = weights[0]
                final = weights[-1]
                change = final - initial
                percent_change = (change / initial * 100) if initial != 0 else float('inf')
                summary["behavior_changes"][behavior] = {
                    "initial": initial,
                    "final": final,
                    "change": change,
                    "percent_change": percent_change
                }
        
        # Calculate energy statistics
        energy_levels = sim_data.get("energy_levels", [])
        if energy_levels:
            summary["energy_stats"] = {
                "min": min(energy_levels),
                "max": max(energy_levels),
                "average": sum(energy_levels) / len(energy_levels),
                "final": energy_levels[-1],
                "standard_deviation": np.std(energy_levels) if len(energy_levels) > 1 else 0
            }
        
        return summary
    
    def print_summary_report(self, simulation_id: Optional[str] = None) -> None:
        """Print a summary report of the simulation.
        
        Args:
            simulation_id: ID of the simulation to summarize (default: latest)
        """
        summary = self.generate_summary_report(simulation_id)
        if not summary:
            return
        
        print(f"\n{'='*80}")
        print(f"Simulation Summary: {summary['simulation_id']}")
        print(f"Run Date: {summary['run_date']}")
        print(f"{'='*80}")
        
        print(f"\nGeneral Information:")
        print(f"  Iterations completed: {summary['iterations']}")
        print(f"  Lifeform survived: {summary['lifeform_survived']}")
        print(f"  Final energy: {summary['final_energy']:.2f}")
        print(f"  Age: {summary['age']}")
        
        if "energy_stats" in summary:
            print(f"\nEnergy Statistics:")
            print(f"  Minimum: {summary['energy_stats']['min']:.2f}")
            print(f"  Maximum: {summary['energy_stats']['max']:.2f}")
            print(f"  Average: {summary['energy_stats']['average']:.2f}")
            print(f"  Standard Deviation: {summary['energy_stats']['standard_deviation']:.2f}")
        
        if "final_performance" in summary:
            print(f"\nFinal Performance Metrics:")
            for metric, value in summary["final_performance"].items():
                print(f"  {metric.capitalize()}: {value:.4f}")
        
        if "average_metrics" in summary:
            print(f"\nAverage Performance Metrics:")
            for metric, value in summary["average_metrics"].items():
                print(f"  {metric.capitalize()}: {value:.4f}")
        
        if "behavior_changes" in summary:
            print(f"\nBehavior Weight Changes:")
            for behavior, data in summary["behavior_changes"].items():
                print(f"  {behavior.capitalize()}: {data['initial']:.2f} → {data['final']:.2f} ({data['percent_change']:.1f}%)")
        
        if "environment" in summary:
            print(f"\nEnvironment Analysis:")
            for metric, value in summary["environment"].items():
                print(f"  {metric.replace('_', ' ').capitalize()}: {value:.4f}")
        
        print(f"\n{'='*80}")


class CognitiveAnalysis:
    """Advanced analysis of cognitive simulation data"""
    
    def __init__(self, log_directory: str = "simulation_logs"):
        """Initialize the cognitive analysis system.
        
        Args:
            log_directory: Directory containing simulation logs
        """
        self.log_directory = log_directory
        self.visualizer = SimulationVisualizer(log_directory)
        
        # Check for required libraries
        try:
            import pandas as pd
            from scipy import stats
            from sklearn.cluster import KMeans
            from sklearn.decomposition import PCA
            self.has_analysis_libs = True
        except ImportError:
            logger.warning("Advanced analysis libraries not available. Analysis capabilities will be limited.")
            self.has_analysis_libs = False
    
    def load_simulation_data_as_df(self, simulation_id: Optional[str] = None) -> pd.DataFrame:
        """Load simulation data and convert to pandas DataFrame for analysis.
        
        Args:
            simulation_id: ID of the simulation to analyze (default: latest)
            
        Returns:
            DataFrame containing simulation data
        """
        if not self.has_analysis_libs:
            logger.error("Pandas is required for DataFrame conversion")
            return pd.DataFrame()
        
        if simulation_id is None:
            simulation_id = self.visualizer.get_latest_simulation_id()
        
        if simulation_id is None:
            logger.error("No simulation logs found")
            raise ValueError("No simulation logs found")
        
        # Load raw data
        data = self.visualizer.load_simulation_data(simulation_id)
        
        if not data["data"]["iterations"]:
            raise ValueError(f"No data available for simulation {simulation_id}")
        
        # Create a basic DataFrame with iterations
        df = pd.DataFrame({"iteration": data["data"]["iterations"]})
        
        # Add energy levels
        if data["data"]["energy_levels"]:
            df["energy_level"] = data["data"]["energy_levels"]
        
        # Add environment data
        if data["data"]["obstacles"]:
            df["obstacles"] = data["data"]["obstacles"]
        if data["data"]["rewards"]:
            df["rewards"] = data["data"]["rewards"]
        if data["data"]["environment_conditions"]:
            df["environment_condition"] = data["data"]["environment_conditions"]
        
        # Add performance metrics
        for metric, values in data["data"]["performance_metrics"].items():
            if len(values) == len(data["data"]["iterations"]):
                df[f"metric_{metric}"] = values
        
        # Add behavior weights
        for behavior, values in data["data"]["behavior_weights"].items():
            if len(values) == len(data["data"]["iterations"]):
                df[f"weight_{behavior}"] = values
        
        return df
    
    def analyze_survival_factors(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze factors that contribute to survival.
        
        Args:
            df: DataFrame containing simulation data
            
        Returns:
            Dictionary with survival analysis
        """
        if "energy_level" not in df.columns:
            return {"error": "Energy level data not available"}

        results = {}

        # Check which factors correlate with energy level
        correlation_cols = [col for col in df.columns if col not in ("energy_level", "iteration")]
        if correlation_cols:
            correlations = {}
            for col in correlation_cols:
                if df[col].dtype in [np.float64, np.int64]:
                    corr = df["energy_level"].corr(df[col])
                    correlations[col] = corr
            
            # Sort by absolute correlation
            sorted_correlations = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
            results["correlations"] = sorted_correlations
            
            # Top positive and negative factors
            pos_factors = [(k, v) for k, v in sorted_correlations if v > 0][:3]
            neg_factors = [(k, v) for k, v in sorted_correlations if v < 0][:3]
            
            results["top_positive_factors"] = pos_factors
            results["top_negative_factors"] = neg_factors
        
        # Analyze energy trends
        results["energy_trends"] = {
            "initial": df["energy_level"].iloc[0],
            "final": df["energy_level"].iloc[-1],
            "min": df["energy_level"].min(),
            "max": df["energy_level"].max(),
            "mean": df["energy_level"].mean(),
            "median": df["energy_level"].median(),
            "std": df["energy_level"].std()
        }

        # Linear regression for energy trend over time
        x = df["iteration"].values.reshape(-1, 1)
        y = df["energy_level"].values
        slope, intercept, r_value, p_value, std_err = stats.linregress(x.flatten(), y)

        results["energy_regression"] = {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_value**2,
            "p_value": p_value,
            "std_err": std_err,
            "trend": "increasing" if slope > 0 else "decreasing",
            "significance": "significant" if p_value < 0.05 else "not significant"
        }

        return results
    
    def analyze_behavior_adaptation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze how behaviors adapt over time.
        
        Args:
            df: DataFrame containing simulation data
            
        Returns:
            Dictionary with behavior adaptation analysis
        """
        # Get behavior weight columns
        weight_cols = [col for col in df.columns if col.startswith("weight_")]
        if not weight_cols:
            return {"error": "Behavior weight data not available"}
        
        # Analysis of weight changes
        weight_changes = {}
        for col in weight_cols:
            behavior = col.replace("weight_", "")
            initial = df[col].iloc[0]
            final = df[col].iloc[-1]
            change = final - initial
            percent_change = (change / initial) * 100 if initial != 0 else float('inf')
            
            weight_changes[behavior] = {
                "initial": initial,
                "final": final,
                "change": change,
                "percent_change": percent_change
            }
        
        # Sort behaviors by amount of adaptation
        sorted_adaptation = sorted(
            [(k, abs(v["percent_change"])) for k, v in weight_changes.items()], 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Analyze if behaviors converge or diverge
        initial_variance = np.var([w["initial"] for w in weight_changes.values()])
        final_variance = np.var([w["final"] for w in weight_changes.values()])
        
        results = {
            "weight_changes": weight_changes,
            "most_adapted_behaviors": sorted_adaptation,
            "behavior_specialization": {
                "initial_variance": initial_variance,
                "final_variance": final_variance,
                "variance_change": final_variance - initial_variance,
                "pattern": "specializing" if final_variance > initial_variance else "generalizing"
            }
        }
        
        # Check if adaptation is still occurring at the end
        if len(df) > 10:
            recent_df = df.iloc[-10:]
            is_still_adapting = any(abs(recent_df[col].iloc[-1] - recent_df[col].iloc[0]) > 0.01 for col in weight_cols)
            results["adaptation_status"] = "still_adapting" if is_still_adapting else "stabilized"
        
        return results
    
    def analyze_environmental_impact(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze how the environment affects lifeform behavior and performance.
        
        Args:
            df: DataFrame containing simulation data
            
        Returns:
            Dictionary with environmental impact analysis
        """
        env_cols = ["environment_condition", "obstacles", "rewards"]

        if any(col not in df.columns for col in env_cols):
            return {"error": "Environment data not available"}

        # Correlations between environment and behaviors
        weight_cols = [col for col in df.columns if col.startswith("weight_")]

        env_behavior_corr = {}
        for env_col in env_cols:
            env_behavior_corr[env_col] = {}
            for weight_col in weight_cols:
                behavior = weight_col.replace("weight_", "")
                corr = df[env_col].corr(df[weight_col])
                env_behavior_corr[env_col][behavior] = corr

        results = {"environment_behavior_correlations": env_behavior_corr}
        
        # Check how environment affects energy levels
        if "energy_level" in df.columns:
            env_energy_corr = {}
            for env_col in env_cols:
                corr = df[env_col].corr(df["energy_level"])
                env_energy_corr[env_col] = corr

            results["environment_energy_correlations"] = env_energy_corr

            # Identify most challenging environmental conditions
            low_energy_periods = df[df["energy_level"] < 0.3]
            if not low_energy_periods.empty:
                avg_env_conditions = {
                    "environment_condition": low_energy_periods["environment_condition"].mean(),
                    "obstacles": low_energy_periods["obstacles"].mean(),
                    "rewards": low_energy_periods["rewards"].mean()
                }
                results["challenging_environments"] = avg_env_conditions

        # Environment stability analysis
        results["environment_stability"] = {
            "environment_condition_variance": df["environment_condition"].var(),
            "obstacles_variance": df["obstacles"].var(),
            "rewards_variance": df["rewards"].var()
        }

        return results
    
    def perform_cluster_analysis(self, df: pd.DataFrame, n_clusters: int = 3) -> Dict[str, Any]:
        """Identify different operational modes using clustering.
        
        Args:
            df: DataFrame containing simulation data
            n_clusters: Number of clusters to identify
            
        Returns:
            Dictionary with cluster analysis results
        """
        if not self.has_analysis_libs:
            return {"error": "sklearn is required for cluster analysis"}
        
        # Select numerical columns for clustering
        num_cols = [col for col in df.columns if df[col].dtype in [np.float64, np.int64] and col != "iteration"]
        if len(num_cols) < 3:
            return {"error": "Not enough numerical data for clustering"}
        
        # Prepare data for clustering
        X = df[num_cols].values
        
        # Normalize data
        X_norm = (X - X.mean(axis=0)) / X.std(axis=0)
        
        # Perform PCA to reduce dimensionality
        pca = PCA(n_components=min(3, len(num_cols)))
        X_pca = pca.fit_transform(X_norm)
        
        # Perform KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_pca)
        
        # Add cluster labels to DataFrame
        df_with_clusters = df.copy()
        df_with_clusters["cluster"] = clusters
        
        # Analyze clusters
        cluster_analysis = {}
        
        for i in range(n_clusters):
            cluster_df = df_with_clusters[df_with_clusters["cluster"] == i]
            
            # Calculate cluster statistics
            cluster_stats = {
                "size": len(cluster_df),
                "percentage": (len(cluster_df) / len(df)) * 100
            }
            
            # For each numerical column, calculate mean and std for this cluster
            for col in num_cols:
                cluster_stats[f"{col}_mean"] = cluster_df[col].mean()
                cluster_stats[f"{col}_std"] = cluster_df[col].std()
            
            cluster_analysis[f"cluster_{i}"] = cluster_stats
        
        # Determine operational modes based on clusters
        operational_modes = []
        for i in range(n_clusters):
            mode = self._create_operational_mode(i, cluster_analysis[f"cluster_{i}"], num_cols)
            operational_modes.append(mode)
        
        return {
            "pca_explained_variance": pca.explained_variance_ratio_.tolist(),
            "cluster_analysis": cluster_analysis,
            "operational_modes": operational_modes,
            "n_clusters": n_clusters
        }
    
    def _create_operational_mode(self, i: int, cluster_stats: Dict[str, Any], num_cols: List[str]) -> Dict[str, Any]:
        """Create an operational mode description for a cluster.
        
        Args:
            i: Cluster index
            cluster_stats: Statistics for the cluster
            num_cols: Numerical columns used for clustering
            
        Returns:
            Dictionary describing the operational mode
        """
        mode = {"cluster": i, "size_percentage": cluster_stats["percentage"]}
        
        # Check energy level
        if "energy_level_mean" in cluster_stats:
            energy_level = cluster_stats["energy_level_mean"]
            if energy_level > 0.7:
                mode["energy_status"] = "high"
            elif energy_level < 0.3:
                mode["energy_status"] = "critical"
            else:
                mode["energy_status"] = "moderate"
        
        # Check environment
        if "obstacles_mean" in cluster_stats and "rewards_mean" in cluster_stats:
            obstacles = cluster_stats["obstacles_mean"]
            rewards = cluster_stats["rewards_mean"]
            
            if obstacles > 0.6:
                mode["environment_type"] = "hostile"
            elif rewards > 0.5:
                mode["environment_type"] = "abundant"
            elif obstacles < 0.2 and rewards < 0.2:
                mode["environment_type"] = "barren"
            else:
                mode["environment_type"] = "balanced"
        
        # Check behavioral emphasis
        max_weight = -float('inf')
        dominant_behavior = None
        
        for col in [c for c in num_cols if c.startswith("weight_")]:
            behavior = col.replace("weight_", "")
            weight = cluster_stats[f"{col}_mean"]
            
            if weight > max_weight:
                max_weight = weight
                dominant_behavior = behavior
        
        if dominant_behavior:
            mode["dominant_behavior"] = dominant_behavior
        
        # Determine a descriptive name for this mode
        if all(key in mode for key in ["energy_status", "environment_type", "dominant_behavior"]):
            mode["name"] = f"{mode['energy_status']}_{mode['environment_type']}_{mode['dominant_behavior']}"
        else:
            mode["name"] = f"cluster_{i}"
        
        return mode
    
    def analyze_learning_effectiveness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze how effectively the lifeform learns and adapts.
        
        Args:
            df: DataFrame containing simulation data
            
        Returns:
            Dictionary with learning effectiveness analysis
        """
        if "metric_efficiency" not in df.columns or len(df) < 10:
            return {"error": "Efficiency metric data not available or insufficient data points"}

        # Split data into time segments
        segment_size = max(10, len(df) // 5)  # At least 10 points per segment, or 5 segments total
        segments = []

        for i in range(0, len(df), segment_size):
            segment = df.iloc[i:min(i + segment_size, len(df))]
            if len(segment) >= 5:  # Only include reasonably sized segments
                segments.append(segment)

        # Calculate learning metrics across segments
        learning_progression = []
        for i, segment in enumerate(segments):
            # Average efficiency in this segment
            avg_efficiency = segment["metric_efficiency"].mean()
            
            # Calculate stability (lower variance = more stable)
            efficiency_stability = 1.0 - segment["metric_efficiency"].var()
            
            # Energy conservation
            if "energy_level" in segment.columns:
                energy_stability = 1.0 - segment["energy_level"].var()
                avg_energy = segment["energy_level"].mean()
            else:
                energy_stability = None
                avg_energy = None
            
            segment_metrics = {
                "segment": i,
                "start_iteration": segment["iteration"].iloc[0],
                "end_iteration": segment["iteration"].iloc[-1],
                "avg_efficiency": avg_efficiency,
                "efficiency_stability": efficiency_stability,
                "avg_energy": avg_energy,
                "energy_stability": energy_stability
            }
            
            learning_progression.append(segment_metrics)

        results = {"learning_progression": learning_progression}

        # Calculate learning rate
        if len(learning_progression) >= 2:
            first_segment = learning_progression[0]
            last_segment = learning_progression[-1]
            
            efficiency_improvement = last_segment["avg_efficiency"] - first_segment["avg_efficiency"]
            stability_improvement = last_segment["efficiency_stability"] - first_segment["efficiency_stability"]
            
            # Calculate learning rate as combination of efficiency and stability improvements
            learning_rate = (efficiency_improvement + stability_improvement) / 2
            
            # Classify learning progress
            if learning_rate > 0.2:
                learning_category = "exceptional"
            elif learning_rate > 0.1:
                learning_category = "good"
            elif learning_rate > 0:
                learning_category = "moderate"
            elif learning_rate > -0.1:
                learning_category = "stagnant"
            else:
                learning_category = "regressing"
            
            results.update({
                "learning_rate": learning_rate,
                "learning_category": learning_category
            })

        # Check for plateaus in learning
        if "metric_efficiency" in df.columns and len(df) > 20:
            # Use rolling average to detect plateaus
            window_size = max(5, len(df) // 20)  # At least 5 points, or 5% of data
            rolling_efficiency = df["metric_efficiency"].rolling(window_size).mean()

            # Calculate derivatives to find flat regions (close to zero slope)
            derivatives = rolling_efficiency.diff().abs()
            plateaus = (derivatives < 0.01).astype(int)

            # Find contiguous plateau regions
            plateau_regions = []
            in_plateau = False
            plateau_start = 0

            for i in range(window_size, len(plateaus)):
                if plateaus.iloc[i] == 1 and not in_plateau:
                    # Start of plateau
                    in_plateau = True
                    plateau_start = i
                elif (plateaus.iloc[i] == 0 or i == len(plateaus) - 1) and in_plateau:
                    # End of plateau
                    in_plateau = False
                    plateau_length = i - plateau_start

                    if plateau_length >= window_size:  # Only count significant plateaus
                        plateau_regions.append({
                            "start_iteration": df["iteration"].iloc[plateau_start],
                            "end_iteration": df["iteration"].iloc[i],
                            "length": plateau_length,
                            "efficiency_level": rolling_efficiency.iloc[plateau_start:i].mean()
                        })

            results["learning_plateaus"] = plateau_regions
            results["plateau_count"] = len(plateau_regions)

        return results
    
    def generate_comprehensive_report(self, simulation_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate a comprehensive analysis report.
        
        Args:
            simulation_id: ID of the simulation to analyze (default: latest)
            
        Returns:
            Dictionary with comprehensive analysis
        """
        if not self.has_analysis_libs:
            return {"error": "Analysis libraries not available"}
            
        if simulation_id is None:
            simulation_id = self.visualizer.get_latest_simulation_id()

        if simulation_id is None:
            return {"error": "No simulation logs found"}

        try:
            # Load and convert simulation data to DataFrame
            df = self.load_simulation_data_as_df(simulation_id)
            
            # Run analyses
            survival_analysis = self.analyze_survival_factors(df)
            behavior_analysis = self.analyze_behavior_adaptation(df)
            environment_analysis = self.analyze_environmental_impact(df)
            learning_analysis = self.analyze_learning_effectiveness(df)
            
            # Run cluster analysis with different numbers of clusters
            cluster_analysis_3 = self.perform_cluster_analysis(df, n_clusters=3)
            cluster_analysis_5 = self.perform_cluster_analysis(df, n_clusters=5)
            
            # Combine all analyses into a report
            report = {
                "simulation_id": simulation_id,
                "generated_at": datetime.now().isoformat(),
                "data_points": len(df),
                "start_iteration": df["iteration"].iloc[0],
                "end_iteration": df["iteration"].iloc[-1],
                "survival_analysis": survival_analysis,
                "behavior_analysis": behavior_analysis,
                "environment_analysis": environment_analysis,
                "learning_analysis": learning_analysis,
                "cluster_analysis": {
                    "3_clusters": cluster_analysis_3,
                    "5_clusters": cluster_analysis_5
                }
            }

            # Generate final assessment
            assessment = {}
            
            # Survival assessment
            if "energy_regression" in survival_analysis:
                energy_trend = survival_analysis["energy_regression"]["trend"]
                survival_trajectory = (
                    "improving" if energy_trend == "increasing" else
                    "critical" if energy_trend == "decreasing" and survival_analysis["energy_trends"]["final"] < 0.3 else
                    "declining" if energy_trend == "decreasing" else
                    "stable"
                )
                assessment["survival_trajectory"] = survival_trajectory

            # Learning assessment
            if "learning_category" in learning_analysis:
                assessment["learning_assessment"] = learning_analysis["learning_category"]

            # Behavioral assessment
            if "adaptation_status" in behavior_analysis:
                assessment["adaptation_status"] = behavior_analysis["adaptation_status"]
                assessment["behavior_strategy"] = (
                    "specializing" if behavior_analysis["behavior_specialization"]["pattern"] == "specializing" 
                    else "generalizing"
                )

            # Overall cognitive capacity assessment
            cognitive_capacity = self._evaluate_cognitive_capacity(
                survival_analysis, learning_analysis, behavior_analysis, environment_analysis
            )

            capacity_category = (
                "exceptional" if cognitive_capacity > 0.8 else
                "high" if cognitive_capacity > 0.6 else
                "moderate" if cognitive_capacity > 0.4 else
                "limited" if cognitive_capacity > 0.2 else
                "primitive"
            )
            assessment["cognitive_capacity"] = capacity_category

            report["assessment"] = assessment
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return {"error": str(e)}
    
    def _evaluate_cognitive_capacity(self, survival_analysis: Dict, learning_analysis: Dict, 
                                    behavior_analysis: Dict, environment_analysis: Dict) -> float:
        """Evaluate overall cognitive capacity based on analysis results.
        
        Args:
            survival_analysis: Results from survival analysis
            learning_analysis: Results from learning analysis
            behavior_analysis: Results from behavior analysis
            environment_analysis: Results from environmental impact analysis
            
        Returns:
            Cognitive capacity score (0.0-1.0)
        """
        cognitive_capacity = 0.0
        factors = 0

        if "learning_rate" in learning_analysis:
            # Normalized learning rate (expect values between -0.5 and 0.5)
            cognitive_capacity += min(1.0, max(0.0, (learning_analysis["learning_rate"] + 0.5) / 1.0))
            factors += 1

        if "adaptation_status" in behavior_analysis:
            # Add adaptation factor
            if behavior_analysis["adaptation_status"] == "still_adapting":
                cognitive_capacity += 0.8  # Still adapting is good
            else:
                cognitive_capacity += 0.4  # Stabilized is okay
            factors += 1

            # Add behavior specialization factor
            if "environment_behavior_correlations" in environment_analysis:
                # Higher correlations suggest appropriate specialization
                avg_corr = np.mean([abs(v) for subdict in environment_analysis["environment_behavior_correlations"].values() 
                                   for v in subdict.values()])
                cognitive_capacity += min(1.0, avg_corr * 2)  # Scale up, as correlations are often < 0.5
                factors += 1

        if "energy_trends" in survival_analysis:
            # Add energy stability factor
            energy_stability = 1.0 - survival_analysis["energy_trends"]["std"]
            cognitive_capacity += energy_stability
            factors += 1

        return cognitive_capacity / factors if factors > 0 else 0
    
    def print_comprehensive_report(self, simulation_id: Optional[str] = None) -> None:
        """Print a comprehensive analysis report.
        
        Args:
            simulation_id: ID of the simulation to analyze (default: latest)
        """
        report = self.generate_comprehensive_report(simulation_id)
        if "error" in report:
            print(f"Error generating report: {report['error']}")
            return
        
        print(f"\n{'='*80}")
        print(f"COGNITIVE SIMULATION ANALYSIS REPORT - {report['simulation_id']}")
        print(f"Generated: {report['generated_at']}")
        print(f"{'='*80}")
        
        print(f"\n{'-'*30} OVERVIEW {'-'*30}")
        print(f"Data points: {report['data_points']}")
        print(f"Iterations: {report['start_iteration']} to {report['end_iteration']}")
        
        # Print assessment
        if "assessment" in report:
            print(f"\n{'-'*30} ASSESSMENT {'-'*30}")
            for key, value in report["assessment"].items():
                print(f"{key.replace('_', ' ').title()}: {value.replace('_', ' ').title()}")
        
        # Print survival analysis
        if "survival_analysis" in report:
            print(f"\n{'-'*30} SURVIVAL ANALYSIS {'-'*30}")
            sa = report["survival_analysis"]
            
            if "energy_trends" in sa:
                print("Energy Trends:")
                for key, value in sa["energy_trends"].items():
                    if isinstance(value, float):
                        print(f"  {key}: {value:.2f}")
                    else:
                        print(f"  {key}: {value}")
            
            if "energy_regression" in sa:
                print("\nEnergy Trend Analysis:")
                er = sa["energy_regression"]
                print(f"  Trend: {er['trend']} ({er['significance']})")
                print(f"  Slope: {er['slope']:.4f}")
                print(f"  R-squared: {er['r_squared']:.4f}")
            
            if "correlations" in sa and sa["correlations"]:
                print("\nTop Energy Correlations:")
                for factor, corr in sa["correlations"][:5]:
                    print(f"  {factor}: {corr:.4f}")
        
        # Print behavior analysis
        if "behavior_analysis" in report:
            print(f"\n{'-'*30} BEHAVIOR ANALYSIS {'-'*30}")
            ba = report["behavior_analysis"]
            
            if "most_adapted_behaviors" in ba:
                print("Most Adapted Behaviors:")
                for behavior, change in ba["most_adapted_behaviors"][:3]:
                    print(f"  {behavior}: {change:.2f}% change")
            
            if "behavior_specialization" in ba:
                bs = ba["behavior_specialization"]
                print(f"\nBehavior Pattern: {bs['pattern']}")
                print(f"  Initial variance: {bs['initial_variance']:.4f}")
                print(f"  Final variance: {bs['final_variance']:.4f}")
            
            if "adaptation_status" in ba:
                print(f"\nAdaptation Status: {ba['adaptation_status'].replace('_', ' ').title()}")
        
        # Print learning analysis
        if "learning_analysis" in report:
            print(f"\n{'-'*30} LEARNING ANALYSIS {'-'*30}")
            la = report["learning_analysis"]
            
            if "learning_category" in la:
                print(f"Learning Category: {la['learning_category'].title()}")
            
            if "learning_rate" in la:
                print(f"Learning Rate: {la['learning_rate']:.4f}")
            
            if "learning_plateaus" in la and la["learning_plateaus"]:
                print(f"\nLearning Plateaus: {la['plateau_count']}")
                for i, plateau in enumerate(la["learning_plateaus"][:3]):
                    print(f"  Plateau {i+1}: Iterations {plateau['start_iteration']} to {plateau['end_iteration']}")
                    print(f"    Length: {plateau_length} iterations")
                    print(f"    Efficiency: {plateau['efficiency_level']:.4f}")
        
        # Print operational modes (from cluster analysis)
        if "cluster_analysis" in report and "3_clusters" in report["cluster_analysis"]:
            print(f"\n{'-'*30} OPERATIONAL MODES {'-'*30}")
            
            modes = report["cluster_analysis"]["3_clusters"]["operational_modes"]
            for mode in modes:
                print(f"\nMode: {mode['name'].replace('_', ' ').title()}")
                print(f"  Size: {mode['size_percentage']:.1f}% of operations")
                
                for key, value in mode.items():
                    if key not in ["name", "size_percentage", "cluster"]:
                        print(f"  {key.replace('_', ' ').title()}: {str(value).replace('_', ' ').title()}")
        
        print(f"\n{'='*80}")
        print("END OF REPORT")
        print(f"{'='*80}\n")


# ==========================================
# Main Function and Utilities
# ==========================================

def try_import_emotional_framework() -> bool:
    """Try to import the emotional dimensionality framework."""
    sys.path.append(os.path.join(os.path.dirname(__file__), 'head_1', 'frameworks', 'emotional_dimensionality'))
    try:
        from emotional_dimensionality_client import EmotionalDimensionalityClient
        logger.info("Emotional dimensionality framework available")
        return True
    except ImportError:
        logger.warning("Emotional dimensionality framework not available")
        return False

def main():
    """Run a demonstration of the cognitive framework."""
    logger.info("Starting cognitive framework demonstration")
    
    # Create artificial lifeform and environment
    lifeform = ArtificialLifeform(name="CognitiveEntity-1")
    environment = Environment(complexity=0.6)
    
    # Create simulation manager
    simulation = SimulationManager(lifeform, environment)
    
    try:
        # Run the simulation for 1000 iterations
        logger.info("Running simulation for 1000 iterations")
        simulation.run_simulation(1000)
        
        # Create visualizer and generate plots
        visualizer = SimulationVisualizer()
        
        # Display summary report
        visualizer.print_summary_report(simulation.simulation_id)
        
        # Display plots if matplotlib is available
        if visualizer.has_matplotlib:
            visualizer.plot_energy_levels(simulation.simulation_id)
            visualizer.plot_environmental_conditions(simulation.simulation_id)
            visualizer.plot_performance_metrics(simulation.simulation_id)
            visualizer.plot_behavior_weights(simulation.simulation_id)
        
        # Perform advanced analysis if libraries are available
        analyzer = CognitiveAnalysis()
        if analyzer.has_analysis_libs:
            analyzer.print_comprehensive_report(simulation.simulation_id)
        
    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user")
        simulation.stop_simulation()
    except Exception as e:
        logger.error(f"Error during demonstration: {e}")
    finally:
        # Clean up resources
        if lifeform.enable_self_awareness and lifeform.awareness:
            lifeform.disconnect_from_awareness_framework()
        
        logger.info("Demonstration completed")

if __name__ == "__main__":
    main()

import logging
import random
import time
import threading
import os
import sys
import gc
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

# Add the frameworks directory to the path to import the self_awareness_client
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frameworks', 'self_awareness'))
from self_awareness_client import SelfAwarenessClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("cognitive-simulation")

class SensorType(Enum):
    """Types of sensors available to the artificial lifeform"""
    ENERGY = "energy"
    OBSTACLE = "obstacle"
    REWARD = "reward"
    ENVIRONMENT = "environment"
    INTERNAL = "internal"

class ActionType(Enum):
    """Types of actions available to the artificial lifeform"""
    MOVE = "move"
    CONSUME = "consume"
    AVOID = "avoid"
    REST = "rest"
    EXPLORE = "explore"
    
@dataclass
class SensorReading:
    """Represents a reading from a sensor"""
    sensor_type: SensorType
    value: float
    uncertainty: float = 0.0
    timestamp: float = field(default_factory=time.time)

@dataclass
class Action:
    """Represents an action the lifeform can take"""
    action_type: ActionType
    intensity: float  # 0.0 to 1.0
    target: Optional[str] = None
    energy_cost: float = 1.0  # Base energy cost for this action
    
    def get_actual_energy_cost(self) -> float:
        """Calculate the actual energy cost based on intensity"""
        return self.energy_cost * self.intensity

class SensorArray:
    """Collection of sensors for the artificial lifeform"""
    def __init__(self):
        self.sensors = {
            SensorType.ENERGY: 0.0,
            SensorType.OBSTACLE: 0.0,
            SensorType.REWARD: 0.0,
            SensorType.ENVIRONMENT: 0.0,
            SensorType.INTERNAL: 0.0,
        }
        self.readings: List[SensorReading] = []
        self.sensor_reliability = {
            SensorType.ENERGY: 0.95,      # 95% reliable
            SensorType.OBSTACLE: 0.85,    # 85% reliable
            SensorType.REWARD: 0.9,       # 90% reliable
            SensorType.ENVIRONMENT: 0.8,  # 80% reliable
            SensorType.INTERNAL: 0.98,    # 98% reliable
        }
    
    def get_reading(self, sensor_type: SensorType) -> SensorReading:
        """Get a reading from a specific sensor with appropriate uncertainty"""
        reliability = self.sensor_reliability[sensor_type]
        base_value = self.sensors[sensor_type]
        
        # Introduce noise based on reliability
        noise = np.random.normal(0, (1 - reliability) * 0.2)
        value = base_value + noise
        uncertainty = 1.0 - reliability
        
        reading = SensorReading(
            sensor_type=sensor_type,
            value=value,
            uncertainty=uncertainty
        )
        
        self.readings.append(reading)
        return reading
    
    def collect_data(self) -> Dict[SensorType, SensorReading]:
        """Collect data from all sensors"""
        return {
            sensor_type: self.get_reading(sensor_type)
            for sensor_type in self.sensors.keys()
        }
    
    def update_sensor(self, sensor_type: SensorType, value: float):
        """Update a sensor's base value"""
        self.sensors[sensor_type] = value


class BehaviorSystem:
    """Manages behaviors and decision-making for the artificial lifeform"""
    def __init__(self):
        self.available_actions = {
            ActionType.MOVE: 0.5,    # Default intensity
            ActionType.CONSUME: 0.5,
            ActionType.AVOID: 0.5,
            ActionType.REST: 0.5,
            ActionType.EXPLORE: 0.5,
        }
        self.behavior_weights = {
            ActionType.MOVE: 1.0,    # Default priority
            ActionType.CONSUME: 1.0,
            ActionType.AVOID: 1.5,   # Higher priority for avoiding obstacles
            ActionType.REST: 0.8,    # Lower priority for resting
            ActionType.EXPLORE: 0.7, # Lower priority for exploration
        }
        # Energy consumption rates for each action type
        self.energy_consumption_rates = {
            ActionType.MOVE: 2.0,
            ActionType.CONSUME: 1.0,
            ActionType.AVOID: 2.5,
            ActionType.REST: 0.2,
            ActionType.EXPLORE: 3.0,
        }
        # Latest action executed
        self.current_action = None
        # Track action outcomes for learning
        self.action_history = []
        
    def select_action(self, sensory_input: Dict[SensorType, SensorReading]) -> Action:
        """
        Select an appropriate action based on sensory input
        Uses a simple utility-based decision model
        """
        # Calculate utility values for each action
        utilities = {}
        
        # Energy level influences action selection
        energy_level = sensory_input[SensorType.ENERGY].value
        
        # When energy is low, prioritize consumption and rest
        low_energy_factor = max(0, 1.0 - energy_level)
        
        for action_type in ActionType:
            # Base utility is the behavior weight
            utility = self.behavior_weights[action_type]
            
            # Adjust utility based on sensory input
            if action_type == ActionType.AVOID:
                # Higher obstacle reading means higher utility for avoid action
                utility *= (1.0 + sensory_input[SensorType.OBSTACLE].value)
            
            elif action_type == ActionType.CONSUME:
                # Higher reward reading means higher utility for consume action
                utility *= (1.0 + sensory_input[SensorType.REWARD].value)
                # Low energy increases consume utility
                utility *= (1.0 + low_energy_factor * 2)
            
            elif action_type == ActionType.REST:
                # Low energy increases rest utility
                utility *= (1.0 + low_energy_factor * 3)
            
            elif action_type == ActionType.EXPLORE:
                # Low reward or low obstacle means more exploration
                exploration_factor = 1.0 - max(
                    sensory_input[SensorType.REWARD].value,
                    sensory_input[SensorType.OBSTACLE].value
                )
                utility *= (1.0 + exploration_factor)
                # But don't explore much when energy is low
                utility *= (1.0 - low_energy_factor * 0.8)
            
            utilities[action_type] = utility
        
        # Select the action with the highest utility
        selected_action_type = max(utilities, key=utilities.get)
        
        # Determine the intensity based on utility
        intensity = min(1.0, self.available_actions[selected_action_type] * 
                         (utilities[selected_action_type] / self.behavior_weights[selected_action_type]))
        
        # Create and return the action
        action = Action(
            action_type=selected_action_type,
            intensity=intensity,
            energy_cost=self.energy_consumption_rates[selected_action_type]
        )
        
        self.current_action = action
        return action
    
    def execute(self, action: Action) -> Dict[str, Any]:
        """Execute a behavior and return the results"""
        result = {
            "action_type": action.action_type.value,
            "intensity": action.intensity,
            "energy_consumed": action.get_actual_energy_cost(),
            "success": True,  # Default to success
            "timestamp": time.time()
        }
        
        # Record action for learning
        self.action_history.append((action, result))
        
        # Return result of execution
        return result
    
    def adapt_behaviors(self, performance_metrics: Dict[str, float]):
        """Adapt behavior weights based on performance"""
        if not self.action_history:
            return
        
        # Simple adaptation mechanism - increase weights for actions that improved performance
        survival_performance = performance_metrics.get("survival", 0)
        efficiency_performance = performance_metrics.get("efficiency", 0)
        
        # Analyze recent actions to see which were effective
        recent_actions = self.action_history[-min(10, len(self.action_history)):]
        
        # Count occurrences of each action type
        action_counts = {}
        for action, _ in recent_actions:
            if action.action_type not in action_counts:
                action_counts[action.action_type] = 0
            action_counts[action.action_type] += 1
        
        # If we're doing well, reinforce the most common actions
        if survival_performance > 0.7 and efficiency_performance > 0.6:
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
        
        # Normalize the weights to prevent extreme values
        total_weight = sum(self.behavior_weights.values())
        for action_type in self.behavior_weights:
            self.behavior_weights[action_type] /= (total_weight / len(self.behavior_weights))
    
    @property
    def energy_consumption(self) -> float:
        """Get the energy consumption for the current action"""
        if self.current_action:
            return self.current_action.get_actual_energy_cost()
        return 0.0


class ArtificialLifeform:
    """Represents an artificial lifeform with sensing, decision-making and adaptive capabilities"""
    def __init__(self, initial_energy: float = 100.0, name: str = "Cognitron"):
        self.name = name
        self.energy = initial_energy
        self.max_energy = initial_energy
        self.sensors = SensorArray()
        self.behaviors = BehaviorSystem()
        self.performance_metrics = {
            "survival": 1.0,          # How well the lifeform is surviving
            "efficiency": 1.0,        # How efficient its actions are
            "adaptability": 0.5,      # How well it adapts to changes
            "exploration": 0.5,       # How well it explores its environment
            "learning_rate": 0.5,     # How quickly it learns
        }
        self.uncertainty_factors = {
            "environmental": 0.5,      # Uncertainty about environment
            "sensory": 0.5,           # Uncertainty about sensory input
            "action_outcome": 0.5,    # Uncertainty about action results
            "energy_estimation": 0.2,  # Uncertainty about energy levels
        }
        self.age = 0
        self.lifetime_energy_consumed = 0
        self.actions_taken = 0
        self.last_action_result = None
        
        # Update the internal sensor to reflect initial energy
        self.sensors.update_sensor(SensorType.ENERGY, self.energy / self.max_energy)
        self.sensors.update_sensor(SensorType.INTERNAL, 1.0)  # Healthy internal state
        
        # Integration with Self-Awareness Framework
        self.awareness = SelfAwarenessClient()
        self.awareness.add_insight_handler(self.handle_insight)
        self.awareness.add_alert_handler(self.handle_alert)
        
    def perceive_environment(self) -> Dict[SensorType, SensorReading]:
        """Gather sensory information from the environment"""
        return self.sensors.collect_data()
    
    def execute_behavior(self, action: Action):
        """Perform a behavioral routine based on the selected action"""
        self.last_action_result = self.behaviors.execute(action)
        self.update_energy_consumption(action.get_actual_energy_cost())
        self.actions_taken += 1
    
    def update_energy_consumption(self, energy_consumed: float):
        """Simulate energy usage based on performed actions"""
        self.energy = max(0, self.energy - energy_consumed)
        self.lifetime_energy_consumed += energy_consumed
        
        # Update energy sensor
        self.sensors.update_sensor(SensorType.ENERGY, self.energy / self.max_energy)
        
        # Report to self-awareness framework
        if self.awareness and hasattr(self.awareness, 'connected') and self.awareness.connected:
            self.awareness.update_decision_metrics(
                confidence=1.0 - self.uncertainty_factors["action_outcome"],
                complexity=energy_consumed / 3.0,  # Normalize to 0-1 scale approximately
                execution_time=0.1  # Simulated execution time
            )
    
    def evaluate_performance(self):
        """Calculate performance metrics based on current state"""
        # Survival metric based on energy level
        self.performance_metrics["survival"] = self.energy / self.max_energy
        
        # Efficiency metric based on energy consumed per action
        if self.actions_taken > 0:
            avg_energy_per_action = self.lifetime_energy_consumed / self.actions_taken
            # Lower average energy consumption is better (higher efficiency)
            self.efficiency_score = max(0, 1.0 - (avg_energy_per_action / 3.0))
            self.performance_metrics["efficiency"] = self.efficiency_score
        
        # Adaptability metric (will be updated based on environment changes)
        # Learning rate metric (will be updated based on performance improvements)
        
        # Report metrics to self-awareness framework
        if self.awareness and hasattr(self.awareness, 'connected') and self.awareness.connected:
            metrics = {
                "energy_level": self.energy / self.max_energy,
                "survival_score": self.performance_metrics["survival"],
                "efficiency_score": self.performance_metrics["efficiency"],
                "actions_taken": self.actions_taken,
                "adaptability": self.performance_metrics["adaptability"],
            }
            self.awareness._send_message({
                "type": "metrics",
                "data": metrics
            })
    
    def detect_uncertainty(self):
        """Identify uncertainty factors that may impact performance"""
        # Sensory uncertainty based on recent sensor readings
        recent_readings = self.sensors.readings[-10:] if len(self.sensors.readings) > 10 else self.sensors.readings
        if recent_readings:
            avg_uncertainty = sum(reading.uncertainty for reading in recent_readings) / len(recent_readings)
            self.uncertainty_factors["sensory"] = avg_uncertainty
        
        # Energy estimation uncertainty - increases as energy gets lower
        energy_ratio = self.energy / self.max_energy
        self.uncertainty_factors["energy_estimation"] = 0.2 + (0.3 * (1.0 - energy_ratio))
        
        # Report uncertainty to self-awareness framework
        if self.awareness and hasattr(self.awareness, 'connected') and self.awareness.connected:
            uncertainty_metrics = {
                "total_uncertainty": sum(self.uncertainty_factors.values()) / len(self.uncertainty_factors),
                "sensory_uncertainty": self.uncertainty_factors["sensory"],
                "energy_uncertainty": self.uncertainty_factors["energy_estimation"],
            }
            self.awareness._send_message({
                "type": "metrics",
                "data": uncertainty_metrics
            })
    
    def handle_insight(self, insight_data):
        """Process insights received from the self-awareness framework"""
        logger.info(f"Lifeform {self.name} received insight: {insight_data}")
        
        # Adjust behavior based on resource efficiency insight
        if "resource_efficiency" in insight_data:
            efficiency = insight_data["resource_efficiency"]["score"]
            if efficiency < 50:
                logger.info(f"Lifeform {self.name} detected low resource efficiency. Adjusting behaviors.")
                # Update the REST action weight to conserve energy
                self.behaviors.behavior_weights[ActionType.REST] *= 1.2
                self.behaviors.behavior_weights[ActionType.EXPLORE] *= 0.8
            else:
                # Encourage more exploration with higher efficiency
                self.behaviors.behavior_weights[ActionType.EXPLORE] *= 1.1
    
    def handle_alert(self, alert_data):
        """Handle alerts from the self-awareness framework"""
        logger.warning(f"Lifeform {self.name} received alert: {alert_data['message']}")
        
        # React to high memory usage alert
        if alert_data.get("category") == "resource" and "memory" in alert_data.get("message", ""):
            logger.warning(f"Lifeform {self.name} performing memory optimization.")
            self.memory_optimization()
    
    def memory_optimization(self):
        """Optimize memory usage"""
        # Clear unnecessary sensor history
        if len(self.sensors.readings) > 100:
            self.sensors.readings = self.sensors.readings[-50:]
        
        # Clear behavior history if it's getting too large
        if len(self.behaviors.action_history) > 100:
            self.behaviors.action_history = self.behaviors.action_history[-50:]
        
        # Run garbage collection
        gc.collect()
    
    def adapt_to_insights(self):
        """Adapt behavior based on performance metrics and uncertainty"""
        # Update behaviors based on performance
        self.behaviors.adapt_behaviors(self.performance_metrics)
        
        # Increase exploration when uncertainty is high
        total_uncertainty = sum(self.uncertainty_factors.values()) / len(self.uncertainty_factors)
        if total_uncertainty > 0.6:
            self.behaviors.behavior_weights[ActionType.EXPLORE] *= 1.1
        
        # Track adaptability - how much the behavior weights have changed
        self.performance_metrics["adaptability"] = 0.5  # Placeholder
    
    def gain_energy(self, amount: float):
        """Gain energy from the environment"""
        self.energy = min(self.max_energy, self.energy + amount)
        # Update energy sensor
        self.sensors.update_sensor(SensorType.ENERGY, self.energy / self.max_energy)
    
    def connect_to_awareness_framework(self):
        """Connect to the self-awareness framework"""
        if not hasattr(self.awareness, 'connected') or not self.awareness.connected:
            self.awareness.connect()
    
    def disconnect_from_awareness_framework(self):
        """Disconnect from the self-awareness framework"""
        if hasattr(self.awareness, 'connected') and self.awareness.connected:
            self.awareness.disconnect()


class Environment:
    """Simulates the environment in which the artificial lifeform exists"""
    def __init__(self, lifeform: ArtificialLifeform, complexity: float = 0.5):
        self.lifeform = lifeform
        self.complexity = complexity  # 0.0 to 1.0, higher means more dynamic environment
        self.obstacle_density = 0.3   # 0.0 to 1.0
        self.reward_density = 0.2     # 0.0 to 1.0
        self.environmental_stability = 0.7  # 0.0 to 1.0, higher means more stable
        
        # Current state
        self.current_obstacles = 0.0
        self.current_rewards = 0.0
        self.current_environmental_condition = 0.5  # Neutral environmental condition
        
        # History for analysis
        self.history = []
    
    def update(self):
        """Simulate environmental changes and interactions"""
        # Record current state
        self.record_state()
        
        # Update environmental conditions with some randomness
        self._update_environmental_conditions()
        
        # Generate obstacles and rewards
        self._generate_obstacles()
        self._generate_rewards()
        
        # Update the lifeform's sensors
        self.lifeform.sensors.update_sensor(SensorType.OBSTACLE, self.current_obstacles)
        self.lifeform.sensors.update_sensor(SensorType.REWARD, self.current_rewards)
        self.lifeform.sensors.update_sensor(SensorType.ENVIRONMENT, self.current_environmental_condition)
    
    def _update_environmental_conditions(self):
        """Update the environmental conditions with some randomness"""
        # More complex environments change more rapidly and unpredictably
        change_factor = (1.0 - self.environmental_stability) * self.complexity
        
        # Generate a random change, weighted by stability and complexity
        random_change = np.random.normal(0, change_factor * 0.2)
        
        # Update environmental condition, keeping it between 0 and 1
        self.current_environmental_condition = max(0, min(1, 
            self.current_environmental_condition + random_change
        ))
    
    def _generate_obstacles(self):
        """Generate obstacles for the lifeform to avoid"""
        # Base probability of obstacles appearing
        base_probability = self.obstacle_density
        
        # Adjust based on environmental conditions
        # Harsher conditions (higher values) mean more obstacles
        adjusted_probability = base_probability * (1.0 + self.current_environmental_condition * 0.5)
        
        # Generate a random value for obstacle intensity
        if random.random() < adjusted_probability:
            # More complex environments have more intense obstacles
            intensity = random.uniform(0.3, 0.3 + self.complexity * 0.7)
            self.current_obstacles = intensity
        else:
            # Obstacles gradually decrease if not refreshed
            self.current_obstacles = max(0, self.current_obstacles * 0.9)
    
    def _generate_rewards(self):
        """Generate rewards (energy sources) for the lifeform"""
        # Base probability of rewards appearing
        base_probability = self.reward_density
        
        # Adjust based on environmental conditions
        # Harsher conditions (higher values) mean fewer rewards
        adjusted_probability = base_probability * (1.0 - self.current_environmental_condition * 0.3)
        
        # Generate random value for reward intensity
        if random.random() < adjusted_probability:
            intensity = random.uniform(0.1, 0.5)
            self.current_rewards = intensity
            
            # If the lifeform's current action is CONSUME, it gains energy
            if (self.lifeform.last_action_result and 
                self.lifeform.last_action_result.get("action_type") == ActionType.CONSUME.value):
                energy_gain = 10 * intensity * self.lifeform.last_action_result.get("intensity", 0.5)
                self.lifeform.gain_energy(energy_gain)
                logger.info(f"Lifeform {self.lifeform.name} gained {energy_gain:.2f} energy from consuming a reward.")
        else:
            # Rewards gradually decrease if not refreshed
            self.current_rewards = max(0, self.current_rewards * 0.8)
    
    def record_state(self):
        """Record the current state for later analysis"""
        state = {
            "timestamp": time.time(),
            "obstacles": self.current_obstacles,
            "rewards": self.current_rewards,
            "environment": self.current_environmental_condition,
            "lifeform_energy": self.lifeform.energy / self.lifeform.max_energy,
        }
        self.history.append(state)
        
        # Keep history manageable
        if len(self.history) > 1000:
            self.history = self.history[-500:]
    
    def get_analysis(self) -> Dict[str, Any]:
        """Analyze the environment history"""
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


class SimulationManager:
    """Manages the simulation of artificial lifeform and environment"""
    def __init__(self, lifeform: ArtificialLifeform, environment: Environment, 
                 log_directory: str = "simulation_logs"):
        self.lifeform = lifeform
        self.environment = environment
        self.running = False
        self.iteration = 0
        self.max_iterations = 10000
        self.log_directory = log_directory
        self.simulation_id = f"sim_{int(time.time())}"
        
        # Ensure log directory exists
        os.makedirs(log_directory, exist_ok=True)
        
        # Simulation statistics
        self.statistics = {
            "start_time": time.time(),
            "iterations": 0,
            "lifeform_survival_time": 0,
            "avg_energy_level": [],
            "avg_performance": {},
            "environment_metrics": {},
        }
        
    def run_simulation(self, num_iterations: int = None):
        """Run the simulation for a specified number of iterations or until stopped"""
        if num_iterations:
            self.max_iterations = num_iterations
        
        self.running = True
        self.lifeform.connect_to_awareness_framework()
        
        try:
            while self.running and self.iteration < self.max_iterations:
                # Check if lifeform has died (energy depleted)
                if self.lifeform.energy <= 0:
                    logger.info(f"Lifeform {self.lifeform.name} has expired after {self.iteration} iterations.")
                    self.statistics["lifeform_survival_time"] = self.iteration
                    break
                
                # Update the environment
                self.environment.update()
                
                # Lifeform perceives environment
                sensory_input = self.lifeform.perceive_environment()
                
                # Lifeform selects an action
                action = self.lifeform.behaviors.select_action(sensory_input)
                
                # Lifeform executes the action
                self.lifeform.execute_behavior(action)
                
                # Lifeform evaluates its performance
                self.lifeform.evaluate_performance()
                
                # Lifeform assesses uncertainty
                self.lifeform.detect_uncertainty()
                
                # Lifeform adapts based on insights
                if self.iteration % 10 == 0:  # Adapt every 10 iterations
                    self.lifeform.adapt_to_insights()
                
                # Update simulation statistics
                self._update_statistics()
                
                # Periodically log the simulation state
                if self.iteration % 100 == 0:
                    self._log_simulation_state()
                
                self.iteration += 1
                
                # Small delay to prevent overwhelming the system
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            logger.info("Simulation interrupted by user.")
        except Exception as e:
            logger.error(f"Error in simulation: {str(e)}")
        finally:
            self.running = False
            self.lifeform.disconnect_from_awareness_framework()
            self._log_simulation_state(final=True)
            self._display_results()
    
    def _update_statistics(self):
        """Update simulation statistics"""
        self.statistics["iterations"] = self.iteration
        self.statistics["avg_energy_level"].append(self.lifeform.energy / self.lifeform.max_energy)
        
        # Store a snapshot of performance metrics periodically
        if self.iteration % 10 == 0:
            for key, value in self.lifeform.performance_metrics.items():
                if key not in self.statistics["avg_performance"]:
                    self.statistics["avg_performance"][key] = []
                self.statistics["avg_performance"][key].append(value)
        
        # Store environment analysis periodically
        if self.iteration % 50 == 0:
            analysis = self.environment.get_analysis()
            for key, value in analysis.items():
                if key not in self.statistics["environment_metrics"]:
                    self.statistics["environment_metrics"][key] = []
                self.statistics["environment_metrics"][key].append(value)
    
    def _log_simulation_state(self, final: bool = False):
        """Log the current state of the simulation"""
        state = {
            "iteration": self.iteration,
            "timestamp": time.time(),
            "lifeform": {
                "name": self.lifeform.name,
                "energy": self.lifeform.energy,
                "max_energy": self.lifeform.max_energy,
                "energy_percentage": self.lifeform.energy / self.lifeform.max_energy,
                "actions_taken": self.lifeform.actions_taken,
                "lifetime_energy_consumed": self.lifeform.lifetime_energy_consumed,
                "performance_metrics": self.lifeform.performance_metrics,
                "uncertainty_factors": self.lifeform.uncertainty_factors,
                "behavior_weights": {k.value: v for k, v in self.lifeform.behaviors.behavior_weights.items()}
            },
            "environment": {
                "obstacles": self.environment.current_obstacles,
                "rewards": self.environment.current_rewards,
                "environmental_condition": self.environment.current_environmental_condition,
            },
            "statistics": {
                "iterations": self.statistics["iterations"],
                "avg_energy": sum(self.statistics["avg_energy_level"]) / len(self.statistics["avg_energy_level"]) 
                    if self.statistics["avg_energy_level"] else 0
            }
        }
        
        # Add final statistics if this is the final log
        if final:
            state["final_statistics"] = {
                "total_iterations": self.iteration,
                "survival_time": self.iteration,
                "final_energy": self.lifeform.energy / self.lifeform.max_energy,
                "final_performance": self.lifeform.performance_metrics,
                "total_actions": self.lifeform.actions_taken,
                "total_energy_consumed": self.lifeform.lifetime_energy_consumed,
            }
        
        # Write log to file
        log_name = f"{self.simulation_id}_{'final' if final else self.iteration}.json"
        log_path = os.path.join(self.log_directory, log_name)
        
        with open(log_path, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Simulation state logged to {log_path}")
    
    def _display_results(self):
        """Display the simulation results"""
        runtime = time.time() - self.statistics["start_time"]
        
        logger.info("=" * 50)
        logger.info(f"Simulation Complete - ID: {self.simulation_id}")
        logger.info(f"Total Iterations: {self.iteration}")
        logger.info(f"Runtime: {runtime:.2f} seconds")
        logger.info(f"Lifeform: {self.lifeform.name}")
        logger.info(f"Final Energy: {self.lifeform.energy:.2f}/{self.lifeform.max_energy} ({self.lifeform.energy / self.lifeform.max_energy * 100:.1f}%)")
        logger.info(f"Actions Taken: {self.lifeform.actions_taken}")
        logger.info(f"Average Energy Level: {sum(self.statistics['avg_energy_level']) / len(self.statistics['avg_energy_level']) * 100:.1f}%")
        logger.info("Final Performance Metrics:")
        for key, value in self.lifeform.performance_metrics.items():
            logger.info(f"  {key}: {value:.2f}")
        logger.info("=" * 50)
    
    def stop_simulation(self):
        """Stop the running simulation"""
        self.running = False


def main():
    """Main function to run the cognitive simulation"""
    # Create the artificial lifeform
    lifeform = ArtificialLifeform(initial_energy=100.0, name="CognitiveEntity-1")
    
    # Create the environment
    environment = Environment(lifeform, complexity=0.6)
    
    # Create the simulation manager
    simulation_manager = SimulationManager(lifeform, environment)
    
    try:
        # Connect to self-awareness framework
        lifeform.connect_to_awareness_framework()
        
        # Run the simulation
        logger.info("Starting cognitive simulation...")
        simulation_manager.run_simulation(num_iterations=5000)
        
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down simulation")
    
    finally:
        # Ensure clean shutdown
        simulation_manager.stop_simulation()
        lifeform.disconnect_from_awareness_framework()
        logger.info("Cognitive simulation completed")

if __name__ == "__main__":
    main()

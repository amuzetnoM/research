"""
Adaptive decision-making example with context-sensitive confidence thresholds.

This example demonstrates how the PUP framework can adapt confidence 
thresholds based on context, enabling more nuanced decision-making
in real-world scenarios with varying levels of risk.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any, Optional
import time

# Import PUP core components
from ___files.core import BeliefState, UncertaintyPropagator, ConfidenceExecutor


class AdaptiveAutonomousAgent:
    """
    Simulated autonomous agent that makes decisions with adaptive confidence thresholds.
    
    This agent demonstrates how confidence thresholds can be adjusted based on context
    factors like risk level, criticality, and past performance.
    """
    
    def __init__(self, base_threshold: float = 0.7):
        """
        Initialize the adaptive agent.
        
        Args:
            base_threshold: Base confidence threshold for decision-making
        """
        self.propagator = UncertaintyPropagator(samples=500)
        self.executor = ConfidenceExecutor(
            threshold=base_threshold,
            adaptive=True,
            min_threshold=0.3,
            max_threshold=0.95
        )
        
        # Sensors with different reliability levels
        self.sensors = {
            'high_quality': {'error_mean': 0.0, 'error_std': 0.05},
            'medium_quality': {'error_mean': 0.0, 'error_std': 0.15},
            'low_quality': {'error_mean': 0.0, 'error_std': 0.3}
        }
        
        # Track agent's performance
        self.decisions = {
            'executed': 0,
            'deferred': 0,
            'successful': 0,
            'failed': 0
        }
        
        # History for visualization
        self.history = []
    
    def read_sensor(self, sensor_type: str, ground_truth: float) -> BeliefState:
        """
        Simulate sensor reading with noise.
        
        Args:
            sensor_type: Type of sensor to read ('high_quality', 'medium_quality', 'low_quality')
            ground_truth: True value being measured
            
        Returns:
            BeliefState representing the sensor reading with uncertainty
        """
        if sensor_type not in self.sensors:
            raise ValueError(f"Unknown sensor type: {sensor_type}")
        
        sensor = self.sensors[sensor_type]
        
        # Add noise to the true value
        error = np.random.normal(sensor['error_mean'], sensor['error_std'])
        reading = ground_truth + error
        
        # Create belief state with uncertainty proportional to sensor quality
        return BeliefState(
            mean=reading,
            variance=sensor['error_std']**2,
            epistemic=False,  # This is aleatoric uncertainty (sensor noise)
            metadata={'sensor_type': sensor_type}
        )
    
    def process_sensor_data(
        self, 
        sensor_readings: Dict[str, BeliefState], 
        fusion_weights: Optional[Dict[str, float]] = None
    ) -> BeliefState:
        """
        Fuse multiple sensor readings into a single belief state.
        
        Args:
            sensor_readings: Dictionary of sensor readings by sensor type
            fusion_weights: Optional weights for each sensor type
            
        Returns:
            Fused belief state
        """
        # Default to equal weights if not provided
        if fusion_weights is None:
            fusion_weights = {
                sensor_type: 1.0 / len(sensor_readings) 
                for sensor_type in sensor_readings
            }
        
        # Extract the means and variances
        means = np.array([reading.mean[0] for reading in sensor_readings.values()])
        variances = np.array([reading.variance[0] for reading in sensor_readings.values()])
        weights = np.array([fusion_weights.get(sensor_type, 1.0 / len(sensor_readings)) 
                           for sensor_type in sensor_readings])
        
        # Normalize weights
        weights = weights / np.sum(weights)
        
        # Compute weighted mean
        fused_mean = np.sum(weights * means)
        
        # Compute fused variance (accounting for both sensor variance and disagreement)
        # This implements the law of total variance
        fused_variance = np.sum(weights * variances)  # Within-sensor uncertainty
        fused_variance += np.sum(weights * (means - fused_mean)**2)  # Between-sensor disagreement
        
        return BeliefState(
            mean=fused_mean,
            variance=fused_variance,
            epistemic=True,  # Fusion introduces epistemic uncertainty
            metadata={'fusion_weights': fusion_weights}
        )
    
    def make_decision(
        self, 
        belief_state: BeliefState, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make a decision based on belief state and context.
        
        Args:
            belief_state: The current belief state about the environment
            context: Contextual information influencing the decision threshold
            
        Returns:
            Decision outcome information
        """
        start_time = time.time()
        
        # Define the action to take if confidence is sufficient
        def take_action(value):
            # Simulate action execution
            action_value = value[0] if isinstance(value, np.ndarray) else value
            
            # Simulate success/failure based on how far the belief is from ground truth
            ground_truth = context.get('ground_truth', 0.0)
            error = abs(action_value - ground_truth)
            
            # Action succeeds if error is small enough
            action_succeeded = error < 0.2
            
            # Update decision statistics
            self.decisions['executed'] += 1
            if action_succeeded:
                self.decisions['successful'] += 1
            else:
                self.decisions['failed'] += 1
            
            return {
                'action': 'executed',
                'value': float(action_value),
                'succeeded': action_succeeded,
                'error': float(error)
            }
        
        # Execute the action if confidence meets the adaptive threshold
        result = self.executor.execute(belief_state, take_action, context)
        
        # If the action was deferred, update statistics
        if isinstance(result, dict) and result.get('action') == 'deferred':
            self.decisions['deferred'] += 1
        
        # Record history for visualization
        self.history.append({
            'timestamp': time.time(),
            'belief_state': belief_state.to_dict(),
            'context': context,
            'result': result,
            'elapsed_time': time.time() - start_time
        })
        
        return result
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get agent performance metrics.
        
        Returns:
            Dictionary of performance metrics
        """
        total_decisions = self.decisions['executed'] + self.decisions['deferred']
        if total_decisions == 0:
            return {
                'success_rate': 0.0,
                'failure_rate': 0.0,
                'deferral_rate': 0.0,
                'total_decisions': 0
            }
        
        # Calculate rates
        deferral_rate = self.decisions['deferred'] / total_decisions
        
        if self.decisions['executed'] == 0:
            success_rate = 0.0
            failure_rate = 0.0
        else:
            success_rate = self.decisions['successful'] / self.decisions['executed']
            failure_rate = self.decisions['failed'] / self.decisions['executed']
        
        return {
            'success_rate': success_rate,
            'failure_rate': failure_rate,
            'deferral_rate': deferral_rate,
            'total_decisions': total_decisions,
            'executed': self.decisions['executed'],
            'deferred': self.decisions['deferred'],
            'successful': self.decisions['successful'],
            'failed': self.decisions['failed']
        }
    
    def visualize_performance(self):
        """Visualize agent performance and decision-making process."""
        if not self.history:
            print("No decision history to visualize")
            return
        
        # Extract data for plotting
        contexts = [entry['context'] for entry in self.history]
        beliefs = [entry['belief_state'] for entry in self.history]
        results = [entry['result'] for entry in self.history]
        
        # Extract relevant metrics
        risk_levels = [ctx.get('risk_level', 0.5) for ctx in contexts]
        ground_truths = [ctx.get('ground_truth', 0.0) for ctx in contexts]
        means = [belief['mean'][0] for belief in beliefs]
        variances = [belief['variance'][0] for belief in beliefs]
        confidences = [belief['confidence'] for belief in beliefs]
        
        # Determine which decisions were executed vs deferred
        executed = [isinstance(r, dict) and r.get('action') == 'executed' for r in results]
        successful = [isinstance(r, dict) and r.get('succeeded', False) for r in results]
        
        # Create figure with subplots
        fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
        
        # Plot 1: Beliefs vs Ground Truth
        ax1 = axes[0]
        decision_indices = np.arange(len(means))
        
        # Plot ground truth
        ax1.plot(decision_indices, ground_truths, 'k--', label='Ground Truth')
        
        # Plot executed and deferred decisions differently
        executed_indices = [i for i, e in enumerate(executed) if e]
        deferred_indices = [i for i, e in enumerate(executed) if not e]
        
        # Plot executed decisions
        if executed_indices:
            ax1.errorbar(
                np.array(executed_indices), 
                [means[i] for i in executed_indices],
                yerr=[np.sqrt(variances[i]) for i in executed_indices],
                fmt='go',
                capsize=5,
                label='Executed'
            )
        
        # Plot deferred decisions
        if deferred_indices:
            ax1.errorbar(
                np.array(deferred_indices), 
                [means[i] for i in deferred_indices],
                yerr=[np.sqrt(variances[i]) for i in deferred_indices],
                fmt='ro',
                capsize=5,
                label='Deferred'
            )
            
        ax1.set_title('Belief States vs Ground Truth')
        ax1.set_ylabel('Value')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Confidence and Risk Levels
        ax2 = axes[1]
        ax2.plot(decision_indices, confidences, 'b-', label='Confidence')
        ax2.plot(decision_indices, risk_levels, 'r-', label='Risk Level')
        
        # Calculate the effective threshold for each decision
        thresholds = []
        for i, ctx in enumerate(contexts):
            risk = ctx.get('risk_level', 0.5)
            criticality = ctx.get('criticality', 0.5)
            
            # Simple approximation of the threshold calculation
            threshold = 0.7 + 0.2 * risk + 0.1 * criticality
            threshold = min(0.95, max(0.3, threshold))
            thresholds.append(threshold)
        
        ax2.plot(decision_indices, thresholds, 'g--', label='Adaptive Threshold')
        
        ax2.set_title('Confidence vs Risk Level and Threshold')
        ax2.set_ylabel('Value (0-1)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Performance over time
        ax3 = axes[2]
        
        # Calculate cumulative metrics
        cum_success = np.cumsum([1 if s else 0 for s in successful])
        cum_failure = np.cumsum([1 if e and not s else 0 for e, s in zip(executed, successful)])
        cum_deferral = np.cumsum([1 if not e else 0 for e in executed])
        cum_total = np.arange(1, len(means) + 1)
        
        # Calculate running success rate
        success_rate = cum_success / np.maximum(1, cum_success + cum_failure)
        
        ax3.plot(decision_indices, success_rate, 'g-', label='Success Rate')
        ax3.plot(decision_indices, cum_deferral / cum_total, 'r-', label='Deferral Rate')
        
        ax3.set_title('Performance Metrics Over Time')
        ax3.set_xlabel('Decision Number')
        ax3.set_ylabel('Rate (0-1)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig("adaptive_decision_making.png")
        print("Visualization saved as 'adaptive_decision_making.png'")
        plt.show()


def simulate_autonomous_navigation():
    """
    Simulate an autonomous navigation scenario with varying risk and sensor quality.
    
    This simulation demonstrates how the PUP framework adapts confidence thresholds
    based on contextual factors like risk level and criticality.
    """
    print("PUP Framework - Adaptive Decision-Making Example")
    print("================================================")
    
    # Create agent
    agent = AdaptiveAutonomousAgent(base_threshold=0.7)
    
    # Run simulation with varying conditions
    num_scenarios = 100
    
    print(f"\nSimulating {num_scenarios} navigation decisions...")
    
    for i in range(num_scenarios):
        # Simulate different ground truth values (e.g., distance to obstacle)
        ground_truth = np.sin(i * 0.1) * 0.5 + 0.5  # Oscillates between 0 and 1
        
        # Risk level increases in certain regions
        risk_level = 0.8 if 0.4 <= ground_truth <= 0.6 else 0.3
        
        # Criticality level (importance of the decision)
        criticality = 0.7 if ground_truth < 0.3 else 0.4
        
        # Context for this decision
        context = {
            'scenario_id': i,
            'ground_truth': ground_truth,
            'risk_level': risk_level,
            'criticality': criticality,
            'location': f"Region {i // 10}"
        }
        
        # Get sensor readings with different quality levels
        sensor_readings = {
            'high_quality': agent.read_sensor('high_quality', ground_truth),
            'medium_quality': agent.read_sensor('medium_quality', ground_truth),
            'low_quality': agent.read_sensor('low_quality', ground_truth)
        }
        
        # Process sensor data (fusion with different weights based on context)
        if risk_level > 0.5:
            # In high-risk scenarios, rely more on high-quality sensors
            fusion_weights = {'high_quality': 0.7, 'medium_quality': 0.2, 'low_quality': 0.1}
        else:
            # In low-risk scenarios, more balanced fusion
            fusion_weights = {'high_quality': 0.5, 'medium_quality': 0.3, 'low_quality': 0.2}
        
        belief_state = agent.process_sensor_data(sensor_readings, fusion_weights)
        
        # Make decision
        result = agent.make_decision(belief_state, context)
        
        # Print progress
        if (i + 1) % 10 == 0:
            print(f"Completed {i + 1}/{num_scenarios} decisions")
    
    # Display performance metrics
    metrics = agent.get_performance_metrics()
    print("\nPerformance Metrics:")
    print(f"  Success Rate:  {metrics['success_rate']:.2f}")
    print(f"  Failure Rate:  {metrics['failure_rate']:.2f}")
    print(f"  Deferral Rate: {metrics['deferral_rate']:.2f}")
    print(f"  Total Decisions: {metrics['total_decisions']}")
    print(f"    - Executed:   {metrics['executed']}")
    print(f"    - Deferred:   {metrics['deferred']}")
    print(f"    - Successful: {metrics['successful']}")
    print(f"    - Failed:     {metrics['failed']}")
    
    # Visualize results
    print("\nGenerating visualization...")
    agent.visualize_performance()


if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Run the simulation
    simulate_autonomous_navigation()
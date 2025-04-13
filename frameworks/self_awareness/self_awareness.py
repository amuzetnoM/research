"""
Self-Awareness Mechanics Framework for AI Systems.

This module implements the computational self-awareness framework described in
the research paper "Self-Awareness Mechanics in Artificial Intelligence Systems".
"""

import logging
import time
import numpy as np
import threading
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Set
import json
import os

logger = logging.getLogger('ai.self_awareness')

class AwarenessDimension(Enum):
    """The five key dimensions of self-awareness in AI systems."""
    INTROSPECTIVE = "introspective"  # Internal states, processes, resources
    CAPABILITY = "capability"        # Understanding of abilities and limitations
    EPISTEMIC = "epistemic"          # Knowledge and knowledge boundaries
    TEMPORAL = "temporal"            # Past states and potential futures
    SOCIAL = "social"                # Relationship to other systems and humans


class SelfAwarenessMetrics:
    """Metrics for tracking self-awareness performance."""
    
    def __init__(self):
        """Initialize the metrics tracking system."""
        self.metrics = {dim.value: 0.0 for dim in AwarenessDimension}
        self.confidence_accuracy = 0.0  # correlation between confidence and performance
        self.adaptation_efficiency = 0.0  # resource efficiency during adaptation
        self.recovery_time = 0.0  # time to recover from perturbations
        self.boundary_detection_rate = 0.0  # rate of correct knowledge boundary detection
        self.history = []
    
    def update(self, dimension: AwarenessDimension, value: float):
        """Update a specific dimension metric."""
        self.metrics[dimension.value] = value
        self.history.append({
            'timestamp': time.time(),
            'dimension': dimension.value,
            'value': value
        })
    
    def get_aggregate_score(self) -> float:
        """Calculate an aggregate self-awareness score."""
        return sum(self.metrics.values()) / len(self.metrics)
    
    def to_dict(self) -> Dict:
        """Convert metrics to a dictionary for serialization."""
        return {
            'dimensions': self.metrics,
            'aggregate_score': self.get_aggregate_score(),
            'confidence_accuracy': self.confidence_accuracy,
            'adaptation_efficiency': self.adaptation_efficiency,
            'recovery_time': self.recovery_time,
            'boundary_detection_rate': self.boundary_detection_rate
        }
    
    def load_from_dict(self, data: Dict):
        """Load metrics from a dictionary."""
        if 'dimensions' in data:
            for dim, value in data['dimensions'].items():
                if dim in self.metrics:
                    self.metrics[dim] = value
        
        for attr in ['confidence_accuracy', 'adaptation_efficiency', 
                    'recovery_time', 'boundary_detection_rate']:
            if attr in data:
                setattr(self, attr, data[attr])


class StateMonitoringModule:
    """Collects real-time telemetry on system operations."""
    
    def __init__(self, sampling_rate: float = 1.0):
        """Initialize the monitoring module.
        
        Args:
            sampling_rate: How often to sample metrics (in Hz)
        """
        self.sampling_rate = sampling_rate
        self.monitoring_active = False
        self.monitor_thread = None
        self.state_data = {}
        self.callbacks = []
    
    def register_callback(self, callback):
        """Register a callback to receive state updates."""
        self.callbacks.append(callback)
    
    def start_monitoring(self):
        """Start the monitoring thread."""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect system state data
                self._collect_state_data()
                
                # Notify callbacks
                for callback in self.callbacks:
                    try:
                        callback(self.state_data)
                    except Exception as e:
                        logger.error(f"Error in monitoring callback: {e}")
                
                # Sleep until next sample
                time.sleep(1.0 / self.sampling_rate)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1.0)  # Avoid tight loop on error
    
    def _collect_state_data(self):
        """Collect current system state data."""
        # Basic resource monitoring
        try:
            import psutil
            mem = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=None)
            
            self.state_data.update({
                'memory_percent': mem.percent,
                'memory_available': mem.available,
                'cpu_percent': cpu,
                'timestamp': time.time()
            })
            
            # Add GPU data if available
            try:
                from utils.gpu_utils import gpu_manager
                if gpu_manager.check_gpu_availability():
                    gpus = gpu_manager.get_gpu_info()
                    self.state_data['gpu'] = gpus
            except (ImportError, AttributeError):
                pass
                
        except ImportError:
            self.state_data.update({
                'memory_percent': 0,
                'memory_available': 0,
                'cpu_percent': 0,
                'timestamp': time.time()
            })


class KnowledgeModelingModule:
    """Maintains representations of system knowledge."""
    
    def __init__(self):
        """Initialize the knowledge modeling module."""
        self.knowledge_graph = {}
        self.confidence_map = {}
        self.knowledge_history = []
        self.max_history_length = 100
    
    def add_knowledge(self, key: str, value: Any, confidence: float, source: str):
        """Add or update a knowledge element.
        
        Args:
            key: Identifier for the knowledge element
            value: The knowledge content
            confidence: Confidence level (0.0-1.0)
            source: Source of the knowledge
        """
        self.knowledge_graph[key] = value
        self.confidence_map[key] = confidence
        
        # Add to history
        history_entry = {
            'timestamp': time.time(),
            'key': key,
            'value': value,
            'confidence': confidence,
            'source': source
        }
        
        self.knowledge_history.append(history_entry)
        
        # Trim history if too long
        if len(self.knowledge_history) > self.max_history_length:
            self.knowledge_history = self.knowledge_history[-self.max_history_length:]
    
    def get_knowledge(self, key: str) -> Tuple[Any, float]:
        """Retrieve knowledge and its confidence.
        
        Args:
            key: The knowledge identifier
            
        Returns:
            Tuple of (value, confidence), or (None, 0.0) if not found
        """
        if key in self.knowledge_graph:
            return (self.knowledge_graph[key], self.confidence_map.get(key, 0.0))
        return (None, 0.0)
    
    def get_knowledge_boundaries(self) -> Set[str]:
        """Identify knowledge boundaries (low confidence areas).
        
        Returns:
            Set of knowledge keys with low confidence
        """
        return {key for key, conf in self.confidence_map.items() if conf < 0.5}
    
    def serialize(self) -> Dict:
        """Serialize the knowledge model to a dictionary."""
        return {
            'knowledge_graph': self.knowledge_graph,
            'confidence_map': self.confidence_map,
            'history_sample': self.knowledge_history[-10:] if self.knowledge_history else []
        }
    
    def load(self, data: Dict):
        """Load from serialized data."""
        if 'knowledge_graph' in data:
            self.knowledge_graph = data['knowledge_graph']
        if 'confidence_map' in data:
            self.confidence_map = data['confidence_map']


class CapabilityAssessmentModule:
    """Models the system's abilities and limitations."""
    
    def __init__(self):
        """Initialize the capability assessment module."""
        self.capabilities = {}
        self.performance_history = {}
        self.resource_requirements = {}
    
    def register_capability(self, capability_id: str, description: str, 
                           resource_requirements: Dict = None):
        """Register a system capability.
        
        Args:
            capability_id: Unique identifier for the capability
            description: Human-readable description
            resource_requirements: Dict of resource requirements
        """
        self.capabilities[capability_id] = {
            'description': description,
            'enabled': True,
            'performance': 0.0,
            'confidence': 0.0
        }
        
        if resource_requirements:
            self.resource_requirements[capability_id] = resource_requirements
    
    def update_capability_performance(self, capability_id: str, 
                                     performance: float, confidence: float):
        """Update performance metrics for a capability.
        
        Args:
            capability_id: The capability to update
            performance: Performance metric (0.0-1.0)
            confidence: Confidence in this assessment (0.0-1.0)
        """
        if capability_id not in self.capabilities:
            logger.warning(f"Updating unknown capability: {capability_id}")
            self.register_capability(capability_id, "Auto-registered capability")
        
        self.capabilities[capability_id]['performance'] = performance
        self.capabilities[capability_id]['confidence'] = confidence
        
        # Add to history
        if capability_id not in self.performance_history:
            self.performance_history[capability_id] = []
            
        self.performance_history[capability_id].append({
            'timestamp': time.time(),
            'performance': performance,
            'confidence': confidence
        })
        
        # Trim history if too long
        if len(self.performance_history[capability_id]) > 100:
            self.performance_history[capability_id] = \
                self.performance_history[capability_id][-100:]
    
    def can_perform(self, capability_id: str, required_performance: float = 0.5) -> bool:
        """Check if the system can perform a capability at required level.
        
        Args:
            capability_id: The capability to check
            required_performance: Minimum required performance level
            
        Returns:
            Boolean indicating whether the system can perform the capability
        """
        if capability_id not in self.capabilities:
            return False
            
        cap = self.capabilities[capability_id]
        return cap['enabled'] and cap['performance'] >= required_performance
    
    def get_capabilities_report(self) -> Dict:
        """Generate a report of all capabilities and their status."""
        return {
            'capabilities': self.capabilities,
            'resource_requirements': self.resource_requirements
        }


class ConfidenceEstimationModule:
    """Quantifies uncertainty across all predictions."""
    
    def __init__(self):
        """Initialize the confidence estimation module."""
        self.global_confidence = 0.8  # Starting confidence level
        self.confidence_history = []
        self.calibration_data = []
    
    def estimate_confidence(self, inputs: Dict, 
                           prediction: Any, 
                           model_uncertainty: Optional[float] = None) -> float:
        """Estimate confidence for a prediction.
        
        Args:
            inputs: Input data for the prediction
            prediction: The prediction made
            model_uncertainty: Model-provided uncertainty (if available)
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Default confidence estimation logic
        # This is a simplistic placeholder - real implementations would
        # use more sophisticated uncertainty quantification
        
        confidence = self.global_confidence
        
        # If model provides uncertainty, use it
        if model_uncertainty is not None:
            confidence = 1.0 - model_uncertainty
        
        # Apply domain-specific confidence adjustments
        confidence = self._adjust_confidence(confidence, inputs, prediction)
        
        # Record confidence
        self.confidence_history.append({
            'timestamp': time.time(),
            'confidence': confidence,
            'prediction': prediction
        })
        
        return confidence
    
    def _adjust_confidence(self, base_confidence: float, 
                          inputs: Dict, prediction: Any) -> float:
        """Apply adjustments to the base confidence estimate.
        
        Args:
            base_confidence: Initial confidence estimate
            inputs: Input data
            prediction: Predicted output
            
        Returns:
            Adjusted confidence score
        """
        confidence = base_confidence
        
        # Detect out-of-distribution inputs
        if self._is_out_of_distribution(inputs):
            confidence *= 0.8
        
        # Bound confidence to valid range
        return max(0.0, min(1.0, confidence))
    
    def _is_out_of_distribution(self, inputs: Dict) -> bool:
        """Check if inputs appear to be out of distribution.
        
        Args:
            inputs: Input data
            
        Returns:
            Boolean indicating if inputs appear unusual
        """
        # Placeholder for OOD detection logic
        # In a real implementation, this would use statistical tests
        # or dedicated OOD detection models
        return False
    
    def update_calibration(self, confidence: float, correct: bool):
        """Update calibration data with ground truth.
        
        Args:
            confidence: Confidence estimate that was given
            correct: Whether the prediction was correct
        """
        self.calibration_data.append((confidence, 1.0 if correct else 0.0))
        
        # Re-calibrate global confidence periodically
        if len(self.calibration_data) % 100 == 0:
            self._recalibrate()
    
    def _recalibrate(self):
        """Recalibrate confidence estimation based on history."""
        if not self.calibration_data:
            return
            
        # Simple recalibration approach
        confidences, correctness = zip(*self.calibration_data[-1000:])
        avg_confidence = np.mean(confidences)
        avg_correctness = np.mean(correctness)
        
        # Adjust global confidence based on calibration error
        calibration_error = avg_correctness - avg_confidence
        self.global_confidence += 0.1 * calibration_error


class RegulatoryControlModule:
    """Modifies system behavior based on self-awareness."""
    
    def __init__(self, safety_bounds: Dict = None):
        """Initialize the regulatory control module.
        
        Args:
            safety_bounds: Dictionary of safety constraints
        """
        self.safety_bounds = safety_bounds or {}
        self.active_regulations = {}
        self.regulation_history = []
    
    def add_regulation(self, regulation_id: str, 
                      condition_fn, action_fn, 
                      description: str = ""):
        """Add a regulatory rule.
        
        Args:
            regulation_id: Unique identifier for this regulation
            condition_fn: Function that evaluates when to apply regulation
            action_fn: Function that performs the regulatory action
            description: Human-readable description
        """
        self.active_regulations[regulation_id] = {
            'condition': condition_fn,
            'action': action_fn,
            'description': description,
            'enabled': True,
            'last_triggered': None
        }
    
    def evaluate_regulations(self, system_state: Dict) -> List[str]:
        """Evaluate and apply all regulatory rules.
        
        Args:
            system_state: Current system state
            
        Returns:
            List of regulation IDs that were triggered
        """
        triggered = []
        
        for reg_id, regulation in self.active_regulations.items():
            if not regulation['enabled']:
                continue
                
            try:
                if regulation['condition'](system_state):
                    # Apply the regulation
                    regulation['action'](system_state)
                    regulation['last_triggered'] = time.time()
                    triggered.append(reg_id)
                    
                    # Record in history
                    self.regulation_history.append({
                        'timestamp': time.time(),
                        'regulation_id': reg_id,
                        'description': regulation['description']
                    })
            except Exception as e:
                logger.error(f"Error in regulation {reg_id}: {e}")
        
        return triggered
    
    def generate_assistance_request(self, issue: str, 
                                   severity: float,
                                   context: Dict) -> Dict:
        """Generate a request for human assistance.
        
        Args:
            issue: Description of the issue
            severity: Severity level (0.0-1.0)
            context: Relevant context information
            
        Returns:
            Assistance request object
        """
        request = {
            'timestamp': time.time(),
            'issue': issue,
            'severity': severity,
            'context': context,
            'id': f"assist-{int(time.time())}"
        }
        
        # Log the assistance request
        logger.warning(f"Assistance request: {issue} (severity: {severity})")
        
        # Add to regulation history
        self.regulation_history.append({
            'timestamp': time.time(),
            'regulation_id': 'assistance_request',
            'description': issue,
            'request': request
        })
        
        return request


class SelfAwarenessFramework:
    """Complete self-awareness framework integrating all modules."""
    
    def __init__(self, config: Dict = None):
        """Initialize the self-awareness framework.
        
        Args:
            config: Configuration dictionary
        """
        config = config or {}
        
        # Initialize all component modules
        self.state_monitoring = StateMonitoringModule(
            sampling_rate=config.get('monitoring_rate', 1.0)
        )
        self.knowledge_modeling = KnowledgeModelingModule()
        self.capability_assessment = CapabilityAssessmentModule()
        self.confidence_estimation = ConfidenceEstimationModule()
        self.regulatory_control = RegulatoryControlModule(
            safety_bounds=config.get('safety_bounds', {})
        )
        
        # Setup metrics tracking
        self.metrics = SelfAwarenessMetrics()
        
        # Connect monitoring to regulatory control
        self.state_monitoring.register_callback(self._state_update_handler)
        
        # Storage for self-model
        self.self_model = {
            'id': config.get('id', f"self-aware-{int(time.time())}"),
            'created_at': time.time(),
            'last_updated': time.time()
        }
        
        logger.info(f"Self-awareness framework initialized: {self.self_model['id']}")
    
    def start(self):
        """Start the self-awareness framework."""
        logger.info("Starting self-awareness framework")
        self.state_monitoring.start_monitoring()
        
        # Register basic capabilities
        self.capability_assessment.register_capability(
            'self_monitoring', 
            'Monitor own system state',
            {'cpu': 0.05, 'memory': 50 * 1024 * 1024}  # 50MB
        )
        
        self.capability_assessment.register_capability(
            'uncertainty_quantification',
            'Estimate uncertainty in predictions',
            {'cpu': 0.1, 'memory': 100 * 1024 * 1024}  # 100MB
        )
        
        # Register basic regulations
        self._setup_default_regulations()
    
    def stop(self):
        """Stop the self-awareness framework."""
        logger.info("Stopping self-awareness framework")
        self.state_monitoring.stop_monitoring()
    
    def _setup_default_regulations(self):
        """Set up default regulatory controls."""
        # Resource usage regulation
        self.regulatory_control.add_regulation(
            'high_memory_usage',
            lambda state: state.get('memory_percent', 0) > 90,
            lambda state: self._handle_high_memory(),
            'Regulate high memory usage'
        )
        
        # Low confidence regulation
        self.regulatory_control.add_regulation(
            'low_confidence_alert',
            lambda state: self.confidence_estimation.global_confidence < 0.5,
            lambda state: self._handle_low_confidence(),
            'Respond to low confidence conditions'
        )
    
    def _handle_high_memory(self):
        """Handle high memory usage regulation."""
        logger.warning("High memory usage detected, initiating memory optimization")
        
        # Add knowledge about this limitation
        self.knowledge_modeling.add_knowledge(
            'memory_constraint',
            'System is operating near memory limits',
            1.0,
            'resource_monitor'
        )
        
        # Example of a regulatory action: request garbage collection
        import gc
        gc.collect()
    
    def _handle_low_confidence(self):
        """Handle low confidence regulation."""
        logger.warning("Operating with low confidence, adjusting behavior")
        
        # Add knowledge about this limitation
        self.knowledge_modeling.add_knowledge(
            'confidence_constraint',
            'System has low confidence in its predictions',
            0.9,
            'confidence_monitor'
        )
        
        # This could trigger behavior changes like:
        # 1. Being more conservative in decisions
        # 2. Seeking additional information
        # 3. Requesting human intervention
    
    def _state_update_handler(self, state: Dict):
        """Handle updates from the state monitoring module.
        
        Args:
            state: Current system state
        """
        # Update last state in self-model
        self.self_model['last_state'] = state
        self.self_model['last_updated'] = time.time()
        
        # Apply regulatory controls
        triggered = self.regulatory_control.evaluate_regulations(state)
        if triggered:
            logger.debug(f"Triggered regulations: {triggered}")
    
    def estimate_system_confidence(self) -> float:
        """Estimate overall system confidence.
        
        Returns:
            Overall confidence score (0.0-1.0)
        """
        # This is a simple example that could be expanded with more complex aggregation
        return self.confidence_estimation.global_confidence
    
    def get_self_model(self) -> Dict:
        """Get the current self-model.
        
        Returns:
            Dictionary representing the system's self-model
        """
        # Update the self-model with current information
        self.self_model.update({
            'knowledge_boundaries': list(self.knowledge_modeling.get_knowledge_boundaries()),
            'capabilities': self.capability_assessment.get_capabilities_report(),
            'confidence': self.estimate_system_confidence(),
            'metrics': self.metrics.to_dict()
        })
        
        return self.self_model
    
    def save_self_model(self, filepath: str):
        """Save the self-model to a file.
        
        Args:
            filepath: Path to save the file
        """
        model = self.get_self_model()
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(model, f, indent=2)
        
        logger.info(f"Self-model saved to {filepath}")
    
    def load_self_model(self, filepath: str):
        """Load a self-model from a file.
        
        Args:
            filepath: Path to the file
        """
        if not os.path.exists(filepath):
            logger.error(f"Self-model file not found: {filepath}")
            return False
            
        try:
            with open(filepath, 'r') as f:
                model = json.load(f)
                
            # Update basic self information
            self.self_model.update({
                'id': model.get('id', self.self_model['id']),
                'created_at': model.get('created_at', self.self_model['created_at']),
                'loaded_from': filepath,
                'loaded_at': time.time()
            })
            
            # Load metrics if available
            if 'metrics' in model:
                self.metrics.load_from_dict(model['metrics'])
                
            # Load knowledge if available
            if 'knowledge' in model:
                self.knowledge_modeling.load(model['knowledge'])
                
            logger.info(f"Self-model loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading self-model: {e}")
            return False

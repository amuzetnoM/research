#!/usr/bin/env python3
"""
Complete Self-Awareness Framework for AI Systems

This module implements the computational self-awareness framework as described in
the research paper "Self-Awareness Mechanics in Artificial Intelligence Systems".
It provides a comprehensive implementation for AI systems to develop self-reflective
capabilities, including:

- State monitoring and introspection
- Knowledge boundary awareness 
- Capability assessment and modeling
- Confidence estimation and uncertainty quantification
- Regulatory control mechanisms
"""

import logging
import time
import numpy as np
import threading
import json
import os
import psutil
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Set, Callable, Union
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("cognitive-self-awareness")

# ==========================================
# Base Classes and Enumerations
# ==========================================

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
        self.last_update = time.time()
    
    def update(self, dimension: AwarenessDimension, value: float):
        """Update a specific dimension metric.
        
        Args:
            dimension: The awareness dimension to update
            value: The new metric value (0.0-1.0)
        """
        self.metrics[dimension.value] = value
        self.history.append({
            'timestamp': time.time(),
            'dimension': dimension.value,
            'value': value
        })
        
        # Trim history if it gets too long
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        
        self.last_update = time.time()
    
    def get_aggregate_score(self) -> float:
        """Calculate an aggregate self-awareness score.
        
        Returns:
            Float between 0.0-1.0 representing overall self-awareness
        """
        return sum(self.metrics.values()) / len(self.metrics)
    
    def get_dimension_score(self, dimension: AwarenessDimension) -> float:
        """Get the score for a specific dimension.
        
        Args:
            dimension: The awareness dimension to query
            
        Returns:
            Score for the specified dimension (0.0-1.0)
        """
        return self.metrics[dimension.value]
    
    def to_dict(self) -> Dict:
        """Convert metrics to a dictionary for serialization.
        
        Returns:
            Dictionary containing all metrics
        """
        return {
            'dimensions': self.metrics.copy(),
            'confidence_accuracy': self.confidence_accuracy,
            'adaptation_efficiency': self.adaptation_efficiency,
            'recovery_time': self.recovery_time,
            'boundary_detection_rate': self.boundary_detection_rate,
            'aggregate_score': self.get_aggregate_score(),
            'last_update': self.last_update
        }
    
    def load_from_dict(self, data: Dict):
        """Load metrics from a dictionary.
        
        Args:
            data: Dictionary containing metrics data
        """
        if 'dimensions' in data:
            for dim, value in data['dimensions'].items():
                if dim in self.metrics:
                    self.metrics[dim] = value
        
        self.confidence_accuracy = data.get('confidence_accuracy', self.confidence_accuracy)
        self.adaptation_efficiency = data.get('adaptation_efficiency', self.adaptation_efficiency)
        self.recovery_time = data.get('recovery_time', self.recovery_time)
        self.boundary_detection_rate = data.get('boundary_detection_rate', self.boundary_detection_rate)


# ==========================================
# Core Framework Modules
# ==========================================

class StateMonitoringModule:
    """Collects real-time telemetry on system operations."""
    
    def __init__(self, sampling_rate: float = 1.0):
        """Initialize the state monitoring module.
        
        Args:
            sampling_rate: Number of samples per second (Hz)
        """
        self.sampling_rate = max(0.1, min(10.0, sampling_rate))  # Clamp between 0.1-10 Hz
        self.monitoring_active = False
        self.monitor_thread = None
        self.callbacks = []
        self.process = psutil.Process()
        
        # The current state representation
        self.state_data = {
            "timestamp": time.time(),
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "memory_info": {},
            "io_counters": {},
            "threads": 0,
            "open_files": 0,
            "connections": 0,
            "context_switches": 0,
            "custom_metrics": {}
        }
    
    def register_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Register a callback to receive state updates.
        
        Args:
            callback: Function that will be called with state data
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Unregister a previously registered callback.
        
        Args:
            callback: Function to remove from callbacks
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def start_monitoring(self):
        """Start the monitoring thread."""
        if self.monitoring_active:
            logger.warning("State monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()
        logger.info(f"State monitoring started (sampling rate: {self.sampling_rate} Hz)")
    
    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
            self.monitor_thread = None
        logger.info("State monitoring stopped")
    
    def add_custom_metric(self, name: str, value: Any):
        """Add a custom metric to the state data.
        
        Args:
            name: Name of the metric
            value: Value of the metric
        """
        self.state_data["custom_metrics"][name] = value
    
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
        try:
            # Basic system metrics
            self.state_data["timestamp"] = time.time()
            self.state_data["cpu_percent"] = self.process.cpu_percent(interval=0.1)
            self.state_data["memory_percent"] = self.process.memory_percent()
            
            # Detailed memory information
            memory_info = self.process.memory_info()
            self.state_data["memory_info"] = {
                "rss": memory_info.rss,  # Resident Set Size
                "vms": memory_info.vms,  # Virtual Memory Size
                "shared": getattr(memory_info, "shared", 0),
                "text": getattr(memory_info, "text", 0),
                "data": getattr(memory_info, "data", 0)
            }
            
            # Process statistics
            self.state_data["threads"] = self.process.num_threads()
            
            try:
                self.state_data["open_files"] = len(self.process.open_files())
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                self.state_data["open_files"] = -1
            
            try:
                self.state_data["connections"] = len(self.process.connections())
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                self.state_data["connections"] = -1
            
            # I/O statistics if available
            try:
                io_counters = self.process.io_counters()
                self.state_data["io_counters"] = {
                    "read_count": io_counters.read_count,
                    "write_count": io_counters.write_count,
                    "read_bytes": io_counters.read_bytes,
                    "write_bytes": io_counters.write_bytes
                }
            except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError):
                self.state_data["io_counters"] = {}
            
            # System-wide metrics
            system_ctx = psutil.cpu_stats()
            self.state_data["context_switches"] = system_ctx.ctx_switches
            
        except Exception as e:
            logger.error(f"Error collecting state data: {e}")


class KnowledgeModelingModule:
    """Maintains representations of system knowledge."""
    
    def __init__(self):
        """Initialize the knowledge modeling module."""
        # Core knowledge representation
        self.knowledge_graph = {}
        
        # Confidence in each knowledge element
        self.confidence_map = {}
        
        # History of knowledge updates
        self.knowledge_history = []
        self.max_history_length = 100
        
        # Knowledge boundaries
        self.knowledge_boundaries = set()
        
        # Metadata
        self.last_updated = time.time()
    
    def add_knowledge(self, key: str, value: Any, confidence: float = 1.0, source: str = "system"):
        """Add or update a knowledge element.
        
        Args:
            key: Unique identifier for the knowledge
            value: The knowledge content
            confidence: Confidence level (0.0-1.0)
            source: Source of the knowledge
        """
        if key in self.knowledge_graph:
            # Update existing knowledge
            old_value = self.knowledge_graph[key]
            old_confidence = self.confidence_map[key]
            
            # Record history
            self.knowledge_history.append({
                "key": key,
                "old_value": old_value,
                "new_value": value,
                "old_confidence": old_confidence,
                "new_confidence": confidence,
                "timestamp": time.time(),
                "source": source
            })
            
            # Trim history if needed
            if len(self.knowledge_history) > self.max_history_length:
                self.knowledge_history = self.knowledge_history[-self.max_history_length:]
        
        # Store the knowledge
        self.knowledge_graph[key] = value
        self.confidence_map[key] = confidence
        self.last_updated = time.time()
    
    def get_knowledge(self, key: str) -> Tuple[Any, float]:
        """Retrieve a knowledge element and its confidence.
        
        Args:
            key: Unique identifier for the knowledge
            
        Returns:
            Tuple of (knowledge_value, confidence)
        """
        if key in self.knowledge_graph:
            return (self.knowledge_graph[key], self.confidence_map[key])
        else:
            # Mark this as a knowledge boundary
            self.knowledge_boundaries.add(key)
            return (None, 0.0)
    
    def remove_knowledge(self, key: str):
        """Remove a knowledge element.
        
        Args:
            key: Unique identifier for the knowledge to remove
        """
        if key in self.knowledge_graph:
            # Record history
            self.knowledge_history.append({
                "key": key,
                "old_value": self.knowledge_graph[key],
                "new_value": None,
                "old_confidence": self.confidence_map[key],
                "new_confidence": 0.0,
                "timestamp": time.time(),
                "action": "remove"
            })
            
            # Remove the knowledge
            del self.knowledge_graph[key]
            del self.confidence_map[key]
            self.last_updated = time.time()
    
    def get_knowledge_boundaries(self) -> Set[str]:
        """Get the set of identified knowledge boundaries.
        
        Returns:
            Set of knowledge keys that have been queried but not found
        """
        return self.knowledge_boundaries.copy()
    
    def decay_confidence(self, decay_rate: float = 0.01):
        """Apply time-based decay to knowledge confidence.
        
        Args:
            decay_rate: Rate at which confidence decays (0.0-1.0)
        """
        for key in self.confidence_map:
            # Apply decay
            self.confidence_map[key] *= (1.0 - decay_rate)
            
            # If confidence drops too low, consider it a boundary
            if self.confidence_map[key] < 0.2:
                self.knowledge_boundaries.add(key)
    
    def save(self, filepath: str):
        """Save the knowledge model to a file.
        
        Args:
            filepath: Path to save the knowledge model
        """
        data = {
            "knowledge_graph": {k: str(v) if not isinstance(v, (int, float, str, bool, list, dict)) else v 
                              for k, v in self.knowledge_graph.items()},
            "confidence_map": self.confidence_map,
            "knowledge_boundaries": list(self.knowledge_boundaries),
            "last_updated": self.last_updated,
            "saved_at": time.time()
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Knowledge model saved to {filepath}")
    
    def load(self, data: Dict[str, Any]):
        """Load the knowledge model from a dictionary.
        
        Args:
            data: Dictionary containing knowledge model data
        """
        if "knowledge_graph" in data:
            self.knowledge_graph = data["knowledge_graph"]
        
        if "confidence_map" in data:
            self.confidence_map = data["confidence_map"]
        
        if "knowledge_boundaries" in data:
            self.knowledge_boundaries = set(data["knowledge_boundaries"])
        
        self.last_updated = data.get("last_updated", time.time())
        logger.info("Knowledge model loaded")


class CapabilityAssessmentModule:
    """Models the system's abilities and limitations."""
    
    def __init__(self):
        """Initialize the capability assessment module."""
        self.capabilities = {}
        self.performance_history = {}
        self.resource_requirements = {}
        self.last_updated = time.time()
    
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
        
        # Initialize performance history
        self.performance_history[capability_id] = []
        self.last_updated = time.time()
        
        logger.info(f"Registered capability: {capability_id}")
    
    def update_capability_performance(self, capability_id: str, 
                                     performance: float, confidence: float):
        """Update performance metrics for a capability.
        
        Args:
            capability_id: Unique identifier for the capability
            performance: Performance score (0.0-1.0)
            confidence: Confidence in the performance assessment (0.0-1.0)
        """
        if capability_id not in self.capabilities:
            logger.warning(f"Updating unknown capability: {capability_id}")
            self.register_capability(capability_id, "Auto-registered capability")
        
        # Update current performance
        self.capabilities[capability_id]['performance'] = performance
        self.capabilities[capability_id]['confidence'] = confidence
        
        # Add to history
        self.performance_history[capability_id].append({
            'timestamp': time.time(),
            'performance': performance,
            'confidence': confidence
        })
        
        # Trim history if too long
        if len(self.performance_history[capability_id]) > 100:
            self.performance_history[capability_id] = \
                self.performance_history[capability_id][-100:]
        
        self.last_updated = time.time()
    
    def disable_capability(self, capability_id: str):
        """Disable a capability.
        
        Args:
            capability_id: Unique identifier for the capability
        """
        if capability_id in self.capabilities:
            self.capabilities[capability_id]['enabled'] = False
            logger.info(f"Disabled capability: {capability_id}")
    
    def enable_capability(self, capability_id: str):
        """Enable a capability.
        
        Args:
            capability_id: Unique identifier for the capability
        """
        if capability_id in self.capabilities:
            self.capabilities[capability_id]['enabled'] = True
            logger.info(f"Enabled capability: {capability_id}")
    
    def can_perform(self, capability_id: str, required_performance: float = 0.5) -> bool:
        """Check if the system can perform a capability at the required level.
        
        Args:
            capability_id: Unique identifier for the capability
            required_performance: Minimum required performance level (0.0-1.0)
            
        Returns:
            Boolean indicating whether the capability can be performed
        """
        if capability_id not in self.capabilities:
            return False
        
        capability = self.capabilities[capability_id]
        return (capability['enabled'] and 
                capability['performance'] >= required_performance)
    
    def get_capabilities_report(self) -> Dict:
        """Generate a report of all capabilities and their status.
        
        Returns:
            Dictionary containing capability status information
        """
        report = {
            'capabilities': self.capabilities.copy(),
            'timestamp': time.time(),
            'total_capabilities': len(self.capabilities),
            'enabled_capabilities': sum(1 for c in self.capabilities.values() if c['enabled']),
            'high_performance_capabilities': sum(1 for c in self.capabilities.values() 
                                              if c['performance'] > 0.7)
        }
        
        return report


class ConfidenceEstimationModule:
    """Quantifies uncertainty across all predictions."""
    
    def __init__(self):
        """Initialize the confidence estimation module."""
        self.global_confidence = 0.8  # Starting confidence level
        self.confidence_history = []
        self.calibration_data = []
        self.domain_adjustments = {}
        self.last_updated = time.time()
    
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
            'prediction': str(prediction)[:100]  # Truncate long predictions
        })
        
        # Trim history if it gets too long
        if len(self.confidence_history) > 1000:
            self.confidence_history = self.confidence_history[-1000:]
        
        self.last_updated = time.time()
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
            confidence *= 0.8  # Reduce confidence for OOD inputs
        
        # Apply domain-specific adjustments
        domain = inputs.get('domain', 'default')
        if domain in self.domain_adjustments:
            confidence *= self.domain_adjustments[domain]
        
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
        
        # Trim calibration data if it gets too long
        if len(self.calibration_data) > 10000:
            self.calibration_data = self.calibration_data[-10000:]
        
        # Re-calibrate global confidence periodically
        if len(self.calibration_data) % 100 == 0:
            self._recalibrate()
        
        self.last_updated = time.time()
    
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
        self.global_confidence = max(0.1, min(0.9, self.global_confidence))
        
        logger.debug(f"Recalibrated confidence: {self.global_confidence:.2f} "
                    f"(error: {calibration_error:.2f})")
    
    def set_domain_adjustment(self, domain: str, adjustment_factor: float):
        """Set confidence adjustment factor for a specific domain.
        
        Args:
            domain: Domain identifier
            adjustment_factor: Factor to adjust confidence by (0.0-2.0)
        """
        self.domain_adjustments[domain] = max(0.1, min(2.0, adjustment_factor))
    
    def get_confidence_stats(self) -> Dict[str, float]:
        """Get statistics about confidence estimation.
        
        Returns:
            Dictionary with confidence statistics
        """
        if not self.confidence_history:
            return {"global_confidence": self.global_confidence}
        
        recent_confidences = [h['confidence'] for h in self.confidence_history[-100:]]
        
        return {
            "global_confidence": self.global_confidence,
            "recent_avg_confidence": np.mean(recent_confidences),
            "recent_min_confidence": min(recent_confidences),
            "recent_max_confidence": max(recent_confidences),
            "recent_std_confidence": np.std(recent_confidences),
            "calibration_samples": len(self.calibration_data)
        }


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
        self.last_update = time.time()
    
    def add_regulation(self, regulation_id: str, 
                      condition_fn: Callable, action_fn: Callable, 
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
        
        logger.info(f"Added regulation: {regulation_id} - {description}")
    
    def enable_regulation(self, regulation_id: str):
        """Enable a specific regulation.
        
        Args:
            regulation_id: ID of the regulation to enable
        """
        if regulation_id in self.active_regulations:
            self.active_regulations[regulation_id]['enabled'] = True
            logger.info(f"Enabled regulation: {regulation_id}")
    
    def disable_regulation(self, regulation_id: str):
        """Disable a specific regulation.
        
        Args:
            regulation_id: ID of the regulation to disable
        """
        if regulation_id in self.active_regulations:
            self.active_regulations[regulation_id]['enabled'] = False
            logger.info(f"Disabled regulation: {regulation_id}")
    
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
                    
                    logger.info(f"Triggered regulation: {reg_id}")
            except Exception as e:
                logger.error(f"Error in regulation {reg_id}: {e}")
        
        # Trim history if needed
        if len(self.regulation_history) > 1000:
            self.regulation_history = self.regulation_history[-1000:]
        
        self.last_update = time.time()
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
        logger.warning(f"Assistance request: {issue} (severity: {severity:.2f})")
        
        # Add to regulation history
        self.regulation_history.append({
            'timestamp': time.time(),
            'regulation_id': 'assistance_request',
            'description': issue,
            'request': request
        })
        
        return request
    
    def get_regulation_history(self, limit: int = 100) -> List[Dict]:
        """Get recent regulation history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of recent regulation events
        """
        return self.regulation_history[-limit:]


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
            'last_updated': time.time(),
            'metrics': {},
            'capabilities': {},
            'knowledge_boundaries': [],
            'confidence': 0.0,
            'last_state': {}
        }
        
        # Configuration and controls
        self.active = False
        self.config = config
        self.data_path = config.get('data_path', 'data/self_awareness')
        
        logger.info(f"Self-awareness framework initialized: {self.self_model['id']}")
    
    def start(self):
        """Start the self-awareness framework."""
        if self.active:
            logger.warning("Self-awareness framework already active")
            return
            
        logger.info("Starting self-awareness framework")
        self.active = True
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
        
        self.capability_assessment.register_capability(
            'recursive_reasoning',
            'Reason about its own reasoning process',
            {'cpu': 0.2, 'memory': 150 * 1024 * 1024}  # 150MB
        )
        
        # Register basic regulations
        self._setup_default_regulations()
    
    def stop(self):
        """Stop the self-awareness framework."""
        if not self.active:
            logger.warning("Self-awareness framework not active")
            return
            
        logger.info("Stopping self-awareness framework")
        self.active = False
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
        
        # High CPU usage regulation
        self.regulatory_control.add_regulation(
            'high_cpu_usage',
            lambda state: state.get('cpu_percent', 0) > 80,
            lambda state: self._handle_high_cpu(),
            'Regulate high CPU usage'
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
    
    def _handle_high_cpu(self):
        """Handle high CPU usage regulation."""
        logger.warning("High CPU usage detected, initiating CPU optimization")
        
        # Add knowledge about this limitation
        self.knowledge_modeling.add_knowledge(
            'cpu_constraint',
            'System is operating near CPU limits',
            1.0,
            'resource_monitor'
        )
        
        # Reduce sampling rate temporarily
        original_rate = self.state_monitoring.sampling_rate
        self.state_monitoring.sampling_rate = max(0.1, original_rate * 0.5)
        
        # After 60 seconds, restore original sampling rate
        threading.Timer(60.0, lambda: setattr(self.state_monitoring, 'sampling_rate', original_rate)).start()
    
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
        
        # Generate an assistance request if enabled
        if self.config.get('enable_assistance_requests', True):
            self.regulatory_control.generate_assistance_request(
                issue="Low confidence in predictions",
                severity=0.7,
                context={
                    "global_confidence": self.confidence_estimation.global_confidence,
                    "knowledge_boundaries": list(self.knowledge_modeling.get_knowledge_boundaries())[:10]
                }
            )
    
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
        # Base confidence from confidence estimation module
        confidence = self.confidence_estimation.global_confidence
        
        # Adjust based on capability awareness
        if self.capability_assessment.capabilities:
            # Average confidence across all capabilities
            capability_confidences = [c['confidence'] for c in self.capability_assessment.capabilities.values()]
            capability_confidence = sum(capability_confidences) / len(capability_confidences)
            
            # Weighted combination
            confidence = 0.7 * confidence + 0.3 * capability_confidence
        
        # Bound to valid range
        return max(0.0, min(1.0, confidence))
    
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
            'metrics': self.metrics.to_dict(),
            'last_updated': time.time()
        })
        
        return self.self_model
    
    def save_self_model(self, filepath: str = None):
        """Save the self-model to a file.
        
        Args:
            filepath: Path to save the file (default: auto-generated)
        """
        model = self.get_self_model()
        
        if filepath is None:
            # Auto-generate filepath if not provided
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"self_model_{self.self_model['id']}_{timestamp}.json"
            filepath = os.path.join(self.data_path, filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(model, f, indent=2)
        
        logger.info(f"Self-model saved to {filepath}")
        
        return filepath
    
    def load_self_model(self, filepath: str) -> bool:
        """Load a self-model from a file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Boolean indicating success
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
    
    def update_on_prediction(self, inputs: Dict, prediction: Any, 
                            confidence: Optional[float] = None, 
                            domain: str = 'default'):
        """Update self-awareness based on a prediction made by the system.
        
        Args:
            inputs: Input data for the prediction
            prediction: The prediction made
            confidence: Model's confidence (if available)
            domain: Domain of the prediction
        """
        # Add domain to inputs for confidence estimation
        inputs_with_domain = inputs.copy()
        inputs_with_domain['domain'] = domain
        
        # Estimate confidence if not provided
        if confidence is None:
            confidence = self.confidence_estimation.estimate_confidence(
                inputs_with_domain, prediction
            )
        
        # Update knowledge
        input_hash = str(hash(str(inputs)))
        self.knowledge_modeling.add_knowledge(
            f"prediction_{input_hash}",
            {
                "input_summary": str(inputs)[:100],
                "prediction": str(prediction)[:100],
                "confidence": confidence
            },
            confidence,
            f"prediction_{domain}"
        )
    
    def update_on_feedback(self, inputs: Dict, prediction: Any, 
                         correct: bool, domain: str = 'default'):
        """Update self-awareness based on feedback about a prediction.
        
        Args:
            inputs: Input data for the prediction
            prediction: The prediction made
            correct: Whether the prediction was correct
            domain: Domain of the prediction
        """
        # Add domain to inputs for confidence estimation
        inputs_with_domain = inputs.copy()
        inputs_with_domain['domain'] = domain
        
        # Get the confidence that was estimated
        input_hash = str(hash(str(inputs)))
        knowledge, confidence = self.knowledge_modeling.get_knowledge(f"prediction_{input_hash}")
        
        # Update calibration data
        self.confidence_estimation.update_calibration(confidence, correct)
        
        # Update capability performance
        capability_id = f"prediction_{domain}"
        
        # Get current performance or initialize
        if capability_id not in self.capability_assessment.capabilities:
            self.capability_assessment.register_capability(
                capability_id,
                f"Make predictions in {domain} domain"
            )
            current_performance = 0.5
            current_samples = 0
        else:
            current_performance = self.capability_assessment.capabilities[capability_id]['performance']
            # Estimate number of samples from history
            current_samples = len(self.capability_assessment.performance_history.get(capability_id, []))
        
        # Update performance using exponential moving average
        alpha = 1.0 / (current_samples + 1)
        new_performance = (1 - alpha) * current_performance + alpha * (1.0 if correct else 0.0)
        
        self.capability_assessment.update_capability_performance(
            capability_id,
            new_performance,
            min(1.0, (current_samples + 1) / 100)  # Confidence increases with samples
        )


# ==========================================
# Utility Functions
# ==========================================

def get_default_config() -> Dict[str, Any]:
    """Get the default configuration for the self-awareness framework.
    
    Returns:
        Dictionary with default configuration
    """
    return {
        'monitoring_rate': 1.0,
        'enable_assistance_requests': True,
        'enable_self_modification': False,
        'safety_bounds': {
            'max_memory_usage': 95,  # %
            'max_cpu_usage': 95,  # %
            'max_disk_usage': 95,  # %
        },
        'data_path': 'data/self_awareness'
    }


def main():
    """Run the self-awareness framework as a standalone process."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Self-Awareness Framework")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--monitoring-rate", type=float, default=1.0, 
                        help="Rate at which to monitor system state (Hz)")
    parser.add_argument("--save-interval", type=int, default=300,
                        help="Interval between auto-saving self-models (seconds)")
    args = parser.parse_args()
    
    # Load configuration
    config = get_default_config()
    if args.config:
        try:
            with open(args.config, 'r') as f:
                loaded_config = json.load(f)
                config.update(loaded_config)
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    # Override with command line arguments
    config['monitoring_rate'] = args.monitoring_rate
    
    # Initialize framework
    framework = SelfAwarenessFramework(config)
    framework.start()
    
    try:
        # Run auto-save loop
        last_save = time.time()
        while True:
            time.sleep(1.0)
            
            # Auto-save self-model
            current_time = time.time()
            if current_time - last_save >= args.save_interval:
                framework.save_self_model()
                last_save = current_time
    
    except KeyboardInterrupt:
        logger.info("Shutting down self-awareness framework")
    finally:
        framework.stop()


if __name__ == "__main__":
    main()

"""
Integration Module for AI Frameworks.

This module provides tools for integrating the Self-Awareness Mechanics
and Emotional Dimensionality Framework together.
"""

import logging
import time
from typing import Dict, List, Optional, Tuple, Any
import threading

logger = logging.getLogger('ai.frameworks.integration')

class AwarenessEmotionalBridge:
    """Bridge between Self-Awareness and Emotional Dimensionality frameworks."""
    
    def __init__(self, self_awareness=None, emotional_framework=None):
        """Initialize the bridge.
        
        Args:
            self_awareness: SelfAwarenessFramework instance
            emotional_framework: EmotionalDimensionalityFramework instance
        """
        self.self_awareness = self_awareness
        self.emotional_framework = emotional_framework
        self.bridge_active = False
        self.bridge_thread = None
        self.update_interval = 5.0  # seconds
        self.last_update = 0
        
        # Cross-framework knowledge
        self.emotional_awareness = {}
        self.self_emotional_state = None
    
    def connect_frameworks(self, self_awareness=None, emotional_framework=None):
        """Connect frameworks to the bridge.
        
        Args:
            self_awareness: SelfAwarenessFramework instance
            emotional_framework: EmotionalDimensionalityFramework instance
            
        Returns:
            True if both frameworks are connected, False otherwise
        """
        if self_awareness:
            self.self_awareness = self_awareness
            
        if emotional_framework:
            self.emotional_framework = emotional_framework
        
        return self.is_ready()
    
    def is_ready(self) -> bool:
        """Check if the bridge is ready (both frameworks connected).
        
        Returns:
            True if both frameworks are connected, False otherwise
        """
        return self.self_awareness is not None and self.emotional_framework is not None
    
    def start_bridge(self) -> bool:
        """Start the integration bridge.
        
        Returns:
            True if started successfully, False otherwise
        """
        if not self.is_ready():
            logger.error("Cannot start bridge: frameworks not connected")
            return False
            
        if self.bridge_active:
            logger.warning("Bridge already active")
            return True
            
        self.bridge_active = True
        self.bridge_thread = threading.Thread(
            target=self._bridge_loop,
            daemon=True
        )
        self.bridge_thread.start()
        logger.info("Integration bridge started")
        return True
    
    def stop_bridge(self):
        """Stop the integration bridge."""
        self.bridge_active = False
        if self.bridge_thread:
            self.bridge_thread.join(timeout=2.0)
            logger.info("Integration bridge stopped")
    
    def _bridge_loop(self):
        """Main bridge processing loop."""
        while self.bridge_active:
            try:
                # Check if it's time for an update
                current_time = time.time()
                if current_time - self.last_update >= self.update_interval:
                    self._update_integration()
                    self.last_update = current_time
                
                # Sleep to avoid tight loop
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in bridge loop: {e}")
                time.sleep(1.0)  # Sleep longer on error
    
    def _update_integration(self):
        """Update the integration between frameworks."""
        try:
            # Get self-model from self-awareness
            self_model = self.self_awareness.get_self_model()
            
            # Analyze system state emotionally
            if self_model and 'last_state' in self_model:
                # Convert system state to text for emotional analysis
                state_text = self._state_to_text(self_model['last_state'])
                
                # Analyze the emotional content
                self.self_emotional_state = self.emotional_framework.analyze(
                    state_text, 
                    context={'source': 'system_state'}
                )
                
                # Add system emotional state to self-awareness knowledge
                self.self_awareness.knowledge_modeling.add_knowledge(
                    'system_emotional_state',
                    self.self_emotional_state.serialize(),
                    self.self_emotional_state.confidence,
                    'emotional_framework'
                )
                
                # Add capability assessment based on emotional state
                valence = self.self_emotional_state.dimensions.get('valence', 0)
                arousal = self.self_emotional_state.dimensions.get('arousal', 0)
                
                # Update capabilities based on emotional state
                # High arousal can indicate stress, affect performance
                performance_modifier = 1.0 - (0.3 * abs(arousal) if arousal > 0.5 else 0)
                # Negative valence might indicate issues
                confidence_modifier = 1.0 - (0.2 * abs(valence) if valence < -0.3 else 0)
                
                self.self_awareness.capability_assessment.update_capability_performance(
                    'emotional_stability',
                    performance=max(0.1, (1.0 + valence) / 2),
                    confidence=max(0.1, confidence_modifier)
                )
            
            # Update Emotional Framework with self-awareness data
            confidence = self.self_awareness.estimate_system_confidence()
            
            # Record in emotional awareness
            self.emotional_awareness = {
                'system_confidence': confidence,
                'timestamp': time.time(),
                'knowledge_boundaries': self.self_awareness.knowledge_modeling.get_knowledge_boundaries(),
                'capabilities': self.self_awareness.capability_assessment.get_capabilities_report()
            }
            
            logger.debug("Integration update completed")
            
        except Exception as e:
            logger.error(f"Error updating integration: {e}")
    
    def _state_to_text(self, state: Dict) -> str:
        """Convert system state to text for emotional analysis.
        
        Args:
            state: System state dictionary
            
        Returns:
            Text representation of the state
        """
        lines = []
        
        # Extract key metrics
        if 'memory_percent' in state:
            memory_percent = state['memory_percent']
            if memory_percent > 90:
                lines.append(f"Memory usage is critically high at {memory_percent}%.")
            elif memory_percent > 75:
                lines.append(f"Memory usage is high at {memory_percent}%.")
            else:
                lines.append(f"Memory usage is normal at {memory_percent}%.")
        
        if 'cpu_percent' in state:
            cpu_percent = state['cpu_percent']
            if cpu_percent > 90:
                lines.append(f"CPU usage is extremely high at {cpu_percent}%.")
            elif cpu_percent > 75:
                lines.append(f"CPU usage is elevated at {cpu_percent}%.")
            else:
                lines.append(f"CPU usage is normal at {cpu_percent}%.")
        
        if 'gpu' in state:
            for i, gpu in enumerate(state['gpu']):
                util = gpu.get('utilization_percent', 0)
                temp = gpu.get('temperature_c', 0)
                
                if temp > 85:
                    lines.append(f"GPU {i} temperature is dangerously high at {temp}°C.")
                elif temp > 75:
                    lines.append(f"GPU {i} temperature is very warm at {temp}°C.")
                
                if util > 95:
                    lines.append(f"GPU {i} utilization is maxed out at {util}%.")
                elif util > 80:
                    lines.append(f"GPU {i} utilization is high at {util}%.")
        
        # Add overall assessment
        if any(("critically" in line or "dangerously" in line) for line in lines):
            lines.append("The system is in a critical state and requires immediate attention.")
        elif any(("high" in line or "elevated" in line or "warm" in line) for line in lines):
            lines.append("The system is under significant load but functioning.")
        else:
            lines.append("The system is operating normally with good resource availability.")
        
        return " ".join(lines)
    
    def get_emotional_state(self) -> Dict:
        """Get the emotional state of the system.
        
        Returns:
            Dictionary with emotional state information
        """
        if self.self_emotional_state:
            emotion, confidence = self.emotional_framework.dominant_emotion(
                self.self_emotional_state
            )
            
            return {
                'dominant_emotion': emotion,
                'confidence': confidence,
                'dimensions': self.self_emotional_state.dimensions,
                'last_update': self.last_update
            }
        
        return {
            'dominant_emotion': 'unknown',
            'confidence': 0.0,
            'dimensions': {},
            'last_update': self.last_update
        }
    
    def analyze_emotional_impact(self, action: str) -> Dict:
        """Analyze the potential emotional impact of an action.
        
        Args:
            action: Description of the action
            
        Returns:
            Dictionary with impact analysis
        """
        if not self.is_ready():
            return {'error': 'Frameworks not connected'}
        
        try:
            # Analyze action text
            action_state = self.emotional_framework.analyze(
                action,
                context={'source': 'action_analysis'}
            )
            
            # Get current system emotional state
            system_state = self.self_emotional_state
            
            if system_state and action_state:
                # Calculate emotional distance
                distance = system_state.emotional_distance(action_state)
                
                # Determine if action would improve emotional state
                # (Simplistic: assumes positive valence is better)
                current_valence = system_state.dimensions.get('valence', 0)
                action_valence = action_state.dimensions.get('valence', 0)
                
                is_improvement = action_valence > current_valence
                
                return {
                    'emotional_distance': distance,
                    'is_improvement': is_improvement,
                    'current_state': system_state.serialize(),
                    'projected_state': action_state.serialize(),
                    'confidence': min(system_state.confidence, action_state.confidence)
                }
            
            return {
                'error': 'Incomplete emotional state data',
                'action_analyzed': bool(action_state),
                'system_analyzed': bool(system_state)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing emotional impact: {e}")
            return {'error': str(e)}


# Convenience function to create a bridge with frameworks
def create_bridge():
    """Create an integration bridge with connected frameworks.
    
    Returns:
        AwarenessEmotionalBridge instance
    """
    try:
        from . import get_self_awareness_framework, get_emotional_framework
        from .config import get_self_awareness_config, get_emotional_config
        
        # Create frameworks
        sa_framework = get_self_awareness_framework(get_self_awareness_config())
        edf_framework = get_emotional_framework(get_emotional_config())
        
        # Create and connect bridge
        bridge = AwarenessEmotionalBridge(sa_framework, edf_framework)
        
        # Start frameworks if needed
        if sa_framework:
            sa_framework.start()
        
        return bridge
        
    except Exception as e:
        logger.error(f"Error creating integration bridge: {e}")
        return None

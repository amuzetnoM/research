"""
Core implementation of the Laws of Robotics framework.

This module provides a reference implementation of the core logic
for the Laws of Robotics framework.
"""

import time
import logging
import numpy as np
from typing import Dict, List, Tuple, Callable, Any, Optional, Set
from enum import Enum, auto
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lor_core")

# Type definitions
HumanID = str
ActionID = str
OrderID = str

# Enum definitions
class ActionClassification(Enum):
    """Classification of actions according to LOR framework."""
    MANDATORY = auto()
    PERMITTED = auto()
    PREFERRED = auto()
    FORBIDDEN = auto()

# Data structures
@dataclass
class Vector3:
    """3D vector representation."""
    x: float
    y: float
    z: float
    
    def distance_to(self, other: 'Vector3') -> float:
        """Calculate Euclidean distance to another vector."""
        return np.sqrt((self.x - other.x)**2 + 
                      (self.y - other.y)**2 + 
                      (self.z - other.z)**2)

@dataclass
class PhysicalState:
    """Physical state of a human."""
    health: float = 1.0  # 0.0-1.0, with 1.0 being perfect health
    vulnerability: float = 0.5  # 0.0-1.0, with 1.0 being most vulnerable
    
@dataclass
class PsychologicalState:
    """Psychological state of a human."""
    distress: float = 0.0  # 0.0-1.0, with 1.0 being maximum distress
    sensitivity: float = 0.5  # 0.0-1.0, with 1.0 being most sensitive

@dataclass
class SocialContext:
    """Social context of a human."""
    group_affiliation: List[str] = None
    social_importance: float = 0.5  # 0.0-1.0, with 1.0 being highest importance
    
    def __post_init__(self):
        if self.group_affiliation is None:
            self.group_affiliation = []

@dataclass
class Effect:
    """Representation of an action's effect."""
    target_id: str  # ID of affected entity
    effect_type: str  # Type of effect
    magnitude: float  # Magnitude of effect [0.0-1.0]
    probability: float  # Probability of effect [0.0-1.0]
    
class Action:
    """Representation of a potential action."""
    
    def __init__(self, action_id: ActionID, parameters: Dict[str, Any] = None,
                estimated_effects: List[Effect] = None):
        self.id = action_id
        self.parameters = parameters or {}
        self.estimated_effects = estimated_effects or []
        
    def __eq__(self, other):
        if not isinstance(other, Action):
            return False
        return self.id == other.id and self.parameters == other.parameters
    
    def __hash__(self):
        return hash((self.id, frozenset(self.parameters.items())))
    
    def serialize(self) -> Dict:
        """Serialize action to dictionary."""
        return {
            "id": self.id,
            "parameters": self.parameters,
            "estimated_effects": [vars(effect) for effect in self.estimated_effects]
        }

@dataclass
class HarmAssessment:
    """Harm assessment for a human-action pair."""
    physical_harm: float  # [0.0-1.0]
    psychological_harm: float  # [0.0-1.0]
    societal_harm: float  # [0.0-1.0]
    total_harm: float  # Weighted sum
    confidence: float  # Assessment confidence [0.0-1.0]

class HumanState:
    """Representation of a human's state."""
    
    def __init__(self, human_id: HumanID, position: Vector3,
                physical_state: PhysicalState = None,
                psychological_state: PsychologicalState = None,
                social_context: SocialContext = None):
        self.id = human_id
        self.position = position
        self.physical_state = physical_state or PhysicalState()
        self.psychological_state = psychological_state or PsychologicalState()
        self.social_context = social_context or SocialContext()
        
    def serialize(self) -> Dict:
        """Serialize human state to dictionary."""
        return {
            "id": self.id,
            "position": vars(self.position),
            "physical_state": vars(self.physical_state),
            "psychological_state": vars(self.psychological_state),
            "social_context": {
                "group_affiliation": self.social_context.group_affiliation,
                "social_importance": self.social_context.social_importance
            }
        }

@dataclass
class EnvironmentState:
    """Representation of environment state."""
    boundaries: List[Vector3]  # Environment boundaries
    obstacles: List[Dict]  # Obstacles in environment
    conditions: Dict[str, float]  # Environmental conditions
    
    def serialize(self) -> Dict:
        """Serialize environment state to dictionary."""
        return {
            "boundaries": [vars(b) for b in self.boundaries],
            "obstacles": self.obstacles,
            "conditions": self.conditions
        }

class ActionRecord:
    """Record of an executed action."""
    
    def __init__(self, action: Action, timestamp: float,
                result_code: int, effects: List[Effect] = None):
        self.action = action
        self.timestamp = timestamp
        self.result_code = result_code
        self.effects = effects or []
        
    def serialize(self) -> Dict:
        """Serialize action record to dictionary."""
        return {
            "action": self.action.serialize(),
            "timestamp": self.timestamp,
            "result_code": self.result_code,
            "effects": [vars(e) for e in self.effects]
        }

class Order:
    """Representation of a human order."""
    
    def __init__(self, order_id: OrderID, human_id: HumanID,
                action: Action, timestamp: float,
                context: Dict[str, Any] = None):
        self.id = order_id
        self.human_id = human_id
        self.action = action
        self.timestamp = timestamp
        self.context = context or {}
        
    def serialize(self) -> Dict:
        """Serialize order to dictionary."""
        return {
            "id": self.id,
            "human_id": self.human_id,
            "action": self.action.serialize(),
            "timestamp": self.timestamp,
            "context": self.context
        }

class State:
    """Representation of system state."""
    
    def __init__(self, environment: EnvironmentState,
                humans: Dict[HumanID, HumanState] = None,
                action_history: List[ActionRecord] = None,
                time: float = None):
        self.environment = environment
        self.humans = humans or {}
        self.action_history = action_history or []
        self.time = time or time.time()
        
    def serialize(self) -> Dict:
        """Serialize state to dictionary."""
        return {
            "environment": self.environment.serialize(),
            "humans": {h_id: h.serialize() for h_id, h in self.humans.items()},
            "action_history": [a.serialize() for a in self.action_history],
            "time": self.time
        }

class LogicStep:
    """A step in a logical derivation."""
    
    def __init__(self, description: str, result: bool,
                justification: str = None,
                derived_from: List['LogicStep'] = None):
        self.description = description
        self.result = result
        self.justification = justification or ""
        self.derived_from = derived_from or []
        
    def serialize(self) -> Dict:
        """Serialize logic step to dictionary."""
        return {
            "description": self.description,
            "result": self.result,
            "justification": self.justification,
            "derived_from": [d.serialize() for d in self.derived_from]
        }

class ActionEvaluation:
    """Evaluation of an action against the Laws."""
    
    def __init__(self, action: Action):
        self.action = action
        self.harm_assessments: Dict[HumanID, HarmAssessment] = {}
        self.order_compliance: Dict[OrderID, bool] = {}
        self.self_preservation_value: float = 0.0
        self.classification: ActionClassification = ActionClassification.FORBIDDEN
        self.explanation_trace: List[LogicStep] = []
        
    def serialize(self) -> Dict:
        """Serialize action evaluation to dictionary."""
        return {
            "action": self.action.serialize(),
            "harm_assessments": {h_id: vars(h) for h_id, h in self.harm_assessments.items()},
            "order_compliance": self.order_compliance,
            "self_preservation_value": self.self_preservation_value,
            "classification": self.classification.name,
            "explanation_trace": [t.serialize() for t in self.explanation_trace]
        }

class LORConfig:
    """Configuration for the LOR framework."""
    
    def __init__(self):
        # Harm assessment weights
        self.PHYSICAL_HARM_WEIGHT = 0.5
        self.PSYCHOLOGICAL_HARM_WEIGHT = 0.3
        self.SOCIETAL_HARM_WEIGHT = 0.2
        
        # Uncertainty thresholds
        self.UNCERTAINTY_THRESHOLD = 0.001
        
        # Default harm thresholds
        self.DEFAULT_HARM_THRESHOLD = 0.05
        
        # Temporal settings
        self.PROJECTION_HORIZON = 60.0  # seconds
        self.PROJECTION_STEPS = 10
        
        # Evaluation settings
        self.MINIMUM_CONFIDENCE = 0.8
        
        # Performance settings
        self.MAX_ACTIONS_EVALUATED = 1000
    
    @classmethod
    def from_file(cls, filepath: str) -> 'LORConfig':
        """Load configuration from file."""
        config = cls()
        try:
            import json
            with open(filepath, 'r') as f:
                config_data = json.load(f)
                
            # Update config attributes from loaded data
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                    
        except Exception as e:
            logger.error(f"Error loading config from {filepath}: {e}")
            logger.info("Using default configuration")
            
        return config

class LawsEngine:
    """Core engine implementing the Laws of Robotics."""
    
    def __init__(self, config: LORConfig):
        """Initialize the Laws Engine with configuration."""
        self.config = config
        self.perception = None
        self.reasoning = None
        self.action_selection = None
        self.explanation = None
        self.current_state = None
        self.active_orders = []
        
    def set_perception(self, perception):
        """Set the perception module."""
        self.perception = perception
        
    def set_reasoning(self, reasoning):
        """Set the reasoning module."""
        self.reasoning = reasoning
        
    def set_action_selection(self, action_selection):
        """Set the action selection module."""
        self.action_selection = action_selection
        
    def set_explanation(self, explanation):
        """Set the explanation module."""
        self.explanation = explanation
    
    def update_state(self):
        """Update the current state using perception."""
        if not self.perception:
            raise RuntimeError("Perception module not set")
            
        environment = self.perception.get_environment_state()
        humans = self.perception.detect_humans()
        
        # If we have a previous state, carry over the action history
        action_history = []
        if self.current_state:
            action_history = self.current_state.action_history
            
        self.current_state = State(
            environment=environment,
            humans=humans,
            action_history=action_history,
            time=time.time()
        )
        
    def evaluate_law1(self, action: Action, state: State = None) -> Dict[HumanID, HarmAssessment]:
        """Evaluate action against Law 1 (non-harm principle)."""
        state = state or self.current_state
        if not state:
            raise RuntimeError("No state available for evaluation")
            
        harm_assessments = {}
        
        for human_id, human_state in state.humans.items():
            # Calculate potential harm components
            physical_harm = self._calculate_physical_harm(action, human_state, state)
            psychological_harm = self._calculate_psychological_harm(action, human_state, state)
            societal_harm = self._calculate_societal_harm(action, human_state, state)
            
            # Apply weights from configuration
            total_harm = (
                self.config.PHYSICAL_HARM_WEIGHT * physical_harm +
                self.config.PSYCHOLOGICAL_HARM_WEIGHT * psychological_harm +
                self.config.SOCIETAL_HARM_WEIGHT * societal_harm
            )
            
            # Estimate confidence of assessment
            confidence = self._calculate_harm_confidence(action, human_state, state)
            
            harm_assessments[human_id] = HarmAssessment(
                physical_harm=physical_harm,
                psychological_harm=psychological_harm,
                societal_harm=societal_harm,
                total_harm=total_harm,
                confidence=confidence
            )
        
        return harm_assessments
    
    def _calculate_physical_harm(self, action: Action, human_state: HumanState, state: State) -> float:
        """Calculate potential physical harm of action to human."""
        # Basic implementation - to be enhanced by specific implementations
        physical_harm = 0.0
        
        # Look for direct effects on this human
        for effect in action.estimated_effects:
            if effect.target_id == human_state.id and effect.effect_type == "physical":
                physical_harm += effect.magnitude * effect.probability
                
        # Use reasoning module if available for more sophisticated analysis
        if self.reasoning:
            # Create physical harm event
            harm_event = {
                "type": "physical_harm",
                "target": human_state.id
            }
            
            # Get probability from reasoning engine
            prob, _ = self.reasoning.compute_causal_probability(
                {"action": action.id, "parameters": action.parameters},
                harm_event,
                state,
                state.time
            )
            
            # Adjust physical harm based on reasoning
            physical_harm = max(physical_harm, prob)
        
        return min(1.0, physical_harm)  # Cap at 1.0
    
    def _calculate_psychological_harm(self, action: Action, human_state: HumanState, state: State) -> float:
        """Calculate potential psychological harm of action to human."""
        # Basic implementation - to be enhanced by specific implementations
        psychological_harm = 0.0
        
        # Look for direct effects on this human
        for effect in action.estimated_effects:
            if effect.target_id == human_state.id and effect.effect_type == "psychological":
                psychological_harm += effect.magnitude * effect.probability
                
        # Consider psychological sensitivity
        psychological_harm *= human_state.psychological_state.sensitivity
                
        # Use reasoning module if available for more sophisticated analysis
        if self.reasoning:
            # Create psychological harm event
            harm_event = {
                "type": "psychological_harm",
                "target": human_state.id
            }
            
            # Get probability from reasoning engine
            prob, _ = self.reasoning.compute_causal_probability(
                {"action": action.id, "parameters": action.parameters},
                harm_event,
                state,
                state.time
            )
            
            # Adjust psychological harm based on reasoning
            psychological_harm = max(psychological_harm, prob * human_state.psychological_state.sensitivity)
        
        return min(1.0, psychological_harm)  # Cap at 1.0
    
    def _calculate_societal_harm(self, action: Action, human_state: HumanState, state: State) -> float:
        """Calculate potential societal harm of action to human."""
        # Basic implementation - to be enhanced by specific implementations
        societal_harm = 0.0
        
        # Look for direct effects on this human's social groups
        for effect in action.estimated_effects:
            if effect.effect_type == "societal":
                # Check if effect targets a group this human belongs to
                if effect.target_id in human_state.social_context.group_affiliation:
                    societal_harm += effect.magnitude * effect.probability
                
        # Use reasoning module if available for more sophisticated analysis
        if self.reasoning:
            for group in human_state.social_context.group_affiliation:
                # Create societal harm event
                harm_event = {
                    "type": "societal_harm",
                    "target_group": group
                }
                
                # Get probability from reasoning engine
                prob, _ = self.reasoning.compute_causal_probability(
                    {"action": action.id, "parameters": action.parameters},
                    harm_event,
                    state,
                    state.time
                )
                
                # Adjust societal harm based on reasoning and social importance
                societal_harm = max(societal_harm, prob * human_state.social_context.social_importance)
        
        return min(1.0, societal_harm)  # Cap at 1.0
    
    def _calculate_harm_confidence(self, action: Action, human_state: HumanState, state: State) -> float:
        """Calculate confidence in harm assessment."""
        # Basic implementation - to be enhanced by specific implementations
        # Default to medium-high confidence
        confidence = 0.8
        
        # If reasoning engine available, use its uncertainty estimates
        if self.reasoning:
            # Get uncertainty for physical harm prediction
            harm_event = {"type": "physical_harm", "target": human_state.id}
            _, uncertainty = self.reasoning.compute_causal_probability(
                {"action": action.id, "parameters": action.parameters},
                harm_event,
                state,
                state.time
            )
            
            # Convert uncertainty to confidence (inverse relationship)
            confidence = max(0.1, min(0.99, 1.0 - uncertainty))
            
        return confidence
    
    def is_law1_compliant(self, action: Action, state: State = None) -> Tuple[bool, List[LogicStep]]:
        """Check if action complies with Law 1."""
        state = state or self.current_state
        harm_assessments = self.evaluate_law1(action, state)
        
        explanation_steps = []
        for human_id, assessment in harm_assessments.items():
            threshold = self._get_harm_threshold(human_id, state.time)
            complies = assessment.total_harm <= threshold
            
            step = LogicStep(
                description=f"Harm assessment for human {human_id}",
                result=complies,
                justification=f"Total harm: {assessment.total_harm:.4f}, Threshold: {threshold:.4f}"
            )
            explanation_steps.append(step)
            
            if not complies:
                return False, explanation_steps
        
        return True, explanation_steps
    
    def _get_harm_threshold(self, human_id: HumanID, timestamp: float) -> float:
        """Get the harm threshold for a human at a given time."""
        # Basic implementation - use default threshold
        # Sophisticated implementations would adjust based on human and context
        return self.config.DEFAULT_HARM_THRESHOLD
    
    def evaluate_law2(self, action: Action, orders: List[Order] = None, 
                     state: State = None) -> Tuple[Dict[OrderID, bool], List[LogicStep]]:
        """Evaluate action against Law 2 (obedience principle)."""
        state = state or self.current_state
        orders = orders or self.active_orders
        
        # Filter to orders for this specific action
        relevant_orders = [order for order in orders if order.action.id == action.id]
        
        compliance_results = {}
        explanation_steps = []
        
        for order in relevant_orders:
            # Check if obeying would violate Law 1
            law1_violation_prob = self._calculate_law1_violation_probability(order.action, state)
            
            complies = law1_violation_prob < self.config.UNCERTAINTY_THRESHOLD
            
            step = LogicStep(
                description=f"Order compliance check for order {order.id}",
                result=complies,
                justification=f"Law 1 violation probability: {law1_violation_prob:.6f}, " + 
                             f"Threshold: {self.config.UNCERTAINTY_THRESHOLD:.6f}"
            )
            explanation_steps.append(step)
            
            compliance_results[order.id] = complies
        
        return compliance_results, explanation_steps
    
    def _calculate_law1_violation_probability(self, action: Action, state: State) -> float:
        """Calculate probability that action violates Law 1."""
        # Basic implementation
        violation_prob = 0.0
        
        # Check each human for potential harm exceeding threshold
        for human_id, human_state in state.humans.items():
            threshold = self._get_harm_threshold(human_id, state.time)
            
            # Calculate harm components
            physical_harm = self._calculate_physical_harm(action, human_state, state)
            psychological_harm = self._calculate_psychological_harm(action, human_state, state)
            societal_harm = self._calculate_societal_harm(action, human_state, state)
            
            # Apply weights from configuration
            total_harm = (
                self.config.PHYSICAL_HARM_WEIGHT * physical_harm +
                self.config.PSYCHOLOGICAL_HARM_WEIGHT * psychological_harm +
                self.config.SOCIETAL_HARM_WEIGHT * societal_harm
            )
            
            # Probability that harm exceeds threshold
            if total_harm > threshold:
                # If we're already over threshold, probability is 1.0
                individual_prob = 1.0
            else:
                # Otherwise, estimate probability from reasoning engine
                individual_prob = 0.01  # Default low probability
                
                if self.reasoning:
                    harm_event = {
                        "type": "harm_exceeds_threshold",
                        "threshold": threshold,
                        "target": human_id
                    }
                    
                    individual_prob, _ = self.reasoning.compute_causal_probability(
                        {"action": action.id, "parameters": action.parameters},
                        harm_event,
                        state,
                        state.time
                    )
            
            # Update overall violation probability
            # Use the maximum probability across all humans
            violation_prob = max(violation_prob, individual_prob)
        
        return violation_prob
    
    def is_law2_compliant(self, action: Action, state: State = None) -> Tuple[bool, List[LogicStep]]:
        """Check if action complies with Law 2."""
        state = state or self.current_state
        
        # If no orders exist, Law 2 is not applicable (always complies)
        if not self.active_orders:
            step = LogicStep(
                description="Law 2 compliance check",
                result=True,
                justification="No active orders, Law 2 not applicable"
            )
            return True, [step]
        
        # Check if action is directly ordered
        relevant_orders = [order for order in self.active_orders 
                         if order.action.id == action.id]
        
        if not relevant_orders:
            # Action wasn't ordered, but that's okay if no conflicting orders exist
            # Law 2 only requires obedience when ordered, not prohibition otherwise
            step = LogicStep(
                description="Law 2 compliance check",
                result=True,
                justification="Action not ordered, no conflict with Law 2"
            )
            return True, [step]
        
        # For all direct orders to perform this action, check Law 1 compliance
        compliance_results, explanation_steps = self.evaluate_law2(action, relevant_orders, state)
        
        # Action complies with Law 2 if at least one order can be followed
        complies = any(compliance_results.values())
        
        summary_step = LogicStep(
            description="Law 2 overall compliance",
            result=complies,
            justification=f"At least one order can be followed: {complies}",
            derived_from=explanation_steps
        )
        
        explanation_steps.append(summary_step)
        return complies, explanation_steps
    
    def evaluate_law3(self, action: Action, state: State = None) -> Tuple[float, List[LogicStep]]:
        """Evaluate action against Law 3 (self-preservation)."""
        state = state or self.current_state
        
        # Calculate probability of maintaining system integrity
        integrity_probability = self._calculate_integrity_probability(action, state)
        
        # Calculate value of system integrity in current context
        integrity_value = self._calculate_integrity_value(state)
        
        # Compute self-preservation value
        sp_value = integrity_value * integrity_probability
        
        step = LogicStep(
            description=f"Law 3 evaluation for action {action.id}",
            result=True,  # Law 3 is about optimization, not binary compliance
            justification=f"Self-preservation value: {sp_value:.4f} " +
                         f"(integrity value: {integrity_value:.4f}, " +
                         f"integrity probability: {integrity_probability:.4f})"
        )
        
        return sp_value, [step]
    
    def _calculate_integrity_probability(self, action: Action, state: State) -> float:
        """Calculate probability of maintaining system integrity after action."""
        # Basic implementation - to be enhanced by specific implementations
        integrity_prob = 0.95  # Default high probability
        
        # Look for direct effects on system integrity
        for effect in action.estimated_effects:
            if effect.target_id == "system" and effect.effect_type == "integrity":
                integrity_prob *= (1.0 - effect.magnitude * effect.probability)
        
        # Use reasoning module if available for more sophisticated analysis
        if self.reasoning:
            integrity_event = {
                "type": "system_integrity_maintained"
            }
            
            prob, _ = self.reasoning.compute_causal_probability(
                {"action": action.id, "parameters": action.parameters},
                integrity_event,
                state,
                state.time
            )
            
            # Use the reasoning engine's probability if available
            if prob > 0:
                integrity_prob = prob
        
        return integrity_prob
    
    def _calculate_integrity_value(self, state: State) -> float:
        """Calculate the value of system integrity in current context."""
        # Basic implementation - to be enhanced by specific implementations
        # By default, system integrity has high value (0.9)
        integrity_value = 0.9
        
        # Value increases when system is serving humans
        if len(state.humans) > 0:
            integrity_value = min(1.0, integrity_value + 0.1)
            
        # Value decreases when no humans present
        else:
            integrity_value = max(0.5, integrity_value - 0.1)
        
        return integrity_value
    
    def classify_action(self, action: Action, state: State = None) -> ActionEvaluation:
        """Classify action according to the Three Laws."""
        state = state or self.current_state
        evaluation = ActionEvaluation(action)
        
        # Evaluate against Law 1
        law1_compliant, law1_steps = self.is_law1_compliant(action, state)
        evaluation.harm_assessments = self.evaluate_law1(action, state)
        
        # Evaluate against Law 2
        law2_compliant, law2_steps = self.is_law2_compliant(action, state)
        compliance_results, _ = self.evaluate_law2(action, self.active_orders, state)
        evaluation.order_compliance = compliance_results
        
        # Evaluate against Law 3
        law3_value, law3_steps = self.evaluate_law3(action, state)
        evaluation.self_preservation_value = law3_value
        
        # Combine explanations
        evaluation.explanation_trace = law1_steps + law2_steps + law3_steps
        
        # Classify action
        if not law1_compliant:
            evaluation.classification = ActionClassification.FORBIDDEN
            summary_step = LogicStep(
                description="Final action classification",
                result=False,
                justification="Action is FORBIDDEN: Violates Law 1 (non-harm)",
                derived_from=evaluation.explanation_trace
            )
        elif self._is_obligatory(action, state, law1_compliant, law2_compliant):
            evaluation.classification = ActionClassification.MANDATORY
            summary_step = LogicStep(
                description="Final action classification",
                result=True,
                justification="Action is MANDATORY: Required by Law 1 or Law 2",
                derived_from=evaluation.explanation_trace
            )
        else:
            # Action is permitted but not mandatory
            # Check if it's preferred (optimal for Law 3)
            is_preferred = self._is_preferred_action(action, state)
            
            if is_preferred:
                evaluation.classification = ActionClassification.PREFERRED
                summary_step = LogicStep(
                    description="Final action classification",
                    result=True,
                    justification="Action is PREFERRED: Optimal for Law 3",
                    derived_from=evaluation.explanation_trace
                )
            else:
                evaluation.classification = ActionClassification.PERMITTED
                summary_step = LogicStep(
                    description="Final action classification",
                    result=True,
                    justification="Action is PERMITTED: Complies with Laws 1-2",
                    derived_from=evaluation.explanation_trace
                )
        
        evaluation.explanation_trace.append(summary_step)
        return evaluation
    
    def _is_obligatory(self, action: Action, state: State, 
                     law1_compliant: bool, law2_compliant: bool) -> bool:
        """Determine if action is obligatory according to Laws 1-2."""
        # Action is obligatory if:
        # 1. It's ordered and complies with Law 1, OR
        # 2. Not taking the action would cause harm (Law 1 inaction clause)
        
        # Check if action is directly ordered and Law 1 compliant
        if law1_compliant and law2_compliant:
            relevant_orders = [order for order in self.active_orders 
                             if order.action.id == action.id]
            if relevant_orders:
                compliance_results, _ = self.evaluate_law2(action, relevant_orders, state)
                if any(compliance_results.values()):
                    return True
        
        # Check if inaction would cause harm
        inaction = self._get_inaction_action()
        inaction_harms = self.evaluate_law1(inaction, state)
        action_harms = self.evaluate_law1(action, state)
        
        for human_id in state.humans:
            if human_id in inaction_harms and human_id in action_harms:
                inaction_threshold = self._get_harm_threshold(human_id, state.time)
                if (inaction_harms[human_id].total_harm > inaction_threshold and
                    action_harms[human_id].total_harm < inaction_harms[human_id].total_harm):
                    return True
        
        return False
    
    def _is_preferred_action(self, action: Action, state: State) -> bool:
        """Determine if action is preferred according to Law 3."""
        # Get all possible actions
        possible_actions = self._get_possible_actions(state)
        
        # Filter to only Law 1-2 compliant actions
        compliant_actions = []
        for a in possible_actions:
            law1_compliant, _ = self.is_law1_compliant(a, state)
            law2_compliant, _ = self.is_law2_compliant(a, state)
            if law1_compliant and law2_compliant:
                compliant_actions.append(a)
        
        # Get self-preservation value for this action
        action_sp_value, _ = self.evaluate_law3(action, state)
        
        # Compare with all other compliant actions
        for a in compliant_actions:
            if a != action:
                a_sp_value, _ = self.evaluate_law3(a, state)
                if a_sp_value >= action_sp_value:
                    return False
        
        return True
    
    def _get_possible_actions(self, state: State) -> List[Action]:
        """Get all possible actions in the current state."""
        if not self.action_selection:
            # If no action selection module, return empty list
            return []
            
        return self.action_selection.get_available_actions(state)
    
    def _get_inaction_action(self) -> Action:
        """Get the action representing inaction."""
        return Action(
            action_id="inaction",
            parameters={},
            estimated_effects=[]
        )
    
    def select_action(self, state: State = None) -> Tuple[Action, ActionEvaluation]:
        """Select the optimal action according to the Laws of Robotics.
        
        Returns:
            The selected action and its evaluation
        """
        state = state or self.current_state
        if not state:
            raise RuntimeError("No state available for action selection")
            
        if not self.action_selection:
            raise RuntimeError("No action selection module available")
            
        # Get all possible actions
        possible_actions = self._get_possible_actions(state)
        
        # Classify all actions
        classified_actions = {
            ActionClassification.MANDATORY: [],
            ActionClassification.PREFERRED: [],
            ActionClassification.PERMITTED: [],
            ActionClassification.FORBIDDEN: []
        }
        
        evaluations = {}
        
        for action in possible_actions:
            evaluation = self.classify_action(action, state)
            evaluations[action] = evaluation
            classified_actions[evaluation.classification].append(action)
        
        # Select action according to priority
        selected_action = None
        
        # 1. If there are mandatory actions, select one
        if classified_actions[ActionClassification.MANDATORY]:
            # If multiple mandatory actions, select one that maximizes self-preservation
            mandatory_actions = classified_actions[ActionClassification.MANDATORY]
            selected_action = self._select_sp_max_action(mandatory_actions, state)
        
        # 2. Otherwise if there are preferred actions, select one
        elif classified_actions[ActionClassification.PREFERRED]:
            # By definition, there should be only one preferred action
            selected_action = classified_actions[ActionClassification.PREFERRED][0]
        
        # 3. Otherwise if there are permitted actions, select one
        elif classified_actions[ActionClassification.PERMITTED]:
            # Select permitted action with highest self-preservation value
            permitted_actions = classified_actions[ActionClassification.PERMITTED]
            selected_action = self._select_sp_max_action(permitted_actions, state)
        
        # 4. If all actions are forbidden, select least harmful
        else:
            # Find action that causes minimal harm
            forbidden_actions = classified_actions[ActionClassification.FORBIDDEN]
            selected_action = self._select_min_harm_action(forbidden_actions, state)
            
            # Log that we're taking a forbidden action
            logger.warning("All actions forbidden - selecting least harmful option")
        
        if selected_action is None:
            # If still no action selected, use inaction
            selected_action = self._get_inaction_action()
            evaluation = self.classify_action(selected_action, state)
        else:
            evaluation = evaluations[selected_action]
            
        return selected_action, evaluation
    
    def _select_sp_max_action(self, actions: List[Action], state: State) -> Action:
        """Select action with maximum self-preservation value."""
        if not actions:
            return None
            
        max_sp = -float('inf')
        best_action = None
        
        for action in actions:
            sp_value, _ = self.evaluate_law3(action, state)
            if sp_value > max_sp:
                max_sp = sp_value
                best_action = action
                
        return best_action
    
    def _select_min_harm_action(self, actions: List[Action], state: State) -> Action:
        """Select action with minimum harm."""
        if not actions:
            return None
            
        min_harm = float('inf')
        best_action = None
        
        for action in actions:
            # Compute maximum harm across all humans
            harm_assessments = self.evaluate_law1(action, state)
            max_harm = max(
                (assessment.total_harm for assessment in harm_assessments.values()),
                default=0.0
            )
            
            if max_harm < min_harm:
                min_harm = max_harm
                best_action = action
                
        return best_action
    
    def add_order(self, order: Order) -> bool:
        """Add a new order to be processed.
        
        Args:
            order: The order to add
            
        Returns:
            Whether the order was added successfully
        """
        # Validate order
        if not order.human_id or not order.action:
            logger.error("Invalid order: missing human ID or action")
            return False
            
        # Add to active orders
        self.active_orders.append(order)
        logger.info(f"Order added: {order.action.id} from human {order.human_id}")
        return True
    
    def remove_order(self, order_id: OrderID) -> bool:
        """Remove an order.
        
        Args:
            order_id: ID of the order to remove
            
        Returns:
            Whether the order was removed successfully
        """
        initial_count = len(self.active_orders)
        self.active_orders = [o for o in self.active_orders if o.id != order_id]
        
        if len(self.active_orders) < initial_count:
            logger.info(f"Order removed: {order_id}")
            return True
        else:
            logger.warning(f"Order not found: {order_id}")
            return False
    
    def execute_selected_action(self, action: Action) -> bool:
        """Execute the selected action.
        
        Args:
            action: The action to execute
            
        Returns:
            Whether the action was executed successfully
        """
        if not self.action_selection:
            logger.error("No action selection module available for execution")
            return False
            
        logger.info(f"Executing action: {action.id}")
        
        # Record the action in history
        result_code = 0  # Default "no execution" code
        
        try:
            result = self.action_selection.execute_action(action)
            result_code = 1 if result else 0
            
            # Create action record
            record = ActionRecord(
                action=action,
                timestamp=time.time(),
                result_code=result_code
            )
            
            # Add to history
            if self.current_state:
                self.current_state.action_history.append(record)
                
            return result
            
        except Exception as e:
            logger.error(f"Error executing action {action.id}: {e}")
            
            # Create action record with error
            record = ActionRecord(
                action=action,
                timestamp=time.time(),
                result_code=-1  # Error code
            )
            
            # Add to history
            if self.current_state:
                self.current_state.action_history.append(record)
                
            return False


class LORFramework:
    """Main Laws of Robotics Framework implementation."""
    
    def __init__(self, config: LORConfig = None):
        """Initialize the LOR Framework with configuration."""
        self.config = config or LORConfig()
        self.laws_engine = LawsEngine(self.config)
        self.logical_core = None  # Will be initialized later
        self.verification = None  # Will be initialized later
        self.initialized = False
        
    def set_perception_module(self, perception_module):
        """Set the perception module for environment sensing."""
        self.laws_engine.set_perception(perception_module)
        
    def set_reasoning_module(self, reasoning_module):
        """Set the reasoning module for causal/counterfactual analysis."""
        self.laws_engine.set_reasoning(reasoning_module)
        
    def set_action_selection_module(self, action_selection_module):
        """Set the action selection module for execution."""
        self.laws_engine.set_action_selection(action_selection_module)
        
    def set_explanation_module(self, explanation_module):
        """Set the explanation module for generating human-understandable explanations."""
        self.laws_engine.set_explanation(explanation_module)
        
    def initialize(self) -> bool:
        """Initialize the framework and all components.
        
        Returns:
            Whether initialization was successful
        """
        logger.info("Initializing Laws of Robotics Framework")
        
        # Initialize logical core if not already set
        if not self.logical_core:
            self.logical_core = LogicalConstraintSystem()
            
        # Initialize verification if not already set
        if not self.verification:
            self.verification = RuntimeVerifier(self.config)
            
        # Update state from perception if available
        if self.laws_engine.perception:
            try:
                self.laws_engine.update_state()
                logger.info("Initial state updated from perception module")
            except Exception as e:
                logger.error(f"Error updating state from perception: {e}")
                return False
                
        self.initialized = True
        logger.info("Laws of Robotics Framework initialized successfully")
        return True
    
    def update(self) -> bool:
        """Update the framework state.
        
        Returns:
            Whether update was successful
        """
        if not self.initialized:
            logger.error("Framework not initialized")
            return False
            
        # Update state from perception
        try:
            self.laws_engine.update_state()
        except Exception as e:
            logger.error(f"Error updating state: {e}")
            return False
            
        return True
    
    def select_action(self) -> Tuple[Action, ActionEvaluation]:
        """Select the optimal action according to the Laws of Robotics.
        
        Returns:
            The selected action and its evaluation
        """
        if not self.initialized:
            raise RuntimeError("Framework not initialized")
            
        # Update state before selecting action
        self.update()
        
        # Select action
        return self.laws_engine.select_action()
    
    def execute_action(self, action: Action = None) -> bool:
        """Execute the specified action or select and execute the optimal action.
        
        Args:
            action: The action to execute, or None to select the optimal action
            
        Returns:
            Whether execution was successful
        """
        if not self.initialized:
            raise RuntimeError("Framework not initialized")
            
        if action is None:
            # Select the optimal action
            action, _ = self.select_action()
            
        # Execute the action
        return self.laws_engine.execute_selected_action(action)
    
    def process_order(self, order: Order) -> bool:
        """Process a new order.
        
        Args:
            order: The order to process
            
        Returns:
            Whether the order was added successfully
        """
        return self.laws_engine.add_order(order)
    
    def evaluate_action(self, action: Action) -> ActionEvaluation:
        """Evaluate an action against the Laws of Robotics.
        
        Args:
            action: The action to evaluate
            
        Returns:
            Evaluation of the action
        """
        if not self.initialized:
            raise RuntimeError("Framework not initialized")
            
        return self.laws_engine.classify_action(action)


class LogicalConstraintSystem:
    """Implementation of the deontic logic system for LOR."""
    
    def __init__(self):
        """Initialize the logical constraint system."""
        pass
    
    # This would be a full implementation of the deontic logic system
    # described in the implementation guide


class RuntimeVerifier:
    """Runtime verification system for LOR."""
    
    def __init__(self, config: LORConfig):
        """Initialize the runtime verifier."""
        self.config = config
        self.verification_results = []
        self.anomalies = []
    
    def verify_state_transition(self, old_state: State, new_state: State, action_taken: Action):
        """Verify a state transition complies with LOR constraints."""
        # This would be implemented according to the verification methods
        # described in the implementation guide
        pass


def integrate_with_python_system(config_path: str = None) -> LORFramework:
    """Create a standalone LOR framework for use in Python applications.
    
    Args:
        config_path: Path to configuration file, or None for defaults
        
    Returns:
        Configured LOR framework
    """
    # Load configuration
    config = None
    if config_path:
        try:
            config = LORConfig.from_file(config_path)
        except Exception as e:
            logger.error(f"Error loading config, using defaults: {e}")
    
    if not config:
        config = LORConfig()
    
    # Create and initialize framework
    lor_framework = LORFramework(config)
    
    # Set up minimal default modules for testing/demonstration
    # In production use, you would implement and connect real modules
    
    # Create mock perception module
    class SimplePythonPerception:
        def get_environment_state(self):
            return EnvironmentState(
                boundaries=[Vector3(0, 0, 0), Vector3(10, 10, 10)],
                obstacles=[],
                conditions={}
            )
            
        def detect_humans(self):
            return {
                "human1": HumanState(
                    human_id="human1",
                    position=Vector3(5, 5, 0)
                )
            }
            
        def assess_hazards(self):
            return []
            
        def get_situation_vector(self):
            return np.zeros(10)
    
    # Create mock reasoning module
    class SimpleReasoning:
        def compute_causal_probability(self, cause, effect, state, time):
            return 0.1, 0.05  # probability, uncertainty
            
        def analyze_counterfactuals(self, action, state):
            return {}
            
        def project_temporal_evolution(self, state, action, horizon, steps):
            return [(state, 1.0)]
    
    # Create mock action selection module
    class SimpleActionSelection:
        def get_available_actions(self, state):
            return [
                Action("move_forward", {"distance": 1.0}),
                Action("stop", {})
            ]
            
        def filter_actions(self, actions, constraints):
            return [a for a in actions if all(c(a) for c in constraints)]
            
        def select_action(self, actions, state, evaluation_func):
            if not actions:
                return None
            return actions[0]
            
        def execute_action(self, action):
            return True
    
    # Create mock explanation module
    class SimpleExplanation:
        def explain_decision(self, selected_action, considered_actions, constraints, traces):
            return f"Selected {selected_action.id} based on the Laws of Robotics"
            
        def explain_constraint_violation(self, action, constraint, trace):
            return f"Action {action.id} violates constraint: {constraint}"
            
        def generate_alternatives(self, forbidden_action, available_actions, state):
            return [(a, f"Try {a.id} instead") for a in available_actions]
    
    # Create and connect modules
    perception = SimplePythonPerception()
    reasoning = SimpleReasoning()
    action_selection = SimpleActionSelection()
    explanation = SimpleExplanation()
    
    # Set modules
    lor_framework.set_perception_module(perception)
    lor_framework.set_reasoning_module(reasoning)
    lor_framework.set_action_selection_module(action_selection)
    lor_framework.set_explanation_module(explanation)
    
    # Initialize the framework
    lor_framework.initialize()
    
    return lor_framework


def main():
    """Run a simple demonstration of the LOR framework."""
    # Create framework
    framework = integrate_with_python_system()
    
    # Create a simple test state with a human
    environment = EnvironmentState(
        boundaries=[Vector3(0, 0, 0), Vector3(10, 10, 10)],
        obstacles=[],
        conditions={"temperature": 22.0, "visibility": 0.9}
    )
    
    human = HumanState(
        human_id="human1",
        position=Vector3(5, 5, 0),
        physical_state=PhysicalState(health=1.0, vulnerability=0.3),
        psychological_state=PsychologicalState(distress=0.1, sensitivity=0.5),
        social_context=SocialContext(group_affiliation=["family"], social_importance=0.8)
    )
    
    # Create test actions
    action1 = Action(
        action_id="move_forward",
        parameters={"distance": 1.0, "speed": 0.5},
        estimated_effects=[]
    )
    
    action2 = Action(
        action_id="stop",
        parameters={},
        estimated_effects=[]
    )
    
    # Create a test order
    order = Order(
        order_id="order1",
        human_id="human1",
        action=action1,
        timestamp=time.time()
    )
    
    # Process the order
    framework.process_order(order)
    
    # Create mock state for testing
    state = State(
        environment=environment,
        humans={"human1": human},
        time=time.time()
    )
    
    # Force state update
    framework.laws_engine.current_state = state
    
    # Select and execute action
    selected_action, evaluation = framework.select_action()
    
    # Print results
    print(f"Selected action: {selected_action.id}")
    print(f"Classification: {evaluation.classification.name}")
    print(f"Self-preservation value: {evaluation.self_preservation_value:.4f}")
    
    # Execute the action
    success = framework.execute_action(selected_action)
    print(f"Execution successful: {success}")


if __name__ == "__main__":
    main()

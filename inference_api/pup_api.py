"""
API endpoints for the Probabilistic Uncertainty Principle (PUP) Framework.
"""

import logging
import traceback
import json
from typing import Dict, Any, Optional, List, Tuple
from flask import Blueprint, jsonify, request
from inference_api.auth import authenticate, authorize
from inference_api.utils.error_handling import APIError, api_error_handler

logger = logging.getLogger(__name__)

try:
    # Attempt to import PUP components
    from head_1.frameworks.probabalistic_uncertainty_principle.pup.belief_state import BeliefState
    from head_1.frameworks.probabalistic_uncertainty_principle.pup.uncertainty_propagator import UncertaintyPropagator
    from head_1.frameworks.probabalistic_uncertainty_principle.pup.confidence_executor import ConfidenceExecutor
    HAS_PUP = True
except ImportError:
    logger.warning("PUP Framework not found. Import failed.")
    HAS_PUP = False

def create_pup_api(config) -> Optional[Blueprint]:
    """
    Create a Blueprint for the PUP API.
    
    Args:
        config: API configuration
        
    Returns:
        Flask Blueprint or None if framework unavailable
    """
    if not HAS_PUP:
        # For now, create a mock implementation
        logger.info("Creating mock PUP API as framework not available")
        return create_mock_pup_api()
    
    # Create Blueprint
    pup_bp = Blueprint('pup', __name__)
    
    # Create global instances
    propagator = UncertaintyPropagator()
    executor = ConfidenceExecutor()
    
    @pup_bp.route('/belief', methods=['POST'])
    @authenticate
    @api_error_handler
    def create_belief():
        """Create a new belief state."""
        try:
            data = request.get_json()
            
            # Validate required fields
            if "mean" not in data:
                raise APIError("Missing required field: mean", 400)
            
            # Create belief state
            belief = BeliefState(
                mean=float(data["mean"]),
                variance=float(data.get("variance", 0.1)),
                epistemic=data.get("epistemic", True)
            )
            
            # Return serialized belief
            return jsonify({
                "status": "ok",
                "belief": belief.to_dict()
            })
            
        except APIError:
            raise
        except Exception as e:
            logger.error(f"Error creating belief: {e}")
            raise APIError(f"Failed to create belief: {str(e)}", 500)
    
    @pup_bp.route('/propagate', methods=['POST'])
    @authenticate
    @api_error_handler
    def propagate_belief():
        """Propagate uncertainty through a transformation."""
        try:
            data = request.get_json()
            
            # Validate required fields
            if "belief" not in data or "transformation" not in data:
                raise APIError("Missing required fields: belief, transformation", 400)
            
            # Create belief from data
            belief_data = data["belief"]
            belief = BeliefState(
                mean=float(belief_data.get("mean", 0.0)),
                variance=float(belief_data.get("variance", 0.1))
            )
            
            # Get transformation type
            transform_type = data["transformation"].get("type", "square")
            
            # Apply appropriate transformation
            if transform_type == "square":
                transformed = propagator.propagate(belief, lambda x: x**2)
            elif transform_type == "log":
                transformed = propagator.propagate(belief, lambda x: math.log(x) if x > 0 else 0)
            elif transform_type == "exp":
                transformed = propagator.propagate(belief, lambda x: math.exp(x))
            else:
                raise APIError(f"Unsupported transformation type: {transform_type}", 400)
            
            # Return result
            return jsonify({
                "status": "ok",
                "original_belief": belief.to_dict(),
                "transformed_belief": transformed.to_dict()
            })
            
        except APIError:
            raise
        except Exception as e:
            logger.error(f"Error propagating belief: {e}")
            raise APIError(f"Failed to propagate belief: {str(e)}", 500)
    
    @pup_bp.route('/execute', methods=['POST'])
    @authenticate
    @api_error_handler
    def execute_with_confidence():
        """Execute an action if confidence exceeds threshold."""
        try:
            data = request.get_json()
            
            # Validate required fields
            if "belief" not in data or "threshold" not in data:
                raise APIError("Missing required fields: belief, threshold", 400)
            
            # Create belief from data
            belief_data = data["belief"]
            belief = BeliefState(
                mean=float(belief_data.get("mean", 0.0)),
                variance=float(belief_data.get("variance", 0.1))
            )
            
            # Get threshold and prepare executor
            threshold = float(data["threshold"])
            custom_executor = ConfidenceExecutor(threshold=threshold)
            
            # Execute with confidence check
            result = custom_executor.execute(
                belief,
                lambda x: {"action": "executed", "value": x},
                fallback_fn=lambda x: {"action": "deferred", "confidence": belief.confidence()}
            )
            
            # Return result
            return jsonify({
                "status": "ok",
                "belief": belief.to_dict(),
                "threshold": threshold,
                "result": result,
                "confidence": belief.confidence(),
                "execution_stats": custom_executor.get_execution_stats()
            })
            
        except APIError:
            raise
        except Exception as e:
            logger.error(f"Error executing with confidence: {e}")
            raise APIError(f"Failed to execute with confidence: {str(e)}", 500)
    
    return pup_bp

def create_mock_pup_api() -> Blueprint:
    """
    Create a mock Blueprint for the PUP API.
    
    Returns:
        Flask Blueprint with mock implementations
    """
    pup_bp = Blueprint('pup', __name__)
    
    @pup_bp.route('/belief', methods=['POST'])
    @authenticate
    @api_error_handler
    def create_belief():
        """Create a new belief state (mock implementation)."""
        try:
            data = request.get_json()
            
            # Validate required fields
            if "mean" not in data:
                raise APIError("Missing required field: mean", 400)
            
            mean = float(data["mean"])
            variance = float(data.get("variance", 0.1))
            
            # Create mock belief
            belief = {
                "mean": mean,
                "variance": variance,
                "confidence": 1.0 - min(1.0, variance / (abs(mean) + 0.1))
            }
            
            return jsonify({
                "status": "ok",
                "belief": belief,
                "note": "This is a mock implementation"
            })
            
        except APIError:
            raise
        except Exception as e:
            logger.error(f"Error in mock belief creation: {e}")
            raise APIError(f"Failed to create belief: {str(e)}", 500)
    
    return pup_bp
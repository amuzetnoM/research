"""
API for the Laws of Robotics framework.

This module provides a REST API layer for the Laws of Robotics framework,
allowing external systems to interact with it.
"""

import json
import time
import logging
import uuid
from typing import Dict, List, Any, Optional, Union
from dataclasses import asdict
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from .lor_core import (
    LORFramework, LORConfig, Action, Order, State, Vector3, HumanState,
    PhysicalState, PsychologicalState, SocialContext, Effect,
    EnvironmentState, ActionClassification, integrate_with_python_system
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lor_api")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Global framework instance
global_framework: Optional[LORFramework] = None

# API version
API_VERSION = "1.0.0"

# Helper functions
def serialize_object(obj):
    """Serialize objects to JSON."""
    if hasattr(obj, "serialize"):
        return obj.serialize()
    elif hasattr(obj, "__dict__"):
        return obj.__dict__
    else:
        return str(obj)

def deserialize_action(action_data: Dict) -> Action:
    """Deserialize an Action from JSON data."""
    estimated_effects = []
    if "estimated_effects" in action_data:
        for effect_data in action_data["estimated_effects"]:
            estimated_effects.append(Effect(
                target_id=effect_data.get("target_id", ""),
                effect_type=effect_data.get("effect_type", ""),
                magnitude=float(effect_data.get("magnitude", 0.0)),
                probability=float(effect_data.get("probability", 0.0))
            ))
    
    return Action(
        action_id=action_data.get("id", ""),
        parameters=action_data.get("parameters", {}),
        estimated_effects=estimated_effects
    )

def deserialize_state(state_data: Dict) -> State:
    """Deserialize a State from JSON data."""
    environment_data = state_data.get("environment", {})
    boundaries = []
    for boundary in environment_data.get("boundaries", []):
        boundaries.append(Vector3(
            x=float(boundary.get("x", 0.0)),
            y=float(boundary.get("y", 0.0)),
            z=float(boundary.get("z", 0.0))
        ))
    
    environment = EnvironmentState(
        boundaries=boundaries,
        obstacles=environment_data.get("obstacles", []),
        conditions=environment_data.get("conditions", {})
    )
    
    humans = {}
    for human_id, human_data in state_data.get("humans", {}).items():
        position_data = human_data.get("position", {})
        position = Vector3(
            x=float(position_data.get("x", 0.0)),
            y=float(position_data.get("y", 0.0)),
            z=float(position_data.get("z", 0.0))
        )
        
        physical_data = human_data.get("physical_state", {})
        physical_state = PhysicalState(
            health=float(physical_data.get("health", 1.0)),
            vulnerability=float(physical_data.get("vulnerability", 0.5))
        )
        
        psychological_data = human_data.get("psychological_state", {})
        psychological_state = PsychologicalState(
            distress=float(psychological_data.get("distress", 0.0)),
            sensitivity=float(psychological_data.get("sensitivity", 0.5))
        )
        
        social_data = human_data.get("social_context", {})
        social_context = SocialContext(
            group_affiliation=social_data.get("group_affiliation", []),
            social_importance=float(social_data.get("social_importance", 0.5))
        )
        
        humans[human_id] = HumanState(
            human_id=human_id,
            position=position,
            physical_state=physical_state,
            psychological_state=psychological_state,
            social_context=social_context
        )
    
    return State(
        environment=environment,
        humans=humans,
        action_history=[],  # We don't deserialize action history from API
        time=state_data.get("time", time.time())
    )

# API routes
@app.route("/api/v1/info", methods=["GET"])
def get_info() -> Response:
    """Get basic information about the API."""
    return jsonify({
        "name": "Laws of Robotics API",
        "version": API_VERSION,
        "status": "active" if global_framework and global_framework.initialized else "inactive",
        "timestamp": time.time()
    })

@app.route("/api/v1/initialize", methods=["POST"])
def initialize_framework() -> Response:
    """Initialize the Laws of Robotics framework."""
    global global_framework
    
    data = request.json or {}
    config_path = data.get("config_path")
    
    try:
        global_framework = integrate_with_python_system(config_path)
        return jsonify({
            "success": True,
            "message": "Framework initialized successfully"
        })
    except Exception as e:
        logger.error(f"Error initializing framework: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/v1/actions/evaluate", methods=["POST"])
def evaluate_action() -> Response:
    """Evaluate an action against the Laws of Robotics."""
    if not global_framework or not global_framework.initialized:
        return jsonify({
            "success": False,
            "error": "Framework not initialized"
        }), 400
    
    data = request.json
    if not data or "action" not in data:
        return jsonify({
            "success": False,
            "error": "Action data required"
        }), 400
    
    try:
        action = deserialize_action(data["action"])
        evaluation = global_framework.evaluate_action(action)
        
        return jsonify({
            "success": True,
            "evaluation": evaluation.serialize()
        })
    except Exception as e:
        logger.error(f"Error evaluating action: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/v1/actions/select", methods=["POST"])
def select_action() -> Response:
    """Select the optimal action according to the Laws of Robotics."""
    if not global_framework or not global_framework.initialized:
        return jsonify({
            "success": False,
            "error": "Framework not initialized"
        }), 400
    
    try:
        # Custom state can be provided optionally
        data = request.json or {}
        if "state" in data:
            # Use provided state instead of current state
            state = deserialize_state(data["state"])
            global_framework.laws_engine.current_state = state
        
        action, evaluation = global_framework.select_action()
        
        return jsonify({
            "success": True,
            "action": action.serialize(),
            "evaluation": evaluation.serialize()
        })
    except Exception as e:
        logger.error(f"Error selecting action: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/v1/actions/execute", methods=["POST"])
def execute_action() -> Response:
    """Execute a specified action or select and execute the optimal action."""
    if not global_framework or not global_framework.initialized:
        return jsonify({
            "success": False,
            "error": "Framework not initialized"
        }), 400
    
    data = request.json or {}
    
    try:
        if "action" in data:
            # Execute specified action
            action = deserialize_action(data["action"])
            success = global_framework.execute_action(action)
        else:
            # Select and execute optimal action
            action, evaluation = global_framework.select_action()
            success = global_framework.execute_action(action)
            
        return jsonify({
            "success": success,
            "action": action.serialize() if success else None,
            "message": "Action executed successfully" if success else "Failed to execute action"
        })
    except Exception as e:
        logger.error(f"Error executing action: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/v1/orders", methods=["POST"])
def process_order() -> Response:
    """Process a new order."""
    if not global_framework or not global_framework.initialized:
        return jsonify({
            "success": False,
            "error": "Framework not initialized"
        }), 400
    
    data = request.json
    if not data or "order" not in data:
        return jsonify({
            "success": False,
            "error": "Order data required"
        }), 400
    
    try:
        order_data = data["order"]
        action = deserialize_action(order_data.get("action", {}))
        
        order = Order(
            order_id=order_data.get("id", str(uuid.uuid4())),
            human_id=order_data.get("human_id", ""),
            action=action,
            timestamp=order_data.get("timestamp", time.time()),
            context=order_data.get("context", {})
        )
        
        success = global_framework.process_order(order)
        
        return jsonify({
            "success": success,
            "order_id": order.id,
            "message": "Order processed successfully" if success else "Failed to process order"
        })
    except Exception as e:
        logger.error(f"Error processing order: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/v1/orders/<order_id>", methods=["DELETE"])
def remove_order(order_id: str) -> Response:
    """Remove an order."""
    if not global_framework or not global_framework.initialized:
        return jsonify({
            "success": False,
            "error": "Framework not initialized"
        }), 400
    
    try:
        success = global_framework.laws_engine.remove_order(order_id)
        
        return jsonify({
            "success": success,
            "message": f"Order {order_id} removed successfully" if success else f"Order {order_id} not found"
        })
    except Exception as e:
        logger.error(f"Error removing order: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/v1/state", methods=["GET"])
def get_state() -> Response:
    """Get the current state."""
    if not global_framework or not global_framework.initialized:
        return jsonify({
            "success": False,
            "error": "Framework not initialized"
        }), 400
    
    try:
        state = global_framework.laws_engine.current_state
        if not state:
            return jsonify({
                "success": False,
                "error": "No state available"
            }), 404
            
        return jsonify({
            "success": True,
            "state": state.serialize()
        })
    except Exception as e:
        logger.error(f"Error getting state: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/v1/state", methods=["PUT"])
def update_state() -> Response:
    """Update the current state."""
    if not global_framework or not global_framework.initialized:
        return jsonify({
            "success": False,
            "error": "Framework not initialized"
        }), 400
    
    data = request.json
    if not data or "state" not in data:
        return jsonify({
            "success": False,
            "error": "State data required"
        }), 400
    
    try:
        state = deserialize_state(data["state"])
        global_framework.laws_engine.current_state = state
        
        return jsonify({
            "success": True,
            "message": "State updated successfully"
        })
    except Exception as e:
        logger.error(f"Error updating state: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "Method not allowed"
    }), 405

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

# Main entry point
def run_api(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """Run the LOR API server."""
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    # Initialize the framework
    global_framework = integrate_with_python_system()
    
    # Run the API server
    run_api(debug=True)

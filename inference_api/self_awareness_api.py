"""
API endpoints for the Self-Awareness Framework.
"""

import logging
import traceback
from typing import Dict, Any, Optional
from flask import Blueprint, jsonify, request
from inference_api.auth import authenticate, authorize
from inference_api.utils.error_handling import APIError, api_error_handler

logger = logging.getLogger(__name__)

try:
    from head_1.frameworks.self_awareness.self_awareness_client import SelfAwarenessClient
    HAS_SELF_AWARENESS = True
except ImportError:
    logger.warning("Self-Awareness Framework not found. Import failed.")
    HAS_SELF_AWARENESS = False

def create_self_awareness_api(config) -> Optional[Blueprint]:
    """
    Create a Blueprint for the Self-Awareness API.
    
    Args:
        config: API configuration
        
    Returns:
        Flask Blueprint or None if framework unavailable
    """
    if not HAS_SELF_AWARENESS:
        return None
    
    # Create Blueprint
    self_awareness_bp = Blueprint('self_awareness', __name__)
    
    # Initialize client
    client = None
    try:
        client = SelfAwarenessClient(
            host=config.SELF_AWARENESS_HOST,
            port=config.SELF_AWARENESS_PORT
        )
        logger.info(f"Self-Awareness client initialized with host={config.SELF_AWARENESS_HOST}, port={config.SELF_AWARENESS_PORT}")
    except Exception as e:
        logger.error(f"Failed to initialize Self-Awareness client: {e}")
        return None
    
    @self_awareness_bp.route('/connect', methods=['POST'])
    @authenticate
    @api_error_handler
    def connect():
        """Connect to the Self-Awareness server."""
        try:
            client.connect()
            return jsonify({"status": "connected"})
        except Exception as e:
            logger.error(f"Connect error: {e}")
            logger.debug(traceback.format_exc())
            raise APIError(f"Failed to connect: {str(e)}", 500)
    
    @self_awareness_bp.route('/disconnect', methods=['POST'])
    @authenticate
    @api_error_handler
    def disconnect():
        """Disconnect from the Self-Awareness server."""
        try:
            client.disconnect()
            return jsonify({"status": "disconnected"})
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
            raise APIError(f"Failed to disconnect: {str(e)}", 500)
    
    @self_awareness_bp.route('/status', methods=['GET'])
    @authenticate
    @api_error_handler
    def status():
        """Get client status."""
        try:
            # Get client status
            response = {
                "connected": client.connected,
                "client_id": client.client_id,
                "metrics": client.get_metrics()
            }
            
            # Get system status if connected
            if client.connected:
                system_status = client.query_system_status()
                response["system_status"] = system_status
            
            return jsonify(response)
        except Exception as e:
            logger.error(f"Status query error: {e}")
            raise APIError(f"Failed to get status: {str(e)}", 500)
    
    @self_awareness_bp.route('/metrics', methods=['POST'])
    @authenticate
    @api_error_handler
    def update_metrics():
        """Update decision metrics."""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ["confidence", "complexity", "execution_time"]
            for field in required_fields:
                if field not in data:
                    raise APIError(f"Missing required field: {field}", 400)
            
            # Update metrics
            client.update_decision_metrics(
                confidence=float(data["confidence"]),
                complexity=float(data["complexity"]),
                execution_time=float(data["execution_time"])
            )
            
            return jsonify({"status": "ok", "message": "Metrics updated successfully"})
            
        except APIError:
            raise
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
            raise APIError(f"Failed to update metrics: {str(e)}", 500)
    
    return self_awareness_bp

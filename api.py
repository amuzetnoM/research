from flask import Flask, jsonify, request, abort
import logging
import os
from inference_api.config import Config
from inference_api.auth import authenticate, authorize
from inference_api.self_awareness_api import create_self_awareness_api
from inference_api.usif_api import create_usif_api
from inference_api.pup_api import create_pup_api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load configuration
config = Config()

# Initialize rate limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day, 50 per hour"]  # Adjust as needed
)

# Create and register blueprints
if config.ENABLE_SELF_AWARENESS:
    self_awareness_api = create_self_awareness_api(config)
    if self_awareness_api:
        app.register_blueprint(self_awareness_api, url_prefix='/self_awareness')
        logger.info("Self-Awareness API registered.")
    else:
        logger.warning("Self-Awareness API not registered due to initialization errors.")

if config.ENABLE_USIF:
    usif_api = create_usif_api(config)
    if usif_api:
        app.register_blueprint(usif_api, url_prefix='/usif')
        logger.info("USIF API registered.")
    else:
        logger.warning("USIF API not registered due to initialization errors.")

if config.ENABLE_PUP:
    pup_api = create_pup_api(config)
    if pup_api:
        app.register_blueprint(pup_api, url_prefix='/pup')
        logger.info("PUP API registered.")
    else:
        logger.warning("PUP API not registered due to initialization errors.")

@app.route('/config', methods=['GET', 'POST'])
@authenticate
@authorize(config.ADMIN_ROLE)
@limiter.limit("10 per minute")  # Example: Limit config changes
def manage_config():
    """Manage the API configuration."""
    global config
    if request.method == 'POST':
        try:
            data = request.get_json()
            config = Config.from_dict(data)
            logger.info(f"Configuration updated: {config.to_dict()}")
            return jsonify({"status": "ok", "message": "Configuration updated successfully."})
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return jsonify({"status": "error", "message": str(e)}), 400

    return jsonify({"status": "ok", "config": config.to_dict()})

@app.route('/health', methods=['GET'])
@limiter.exempt
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "API is healthy."})

if __name__ == '__main__':
    port = int(os.environ.get('API_PORT', 5000))
    debug_mode = os.environ.get('API_DEBUG', 'False').lower() == 'true'
    ssl_context = None
    
    if config.USE_SSL:
        from inference_api.utils.security import get_ssl_context
        ssl_context = get_ssl_context(config.SSL_CERT, config.SSL_KEY)
    
    app.run(
        debug=debug_mode, 
        host='0.0.0.0', 
        port=port, 
        ssl_context=ssl_context
    )

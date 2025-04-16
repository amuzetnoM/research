"""
DSPy Integration API for Frontend

This module provides a Flask API to expose DSPy functionality to the frontend dashboard.
It allows the frontend to use DSPy capabilities without directly interfacing with Python.
"""

import os
import json
import logging
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import our DSPy setup
import dspy_setup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'logs', 'dspy_api.log'), 'a')
    ]
)
logger = logging.getLogger("dspy-api")

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize DSPy
dspy_initialized = dspy_setup.initialize_dspy()

# Create DSPy modules
metric_analyzer = dspy_setup.create_metric_analyzer()
container_comparator = dspy_setup.create_container_comparator()
insight_generator = dspy_setup.create_insight_generator()

@app.route('/api/dspy/status', methods=['GET'])
def get_status():
    """Get DSPy initialization status"""
    return jsonify({
        "status": "active" if dspy_initialized else "inactive",
        "message": "DSPy is initialized and ready" if dspy_initialized else "DSPy initialization failed"
    })

@app.route('/api/dspy/analyze-metrics', methods=['POST'])
def analyze_metrics():
    """Analyze metrics using DSPy"""
    try:
        data = request.json
        metrics = data.get('metrics', {})
        context = data.get('context', '')
        
        # Use the DSPy module to analyze metrics
        result = metric_analyzer(metrics=metrics, context=context)
        
        return jsonify({
            "analysis": result.analysis,
            "metrics": metrics,
            "success": True
        })
    except Exception as e:
        logger.error(f"Error analyzing metrics: {e}")
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

@app.route('/api/dspy/compare-containers', methods=['POST'])
def compare_containers():
    """Compare two containers using DSPy"""
    try:
        data = request.json
        container1_metrics = data.get('container1_metrics', {})
        container2_metrics = data.get('container2_metrics', {})
        metric_name = data.get('metric_name', '')
        
        # Use the DSPy module to compare containers
        result = container_comparator(
            container1_metrics=container1_metrics,
            container2_metrics=container2_metrics,
            metric_name=metric_name
        )
        
        return jsonify({
            "comparison": result.comparison,
            "recommendation": result.recommendation,
            "success": True
        })
    except Exception as e:
        logger.error(f"Error comparing containers: {e}")
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

@app.route('/api/dspy/generate-insights', methods=['POST'])
def generate_insights():
    """Generate insights from data using DSPy"""
    try:
        data = request.json
        input_data = data.get('data', {})
        context = data.get('context', '')
        
        # Use the DSPy module to generate insights
        result = insight_generator(
            data=input_data,
            context=context
        )
        
        return jsonify({
            "insights": result.insights,
            "summary": result.summary,
            "success": True
        })
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), 'logs'), exist_ok=True)
    
    # Message about status
    status = "initialized" if dspy_initialized else "initialization failed"
    logger.info(f"Starting DSPy API server with DSPy {status}")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
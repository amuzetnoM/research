import json
import logging
import uuid
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List
from queue import Queue
from flask import Flask, request, Response, jsonify
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("self-awareness-server")

class SelfAwarenessServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Dict[str, Queue] = {}
        self.client_data: Dict[str, Dict[str, Any]] = {}
        self.running = False
        self.monitor_threads: Dict[str, threading.Thread] = {}
        
        # Create Flask app
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        # Client registration endpoint
        @self.app.route('/register', methods=['POST'])
        def register_client():
            # Generate a unique ID for this client
            client_id = str(uuid.uuid4())
            
            # Create message queue for this client
            self.clients[client_id] = Queue()
            
            # Store client data
            self.client_data[client_id] = {
                "connected_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "metadata": {},
                "metrics": {}
            }
            
            logger.info(f"New client registered: {client_id}")
            
            # Start the monitoring thread for this client
            self._start_monitoring(client_id)
            
            return jsonify({
                "type": "welcome",
                "client_id": client_id,
                "message": "Connected to Self-Awareness Framework",
                "timestamp": datetime.now().isoformat()
            })
        
        # Client metadata endpoint
        @self.app.route('/client/<client_id>/metadata', methods=['POST'])
        def update_metadata(client_id):
            if client_id not in self.clients:
                return jsonify({"error": "Client not registered"}), 404
                
            # Update last activity timestamp
            self.client_data[client_id]["last_activity"] = datetime.now().isoformat()
            
            # Update metadata
            data = request.json
            self.client_data[client_id]["metadata"].update(data.get("data", {}))
            logger.debug(f"Updated metadata for client {client_id}")
            
            return jsonify({"status": "ok"})
        
        # Client metrics endpoint
        @self.app.route('/client/<client_id>/metrics', methods=['POST'])
        def update_metrics(client_id):
            if client_id not in self.clients:
                return jsonify({"error": "Client not registered"}), 404
                
            # Update last activity timestamp
            self.client_data[client_id]["last_activity"] = datetime.now().isoformat()
            
            # Update metrics
            data = request.json
            self.client_data[client_id]["metrics"].update(data.get("data", {}))
            
            # Analyze metrics
            self._analyze_metrics(client_id)
            
            return jsonify({"status": "ok"})
        
        # Client query endpoint
        @self.app.route('/client/<client_id>/query', methods=['POST'])
        def handle_query(client_id):
            if client_id not in self.clients:
                return jsonify({"error": "Client not registered"}), 404
                
            # Update last activity timestamp
            self.client_data[client_id]["last_activity"] = datetime.now().isoformat()
            
            # Process query
            query = request.json.get("query", {})
            response = self._handle_query(client_id, query)
            
            return jsonify(response)
        
        # Client events stream endpoint
        @self.app.route('/client/<client_id>/events', methods=['GET'])
        def get_events(client_id):
            if client_id not in self.clients:
                return jsonify({"error": "Client not registered"}), 404
            
            def generate():
                # Send initial message
                yield 'data: {"type":"connection_established"}\n\n'
                
                while client_id in self.clients:
                    # Wait for a message in the queue
                    try:
                        message = self.clients[client_id].get(timeout=30)
                        yield f'data: {json.dumps(message)}\n\n'
                    except:
                        # Send keep-alive message
                        yield 'data: {"type":"keepalive"}\n\n'
            
            return Response(generate(), mimetype='text/event-stream')
        
        # Client disconnection endpoint
        @self.app.route('/client/<client_id>/disconnect', methods=['POST'])
        def disconnect_client(client_id):
            if client_id in self.clients:
                self._cleanup_client(client_id)
                logger.info(f"Client {client_id} disconnected")
            
            return jsonify({"status": "ok"})
    
    def _start_monitoring(self, client_id: str):
        """Start monitoring thread for a client"""
        thread = threading.Thread(
            target=self._monitor_client,
            args=(client_id,),
            daemon=True
        )
        self.monitor_threads[client_id] = thread
        thread.start()
    
    def _monitor_client(self, client_id: str):
        """Monitoring loop for a connected client"""
        try:
            while client_id in self.clients and self.running:
                # Only send insights if we have enough data and client is still connected
                if client_id in self.clients and len(self.client_data[client_id].get("metrics", {})) > 0:
                    insights = self._generate_insights(client_id)
                    if insights:
                        self.clients[client_id].put({
                            "type": "insights",
                            "data": insights,
                            "timestamp": datetime.now().isoformat()
                        })
                
                # Adaptive sleep - more frequent updates for active clients
                time_since_activity = (datetime.now() - datetime.fromisoformat(
                    self.client_data[client_id]["last_activity"]
                )).total_seconds()
                
                sleep_time = min(max(5, time_since_activity / 10), 60)
                time.sleep(sleep_time)
        
        except Exception as e:
            logger.error(f"Error in monitoring task for client {client_id}: {str(e)}")
    
    def _analyze_metrics(self, client_id: str):
        """Analyze metrics and provide feedback if needed"""
        metrics = self.client_data[client_id].get("metrics", {})
        
        # Example: Check for high memory usage
        if metrics.get("memory_percent", 0) > 80:
            if client_id in self.clients:
                self.clients[client_id].put({
                    "type": "alert",
                    "category": "resource",
                    "message": "High memory usage detected. Consider optimizing memory allocation.",
                    "timestamp": datetime.now().isoformat(),
                    "data": {
                        "memory_percent": metrics.get("memory_percent")
                    }
                })
    
    def _generate_insights(self, client_id: str) -> Dict[str, Any]:
        """Generate insights about the client's operation"""
        metrics = self.client_data[client_id].get("metrics", {})
        metadata = self.client_data[client_id].get("metadata", {})
        
        insights = {}
        
        # Example insights generation
        if "cpu_percent" in metrics and "memory_percent" in metrics:
            insights["resource_efficiency"] = {
                "score": 100 - (metrics["cpu_percent"] + metrics["memory_percent"]) / 2,
                "recommendation": "Resource usage is within normal parameters." 
                if metrics["cpu_percent"] < 70 and metrics["memory_percent"] < 70
                else "Consider optimizing resource usage patterns."
            }
        
        if "decision_confidence" in metrics:
            insights["decision_quality"] = {
                "score": metrics["decision_confidence"],
                "trend": "stable"  # We would calculate this based on history
            }
        
        return insights
    
    def _handle_query(self, client_id: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a query from the client"""
        query_type = query.get("type")
        response = {
            "type": "query_response",
            "query_type": query_type,
            "timestamp": datetime.now().isoformat()
        }
        
        if query_type == "system_status":
            response["data"] = {
                "server_status": "healthy",
                "connected_clients": len(self.clients),
                "uptime": (datetime.now() - datetime.fromisoformat(
                    self.client_data[client_id]["connected_at"]
                )).total_seconds()
            }
        
        elif query_type == "self_metrics":
            response["data"] = self.client_data[client_id].get("metrics", {})
        
        else:
            response["error"] = f"Unknown query type: {query_type}"
        
        return response
    
    def _cleanup_client(self, client_id: str):
        """Clean up resources for a disconnected client"""
        # Stop monitoring thread
        if client_id in self.monitor_threads:
            # Thread will exit on its own since it checks for client_id in self.clients
            del self.monitor_threads[client_id]
        
        # Remove client
        if client_id in self.clients:
            del self.clients[client_id]
        
        # Keep data for a while for potential reconnection
        # Could implement a cleanup task to remove old data
    
    def start(self):
        """Start the self-awareness server"""
        self.running = True
        logger.info(f"Self-Awareness Server running on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, threaded=True)
    
    def stop(self):
        """Stop the self-awareness server"""
        self.running = False
        logger.info("Self-Awareness Server stopped")
        # In a production environment, we would use a proper shutdown mechanism
        # This is simplified for demonstration

def main():
    port = int(os.environ.get('SELF_AWARENESS_PORT', 8765))
    host = os.environ.get('SELF_AWARENESS_HOST', '0.0.0.0')
    server = SelfAwarenessServer(host=host, port=port)
    server.start()

if __name__ == "__main__":
    main()

import asyncio
import json
import logging
import websockets
import uuid
from datetime import datetime
from typing import Dict, Set, Any, Optional

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
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.client_data: Dict[str, Dict[str, Any]] = {}
        self.running = False
        
    async def handle_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        # Generate a unique ID for this client
        client_id = str(uuid.uuid4())
        
        try:
            # Register new client
            self.clients[client_id] = websocket
            self.client_data[client_id] = {
                "connected_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "metadata": {},
                "metrics": {}
            }
            
            logger.info(f"New client connected: {client_id}")
            
            # Send welcome message with client_id
            await websocket.send(json.dumps({
                "type": "welcome",
                "client_id": client_id,
                "message": "Connected to Self-Awareness Framework",
                "timestamp": datetime.now().isoformat()
            }))
            
            # Start the autonomous monitoring for this client
            monitor_task = asyncio.create_task(self._monitor_client(client_id))
            
            # Process incoming messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    self.client_data[client_id]["last_activity"] = datetime.now().isoformat()
                    
                    # Process the message based on its type
                    if data.get("type") == "metadata":
                        self.client_data[client_id]["metadata"].update(data.get("data", {}))
                        logger.debug(f"Updated metadata for client {client_id}")
                    
                    elif data.get("type") == "metrics":
                        self.client_data[client_id]["metrics"].update(data.get("data", {}))
                        await self._analyze_metrics(client_id)
                        
                    elif data.get("type") == "query":
                        response = await self._handle_query(client_id, data.get("query"))
                        await websocket.send(json.dumps(response))
                    
                    else:
                        logger.warning(f"Unknown message type from client {client_id}: {data.get('type')}")
                
                except json.JSONDecodeError:
                    logger.error(f"Received invalid JSON from client {client_id}")
                
                except Exception as e:
                    logger.error(f"Error processing message from client {client_id}: {str(e)}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} connection closed")
        
        finally:
            # Cleanup on disconnect
            if client_id in self.clients:
                del self.clients[client_id]
            monitor_task.cancel()
            logger.info(f"Client {client_id} disconnected and monitoring stopped")
    
    async def _monitor_client(self, client_id: str):
        """Autonomous monitoring loop for a connected client"""
        try:
            while client_id in self.clients:
                # Only send insights if we have enough data
                if len(self.client_data[client_id].get("metrics", {})) > 0:
                    insights = await self._generate_insights(client_id)
                    if insights and self.clients.get(client_id):
                        await self.clients[client_id].send(json.dumps({
                            "type": "insights",
                            "data": insights,
                            "timestamp": datetime.now().isoformat()
                        }))
                
                # Adaptive sleep - more frequent updates for active clients
                time_since_activity = (datetime.now() - datetime.fromisoformat(
                    self.client_data[client_id]["last_activity"]
                )).total_seconds()
                
                sleep_time = min(max(5, time_since_activity / 10), 60)
                await asyncio.sleep(sleep_time)
        
        except asyncio.CancelledError:
            logger.debug(f"Monitoring task for client {client_id} cancelled")
        
        except Exception as e:
            logger.error(f"Error in monitoring task for client {client_id}: {str(e)}")
    
    async def _analyze_metrics(self, client_id: str):
        """Analyze metrics and provide feedback if needed"""
        metrics = self.client_data[client_id].get("metrics", {})
        
        # Example: Check for high memory usage
        if metrics.get("memory_percent", 0) > 80:
            if self.clients.get(client_id):
                await self.clients[client_id].send(json.dumps({
                    "type": "alert",
                    "category": "resource",
                    "message": "High memory usage detected. Consider optimizing memory allocation.",
                    "timestamp": datetime.now().isoformat(),
                    "data": {
                        "memory_percent": metrics.get("memory_percent")
                    }
                }))
    
    async def _generate_insights(self, client_id: str) -> Dict[str, Any]:
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
    
    async def _handle_query(self, client_id: str, query: Dict[str, Any]) -> Dict[str, Any]:
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
    
    async def start(self):
        """Start the self-awareness server"""
        self.running = True
        server = await websockets.serve(self.handle_client, self.host, self.port)
        logger.info(f"Self-Awareness Server running on {self.host}:{self.port}")
        
        try:
            await server.wait_closed()
        finally:
            self.running = False
            logger.info("Self-Awareness Server stopped")

async def main():
    server = SelfAwarenessServer()
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())

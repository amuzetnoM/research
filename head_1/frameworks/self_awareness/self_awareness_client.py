import asyncio
import json
import logging
import os
import platform
import psutil
import sys
import time
import traceback
import websockets
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("self-awareness-client")

class SelfAwarenessClient:
    def __init__(self, 
                 host: Optional[str] = None, 
                 port: Optional[int] = None,
                 auto_reconnect: bool = True,
                 max_reconnect_attempts: int = 10):
        """
        Initialize the Self-Awareness Client.
        
        Args:
            host: The server host (defaults to environment variable or "localhost")
            port: The server port (defaults to environment variable or 8765)
            auto_reconnect: Whether to automatically attempt reconnection
            max_reconnect_attempts: Maximum number of reconnection attempts
        """
        # Server connection settings
        self.host = host or os.environ.get("SELF_AWARENESS_HOST", "localhost")
        self.port = port or int(os.environ.get("SELF_AWARENESS_PORT", "8765"))
        self.auto_reconnect = auto_reconnect
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_attempts = 0
        self.reconnect_delay = 1  # Initial delay in seconds, will increase with backoff
        
        # Client state
        self.websocket = None
        self.client_id = None
        self.connected = False
        self.running = False
        self.process = psutil.Process()
        
        # Monitoring tasks
        self.tasks = []
        
        # Insight and alert handlers
        self.insight_handlers: List[Callable[[Dict[str, Any]], None]] = []
        self.alert_handlers: List[Callable[[Dict[str, Any]], None]] = []
        
        # System information
        self.system_info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": sys.version,
            "cpu_count": psutil.cpu_count(),
            "start_time": datetime.now().isoformat()
        }
        
        # Self-metrics
        self.metrics = {}
        
        # Message queue for when disconnected
        self.message_queue = []

    async def connect(self):
        """Connect to the self-awareness server"""
        if self.connected:
            logger.warning("Already connected to self-awareness server")
            return
        
        self.running = True
        await self._connect()
    
    async def _connect(self):
        """Internal connection method with retry logic"""
        while self.running and not self.connected:
            try:
                logger.info(f"Connecting to self-awareness server at ws://{self.host}:{self.port}")
                self.websocket = await websockets.connect(f"ws://{self.host}:{self.port}")
                
                # Process the welcome message to get client_id
                welcome = await self.websocket.recv()
                welcome_data = json.loads(welcome)
                
                if welcome_data.get("type") == "welcome":
                    self.client_id = welcome_data.get("client_id")
                    self.connected = True
                    self.reconnect_attempts = 0
                    self.reconnect_delay = 1
                    
                    logger.info(f"Connected to self-awareness server with ID: {self.client_id}")
                    
                    # Send initial system information
                    await self._send_message({
                        "type": "metadata",
                        "data": self.system_info
                    })
                    
                    # Start background tasks
                    self._start_background_tasks()
                    
                    # Process any queued messages
                    if self.message_queue:
                        for message in self.message_queue:
                            await self._send_message(message)
                        self.message_queue = []
                    
                    # Start the message receiver loop
                    await self._message_receiver()
                else:
                    logger.error(f"Unexpected welcome message: {welcome_data}")
                    await self.websocket.close()
            
            except (websockets.exceptions.ConnectionClosed, 
                    websockets.exceptions.WebSocketException,
                    ConnectionRefusedError) as e:
                self.connected = False
                self.websocket = None
                
                if not self.auto_reconnect or self.reconnect_attempts >= self.max_reconnect_attempts:
                    logger.error(f"Failed to connect to self-awareness server: {str(e)}")
                    break
                
                self.reconnect_attempts += 1
                logger.warning(f"Connection attempt {self.reconnect_attempts} failed, retrying in {self.reconnect_delay}s")
                await asyncio.sleep(self.reconnect_delay)
                
                # Exponential backoff with maximum of 60 seconds
                self.reconnect_delay = min(self.reconnect_delay * 2, 60)
            
            except Exception as e:
                logger.error(f"Unexpected error during connection: {str(e)}")
                logger.debug(traceback.format_exc())
                break
    
    async def disconnect(self):
        """Disconnect from the self-awareness server"""
        self.running = False
        
        # Cancel all background tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Close websocket connection
        if self.websocket:
            await self.websocket.close()
        
        self.connected = False
        logger.info("Disconnected from self-awareness server")
    
    async def _message_receiver(self):
        """Process incoming messages from the server"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get("type")
                    
                    if message_type == "insights":
                        for handler in self.insight_handlers:
                            try:
                                handler(data.get("data", {}))
                            except Exception as e:
                                logger.error(f"Error in insight handler: {str(e)}")
                    
                    elif message_type == "alert":
                        for handler in self.alert_handlers:
                            try:
                                handler(data)
                            except Exception as e:
                                logger.error(f"Error in alert handler: {str(e)}")
                    
                    elif message_type == "query_response":
                        # This would be handled by specific query methods
                        pass
                    
                    else:
                        logger.debug(f"Received message of type {message_type}: {data}")
                
                except json.JSONDecodeError:
                    logger.error("Received invalid JSON message")
                
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Connection to self-awareness server closed")
            self.connected = False
            
            # Attempt reconnection if enabled
            if self.auto_reconnect and self.running:
                asyncio.create_task(self._connect())
        
        except Exception as e:
            logger.error(f"Error in message receiver: {str(e)}")
            self.connected = False
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        # Cancel any existing tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        self.tasks = [
            asyncio.create_task(self._monitor_system_resources()),
            asyncio.create_task(self._monitor_memory_patterns()),
        ]
    
    async def _monitor_system_resources(self):
        """Periodically monitor and report system resource usage"""
        try:
            while self.connected and self.running:
                try:
                    # Collect resource metrics
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    memory_info = self.process.memory_info()
                    memory_percent = self.process.memory_percent()
                    
                    # Update metrics
                    metrics = {
                        "cpu_percent": cpu_percent,
                        "memory_rss": memory_info.rss,
                        "memory_vms": memory_info.vms,
                        "memory_percent": memory_percent,
                        "num_threads": self.process.num_threads(),
                        "cpu_times": self.process.cpu_times()._asdict(),
                    }
                    
                    self.metrics.update(metrics)
                    
                    # Send to server
                    await self._send_message({
                        "type": "metrics",
                        "data": metrics
                    })
                
                except Exception as e:
                    logger.error(f"Error collecting system metrics: {str(e)}")
                
                # Adaptive monitoring frequency based on resource usage
                # Monitor more frequently when load is high
                sleep_time = 10
                if cpu_percent > 70 or memory_percent > 70:
                    sleep_time = 5
                
                await asyncio.sleep(sleep_time)
        
        except asyncio.CancelledError:
            logger.debug("System resource monitoring task cancelled")
        
        except Exception as e:
            logger.error(f"Unexpected error in system monitoring: {str(e)}")
    
    async def _monitor_memory_patterns(self):
        """Monitor memory allocation and deallocations patterns"""
        try:
            memory_samples = []
            sample_interval = 30  # seconds
            
            while self.connected and self.running:
                try:
                    # Collect memory info
                    memory_info = self.process.memory_info()
                    memory_samples.append({
                        "timestamp": time.time(),
                        "rss": memory_info.rss,
                        "vms": memory_info.vms
                    })
                    
                    # Keep only the last 10 samples
                    if len(memory_samples) > 10:
                        memory_samples.pop(0)
                    
                    # Analyze memory trends if we have enough samples
                    if len(memory_samples) >= 3:
                        # Calculate growth rate
                        first = memory_samples[0]
                        last = memory_samples[-1]
                        time_diff = last["timestamp"] - first["timestamp"]
                        
                        if time_diff > 0:
                            rss_growth_rate = (last["rss"] - first["rss"]) / time_diff
                            
                            # Update metrics with memory analysis
                            self.metrics.update({
                                "memory_growth_rate": rss_growth_rate,
                                "memory_stability": "growing" if rss_growth_rate > 1024*10 else "stable"
                            })
                    
                except Exception as e:
                    logger.error(f"Error analyzing memory patterns: {str(e)}")
                
                await asyncio.sleep(sample_interval)
        
        except asyncio.CancelledError:
            logger.debug("Memory pattern monitoring task cancelled")
        
        except Exception as e:
            logger.error(f"Unexpected error in memory monitoring: {str(e)}")
    
    async def _send_message(self, message: Dict[str, Any]):
        """Send a message to the self-awareness server"""
        # Add timestamp if not already present
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
        
        if not self.connected:
            # Queue message for when connection is established
            self.message_queue.append(message)
            return
        
        try:
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            self.message_queue.append(message)
    
    async def query_system_status(self) -> Dict[str, Any]:
        """Query the server for system status information"""
        if not self.connected:
            return {"error": "Not connected to self-awareness server"}
        
        try:
            await self._send_message({
                "type": "query",
                "query": {
                    "type": "system_status"
                }
            })
            
            # Wait for response (in a real implementation, we would use a future or callback)
            # This is simplified for demonstration
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            return json.loads(response)
        
        except asyncio.TimeoutError:
            return {"error": "Timeout waiting for system status response"}
        
        except Exception as e:
            return {"error": f"Error querying system status: {str(e)}"}
    
    def add_insight_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Add a handler function for insights received from the server"""
        self.insight_handlers.append(handler)
    
    def add_alert_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Add a handler function for alerts received from the server"""
        self.alert_handlers.append(handler)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get the current set of self-metrics"""
        return self.metrics.copy()

    async def update_decision_metrics(self, confidence: float, complexity: float, execution_time: float):
        """Update metrics related to decision-making processes"""
        metrics = {
            "decision_confidence": confidence,
            "decision_complexity": complexity,
            "decision_execution_time": execution_time,
            "decisions_per_minute": self.metrics.get("decisions_per_minute", 0) + 1
        }
        
        self.metrics.update(metrics)
        
        await self._send_message({
            "type": "metrics",
            "data": metrics
        })

    # Context manager support
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

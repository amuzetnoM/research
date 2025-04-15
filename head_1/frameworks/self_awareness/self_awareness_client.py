import json
import logging
import os
import platform
import psutil
import sys
import time
import traceback
import threading
import requests
import sseclient # type: ignore
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
        self.client_id = None
        self.connected = False
        self.running = False
        self.process = psutil.Process()
        
        # Monitoring tasks
        self.threads = []
        
        # Event listeners
        self.sse_thread = None
        
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
        
        # Server base URL
        self.base_url = f"http://{self.host}:{self.port}"
        
        # Session for HTTP requests
        self.session = requests.Session()
    
    def connect(self):
        """Connect to the self-awareness server"""
        if self.connected:
            logger.warning("Already connected to self-awareness server")
            return
        
        self.running = True
        self._connect()
    
    def _connect(self):
        """Internal connection method with retry logic"""
        while self.running and not self.connected:
            try:
                logger.info(f"Connecting to self-awareness server at {self.base_url}")
                
                # Register with the server
                response = self.session.post(f"{self.base_url}/register")
                response.raise_for_status()
                welcome_data = response.json()
                
                if welcome_data.get("type") == "welcome":
                    self.client_id = welcome_data.get("client_id")
                    self.connected = True
                    self.reconnect_attempts = 0
                    self.reconnect_delay = 1
                    
                    logger.info(f"Connected to self-awareness server with ID: {self.client_id}")
                    
                    # Send initial system information
                    self._send_message({
                        "type": "metadata",
                        "data": self.system_info
                    })
                    
                    # Start background tasks
                    self._start_background_tasks()
                    
                    # Process any queued messages
                    if self.message_queue:
                        for message in self.message_queue:
                            self._send_message(message)
                        self.message_queue = []
                    
                    # Start the event listener
                    self._start_event_listener()
                else:
                    logger.error(f"Unexpected welcome message: {welcome_data}")
            
            except (requests.exceptions.RequestException, ConnectionError) as e:
                self.connected = False
                
                if not self.auto_reconnect or self.reconnect_attempts >= self.max_reconnect_attempts:
                    logger.error(f"Failed to connect to self-awareness server: {str(e)}")
                    break
                
                self.reconnect_attempts += 1
                logger.warning(f"Connection attempt {self.reconnect_attempts} failed, retrying in {self.reconnect_delay}s")
                time.sleep(self.reconnect_delay)
                
                # Exponential backoff with maximum of 60 seconds
                self.reconnect_delay = min(self.reconnect_delay * 2, 60)
            
            except Exception as e:
                logger.error(f"Unexpected error during connection: {str(e)}")
                logger.debug(traceback.format_exc())
                break
    
    def disconnect(self):
        """Disconnect from the self-awareness server"""
        self.running = False
        
        # Stop all background threads
        self._stop_background_tasks()
        
        # Notify server if connected
        if self.connected and self.client_id:
            try:
                self.session.post(f"{self.base_url}/client/{self.client_id}/disconnect")
            except Exception as e:
                logger.error(f"Error during disconnection: {str(e)}")
        
        self.connected = False
        logger.info("Disconnected from self-awareness server")
    
    def _start_event_listener(self):
        """Start the SSE event listener thread"""
        self.sse_thread = threading.Thread(
            target=self._event_listener,
            daemon=True
        )
        self.sse_thread.start()
    
    def _event_listener(self):  # sourcery skip: low-code-quality
        """Listen for server-sent events"""
        try:
            headers = {'Accept': 'text/event-stream'}
            url = f"{self.base_url}/client/{self.client_id}/events"

            while self.connected and self.running:
                try:
                    response = self.session.get(url, headers=headers, stream=True)
                    client = sseclient.SSEClient(response)

                    for event in client.events():
                        if not self.connected or not self.running:
                            break

                        try:
                            data = json.loads(event.data)
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

                            elif message_type != "keepalive":
                                logger.debug(f"Received message of type {message_type}: {data}")

                        except json.JSONDecodeError:
                            logger.error("Received invalid JSON message")

                        except Exception as e:
                            logger.error(f"Error processing message: {str(e)}")

                except (requests.exceptions.RequestException, ConnectionError):
                    logger.warning("Connection to self-awareness server closed")
                    self.connected = False

                    # Attempt reconnection if enabled
                    if self.auto_reconnect and self.running:
                        self._connect()
                    break

                except Exception as e:
                    logger.error(f"Error in event listener: {str(e)}")
                    self.connected = False
                    time.sleep(5)  # Wait before retrying

        except Exception as e:
            logger.error(f"Fatal error in event listener: {str(e)}")
            self.connected = False
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        # Cancel any existing tasks
        self._stop_background_tasks()
        
        # Create and start new threads
        system_resources_thread = threading.Thread(
            target=self._monitor_system_resources,
            daemon=True
        )
        
        memory_patterns_thread = threading.Thread(
            target=self._monitor_memory_patterns,
            daemon=True
        )
        
        self.threads = [system_resources_thread, memory_patterns_thread]
        
        for thread in self.threads:
            thread.start()
    
    def _stop_background_tasks(self):
        """Stop background tasks - threads will exit on their own since they check self.running"""
        self.threads = []
    
    def _monitor_system_resources(self):
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
                    self._send_message({
                        "type": "metrics",
                        "data": metrics
                    })
                
                except Exception as e:
                    logger.error(f"Error collecting system metrics: {str(e)}")
                
                # Adaptive monitoring frequency based on resource usage
                sleep_time = 10
                if cpu_percent > 70 or memory_percent > 70:
                    sleep_time = 5
                
                time.sleep(sleep_time)
        
        except Exception as e:
            logger.error(f"Unexpected error in system monitoring: {str(e)}")
    
    def _monitor_memory_patterns(self):
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
                
                time.sleep(sample_interval)
        
        except Exception as e:
            logger.error(f"Unexpected error in memory monitoring: {str(e)}")
    
    def _send_message(self, message: Dict[str, Any]):
        """Send a message to the self-awareness server"""
        # Add timestamp if not already present
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
        
        if not self.connected or not self.client_id:
            # Queue message for when connection is established
            self.message_queue.append(message)
            return
        
        try:
            # Determine endpoint based on message type
            if message["type"] == "metadata":
                endpoint = f"{self.base_url}/client/{self.client_id}/metadata"
            elif message["type"] == "metrics":
                endpoint = f"{self.base_url}/client/{self.client_id}/metrics"
            elif message["type"] == "query":
                endpoint = f"{self.base_url}/client/{self.client_id}/query"
            else:
                logger.warning(f"Unknown message type: {message['type']}")
                return
            
            # Send the request
            response = self.session.post(endpoint, json=message)
            response.raise_for_status()
        
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            self.message_queue.append(message)
            
            # Check if connection is lost
            if isinstance(e, requests.exceptions.ConnectionError):
                self.connected = False
                if self.auto_reconnect and self.running:
                    self._connect()
    
    def query_system_status(self) -> Dict[str, Any]:
        """Query the server for system status information"""
        if not self.connected:
            return {"error": "Not connected to self-awareness server"}
        
        try:
            query_message = {
                "type": "query",
                "query": {
                    "type": "system_status"
                }
            }
            
            endpoint = f"{self.base_url}/client/{self.client_id}/query"
            response = self.session.post(endpoint, json=query_message)
            response.raise_for_status()
            
            return response.json()
        
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

    def update_decision_metrics(self, confidence: float, complexity: float, execution_time: float):
        """Update metrics related to decision-making processes"""
        metrics = {
            "decision_confidence": confidence,
            "decision_complexity": complexity,
            "decision_execution_time": execution_time,
            "decisions_per_minute": self.metrics.get("decisions_per_minute", 0) + 1
        }
        
        self.metrics.update(metrics)
        
        self._send_message({
            "type": "metrics",
            "data": metrics
        })
    
    # Context manager support
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

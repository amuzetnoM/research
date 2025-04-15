import logging
import random
import time
import threading
from self_awareness_client import SelfAwarenessClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("example-ai-agent")

class SimpleAIAgent:
    def __init__(self):
        self.awareness = SelfAwarenessClient()
        self.running = False
        self.processing_intensity = 5  # Scale 1-10
        
        # Register handlers for insights and alerts
        self.awareness.add_insight_handler(self.handle_insight)
        self.awareness.add_alert_handler(self.handle_alert)
    
    def handle_insight(self, insight_data):
        """Process insights received from the self-awareness framework"""
        logger.info(f"Received insight: {insight_data}")
        
        # Example: Adjust behavior based on resource efficiency insight
        if "resource_efficiency" in insight_data:
            efficiency = insight_data["resource_efficiency"]["score"]
            if efficiency < 50:
                logger.info("Resource efficiency is low. Adjusting processing parameters.")
                # Simulate adjusting parameters
                self.processing_intensity = max(1, self.processing_intensity - 1)
    
    def handle_alert(self, alert_data):
        """Handle alerts from the self-awareness framework"""
        logger.warning(f"Received alert: {alert_data['message']}")
        
        # Example: React to high memory usage alert
        if alert_data.get("category") == "resource" and "memory" in alert_data.get("message", ""):
            logger.warning("Memory alert received. Performing garbage collection.")
            # Simulate memory cleanup
            import gc
            gc.collect()
    
    def start(self):
        """Start the AI agent"""
        logger.info("Starting example AI agent")
        self.running = True
        
        # Connect to self-awareness framework
        self.awareness.connect()
        
        # Start processing thread
        self.process_thread = threading.Thread(target=self.process_loop)
        self.process_thread.daemon = True
        self.process_thread.start()
    
    def stop(self):
        """Stop the AI agent"""
        logger.info("Stopping example AI agent")
        self.running = False
        
        # Wait for processing to complete
        if hasattr(self, 'process_thread') and self.process_thread.is_alive():
            self.process_thread.join(timeout=3.0)
        
        # Disconnect from self-awareness framework
        self.awareness.disconnect()
    
    def process_loop(self):
        """Main processing loop simulating AI workload"""
        decision_count = 0
        
        while self.running:
            try:
                # Simulate AI processing
                logger.debug(f"Processing with intensity level {self.processing_intensity}")
                
                # Simulate computational load
                start_time = time.time()
                self.simulate_processing()
                execution_time = time.time() - start_time
                
                # Make a simulated decision with random confidence
                confidence = random.uniform(0.7, 0.98)
                complexity = random.uniform(1.0, 10.0)
                
                # Report decision metrics
                self.awareness.update_decision_metrics(
                    confidence=confidence,
                    complexity=complexity,
                    execution_time=execution_time
                )
                
                decision_count += 1
                if decision_count % 5 == 0:
                    # Periodically query system status
                    status = self.awareness.query_system_status()
                    logger.info(f"System status: {status}")
                
                # Adaptive sleep based on intensity
                time.sleep(11 - self.processing_intensity)
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                time.sleep(5)  # Sleep longer on error
    
    def simulate_processing(self):
        """Simulate AI processing workload"""
        # Create some memory allocations
        data = [random.random() for _ in range(100000 * self.processing_intensity)]
        
        # Simulate CPU usage
        for _ in range(self.processing_intensity * 1000):
            _ = [i * i for i in range(1000)]
        
        # Clear some data to avoid memory issues in example
        if random.random() > 0.7:
            data.clear()

def main():
    agent = SimpleAIAgent()
    
    try:
        agent.start()
        
        # Run for a while
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down")
    
    finally:
        agent.stop()

if __name__ == "__main__":
    main()

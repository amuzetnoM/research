import asyncio
import logging
import random
import time
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
    
    async def run(self):
        """Main AI agent loop"""
        try:
            # Connect to the self-awareness framework
            await self.awareness.connect()
            
            self.running = True
            self.processing_intensity = 3  # Scale from 1-10
            
            # Simulate AI work
            while self.running:
                start_time = time.time()
                
                # Simulate AI decision making
                decision_complexity = random.uniform(1.0, 10.0)
                decision_confidence = random.uniform(0.7, 0.99)
                
                # Simulate variable computational load based on processing intensity
                await self.simulate_computation(self.processing_intensity)
                
                execution_time = time.time() - start_time
                
                # Report decision metrics to the self-awareness framework
                await self.awareness.update_decision_metrics(
                    confidence=decision_confidence,
                    complexity=decision_complexity,
                    execution_time=execution_time
                )
                
                # Adaptive sleep based on processing intensity
                await asyncio.sleep(1 + (10 - self.processing_intensity) / 2)
        
        except KeyboardInterrupt:
            logger.info("Stopping AI agent due to keyboard interrupt")
        
        except Exception as e:
            logger.error(f"Error in AI agent: {str(e)}")
        
        finally:
            self.running = False
            await self.awareness.disconnect()
    
    async def simulate_computation(self, intensity):
        """Simulate computational work with variable intensity"""
        # Create some memory allocations to simulate work
        data = [random.random() for _ in range(int(100000 * intensity))]
        
        # Simulate CPU-intensive operation
        result = 0
        for i in range(int(50000 * intensity)):
            result += (i * i) % 1337
        
        return result

async def main():
    agent = SimpleAIAgent()
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())

"""
DSPy Setup for Research Dashboard

This module initializes and configures DSPy for use in our research dashboard.
DSPy enables us to program language models with modular, optimizable components.
"""

import os
import logging
import dspy
from typing import Optional, Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'logs', 'dspy.log'), 'a')
    ]
)
logger = logging.getLogger("dspy-setup")

def initialize_dspy(api_key: Optional[str] = None, model_name: str = 'openai/gpt-4o-mini') -> bool:
    """
    Initialize DSPy with the specified LM configuration.
    
    Args:
        api_key: OpenAI API key (or None to use environment variable)
        model_name: Name of the model to use
        
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    try:
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(__file__), 'logs'), exist_ok=True)
        
        # Set API key from environment variable if not provided
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                logger.warning("No API key provided and OPENAI_API_KEY environment variable not set")
                logger.info("Using DSPy with a local LM or demo mode")
        
        # Initialize language model
        lm = dspy.LM(model_name, api_key=api_key)
        
        # Configure DSPy to use this language model
        dspy.configure(lm=lm)
        
        logger.info(f"DSPy initialized successfully with model: {model_name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize DSPy: {e}")
        return False

def create_metric_analyzer() -> dspy.Module:
    """
    Create a DSPy module for analyzing research metrics.
    
    Returns:
        dspy.Module: A configured DSPy module for metric analysis
    """
    # Define a simple ChainOfThought module for metric analysis
    class MetricAnalyzer(dspy.ChainOfThought):
        """Analyze research metrics and provide insights."""
        
        def __init__(self):
            super().__init__(
                signature=dspy.Signature(
                    metrics="Dict[str, float]",
                    context="str",
                    analysis="str"
                )
            )
    
    return MetricAnalyzer()

def create_container_comparator() -> dspy.Module:
    """
    Create a DSPy module for comparing research containers.
    
    Returns:
        dspy.Module: A configured DSPy module for container comparison
    """
    # Define a module for comparing containers
    class ContainerComparator(dspy.MultiChainComparison):
        """Compare metrics between two research containers."""
        
        def __init__(self):
            super().__init__(
                signature=dspy.Signature(
                    container1_metrics="Dict[str, float]",
                    container2_metrics="Dict[str, float]",
                    metric_name="str",
                    comparison="str",
                    recommendation="str"
                )
            )
    
    return ContainerComparator()

def create_insight_generator() -> dspy.Module:
    """
    Create a DSPy module for generating insights from research data.
    
    Returns:
        dspy.Module: A configured DSPy module for insight generation
    """
    # Define a module for generating insights
    class InsightGenerator(dspy.ChainOfThought):
        """Generate insights from research metrics and data."""
        
        def __init__(self):
            super().__init__(
                signature=dspy.Signature(
                    data="Dict[str, Any]",
                    context="str",
                    insights="List[str]",
                    summary="str"
                )
            )
    
    return InsightGenerator()

if __name__ == "__main__":
    # Initialize DSPy when run directly
    initialize_dspy()
    
    # Test the modules
    metric_analyzer = create_metric_analyzer()
    container_comparator = create_container_comparator()
    insight_generator = create_insight_generator()
    
    logger.info("DSPy modules created successfully")
    logger.info("Run with an API key to use with actual LMs")
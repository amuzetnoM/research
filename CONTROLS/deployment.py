import json
from pathlib import Path
from typing import Union
import logging

logger = logging.getLogger(__name__)

FRAMEWORK_AVAILABLE = True  # Placeholder for actual framework availability check

class DeploymentManager:
    """Manages deployment of Self-Awareness Framework instances."""
    
    def __init__(self, base_path: Union[str, Path] = None):
        """Initialize the deployment manager.
        
        Args:
            base_path: Base directory for deployments
        """
        if not FRAMEWORK_AVAILABLE:
            logger.warning("Self-Awareness Framework not available. Limited functionality.")
        
        self.base_path = Path(base_path) if base_path else Path.cwd() / "self_awareness_deployments"
        self.framework_instances = {}
        self.deployment_configs = {}
        
        # Create necessary directories
        self._setup_directories()
    
    def _setup_directories(self):
        """Create necessary directory structure for deployments."""
        directories = [
            self.base_path,
            self.base_path / "configs",
            self.base_path / "data",
            self.base_path / "models",
            self.base_path / "logs",
            # Add directories for emotional framework
            self.base_path / "data" / "emotional_analysis",
            self.base_path / "data" / "emotional_analysis" / "models"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {directory}")
    
    def deploy_self_awareness_framework(self, container_id: str = 'default') -> bool:
        """Deploy the Self-Awareness Framework with extended configuration.
        
        Args:
            container_id: Container or instance identifier
            
        Returns:
            True if successful, False otherwise
        """
        if not FRAMEWORK_AVAILABLE:
            logger.error("Cannot deploy: Self-Awareness Framework not available")
            return False
            
        try:
            logger.info(f"Deploying Self-Awareness Framework to {container_id}")
            
            # Create container-specific configuration
            config = {
                'id': f"self-aware-{container_id}",
                'monitoring_rate': 1.0,
                'container_id': container_id,
                'safety_bounds': {
                    'max_memory_percent': 90,
                    'max_cpu_percent': 95
                }
            }
            
            # Create deployment
            config_path = self.create_deployment(container_id, config)
            if not config_path:
                logger.error(f"Failed to create deployment for {container_id}")
                return False
                
            # Get framework instance
            if container_id not in self.framework_instances:
                logger.error(f"Framework instance for {container_id} not found")
                return False
                
            framework = self.framework_instances[container_id]
            
            # Register additional capabilities specific to the container
            framework.capability_assessment.register_capability(
                'recursive_reasoning', 
                'Perform recursive reasoning and self-modification',
                {'cpu': 0.2, 'memory': 200 * 1024 * 1024}  # 200MB
            )
            
            framework.capability_assessment.register_capability(
                'uncertainty_modeling', 
                'Model uncertainty across multiple domains',
                {'cpu': 0.15, 'memory': 150 * 1024 * 1024}  # 150MB
            )
            
            # Update capability performance with initial values
            framework.capability_assessment.update_capability_performance(
                'self_monitoring', 0.85, 0.9)
            framework.capability_assessment.update_capability_performance(
                'uncertainty_quantification', 0.7, 0.8)
            framework.capability_assessment.update_capability_performance(
                'recursive_reasoning', 0.6, 0.75)
            framework.capability_assessment.update_capability_performance(
                'uncertainty_modeling', 0.65, 0.7)
            
            # Add knowledge elements
            framework.knowledge_modeling.add_knowledge(
                'system_architecture', 
                'Comprehensive understanding of system architecture',
                0.9, 
                'initialization'
            )
            
            framework.knowledge_modeling.add_knowledge(
                'reasoning_limitations', 
                'Awareness of recursive reasoning limitations',
                0.6, 
                'initialization'
            )
            
            # Update metrics for all dimensions
            for dim in AwarenessDimension:
                # Set different values for each dimension to create a realistic profile
                value = 0.5  # Base value
                
                if dim == AwarenessDimension.INTROSPECTIVE:
                    value = 0.8  # Strong in introspection
                elif dim == AwarenessDimension.CAPABILITY:
                    value = 0.75  # Good capability awareness
                elif dim == AwarenessDimension.EPISTEMIC:
                    value = 0.6  # Moderate knowledge awareness
                elif dim == AwarenessDimension.TEMPORAL:
                    value = 0.5  # Average temporal awareness
                elif dim == AwarenessDimension.SOCIAL:
                    value = 0.4  # Lower social awareness
                    
                framework.metrics.update(dim, value)
            
            # Get and save the self-model
            self._save_deployment_model(container_id)
            
            logger.info(f"Self-Awareness Framework deployed to {container_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deploying Self-Awareness Framework: {e}")
            return False
            
    def deploy_emotional_framework(self, container_id: str = 'default') -> bool:
        """Deploy the Emotional Dimensionality Framework.
        
        Args:
            container_id: Container or instance identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Dynamic import to avoid dependencies when not needed
            from self_awareness import EmotionalDimensionalityFramework, RuleBasedEDFModel, NeuralEDFModel
            
            logger.info(f"Deploying Emotional Dimensionality Framework to {container_id}")
            
            # Create container-specific configuration
            neural_model_path = self.base_path / "data" / "emotional_analysis" / "models" / "neural_edf_model.pt"
            config = {
                'id': f"edf-{container_id}",
                'neural_model_path': str(neural_model_path),
                'container_id': container_id
            }
            
            # Initialize framework
            framework = EmotionalDimensionalityFramework(config)
            
            # Add rule-based model
            rule_based_model = RuleBasedEDFModel()
            framework.add_model("rule_based", rule_based_model)
            
            # Try to add neural model if file exists
            if neural_model_path.exists():
                neural_model = NeuralEDFModel(str(neural_model_path))
                if neural_model.model_loaded:
                    framework.add_model("neural", neural_model)
                    logger.info("Neural EDF model loaded successfully")
                else:
                    logger.warning("Neural EDF model could not be loaded")
            else:
                logger.info("Neural EDF model not found, using rule-based model only")
                
                # Create a directory to hold dummy model if needed
                neural_model_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Create a placeholder file for future use
                if not neural_model_path.exists():
                    with open(neural_model_path, 'w') as f:
                        f.write('placeholder')
                    logger.info(f"Created placeholder for neural model at {neural_model_path}")
            
            # Save framework configuration
            output_file = self.base_path / "data" / "emotional_analysis" / f"{container_id}_edf_config.json"
            framework.save_configuration(str(output_file))
            
            # Store the framework instance (optional - if we want to keep it active)
            self.framework_instances[f"edf-{container_id}"] = framework
            
            logger.info(f"Emotional Dimensionality Framework deployed to {container_id}")
            
            # Perform a test analysis
            test_text = "I'm excited about the potential of this advanced AI research project!"
            result = framework.analyze(test_text)
            
            # Save sample analysis
            sample_file = self.base_path / "data" / "emotional_analysis" / f"{container_id}_sample_analysis.json"
            with open(sample_file, 'w') as f:
                json.dump(result.serialize(), f, indent=2)
            
            logger.info(f"Sample analysis saved to {sample_file}")
            
            return True
            
        except ImportError:
            logger.error("Emotional Dimensionality Framework not available.")
            return False
        except Exception as e:
            logger.error(f"Error deploying Emotional Dimensionality Framework: {e}")
            return False
            
    def configure_framework_startup(self) -> bool:
        """Create a configuration file for auto-starting frameworks on startup.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create configuration directory if it doesn't exist
            config_dir = Path(self.base_path) / "configs" / "startup"
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Create configuration file
            config_file = config_dir / "startup_config.json"
            
            config = {
                "auto_start": True,
                "frameworks": {
                    "self_awareness": {
                        "enabled": True,
                        "monitoring_rate": 1.0,
                        "save_model_interval": 3600  # Save self-model every hour
                    },
                    "emotional_dimensionality": {
                        "enabled": True,
                        "default_model": "rule_based"
                    }
                }
            }
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
            logger.info(f"Created framework startup configuration at {config_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error configuring framework startup: {e}")
            return False
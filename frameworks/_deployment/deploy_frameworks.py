"""
Deployment script for Self-Awareness and Emotional Dimensionality Frameworks.

This script initializes, configures, and deploys the frameworks across containers,
setting up all necessary data structures and visualization tools.
"""

import os
import sys
import json
import shutil
import logging
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '../..'))
sys.path.append(parent_dir)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(script_dir, 'deployment.log'))
    ]
)
logger = logging.getLogger('deployment')

def create_directories():
    """Create necessary directories for framework data and models."""
    directories = [
        os.path.join(parent_dir, 'data', 'self_models'),
        os.path.join(parent_dir, 'data', 'self_models', 'history'),
        os.path.join(parent_dir, 'data', 'emotional_analysis'),
        os.path.join(parent_dir, 'data', 'emotional_analysis', 'models')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def deploy_self_awareness_framework(container_id='terminal_1'):
    """Deploy the Self-Awareness Framework to the specified container."""
    try:
        from system.ai_frameworks.self_awareness import SelfAwarenessFramework, AwarenessDimension
        
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
        
        # Initialize framework
        framework = SelfAwarenessFramework(config)
        
        # Start the framework
        framework.start()
        
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
        
        # Update capability performance with some initial values
        framework.capability_assessment.update_capability_performance(
            'self_monitoring', 0.85, 0.9)
        framework.capability_assessment.update_capability_performance(
            'uncertainty_quantification', 0.7, 0.8)
        framework.capability_assessment.update_capability_performance(
            'recursive_reasoning', 0.6, 0.75)
        framework.capability_assessment.update_capability_performance(
            'uncertainty_modeling', 0.65, 0.7)
        
        # Add some knowledge elements
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
        
        # Update metrics
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
        self_model = framework.get_self_model()
        
        # Save to container-specific file
        output_file = os.path.join(parent_dir, 'data', 'self_models', f'{container_id}_self_model.json')
        with open(output_file, 'w') as f:
            json.dump(self_model, f, indent=2)
        
        # Also save to history
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        history_file = os.path.join(parent_dir, 'data', 'self_models', 'history', 
                                   f'{container_id}_{timestamp}.json')
        with open(history_file, 'w') as f:
            json.dump(self_model, f, indent=2)
        
        logger.info(f"Self-Awareness Framework deployed to {container_id}")
        logger.info(f"Self-model saved to {output_file}")
        
        # Stop the framework
        framework.stop()
        
        return True
    
    except Exception as e:
        logger.error(f"Error deploying Self-Awareness Framework: {e}")
        return False

def deploy_emotional_framework(container_id='terminal_1'):
    """Deploy the Emotional Dimensionality Framework to the specified container."""
    try:
        from system.ai_frameworks.emotional_dimensionality import (
            EmotionalDimensionalityFramework, 
            RuleBasedEDFModel, 
            NeuralEDFModel
        )
        
        logger.info(f"Deploying Emotional Dimensionality Framework to {container_id}")
        
        # Create container-specific configuration
        config = {
            'id': f"edf-{container_id}",
            'neural_model_path': os.path.join(parent_dir, 'data', 'emotional_analysis', 'models', 'neural_edf_model.pt'),
            'container_id': container_id
        }
        
        # Initialize framework
        framework = EmotionalDimensionalityFramework(config)
        
        # Add rule-based model
        rule_based_model = RuleBasedEDFModel()
        framework.add_model("rule_based", rule_based_model)
        
        # Try to add neural model if file exists
        neural_model_path = config['neural_model_path']
        if os.path.exists(neural_model_path):
            neural_model = NeuralEDFModel(neural_model_path)
            if neural_model.model_loaded:
                framework.add_model("neural", neural_model)
                logger.info("Neural EDF model loaded successfully")
            else:
                logger.warning("Neural EDF model could not be loaded")
        else:
            logger.info("Neural EDF model not found, using rule-based model only")
            
            # Create a directory to hold dummy model if needed
            os.makedirs(os.path.dirname(neural_model_path), exist_ok=True)
            
            # Create a placeholder file for future use
            if not os.path.exists(neural_model_path):
                with open(neural_model_path, 'w') as f:
                    f.write('placeholder')
                logger.info(f"Created placeholder for neural model at {neural_model_path}")
        
        # Save framework configuration
        output_file = os.path.join(parent_dir, 'data', 'emotional_analysis', f'{container_id}_edf_config.json')
        framework.save_configuration(output_file)
        
        logger.info(f"Emotional Dimensionality Framework deployed to {container_id}")
        logger.info(f"Framework configuration saved to {output_file}")
        
        # Perform a test analysis
        test_text = "I'm excited about the potential of this advanced AI research project!"
        result = framework.analyze(test_text)
        
        # Save sample analysis
        sample_file = os.path.join(parent_dir, 'data', 'emotional_analysis', f'{container_id}_sample_analysis.json')
        with open(sample_file, 'w') as f:
            json.dump(result.serialize(), f, indent=2)
        
        logger.info(f"Sample analysis saved to {sample_file}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error deploying Emotional Dimensionality Framework: {e}")
        return False

def update_runtime_scripts():
    """Update runtime optimization scripts to initialize frameworks."""
    try:
        # Paths to the runtime scripts
        scripts = [
            os.path.join(parent_dir, 'terminal_1', 'runtime_optimization.sh'),
            os.path.join(parent_dir, 'terminal_2', 'runtime_optimization.sh')
        ]
        
        # Framework initialization code to insert
        framework_init_code = """
# Initialize AI frameworks if enabled
initialize_frameworks() {
  # Initialize Self-Awareness Mechanics if enabled
  if [[ "$ENABLE_SELF_AWARENESS" == "true" ]]; then
    echo "Initializing Self-Awareness Mechanics framework..."
    python3 -c "
try:
    from system.ai_frameworks.self_awareness import SelfAwarenessFramework
    
    # Get configuration
    config = {
        'id': f'self-aware-{os.environ.get(\\"CONTAINER_ID\\", \\"unknown\\")}',
        'monitoring_rate': 1.0
    }
    
    # Initialize the framework
    framework = SelfAwarenessFramework(config)
    
    # Start the framework
    framework.start()
    print('Self-Awareness Mechanics framework initialized and running')
except Exception as e:
    print(f'Error initializing Self-Awareness Mechanics: {e}')
" &
  fi
  
  # Initialize Emotional Dimensionality Framework if enabled
  if [[ "$ENABLE_EMOTIONAL_FRAMEWORK" == "true" ]]; then
    echo "Initializing Emotional Dimensionality Framework..."
    python3 -c "
try:
    from system.ai_frameworks.emotional_dimensionality import EmotionalDimensionalityFramework, RuleBasedEDFModel
    
    # Get configuration
    container_id = os.environ.get(\\"CONTAINER_ID\\", \\"unknown\\")
    config = {
        'id': f'edf-{container_id}'
    }
    
    # Initialize the framework
    framework = EmotionalDimensionalityFramework(config)
    
    # Add rule-based model
    framework.add_model('rule_based', RuleBasedEDFModel())
    
    print('Emotional Dimensionality Framework initialized')
except Exception as e:
    print(f'Error initializing Emotional Dimensionality Framework: {e}')
" &
  fi
}
"""
        
        # Call to initialize frameworks
        init_call = """
# Initialize AI frameworks
export ENABLE_SELF_AWARENESS=true
export ENABLE_EMOTIONAL_FRAMEWORK=true
initialize_frameworks
"""
        
        # Update each script
        for script_path in scripts:
            if os.path.exists(script_path):
                logger.info(f"Updating runtime script: {script_path}")
                
                # Read the current content
                with open(script_path, 'r') as f:
                    content = f.read()
                
                # Check if frameworks are already initialized
                if "initialize_frameworks" in content:
                    logger.info(f"Frameworks already initialized in {script_path}")
                    continue
                
                # Find the position to insert the initialization
                optimization_end = content.find("# Apply remaining optimizations")
                if optimization_end == -1:
                    # Alternative location if the first one is not found
                    optimization_end = content.find("# Print environment summary")
                
                if optimization_end != -1:
                    # Insert the framework initialization code before the summary
                    new_content = content[:optimization_end] + framework_init_code + "\n" + content[optimization_end:]
                    
                    # Find position to add the initialization call - just before printing summary
                    summary_pos = new_content.find("# Print environment summary")
                    if summary_pos != -1:
                        new_content = new_content[:summary_pos] + init_call + "\n" + new_content[summary_pos:]
                        
                        # Write the updated content
                        with open(script_path, 'w') as f:
                            f.write(new_content)
                        
                        logger.info(f"Updated {script_path} with framework initialization")
                    else:
                        logger.warning(f"Could not find position to add initialization call in {script_path}")
                else:
                    logger.warning(f"Could not find position to insert framework code in {script_path}")
            else:
                logger.warning(f"Runtime script not found: {script_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error updating runtime scripts: {e}")
        return False

def install_required_libraries():
    """Install required Python libraries for the frameworks."""
    try:
        logger.info("Installing required libraries for AI frameworks...")
        
        # Define list of required packages
        packages = [
            "numpy",
            "pandas",
            "matplotlib",
            "plotly",
            "networkx",
            "ipywidgets",
            "seaborn"
        ]
        
        # Use pip to install
        for package in packages:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    check=True,
                    capture_output=True,
                    text=True
                )
                logger.info(f"Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to install {package}: {e.stderr}")
                # Continue with other packages
        
        return True
        
    except Exception as e:
        logger.error(f"Error installing required libraries: {e}")
        return False

def copy_notebook_to_containers():
    """Copy the self-model visualization notebook to container directories."""
    try:
        # Source notebook
        source_notebook = os.path.join(parent_dir, 'notebooks', 'self_model_visualization.ipynb')
        
        # Destination directories
        destinations = [
            os.path.join(parent_dir, 'terminal_1', 'notebooks'),
            os.path.join(parent_dir, 'terminal_2', 'notebooks')
        ]
        
        # Create destination directories if they don't exist
        for dest_dir in destinations:
            os.makedirs(dest_dir, exist_ok=True)
            
            # Copy the notebook
            dest_file = os.path.join(dest_dir, 'self_model_visualization.ipynb')
            shutil.copy2(source_notebook, dest_file)
            logger.info(f"Copied visualization notebook to {dest_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error copying visualization notebook: {e}")
        return False

def configure_framework_startup():
    """Create a configuration file for auto-starting frameworks on container startup."""
    try:
        # Create configuration directory if it doesn't exist
        config_dir = os.path.join(parent_dir, 'system', 'ai_frameworks', 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        # Create configuration file
        config_file = os.path.join(config_dir, 'startup_config.json')
        
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
        
        # Create also the Python module to access this configuration
        config_module_path = os.path.join(config_dir, '__init__.py')
        with open(config_module_path, 'w') as f:
            f.write("""\"\"\"
Configuration module for AI frameworks.
\"\"\"

import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'startup_config.json')

def get_self_awareness_config():
    \"\"\"Get configuration for Self-Awareness Framework.\"\"\"
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        return config.get('frameworks', {}).get('self_awareness', {})
    except Exception as e:
        print(f"Error loading self-awareness config: {e}")
        return {}

def get_emotional_config():
    \"\"\"Get configuration for Emotional Dimensionality Framework.\"\"\"
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        return config.get('frameworks', {}).get('emotional_dimensionality', {})
    except Exception as e:
        print(f"Error loading emotional dimensionality config: {e}")
        return {}
""")
        
        logger.info(f"Created framework configuration module at {config_module_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error configuring framework startup: {e}")
        return False

def parse_arguments():
    """Parse command line arguments for the deployment script."""
    parser = argparse.ArgumentParser(description='Deploy AI Frameworks')
    
    parser.add_argument('--container', '-c', choices=['terminal_1', 'terminal_2', 'all'], 
                        default='all', help='Container to deploy to')
    parser.add_argument('--self-awareness', '-s', action='store_true', 
                       help='Deploy Self-Awareness Framework')
    parser.add_argument('--emotional', '-e', action='store_true',
                       help='Deploy Emotional Dimensionality Framework')
    parser.add_argument('--update-scripts', '-u', action='store_true',
                       help='Update runtime scripts')
    parser.add_argument('--install-libs', '-i', action='store_true',
                       help='Install required libraries')
    parser.add_argument('--all', '-a', action='store_true',
                       help='Perform all deployment steps')
    
    args = parser.parse_args()
    
    # If no specific action is selected, do all
    if not any([args.self_awareness, args.emotional, args.update_scripts, args.install_libs]):
        args.all = True
        
    return args

def main():
    """Main entry point for deployment script."""
    args = parse_arguments()
    
    logger.info("Starting AI Frameworks deployment")
    
    # Create necessary directories
    create_directories()
    
    # Determine which containers to deploy to
    containers = []
    if args.container == 'all':
        containers = ['terminal_1', 'terminal_2']
    else:
        containers = [args.container]
    
    # Install required libraries if needed
    if args.all or args.install_libs:
        install_required_libraries()
    
    # Configure framework startup
    configure_framework_startup()
    
    # Deploy frameworks to each container
    for container in containers:
        if args.all or args.self_awareness:
            if deploy_self_awareness_framework(container):
                logger.info(f"Self-Awareness Framework successfully deployed to {container}")
            else:
                logger.error(f"Failed to deploy Self-Awareness Framework to {container}")
        
        if args.all or args.emotional:
            if deploy_emotional_framework(container):
                logger.info(f"Emotional Dimensionality Framework successfully deployed to {container}")
            else:
                logger.error(f"Failed to deploy Emotional Dimensionality Framework to {container}")
    
    # Update runtime scripts if needed
    if args.all or args.update_scripts:
        if update_runtime_scripts():
            logger.info("Runtime scripts updated successfully")
        else:
            logger.error("Failed to update runtime scripts")
    
    # Copy visualization notebook
    copy_notebook_to_containers()
    
    logger.info("AI Frameworks deployment completed")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

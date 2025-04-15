#!/usr/bin/env python3
"""
Self-Awareness Framework Deployment Utilities

This module provides utilities for deploying, configuring, and managing
instances of the Self-Awareness Framework. It handles setup of directory
structures, initialization, configuration management, and integration
with other systems.

These utilities make it easy to:
- Deploy the framework in various environments
- Monitor framework instances
- Manage self-models and knowledge repositories
- Integrate with other systems and frameworks
"""

import argparse
import json
import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union, Callable

# Import the self-awareness framework
try:
    from self_awareness import (
        SelfAwarenessFramework, 
        AwarenessDimension, 
        get_default_config
    )
    FRAMEWORK_AVAILABLE = True
except ImportError:
    FRAMEWORK_AVAILABLE = False
    print("Warning: Self-Awareness Framework not found. Limited functionality available.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('deployment.log')
    ]
)
logger = logging.getLogger("self-awareness-deployment")


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
            self.base_path / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {directory}")
    
    def create_deployment(self, 
                         deployment_id: str, 
                         config: Optional[Dict] = None,
                         auto_start: bool = True) -> Optional[str]:
        """Create a new framework deployment.
        
        Args:
            deployment_id: Unique identifier for this deployment
            config: Configuration dictionary (or None for defaults)
            auto_start: Whether to start the framework after creation
            
        Returns:
            Path to the deployment configuration file, or None if failed
        """
        if not FRAMEWORK_AVAILABLE:
            logger.error("Cannot create deployment: Self-Awareness Framework not available")
            return None
        
        # Don't allow duplicate deployments
        if deployment_id in self.deployment_configs:
            logger.error(f"Deployment '{deployment_id}' already exists")
            return None
        
        # Create deployment-specific directories
        deployment_dir = self.base_path / deployment_id
        data_dir = deployment_dir / "data"
        logs_dir = deployment_dir / "logs"
        
        for directory in [deployment_dir, data_dir, logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Prepare configuration
        deployment_config = get_default_config()
        if config:
            deployment_config.update(config)
        
        # Add deployment-specific settings
        deployment_config.update({
            'id': f"self-aware-{deployment_id}",
            'deployment_id': deployment_id,
            'data_path': str(data_dir),
            'created_at': datetime.now().isoformat(),
            'deployment_path': str(deployment_dir)
        })
        
        # Save configuration
        config_path = self.base_path / "configs" / f"{deployment_id}_config.json"
        with open(config_path, 'w') as f:
            json.dump(deployment_config, f, indent=2)
        
        # Store the deployment configuration
        self.deployment_configs[deployment_id] = {
            'config': deployment_config,
            'path': str(deployment_dir),
            'config_path': str(config_path),
            'active': False
        }
        
        logger.info(f"Created deployment '{deployment_id}' at {deployment_dir}")
        
        # Start the framework if requested
        if auto_start:
            self.start_deployment(deployment_id)
        
        return str(config_path)
    
    def start_deployment(self, deployment_id: str) -> bool:
        """Start a framework deployment.
        
        Args:
            deployment_id: Identifier for the deployment to start
            
        Returns:
            True if successful, False otherwise
        """
        if not FRAMEWORK_AVAILABLE:
            logger.error("Cannot start deployment: Self-Awareness Framework not available")
            return False
        
        if deployment_id not in self.deployment_configs:
            logger.error(f"Deployment '{deployment_id}' not found")
            return False
        
        if deployment_id in self.framework_instances:
            logger.warning(f"Deployment '{deployment_id}' already running")
            return True
        
        # Get the deployment configuration
        deployment_data = self.deployment_configs[deployment_id]
        config = deployment_data['config']
        
        try:
            # Initialize the framework
            framework = SelfAwarenessFramework(config)
            
            # Start the framework
            framework.start()
            
            # Register basic capabilities
            self._register_standard_capabilities(framework)
            
            # Store the framework instance
            self.framework_instances[deployment_id] = framework
            
            # Update deployment status
            self.deployment_configs[deployment_id]['active'] = True
            self.deployment_configs[deployment_id]['started_at'] = datetime.now().isoformat()
            
            logger.info(f"Started deployment '{deployment_id}'")
            return True
            
        except Exception as e:
            logger.error(f"Error starting deployment '{deployment_id}': {e}")
            return False
    
    def stop_deployment(self, deployment_id: str) -> bool:
        """Stop a framework deployment.
        
        Args:
            deployment_id: Identifier for the deployment to stop
            
        Returns:
            True if successful, False otherwise
        """
        if deployment_id not in self.framework_instances:
            logger.error(f"Deployment '{deployment_id}' not running")
            return False
        
        try:
            # Get the framework instance
            framework = self.framework_instances[deployment_id]
            
            # Stop the framework
            framework.stop()
            
            # Save the self-model
            self._save_deployment_model(deployment_id)
            
            # Remove the framework instance
            del self.framework_instances[deployment_id]
            
            # Update deployment status
            self.deployment_configs[deployment_id]['active'] = False
            self.deployment_configs[deployment_id]['stopped_at'] = datetime.now().isoformat()
            
            logger.info(f"Stopped deployment '{deployment_id}'")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping deployment '{deployment_id}': {e}")
            return False
    
    def _save_deployment_model(self, deployment_id: str) -> Optional[str]:
        """Save the self-model for a deployment.
        
        Args:
            deployment_id: Identifier for the deployment
            
        Returns:
            Path to the saved model file, or None if failed
        """
        if deployment_id not in self.framework_instances:
            return None
        
        try:
            # Get the framework instance
            framework = self.framework_instances[deployment_id]
            
            # Generate a filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            models_dir = self.base_path / "models"
            filepath = models_dir / f"{deployment_id}_model_{timestamp}.json"
            
            # Save the self-model
            saved_path = framework.save_self_model(str(filepath))
            
            return saved_path
            
        except Exception as e:
            logger.error(f"Error saving model for deployment '{deployment_id}': {e}")
            return None
    
    def delete_deployment(self, deployment_id: str, keep_data: bool = True) -> bool:
        """Delete a framework deployment.
        
        Args:
            deployment_id: Identifier for the deployment to delete
            keep_data: Whether to keep the deployment data
            
        Returns:
            True if successful, False otherwise
        """
        if deployment_id not in self.deployment_configs:
            logger.error(f"Deployment '{deployment_id}' not found")
            return False
        
        # Stop the deployment if it's running
        if deployment_id in self.framework_instances:
            self.stop_deployment(deployment_id)
        
        # Remove deployment files
        deployment_dir = Path(self.deployment_configs[deployment_id]['path'])
        config_path = Path(self.deployment_configs[deployment_id]['config_path'])
        
        try:
            # Remove config file
            if config_path.exists():
                config_path.unlink()
            
            # Remove deployment directory if not keeping data
            if not keep_data and deployment_dir.exists():
                shutil.rmtree(deployment_dir)
            
            # Remove from tracking
            del self.deployment_configs[deployment_id]
            
            logger.info(f"Deleted deployment '{deployment_id}'")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting deployment '{deployment_id}': {e}")
            return False
    
    def _register_standard_capabilities(self, framework: SelfAwarenessFramework):
        """Register standard capabilities for the framework.
        
        Args:
            framework: Framework instance to configure
        """
        # The framework already registers some basic capabilities in its start() method,
        # but we can add more specialized ones here
        
        framework.capability_assessment.register_capability(
            'self_improvement',
            'Ability to improve own performance based on experience',
            {'cpu': 0.2, 'memory': 200 * 1024 * 1024}  # 200MB
        )
        
        framework.capability_assessment.register_capability(
            'error_detection',
            'Ability to detect errors in own operation',
            {'cpu': 0.1, 'memory': 50 * 1024 * 1024}  # 50MB
        )
        
        framework.capability_assessment.register_capability(
            'anomaly_detection',
            'Ability to detect anomalies in environment or input',
            {'cpu': 0.15, 'memory': 100 * 1024 * 1024}  # 100MB
        )
        
        # Set initial performance values
        framework.capability_assessment.update_capability_performance(
            'self_improvement', 0.6, 0.7)
        framework.capability_assessment.update_capability_performance(
            'error_detection', 0.75, 0.8)
        framework.capability_assessment.update_capability_performance(
            'anomaly_detection', 0.7, 0.75)
    
    def get_deployment_status(self, deployment_id: str = None) -> Dict:
        """Get status information for deployments.
        
        Args:
            deployment_id: Specific deployment to query, or None for all
            
        Returns:
            Dictionary with deployment status information
        """
        if deployment_id:
            # Return status for a specific deployment
            if deployment_id not in self.deployment_configs:
                return {"error": f"Deployment '{deployment_id}' not found"}
            
            status = self.deployment_configs[deployment_id].copy()
            
            # Add current state if active
            if deployment_id in self.framework_instances:
                framework = self.framework_instances[deployment_id]
                status['self_model'] = framework.get_self_model()
            
            return status
        else:
            # Return summary status for all deployments
            return {
                'total_deployments': len(self.deployment_configs),
                'active_deployments': len(self.framework_instances),
                'deployments': {
                    id: {
                        'active': id in self.framework_instances,
                        'path': data['path'],
                        'created_at': data['config'].get('created_at')
                    }
                    for id, data in self.deployment_configs.items()
                }
            }
    
    def update_all_metrics(self, dimension: AwarenessDimension, value: float):
        """Update a specific metric for all active deployments.
        
        Args:
            dimension: Awareness dimension to update
            value: New value for the metric
        """
        for deployment_id, framework in self.framework_instances.items():
            framework.metrics.update(dimension, value)
            logger.debug(f"Updated {dimension.value} metric to {value} for '{deployment_id}'")


class IntegrationManager:
    """Manages integration between the Self-Awareness Framework and other systems."""
    
    def __init__(self, deployment_manager: Optional[DeploymentManager] = None):
        """Initialize the integration manager.
        
        Args:
            deployment_manager: DeploymentManager instance to integrate with
        """
        self.deployment_manager = deployment_manager or DeploymentManager()
        self.integrations = {}
        self.integration_configs = {}
        self.integration_status = {}
    
    def register_integration(self, 
                           integration_id: str, 
                           target_system: str,
                           config: Dict) -> bool:
        """Register an integration with another system.
        
        Args:
            integration_id: Unique identifier for the integration
            target_system: Type or name of the target system
            config: Configuration for the integration
            
        Returns:
            True if successful, False otherwise
        """
        if integration_id in self.integrations:
            logger.warning(f"Integration '{integration_id}' already exists, updating config")
        
        self.integration_configs[integration_id] = {
            'target_system': target_system,
            'config': config,
            'created_at': datetime.now().isoformat()
        }
        
        # Initialize integration status
        self.integration_status[integration_id] = {
            'active': False,
            'last_updated': datetime.now().isoformat(),
            'status': 'registered',
            'messages': []
        }
        
        logger.info(f"Registered integration '{integration_id}' with {target_system}")
        return True
    
    def setup_integration(self, 
                         integration_id: str, 
                         deployment_id: str) -> bool:
        """Set up an integration between a framework deployment and another system.
        
        Args:
            integration_id: Identifier for the integration config to use
            deployment_id: Identifier for the deployment to integrate
            
        Returns:
            True if successful, False otherwise
        """
        if integration_id not in self.integration_configs:
            logger.error(f"Integration '{integration_id}' not found")
            return False
        
        if deployment_id not in self.deployment_manager.deployment_configs:
            logger.error(f"Deployment '{deployment_id}' not found")
            return False
        
        integration_config = self.integration_configs[integration_id]
        target_system = integration_config['target_system']
        
        # Depending on the target system, create appropriate integration
        try:
            if target_system == 'monitoring':
                integration = self._setup_monitoring_integration(
                    deployment_id, integration_config['config'])
            elif target_system == 'database':
                integration = self._setup_database_integration(
                    deployment_id, integration_config['config'])
            elif target_system == 'message_queue':
                integration = self._setup_message_queue_integration(
                    deployment_id, integration_config['config'])
            elif target_system == 'api':
                integration = self._setup_api_integration(
                    deployment_id, integration_config['config'])
            else:
                logger.error(f"Unsupported target system: {target_system}")
                return False
            
            # Store the integration
            self.integrations[integration_id] = integration
            
            # Update integration status
            self.integration_status[integration_id]['active'] = True
            self.integration_status[integration_id]['status'] = 'active'
            self.integration_status[integration_id]['deployment_id'] = deployment_id
            self.integration_status[integration_id]['last_updated'] = datetime.now().isoformat()
            
            logger.info(f"Integration '{integration_id}' set up for deployment '{deployment_id}'")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up integration '{integration_id}': {e}")
            # Update integration status with error
            self.integration_status[integration_id]['status'] = 'error'
            self.integration_status[integration_id]['error'] = str(e)
            self.integration_status[integration_id]['last_updated'] = datetime.now().isoformat()
            return False
    
    def _setup_monitoring_integration(self, deployment_id: str, config: Dict) -> Dict:
        """Set up integration with a monitoring system.
        
        Args:
            deployment_id: Identifier for the deployment
            config: Configuration for the integration
            
        Returns:
            Integration object
        """
        # Get the framework instance
        framework = self.deployment_manager.framework_instances.get(deployment_id)
        if not framework:
            raise ValueError(f"Deployment '{deployment_id}' not active")
        
        # Create monitoring integration
        monitoring_type = config.get('type', 'prometheus')
        endpoint = config.get('endpoint', 'http://localhost:9090/metrics')
        
        if monitoring_type == 'prometheus':
            # Import prometheus client only when needed
            try:
                import prometheus_client
                from prometheus_client import Counter, Gauge, Histogram, Summary
                
                # Create registry for metrics
                registry = prometheus_client.CollectorRegistry()
                
                # Create metrics
                metrics = {
                    'confidence': Gauge('self_awareness_confidence', 
                                      'System confidence', registry=registry),
                    'capability_score': Gauge('self_awareness_capability_score', 
                                            'Overall capability score', registry=registry),
                    'knowledge_boundaries': Gauge('self_awareness_knowledge_boundaries', 
                                                'Number of knowledge boundaries', registry=registry),
                    'memory_usage': Gauge('self_awareness_memory_usage', 
                                        'Memory usage in percent', registry=registry),
                    'cpu_usage': Gauge('self_awareness_cpu_usage', 
                                     'CPU usage in percent', registry=registry)
                }
                
                # Create metrics for each awareness dimension
                for dim in AwarenessDimension:
                    metrics[f'dimension_{dim.value}'] = Gauge(
                        f'self_awareness_dimension_{dim.value}',
                        f'{dim.value.capitalize()} awareness dimension score',
                        registry=registry
                    )
                
                # Start metrics HTTP server if configured
                if config.get('start_http_server', False):
                    port = config.get('port', 8000)
                    prometheus_client.start_http_server(port, registry=registry)
                    logger.info(f"Started Prometheus metrics server on port {port}")
                
                # Register update callback
                def update_metrics(state):
                    # Update basic metrics
                    metrics['memory_usage'].set(state.get('memory_percent', 0))
                    metrics['cpu_usage'].set(state.get('cpu_percent', 0))
                    
                    # Get self-model for more metrics
                    self_model = framework.get_self_model()
                    metrics['confidence'].set(self_model.get('confidence', 0))
                    metrics['knowledge_boundaries'].set(
                        len(self_model.get('knowledge_boundaries', [])))
                    
                    # Update dimension metrics
                    for dim in AwarenessDimension:
                        metrics[f'dimension_{dim.value}'].set(
                            framework.metrics.get_dimension_score(dim))
                
                # Register with state monitoring
                framework.state_monitoring.register_callback(update_metrics)
                
                return {
                    'type': 'prometheus',
                    'registry': registry,
                    'metrics': metrics,
                    'endpoint': endpoint,
                    'callback': update_metrics
                }
                
            except ImportError:
                logger.error("Prometheus client not installed. Run 'pip install prometheus_client'")
                raise ImportError("prometheus_client module required for Prometheus integration")
        else:
            raise ValueError(f"Unsupported monitoring type: {monitoring_type}")
    
    def _setup_database_integration(self, deployment_id: str, config: Dict) -> Dict:
        """Set up integration with a database system.
        
        Args:
            deployment_id: Identifier for the deployment
            config: Configuration for the integration
            
        Returns:
            Integration object
        """
        # Implementation for database integration
        # For now, return a placeholder integration
        return {
            'type': 'database',
            'config': config,
            'deployment_id': deployment_id,
            'enabled': True
        }
    
    def _setup_message_queue_integration(self, deployment_id: str, config: Dict) -> Dict:
        """Set up integration with a message queue system.
        
        Args:
            deployment_id: Identifier for the deployment
            config: Configuration for the integration
            
        Returns:
            Integration object
        """
        # Implementation for message queue integration
        # For now, return a placeholder integration
        return {
            'type': 'message_queue',
            'config': config,
            'deployment_id': deployment_id,
            'enabled': True
        }
    
    def _setup_api_integration(self, deployment_id: str, config: Dict) -> Dict:
        """Set up integration with an API.
        
        Args:
            deployment_id: Identifier for the deployment
            config: Configuration for the integration
            
        Returns:
            Integration object
        """
        # Implementation for API integration
        # For now, return a placeholder integration
        return {
            'type': 'api',
            'config': config,
            'deployment_id': deployment_id,
            'enabled': True
        }
    
    def stop_integration(self, integration_id: str) -> bool:
        """Stop an active integration.
        
        Args:
            integration_id: Identifier for the integration to stop
            
        Returns:
            True if successful, False otherwise
        """
        if integration_id not in self.integrations:
            logger.error(f"Integration '{integration_id}' not active")
            return False
        
        try:
            integration = self.integrations[integration_id]
            
            # Stop the integration based on type
            if integration['type'] == 'prometheus':
                # Unregister the callback from framework
                deployment_id = self.integration_status[integration_id]['deployment_id']
                framework = self.deployment_manager.framework_instances.get(deployment_id)
                if framework:
                    framework.state_monitoring.unregister_callback(integration['callback'])
            
            # Remove from active integrations
            del self.integrations[integration_id]
            
            # Update status
            self.integration_status[integration_id]['active'] = False
            self.integration_status[integration_id]['status'] = 'stopped'
            self.integration_status[integration_id]['last_updated'] = datetime.now().isoformat()
            
            logger.info(f"Integration '{integration_id}' stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping integration '{integration_id}': {e}")
            return False
    
    def get_integration_status(self, integration_id: str = None) -> Dict:
        """Get status information for integrations.
        
        Args:
            integration_id: Specific integration to query, or None for all
            
        Returns:
            Dictionary with integration status information
        """
        if integration_id:
            # Return status for a specific integration
            if integration_id not in self.integration_status:
                return {"error": f"Integration '{integration_id}' not found"}
            
            return self.integration_status[integration_id]
        else:
            # Return summary status for all integrations
            return {
                'total_integrations': len(self.integration_configs),
                'active_integrations': len(self.integrations),
                'integrations': self.integration_status
            }


class EnvironmentSetup:
    """Sets up the environment for the Self-Awareness Framework."""
    
    def __init__(self, base_path: Union[str, Path] = None):
        """Initialize the environment setup.
        
        Args:
            base_path: Base directory for the environment
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.dependencies_checked = False
        self.setup_complete = False
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed.
        
        Returns:
            True if all dependencies are met, False otherwise
        """
        required_packages = [
            'numpy',
            'psutil',
            'matplotlib',
            'requests'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.warning(f"Missing dependencies: {', '.join(missing_packages)}")
            return False
        
        logger.info("All required dependencies are installed")
        self.dependencies_checked = True
        return True
    
    def install_dependencies(self, missing_only: bool = True) -> bool:
        """Install required dependencies.
        
        Args:
            missing_only: Only install missing dependencies
            
        Returns:
            True if successful, False otherwise
        """
        if missing_only and not self.dependencies_checked:
            self.check_dependencies()
        
        try:
            import pip
            
            packages_to_install = [
                'numpy',
                'psutil>=5.8.0',
                'matplotlib>=3.3.0',
                'requests>=2.25.0'
            ]
            
            logger.info(f"Installing dependencies: {', '.join(packages_to_install)}")
            
            # Use pip to install packages
            for package in packages_to_install:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', package],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    logger.error(f"Failed to install {package}: {result.stderr}")
                    return False
                
                logger.debug(f"Installed {package}")
            
            logger.info("All dependencies installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error installing dependencies: {e}")
            return False
    
    def setup_environment(self, 
                         deployment_id: str = 'default',
                         monitoring: bool = True,
                         integration: bool = True) -> bool:
        """Set up the complete environment.
        
        Args:
            deployment_id: Identifier for the default deployment
            monitoring: Whether to set up monitoring
            integration: Whether to set up integrations
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("Setting up Self-Awareness Framework environment")
        
        # Check/install dependencies
        if not self.dependencies_checked and not self.check_dependencies():
            logger.info("Installing missing dependencies")
            if not self.install_dependencies():
                logger.error("Failed to install dependencies")
                return False
        
        # Create required directories
        try:
            directories = [
                'data',
                'logs',
                'configs',
                'models',
                'integrations'
            ]
            
            for directory in directories:
                dir_path = self.base_path / directory
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created directory: {dir_path}")
            
            # Create deployment manager
            deployment_manager = DeploymentManager(self.base_path / 'deployments')
            
            # Create default deployment
            deployment_manager.create_deployment(deployment_id)
            
            if monitoring:
                # Set up monitoring integration
                integration_manager = IntegrationManager(deployment_manager)
                integration_manager.register_integration(
                    'monitoring',
                    'monitoring',
                    {'type': 'prometheus', 'start_http_server': True, 'port': 8000}
                )
                integration_manager.setup_integration('monitoring', deployment_id)
            
            self.setup_complete = True
            logger.info("Environment setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up environment: {e}")
            return False


def setup_deployment_environment(args: Dict) -> bool:
    """Set up the deployment environment based on CLI arguments.
    
    Args:
        args: Dictionary containing setup arguments
        
    Returns:
        True if successful, False otherwise
    """
    base_path = args.get('base_path')
    env_setup = EnvironmentSetup(base_path)
    
    # Check if dependencies need to be installed
    if args.get('install_deps', False):
        if not env_setup.install_dependencies(not args.get('force_deps', False)):
            logger.error("Failed to install dependencies")
            return False
    
    # Set up the environment
    return env_setup.setup_environment(
        deployment_id=args.get('deployment_id', 'default'),
        monitoring=args.get('monitoring', True),
        integration=args.get('integration', True)
    )


def run_deployment(args: Dict) -> bool:
    """Run a framework deployment based on CLI arguments.
    
    Args:
        args: Dictionary containing run arguments
        
    Returns:
        True if successful, False otherwise
    """
    base_path = args.get('base_path')
    deployment_id = args.get('deployment_id')
    config_path = args.get('config')
    
    deployment_manager = DeploymentManager(base_path)
    
    # Load custom configuration if specified
    config = None
    if config_path:
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False
    
    # Create and start deployment
    if not deployment_manager.create_deployment(deployment_id, config):
        logger.error(f"Failed to create deployment '{deployment_id}'")
        return False
    
    try:
        # Run until interrupted
        logger.info(f"Deployment '{deployment_id}' running. Press Ctrl+C to stop.")
        
        while True:
            time.sleep(1)
            
            # Periodically save the self-model
            if args.get('save_interval'):
                # Implementation for periodic saving would go here
                pass
                
    except KeyboardInterrupt:
        logger.info("Stopping deployment due to keyboard interrupt")
        deployment_manager.stop_deployment(deployment_id)
    
    return True


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Self-Awareness Framework Deployment Utilities",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Global options
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose output")
    parser.add_argument("--base-path", type=str, default=None,
                       help="Base directory for deployments")
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up deployment environment")
    setup_parser.add_argument("--install-deps", action="store_true",
                             help="Install required dependencies")
    setup_parser.add_argument("--force-deps", action="store_true",
                             help="Force reinstallation of dependencies")
    setup_parser.add_argument("--deployment-id", type=str, default="default",
                             help="Identifier for default deployment")
    setup_parser.add_argument("--no-monitoring", action="store_true",
                             help="Disable monitoring setup")
    setup_parser.add_argument("--no-integration", action="store_true",
                             help="Disable integration setup")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run a framework deployment")
    run_parser.add_argument("deployment_id", type=str,
                           help="Identifier for the deployment")
    run_parser.add_argument("--config", type=str,
                           help="Path to configuration file")
    run_parser.add_argument("--save-interval", type=int, default=300,
                           help="Interval between auto-saving self-models (seconds)")
    
    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a running deployment")
    stop_parser.add_argument("deployment_id", type=str,
                            help="Identifier for the deployment to stop")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Get deployment status")
    status_parser.add_argument("--deployment-id", type=str,
                              help="Identifier for a specific deployment (optional)")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a deployment")
    delete_parser.add_argument("deployment_id", type=str,
                             help="Identifier for the deployment to delete")
    delete_parser.add_argument("--keep-data", action="store_true", default=True,
                             help="Keep deployment data (default)")
    delete_parser.add_argument("--remove-data", action="store_true",
                             help="Remove all deployment data")
    
    return parser.parse_args()


def main():
    """Main entry point for deployment utilities."""
    args = parse_arguments()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Execute command
    if args.command == "setup":
        setup_args = vars(args)
        # Convert "no_" arguments to their positive form
        setup_args['monitoring'] = not args.no_monitoring
        setup_args['integration'] = not args.no_integration
        setup_deployment_environment(setup_args)
    
    elif args.command == "run":
        run_args = vars(args)
        run_deployment(run_args)
    
    elif args.command == "stop":
        deployment_manager = DeploymentManager(args.base_path)
        deployment_manager.stop_deployment(args.deployment_id)
    
    elif args.command == "status":
        deployment_manager = DeploymentManager(args.base_path)
        status = deployment_manager.get_deployment_status(args.deployment_id)
        print(json.dumps(status, indent=2))
    
    elif args.command == "delete":
        deployment_manager = DeploymentManager(args.base_path)
        # If --remove-data is specified, don't keep data
        keep_data = args.keep_data and not args.remove_data
        deployment_manager.delete_deployment(args.deployment_id, keep_data)
    
    else:
        # No command or invalid command
        print("Please specify a valid command. Use --help for options.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

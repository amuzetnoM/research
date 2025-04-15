"""
Configuration class for the API.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Config:
    """
    Configuration class for the API that manages settings with both
    environment variables and file-based configuration.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to a JSON configuration file (optional)
        """
        # API settings
        self.API_KEY = os.environ.get('API_KEY', 'development_key')
        self.ADMIN_ROLE = os.environ.get('ADMIN_ROLE', 'admin')
        
        # SSL settings
        self.USE_SSL = os.environ.get('USE_SSL', 'False').lower() == 'true'
        self.SSL_CERT = os.environ.get('SSL_CERT', 'certs/server.crt')
        self.SSL_KEY = os.environ.get('SSL_KEY', 'certs/server.key')
        
        # Framework enablement
        self.ENABLE_SELF_AWARENESS = os.environ.get('ENABLE_SELF_AWARENESS', 'True').lower() == 'true'
        self.ENABLE_USIF = os.environ.get('ENABLE_USIF', 'True').lower() == 'true'
        self.ENABLE_PUP = os.environ.get('ENABLE_PUP', 'True').lower() == 'true'
        
        # Framework connection settings
        self.SELF_AWARENESS_HOST = os.environ.get('SELF_AWARENESS_HOST', 'localhost')
        self.SELF_AWARENESS_PORT = int(os.environ.get('SELF_AWARENESS_PORT', '8765'))
        
        self.USIF_HOST = os.environ.get('USIF_HOST', 'localhost')
        self.USIF_PORT = int(os.environ.get('USIF_PORT', '8766'))
        
        self.PUP_HOST = os.environ.get('PUP_HOST', 'localhost')
        self.PUP_PORT = int(os.environ.get('PUP_PORT', '8767'))
        
        # Load from file if provided
        if config_file:
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file: str) -> bool:
        """
        Load configuration from a JSON file.
        
        Args:
            config_file: Path to a JSON configuration file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Update config with file values
            for key, value in config_data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            
            logger.info(f"Configuration loaded from {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_file}: {e}")
            return False
    
    def save_to_file(self, config_file: str) -> bool:
        """
        Save configuration to a JSON file.
        
        Args:
            config_file: Path to save the configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(config_file, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            
            logger.info(f"Configuration saved to {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {config_file}: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to a dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            'API_KEY': self.API_KEY,
            'ADMIN_ROLE': self.ADMIN_ROLE,
            'USE_SSL': self.USE_SSL,
            'SSL_CERT': self.SSL_CERT,
            'SSL_KEY': self.SSL_KEY,
            'ENABLE_SELF_AWARENESS': self.ENABLE_SELF_AWARENESS,
            'ENABLE_USIF': self.ENABLE_USIF,
            'ENABLE_PUP': self.ENABLE_PUP,
            'SELF_AWARENESS_HOST': self.SELF_AWARENESS_HOST,
            'SELF_AWARENESS_PORT': self.SELF_AWARENESS_PORT,
            'USIF_HOST': self.USIF_HOST,
            'USIF_PORT': self.USIF_PORT,
            'PUP_HOST': self.PUP_HOST,
            'PUP_PORT': self.PUP_PORT
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """
        Create a configuration from a dictionary.
        
        Args:
            data: Dictionary with configuration values
            
        Returns:
            Config instance
        """
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config

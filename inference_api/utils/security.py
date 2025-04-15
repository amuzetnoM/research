"""
Security utilities for the API.
"""

import os
import logging
import ssl
from typing import Optional, Tuple, Union
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

def get_ssl_context(cert_file: str, key_file: str) -> Union[ssl.SSLContext, None]:
    """
    Create an SSL context for the API.
    
    Args:
        cert_file: Path to the SSL certificate file
        key_file: Path to the SSL key file
        
    Returns:
        SSLContext if successful, None otherwise
    """
    try:
        if not os.path.exists(cert_file) or not os.path.exists(key_file):
            logger.warning(f"SSL certificate or key not found: {cert_file}, {key_file}")
            return None
        
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        logger.info("SSL context created successfully")
        return context
        
    except Exception as e:
        logger.error(f"Failed to create SSL context: {e}")
        return None

def generate_self_signed_cert(cert_output: str, key_output: str, days: int = 365) -> bool:
    """
    Generate a self-signed SSL certificate for development.
    
    Args:
        cert_output: Path to save the certificate
        key_output: Path to save the private key
        days: Validity period in days
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure the output directories exist
        os.makedirs(os.path.dirname(cert_output), exist_ok=True)
        os.makedirs(os.path.dirname(key_output), exist_ok=True)
        
        # Generate a private key
        result = subprocess.run(
            ["openssl", "genrsa", "-out", key_output, "2048"],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Generate a self-signed certificate
        subject = "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        result = subprocess.run(
            [
                "openssl", "req", "-new", "-x509", "-key", key_output,
                "-out", cert_output, "-days", str(days), "-subj", subject
            ],
            check=True,
            capture_output=True,
            text=True
        )
        
        logger.info(f"Self-signed certificate generated at {cert_output}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate self-signed certificate: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error generating self-signed certificate: {e}")
        return False

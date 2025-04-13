"""
System Utilities

Provides system-level utility functions for the setup process.
"""

import logging
import os
import platform
import subprocess
import sys
import ctypes
import psutil

# Get logger
logger = logging.getLogger('setup')

def is_admin():
    """
    Check if the script is running with administrative privileges.
    
    Returns:
        bool: True if running as admin/root, False otherwise
    """
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception as e:
        logger.warning(f"Failed to check admin status: {e}")
        return False

def request_admin_permission():
    """
    Request administrative permissions from the user.
    This doesn't elevate privileges but asks if they want to continue without them.
    
    Returns:
        bool: True if user wants to continue, False otherwise
    """
    if is_admin():
        return True
    
    print("\nThis script may require administrative privileges for some operations.")
    print("You are currently NOT running with admin/root privileges.")
    
    while True:
        response = input("Do you want to continue anyway? [y/n]: ").lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'.")

def get_system_info():
    """
    Get system information.
    
    Returns:
        dict: System information
    """
    info = {
        'os': platform.system(),
        'os_version': platform.version(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(logical=False),
        'cpu_logical_count': psutil.cpu_count(logical=True),
        'memory_total': psutil.virtual_memory().total,
        'disk_total': psutil.disk_usage('/').total,
    }
    
    try:
        if platform.system() == "Windows":
            info['architecture'] = platform.architecture()[0]
        else:
            info['architecture'] = subprocess.check_output(['uname', '-m']).decode().strip()
    except Exception as e:
        logger.warning(f"Failed to get architecture: {e}")
        info['architecture'] = platform.machine()
    
    return info

def check_command_exists(command):
    """
    Check if a command exists in the system PATH.
    
    Args:
        command (str): Command to check
        
    Returns:
        bool: True if command exists, False otherwise
    """
    try:
        subprocess.run(
            ["which" if platform.system() != "Windows" else "where", command],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.SubprocessError:
        return False

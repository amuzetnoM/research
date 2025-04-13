#!/usr/bin/env python3
"""
Python Pre-installation Script for AI Research Environment

This script automatically installs Python 3 and its dependencies without
user interaction. It can detect corrupted Python installations and repair them.
It supports Windows, macOS, and Linux platforms.

Usage:
    python _preinstall.py
    # or simply
    ./_preinstall.py

Features:
    - Cross-platform Python installation
    - Silent/unattended mode
    - Integrity validation
    - Auto-repair capabilities
    - Environment validation
"""

import os
import sys
import platform
import subprocess
import shutil
import tempfile
import hashlib
import urllib.request
import logging
import time
import zipfile
import tarfile
import re
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('python_install.log')
    ]
)
logger = logging.getLogger('python_installer')

# Default Python version to install
DEFAULT_PYTHON_VERSION = "3.9.13"  # Stable version with good compatibility

# Platform-specific constants
WINDOWS = platform.system() == "Windows"
MACOS = platform.system() == "Darwin"
LINUX = platform.system() == "Linux"

# Download URLs and verification hashes
PYTHON_DOWNLOADS = {
    "Windows": {
        "3.9.13": {
            "url": "https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe",
            "sha256": "fb3d0466f09f573a9080a37bf371ceeb89c3c7d84c9410fa4a7517bc2813ecc7",
            "install_args": ["/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0"]
        },
        "3.10.11": {
            "url": "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe",
            "sha256": "68ca4decbefbfb2ffedfafe4b573cc82ad4ad9c7084198620993443fb3bcb62b",
            "install_args": ["/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0"]
        }
    },
    "Darwin": {
        "3.9.13": {
            "url": "https://www.python.org/ftp/python/3.9.13/python-3.9.13-macos11.pkg",
            "sha256": "4a83042ddf6774c2b3533a42993a19c0c514929a2f6166bd3c4ddd4c6040d4a9",
            "install_args": []
        },
        "3.10.11": {
            "url": "https://www.python.org/ftp/python/3.10.11/python-3.10.11-macos11.pkg",
            "sha256": "7b1b8330470881e7d5f103e3a45033cf8e4e43421a42127c19db19ad1bda5095",
            "install_args": []
        }
    },
    "Linux": {
        # Linux typically uses package managers, no direct download needed
        "apt": ["python3", "python3-pip", "python3-venv", "python3-dev"],
        "yum": ["python3", "python3-pip", "python3-devel"],
        "dnf": ["python3", "python3-pip", "python3-devel"],
        "pacman": ["python", "python-pip"],
        "zypper": ["python3", "python3-pip", "python3-devel"]
    }
}

# Package manager detection commands
PACKAGE_MANAGERS = {
    "apt": "apt-get --version",
    "yum": "yum --version",
    "dnf": "dnf --version",
    "pacman": "pacman --version",
    "zypper": "zypper --version"
}

# Essential Python packages to install
ESSENTIAL_PACKAGES = [
    "pip",
    "setuptools",
    "wheel",
    "virtualenv",
    "pytest"
]

def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        if WINDOWS:
            try:
                # Check for admin privileges on Windows
                return subprocess.check_call(["net", "session"], 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE) == 0
            except:
                return False
        else:
            # Check for root on Unix-like systems
            return os.geteuid() == 0
    except:
        return False

def request_admin():
    """Request administrative privileges if not already running as admin."""
    if is_admin():
        return True
        
    logger.warning("This script requires administrative privileges")
    
    if WINDOWS:
        try:
            # Re-run the script with elevated privileges on Windows
            script_path = os.path.abspath(__file__)
            subprocess.run(["powershell", "Start-Process", "python", 
                         f'"{script_path}"', "-Verb", "RunAs"],
                         check=True)
            sys.exit(0)
        except:
            logger.error("Failed to elevate privileges")
            return False
    else:
        try:
            # Re-run with sudo on Unix-like systems
            script_path = os.path.abspath(__file__)
            subprocess.run(["sudo", "python3", script_path], check=True)
            sys.exit(0)
        except:
            logger.error("Failed to elevate privileges with sudo")
            return False
    
    return False

def download_file(url, target_path):
    """Download a file from URL to target path with progress reporting."""
    logger.info(f"Downloading {url} to {target_path}")
    
    try:
        with urllib.request.urlopen(url) as response, open(target_path, 'wb') as out_file:
            file_size = int(response.info().get('Content-Length', 0))
            downloaded = 0
            block_size = 1024 * 8
            
            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                    
                downloaded += len(buffer)
                out_file.write(buffer)
                
                # Calculate progress percentage
                if file_size > 0:
                    percent = int(downloaded * 100 / file_size)
                    sys.stdout.write(f"\rDownloading: {percent}% ({downloaded} / {file_size} bytes)")
                    sys.stdout.flush()
        
        sys.stdout.write("\n")
        logger.info("Download completed successfully")
        return True
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return False

def verify_checksum(file_path, expected_sha256):
    """Verify the SHA-256 checksum of a file."""
    logger.info(f"Verifying checksum of {file_path}")
    
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        actual_sha256 = sha256_hash.hexdigest()
        
        if actual_sha256 == expected_sha256:
            logger.info("Checksum verification successful")
            return True
        else:
            logger.error(f"Checksum verification failed. Expected: {expected_sha256}, Got: {actual_sha256}")
            return False
    except Exception as e:
        logger.error(f"Checksum verification error: {e}")
        return False

def detect_python():
    """Detect if Python is installed and working properly."""
    logger.info("Checking for Python installation")
    
    try:
        # Try to run Python and get its version
        python_exec = "python" if WINDOWS else "python3"
        result = subprocess.run(
            [python_exec, "-c", "import sys; print(sys.version)"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            version_string = result.stdout.strip()
            logger.info(f"Python is installed: {version_string}")
            
            # Parse version
            match = re.search(r'(\d+)\.(\d+)\.(\d+)', version_string)
            if match:
                major, minor, patch = map(int, match.groups())
                if major >= 3 and minor >= 8:
                    logger.info("Python version is sufficient (3.8+)")
                    return True, version_string
                else:
                    logger.warning(f"Python version {major}.{minor}.{patch} is too old")
                    return False, version_string
        
        logger.warning("Python is not installed or not working properly")
        return False, None
        
    except Exception as e:
        logger.error(f"Error detecting Python: {e}")
        return False, None

def install_python_windows(version=DEFAULT_PYTHON_VERSION):
    """Install Python on Windows."""
    logger.info(f"Installing Python {version} on Windows")
    
    python_info = PYTHON_DOWNLOADS["Windows"].get(version)
    if not python_info:
        logger.error(f"No download information for Python {version}")
        return False
    
    # Create a temporary directory for downloads
    with tempfile.TemporaryDirectory() as temp_dir:
        installer_path = os.path.join(temp_dir, f"python-{version}-installer.exe")
        
        # Download the installer
        if not download_file(python_info["url"], installer_path):
            return False
        
        # Verify the installer
        if not verify_checksum(installer_path, python_info["sha256"]):
            return False
        
        # Run the installer
        logger.info("Running Python installer...")
        try:
            process = subprocess.run(
                [installer_path] + python_info["install_args"],
                check=True
            )
            logger.info("Python installation completed successfully")
            
            # Update PATH environment variable to include Python without restarting
            update_windows_path()
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Python installation failed: {e}")
            return False

def update_windows_path():
    """Update Windows PATH environment variable without restarting."""
    logger.info("Updating Windows PATH environment variable")
    
    try:
        # Get the current PATH
        path = os.environ.get("PATH", "")
        
        # Get the Python installation directory from the registry
        python_path = None
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                            r"SOFTWARE\Python\PythonCore\3.9\InstallPath") as key:
                python_path = winreg.QueryValue(key, "")
        except:
            # Try default installation paths
            potential_paths = [
                os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Python39"),
                os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Python39"),
                os.path.join(os.environ.get("LocalAppData", "C:\\Users\\User\\AppData\\Local"), "Programs\\Python\\Python39")
            ]
            
            for p in potential_paths:
                if os.path.exists(p):
                    python_path = p
                    break
        
        if python_path and python_path not in path:
            # Add Python path and Scripts folder to PATH
            scripts_path = os.path.join(python_path, "Scripts")
            new_path = f"{python_path};{scripts_path};{path}"
            
            # Set the PATH for the current process
            os.environ["PATH"] = new_path
            
            # Try to set the PATH persistently using setx
            try:
                subprocess.run(["setx", "PATH", new_path], check=True)
                logger.info("Updated PATH environment variable permanently")
            except:
                logger.warning("Could not update PATH permanently. Changes will affect only this process.")
        
        return True
    except Exception as e:
        logger.error(f"Failed to update PATH: {e}")
        return False

def install_python_macos(version=DEFAULT_PYTHON_VERSION):
    """Install Python on macOS."""
    logger.info(f"Installing Python {version} on macOS")
    
    python_info = PYTHON_DOWNLOADS["Darwin"].get(version)
    if not python_info:
        logger.error(f"No download information for Python {version}")
        return False
    
    # Create a temporary directory for downloads
    with tempfile.TemporaryDirectory() as temp_dir:
        installer_path = os.path.join(temp_dir, f"python-{version}-installer.pkg")
        
        # Download the installer
        if not download_file(python_info["url"], installer_path):
            return False
        
        # Verify the installer
        if not verify_checksum(installer_path, python_info["sha256"]):
            return False
        
        # Run the installer
        logger.info("Running Python installer...")
        try:
            process = subprocess.run(
                ["installer", "-pkg", installer_path, "-target", "/"],
                check=True
            )
            logger.info("Python installation completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Python installation failed: {e}")
            return False

def detect_linux_package_manager():
    """Detect the Linux package manager."""
    logger.info("Detecting Linux package manager")
    
    for manager, command in PACKAGE_MANAGERS.items():
        try:
            result = subprocess.run(
                command.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            if result.returncode == 0:
                logger.info(f"Detected package manager: {manager}")
                return manager
        except:
            continue
    
    logger.error("Could not detect a supported package manager")
    return None

def install_python_linux():
    """Install Python on Linux using the appropriate package manager."""
    logger.info("Installing Python on Linux")
    
    # Detect package manager
    manager = detect_linux_package_manager()
    if not manager:
        return False
    
    packages = PYTHON_DOWNLOADS["Linux"].get(manager, [])
    if not packages:
        logger.error(f"No package information for {manager}")
        return False
    
    # Update package repositories
    logger.info(f"Updating {manager} package repositories")
    try:
        if manager == "apt":
            subprocess.run(["apt-get", "update", "-y"], check=True)
        elif manager == "yum" or manager == "dnf":
            subprocess.run([manager, "check-update", "-y"], check=False)
        elif manager == "pacman":
            subprocess.run(["pacman", "-Sy"], check=True)
        elif manager == "zypper":
            subprocess.run(["zypper", "refresh"], check=True)
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to update package repositories: {e}")
    
    # Install packages
    logger.info(f"Installing Python packages: {', '.join(packages)}")
    try:
        if manager == "apt":
            subprocess.run(["apt-get", "install", "-y"] + packages, check=True)
        elif manager in ["yum", "dnf"]:
            subprocess.run([manager, "install", "-y"] + packages, check=True)
        elif manager == "pacman":
            subprocess.run(["pacman", "-S", "--noconfirm"] + packages, check=True)
        elif manager == "zypper":
            subprocess.run(["zypper", "install", "-y"] + packages, check=True)
        
        logger.info("Python installation completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Python installation failed: {e}")
        return False

def install_python_automatically():
    """Install Python automatically based on detected platform."""
    logger.info("Starting automatic Python installation")
    
    if WINDOWS:
        return install_python_windows()
    elif MACOS:
        return install_python_macos()
    elif LINUX:
        return install_python_linux()
    else:
        logger.error(f"Unsupported platform: {platform.system()}")
        return False

def verify_pip():
    """Verify that pip is installed and working."""
    logger.info("Verifying pip installation")
    
    try:
        pip_command = "pip" if WINDOWS else "pip3"
        result = subprocess.run(
            [pip_command, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            logger.info(f"pip is installed: {result.stdout.strip()}")
            return True
        else:
            logger.warning("pip is not installed or not working properly")
            return False
    except Exception as e:
        logger.error(f"Error verifying pip: {e}")
        return False

def install_pip():
    """Install pip if not already installed."""
    logger.info("Installing pip")
    
    try:
        if WINDOWS:
            python_command = "python"
        else:
            python_command = "python3"
        
        # Download get-pip.py
        with tempfile.TemporaryDirectory() as temp_dir:
            get_pip_path = os.path.join(temp_dir, "get-pip.py")
            
            if not download_file("https://bootstrap.pypa.io/get-pip.py", get_pip_path):
                return False
            
            # Run get-pip.py
            subprocess.run([python_command, get_pip_path], check=True)
            
            logger.info("pip installation completed successfully")
            return True
    except Exception as e:
        logger.error(f"pip installation failed: {e}")
        return False

def install_essential_packages():
    """Install essential Python packages."""
    logger.info(f"Installing essential packages: {', '.join(ESSENTIAL_PACKAGES)}")
    
    try:
        pip_command = "pip" if WINDOWS else "pip3"
        subprocess.run(
            [pip_command, "install", "--upgrade"] + ESSENTIAL_PACKAGES,
            check=True
        )
        
        logger.info("Essential packages installed successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to install essential packages: {e}")
        return False

def verify_python_integrity():
    """Verify the integrity of the Python installation."""
    logger.info("Verifying Python installation integrity")
    
    try:
        python_command = "python" if WINDOWS else "python3"
        tests = [
            # Test basic Python functionality
            [python_command, "-c", "print('hello world')"],
            # Test import system
            [python_command, "-c", "import sys, os, json, urllib, logging"],
            # Test pip functionality
            [python_command, "-m", "pip", "--version"],
            # Test pip install
            [python_command, "-m", "pip", "install", "--upgrade", "pip"]
        ]
        
        for test in tests:
            logger.debug(f"Running verification test: {' '.join(test)}")
            result = subprocess.run(
                test,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"Verification test failed: {' '.join(test)}")
                return False
        
        logger.info("Python installation integrity verified")
        return True
    except Exception as e:
        logger.error(f"Verification test error: {e}")
        return False

def repair_python_installation():
    """Attempt to repair a corrupted Python installation."""
    logger.info("Attempting to repair Python installation")
    
    # Uninstall Python first (if possible)
    logger.info("Uninstalling existing Python installation")
    try:
        if WINDOWS:
            # Find Python in the installed programs list
            try:
                result = subprocess.run(
                    ["wmic", "product", "where", "name like '%Python%'", "get", "name,version"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                logger.info(f"Found Python installations: {result.stdout.strip()}")
                
                # Try to uninstall using the Python uninstaller
                uninstall_attempts = [
                    # Generic uninstaller path
                    r"C:\Program Files\Python39\Uninstall.exe",
                    # Other potential paths
                    r"C:\Program Files (x86)\Python39\Uninstall.exe",
                    r"C:\Python39\Uninstall.exe"
                ]
                
                for uninstaller in uninstall_attempts:
                    if os.path.exists(uninstaller):
                        logger.info(f"Found uninstaller at {uninstaller}")
                        subprocess.run([uninstaller, "/quiet"], check=False)
            except Exception as e:
                logger.warning(f"Error uninstalling Python: {e}")
        elif LINUX:
            # Linux uninstallation depends on the package manager
            manager = detect_linux_package_manager()
            if manager:
                packages = PYTHON_DOWNLOADS["Linux"].get(manager, [])
                if packages:
                    try:
                        if manager == "apt":
                            subprocess.run(["apt-get", "remove", "--purge", "-y"] + packages, check=False)
                        elif manager in ["yum", "dnf"]:
                            subprocess.run([manager, "remove", "-y"] + packages, check=False)
                        elif manager == "pacman":
                            subprocess.run(["pacman", "-R", "--noconfirm"] + packages, check=False)
                        elif manager == "zypper":
                            subprocess.run(["zypper", "remove", "-y"] + packages, check=False)
                    except Exception as e:
                        logger.warning(f"Error uninstalling Python: {e}")
        elif MACOS:
            # macOS uninstallation is more complex
            python_dirs = [
                "/Library/Frameworks/Python.framework",
                "/Applications/Python 3.*",
                "/usr/local/bin/python3*"
            ]
            
            for pattern in python_dirs:
                try:
                    for path in Path("/").glob(pattern.lstrip("/")):
                        if path.exists():
                            logger.info(f"Removing {path}")
                            if path.is_file() or path.is_symlink():
                                path.unlink()
                            else:
                                shutil.rmtree(path)
                except Exception as e:
                    logger.warning(f"Error removing {pattern}: {e}")
    except Exception as e:
        logger.warning(f"Failed to uninstall Python: {e}")
    
    # Install a fresh Python
    return install_python_automatically()

def main():
    """Main function to install and verify Python."""
    logger.info("Starting Python pre-installation script")
    
    # Check for administrative privileges
    if not is_admin():
        logger.warning("Script is not running with admin privileges")
        if not request_admin():
            logger.error("Cannot proceed without admin privileges")
            return 1
    
    # Check if Python is already installed and working
    python_installed, python_version = detect_python()
    
    if python_installed:
        logger.info("Python is already installed and working")
        
        # Verify Python integrity
        if verify_python_integrity():
            logger.info("Python installation is valid")
        else:
            logger.warning("Python installation appears to be corrupted")
            
            # Try to repair
            logger.info("Attempting to repair Python installation")
            if repair_python_installation():
                logger.info("Python repair successful")
            else:
                logger.error("Failed to repair Python installation")
                return 1
    else:
        # Install Python
        logger.info("Python is not installed or not working properly")
        if install_python_automatically():
            logger.info("Python installation successful")
        else:
            logger.error("Failed to install Python")
            return 1
    
    # Verify pip
    if not verify_pip():
        logger.info("pip is not installed or not working properly")
        if install_pip():
            logger.info("pip installation successful")
        else:
            logger.error("Failed to install pip")
            return 1
    
    # Install essential packages
    if install_essential_packages():
        logger.info("Essential packages installed successfully")
    else:
        logger.error("Failed to install essential packages")
        return 1
    
    # Final verification
    if verify_python_integrity():
        logger.info("Python environment is ready for use")
    else:
        logger.error("Python environment is not functioning correctly")
        return 1
    
    logger.info("Python pre-installation completed successfully")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

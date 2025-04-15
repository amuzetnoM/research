from setuptools import setup, find_packages

setup(
    name="self-awareness-framework",
    version="0.2.0",
    description="Self-Awareness Framework for AI Systems",
    author="Research Team",
    author_email="research@example.com",
    packages=find_packages(),
    install_requires=[
        # Core dependencies
        "numpy>=1.19.0",
        "pandas>=1.1.0", 
        "matplotlib>=3.3.0",
        "seaborn>=0.11.0",
        
        # Self-awareness framework dependencies
        "flask>=2.0.0",
        "psutil>=5.8.0",
        "requests>=2.25.1",
        "sseclient-py>=1.7.2",
        
        # Cognitive simulation dependencies
        "threading",  # Python standard library
        "logging",    # Python standard library
        "random",     # Python standard library
        "time",       # Python standard library
        "os",         # Python standard library
        "sys",        # Python standard library
        "json",       # Python standard library
        "datetime",   # Python standard library
        "gc",         # Python standard library
        
        # Additional utilities
        "scikit-learn>=0.24.0",
        "pytest>=6.2.5",
    ],
    extras_require={
        "dev": [
            "black>=21.5b2",
            "isort>=5.9.1",
            "flake8>=3.9.2",
            "mypy>=0.812",
        ],
        "gpu": [
            "torch>=1.9.0",
            "tensorflow>=2.5.0",
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)

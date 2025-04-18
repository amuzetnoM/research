"""
Setup script for the Probabilistic Uncertainty Principle (PUP) framework.
"""

import os
from setuptools import setup, find_packages

# Read the contents of README.md if it exists
this_directory = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(this_directory, 'README.md')
long_description = ''
if os.path.exists(readme_path):
    with open(readme_path, encoding='utf-8') as f:
        long_description = f.read()

setup(
    name="pup",
    version="0.1.0",
    author="Research Team",
    author_email="research@example.com",
    description="Probabilistic Uncertainty Principle Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/organization/pup",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "joblib>=1.0.0",
    ],
    extras_require={
        "torch": ["torch>=1.7.0"],
        "tensorflow": ["tensorflow>=2.4.0"],
        "dev": ["pytest>=7.0.0", "black>=22.1.0", "flake8>=4.0.0"],
        "visualization": ["matplotlib>=3.5.0", "seaborn>=0.11.0"],
    },
)
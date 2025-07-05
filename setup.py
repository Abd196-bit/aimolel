"""
Setup script for DieAI Knowledge Library
"""
from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read version from __init__.py
with open(os.path.join(this_directory, 'dieai_knowledge', '__init__.py'), 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"').strip("'")
            break

setup(
    name="dieai-knowledge",
    version=version,
    author="DieAI Team",
    author_email="info@dieai.com",
    description="A comprehensive Python library for mathematics and science knowledge processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dieai/dieai-knowledge",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Education",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - pure Python
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    include_package_data=True,
    package_data={
        "dieai_knowledge": ["../data.txt"],
    },
    keywords="mathematics science physics chemistry biology education knowledge ai",
    project_urls={
        "Bug Reports": "https://github.com/dieai/dieai-knowledge/issues",
        "Source": "https://github.com/dieai/dieai-knowledge",
        "Documentation": "https://github.com/dieai/dieai-knowledge/wiki",
    },
)
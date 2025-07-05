"""
Setup configuration for the DyPy library
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dypy",
    version="1.0.0",
    author="DieAI Team",
    author_email="support@dieai.com",
    description="Python client library for DieAI custom transformer API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dieai/dypy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "typing-extensions>=3.7.4; python_version<'3.8'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio",
            "black",
            "flake8",
            "mypy",
        ],
    },
    keywords="ai, artificial intelligence, transformer, chatbot, api, client",
    project_urls={
        "Bug Reports": "https://github.com/dieai/dypy/issues",
        "Source": "https://github.com/dieai/dypy",
        "Documentation": "https://docs.dieai.com",
    },
)
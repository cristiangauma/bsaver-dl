#!/usr/bin/env python3
"""Setup script for BeatSaver Playlist Downloader.

This setuptools configuration script defines the package metadata, dependencies,
and installation requirements for the BeatSaver Playlist Downloader. It handles
cross-platform installation and creates console script entry points.

The script automatically reads:
- README.md for the long description
- requirements.txt for dependency specifications
- Package structure for automatic discovery

Key Features:
- Cross-platform compatibility (Windows, macOS, Linux)
- Python 3.7+ support
- Automatic dependency management
- Console script entry point creation
- Rich metadata for PyPI distribution

Usage:
    python setup.py install          # Install the package
    python setup.py develop          # Install in development mode
    pip install -e .                 # Editable install (recommended)

Author: Open Source Community
License: MIT
"""

from pathlib import Path
from setuptools import setup, find_packages

# Read the README file for long description
this_directory = Path(__file__).parent.parent  # Go up one level from setup/
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
requirements_path = Path(__file__).parent / "requirements.txt"  # requirements.txt is in setup/
if requirements_path.exists():
    with requirements_path.open(encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="bsaver-dl",
    version="1.0.0",
    author="Open Source Community",
    author_email="",
    description="A comprehensive CLI tool for downloading Beatsaver playlists",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cristiangauma/bsaver-dl",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bsaver-dl=bsaver_dl:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Utilities",
    ],
    keywords="beatsaver beat-saver playlist downloader music game vr",
    project_urls={
        "Bug Reports": "https://github.com/cristiangauma/bsaver-dl/issues",
        "Source": "https://github.com/cristiangauma/bsaver-dl",
        "Documentation": "https://github.com/cristiangauma/bsaver-dl#readme",
    },
) 
"""
FoxNest Windows Installer Setup Script
"""

from setuptools import setup, find_packages
import os
import sys

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), '..', '..', 'README.md')
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "FoxNest Version Control System"

setup(
    name="foxnest",
    version="1.0.0",
    description="FoxNest Version Control System",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="FoxNest Team",
    author_email="support@foxnest.dev",
    url="https://github.com/foxnest/foxnest",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.25.0",
        "flask>=2.0.0",
    ],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'fox=foxnest.fox_client:main',
            'fox-server=foxnest.server:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Version Control",
    ],
)

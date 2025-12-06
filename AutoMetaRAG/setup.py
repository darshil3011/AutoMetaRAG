"""
Setup script for AutoMetaRAG package.
"""

from setuptools import setup, find_packages
import os

# Get the parent directory (project root)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Read requirements from requirements.txt in project root
requirements_path = os.path.join(project_root, 'requirements.txt')
try:
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
except FileNotFoundError:
    requirements = []

# Read README for long description from project root
readme_path = os.path.join(project_root, 'README.md')
try:
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "AutoMetaRAG: Automatic Metadata Generation for RAG Systems"

setup(
    name="AutoMetaRAG",
    version="1.0.0",
    description="Automatic Metadata Generation for RAG Systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AutoMetaRAG Contributors",
    packages=find_packages(where=project_root),
    package_dir={"": project_root},
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "AutoMetaRAG=AutoMetaRAG.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)


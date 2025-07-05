#!/usr/bin/env python
"""Setup script for autoplaytest package distribution."""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="autoplaytest",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered Playwright testing engine for automated web application testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/autoplaytest",
    packages=find_packages(where=".", include=["src*", "config*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "playwright>=1.40.0",
        "aiohttp>=3.9.1",
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.0",
        "sqlalchemy>=2.0.23",
        "numpy>=1.26.0,<2.0.0",
        "pandas>=2.0.3",
        "scikit-learn>=1.3.2",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
        "jinja2>=3.1.2",
        "anthropic>=0.7.7",
        "openai>=1.3.0",
        "google-generativeai>=0.3.0",
        "aiofiles>=23.2.1",
        "httpx>=0.25.2",
        "tenacity>=8.2.3",
        "beautifulsoup4>=4.12.2",
        "lxml>=4.9.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.23.2",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "isort>=5.12.0",
            "pre-commit>=3.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "autoplaytest=src.simple_runner:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.md", "*.json"],
        "config": ["**/*.yaml", "**/*.yml", "**/*.md"],
    },
)
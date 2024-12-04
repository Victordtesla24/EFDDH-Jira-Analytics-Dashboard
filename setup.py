"""Setup configuration for JIRA Analytics Dashboard."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="jira-analytics-dashboard",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A powerful analytics dashboard for visualizing JIRA project data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/EFDDH-Jira-Analytics-Dashboard",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "": ["py.typed"],
        "ui": ["*.html", "*.css", "*.js"],
        "config": ["*.toml", "*.json"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Web Environment",
        "Framework :: Streamlit",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.3.1",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.10.0",
            "black>=23.3.0",
            "flake8>=6.0.0",
            "mypy>=1.3.0",
            "isort>=5.12.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "jira-dashboard=streamlit_app:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/EFDDH-Jira-Analytics-Dashboard/issues",
        "Source": "https://github.com/yourusername/EFDDH-Jira-Analytics-Dashboard",
        "Documentation": "https://github.com/yourusername/EFDDH-Jira-Analytics-Dashboard#readme",
    },
)

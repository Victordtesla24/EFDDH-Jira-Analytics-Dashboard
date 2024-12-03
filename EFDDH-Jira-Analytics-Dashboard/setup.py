from setuptools import setup, find_packages

setup(
    name="jira-analytics-dashboard",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'streamlit>=1.24.0',
        'pandas>=1.5.0',
        'numpy>=1.23.0',
        'plotly>=5.13.0',
        'matplotlib>=3.7.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.3.1',
            'pytest-cov>=4.0.0',
            'black>=22.3.0',
            'flake8>=6.0.0',
        ],
    },
)

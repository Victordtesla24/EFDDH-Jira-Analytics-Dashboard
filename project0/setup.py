from setuptools import setup, find_packages

setup(
    name="auto_error_handler",
    version="1.0.0",
    packages=find_packages(where="scripts"),
    package_dir={"": "scripts"},
    install_requires=[
        'openai>=1.3.7',
        'python-docx>=0.8.11',
        'pypdf>=3.17.1',
        'flask>=2.3.2',
        'beautifulsoup4>=4.12.2',
        'spacy>=3.7.2',
        'scikit-learn>=1.3.2',
        'numpy>=1.24.3',
        'requests>=2.31.0',
        'python-dotenv>=1.0.0'
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.3',
            'mypy>=1.7.0',
            'typing-extensions>=4.8.0'
        ],
    },
    python_requires='>=3.8',
)
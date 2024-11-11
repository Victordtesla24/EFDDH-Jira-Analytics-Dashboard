import sys
import subprocess
import logging
from typing import List

class PackageManager:
    PACKAGE_MAPPING = {
        'spacy': ['spacy', 'en-core-web-sm'],
        'sklearn': ['scikit-learn'],
        'sklearn.feature_extraction.text': ['scikit-learn'],
        'openai': ['openai>=1.3.7'],
        'python-docx': ['python-docx>=0.8.11'],
        'pypdf': ['pypdf>=3.17.1'],
        'flask': ['flask>=2.3.2'],
        'beautifulsoup4': ['beautifulsoup4>=4.12.2'],
        'spacy': ['spacy>=3.7.2', 'en-core-web-sm'],
        'sklearn': ['scikit-learn>=1.3.2', 'numpy>=1.24.3'],
        'pytest': ['pytest>=7.4.3'],
        'requests': ['requests>=2.31.0'],
        'python-dotenv': ['python-dotenv>=1.0.0'],
        'pandas': ['pandas>=2.1.0', 'numpy>=1.24.3'],
        'tensorflow': ['tensorflow>=2.14.0'],
        'torch': ['torch>=2.1.0'],
        'matplotlib': ['matplotlib>=3.8.0'],
        'seaborn': ['seaborn>=0.13.0'],
        'jupyter': ['jupyter>=1.0.0'],
        'sqlalchemy': ['sqlalchemy>=2.0.0'],
        'pytest-cov': ['pytest-cov>=4.1.0'],
        'black': ['black>=23.10.0'],
        'mypy': ['mypy>=1.6.1'],
        'pylint': ['pylint>=3.0.2']
    }

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def handle_import_error(self, error_msg: str) -> bool:
        module_name = error_msg.split("'")[1] if "'" in error_msg else error_msg
        if not module_name:
            return False

        try:
            packages = self.PACKAGE_MAPPING.get(module_name, [module_name])
            if not self._install_packages(packages):
                return False

            if module_name == 'spacy':
                return self._setup_spacy()
            return True
        except Exception as e:
            self.logger.error(f"Failed to handle import error: {str(e)}")
            return False

    def _install_packages(self, packages: List[str]) -> bool:
        try:
            for package in packages:
                self.logger.info(f"Installing {package}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
            return True
        except Exception as e:
            self.logger.error(f"Package installation failed: {str(e)}")
            return False

    def _setup_spacy(self) -> bool:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "spacy"])
            import spacy
            if not spacy.util.is_package('en_core_web_sm'):
                subprocess.check_call([
                    sys.executable, "-m", "spacy", "download", "en_core_web_sm"
                ])
            return True
        except Exception:
            return False
from selenium import webdriver
import importlib
import sys
from types import ModuleType
import os
import logging

def create_dummy_opera():
    """Create a dummy Opera module to prevent import errors"""
    class DummyOpera:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError("Opera WebDriver is no longer supported")
    
    return DummyOpera

def patch_pytest_dash():
    """Patch pytest-dash to handle missing Opera driver"""
    try:
        # Create a dummy webdriver module if needed
        if not hasattr(webdriver, 'Opera'):
            setattr(webdriver, 'Opera', create_dummy_opera())
        
        # Now patch pytest-dash
        pytest_dash = importlib.import_module('pytest_dash')
        if hasattr(pytest_dash, 'utils'):
            driver_map = getattr(pytest_dash.utils, '_driver_map', {})
            driver_map.pop('Opera', None)  # Remove Opera from driver map
            driver_map['Chrome'] = webdriver.Chrome  # Ensure Chrome is available
        
        # Ensure Chrome WebDriver path is correct
        webdriver_path = '/path/to/chromedriver'  # Update this path as needed
        if not os.path.exists(webdriver_path):
            logging.error(f"Chrome WebDriver not found at {webdriver_path}")
            raise FileNotFoundError(f"Chrome WebDriver not found at {webdriver_path}")
        setattr(webdriver, 'Chrome', lambda options: webdriver.Chrome(executable_path=webdriver_path, options=options))
            
    except ImportError as e:
        logging.warning(f"Could not patch pytest-dash: {e}")
    except Exception as e:
        logging.warning(f"Error during patching: {e}")

import importlib.util
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from unittest.mock import patch
import pytest

@pytest.fixture
def mock_streamlit():
    """Fixture to mock streamlit components."""
    with patch("streamlit.set_page_config"), \
         patch("streamlit.error"), \
         patch("streamlit.stop"), \
         patch("streamlit.spinner"):
        yield

@pytest.fixture
def sample_data():
    """Fixture to provide sample test data."""
    return pd.DataFrame({
        "key": ["PROJ-1", "PROJ-2"],
        "summary": ["Task 1", "Task 2"],
        "status": ["Done", "In Progress"],
        "created": ["2024-01-01", "2024-01-02"],
        "resolved": ["2024-01-05", None],
    })

def import_analytics_page():
    """Helper function to import the analytics page module."""
    spec = importlib.util.spec_from_file_location(
        "analytics_page", 
        "src/pages/1_📊_Analytics.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_page_configuration(mock_streamlit):
    """Test the page configuration setup."""
    with patch("streamlit.set_page_config") as mock_config:
        import_analytics_page()
        mock_config.assert_called_once_with(
            page_title="Analytics", 
            page_icon="📊"
        )

def test_data_loading_and_preparation(mock_streamlit, sample_data):
    """Test data loading and preparation process."""
    with patch("src.data.data_loader.load_data", return_value=sample_data) as mock_load, \
         patch("src.data.data_loader.prepare_data", return_value=sample_data) as mock_prepare, \
         patch("pages.analytics.show_analytics") as mock_show:

        import_analytics_page()

        mock_load.assert_called_once()
        assert isinstance(mock_load.call_args[0][0], Path)
        assert str(mock_load.call_args[0][0]).endswith("EFDDH-Jira-Data-Sprint21.csv")
        mock_prepare.assert_called_once_with(sample_data)
        mock_show.assert_called_once_with(sample_data)

def test_error_handling_data_load(mock_streamlit):
    """Test error handling when data loading fails."""
    with patch("src.data.data_loader.load_data", return_value=None) as mock_load, \
         patch("streamlit.error") as mock_error, \
         patch("streamlit.stop") as mock_stop:

        import_analytics_page()

        mock_error.assert_called_once_with("Failed to load data from CSV file")
        mock_stop.assert_called_once()

def test_error_handling_data_preparation(mock_streamlit, sample_data):
    """Test error handling when data preparation fails."""
    with patch("src.data.data_loader.load_data", return_value=sample_data) as mock_load, \
         patch("src.data.data_loader.prepare_data", return_value=None) as mock_prepare, \
         patch("streamlit.error") as mock_error, \
         patch("streamlit.stop") as mock_stop:

        import_analytics_page()

        mock_error.assert_called_once_with("Failed to prepare data for analysis")
        mock_stop.assert_called_once()

def test_error_handling_exception(mock_streamlit):
    """Test error handling for general exceptions."""
    error_msg = "Test error"
    with patch("src.data.data_loader.load_data", side_effect=Exception(error_msg)) as mock_load, \
         patch("streamlit.error") as mock_error, \
         patch("streamlit.stop") as mock_stop:

        import_analytics_page()

        mock_error.assert_called_once_with(f"An error occurred: {error_msg}")
        mock_stop.assert_called_once()

def test_spinner_usage(mock_streamlit, sample_data):
    """Test proper usage of the loading spinner."""
    with patch("src.data.data_loader.load_data", return_value=sample_data), \
         patch("src.data.data_loader.prepare_data", return_value=sample_data), \
         patch("streamlit.spinner") as mock_spinner, \
         patch("pages.analytics.show_analytics"):

        import_analytics_page()

        mock_spinner.assert_called_once_with("Loading analytics dashboard...")

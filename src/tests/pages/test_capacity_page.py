import pytest
import pandas as pd
from pathlib import Path
import importlib.util
from unittest.mock import patch

@pytest.fixture
def mock_streamlit():
    with patch("streamlit.set_page_config"), patch("streamlit.error"), patch(
        "streamlit.stop"
    ), patch("streamlit.spinner"):
        yield

@pytest.fixture
def sample_data():
    return pd.DataFrame(
        {
            "key": ["PROJ-1", "PROJ-2"],
            "summary": ["Task 1", "Task 2"],
            "status": ["Done", "In Progress"],
            "created": ["2024-01-01", "2024-01-02"],
            "resolved": ["2024-01-05", None],
        }
    )

def import_capacity_page():
    """Helper function to import the capacity page module."""
    spec = importlib.util.spec_from_file_location(
        "capacity_page", "src/pages/2_👥_Capacity.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_page_configuration(mock_streamlit):
    with patch("streamlit.set_page_config") as mock_config:
        import_capacity_page()
        mock_config.assert_called_once_with(
            page_title="Capacity Management", page_icon="👥"
        )

def test_data_load_failure(mock_streamlit):
    with patch("src.data.data_loader.load_data", return_value=None) as mock_load, patch(
        "streamlit.error"
    ) as mock_error, patch("streamlit.stop") as mock_stop:
        import_capacity_page()

        mock_error.assert_called_once_with("Failed to load data from CSV file")
        mock_stop.assert_called_once()

def test_data_preparation_failure(mock_streamlit, sample_data):
    with patch(
        "src.data.data_loader.load_data", return_value=sample_data
    ) as mock_load, patch(
        "src.data.data_loader.prepare_data", return_value=None
    ) as mock_prepare, patch(
        "streamlit.error"
    ) as mock_error, patch(
        "streamlit.stop"
    ) as mock_stop:
        import_capacity_page()

        mock_error.assert_called_once_with("Failed to prepare data for analysis")
        mock_stop.assert_called_once()

def test_successful_data_flow(mock_streamlit, sample_data):
    with patch(
        "src.data.data_loader.load_data", return_value=sample_data
    ) as mock_load, patch(
        "src.data.data_loader.prepare_data", return_value=sample_data
    ) as mock_prepare, patch(
        "src.components.visualizations.show_capacity_management"
    ) as mock_show:
        import_capacity_page()

        mock_load.assert_called_once()
        assert isinstance(mock_load.call_args[0][0], Path)
        assert str(mock_load.call_args[0][0]).endswith("EFDDH-Jira-Data-Sprint21.csv")
        mock_prepare.assert_called_once_with(sample_data)
        mock_show.assert_called_once_with(sample_data)

def test_error_handling_chain(mock_streamlit):
    with patch("src.data.data_loader.load_data", return_value=None) as mock_load, patch(
        "src.data.data_loader.prepare_data"
    ) as mock_prepare, patch("streamlit.error") as mock_error, patch(
        "streamlit.stop"
    ) as mock_stop:
        import_capacity_page()

        mock_prepare.assert_not_called()
        mock_error.assert_called_once_with("Failed to load data from CSV file")
        mock_stop.assert_called_once()

def test_spinner_usage(mock_streamlit, sample_data):
    with patch("src.data.data_loader.load_data", return_value=sample_data), patch(
        "src.data.data_loader.prepare_data", return_value=sample_data
    ), patch("streamlit.spinner") as mock_spinner, patch(
        "src.components.visualizations.show_capacity_management"
    ):
        import_capacity_page()

        mock_spinner.assert_called_once_with("Loading capacity management dashboard...")

def test_exception_handling(mock_streamlit):
    error_msg = "Test error"
    with patch(
        "src.data.data_loader.load_data", side_effect=Exception(error_msg)
    ) as mock_load, patch("streamlit.error") as mock_error, patch(
        "streamlit.stop"
    ) as mock_stop:
        import_capacity_page()

        mock_error.assert_called_once_with(f"An error occurred: {error_msg}")
        mock_stop.assert_called_once()

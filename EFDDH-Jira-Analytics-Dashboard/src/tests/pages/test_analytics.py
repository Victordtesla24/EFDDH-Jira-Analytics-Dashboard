import pandas as pd
import pytest
from pathlib import Path

from src.pages.analytics import show_analytics
from src.data.data_loader import load_data, prepare_data


@pytest.fixture
def test_data():
    """Load actual test data from CSV."""
    data_path = Path("data/EFDDH-Jira-Data-Sprint21.csv")
    df = load_data(data_path)
    return prepare_data(df)


@pytest.fixture
def mock_streamlit(mocker):
    """Mock Streamlit components."""
    return {
        "title": mocker.patch("streamlit.title"),
        "sidebar": mocker.patch("streamlit.sidebar"),
        "dataframe": mocker.patch("streamlit.dataframe"),
        "error": mocker.patch("streamlit.error"),
        "warning": mocker.patch("streamlit.warning"),
        "columns": mocker.patch("streamlit.columns"),
        "plotly_chart": mocker.patch("streamlit.plotly_chart"),
        "metric": mocker.patch("streamlit.metric"),
    }


def test_show_analytics(mock_streamlit):
    """Test analytics display with minimal data."""
    test_data = pd.DataFrame(
        {
            "Issue key": ["TEST-1", "TEST-2"],
            "Created": ["2024-01-01", "2024-01-02"],
            "Resolved": ["2024-01-15", "2024-01-16"],
            "Story Points": [1.0, 2.0],
            "Status": ["Done", "In Progress"],
        }
    )

    show_analytics(test_data)

    # Verify only essential calls
    assert mock_streamlit["title"].called


def test_show_analytics_error(mock_streamlit):
    """Test analytics page error handling."""
    show_analytics(None)

    # Verify error was displayed
    assert mock_streamlit["error"].called
    error_message = mock_streamlit["error"].call_args[0][0]
    assert "Error" in error_message, "Error message not displayed"


def test_analytics_page_renders_correctly(mock_streamlit, test_data):
    """Test analytics page rendering with actual data."""
    # Ensure required columns exist
    test_data["Issue Type"] = test_data.get("Issue Type", "Story")
    test_data["Priority"] = test_data.get("Priority", "Medium")
    test_data["Status"] = test_data.get("Status", "Done")

    show_analytics(test_data)

    # Verify components were displayed
    assert mock_streamlit["title"].called
    assert mock_streamlit["plotly_chart"].called
    assert mock_streamlit["metric"].called

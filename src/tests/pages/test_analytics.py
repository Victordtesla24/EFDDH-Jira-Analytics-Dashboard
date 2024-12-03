import pandas as pd
import pytest

from pages.analytics import show_analytics


@pytest.fixture
def test_data():
    """Create test data."""
    return pd.DataFrame(
        {
            "Issue Type": ["Story"] * 5,
            "Priority": ["Medium"] * 5,
            "Status": ["Done"] * 3 + ["In Progress"] * 2,
            "Story Points": [5, 3, 8, 2, 1],
            "Created": ["2024-01-01"] * 5,
            "Epic Link": ["EPIC-1"] * 5,
            "Epic Name": ["Test Epic"] * 5,
        }
    )


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


def test_analytics_page_handles_empty_data(mock_streamlit):
    """Test analytics page with empty data."""
    show_analytics(None)
    assert mock_streamlit["error"].called


def test_analytics_page_handles_missing_columns(mock_streamlit, test_data):
    """Test analytics page with missing columns."""
    test_data = test_data.drop(columns=["Story Points"])
    show_analytics(test_data)
    assert mock_streamlit["error"].called

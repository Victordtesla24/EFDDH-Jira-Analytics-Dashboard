import pandas as pd
import pytest

from pages.analytics import show_analytics
from src.data.data_loader import prepare_data


@pytest.fixture
def test_data():
    """Create test data for integration testing."""
    df = pd.DataFrame(
        {
            "Created": ["2024-01-01", "2024-01-03"],
            "Resolved": ["2024-01-02", "2024-01-04"],
            "Priority": ["High", "Medium"],
            "Issue Type": ["Bug", "Story"],
            "Sprint": ["Sprint 1", "Sprint 1"],
            "Story Points": [5, 3],
            "Epic Name": ["Epic 1", "Epic 2"],
            "Status": ["Done", "In Progress"],
        }
    )
    return prepare_data(df)


@pytest.fixture
def mock_streamlit(mocker):
    """Mock Streamlit components."""
    mocked = {
        "title": mocker.patch("streamlit.title"),
        "write": mocker.patch("streamlit.write"),
        "plotly_chart": mocker.patch("streamlit.plotly_chart"),
        "metric": mocker.patch("streamlit.metric"),
        "error": mocker.patch("streamlit.error"),
        "columns": mocker.patch(
            "streamlit.columns",
            return_value=[
                mocker.MagicMock(),
                mocker.MagicMock(),
                mocker.MagicMock(),
            ],
        ),
    }
    return mocked


def test_analytics_integration(mock_streamlit, test_data):
    """Test analytics page with real data."""
    # Ensure required columns exist
    if "Story Points" not in test_data.columns:
        test_data["Story Points"] = 1.0  # Add default story points
    if "Status" not in test_data.columns:
        test_data["Status"] = "Done"  # Add default status

    show_analytics(test_data)

    # Verify charts were created
    assert mock_streamlit["plotly_chart"].called

    # Verify metrics were displayed
    assert mock_streamlit["metric"].called

    # No errors should be shown
    assert not mock_streamlit["error"].called

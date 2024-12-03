from unittest.mock import MagicMock

import pandas as pd
import pytest


@pytest.fixture
def test_data():
    """Create sample data for testing."""
    return pd.DataFrame(
        {
            "Issue Type": ["Story", "Task", "Bug"],
            "Priority": ["High", "Low", "Medium"],
            "Status": ["Done", "Done", "In Progress"],
            "Story Points": [3, 8, 5],
            "Created": ["2024-01-02", "2024-01-03", "2024-01-04"],
            "Epic Link": ["EPIC-2", "EPIC-1", "EPIC-3"],
            "Epic Name": ["Epic 2", "Epic 1", "Epic 3"],
        }
    )


@pytest.fixture
def test_data_path(tmp_path):
    """Create a temporary test data file."""
    data_file = tmp_path / "test_data.csv"
    test_data = pd.DataFrame(
        {
            "Issue Type": ["Story", "Task", "Bug"],
            "Priority": ["High", "Medium", "Low"],
            "Status": ["Done", "In Progress", "To Do"],
        }
    )
    test_data.to_csv(data_file, index=False)
    return data_file


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components."""
    mock = MagicMock()
    mock.title = MagicMock()
    mock.header = MagicMock()
    mock.plotly_chart = MagicMock()
    mock.metric = MagicMock()
    mock.error = MagicMock()
    mock.warning = MagicMock()
    mock.success = MagicMock()
    mock.info = MagicMock()
    mock.dataframe = MagicMock()
    mock.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
    return mock

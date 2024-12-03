from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture(scope="session")
def sample_jira_data():
    """Create sample data for testing."""
    return pd.DataFrame(
        {
            "Issue key": ["TEST-1", "TEST-2"],
            "Created": ["2024-01-01", "2024-01-02"],
            "Resolved": ["2024-01-02", "2024-01-03"],
            "Priority": ["High", "Medium"],
            "Issue Type": ["Bug", "Task"],
            "Sprint": ["Sprint 1", "Sprint 2"],
            "Status": ["Closed", "In Progress"],
            "Story Points": [5, 3],
            "Epic Name": ["Epic 1", "Epic 2"],
        }
    )


@pytest.fixture(scope="session")
def test_data_path():
    """Provide the path to the test data file."""
    return Path("data/EFDDH-Jira-Data-Sprint21.csv")


@pytest.fixture
def processed_jira_data(sample_jira_data):
    """Create processed data for testing."""
    df = sample_jira_data.copy()
    df["Created"] = pd.to_datetime(df["Created"])
    df["Resolved"] = pd.to_datetime(df["Resolved"])
    df["Resolution Time (Days)"] = (df["Resolved"] - df["Created"]).dt.days
    return df


@pytest.fixture
def mock_streamlit(mocker):
    """Mock all required Streamlit components."""
    return {
        "plotly_chart": mocker.patch("streamlit.plotly_chart"),
        "header": mocker.patch("streamlit.header"),
        "error": mocker.patch("streamlit.error"),
        "metric": mocker.patch("streamlit.metric"),
        "warning": mocker.patch("streamlit.warning"),
        "subheader": mocker.patch("streamlit.subheader"),
        "write": mocker.patch("streamlit.write"),
    }


@pytest.fixture
def test_data():
    """Create test data for analytics."""
    data = pd.DataFrame(
        {
            "Issue key": ["TEST-1", "TEST-2"],
            "Created": ["2024-01-01", "2024-01-02"],
            "Resolved": ["2024-01-15", "2024-01-16"],
            "Updated": ["2024-01-15", "2024-01-16"],
            "Story Points": [5.0, 3.0],
            "Epic Name": ["Test Epic 1", "Test Epic 2"],
            "Status": ["Done", "In Progress"],
        }
    )

    # Convert date columns to datetime
    date_columns = ["Created", "Resolved", "Updated"]
    for col in date_columns:
        data[col] = pd.to_datetime(data[col])

    return data

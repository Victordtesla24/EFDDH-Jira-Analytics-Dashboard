from unittest.mock import MagicMock, patch

import pandas as pd
import plotly.graph_objects as go
import pytest
import streamlit as st

from data.data_loader import prepare_data
from pages.analytics import show_analytics


@pytest.fixture
def test_data():
    """Create test data for integration testing."""
    df = pd.DataFrame(
        {
            "Created": pd.to_datetime(["2024-01-01", "2024-01-03"]),
            "Resolved": pd.to_datetime(["2024-01-02", "2024-01-04"]),
            "Priority": ["High", "Medium"],
            "Issue Type": ["Bug", "Story"],
            "Sprint": ["Sprint 1", "Sprint 1"],
            "Story Points": [5, 3],
            "Epic Name": ["Epic 1", "Epic 2"],
            "Status": ["Done", "In Progress"],
        }
    )
    return df


@pytest.fixture
def mock_streamlit(mocker):
    """Mock Streamlit components."""
    # Create mock context managers for columns
    col_mocks = [MagicMock(), MagicMock()]
    for col in col_mocks:
        col.__enter__ = MagicMock(return_value=col)
        col.__exit__ = MagicMock(return_value=None)

    mocked = {
        "title": mocker.patch("streamlit.title"),
        "write": mocker.patch("streamlit.write"),
        "plotly_chart": mocker.patch("streamlit.plotly_chart"),
        "metric": mocker.patch("streamlit.metric"),
        "error": mocker.patch("streamlit.error"),
        "info": mocker.patch("streamlit.info"),
        "warning": mocker.patch("streamlit.warning"),
        "columns": mocker.patch("streamlit.columns", return_value=col_mocks),
    }

    # Patch st.spinner context manager
    spinner_mock = MagicMock()
    spinner_mock.__enter__ = MagicMock(return_value=None)
    spinner_mock.__exit__ = MagicMock(return_value=None)
    mocked["spinner"] = mocker.patch("streamlit.spinner", return_value=spinner_mock)

    return mocked


@pytest.fixture
def mock_visualizations(mocker):
    """Mock visualization components."""
    return {
        "show_charts": mocker.patch("src.components.visualizations.show_charts"),
        "show_velocity_metrics": mocker.patch(
            "src.components.visualizations.show_velocity_metrics"
        ),
        "show_epic_progress": mocker.patch(
            "src.components.visualizations.show_epic_progress"
        ),
        "show_capacity_management": mocker.patch(
            "src.components.visualizations.show_capacity_management"
        ),
    }


def test_analytics_integration(mock_streamlit, mock_visualizations, test_data):
    """Test analytics page with real data."""

    # Configure visualization mocks to create charts
    def mock_show_charts(data):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[1, 2, 3]))
        st.plotly_chart(fig)

    mock_visualizations["show_charts"].side_effect = mock_show_charts

    def mock_show_epic_progress(data):
        fig = go.Figure()
        fig.add_trace(go.Bar(x=["Epic 1", "Epic 2"], y=[50, 75]))
        st.plotly_chart(fig)

    mock_visualizations["show_epic_progress"].side_effect = mock_show_epic_progress

    # Show analytics with properly formatted data
    show_analytics(test_data)

    # Verify charts were created
    assert (
        mock_streamlit["plotly_chart"].call_count >= 2
    ), "Expected at least 2 charts to be created"

    # Verify metrics were displayed
    assert mock_streamlit["metric"].call_count > 0, "No metrics were displayed"

    # No errors should be shown
    assert not mock_streamlit["error"].called, "Errors were displayed"

    # Verify specific metrics
    metric_calls = mock_streamlit["metric"].call_args_list
    metric_labels = [call.kwargs.get("label", "") for call in metric_calls]

    # Check for required metrics
    assert any(
        "Total Issues" in label for label in metric_labels
    ), "Total Issues metric missing"
    assert any(
        "Completed Issues" in label for label in metric_labels
    ), "Completed Issues metric missing"

    # Verify visualization components were called
    assert mock_visualizations["show_charts"].called, "show_charts was not called"
    assert mock_visualizations[
        "show_epic_progress"
    ].called, "show_epic_progress was not called"
    assert mock_visualizations[
        "show_velocity_metrics"
    ].called, "show_velocity_metrics was not called"

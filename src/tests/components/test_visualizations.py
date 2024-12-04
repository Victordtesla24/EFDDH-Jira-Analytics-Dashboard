from typing import Dict, List, Optional, Union, Any
import pytest
import pandas as pd
import plotly.graph_objects as go
from unittest.mock import MagicMock, patch

from src.components.visualizations import (
    calculate_velocity_metrics,
    show_analytics,
    show_capacity_management,
    show_charts,
    show_epic_progress,
    show_metrics_with_recovery,
    show_velocity_metrics,
    validate_data,
)


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame(
        {
            "Issue key": ["EFDDH-1", "EFDDH-2", "EFDDH-3", "EFDDH-4", "EFDDH-5"],
            "Created": pd.date_range(start="2024-01-01", periods=5),
            "Status": ["Done"] * 3 + ["In Progress"] * 2,
            "Story Points": [5, 3, 8, 4, 2],
            "Epic Name": ["Epic1", "Epic1", "Epic2", "Epic2", "Epic1"],
            "Assignee": ["User1", "User2", "User1", "User2", "User1"],
        }
    )


def test_validate_data():
    """Test data validation function."""
    valid_df = pd.DataFrame({"col1": [1], "col2": [2]})
    assert validate_data(valid_df) is True
    assert validate_data(valid_df, ["col1"]) is True
    assert validate_data(valid_df, ["col3"]) is False
    assert validate_data(None) is False
    assert validate_data(pd.DataFrame()) is False


@patch("src.components.visualizations.st")
def test_show_charts(mock_st, sample_data):
    """Test chart visualization."""
    show_charts(sample_data)
    assert mock_st.plotly_chart.called
    fig = mock_st.plotly_chart.call_args[0][0]
    assert isinstance(fig, go.Figure)
    assert mock_st.plotly_chart.call_args[1]["use_container_width"] is True


@patch("src.components.visualizations.st")
def test_show_charts_error_handling(mock_st):
    """Test chart visualization error handling."""
    show_charts(None)
    mock_st.error.assert_called_once_with("No data available for visualization")

    invalid_df = pd.DataFrame({"wrong_column": [1, 2]})
    show_charts(invalid_df)
    assert mock_st.error.call_count == 2


@patch("src.components.visualizations.st")
def test_show_epic_progress(mock_st, sample_data):
    """Test epic progress visualization."""
    show_epic_progress(sample_data)
    assert mock_st.plotly_chart.called
    fig = mock_st.plotly_chart.call_args[0][0]
    assert isinstance(fig, go.Figure)


@patch("src.components.visualizations.st")
def test_show_epic_progress_error_handling(mock_st):
    """Test epic progress error handling."""
    show_epic_progress(None)
    mock_st.error.assert_called_once()

    invalid_df = pd.DataFrame({"wrong_column": [1, 2]})
    show_epic_progress(invalid_df)
    assert mock_st.error.call_count == 2


@patch("src.components.visualizations.st")
def test_show_velocity_metrics(mock_st, sample_data):
    """Test velocity metrics display."""
    mock_cols = [MagicMock(), MagicMock()]
    mock_st.columns.return_value = mock_cols

    show_velocity_metrics(sample_data)

    assert mock_st.columns.called
    assert mock_st.metric.call_count == 2

    # Verify metrics values
    metric_calls = mock_st.metric.call_args_list
    velocity_call = next(
        call for call in metric_calls if "Average Velocity" in call[0][0]
    )
    completed_call = next(
        call for call in metric_calls if "Completed Stories" in call[0][0]
    )

    assert "8.0" in velocity_call[0][1]  # 16 points / 2 weeks
    assert completed_call[0][1] == 3


@patch("src.components.visualizations.st")
def test_show_capacity_management(mock_st, sample_data):
    """Test capacity management visualization."""
    mock_cols = [MagicMock(), MagicMock(), MagicMock()]
    mock_st.columns.return_value = mock_cols

    show_capacity_management(sample_data)

    assert mock_st.title.called
    assert mock_st.columns.called
    assert mock_st.plotly_chart.call_count >= 2  # Trend and workload charts

    # Verify metrics
    metric_calls = mock_st.metric.call_args_list
    metrics = {call[0][0]: float(call[0][1].strip("0")) for call in metric_calls}

    assert metrics["Total Story Points"] == 22
    assert metrics["Completed Points"] == 16
    assert metrics["In Progress Points"] == 6


@patch("src.components.visualizations.st")
def test_show_capacity_management_error_handling(mock_st):
    """Test capacity management error handling."""
    show_capacity_management(None)
    mock_st.error.assert_called_once()

    invalid_df = pd.DataFrame({"wrong_column": [1, 2]})
    show_capacity_management(invalid_df)
    assert mock_st.error.call_count == 2


def test_calculate_velocity_metrics(sample_data):
    """Test velocity metrics calculation."""
    metrics = calculate_velocity_metrics(sample_data)
    assert metrics["velocity"] == 8.0  # (5 + 3 + 8) / 2 weeks
    assert metrics["completed"] == 3

    # Test edge cases
    assert calculate_velocity_metrics(pd.DataFrame()) == {
        "velocity": 0.0,
        "completed": 0,
    }
    assert calculate_velocity_metrics(None) == {"velocity": 0.0, "completed": 0}


@patch("src.components.visualizations.st")
def test_show_metrics_with_recovery(mock_st, sample_data):
    """Test metrics display with recovery."""
    mock_st.columns.return_value = [MagicMock(), MagicMock()]

    # Test successful case
    show_metrics_with_recovery(sample_data)
    assert not mock_st.error.called

    # Test recovery case
    with patch(
        "src.components.visualizations.show_velocity_metrics",
        side_effect=Exception("Test error"),
    ):
        show_metrics_with_recovery(sample_data)
        assert mock_st.warning.called


@patch("src.components.visualizations.st")
def test_show_analytics(mock_st, sample_data):
    """Test analytics dashboard display."""
    mock_st.columns.return_value = [MagicMock(), MagicMock()]

    show_analytics(sample_data)

    assert mock_st.columns.called
    assert mock_st.metric.call_count >= 2

    # Test error handling
    show_analytics(None)
    mock_st.error.assert_called_with("No data available for analysis")

    invalid_df = pd.DataFrame({"wrong_column": [1, 2]})
    show_analytics(invalid_df)
    assert mock_st.error.call_count == 2

from unittest.mock import patch

import pandas as pd
import plotly.graph_objects as go
import pytest

from src.components.visualizations import (show_charts, show_epic_progress,
                                           show_velocity_metrics)


def test_show_charts(mock_streamlit):
    """Test basic chart visualization."""
    test_data = pd.DataFrame(
        {
            "Created": pd.date_range(start="2024-01-01", periods=5),
            "Status": ["Done"] * 5,
        }
    )

    show_charts(test_data)
    assert mock_streamlit["plotly_chart"].called
    call_args = mock_streamlit["plotly_chart"].call_args
    assert isinstance(call_args[0][0], go.Figure)
    assert call_args[1]["use_container_width"] is True


def test_show_charts_empty_data(mock_streamlit):
    """Test chart visualization with empty data."""
    empty_df = pd.DataFrame()
    show_charts(empty_df)
    assert mock_streamlit["error"].called
    error_msg = mock_streamlit["error"].call_args[0][0]
    assert error_msg == "No data available for visualization"


def test_show_epic_progress(mock_streamlit):
    """Test epic progress visualization."""
    test_data = pd.DataFrame(
        {
            "Epic Name": ["Epic1", "Epic2"],
            "Story Points": [5, 3],
            "Status": ["Done", "In Progress"],
        }
    )

    show_epic_progress(test_data)
    assert mock_streamlit["plotly_chart"].called
    call_args = mock_streamlit["plotly_chart"].call_args
    assert isinstance(call_args[0][0], go.Figure)
    assert call_args[1]["use_container_width"] is True


def test_show_epic_progress_empty_data(mock_streamlit):
    """Test epic progress with empty data."""
    empty_df = pd.DataFrame()
    show_epic_progress(empty_df)
    assert mock_streamlit["error"].called
    msg = mock_streamlit["error"].call_args[0][0]
    assert msg == "No data available for epic progress visualization"


def test_show_epic_progress_missing_columns(mock_streamlit):
    """Test epic progress with missing required columns."""
    incomplete_df = pd.DataFrame({"Epic Name": ["Epic1"], "Status": ["Done"]})
    show_epic_progress(incomplete_df)
    assert mock_streamlit["error"].called
    msg = mock_streamlit["error"].call_args[0][0]
    assert msg == "Missing required columns for epic progress visualization"


def test_show_velocity_metrics(mock_streamlit):
    """Test velocity metrics display."""
    test_df = pd.DataFrame(
        {
            "Status": ["Done", "Done", "In Progress"],
            "Story Points": [5, 3, 8],
            "Created": pd.date_range(start="2024-01-01", periods=3),
        }
    )

    show_velocity_metrics(test_df)
    assert mock_streamlit["metric"].called

    metric_calls = mock_streamlit["metric"].call_args_list
    metrics_found = {"velocity": False, "completed": False}

    for call in metric_calls:
        args = call[0]
        if "Average Velocity" in args[0]:
            metrics_found["velocity"] = True
            assert "4.0" in args[1]
        elif "Completed Stories" in args[0]:
            metrics_found["completed"] = True
            assert args[1] == 2

    assert all(metrics_found.values()), "Not all expected metrics were displayed"


def test_show_velocity_metrics_empty_data(mock_streamlit):
    """Test velocity metrics with empty data."""
    empty_df = pd.DataFrame()
    show_velocity_metrics(empty_df)
    assert mock_streamlit["error"].called
    error_msg = mock_streamlit["error"].call_args[0][0]
    assert error_msg == "No data available for velocity metrics"


def test_show_velocity_metrics_no_completed_items(mock_streamlit):
    """Test velocity metrics with no completed items."""
    test_df = pd.DataFrame(
        {
            "Status": ["In Progress", "To Do"],
            "Story Points": [5, 3],
            "Created": pd.date_range(start="2024-01-01", periods=2),
        }
    )

    show_velocity_metrics(test_df)
    assert mock_streamlit["warning"].called
    warning_msg = mock_streamlit["warning"].call_args[0][0]
    assert warning_msg == "No completed items found for velocity calculation"


def test_show_velocity_metrics_calculation(mock_streamlit):
    """Test velocity metrics calculation accuracy."""
    test_df = pd.DataFrame(
        {
            "Status": ["Done", "Done"],
            "Story Points": [10, 20],
            "Created": pd.date_range(start="2024-01-01", periods=2),
        }
    )

    show_velocity_metrics(test_df)
    assert mock_streamlit["metric"].called

    metric_calls = mock_streamlit["metric"].call_args_list
    metrics_found = {"velocity": False, "completed": False}

    for call in metric_calls:
        args = call[0]
        if "Average Velocity" in args[0]:
            metrics_found["velocity"] = True
            assert "15.0" in args[1]
        elif "Completed Stories" in args[0]:
            metrics_found["completed"] = True
            assert args[1] == 2

    assert all(metrics_found.values()), "Not all expected metrics were displayed"

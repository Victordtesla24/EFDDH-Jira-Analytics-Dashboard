from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.streamlit_app import (filter_data, initialize_app,
                               load_dashboard_data, run_app,
                               show_agile_process, show_filters, show_handbook)


class MockSidebar:
    """Mock sidebar context manager."""

    def __init__(self):
        self.header = MagicMock()
        self.multiselect = MagicMock(
            side_effect=[
                ["High", "Medium"],  # Priority
                ["Bug", "Story"],  # Issue Type
                ["Sprint 1"],  # Sprint
            ]
        )
        self.date_input = MagicMock(return_value=[date(2024, 1, 1), date(2024, 1, 3)])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class MockColumn:
    """Mock column context manager."""

    def __init__(self):
        self.metric = MagicMock()
        self.markdown = MagicMock()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None


class MockTab:
    """Mock tab context manager."""

    def __init__(self):
        self.markdown = MagicMock()
        self.metric = MagicMock()
        self.warning = MagicMock()
        self.columns = MagicMock()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None


def test_initialize_app(mock_streamlit):
    """Test app initialization."""
    initialize_app()

    mock_streamlit.set_page_config.assert_called_once()
    config_args = mock_streamlit.set_page_config.call_args[1]
    assert config_args["layout"] == "wide"

    mock_streamlit.markdown.assert_called_once()
    css_args = mock_streamlit.markdown.call_args
    assert "style" in css_args[0][0]
    assert css_args[1]["unsafe_allow_html"] is True


def test_load_dashboard_data(mock_streamlit, sample_data):
    """Test dashboard data loading."""
    with patch("src.streamlit_app.load_data", return_value=sample_data), patch(
        "src.streamlit_app.prepare_data", return_value=sample_data
    ):

        # Test successful load
        result = load_dashboard_data()
        assert result is not None
        assert not result.empty
        assert not mock_streamlit.error.called

        # Test empty data
        with patch("src.streamlit_app.load_data", return_value=pd.DataFrame()):
            result = load_dashboard_data()
            assert result is None
            mock_streamlit.error.assert_called_with("No data available in the CSV file")

        # Test preparation failure
        with patch("src.streamlit_app.prepare_data", return_value=pd.DataFrame()):
            result = load_dashboard_data()
            assert result is None
            mock_streamlit.error.assert_called_with(
                "Failed to prepare data for analysis"
            )


def test_show_filters(mock_streamlit, sample_data):
    """Test filter controls."""
    # Setup mock returns
    mock_streamlit.multiselect.side_effect = [
        ["High", "Medium"],  # Priority
        ["Bug", "Story"],  # Issue Type
        ["Sprint 1"],  # Sprint
    ]
    mock_streamlit.date_input.return_value = [date(2024, 1, 1), date(2024, 1, 3)]

    priorities, types, sprints, dates = show_filters(sample_data)

    assert len(mock_streamlit.multiselect.call_args_list) == 3
    assert mock_streamlit.date_input.called

    assert priorities == ["High", "Medium"]
    assert types == ["Bug", "Story"]
    assert sprints == ["Sprint 1"]
    assert len(dates) == 2


def test_filter_data(sample_data):
    """Test data filtering."""
    filters = (
        ["High", "Medium"],  # priorities
        ["Bug", "Story"],  # issue types
        ["Sprint 1"],  # sprints
        (date(2024, 1, 1), date(2024, 1, 2)),  # dates
    )

    filtered = filter_data(sample_data, filters)

    assert len(filtered) > 0
    assert all(p in ["High", "Medium"] for p in filtered["Priority"])
    assert all(t in ["Bug", "Story"] for t in filtered["Issue Type"])
    assert all(s in ["Sprint 1"] for s in filtered["Sprint"])
    assert all(d.date() <= date(2024, 1, 2) for d in filtered["Created"])


def test_show_handbook(mock_streamlit):
    """Test handbook display."""
    show_handbook()
    assert mock_streamlit.markdown.called
    handbook_content = mock_streamlit.markdown.call_args[0][0]
    assert "Project Handbook" in handbook_content
    assert "Key Features" in handbook_content
    assert "Getting Started" in handbook_content


def test_show_agile_process(mock_streamlit):
    """Test agile process display."""
    show_agile_process()
    assert mock_streamlit.markdown.called
    agile_content = mock_streamlit.markdown.call_args[0][0]
    assert "Agile Methodology" in agile_content
    assert "Process Components" in agile_content
    assert "Best Practices" in agile_content


def test_run_app_success(mock_streamlit, sample_data):
    """Test successful app execution."""
    # Setup filter mocks
    filters = (
        ["High", "Medium"],
        ["Bug", "Story"],
        ["Sprint 1"],
        (date(2024, 1, 1), date(2024, 1, 3)),
    )

    # Create mock sidebar
    mock_sidebar = MockSidebar()
    mock_streamlit.sidebar = mock_sidebar

    # Create mock tabs with proper context management
    mock_tabs = [MockTab(), MockTab(), MockTab()]
    mock_streamlit.tabs.return_value = mock_tabs

    # Create mock columns
    mock_cols = [MockColumn(), MockColumn()]
    mock_streamlit.columns.return_value = mock_cols

    # Setup all mocks
    with patch(
        "src.streamlit_app.load_dashboard_data", return_value=sample_data
    ), patch("src.streamlit_app.show_filters", return_value=filters), patch(
        "src.streamlit_app.filter_data", return_value=sample_data
    ), patch(
        "src.components.visualizations.show_charts"
    ) as mock_charts, patch(
        "src.components.visualizations.show_velocity_metrics"
    ) as mock_velocity, patch(
        "src.components.visualizations.show_epic_progress"
    ) as mock_epic, patch(
        "src.components.visualizations.show_capacity_management"
    ) as mock_capacity:

        # Run app
        run_app()

        # Verify initialization
        mock_streamlit.set_page_config.assert_called_once()

        # Verify metrics were called
        assert mock_streamlit.metric.call_count >= 2

        # Execute the column context
        with mock_cols[1]:
            mock_charts.assert_not_called()

        # Verify visualizations were called in the correct order
        assert mock_charts.called, "show_charts was not called"
        assert mock_velocity.called, "show_velocity_metrics was not called"
        assert mock_epic.called, "show_epic_progress was not called"
        assert mock_capacity.called, "show_capacity_management was not called"

        # Verify the order of visualization calls with correct arguments
        mock_charts.assert_called_once_with(sample_data)
        mock_velocity.assert_called_once_with(sample_data)
        mock_epic.assert_called_once_with(sample_data)
        mock_capacity.assert_called_once_with(sample_data)


def test_run_app_error_handling(mock_streamlit):
    """Test app error handling."""
    # Test data loading failure
    with patch("src.streamlit_app.load_dashboard_data", return_value=None):
        run_app()
        assert mock_streamlit.stop.called

    # Test unexpected error
    with patch(
        "src.streamlit_app.load_dashboard_data", side_effect=Exception("Test error")
    ):
        run_app()
        mock_streamlit.error.assert_called_with("An error occurred: Test error")
        assert mock_streamlit.stop.call_count == 2


def test_run_app_empty_filtered_data(mock_streamlit, sample_data):
    """Test handling of empty filtered data."""
    filters = (
        ["High", "Medium"],
        ["Bug", "Story"],
        ["Sprint 1"],
        (date(2024, 1, 1), date(2024, 1, 3)),
    )

    # Create mock sidebar
    mock_sidebar = MockSidebar()
    mock_streamlit.sidebar = mock_sidebar

    # Create mock tabs with proper context management
    mock_tabs = [MockTab(), MockTab(), MockTab()]
    mock_streamlit.tabs.return_value = mock_tabs

    with patch(
        "src.streamlit_app.load_dashboard_data", return_value=sample_data
    ), patch("src.streamlit_app.show_filters", return_value=filters), patch(
        "src.streamlit_app.filter_data", return_value=pd.DataFrame()
    ):
        run_app()
        mock_streamlit.warning.assert_called_with(
            "No data matches the selected filters"
        )

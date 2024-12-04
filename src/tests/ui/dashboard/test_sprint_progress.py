"""Tests for sprint progress visualization functionality."""

from datetime import datetime, timedelta

import pandas as pd
import pytest

from ui.dashboard.sprint_progress import (create_burndown_chart,
                                              create_status_distribution,
                                              create_velocity_chart)


@pytest.fixture
def sample_progress_data():
    """Create sample data for progress visualization testing."""
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(14)]

    data = []
    # Create issues with different completion dates
    for i in range(10):
        data.append(
            {
                "Sprint": "BP: EFDDH Sprint 21",
                "Status": "Done" if i < 7 else "In Progress",
                "Story Points": i + 1,
                "Created": dates[0],
                "Resolved": dates[i] if i < 7 else None,
                "Issue key": f"EFDDH-{i+1}",
            }
        )

    return pd.DataFrame(data)


@pytest.mark.priority_high
@pytest.mark.visuals
def test_create_burndown_chart(sample_progress_data):
    """Test burndown chart creation."""
    chart = create_burndown_chart(sample_progress_data)

    assert chart is not None
    assert chart.data  # Chart has data traces
    assert chart.layout.title.text  # Chart has a title
    assert chart.layout.xaxis.title.text  # X-axis is labeled
    assert chart.layout.yaxis.title.text  # Y-axis is labeled


@pytest.mark.priority_high
@pytest.mark.visuals
def test_create_burndown_chart_empty_data():
    """Test burndown chart creation with empty data."""
    empty_df = pd.DataFrame()
    chart = create_burndown_chart(empty_df)

    assert chart is not None
    assert chart.data  # Should have at least empty traces
    assert chart.layout.title.text  # Should still have a title


@pytest.mark.priority_high
@pytest.mark.visuals
def test_create_status_distribution(sample_progress_data):
    """Test status distribution chart creation."""
    chart = create_status_distribution(sample_progress_data)

    assert chart is not None
    assert chart.data  # Chart has data traces
    assert chart.layout.title.text  # Chart has a title
    assert len(chart.data[0].values) == 2  # Should have 2 status categories


@pytest.mark.priority_high
@pytest.mark.visuals
def test_create_status_distribution_empty_data():
    """Test status distribution chart creation with empty data."""
    empty_df = pd.DataFrame()
    chart = create_status_distribution(empty_df)

    assert chart is not None
    assert chart.data  # Should have at least empty traces
    assert chart.layout.title.text  # Should still have a title


@pytest.mark.priority_high
@pytest.mark.visuals
def test_create_velocity_chart(sample_progress_data):
    """Test velocity chart creation."""
    chart = create_velocity_chart(sample_progress_data)

    assert chart is not None
    assert chart.data  # Chart has data traces
    assert chart.layout.title.text  # Chart has a title
    assert chart.layout.xaxis.title.text  # X-axis is labeled
    assert chart.layout.yaxis.title.text  # Y-axis is labeled


@pytest.mark.priority_high
@pytest.mark.visuals
def test_create_velocity_chart_empty_data():
    """Test velocity chart creation with empty data."""
    empty_df = pd.DataFrame()
    chart = create_velocity_chart(empty_df)

    assert chart is not None
    assert chart.data  # Should have at least empty traces
    assert chart.layout.title.text  # Should still have a title

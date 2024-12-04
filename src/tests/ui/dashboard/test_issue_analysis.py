"""Tests for issue analysis visualization functionality."""

from datetime import datetime, timedelta

import pandas as pd
import pytest

from ui.dashboard.issue_analysis import (create_daily_created_trend,
                                             create_issue_types_chart,
                                             create_priority_distribution,
                                             create_story_points_distribution)


@pytest.fixture
def sample_issue_data():
    """Create sample data for issue analysis testing."""
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(14)]

    data = []
    issue_types = ["Story", "Bug", "Epic", "Task"]
    priorities = ["Highest", "High", "Medium", "Low"]

    for i in range(20):
        data.append(
            {
                "Sprint": "BP: EFDDH Sprint 21",
                "Issue Type": issue_types[i % len(issue_types)],
                "Priority": priorities[i % len(priorities)],
                "Status": "Done" if i < 15 else "In Progress",
                "Story Points": (i % 8) + 1,
                "Created": dates[i % len(dates)],
                "Resolved": dates[(i + 3) % len(dates)] if i < 15 else None,
                "Issue key": f"EFDDH-{i+1}",
            }
        )

    return pd.DataFrame(data)


@pytest.mark.priority_high
@pytest.mark.visuals
def test_create_issue_types_chart(sample_issue_data):
    """Test issue types chart creation."""
    chart = create_issue_types_chart(sample_issue_data)

    assert chart is not None
    assert chart.data  # Chart has data traces
    assert chart.layout.title.text  # Chart has a title
    assert len(chart.data[0].y) == 4  # Should have 4 issue types
    assert all(
        count == 5 for count in chart.data[0].y
    )  # Each type should have 5 issues


@pytest.mark.priority_high
@pytest.mark.visuals
def test_create_issue_types_chart_empty_data():
    """Test issue types chart creation with empty data."""
    empty_df = pd.DataFrame()
    chart = create_issue_types_chart(empty_df)

    assert chart is not None
    assert chart.data  # Should have at least empty traces
    assert chart.layout.title.text  # Should still have a title


@pytest.mark.priority_high
@pytest.mark.visuals
def test_create_priority_distribution(sample_issue_data):
    """Test priority distribution chart creation."""
    chart = create_priority_distribution(sample_issue_data)

    assert chart is not None
    assert chart.data  # Chart has data traces
    assert chart.layout.title.text  # Chart has a title
    assert len(chart.data[0].y) == 4  # Should have 4 priority levels
    assert all(
        count == 5 for count in chart.data[0].y
    )  # Each priority should have 5 issues


@pytest.mark.priority_high
@pytest.mark.visuals
def test_create_priority_distribution_empty_data():
    """Test priority distribution chart creation with empty data."""
    empty_df = pd.DataFrame()
    chart = create_priority_distribution(empty_df)

    assert chart is not None
    assert chart.data  # Should have at least empty traces
    assert chart.layout.title.text  # Should still have a title


@pytest.mark.priority_high
@pytest.mark.visuals
def test_create_story_points_distribution(sample_issue_data):
    """Test story points distribution chart creation."""
    chart = create_story_points_distribution(sample_issue_data)

    assert chart is not None
    assert chart.data  # Chart has data traces
    assert chart.layout.title.text  # Chart has a title
    assert chart.layout.xaxis.title.text  # X-axis is labeled
    assert chart.layout.yaxis.title.text  # Y-axis is labeled


@pytest.mark.priority_high
@pytest.mark.visuals
def test_create_story_points_distribution_empty_data():
    """Test story points distribution chart creation with empty data."""
    empty_df = pd.DataFrame()
    chart = create_story_points_distribution(empty_df)

    assert chart is not None
    assert chart.data  # Should have at least empty traces
    assert chart.layout.title.text  # Should still have a title


@pytest.mark.priority_high
@pytest.mark.visuals
def test_create_daily_created_trend(sample_issue_data):
    """Test daily created trend chart creation."""
    chart = create_daily_created_trend(sample_issue_data)

    assert chart is not None
    assert chart.data  # Chart has data traces
    assert chart.layout.title.text  # Chart has a title
    assert chart.layout.xaxis.title.text  # X-axis is labeled
    assert chart.layout.yaxis.title.text  # Y-axis is labeled


@pytest.mark.priority_high
@pytest.mark.visuals
def test_create_daily_created_trend_empty_data():
    """Test daily created trend chart creation with empty data."""
    empty_df = pd.DataFrame()
    chart = create_daily_created_trend(empty_df)

    assert chart is not None
    assert chart.data  # Should have at least empty traces
    assert chart.layout.title.text  # Should still have a title

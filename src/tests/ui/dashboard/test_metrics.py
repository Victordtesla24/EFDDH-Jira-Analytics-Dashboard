"""Tests for dashboard metrics functionality."""

from datetime import datetime, timedelta

import pandas as pd
import pytest

from src.ui.dashboard.metrics import get_sprint_metrics


@pytest.fixture
def sample_metrics_data():
    """Create sample data for metrics testing."""
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(14)]

    data = []
    # Current sprint data
    for i in range(10):
        data.append(
            {
                "Sprint": "BP: EFDDH Sprint 21",
                "Status": "Done" if i < 7 else "In Progress",
                "Story Points": i + 1,
                "Created": dates[0],
                "Resolved": dates[3] if i < 7 else None,
                "Issue key": f"EFDDH-{i+1}",
            }
        )

    # Previous sprint data
    for i in range(8):
        data.append(
            {
                "Sprint": "BP: EFDDH Sprint 20",
                "Status": "Done" if i < 5 else "In Progress",
                "Story Points": i + 1,
                "Created": dates[0] - timedelta(days=14),
                "Resolved": dates[3] - timedelta(days=14) if i < 5 else None,
                "Issue key": f"EFDDH-{i+11}",
            }
        )

    return pd.DataFrame(data)


@pytest.mark.priority_high
@pytest.mark.metrics
def test_get_sprint_metrics_current_only(sample_metrics_data):
    """Test metrics calculation for current sprint only."""
    metrics = get_sprint_metrics(sample_metrics_data, "BP: EFDDH Sprint 21", None)

    assert metrics["current"]["total_issues"] == 10
    assert metrics["current"]["completed"] == 7
    assert metrics["current"]["story_points"] == sum(
        range(1, 8)
    )  # Sum of points for completed issues
    assert all(delta == 0 for delta in metrics["deltas"].values())


@pytest.mark.priority_high
@pytest.mark.metrics
def test_get_sprint_metrics_with_comparison(sample_metrics_data):
    """Test metrics calculation with sprint comparison."""
    metrics = get_sprint_metrics(
        sample_metrics_data, "BP: EFDDH Sprint 21", "BP: EFDDH Sprint 20"
    )

    # Current sprint metrics
    assert metrics["current"]["total_issues"] == 10
    assert metrics["current"]["completed"] == 7
    assert metrics["current"]["story_points"] == sum(range(1, 8))

    # Previous sprint metrics
    assert metrics["previous"]["total_issues"] == 8
    assert metrics["previous"]["completed"] == 5
    assert metrics["previous"]["story_points"] == sum(range(1, 6))

    # Delta calculations (as percentages)
    assert metrics["deltas"]["total_issues"] == ((10 - 8) / 8) * 100  # 25% increase
    assert metrics["deltas"]["completed"] == ((7 - 5) / 5) * 100  # 40% increase
    assert (
        metrics["deltas"]["story_points"] == ((28 - 15) / 15) * 100
    )  # ~86.67% increase


@pytest.mark.priority_high
@pytest.mark.metrics
def test_get_sprint_metrics_empty_data():
    """Test metrics calculation with empty data."""
    empty_df = pd.DataFrame()
    metrics = get_sprint_metrics(empty_df, "Any Sprint", None)

    assert metrics["current"]["total_issues"] == 0
    assert metrics["current"]["completed"] == 0
    assert metrics["current"]["story_points"] == 0
    assert all(delta == 0 for delta in metrics["deltas"].values())


@pytest.mark.priority_high
@pytest.mark.metrics
def test_get_sprint_metrics_invalid_sprint(sample_metrics_data):
    """Test metrics calculation with invalid sprint name."""
    metrics = get_sprint_metrics(sample_metrics_data, "Non-existent Sprint", None)

    assert metrics["current"]["total_issues"] == 0
    assert metrics["current"]["completed"] == 0
    assert metrics["current"]["story_points"] == 0
    assert all(delta == 0 for delta in metrics["deltas"].values())

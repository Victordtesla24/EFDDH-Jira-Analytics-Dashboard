"""Tests for sprint selector functionality."""

from datetime import datetime, timedelta

import pandas as pd
import pytest

from ui.dashboard.sprint_selector import (get_available_sprints,
                                              get_sprint_data)


@pytest.fixture
def sample_sprint_data():
    """Create sample sprint data for testing."""
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(14)]

    return pd.DataFrame(
        {
            "Sprint": ["BP: EFDDH Sprint 21"] * 5,
            "Status": ["Done", "In Progress", "Done", "To Do", "Done"],
            "Story Points": [3, 5, 2, 1, 3],
            "Created": [dates[0]] * 5,  # All created at sprint start
            "Resolved": [
                dates[3],
                None,
                dates[7],
                None,
                dates[10],
            ],  # Some resolved during sprint
            "Issue key": ["EFDDH-1", "EFDDH-2", "EFDDH-3", "EFDDH-4", "EFDDH-5"],
        }
    )


@pytest.mark.priority_high
@pytest.mark.dashboard
def test_get_available_sprints(sample_sprint_data):
    """Test getting available sprints from data."""
    sprints = get_available_sprints(sample_sprint_data)
    assert len(sprints) == 1
    assert sprints[0] == "BP: EFDDH Sprint 21"


@pytest.mark.priority_high
@pytest.mark.dashboard
def test_get_available_sprints_empty_data():
    """Test getting sprints from empty data."""
    empty_df = pd.DataFrame()
    sprints = get_available_sprints(empty_df)
    assert len(sprints) == 0


@pytest.mark.priority_high
@pytest.mark.dashboard
def test_get_sprint_data(sample_sprint_data):
    """Test getting data for a specific sprint."""
    sprint_data = get_sprint_data(sample_sprint_data, "BP: EFDDH Sprint 21")
    assert len(sprint_data) == 5
    assert all(sprint_data["Sprint"] == "BP: EFDDH Sprint 21")


@pytest.mark.priority_high
@pytest.mark.dashboard
def test_get_sprint_data_no_matches(sample_sprint_data):
    """Test getting data for a non-existent sprint."""
    sprint_data = get_sprint_data(sample_sprint_data, "Non-existent Sprint")
    assert sprint_data.empty

from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from data.processors import (JiraDataProcessor, process_jira_data,
                                 process_sprint_data)


@pytest.fixture
def sample_jira_data():
    """Create sample JIRA data for testing."""
    return pd.DataFrame(
        {
            "Issue key": ["TEST-1", "TEST-2", "TEST-3"],
            "Created": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "Resolved": ["2024-01-02", None, "2024-01-04"],
            "Status": ["Done", "In Progress", "Done"],
            "Story Points": [5, 3, 8],
            "Sprint": ["Sprint 1", "Sprint 1", "Sprint 2"],
            "Priority": ["High", "Medium", "Low"],
            "Issue Type": ["Bug", "Story", "Task"],
            "Epic Link": ["EPIC-1", "EPIC-2", "EPIC-1"],
        }
    )


@pytest.fixture
def sample_sprint_data():
    """Create sample sprint data for testing."""
    return pd.DataFrame(
        {
            "sprint_name": ["Sprint 1", "Sprint 2"],
            "start_date": ["2024-01-01", "2024-01-15"],
            "end_date": ["2024-01-14", "2024-01-28"],
        }
    )


@pytest.fixture
def processed_jira_data(sample_jira_data):
    """Create pre-processed JIRA data."""
    sample_jira_data["Created"] = pd.to_datetime(sample_jira_data["Created"])
    sample_jira_data["Resolved"] = pd.to_datetime(sample_jira_data["Resolved"])
    return sample_jira_data


def test_jira_data_processor_initialization(sample_jira_data):
    """Test JiraDataProcessor initialization."""
    processor = JiraDataProcessor(sample_jira_data)
    assert processor.df.equals(sample_jira_data)


def test_get_sprint_metrics_with_data(processed_jira_data):
    """Test sprint metrics calculation with valid data."""
    processor = JiraDataProcessor(processed_jira_data)
    metrics = processor.get_sprint_metrics()

    assert metrics["total_issues"] == 3
    assert metrics["completion_rate"] == pytest.approx(
        66.67, rel=0.01
    )  # 2 out of 3 resolved
    assert isinstance(metrics["avg_cycle_time"], float)
    assert metrics["avg_cycle_time"] == 1.0  # Both resolved issues took 1 day


def test_get_sprint_metrics_empty_data():
    """Test sprint metrics with empty data."""
    processor = JiraDataProcessor(pd.DataFrame())
    metrics = processor.get_sprint_metrics()

    assert metrics["total_issues"] == 0
    assert metrics["completion_rate"] == 0
    assert pd.isna(metrics["avg_cycle_time"])


def test_get_sprint_metrics_no_resolved_issues(sample_jira_data):
    """Test sprint metrics when no issues are resolved."""
    sample_jira_data["Resolved"] = None
    processor = JiraDataProcessor(sample_jira_data)
    metrics = processor.get_sprint_metrics()

    assert metrics["total_issues"] == 3
    assert metrics["completion_rate"] == 0
    assert pd.isna(metrics["avg_cycle_time"])


def test_process_jira_data_full(sample_jira_data):
    """Test JIRA data processing with all fields."""
    processed_data = process_jira_data(sample_jira_data)

    # Verify date conversions
    assert pd.api.types.is_datetime64_dtype(processed_data["Created"])
    assert pd.api.types.is_datetime64_dtype(processed_data["Resolved"])

    # Verify resolution time calculation
    assert processed_data["Resolution Time (Days)"].iloc[0] == 1
    assert pd.isna(processed_data["Resolution Time (Days)"].iloc[1])
    assert processed_data["Resolution Time (Days)"].iloc[2] == 1

    # Verify status categories
    assert processed_data["Status Category"].iloc[0] == "Done"
    assert processed_data["Status Category"].iloc[1] == "In Progress"
    assert processed_data["Status Category"].iloc[2] == "Done"


def test_process_jira_data_minimal():
    """Test processing with minimal required fields."""
    minimal_data = pd.DataFrame({"Created": ["2024-01-01"], "Status": ["In Progress"]})
    processed_data = process_jira_data(minimal_data)

    assert not processed_data.empty
    assert pd.api.types.is_datetime64_dtype(processed_data["Created"])
    assert processed_data["Status Category"].iloc[0] == "In Progress"


def test_process_jira_data_invalid_dates():
    """Test processing with invalid date formats."""
    invalid_data = pd.DataFrame(
        {"Created": ["invalid"], "Resolved": ["2024-01-01"], "Status": ["Done"]}
    )
    processed_data = process_jira_data(invalid_data)

    assert not processed_data.empty
    assert pd.isna(processed_data["Created"].iloc[0])
    assert pd.api.types.is_datetime64_dtype(processed_data["Resolved"])


def test_process_jira_data_custom_status():
    """Test processing with custom status values."""
    custom_data = pd.DataFrame({"Created": ["2024-01-01"], "Status": ["Custom Status"]})
    processed_data = process_jira_data(custom_data)

    assert processed_data["Status Category"].iloc[0] == "Other"


def test_process_sprint_data_success(sample_sprint_data):
    """Test successful sprint data processing."""
    processed_data = process_sprint_data(sample_sprint_data)

    assert pd.api.types.is_datetime64_dtype(processed_data["start_date"])
    assert pd.api.types.is_datetime64_dtype(processed_data["end_date"])
    assert processed_data["start_date"].iloc[0] == pd.Timestamp("2024-01-01")
    assert processed_data["end_date"].iloc[1] == pd.Timestamp("2024-01-28")


def test_process_sprint_data_empty():
    """Test processing empty sprint data."""
    processed_data = process_sprint_data(pd.DataFrame())
    assert processed_data.empty


def test_process_sprint_data_invalid_dates():
    """Test processing sprint data with invalid dates."""
    invalid_data = pd.DataFrame(
        {
            "sprint_name": ["Sprint 1"],
            "start_date": ["invalid"],
            "end_date": ["2024-01-14"],
        }
    )
    processed_data = process_sprint_data(invalid_data)

    assert pd.isna(processed_data["start_date"].iloc[0])
    assert processed_data["end_date"].iloc[0] == pd.Timestamp("2024-01-14")


def test_process_sprint_data_missing_columns():
    """Test processing sprint data with missing columns."""
    incomplete_data = pd.DataFrame({"sprint_name": ["Sprint 1"]})
    processed_data = process_sprint_data(incomplete_data)

    assert "start_date" in processed_data.columns
    assert "end_date" in processed_data.columns
    assert pd.isna(processed_data["start_date"].iloc[0])
    assert pd.isna(processed_data["end_date"].iloc[0])

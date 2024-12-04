"""Tests for file upload handling."""

import io
from datetime import datetime

import pandas as pd
import pytest
import streamlit as st

from src.ui.dashboard.file_handler import (handle_file_upload,
                                           validate_csv_structure)


@pytest.fixture
def mock_csv_file():
    """Create a mock CSV file for testing."""
    csv_content = """Issue key,Sprint,Status,Story Points,Created,Updated,Resolved,Due Date
EFDDH-1,BP: EFDDH Sprint 21,Done,3,2024-01-01,2024-01-02,2024-01-03,2024-01-10
EFDDH-2,BP: EFDDH Sprint 21,In Progress,5,2024-01-01,2024-01-02,,2024-01-10
EFDDH-3,BP: EFDDH Sprint 20,Done,2,2023-12-15,2023-12-16,2023-12-17,2023-12-24"""
    return io.StringIO(csv_content)


@pytest.fixture
def mock_empty_csv():
    """Create an empty CSV file for testing."""
    return io.StringIO("")


@pytest.fixture
def mock_invalid_csv():
    """Create an invalid CSV file for testing."""
    return io.StringIO("Invalid,CSV,Content\nMissing,Required,Columns")


@pytest.mark.priority_high
@pytest.mark.dashboard
def test_validate_csv_structure():
    """Test CSV structure validation."""
    # Valid structure
    valid_df = pd.DataFrame(
        {
            "Issue key": ["EFDDH-1"],
            "Sprint": ["BP: EFDDH Sprint 21"],
            "Status": ["Done"],
            "Story Points": [3],
            "Created": ["2024-01-01"],
            "Updated": ["2024-01-02"],
            "Resolved": ["2024-01-03"],
            "Due Date": ["2024-01-10"],
        }
    )
    assert validate_csv_structure(valid_df)

    # Missing required columns
    invalid_df = pd.DataFrame(
        {"Issue key": ["EFDDH-1"], "Sprint": ["BP: EFDDH Sprint 21"]}
    )
    assert not validate_csv_structure(invalid_df)


@pytest.mark.priority_high
@pytest.mark.dashboard
def test_handle_file_upload_valid_file(mock_csv_file, monkeypatch):
    """Test file upload handling with valid CSV file."""

    def mock_file_uploader(*args, **kwargs):
        return mock_csv_file

    def mock_markdown(*args, **kwargs):
        pass

    monkeypatch.setattr("streamlit.file_uploader", mock_file_uploader)
    monkeypatch.setattr("streamlit.markdown", mock_markdown)

    df = handle_file_upload()

    assert not df.empty
    assert len(df) == 3
    assert "Issue key" in df.columns
    assert "Sprint" in df.columns
    assert "Status" in df.columns
    assert "Story Points" in df.columns

    # Check date columns
    date_columns = ["Created", "Updated", "Resolved", "Due Date"]
    for col in date_columns:
        assert pd.api.types.is_datetime64_any_dtype(df[col])


@pytest.mark.priority_high
@pytest.mark.dashboard
def test_handle_file_upload_empty_file(mock_empty_csv, monkeypatch):
    """Test file upload handling with empty CSV file."""

    def mock_file_uploader(*args, **kwargs):
        return mock_empty_csv

    def mock_markdown(*args, **kwargs):
        pass

    monkeypatch.setattr("streamlit.file_uploader", mock_file_uploader)
    monkeypatch.setattr("streamlit.markdown", mock_markdown)

    df = handle_file_upload()
    assert df.empty


@pytest.mark.priority_high
@pytest.mark.dashboard
def test_handle_file_upload_invalid_file(mock_invalid_csv, monkeypatch):
    """Test file upload handling with invalid CSV file."""

    def mock_file_uploader(*args, **kwargs):
        return mock_invalid_csv

    def mock_markdown(*args, **kwargs):
        pass

    monkeypatch.setattr("streamlit.file_uploader", mock_file_uploader)
    monkeypatch.setattr("streamlit.markdown", mock_markdown)

    df = handle_file_upload()
    assert df.empty


@pytest.mark.priority_medium
@pytest.mark.dashboard
def test_handle_file_upload_date_formats(monkeypatch):
    """Test handling of different date formats."""
    csv_content = """Issue key,Sprint,Status,Story Points,Created,Updated,Resolved,Due Date
EFDDH-1,BP: EFDDH Sprint 21,Done,3,2024-01-01,2024-01-02,2024-01-03T10:30:00,2024-01-04
EFDDH-2,BP: EFDDH Sprint 21,Done,5,2024-01-05,2024-01-05,2024-01-07T15:45:00,2024-01-08"""

    def mock_file_uploader(*args, **kwargs):
        return io.StringIO(csv_content)

    def mock_markdown(*args, **kwargs):
        pass

    monkeypatch.setattr("streamlit.file_uploader", mock_file_uploader)
    monkeypatch.setattr("streamlit.markdown", mock_markdown)

    df = handle_file_upload()

    assert not df.empty
    date_columns = ["Created", "Updated", "Resolved", "Due Date"]
    for col in date_columns:
        assert pd.api.types.is_datetime64_any_dtype(df[col])
        assert not df[col].isna().all()


@pytest.mark.priority_low
@pytest.mark.dashboard
def test_handle_file_upload_large_file(monkeypatch):
    """Test handling of large CSV files."""
    rows = []
    for i in range(1000):
        rows.append(
            f"EFDDH-{i},BP: EFDDH Sprint 21,Done,3,2024-01-01,"
            f"2024-01-02,2024-01-03,2024-01-10"
        )

    csv_content = (
        "Issue key,Sprint,Status,Story Points,Created,Updated,Resolved,Due Date\n"
        + "\n".join(rows)
    )

    def mock_file_uploader(*args, **kwargs):
        return io.StringIO(csv_content)

    def mock_markdown(*args, **kwargs):
        pass

    monkeypatch.setattr("streamlit.file_uploader", mock_file_uploader)
    monkeypatch.setattr("streamlit.markdown", mock_markdown)

    df = handle_file_upload()
    assert len(df) == 1000
    assert all(
        pd.api.types.is_datetime64_any_dtype(df[col])
        for col in ["Created", "Updated", "Resolved", "Due Date"]
    )

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from data.data_loader import load_data, prepare_data


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame(
        {
            "Issue key": ["TEST-1", "TEST-2"],
            "Created": ["2024-01-01", "2024-01-02"],
            "Updated": ["2024-01-02", "2024-01-03"],
            "Resolved": ["2024-01-03", None],
            "Due Date": ["2024-02-01", None],
            "Status": ["Done", "In Progress"],
            "Sprint": ["Sprint 1", "Sprint 2"],
            "Story Points": [5, 3],
            "Epic Name": ["Epic 1", "Epic 2"],
            "Priority": ["High", "Medium"],
            "Issue Type": ["Bug", "Story"],
        }
    )


@pytest.fixture
def mock_streamlit():
    """Mock streamlit components."""
    with patch("streamlit.error") as mock_error, patch(
        "streamlit.cache_data", lambda *args, **kwargs: lambda x: x
    ):
        yield {"error": mock_error}


@pytest.fixture
def mock_file(sample_data, tmp_path):
    """Create a mock CSV file."""
    file_path = tmp_path / "test.csv"
    sample_data.to_csv(file_path, index=False)
    return file_path


def test_load_data_success(mock_streamlit, mock_file, sample_data):
    """Test successful data loading."""
    df = load_data(mock_file)
    assert not df.empty
    assert "Issue key" in df.columns
    assert len(df) == 2
    assert not mock_streamlit["error"].called


def test_load_data_missing_file(mock_streamlit):
    """Test handling of missing file."""
    with patch("pathlib.Path.exists", return_value=False):
        df = load_data(Path("nonexistent.csv"))
        assert df.empty
        mock_streamlit["error"].assert_called_once()


def test_load_data_missing_columns(mock_streamlit, tmp_path):
    """Test handling of data with missing required columns."""
    invalid_data = pd.DataFrame({"Column1": [1, 2], "Column2": [3, 4]})
    test_file = tmp_path / "invalid.csv"
    invalid_data.to_csv(test_file, index=False)

    df = load_data(test_file)
    assert df.empty
    mock_streamlit["error"].assert_called_once()


def test_load_data_empty_file(mock_streamlit, tmp_path):
    """Test handling of empty file."""
    test_file = tmp_path / "empty.csv"
    pd.DataFrame().to_csv(test_file, index=False)

    df = load_data(test_file)
    assert df.empty
    mock_streamlit["error"].assert_called_once()


def test_prepare_data_success(sample_data):
    """Test successful data preparation."""
    df = prepare_data(sample_data)

    # Verify date conversions
    date_columns = ["Created", "Updated", "Resolved", "Due Date"]
    for col in date_columns:
        assert pd.api.types.is_datetime64_dtype(df[col])

    # Verify Story Points is numeric
    assert pd.api.types.is_numeric_dtype(df["Story Points"])

    # Verify Status handling
    assert df["Status"].fillna("In Progress").iloc[1] == "In Progress"

    # Verify Priority handling
    assert df["Priority"].fillna("Medium").iloc[1] == "Medium"

    # Verify Issue Type handling
    assert df["Issue Type"].fillna("Story").iloc[1] == "Story"

    # Verify Sprint handling
    assert df["Sprint"].fillna("No Sprint").iloc[0] == "Sprint 1"

    # Verify Epic Link handling
    assert df["Epic Name"].fillna("No Epic").iloc[0] == "Epic 1"


def test_prepare_data_empty():
    """Test preparation of empty DataFrame."""
    df = prepare_data(pd.DataFrame())
    assert df.empty


def test_prepare_data_missing_optional_columns(sample_data):
    """Test preparation with missing optional columns."""
    minimal_data = sample_data[["Issue key", "Created", "Status"]]
    df = prepare_data(minimal_data)
    assert not df.empty
    assert pd.api.types.is_datetime64_dtype(df["Created"])


def test_prepare_data_invalid_dates():
    """Test handling of invalid dates."""
    invalid_data = pd.DataFrame(
        {"Issue key": ["TEST-1"], "Created": ["invalid_date"], "Status": ["Done"]}
    )
    df = prepare_data(invalid_data)
    assert not df.empty
    assert pd.isna(df["Created"].iloc[0])


def test_prepare_data_error_handling(mock_streamlit):
    """Test error handling during data preparation."""
    with patch("pandas.to_datetime", side_effect=Exception("Test error")):
        df = prepare_data(pd.DataFrame({"Created": ["2024-01-01"]}))
        assert df.empty
        mock_streamlit["error"].assert_called_once()


def test_load_data_default_path(mock_streamlit):
    """Test loading data with default path."""
    with patch("pathlib.Path.exists", return_value=True), patch(
        "pandas.read_csv",
        return_value=pd.DataFrame(
            {"Issue key": ["TEST-1"], "Created": ["2024-01-01"], "Status": ["Done"]}
        ),
    ):
        df = load_data()
        assert not df.empty
        assert "Issue key" in df.columns
        assert not mock_streamlit["error"].called

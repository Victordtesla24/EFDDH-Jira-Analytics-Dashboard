from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from src.data.data_loader import load_data, prepare_data


@pytest.fixture(autouse=True)
def mock_cache(monkeypatch):
    """Mock streamlit cache decorator."""

    def mock_decorator(*args, **kwargs):
        def wrapper(func):
            def wrapped_func(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapped_func

        return wrapper

    monkeypatch.setattr("streamlit.cache_data", mock_decorator)


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "Created": ["01/01/2024", "03/01/2024"],
            "Resolved": ["02/01/2024", "04/01/2024"],
            "Priority": ["High", "Medium"],
            "Issue Type": ["Bug", "Story"],
            "Sprint": ["Sprint 1", "Sprint 1"],
            "Story Points": [5, None],  # Include null value
            "Epic Name": ["Epic 1", None],  # Include null value
            "Status": ["Done", None],  # Include null value
        }
    )


def test_load_data_default_path(mock_streamlit, sample_df):
    """Test loading data with default path."""
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("src.data.data_loader.pd.read_csv", return_value=sample_df),
    ):
        df = load_data()
        assert df is not None
        assert not df.empty
        assert isinstance(df, pd.DataFrame)


def test_load_data_custom_path(mock_streamlit, sample_df):
    """Test loading data with custom path."""
    custom_path = Path("custom/path.csv")
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("src.data.data_loader.pd.read_csv", return_value=sample_df),
    ):
        df = load_data(custom_path)
        assert df is not None
        assert not df.empty
        assert isinstance(df, pd.DataFrame)


def test_load_data_file_not_found(mock_streamlit):
    """Test handling of missing file."""
    test_path = Path("nonexistent.csv")
    with patch("pathlib.Path.exists", return_value=False):
        df = load_data(test_path)
        assert df is None
        assert mock_streamlit["error"].called
        error_msg = mock_streamlit["error"].call_args[0][0]
        assert "Failed to load data: Data file not found:" in error_msg
        assert str(test_path) in error_msg


def test_prepare_data_valid_input(sample_df):
    """Test data preparation with valid input including null values."""
    df = prepare_data(sample_df)
    assert df is not None
    assert "Created_Week" in df.columns

    # Verify null values are handled as expected
    assert df["Story Points"].iloc[1] == 0  # Null Story Points should be 0
    assert df["Epic Name"].iloc[1] == "No Epic"  # Null Epic Name should be "No Epic"
    # Null Status should be "In Progress"
    assert df["Status"].iloc[1] == "In Progress"

    # Verify date conversions
    assert isinstance(df["Created"].iloc[0], pd.Timestamp)
    assert isinstance(df["Created_Week"], pd.Series)


def test_prepare_data_all_null_values():
    """Test prepare_data with all null values."""
    df_all_nulls = pd.DataFrame(
        {
            "Created": [None, None],
            "Resolved": [None, None],
            "Priority": [None, None],
            "Issue Type": [None, None],
            "Sprint": [None, None],
            "Story Points": [None, None],
            "Epic Name": [None, None],
            "Status": [None, None],
        }
    )

    df = prepare_data(df_all_nulls)
    assert df is not None

    # Verify default values for null fields
    assert (df["Story Points"] == 0).all()
    assert (df["Epic Name"] == "No Epic").all()
    assert (df["Status"] == "In Progress").all()

    # Verify default date handling
    assert (df["Created"] == pd.Timestamp("2024-01-01")).all()
    assert pd.isna(df["Resolved"]).all()


def test_prepare_data_none_input():
    """Test prepare_data with None input."""
    result = prepare_data(None)
    assert result is None

from pathlib import Path

from src.data.data_loader import load_data, prepare_data


def test_load_data(test_data_path):
    """Test loading data from the actual CSV file."""
    df = load_data(test_data_path)
    assert df is not None
    assert not df.empty
    assert all(
        col in df.columns for col in ["Created", "Resolved", "Priority", "Issue Type", "Sprint"]
    )


def test_load_data_missing_file():
    """Test handling of missing data file."""
    df = load_data(Path("nonexistent.csv"))
    assert df is None


def test_prepare_data(sample_jira_data):
    """Test data preparation with actual data."""
    processed_df = prepare_data(sample_jira_data)
    assert "Created_Week" in processed_df.columns
    assert processed_df["Created"].dtype == "datetime64[ns]"
    assert processed_df["Resolved"].dtype == "datetime64[ns]"

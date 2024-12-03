import pandas as pd
import pytest

from src.utils.validation import (ensure_test_data, validate_epic_data,
                                  validate_input_data, validate_jira_data,
                                  validate_velocity_data)


@pytest.fixture
def valid_jira_data():
    """Create valid test data."""
    return pd.DataFrame(
        {
            "Issue key": ["TEST-1", "TEST-2"],
            "Created": ["2024-01-01", "2024-01-02"],
            "Resolved": ["2024-01-02", None],
            "Priority": ["High", "Medium"],
            "Issue Type": ["Bug", "Task"],
            "Sprint": ["Sprint 1", "Sprint 2"],
            "Status": ["Closed", "In Progress"],
            "Story Points": [5, 3],
            "Epic Name": ["Epic 1", "Epic 2"],
        }
    )


def test_validate_jira_data_valid(valid_jira_data):
    """Test validation with valid data."""
    assert validate_jira_data(valid_jira_data) is True


def test_validate_jira_data_missing_columns():
    """Test validation with missing required columns."""
    invalid_data = pd.DataFrame({"Issue key": ["TEST-1"], "Created": ["2024-01-01"]})
    assert validate_jira_data(invalid_data) is False


def test_validate_jira_data_empty():
    """Test validation with empty DataFrame."""
    empty_data = pd.DataFrame()
    assert validate_jira_data(empty_data) is False


def test_validate_jira_data_null_epic():
    """Test validation with null Epic Names."""
    data_null_epic = pd.DataFrame(
        {
            "Issue key": ["TEST-1", "TEST-2"],
            "Created": ["2024-01-01", "2024-01-02"],
            "Priority": ["High", "Medium"],
            "Epic Name": [None, None],
        }
    )
    assert validate_jira_data(data_null_epic) is False


def test_validate_jira_data_invalid_dates():
    """Test validation with invalid date formats."""
    data_invalid_dates = pd.DataFrame(
        {
            "Issue key": ["TEST-1"],
            "Created": ["invalid-date"],
            "Priority": ["High"],
            "Epic Name": ["Epic 1"],
        }
    )
    assert validate_jira_data(data_invalid_dates) is False


def test_validate_velocity_data_valid(valid_jira_data):
    """Test velocity data validation with valid data."""
    valid_jira_data["Story Points"] = [5, 3]
    assert validate_velocity_data(valid_jira_data) is True


def test_validate_velocity_data_missing_columns():
    """Test velocity data validation with missing columns."""
    invalid_data = pd.DataFrame({"Sprint": ["Sprint 1"]})
    assert validate_velocity_data(invalid_data) is False


def test_validate_velocity_data_non_numeric():
    """Test velocity data validation with non-numeric story points."""
    invalid_data = pd.DataFrame(
        {"Sprint": ["Sprint 1"], "Story Points": ["invalid"], "Status": ["Done"]}
    )
    assert validate_velocity_data(invalid_data) is False


def test_validate_epic_data_valid(valid_jira_data):
    """Test epic data validation with valid data."""
    valid_jira_data["Story Points"] = [5, 3]
    assert validate_epic_data(valid_jira_data) is True


def test_validate_epic_data_missing_columns():
    """Test epic data validation with missing columns."""
    invalid_data = pd.DataFrame({"Epic Name": ["Epic 1"]})
    assert validate_epic_data(invalid_data) is False


def test_validate_epic_data_null_epics():
    """Test epic data validation with all null epic names."""
    invalid_data = pd.DataFrame(
        {
            "Epic Name": [None, None],
            "Story Points": [5, 3],
            "Status": ["Done", "In Progress"],
        }
    )
    assert validate_epic_data(invalid_data) is False


def test_ensure_test_data_missing_file(mocker):
    """Test handling of missing test data file."""
    mocker.patch("pathlib.Path.exists", return_value=False)
    mock_stop = mocker.patch("streamlit.stop")
    mock_error = mocker.patch("streamlit.error")

    ensure_test_data()
    assert mock_error.called
    assert mock_stop.called


def test_ensure_test_data_invalid_format(mocker, tmp_path):
    """Test handling of invalid test data format."""
    # Create temporary invalid CSV file
    test_file = tmp_path / "test.csv"
    pd.DataFrame({"Invalid": ["data"]}).to_csv(test_file)

    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pandas.read_csv", return_value=pd.DataFrame({"Invalid": ["data"]}))
    mock_stop = mocker.patch("streamlit.stop")
    mock_error = mocker.patch("streamlit.error")

    ensure_test_data()
    assert mock_error.called
    assert "Invalid data format" in mock_error.call_args[0][0]
    assert mock_stop.called


def test_data_validation(valid_jira_data):
    """Test data validation with various input scenarios."""
    # Test with valid data
    assert validate_input_data(valid_jira_data, required_columns=["Priority", "Status"])

    # Test with missing columns
    invalid_data = pd.DataFrame({"Invalid": ["data"]})
    assert not validate_input_data(
        invalid_data, required_columns=["Priority", "Status"]
    )

    # Test with empty data
    assert not validate_input_data(
        pd.DataFrame(), required_columns=["Priority", "Status"]
    )

    # Test with None data
    assert not validate_input_data(None, required_columns=["Priority", "Status"])

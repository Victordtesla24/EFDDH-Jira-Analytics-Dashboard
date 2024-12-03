import pandas as pd

from src.data.processors import process_jira_data


def test_process_jira_data():
    """Test data processing functionality."""
    input_data = pd.DataFrame(
        {
            "Created": ["2024-01-01", "2024-01-02"],
            "Resolved": ["2024-01-02", None],
            "Priority": ["High", "Medium"],
            "Issue Type": ["Bug", "Task"],
            "Status": ["Closed", "In Progress"],
        }
    )

    processed_data = process_jira_data(input_data)

    # Verify date processing
    assert pd.api.types.is_datetime64_dtype(processed_data["Created"])
    assert pd.api.types.is_datetime64_dtype(processed_data["Resolved"])

    # Verify calculated fields
    assert "Resolution Time (Days)" in processed_data.columns
    assert processed_data["Resolution Time (Days)"].iloc[0] == 1
    assert pd.isna(processed_data["Resolution Time (Days)"].iloc[1])

    # Verify status categories
    assert "Status Category" in processed_data.columns
    assert processed_data["Status Category"].iloc[0] == "Done"
    assert processed_data["Status Category"].iloc[1] == "In Progress"

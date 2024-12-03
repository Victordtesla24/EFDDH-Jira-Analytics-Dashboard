import pandas as pd
import pytest
from src.pages.analytics import show_analytics
from src.components.visualizations import (
    show_charts,
    show_epic_progress,
    show_status_metrics,
    show_summary_metrics,
    show_timeline_analysis,
    show_velocity_metrics,
)


@pytest.fixture
def sample_jira_data():
    """Create sample data for testing."""
    return pd.DataFrame(
        {
            "Issue key": ["TEST-1", "TEST-2"],
            "Created": ["01/01/2024", "02/01/2024"],
            "Resolved": ["02/01/2024", "03/01/2024"],
            "Priority": ["High", "Medium"],
            "Issue Type": ["Bug", "Task"],
            "Sprint": ["Sprint 1", "Sprint 2"],
        }
    )


@pytest.fixture
def mock_streamlit(mocker):
    """Mock all required Streamlit components."""
    return {
        "plotly_chart": mocker.patch("streamlit.plotly_chart"),
        "header": mocker.patch("streamlit.header"),
        "error": mocker.patch("streamlit.error"),
        "metric": mocker.patch("streamlit.metric"),
        "warning": mocker.patch("streamlit.warning"),
    }


def test_show_charts(mock_streamlit, sample_jira_data, mocker):
    """Test chart generation and display."""
    # Add required columns if missing
    if "Issue Type" not in sample_jira_data.columns:
        sample_jira_data["Issue Type"] = ["Bug", "Task"]
    if "Priority" not in sample_jira_data.columns:
        sample_jira_data["Priority"] = ["High", "Medium"]

    # Mock plotly express
    mock_px = mocker.patch("src.components.visualizations.px")
    mock_bar = mocker.MagicMock()
    mock_pie = mocker.MagicMock()
    mock_px.bar.return_value = mock_bar
    mock_px.pie.return_value = mock_pie

    show_charts(sample_jira_data)

    # Verify plotly express calls
    assert mock_px.bar.called
    assert mock_px.pie.called
    assert mock_streamlit["plotly_chart"].call_count >= 2


def test_velocity_metrics(mock_streamlit, sample_jira_data):
    """Test velocity metrics calculation and display."""
    # Prepare minimal test data with only required fields
    test_data = pd.DataFrame(
        {
            "Story Points": [5, 3],
            "Created": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "Resolved": pd.to_datetime(["2024-01-15", "2024-01-16"]),
        }
    )

    show_velocity_metrics(test_data)

    # Verify only essential metrics
    assert mock_streamlit["metric"].called
    assert "Story Points" in str(mock_streamlit["metric"].call_args_list)


def test_epic_progress(mock_streamlit, sample_jira_data, mocker):
    """Test epic progress visualization."""
    # Add required columns to test data
    sample_jira_data["Epic Name"] = ["Epic 1", "Epic 2"]
    sample_jira_data["Story Points"] = [5, 3]
    sample_jira_data["Status"] = ["Closed", "In Progress"]

    mock_px = mocker.patch("src.components.visualizations.px")
    mock_bar = mocker.MagicMock()
    mock_px.bar.return_value = mock_bar

    show_epic_progress(sample_jira_data)

    # Verify epic metrics
    assert mock_px.bar.called
    assert mock_streamlit["plotly_chart"].called

    # Verify data calculations
    epic_data = sample_jira_data.groupby("Epic Name")["Story Points"].sum()
    assert not epic_data.empty


def test_visualization_components(mock_streamlit):
    """Test all visualization components with minimal data."""
    test_data = pd.DataFrame(
        {
            "Status": ["Done", "In Progress"],
            "Story Points": [5, 3],
            "Created": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "Resolved": pd.to_datetime(["2024-01-15", "2024-01-16"]),
            "Epic Name": ["Epic 1", "Epic 2"],
        }
    )

    # Test all visualization functions
    show_summary_metrics(test_data)
    show_velocity_metrics(test_data)
    show_epic_progress(test_data)
    show_timeline_analysis(test_data)

    # Verify essential functionality
    assert mock_streamlit["metric"].called
    assert mock_streamlit["plotly_chart"].called


def test_show_charts_empty_data(mock_streamlit):
    """Test chart generation with empty data."""
    empty_df = pd.DataFrame()
    show_charts(empty_df)
    assert mock_streamlit["error"].called
    assert "No data available" in str(mock_streamlit["error"].call_args[0][0])


def test_show_charts_missing_columns(mock_streamlit):
    """Test chart generation with missing columns."""
    incomplete_df = pd.DataFrame({"Other Column": [1, 2]})
    show_charts(incomplete_df)
    assert mock_streamlit["error"].called
    assert "Missing required columns" in str(mock_streamlit["error"].call_args[0][0])


def test_show_charts_null_values(mock_streamlit, sample_jira_data):
    """Test chart generation with null values."""
    data_with_nulls = sample_jira_data.copy()
    data_with_nulls.loc[0, "Issue Type"] = None
    show_charts(data_with_nulls)
    assert mock_streamlit["warning"].called or mock_streamlit["plotly_chart"].called


@pytest.mark.parametrize("column", ["Issue Type", "Priority"])
def test_show_charts_single_category(mock_streamlit, sample_jira_data, column):
    """Test chart generation with single category."""
    single_category_data = sample_jira_data.copy()
    single_category_data[column] = "Single Value"
    show_charts(single_category_data)
    assert mock_streamlit["plotly_chart"].called


def test_chart_styling(mock_streamlit, test_data):
    """Test chart styling and configuration."""
    # Add required columns
    test_data["Issue Type"] = ["Bug", "Story"]
    test_data["Priority"] = ["High", "Medium"]

    show_charts(test_data)

    # Verify charts were created
    assert mock_streamlit["plotly_chart"].called
    assert mock_streamlit["plotly_chart"].call_count >= 2  # At least issue type and priority charts


def test_chart_functionality(mock_streamlit, test_data):
    """Test chart functionality with actual data."""
    show_charts(test_data)
    
    # Verify charts were created
    assert mock_streamlit["plotly_chart"].called
    assert mock_streamlit["plotly_chart"].call_count >= 2


def test_metrics_functionality(mock_streamlit, test_data):
    """Test metrics display functionality."""
    show_analytics(test_data)
    
    # Verify metrics were displayed
    assert mock_streamlit["metric"].called
    assert mock_streamlit["metric"].call_count >= 3
    
    # Verify specific metrics
    metric_calls = [call[0] for call in mock_streamlit["metric"].call_args_list]
    metric_labels = [call[0] for call in metric_calls]
    
    expected_metrics = ["Total Story Points", "Total Issues", "Completed Issues"]
    for metric in expected_metrics:
        assert any(metric in label for label in metric_labels)

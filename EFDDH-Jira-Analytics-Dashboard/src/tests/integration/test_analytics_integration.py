import pandas as pd
import pytest
from datetime import datetime
from pathlib import Path
import numpy as np

from src.pages.analytics import show_analytics
from src.data.data_loader import load_data, prepare_data
from src.utils.ai_validation import validate_visualization_output
from src.utils.testing import capture_streamlit_output


@pytest.fixture
def test_data():
    """Use actual JIRA data for integration testing."""
    try:
        data_path = Path("data/EFDDH-Jira-Data-Sprint21.csv")
        df = load_data(data_path)
        return prepare_data(df)
    except Exception as e:
        pytest.skip(f"Could not load test data: {str(e)}")


def test_analytics_integration(mock_streamlit, test_data):
    """Test analytics integration focusing on visualizations."""
    with capture_streamlit_output() as output:
        show_analytics(test_data)

    # Verify specific charts are present
    chart_titles = [
        chart.layout.title.text
        for chart in output["charts"]
        if hasattr(chart, "layout") and hasattr(chart.layout, "title")
    ]

    expected_charts = [
        "Issue Type Distribution",
        "Priority Distribution",
        "Epic Progress Overview"
    ]

    for expected in expected_charts:
        assert any(expected in title for title in chart_titles), f"Missing chart: {expected}"

    # Verify metrics
    metrics_dict = {m["label"]: m["value"] for m in output["metrics"]}
    assert "Total Story Points" in metrics_dict
    assert "Total Issues" in metrics_dict
    assert "Completed Issues" in metrics_dict


def test_chart_rendering(mock_streamlit, test_data):
    """Test that charts render correctly with actual data."""
    with capture_streamlit_output() as output:
        show_analytics(test_data)

    # Check each chart has required attributes
    for chart in output["charts"]:
        assert hasattr(chart, "layout"), "Chart missing layout"
        assert hasattr(chart.layout, "title"), "Chart missing title"
        assert chart.data, "Chart has no data"


def test_metric_calculations(mock_streamlit, test_data):
    """Test metric calculations in analytics integration."""
    with capture_streamlit_output() as output:
        show_analytics(test_data)

    # Convert metrics to dictionary for easier testing
    metrics_dict = {m["label"]: m["value"] for m in output["metrics"]}

    # Verify essential metrics are present with correct types
    assert "Total Story Points" in metrics_dict, "Missing total story points metric"
    assert isinstance(
        metrics_dict["Total Story Points"], (str, int, float)
    ), "Invalid story points type"

    assert "Total Issues" in metrics_dict, "Missing total issues metric"
    assert isinstance(metrics_dict["Total Issues"], (int, np.integer)), "Invalid total issues type"

    assert "Avg Velocity (points/week)" in metrics_dict, "Missing velocity metric"

from unittest.mock import patch

import pytest

from src.utils.health_checks import (check_data_availability,
                                     check_metric_calculations,
                                     check_visualization_components,
                                     verify_dashboard_health)


def test_check_data_availability_success():
    with patch("src.utils.health_checks._check_data_sources", return_value=True):
        result = check_data_availability()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] is True
        assert result[1] == "Data sources available"


def test_check_data_availability_failure():
    with patch("src.utils.health_checks._check_data_sources", return_value=False):
        result = check_data_availability()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] is False
        assert result[1] == "Data sources unavailable"


def test_check_data_availability_error():
    with patch(
        "src.utils.health_checks._check_data_sources",
        side_effect=Exception("Test error"),
    ):
        result = check_data_availability()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] is False
        assert "Data source check failed: Test error" in result[1]


def test_check_metric_calculations_success():
    with patch("src.utils.health_checks._verify_metrics", return_value=True):
        result = check_metric_calculations()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] is True
        assert result[1] == "Metric calculations verified"


def test_check_metric_calculations_failure():
    with patch("src.utils.health_checks._verify_metrics", return_value=False):
        result = check_metric_calculations()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] is False
        assert result[1] == "Metric calculations failed"


def test_check_metric_calculations_error():
    with patch(
        "src.utils.health_checks._verify_metrics", side_effect=Exception("Test error")
    ):
        result = check_metric_calculations()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] is False
        assert "Metric calculation check failed: Test error" in result[1]


def test_check_visualization_components_success():
    with patch("src.utils.health_checks._verify_visualizations", return_value=True):
        result = check_visualization_components()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] is True
        assert result[1] == "Visualization components healthy"


def test_check_visualization_components_failure():
    with patch("src.utils.health_checks._verify_visualizations", return_value=False):
        result = check_visualization_components()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] is False
        assert result[1] == "Visualization components unhealthy"


def test_check_visualization_components_error():
    with patch(
        "src.utils.health_checks._verify_visualizations",
        side_effect=Exception("Test error"),
    ):
        result = check_visualization_components()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] is False
        assert "Visualization check failed: Test error" in result[1]


def test_verify_dashboard_health_all_success():
    with patch("src.utils.health_checks._check_data_sources", return_value=True), patch(
        "src.utils.health_checks._verify_metrics", return_value=True
    ), patch("src.utils.health_checks._verify_visualizations", return_value=True):
        result = verify_dashboard_health()
        assert isinstance(result, list)
        assert len(result) == 3
        for check in result:
            assert isinstance(check, tuple)
            assert len(check) == 2
            assert check[0] is True


def test_verify_dashboard_health_mixed_results():
    with patch("src.utils.health_checks._check_data_sources", return_value=True), patch(
        "src.utils.health_checks._verify_metrics", return_value=False
    ), patch(
        "src.utils.health_checks._verify_visualizations",
        side_effect=Exception("Test error"),
    ):
        result = verify_dashboard_health()
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0][0] is True  # Data check success
        assert result[1][0] is False  # Metric check failure
        assert result[2][0] is False  # Visualization check error

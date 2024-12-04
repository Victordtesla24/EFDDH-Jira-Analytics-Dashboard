import pytest
import logging
from src.utils.monitoring import MetricsMonitor

@pytest.fixture
def monitor():
    return MetricsMonitor()

def test_init():
    monitor = MetricsMonitor()
    assert monitor.metrics_history == []

def test_track_metric_performance(monitor):
    test_metrics = {"response_time": 100, "error_rate": 0.01}
    monitor.track_metric_performance(test_metrics)
    assert len(monitor.metrics_history) == 1
    assert monitor.metrics_history[0] == test_metrics

def test_track_multiple_metrics(monitor):
    metrics1 = {"response_time": 100, "error_rate": 0.01}
    metrics2 = {"response_time": 150, "error_rate": 0.02}

    monitor.track_metric_performance(metrics1)
    monitor.track_metric_performance(metrics2)

    assert len(monitor.metrics_history) == 2
    assert monitor.metrics_history[0] == metrics1
    assert monitor.metrics_history[1] == metrics2

def test_alert_on_failure(caplog):
    monitor = MetricsMonitor()
    test_error = Exception("Test error message")

    with caplog.at_level(logging.ERROR):
        monitor.alert_on_failure(test_error)

    assert "Metric failure detected: Test error message" in caplog.text

def test_alert_on_failure_with_custom_error(caplog):
    monitor = MetricsMonitor()

    class CustomError(Exception):
        pass

    test_error = CustomError("Custom error message")

    with caplog.at_level(logging.ERROR):
        monitor.alert_on_failure(test_error)

    assert "Metric failure detected: Custom error message" in caplog.text

def test_analyze_trends_with_insufficient_data(monitor):
    # Should not raise any errors with insufficient data
    for i in range(5):
        monitor.track_metric_performance({"value": i})
    assert len(monitor.metrics_history) == 5

def test_analyze_trends_with_sufficient_data(monitor):
    # Add more than 10 metrics to trigger trend analysis
    for i in range(15):
        monitor.track_metric_performance({"value": i})

    assert len(monitor.metrics_history) == 15
    # Verify the last 10 metrics are available for analysis
    recent_metrics = monitor.metrics_history[-10:]
    assert len(recent_metrics) == 10
    assert all(isinstance(m, dict) for m in recent_metrics)

def test_analyze_trends_with_exactly_ten_metrics(monitor):
    # Test boundary condition with exactly 10 metrics
    for i in range(10):
        monitor.track_metric_performance({"value": i})

    assert len(monitor.metrics_history) == 10
    recent_metrics = monitor.metrics_history[-10:]
    assert len(recent_metrics) == 10

def test_metrics_history_persistence(monitor):
    initial_metrics = {"response_time": 100}
    updated_metrics = {"response_time": 150}

    monitor.track_metric_performance(initial_metrics)
    assert monitor.metrics_history[0] == initial_metrics

    monitor.track_metric_performance(updated_metrics)
    assert len(monitor.metrics_history) == 2
    assert monitor.metrics_history[1] == updated_metrics
    # Ensure first metric wasn't overwritten
    assert monitor.metrics_history[0] == initial_metrics

def test_track_metric_performance_with_empty_metrics(monitor):
    empty_metrics = {}
    monitor.track_metric_performance(empty_metrics)
    assert len(monitor.metrics_history) == 1
    assert monitor.metrics_history[0] == empty_metrics

def test_track_metric_performance_with_none_values(monitor):
    metrics_with_none = {"value": None}
    monitor.track_metric_performance(metrics_with_none)
    assert len(monitor.metrics_history) == 1
    assert monitor.metrics_history[0]["value"] is None

def test_track_metric_performance_with_nested_dict(monitor):
    nested_metrics = {"outer": {"inner": 100, "other": {"deep": "value"}}}
    monitor.track_metric_performance(nested_metrics)
    assert len(monitor.metrics_history) == 1
    assert monitor.metrics_history[0] == nested_metrics

def test_track_metric_performance_with_list_values(monitor):
    metrics_with_list = {"values": [1, 2, 3], "names": ["a", "b", "c"]}
    monitor.track_metric_performance(metrics_with_list)
    assert len(monitor.metrics_history) == 1
    assert monitor.metrics_history[0] == metrics_with_list

def test_alert_on_failure_with_none_error(caplog):
    monitor = MetricsMonitor()
    with caplog.at_level(logging.ERROR):
        monitor.alert_on_failure(None)
    assert "Metric failure detected: None" in caplog.text

def test_analyze_trends_with_mixed_metric_types(monitor):
    # Test handling of different metric types in trend analysis
    metrics = [
        {"value": 1, "type": "numeric"},
        {"value": "string", "type": "text"},
        {"value": True, "type": "boolean"},
        {"value": None, "type": "null"},
        {"value": [1, 2, 3], "type": "list"},
        {"value": {"nested": "dict"}, "type": "dict"},
    ]
    for metric in metrics:
        monitor.track_metric_performance(metric)

    assert len(monitor.metrics_history) == len(metrics)
    assert all(m == e for m, e in zip(monitor.metrics_history, metrics))

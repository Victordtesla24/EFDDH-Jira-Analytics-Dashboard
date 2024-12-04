import pytest
from unittest.mock import MagicMock, patch
import streamlit as st

from src.utils.testing import capture_streamlit_output

@pytest.fixture
def mock_streamlit():
    # Store original functions
    original_funcs = {
        "plotly_chart": getattr(st, "plotly_chart", None),
        "metric": getattr(st, "metric", None),
        "error": getattr(st, "error", None),
        "warning": getattr(st, "warning", None),
    }

    yield

    # Restore original functions after test
    for func_name, func in original_funcs.items():
        if func is not None:
            setattr(st, func_name, func)

def test_capture_plotly_chart(mock_streamlit):
    mock_figure = MagicMock()

    with capture_streamlit_output() as output:
        st.plotly_chart(mock_figure)

    assert len(output["charts"]) == 1
    assert output["charts"][0] == mock_figure

def test_capture_metric(mock_streamlit):
    with capture_streamlit_output() as output:
        st.metric("Test Label", 42)

    assert len(output["metrics"]) == 1
    assert output["metrics"][0]["label"] == "Test Label"
    assert output["metrics"][0]["value"] == 42

def test_capture_error(mock_streamlit):
    with capture_streamlit_output() as output:
        st.error("Test Error")

    assert len(output["errors"]) == 1
    assert output["errors"][0] == "Test Error"

def test_capture_warning(mock_streamlit):
    with capture_streamlit_output() as output:
        st.warning("Test Warning")

    assert len(output["warnings"]) == 1
    assert output["warnings"][0] == "Test Warning"

def test_capture_multiple_outputs(mock_streamlit):
    mock_figure1 = MagicMock()
    mock_figure2 = MagicMock()

    with capture_streamlit_output() as output:
        st.plotly_chart(mock_figure1)
        st.metric("Label 1", 42)
        st.error("Error 1")
        st.warning("Warning 1")
        st.plotly_chart(mock_figure2)
        st.metric("Label 2", 84)

    assert len(output["charts"]) == 2
    assert len(output["metrics"]) == 2
    assert len(output["errors"]) == 1
    assert len(output["warnings"]) == 1

    assert output["metrics"][0]["label"] == "Label 1"
    assert output["metrics"][1]["label"] == "Label 2"
    assert output["errors"][0] == "Error 1"
    assert output["warnings"][0] == "Warning 1"

def test_nested_context_managers(mock_streamlit):
    with capture_streamlit_output() as outer:
        st.error("Outer Error")
        with capture_streamlit_output() as inner:
            st.error("Inner Error")
        st.warning("Outer Warning")

    assert len(outer["errors"]) == 1
    assert outer["errors"][0] == "Outer Error"
    assert len(outer["warnings"]) == 1
    assert outer["warnings"][0] == "Outer Warning"

    assert len(inner["errors"]) == 1
    assert inner["errors"][0] == "Inner Error"
    assert len(inner["warnings"]) == 0

def test_exception_handling(mock_streamlit):
    try:
        with capture_streamlit_output() as output:
            st.error("Test Error")
            raise ValueError("Test Exception")
    except ValueError:
        pass

    assert len(output["errors"]) == 1
    assert output["errors"][0] == "Test Error"

def test_kwargs_handling(mock_streamlit):
    mock_figure = MagicMock()

    with capture_streamlit_output() as output:
        st.plotly_chart(mock_figure, use_container_width=True)
        st.metric("Test Label", 42, delta=5)
        st.error("Test Error", icon="🚨")

    assert len(output["charts"]) == 1
    assert len(output["metrics"]) == 1
    assert len(output["errors"]) == 1

def test_function_restoration_after_exception():
    original_plotly = getattr(st, "plotly_chart", None)

    try:
        with capture_streamlit_output():
            raise RuntimeError("Test error")
    except RuntimeError:
        pass

    current_plotly = getattr(st, "plotly_chart", None)
    assert current_plotly == original_plotly

def test_missing_original_functions():
    with patch.object(st, "plotly_chart", None):
        with patch.object(st, "metric", None):
            with capture_streamlit_output() as output:
                # These should not raise errors even though original functions are None
                st.error("Test Error")
                st.warning("Test Warning")

            assert len(output["errors"]) == 1
            assert len(output["warnings"]) == 1

def test_none_values_in_outputs():
    with capture_streamlit_output() as output:
        st.metric("Test Label", None)
        st.error(None)
        st.warning(None)

    assert len(output["metrics"]) == 1
    assert output["metrics"][0]["value"] is None
    assert len(output["errors"]) == 1
    assert output["errors"][0] == "None"
    assert len(output["warnings"]) == 1
    assert output["warnings"][0] == "None"

def test_complex_kwargs():
    mock_figure = MagicMock()
    complex_kwargs = {
        "use_container_width": True,
        "theme": {"background": "#ffffff"},
        "config": {"responsive": True},
        "key": "test_key",
        "help": "test help text",
        "on_change": lambda x: x,
    }

    with capture_streamlit_output() as output:
        st.plotly_chart(mock_figure, **complex_kwargs)
        st.metric("Test Label", 42, delta=5, delta_color="normal", help="test")
        st.error("Test Error", icon="🚨", help="error help")

    assert len(output["charts"]) == 1
    assert len(output["metrics"]) == 1
    assert len(output["errors"]) == 1

def test_multiple_exceptions():
    original_funcs = {
        "plotly_chart": getattr(st, "plotly_chart", None),
        "metric": getattr(st, "metric", None),
    }

    try:
        with capture_streamlit_output():
            st.metric("Test Label", 42)
            raise ValueError("First error")
    except ValueError:
        try:
            with capture_streamlit_output():
                st.error("Another Error")
                raise RuntimeError("Second error")
        except RuntimeError:
            pass

    # Verify original functions are restored
    for func_name, original_func in original_funcs.items():
        assert getattr(st, func_name, None) == original_func

def test_empty_context():
    with capture_streamlit_output() as output:
        pass

    assert output["charts"] == []
    assert output["metrics"] == []
    assert output["errors"] == []
    assert output["warnings"] == []

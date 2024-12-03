from contextlib import contextmanager
import streamlit as st
from typing import Dict, Any


@contextmanager
def capture_streamlit_output():
    """
    Context manager to capture Streamlit output for testing.

    Yields:
        Dict containing captured Streamlit output
    """
    output = {"charts": [], "metrics": [], "errors": [], "warnings": []}

    # Mock Streamlit functions to capture output
    def mock_plotly_chart(fig, **kwargs):
        output["charts"].append(fig)

    def mock_metric(label, value, **kwargs):
        output["metrics"].append({"label": label, "value": value})

    def mock_error(msg, **kwargs):
        output["errors"].append(str(msg))

    def mock_warning(msg, **kwargs):
        output["warnings"].append(str(msg))

    # Store original functions
    original_funcs = {
        "plotly_chart": getattr(st, "plotly_chart", None),
        "metric": getattr(st, "metric", None),
        "error": getattr(st, "error", None),
        "warning": getattr(st, "warning", None),
    }

    # Replace with mocks
    st.plotly_chart = mock_plotly_chart
    st.metric = mock_metric
    st.error = mock_error
    st.warning = mock_warning

    try:
        yield output
    finally:
        # Restore original functions
        for func_name, func in original_funcs.items():
            if func is not None:
                setattr(st, func_name, func)

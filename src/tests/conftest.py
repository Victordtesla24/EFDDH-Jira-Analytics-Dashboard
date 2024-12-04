"""Shared test fixtures."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from unittest.mock import MagicMock

import pandas as pd
import pytest


@pytest.fixture
def mock_streamlit():
    """Mock common Streamlit functions."""

    class MockStreamlit:
        def __init__(self):
            self.markdown_calls = []
            self.metric_calls = []
            self.multiselect_calls = []
            self.date_input_calls = []

        def markdown(self, *args, **kwargs):
            self.markdown_calls.append((args, kwargs))

        def metric(self, *args, **kwargs):
            self.metric_calls.append((args, kwargs))

        def multiselect(self, *args, **kwargs):
            self.multiselect_calls.append((args, kwargs))
            return []

        def date_input(self, *args, **kwargs):
            self.date_input_calls.append((args, kwargs))
            return datetime.now()

    mock_st = MockStreamlit()
    return mock_st


@pytest.fixture
def sample_sprint_data():
    """Create sample sprint data for testing."""
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(14)]

    return pd.DataFrame(
        {
            "Sprint": ["BP: EFDDH Sprint 21"] * 5,
            "Status": ["Done", "In Progress", "Done", "To Do", "Done"],
            "Story Points": [3, 5, 2, 1, 3],
            "Created": [dates[0]] * 5,  # All created at sprint start
            "Resolved": [
                dates[3],
                None,
                dates[7],
                None,
                dates[10],
            ],  # Some resolved during sprint
            "Issue key": ["EFDDH-1", "EFDDH-2", "EFDDH-3", "EFDDH-4", "EFDDH-5"],
        }
    )


@pytest.fixture
def mock_plotly_chart():
    """Mock Plotly chart rendering."""
    return MagicMock()


@pytest.fixture
def mock_file_upload_context():
    """Mock file upload context with Streamlit components."""

    class MockUploadContext:
        def __init__(self):
            self.uploaded_file = None
            self.markdown_calls = []

        def set_uploaded_file(self, file):
            self.uploaded_file = file

        def markdown(self, *args, **kwargs):
            self.markdown_calls.append((args, kwargs))

    return MockUploadContext()

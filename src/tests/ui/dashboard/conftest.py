"""Shared test fixtures for dashboard tests."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import plotly.graph_objects
import pytest
import streamlit as st


@pytest.fixture
def sample_dates():
    """Create sample dates for testing."""
    start_date = datetime(2024, 1, 1)
    return [start_date + timedelta(days=i) for i in range(14)]


@pytest.fixture
def sample_sprint_data(sample_dates):
    """Create comprehensive sample sprint data for testing."""
    data = []
    sprints = [f"BP: EFDDH Sprint {i}" for i in range(19, 22)]  # Sprints 19-21

    issue_types = ["Story", "Bug", "Epic", "Task"]
    priorities = ["Highest", "High", "Medium", "Low"]
    statuses = ["Done", "In Progress", "To Do", "Story Done", "Closed"]

    issue_counter = 1
    for sprint in sprints:
        num_issues = 10 if sprint == "BP: EFDDH Sprint 21" else 8
        for i in range(num_issues):
            created_date = sample_dates[i % len(sample_dates)]
            resolved_date = created_date + timedelta(days=3) if i % 3 == 0 else None

            data.append(
                {
                    "Issue key": f"EFDDH-{issue_counter}",
                    "Sprint": sprint,
                    "Issue Type": issue_types[i % len(issue_types)],
                    "Priority": priorities[i % len(priorities)],
                    "Status": statuses[i % len(statuses)],
                    "Story Points": (i % 8) + 1,  # Points 1-8
                    "Created": created_date,
                    "Updated": created_date + timedelta(days=1),
                    "Resolved": resolved_date,
                    "Due Date": created_date + timedelta(days=14),
                }
            )
            issue_counter += 1

    return pd.DataFrame(data)


@pytest.fixture
def empty_sprint_data():
    """Create empty DataFrame with correct columns."""
    return pd.DataFrame(
        columns=[
            "Issue key",
            "Sprint",
            "Issue Type",
            "Priority",
            "Status",
            "Story Points",
            "Created",
            "Updated",
            "Resolved",
            "Due Date",
        ]
    )


@pytest.fixture
def mock_streamlit(monkeypatch):
    """Mock common Streamlit functions."""

    class MockDelta:
        def __init__(self):
            self.markdown_calls = []
            self.metric_calls = []

    mock_delta = MockDelta()

    def mock_markdown(*args, **kwargs):
        mock_delta.markdown_calls.append((args, kwargs))

    def mock_metric(*args, **kwargs):
        mock_delta.metric_calls.append((args, kwargs))

    monkeypatch.setattr("streamlit.markdown", mock_markdown)
    monkeypatch.setattr("streamlit.metric", mock_metric)

    return mock_delta


@pytest.fixture
def mock_plotly_figure(monkeypatch):
    """Mock Plotly figure creation."""

    class MockFigure:
        def __init__(self, *args, **kwargs):
            self.data = []
            self.layout = type(
                "MockLayout",
                (),
                {
                    "title": type("MockTitle", (), {"text": ""}),
                    "xaxis": type(
                        "MockXAxis", (), {"title": type("MockTitle", (), {"text": ""})}
                    ),
                    "yaxis": type(
                        "MockYAxis", (), {"title": type("MockTitle", (), {"text": ""})}
                    ),
                    "showlegend": True,
                    "hovermode": None,
                    "plot_bgcolor": None,
                    "paper_bgcolor": None,
                    "margin": None,
                },
            )

        def add_trace(self, trace):
            self.data.append(trace)
            return self

        def update_layout(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self.layout, key, value)
            return self

    monkeypatch.setattr("plotly.graph_objects.Figure", MockFigure)
    return MockFigure


@pytest.fixture
def mock_file_upload_context(monkeypatch):
    """Mock file upload context with Streamlit components."""

    class MockUploadContext:
        def __init__(self):
            self.uploaded_file = None
            self.markdown_calls = []

        def set_uploaded_file(self, file):
            self.uploaded_file = file

    context = MockUploadContext()

    def mock_file_uploader(*args, **kwargs):
        return context.uploaded_file

    def mock_markdown(*args, **kwargs):
        context.markdown_calls.append((args, kwargs))

    monkeypatch.setattr("streamlit.file_uploader", mock_file_uploader)
    monkeypatch.setattr("streamlit.markdown", mock_markdown)

    return context

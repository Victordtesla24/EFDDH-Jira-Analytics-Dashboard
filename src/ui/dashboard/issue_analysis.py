"""Issue analysis visualization functionality."""

from typing import Any, Dict, List, Optional, Union

import pandas as pd
import plotly.graph_objects as go


def create_issue_types_chart(data: pd.DataFrame) -> go.Figure:
    """Create issue types distribution chart."""
    fig = go.Figure()

    if not data.empty and "Issue Type" in data.columns:
        type_counts = data["Issue Type"].value_counts()
        fig.add_trace(
            go.Bar(x=type_counts.index, y=type_counts.values, marker_color="#007DBA")
        )
    else:
        # Add empty trace for consistent layout
        fig.add_trace(go.Bar(x=["No Data"], y=[0], marker_color="#007DBA"))

    fig.update_layout(
        title="Sprint Issue Types",
        xaxis_title="Issue Type",
        yaxis_title="Count",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig


def create_priority_distribution(data: pd.DataFrame) -> go.Figure:
    """Create priority distribution chart."""
    fig = go.Figure()

    if not data.empty and "Priority" in data.columns:
        priority_counts = data["Priority"].value_counts()
        fig.add_trace(
            go.Bar(
                x=priority_counts.index,
                y=priority_counts.values,
                marker_color="#00A3BF",
            )
        )
    else:
        # Add empty trace for consistent layout
        fig.add_trace(go.Bar(x=["No Data"], y=[0], marker_color="#00A3BF"))

    fig.update_layout(
        title="Issue Priority Distribution",
        xaxis_title="Priority",
        yaxis_title="Count",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig


def create_story_points_distribution(data: pd.DataFrame) -> go.Figure:
    """Create story points distribution chart."""
    fig = go.Figure()

    if not data.empty and "Story Points" in data.columns:
        points_data = data["Story Points"].dropna()
        if not points_data.empty:
            fig.add_trace(
                go.Histogram(x=points_data, nbinsx=10, marker_color="#36B37E")
            )
    else:
        # Add empty trace for consistent layout
        fig.add_trace(go.Histogram(x=[0], nbinsx=1, marker_color="#36B37E"))

    fig.update_layout(
        title="Story Points Distribution",
        xaxis_title="Story Points",
        yaxis_title="Count",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig


def create_daily_created_trend(data: pd.DataFrame) -> go.Figure:
    """Create daily created issues trend chart."""
    fig = go.Figure()

    if not data.empty and "Created" in data.columns:
        daily_counts = data["Created"].value_counts().sort_index()
        fig.add_trace(
            go.Scatter(
                x=daily_counts.index,
                y=daily_counts.values,
                mode="lines+markers",
                marker_color="#FF5630",
                line_color="#FF5630",
            )
        )
    else:
        # Add empty trace for consistent layout
        fig.add_trace(
            go.Scatter(
                x=[pd.Timestamp.now()],
                y=[0],
                mode="lines+markers",
                marker_color="#FF5630",
                line_color="#FF5630",
            )
        )

    fig.update_layout(
        title="Daily Created Issues",
        xaxis_title="Date",
        yaxis_title="Number of Issues",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig

import logging

import pandas as pd
import plotly.express as px
import streamlit as st

from src.utils.formatting import get_anz_template

logger = logging.getLogger(__name__)


def show_charts(data: pd.DataFrame) -> None:
    """Display charts for JIRA data analysis."""
    if data.empty:
        st.error("No data available for visualization")
        return

    # Ensure Created column is datetime
    data = data.copy()
    data["Created"] = pd.to_datetime(data["Created"])

    # Create weekly trend chart
    weekly_data = (
        data.groupby(pd.Grouper(key="Created", freq="W"))
        .size()
        .reset_index(name="count")
    )
    fig = px.line(
        weekly_data,
        x="Created",
        y="count",
        title="Weekly Issue Creation Trend",
        template=get_anz_template(),
    )
    st.plotly_chart(fig, use_container_width=True)


def show_epic_progress(data: pd.DataFrame) -> None:
    """Show epic progress visualization."""
    if data.empty:
        st.error("No data available for epic progress visualization")
        return

    # Ensure required columns exist
    required_cols = ["Epic Name", "Story Points", "Status"]
    if not all(col in data.columns for col in required_cols):
        st.error("Missing required columns for epic progress visualization")
        return

    # Prepare data
    epic_data = (
        data.groupby("Epic Name")
        .agg({"Story Points": "sum", "Status": lambda x: (x == "Done").sum()})
        .reset_index()
    )

    epic_data.columns = ["Epic Name", "Total Points", "Completed"]
    epic_data["In Progress"] = epic_data["Total Points"] - epic_data["Completed"]

    # Create visualization
    fig = px.bar(
        epic_data,
        x="Epic Name",
        y=["Completed", "In Progress"],
        title="Epic Progress Overview",
        template=get_anz_template(),
        barmode="stack",
    )
    st.plotly_chart(fig, use_container_width=True)


def show_velocity_metrics(data: pd.DataFrame) -> None:
    """Show velocity metrics."""
    if data.empty:
        st.error("No data available for velocity metrics")
        return

    # Clean data
    metrics_data = data.copy()
    metrics_data = metrics_data.dropna(subset=["Story Points", "Status"])

    # Calculate metrics only for completed items
    completed = metrics_data[metrics_data["Status"] == "Done"]

    if len(completed) == 0:
        st.warning("No completed items found for velocity calculation")
        return

    # Calculate velocity (points per week)
    velocity = completed["Story Points"].sum() / max(1, len(completed))

    # Display metrics
    cols = st.columns(2)
    with cols[0]:
        st.metric("Average Velocity", f"{velocity:.1f} points/week")
    with cols[1]:
        st.metric("Completed Stories", len(completed))

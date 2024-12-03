import logging
from typing import Callable, List

import pandas as pd
import plotly.express as px  # type: ignore
import streamlit as st
from plotly.graph_objects import Figure  # type: ignore

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
    weekly_counts = data.groupby(pd.Grouper(key="Created", freq="W")).size()
    weekly_data = pd.DataFrame(
        {"Created": weekly_counts.index, "count": weekly_counts.values}
    )

    fig: Figure = px.line(
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
    required_cols: List[str] = ["Epic Name", "Story Points", "Status"]
    if not all(col in data.columns for col in required_cols):
        st.error("Missing required columns for epic progress visualization")
        return

    # Prepare data
    status_agg: Callable[[pd.Series], int] = lambda x: (x == "Done").sum()
    epic_data = (
        data.groupby("Epic Name")
        .agg({"Story Points": "sum", "Status": status_agg})
        .reset_index()
    )

    # Create new DataFrame with desired columns
    epic_data = pd.DataFrame(
        {
            "Epic Name": epic_data["Epic Name"],
            "Total Points": epic_data["Story Points"],
            "Completed": epic_data["Status"],
        }
    )
    epic_data["In Progress"] = epic_data["Total Points"] - epic_data["Completed"]

    # Create visualization
    fig: Figure = px.bar(
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


def show_capacity_management(data: pd.DataFrame) -> None:
    """Show capacity management visualization."""
    if data is None or data.empty:
        st.error("No data available for capacity management")
        return

    st.title("Team Capacity Management")

    # Calculate team capacity metrics
    total_story_points = data["Story Points"].fillna(0).sum()
    completed_points = data[data["Status"] == "Done"]["Story Points"].fillna(0).sum()
    in_progress_points = (
        data[data["Status"] == "In Progress"]["Story Points"].fillna(0).sum()
    )

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Story Points", f"{total_story_points:.0f}")
    with col2:
        st.metric("Completed Points", f"{completed_points:.0f}")
    with col3:
        st.metric("In Progress Points", f"{in_progress_points:.0f}")

    # Create capacity trend visualization
    st.subheader("Capacity Trend")
    weekly_points = data.groupby(pd.Grouper(key="Created", freq="W"))[
        "Story Points"
    ].sum()
    weekly_capacity = pd.DataFrame(
        {"Created": weekly_points.index, "Story Points": weekly_points.values}
    )

    fig = px.line(
        weekly_capacity,
        x="Created",
        y="Story Points",
        title="Weekly Capacity Trend",
        template=get_anz_template(),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Show team workload distribution
    st.subheader("Team Workload Distribution")
    if "Assignee" in data.columns:
        assignee_load = (
            data[data["Status"] != "Done"]
            .groupby("Assignee")["Story Points"]
            .sum()
            .sort_values(ascending=False)
        )
        workload_data = pd.DataFrame(
            {"Assignee": assignee_load.index, "Story Points": assignee_load.values}
        )
        fig = px.bar(
            workload_data,
            x="Assignee",
            y="Story Points",
            title="Current Team Workload",
            template=get_anz_template(),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Assignee information not available for workload distribution")

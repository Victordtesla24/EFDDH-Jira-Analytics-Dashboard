"""Visualization components for analytics."""

import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import plotly.express as px
import streamlit as st
from plotly.graph_objects import Figure

logger = logging.getLogger(__name__)


def get_chart_layout():
    """Get base chart layout settings."""
    return {
        "font": {"family": "Arial, sans-serif", "size": 12},
        "showlegend": True,
        "plot_bgcolor": "#FFFFFF",
        "paper_bgcolor": "#FFFFFF",
        "margin": dict(l=40, r=40, t=40, b=40),
    }


def validate_data(
    data: Optional[pd.DataFrame], required_cols: List[str] = None
) -> bool:
    """Validate DataFrame has required columns and is not empty."""
    if data is None or data.empty:
        return False
    if required_cols and not all(col in data.columns for col in required_cols):
        return False
    return True


def is_completed_status(status: str) -> bool:
    """Check if a status represents completion."""
    return status.lower() in ["done", "closed", "story done", "epic done"]


def calculate_velocity_metrics(
    data: Optional[pd.DataFrame],
) -> Dict[str, Union[float, int]]:
    """Calculate velocity metrics from data."""
    if not validate_data(data, ["Status", "Story Points"]):
        return {"velocity": 0.0, "completed": 0}

    try:
        completed_data = data[data["Status"].apply(is_completed_status)]
        total_points = completed_data["Story Points"].fillna(0).sum()
        num_completed = len(completed_data)

        # Assuming 2-week sprints for velocity calculation
        velocity = total_points / 2 if num_completed > 0 else 0.0

        return {"velocity": velocity, "completed": num_completed}
    except Exception as e:
        logger.error(f"Error calculating velocity metrics: {str(e)}")
        return {"velocity": 0.0, "completed": 0}


def show_charts(data: pd.DataFrame) -> None:
    """Display charts for JIRA data analysis."""
    if not validate_data(data, ["Created"]):
        st.error("No data available for visualization")
        return

    try:
        # Create weekly trend chart
        weekly_counts = (
            data.groupby(pd.Grouper(key="Created", freq="W"))
            .size()
            .reset_index(name="count")
        )

        fig = px.line(
            weekly_counts,
            x="Created",
            y="count",
            title="Weekly Issue Creation Trend",
            template="plotly_white",
        )
        fig.update_layout(
            **get_chart_layout(), xaxis_title="Date", yaxis_title="Number of Issues"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Add Priority Distribution if available
        if "Priority" in data.columns:
            priority_counts = data["Priority"].value_counts()
            fig = px.pie(
                values=priority_counts.values,
                names=priority_counts.index,
                title="Issue Priority Distribution",
                template="plotly_white",
            )
            fig.update_layout(**get_chart_layout())
            st.plotly_chart(fig, use_container_width=True)

        # Add Issue Type Distribution if available
        if "Issue Type" in data.columns:
            type_counts = data["Issue Type"].value_counts()
            fig = px.bar(
                x=type_counts.index,
                y=type_counts.values,
                title="Issue Type Distribution",
                template="plotly_white",
            )
            fig.update_layout(
                **get_chart_layout(), xaxis_title="Issue Type", yaxis_title="Count"
            )
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        logger.error(f"Error creating charts: {str(e)}")
        st.error("Failed to create visualization")


def show_epic_progress(data: pd.DataFrame) -> None:
    """Show epic progress visualization."""
    if not validate_data(data, ["Epic Name", "Story Points", "Status"]):
        st.error("No data available for epic progress")
        return

    try:
        # Calculate epic progress
        data["Completed"] = data["Status"].apply(is_completed_status)
        epic_data = (
            data.groupby("Epic Name")
            .agg(
                {
                    "Story Points": "sum",
                    "Completed": lambda x: sum(x) * 1.0,  # Convert to float
                }
            )
            .reset_index()
        )

        # Filter out empty epics and null Epic Names
        epic_data = epic_data[
            (epic_data["Story Points"] > 0) & (epic_data["Epic Name"].notna())
        ]

        if not epic_data.empty:
            epic_data["Progress"] = (
                epic_data["Completed"] / epic_data["Story Points"] * 100
            ).round(1)

            fig = px.bar(
                epic_data,
                x="Epic Name",
                y="Progress",
                title="Epic Progress (%)",
                template="plotly_white",
                text=epic_data["Progress"].apply(lambda x: f"{x:.1f}%"),
            )
            fig.update_layout(
                **get_chart_layout(), xaxis_title="Epic", yaxis_title="Completion (%)"
            )
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No epic progress data available")

    except Exception as e:
        logger.error(f"Error creating epic progress: {str(e)}")
        st.error("Failed to create epic progress visualization")


def show_velocity_metrics(data: pd.DataFrame) -> None:
    """Show velocity metrics."""
    if not validate_data(data, ["Story Points", "Status"]):
        st.error("No data available for velocity metrics")
        return

    try:
        metrics = calculate_velocity_metrics(data)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average Velocity", f"{metrics['velocity']:.1f} points/sprint")
        with col2:
            st.metric("Completed Stories", metrics["completed"])

    except Exception as e:
        logger.error(f"Error showing velocity metrics: {str(e)}")
        st.error("Failed to display velocity metrics")


def show_capacity_management(data: pd.DataFrame) -> None:
    """Show capacity management visualization."""
    if not validate_data(data, ["Story Points", "Status", "Assignee"]):
        st.error("No data available for capacity management")
        return

    try:
        st.title("Team Capacity Management")

        # Calculate capacity metrics
        data["Completed"] = data["Status"].apply(is_completed_status)
        metrics = {
            "Total Story Points": data["Story Points"].fillna(0).sum(),
            "Completed Points": data[data["Completed"]]["Story Points"].fillna(0).sum(),
            "In Progress Points": data[~data["Completed"]]["Story Points"]
            .fillna(0)
            .sum(),
        }

        # Display metrics
        cols = st.columns(3)
        for i, (label, value) in enumerate(metrics.items()):
            with cols[i]:
                st.metric(label, f"{value:.0f}")

        # Show team workload distribution
        workload_data = (
            data[~data["Completed"]]
            .groupby("Assignee")["Story Points"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        if not workload_data.empty:
            fig = px.bar(
                workload_data,
                x="Assignee",
                y="Story Points",
                title="Current Team Workload",
                template="plotly_white",
                text=workload_data["Story Points"].round(1),
            )
            fig.update_layout(
                **get_chart_layout(),
                xaxis_title="Team Member",
                yaxis_title="Story Points",
            )
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

            # Add workload distribution pie chart
            fig = px.pie(
                workload_data,
                values="Story Points",
                names="Assignee",
                title="Workload Distribution",
                template="plotly_white",
            )
            fig.update_layout(**get_chart_layout())
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No workload data available")

    except Exception as e:
        logger.error(f"Error in capacity management: {str(e)}")
        st.error("Failed to display capacity management")

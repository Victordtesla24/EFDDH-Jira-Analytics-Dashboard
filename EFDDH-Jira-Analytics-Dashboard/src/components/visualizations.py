import pandas as pd
import plotly.express as px
import streamlit as st
import logging
from typing import Optional, Dict, Any, List

from src.config.settings import settings

logger = logging.getLogger(__name__)


def get_chart_template():
    """Get common chart template with ANZ styling."""
    return {
        "layout": {
            "font": {"family": settings.charts.font_family},
            "paper_bgcolor": settings.charts.background_color,
            "plot_bgcolor": settings.charts.background_color,
            "title": {"font": {"color": settings.charts.text_color}},
            "xaxis": {"gridcolor": "#F5F5F5"},
            "yaxis": {"gridcolor": "#F5F5F5"},
        }
    }


def show_summary_metrics(filtered_data: pd.DataFrame) -> None:
    """Display enhanced summary metrics with ANZ styling."""
    try:
        st.subheader("Summary Metrics")
        if filtered_data is None or filtered_data.empty:
            st.warning("No data available for the selected filters.")
            return

        # Calculate additional metrics
        completion_rate = (
            filtered_data["Resolved"].notna().sum() / len(filtered_data) * 100
            if len(filtered_data) > 0
            else 0
        )

        metrics = {
            "Total Issues": {
                "value": len(filtered_data),
                "delta": None,
                "help": "Total number of issues in selected period",
            },
            "Resolved Issues": {
                "value": filtered_data["Resolved"].notna().sum(),
                "delta": f"{completion_rate:.1f}% completion rate",
                "help": "Number of resolved issues",
            },
            "Unresolved Issues": {
                "value": filtered_data["Resolved"].isna().sum(),
                "delta": None,
                "help": "Number of open issues",
            },
        }

        cols = st.columns(len(metrics))
        for col, (label, data) in zip(cols, metrics.items()):
            with col:
                st.metric(
                    label=label,
                    value=data["value"],
                    delta=data["delta"],
                    help=data["help"],
                )

    except Exception as e:
        st.error(f"Error displaying metrics: {str(e)}")


def create_bar_chart(data: pd.DataFrame, x: str, y: str, title: str) -> Optional[px.bar]:
    """Create a bar chart for the given columns."""
    if data.empty or x not in data.columns:
        return None

    return px.bar(data, x=x, y=y, title=title)


def create_pie_chart(data: pd.DataFrame, column: str, title: str) -> Optional[px.pie]:
    """Create a pie chart for the given column."""
    if data.empty or column not in data.columns:
        return None

    value_counts = data[column].value_counts()
    if value_counts.empty:
        return None

    return px.pie(names=value_counts.index, values=value_counts.values, title=title, hole=0.3)


def show_charts(jira_data: pd.DataFrame, filtered_data: pd.DataFrame) -> None:
    """Display various charts for Jira data analysis."""
    # Create weekly trend chart
    weekly_data = (
        filtered_data.groupby('Created_Week')
        .size()
        .reset_index(name='count')
    )
    
    # Create status distribution chart
    status_dist = (
        filtered_data['Status']
        .value_counts()
        .plot(kind='pie', autopct='%1.1f%%')
    )
    
    # Create epic progress chart
    epic_data = filtered_data[
        filtered_data['Issue Type'] == 'Epic'
    ].groupby('Status').size()


def show_metrics(data: pd.DataFrame) -> None:
    """Display key metrics including velocity."""
    if "Story Points" not in data.columns:
        return

    total_issues = len(data)
    total_points = data["Story Points"].sum()

    # Calculate velocity (points per week)
    if "Created_Week" in data.columns:
        weeks = data["Created_Week"].nunique()
        velocity = total_points / max(weeks, 1)
    else:
        velocity = 0

    # Display metrics
    metrics = {
        "Total Issues": total_issues,
        "Total Story Points": total_points,
        "Avg Velocity (points/week)": round(velocity, 1),
    }

    for label, value in metrics.items():
        st.metric(label=label, value=value)


def show_velocity_metrics(data: pd.DataFrame) -> None:
    """Display velocity metrics."""
    try:
        # Ensure we have required columns
        required_columns = ["Story Points", "Created", "Resolved"]
        if not all(col in data.columns for col in required_columns):
            st.warning("Missing required columns for velocity metrics")
            return

        # Calculate metrics with proper error handling
        resolved_issues = data[data["Resolved"].notna()]
        if resolved_issues.empty:
            st.warning("No resolved issues found for velocity calculation")
            return

        # Calculate velocity metrics with defaults
        total_points = resolved_issues["Story Points"].sum()
        total_weeks = max(
            (resolved_issues["Resolved"].max() - resolved_issues["Created"].min()).days / 7, 1
        )
        avg_velocity = total_points / total_weeks if total_weeks > 0 else 0

        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Story Points", f"{total_points:.0f}")
        with col2:
            st.metric("Weeks", f"{total_weeks:.1f}")
        with col3:
            st.metric("Avg Velocity (points/week)", f"{avg_velocity:.1f}")

    except Exception as e:
        st.error(f"Error displaying velocity metrics: {str(e)}")


def show_status_metrics(filtered_data: pd.DataFrame) -> None:
    """Display status distribution and progress metrics."""
    try:
        st.subheader("Status Distribution")

        # Get chart template
        chart_template = get_chart_template()

        # Status breakdown
        status_dist = filtered_data["Status"].value_counts()

        # Calculate progress metrics
        total_issues = len(filtered_data)
        completed_issues = len(
            filtered_data[filtered_data["Status"].isin(["Closed", "Story Done"])]
        )
        completion_rate = (completed_issues / total_issues * 100) if total_issues > 0 else 0

        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Completion Rate",
                f"{completion_rate:.1f}%",
                help="Percentage of completed issues",
            )
        with col2:
            st.metric(
                "In Progress Issues",
                len(filtered_data[filtered_data["Status"] == "Story in Progress"]),
                help="Number of issues currently in progress",
            )

        # Status Distribution Chart
        fig = px.pie(
            names=status_dist.index,
            values=status_dist.values,
            title="Issue Status Distribution",
            template=chart_template,
        )
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error displaying status metrics: {str(e)}")


def show_epic_progress(filtered_data: pd.DataFrame) -> None:
    """Display epic progress and tracking metrics."""
    try:
        st.subheader("Epic Progress")

        # Get chart template
        chart_template = get_chart_template()

        # Epic level metrics
        epic_metrics = (
            filtered_data.groupby("Epic Name")
            .agg(
                {
                    "Story Points": "sum",
                    "Issue key": "count",
                    "Status": lambda x: (x == "Closed").sum(),
                }
            )
            .reset_index()
        )

        epic_metrics["Completion Rate"] = epic_metrics["Status"] / epic_metrics["Issue key"] * 100

        # Epic Progress Chart
        fig = px.bar(
            epic_metrics,
            x="Epic Name",
            y="Story Points",
            color="Completion Rate",
            title="Epic Progress Overview",
            labels={
                "Epic Name": "Epic",
                "Story Points": "Total Story Points",
                "Completion Rate": "% Complete",
            },
            template=chart_template,
        )
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error displaying epic progress: {str(e)}")


def show_timeline_analysis(data: pd.DataFrame) -> None:
    """Display timeline analysis of issues."""
    try:
        # Ensure date columns are datetime
        date_columns = ["Created", "Resolved", "Updated", "Due Date"]
        for col in date_columns:
            if col in data.columns:
                data[col] = pd.to_datetime(data[col], format="mixed", errors="coerce")

        # Create timeline visualization
        timeline_data = data.sort_values("Created")
        fig = px.line(
            timeline_data,
            x="Created",
            y=timeline_data.groupby("Created").size(),
            title="Issue Creation Timeline",
        )
        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Error displaying timeline analysis: {str(e)}")

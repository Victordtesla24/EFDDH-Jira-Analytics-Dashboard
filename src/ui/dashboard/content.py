"""Dashboard content module."""

from typing import Any, Dict, List, Optional, Union

import pandas as pd
import streamlit as st

from src.ui.dashboard.issue_analysis import (create_daily_created_trend,
                                             create_issue_types_chart,
                                             create_priority_distribution,
                                             create_story_points_distribution)
from src.ui.dashboard.metrics import get_sprint_metrics
from src.ui.dashboard.sprint_progress import (create_burndown_chart,
                                              create_status_distribution,
                                              create_velocity_chart)
from src.ui.dashboard.sprint_selector import (get_available_sprints,
                                              get_sprint_data)


def show_dashboard_content(data: pd.DataFrame) -> None:
    """Display the main dashboard content."""
    st.markdown("## Sprint Analytics")

    # Sprint selection
    col1, col2 = st.columns(2)
    with col1:
        available_sprints = get_available_sprints(data)
        current_sprint = st.selectbox(
            "Select Current Sprint",
            options=available_sprints,
            index=0 if available_sprints else None,
        )

    with col2:
        previous_sprints = available_sprints.copy() if available_sprints else []
        if current_sprint in previous_sprints:
            previous_sprints.remove(current_sprint)
        previous_sprint = st.selectbox(
            "Select Previous Sprint",
            options=previous_sprints,
            index=0 if previous_sprints else None,
        )

    # Get sprint data
    current_data = get_sprint_data(data, current_sprint)
    previous_data = get_sprint_data(data, previous_sprint) if previous_sprint else None

    # Display metrics
    metrics = get_sprint_metrics(data, current_sprint, previous_sprint)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Total Issues",
            metrics["current"]["total_issues"],
            metrics["deltas"]["total_issues"],
        )

    with col2:
        st.metric(
            "Completed Issues",
            metrics["current"]["completed"],
            metrics["deltas"]["completed"],
        )

    with col3:
        st.metric(
            "Story Points",
            f"{metrics['current']['story_points']:.0f}",
            f"{metrics['deltas']['story_points']:.1f}%",
        )

    # Display charts
    if current_data is not None and not current_data.empty:
        st.markdown("### Sprint Progress")
        col1, col2 = st.columns(2)

        with col1:
            burndown_chart = create_burndown_chart(current_data)
            st.plotly_chart(burndown_chart, use_container_width=True)

        with col2:
            status_chart = create_status_distribution(current_data)
            st.plotly_chart(status_chart, use_container_width=True)

        st.markdown("### Issue Analysis")
        col1, col2 = st.columns(2)

        with col1:
            types_chart = create_issue_types_chart(current_data)
            st.plotly_chart(types_chart, use_container_width=True)

            points_chart = create_story_points_distribution(current_data)
            st.plotly_chart(points_chart, use_container_width=True)

        with col2:
            priority_chart = create_priority_distribution(current_data)
            st.plotly_chart(priority_chart, use_container_width=True)

            trend_chart = create_daily_created_trend(current_data)
            st.plotly_chart(trend_chart, use_container_width=True)

        st.markdown("### Team Velocity")
        velocity_chart = create_velocity_chart(data)
        st.plotly_chart(velocity_chart, use_container_width=True)

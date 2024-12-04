"""Dashboard header component."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import streamlit as st

from ui.dashboard.constants import create_metric_card


def show_header(metrics: dict, current_sprint: str) -> None:
    """Display dashboard header with key metrics."""
    st.markdown(
        f"""
        <div class="main-header">
            <h1>📊 JIRA Analytics Dashboard</h1>
            <p>Current Sprint: {current_sprint}</p>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Key Metrics Section
    st.markdown('<div class="metrics-container">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            create_metric_card(
                "Sprint Issues",
                str(metrics["current"]["total_issues"]),
                f"{metrics['deltas']['total_issues']:+.1f}% vs prev sprint",
                tooltip="Total issues in current sprint vs previous sprint",
            ),
            unsafe_allow_html=True,
        )

    with col2:
        completed = metrics["current"]["completed"]
        total = metrics["current"]["total_issues"]
        completion_rate = (completed / total * 100) if total > 0 else 0
        st.markdown(
            create_metric_card(
                "Completed Issues",
                str(completed),
                f"{metrics['deltas']['completed']:+.1f}% vs prev sprint",
                tooltip="Completed issues in current sprint vs previous sprint",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            create_metric_card(
                "Completion Rate",
                f"{completion_rate:.1f}%",
                f"{metrics['deltas']['completed']:+.1f}% vs prev sprint",
                tooltip="Sprint completion rate vs previous sprint",
            ),
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            create_metric_card(
                "Story Points",
                f"{metrics['current']['story_points']:.0f}",
                f"{metrics['deltas']['story_points']:+.1f}% vs prev sprint",
                tooltip="Story points in current sprint vs previous sprint",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

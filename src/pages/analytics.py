"""Analytics page module."""

import logging

import pandas as pd
import plotly.express as px
import streamlit as st

from components.visualizations import (show_capacity_management,
                                           show_charts, show_epic_progress,
                                           show_velocity_metrics)

logger = logging.getLogger(__name__)


def is_completed_status(status: str) -> bool:
    """Check if a status represents completion."""
    return status.lower() in ["done", "closed", "story done", "epic done"]


def validate_analytics_data(data: pd.DataFrame) -> bool:
    """Validate data for analytics page."""
    if data is None or data.empty:
        logger.warning("No data available for analysis")
        return False

    required_columns = ["Status"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        logger.warning(f"Missing required columns: {missing_columns}")
        return False

    return True


def show_analytics(data: pd.DataFrame) -> None:
    """Display analytics dashboard."""
    if not validate_analytics_data(data):
        st.error("No data available for analysis")
        return

    try:
        # Header metrics
        col1, col2 = st.columns(2)
        with col1:
            total_issues = len(data)
            st.metric("Total Issues", total_issues)

            completed_issues = len(data[data["Status"].apply(is_completed_status)])
            st.metric("Completed Issues", completed_issues)

            # Story Points metrics if available
            if "Story Points" in data.columns:
                total_points = data["Story Points"].fillna(0).sum()
                completed_points = (
                    data[data["Status"].apply(is_completed_status)]["Story Points"]
                    .fillna(0)
                    .sum()
                )

                completion_rate = (
                    (completed_issues / total_issues * 100) if total_issues > 0 else 0
                )

                st.metric(
                    "Story Points",
                    f"{total_points:.0f}",
                    (
                        f"{completion_rate:.1f}% Complete"
                        if total_points > 0
                        else "No points"
                    ),
                )
            else:
                logger.info("Story Points column not available")

        with col2:
            try:
                # Show visualizations
                show_charts(data)
            except Exception as e:
                logger.error(f"Error showing charts: {str(e)}")
                st.error("Failed to display charts")

            try:
                show_velocity_metrics(data)
            except Exception as e:
                logger.error(f"Error showing velocity metrics: {str(e)}")
                st.error("Failed to display velocity metrics")

            try:
                show_epic_progress(data)
            except Exception as e:
                logger.error(f"Error showing epic progress: {str(e)}")
                st.error("Failed to display epic progress")

        try:
            # Show capacity management in full width
            show_capacity_management(data)
        except Exception as e:
            logger.error(f"Error showing capacity management: {str(e)}")
            st.error("Failed to display capacity management")

    except Exception as e:
        logger.error(f"Error displaying analytics: {str(e)}")
        st.error("Error displaying analytics dashboard")

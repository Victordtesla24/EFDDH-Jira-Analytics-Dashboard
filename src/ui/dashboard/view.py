"""Dashboard view module."""

from typing import Any, Dict, List, Optional, Union

import pandas as pd
import streamlit as st

from src.ui.dashboard.content import show_dashboard_content
from src.ui.dashboard.header import show_header


def is_completed_status(status: str) -> bool:
    """Check if a status represents completion."""
    return str(status).lower() in [
        "done",
        "closed",
        "story done",
        "epic done",
        "resolved",
        "complete",
        "completed",
    ]


def calculate_metrics(data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """Calculate metrics for the dashboard header."""
    # Default metrics structure
    metrics = {
        "current": {
            "total_issues": 0,
            "completed": 0,
            "story_points": 0,
            "completion_rate": 0,
        },
        "deltas": {
            "total_issues": 0,
            "completed": 0,
            "story_points": 0,
            "completion_rate": 0,
        },
    }

    if data is not None and not data.empty:
        # Calculate current sprint metrics
        metrics["current"]["total_issues"] = len(data)

        # Check for completed issues using case-insensitive status check
        completed_issues = data[data["Status"].apply(is_completed_status)]
        metrics["current"]["completed"] = len(completed_issues)

        # Calculate story points
        if "Story Points" in data.columns:
            # Calculate total story points for completed issues only
            metrics["current"]["story_points"] = (
                completed_issues["Story Points"].fillna(0).sum()
            )

            # Calculate completion rate
            if metrics["current"]["total_issues"] > 0:
                completion_rate = (
                    metrics["current"]["completed"] / metrics["current"]["total_issues"]
                ) * 100
                metrics["current"]["completion_rate"] = round(completion_rate, 1)
            else:
                metrics["current"]["completion_rate"] = 0

        # For this example, we'll set deltas to 0
        # In a real implementation, you would compare with previous sprint data

    return metrics


def get_current_sprint(data: Optional[pd.DataFrame] = None) -> str:
    """Get the current sprint name."""
    if data is not None and not data.empty:
        if "Sprint" in data.columns and not data["Sprint"].empty:
            # Get the sprint with the highest sprint number
            sprints = data["Sprint"].dropna().unique()
            if len(sprints) > 0:
                try:
                    # Sort sprints by number (extract number from "BP: EFDDH Sprint X")
                    sprint_numbers = {}
                    for s in sprints:
                        try:
                            # Split by "Sprint" and ensure there's content after it
                            parts = s.split("Sprint")
                            if len(parts) > 1 and parts[1].strip():
                                sprint_numbers[s] = int(parts[1].strip())
                        except (ValueError, AttributeError):
                            continue

                    if sprint_numbers:
                        current_sprint = max(
                            sprint_numbers.keys(), key=lambda s: sprint_numbers[s]
                        )
                        return str(current_sprint)
                except Exception:
                    pass
    return "No Sprint Data"


def show_dashboard(data: Optional[pd.DataFrame] = None) -> None:
    """Display the main dashboard view."""
    # Always calculate metrics and get current sprint, even with empty data
    metrics = calculate_metrics(data)
    current_sprint = get_current_sprint(data)

    # Show header section with metrics
    show_header(metrics, current_sprint)

    # Show main dashboard content only if we have data
    if data is not None and not data.empty:
        show_dashboard_content(data)
    else:
        st.warning("Please upload JIRA data to view analytics.")

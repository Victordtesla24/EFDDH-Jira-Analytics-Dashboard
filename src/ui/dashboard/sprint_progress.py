"""Sprint progress visualization functionality."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import plotly.graph_objects as go


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


def create_burndown_chart(data: pd.DataFrame) -> go.Figure:
    """Create sprint burndown chart."""
    fig = go.Figure()

    if not data.empty and all(
        col in data.columns for col in ["Created", "Resolved", "Story Points"]
    ):
        # Get sprint date range
        start_date = data["Created"].min()
        end_date = data["Created"].max() + timedelta(days=14)  # Assume 2-week sprints

        # Calculate ideal burndown
        total_points = data["Story Points"].sum()
        dates = pd.date_range(start=start_date, end=end_date)
        ideal_points = [total_points * (1 - i / len(dates)) for i in range(len(dates))]

        # Calculate actual burndown
        actual_points = []
        remaining_points = total_points
        for date in dates:
            resolved = data[(data["Resolved"].notna()) & (data["Resolved"] <= date)][
                "Story Points"
            ].sum()
            remaining_points = total_points - resolved
            actual_points.append(remaining_points)

        # Add traces
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=ideal_points,
                name="Ideal",
                line=dict(color="#36B37E", dash="dash"),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=dates, y=actual_points, name="Actual", line=dict(color="#FF5630")
            )
        )
    else:
        # Add empty traces for consistent layout
        fig.add_trace(
            go.Scatter(
                x=[datetime.now()],
                y=[0],
                name="Ideal",
                line=dict(color="#36B37E", dash="dash"),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=[datetime.now()], y=[0], name="Actual", line=dict(color="#FF5630")
            )
        )

    fig.update_layout(
        title="Sprint Burndown",
        xaxis_title="Date",
        yaxis_title="Story Points Remaining",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig


def create_status_distribution(data: pd.DataFrame) -> go.Figure:
    """Create issue status distribution chart."""
    fig = go.Figure()

    if not data.empty and "Status" in data.columns:
        status_counts = data["Status"].value_counts()
        fig.add_trace(
            go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                marker=dict(colors=["#36B37E", "#FF5630", "#00A3BF"]),
            )
        )
    else:
        # Add empty trace for consistent layout
        fig.add_trace(
            go.Pie(labels=["No Data"], values=[1], marker=dict(colors=["#CCCCCC"]))
        )

    fig.update_layout(
        title="Issue Status Distribution",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig


def create_velocity_chart(data: pd.DataFrame) -> go.Figure:
    """Create sprint velocity chart."""
    fig = go.Figure()

    if not data.empty and all(
        col in data.columns for col in ["Sprint", "Status", "Story Points"]
    ):
        # Calculate velocity per sprint using consistent completion status check
        sprint_velocity = (
            data[
                data["Status"].apply(is_completed_status)
                & (data["Story Points"].notna())
            ]
            .groupby("Sprint")["Story Points"]
            .sum()
        )

        # Sort sprints by number
        try:
            sprint_numbers = {}
            for sprint in sprint_velocity.index:
                try:
                    # Split by "Sprint" and ensure there's content after it
                    parts = str(sprint).split("Sprint")
                    if len(parts) > 1 and parts[1].strip():
                        sprint_numbers[sprint] = int(parts[1].strip())
                except (ValueError, AttributeError):
                    continue

            if sprint_numbers:
                sprints = sorted(sprint_numbers.keys(), key=lambda x: sprint_numbers[x])
                velocities = [sprint_velocity[sprint] for sprint in sprints]
                fig.add_trace(go.Bar(x=sprints, y=velocities, marker_color="#00A3BF"))
            else:
                # Fallback to unsorted if no valid sprint numbers
                fig.add_trace(
                    go.Bar(
                        x=list(sprint_velocity.index),
                        y=list(sprint_velocity.values),
                        marker_color="#00A3BF",
                    )
                )
        except Exception:
            # Fallback to unsorted if any error occurs
            fig.add_trace(
                go.Bar(
                    x=list(sprint_velocity.index),
                    y=list(sprint_velocity.values),
                    marker_color="#00A3BF",
                )
            )
    else:
        # Add empty trace for consistent layout
        fig.add_trace(go.Bar(x=["No Data"], y=[0], marker_color="#00A3BF"))

    fig.update_layout(
        title="Sprint Velocity",
        xaxis_title="Sprint",
        yaxis_title="Story Points Completed",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig

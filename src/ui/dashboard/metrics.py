"""Dashboard metrics calculation module."""

import logging
from typing import Any, Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def calculate_delta_percentage(current: float, previous: float) -> float:
    """Calculate percentage change between current and previous values."""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100


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


def get_sprint_metrics(
    data: pd.DataFrame, current_sprint: str, previous_sprint: Optional[str]
) -> Dict[str, Any]:
    """
    Calculate sprint metrics with optional comparison to previous sprint.

    Args:
        data: DataFrame containing sprint data
        current_sprint: Name of the current sprint
        previous_sprint: Name of the previous sprint for comparison (optional)

    Returns:
        Dictionary containing current metrics, previous metrics (if applicable),
        and percentage changes
    """
    # Initialize metrics structure
    metrics = {
        "current": {"total_issues": 0, "completed": 0, "story_points": 0},
        "previous": {"total_issues": 0, "completed": 0, "story_points": 0},
        "deltas": {"total_issues": 0, "completed": 0, "story_points": 0},
    }

    try:
        if data is None or data.empty:
            logger.warning("Empty data provided for metrics calculation")
            return metrics

        # Calculate current sprint metrics
        current_data = data[data["Sprint"] == current_sprint]
        if current_data.empty:
            logger.warning(f"No data found for sprint: {current_sprint}")
            return metrics

        metrics["current"]["total_issues"] = len(current_data)
        metrics["current"]["completed"] = len(
            current_data[current_data["Status"].apply(is_completed_status)]
        )
        metrics["current"]["story_points"] = (
            current_data[current_data["Status"].apply(is_completed_status)][
                "Story Points"
            ]
            .fillna(0)
            .sum()
        )

        # Calculate previous sprint metrics if provided
        if previous_sprint:
            previous_data = data[data["Sprint"] == previous_sprint]
            if not previous_data.empty:
                metrics["previous"]["total_issues"] = len(previous_data)
                metrics["previous"]["completed"] = len(
                    previous_data[previous_data["Status"].apply(is_completed_status)]
                )
                metrics["previous"]["story_points"] = (
                    previous_data[previous_data["Status"].apply(is_completed_status)][
                        "Story Points"
                    ]
                    .fillna(0)
                    .sum()
                )

                # Calculate deltas
                for metric in ["total_issues", "completed", "story_points"]:
                    current_val = metrics["current"][metric]
                    previous_val = metrics["previous"][metric]
                    metrics["deltas"][metric] = calculate_delta_percentage(
                        current_val, previous_val
                    )

        logger.info(f"Calculated metrics for sprint {current_sprint}: {metrics}")
        return metrics

    except Exception as e:
        logger.error(f"Error calculating sprint metrics: {str(e)}")
        return metrics

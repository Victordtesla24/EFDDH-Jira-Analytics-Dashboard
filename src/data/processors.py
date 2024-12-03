from typing import Any, Dict

import pandas as pd


class JiraDataProcessor:
    """Process and transform Jira data for visualization."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def get_sprint_metrics(self) -> Dict[str, Any]:
        """Calculate sprint-level metrics."""
        completion_rate = (self.df["Resolved"].notna().sum() / len(self.df)) * 100
        cycle_time = (self.df["Resolved"] - self.df["Created"]).dt.days.mean()

        return {
            "total_issues": len(self.df),
            "completion_rate": completion_rate,
            "avg_cycle_time": cycle_time,
        }


def process_jira_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process Jira data for analysis."""
    # Convert dates
    for col in ["Created", "Resolved"]:
        df[col] = pd.to_datetime(df[col], format="%Y-%m-%d", errors="coerce")

    # Calculate resolution time
    df["Resolution Time (Days)"] = (df["Resolved"] - df["Created"]).dt.days

    # Status category mapping
    status_map = {
        "Closed": "Done",
        "Story Done": "Done",
        "In Progress": "In Progress",
        "Story in Progress": "In Progress",
        "To Do": "To Do",
        "Backlog": "To Do",
    }

    # Add status categories with updated mapping
    df["Status Category"] = df["Status"].map(status_map).fillna("Other")

    return df


def process_sprint_data(sprint_data: pd.DataFrame) -> pd.DataFrame:
    """Process sprint data with proper date handling and validation."""
    return sprint_data.assign(
        start_date=pd.to_datetime(sprint_data["start_date"]),
        end_date=pd.to_datetime(sprint_data["end_date"]),
    )

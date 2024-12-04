import re
from typing import Any, Dict

import numpy as np
import pandas as pd


class JiraDataProcessor:
    """Process and transform Jira data for visualization."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def get_sprint_metrics(self) -> Dict[str, Any]:
        """Calculate sprint-level metrics."""
        if self.df.empty:
            return {"total_issues": 0, "completion_rate": 0.0, "avg_cycle_time": np.nan}

        # Ensure Resolved column exists
        if "Resolved" not in self.df.columns:
            self.df["Resolved"] = pd.NaT

        # Calculate completion rate
        resolved_count = self.df["Resolved"].notna().sum()
        total_count = len(self.df)
        completion_rate = (
            (resolved_count / total_count * 100) if total_count > 0 else 0.0
        )

        # Calculate cycle time - ensure NaN when no resolved issues
        if resolved_count == 0:
            avg_cycle_time = np.nan
        else:
            resolved_mask = self.df["Resolved"].notna()
            if not any(resolved_mask):
                avg_cycle_time = np.nan
            else:
                cycle_times = pd.to_datetime(
                    self.df.loc[resolved_mask, "Resolved"]
                ) - pd.to_datetime(self.df.loc[resolved_mask, "Created"])
                avg_cycle_time = cycle_times.dt.days.mean()

        return {
            "total_issues": total_count,
            "completion_rate": completion_rate,
            "avg_cycle_time": avg_cycle_time,
        }


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


def extract_sprint_number(sprint_str: str) -> int:
    """Extract sprint number from sprint string."""
    try:
        if (
            pd.isna(sprint_str)
            or not str(sprint_str).strip()
            or sprint_str == "No Sprint"
        ):
            return -1  # Use -1 for no sprint to sort them last
        match = re.search(r"Sprint\s*(\d+)", str(sprint_str))
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return -1
        return -1
    except Exception:
        return -1


def process_jira_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process Jira data for analysis."""
    if df.empty:
        return df

    # Create a copy to avoid modifying the original
    processed_df = df.copy()

    # Convert dates with flexible parsing and ensure datetime64 dtype
    for col in ["Created", "Resolved", "Updated", "Due Date"]:
        if col in processed_df.columns:
            processed_df[col] = pd.to_datetime(processed_df[col], errors="coerce")
            # Ensure datetime64 dtype even if all values are NaT
            if not pd.api.types.is_datetime64_dtype(processed_df[col]):
                processed_df[col] = processed_df[col].astype("datetime64[ns]")

    # Calculate resolution time if Created column exists
    if "Created" in processed_df.columns:
        if "Resolved" not in processed_df.columns:
            processed_df["Resolved"] = pd.NaT
        processed_df["Resolution Time (Days)"] = (
            processed_df["Resolved"] - processed_df["Created"]
        ).dt.days

    # Status category mapping
    status_map = {
        "Closed": "Done",
        "Done": "Done",
        "Story Done": "Done",
        "Epic Done": "Done",
        "Resolved": "Done",
        "Complete": "Done",
        "Completed": "Done",
        "In Progress": "In Progress",
        "Story in Progress": "In Progress",
        "In Development": "In Progress",
        "Development": "In Progress",
        "To Do": "To Do",
        "Backlog": "To Do",
        "Open": "To Do",
        "New": "To Do",
    }

    # Add status categories with exact mapping
    if "Status" in processed_df.columns:
        processed_df["Status Category"] = (
            processed_df["Status"].str.strip().map(status_map).fillna("Other")
        )

        # Add completed flag based on status
        processed_df["Completed"] = processed_df["Status"].apply(is_completed_status)

    # Convert Story Points to numeric, replacing NaN with 0
    if "Story Points" in processed_df.columns:
        processed_df["Story Points"] = pd.to_numeric(
            processed_df["Story Points"], errors="coerce"
        ).fillna(0)

    # Process Sprint column if it exists
    if "Sprint" in processed_df.columns:
        # Ensure Sprint is string type and handle empty values
        processed_df["Sprint"] = processed_df["Sprint"].fillna("No Sprint").astype(str)

        # Clean sprint values - take first sprint if multiple
        processed_df["Sprint"] = processed_df["Sprint"].apply(
            lambda x: x.split(",")[0].strip() if "," in x else x.strip()
        )

        # Extract sprint numbers for sorting
        processed_df["Sprint Number"] = processed_df["Sprint"].apply(
            extract_sprint_number
        )

    return processed_df


def process_sprint_data(sprint_data: pd.DataFrame) -> pd.DataFrame:
    """Process sprint data with proper date handling and validation."""
    if sprint_data.empty:
        return sprint_data

    processed_data = sprint_data.copy()

    # Ensure required columns exist
    required_columns = ["start_date", "end_date"]
    for col in required_columns:
        if col not in processed_data.columns:
            processed_data[col] = pd.NaT

    # Convert dates with error handling and ensure datetime64 dtype
    for col in required_columns:
        processed_data[col] = pd.to_datetime(processed_data[col], errors="coerce")
        # Ensure datetime64 dtype even if all values are NaT
        if not pd.api.types.is_datetime64_dtype(processed_data[col]):
            processed_data[col] = processed_data[col].astype("datetime64[ns]")

    return processed_data

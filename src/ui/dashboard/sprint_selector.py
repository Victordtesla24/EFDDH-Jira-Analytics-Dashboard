"""Sprint selection functionality."""

from typing import Any, Dict, List, Optional, Union

import pandas as pd


def get_available_sprints(data: pd.DataFrame) -> List[str]:
    """Get list of available sprints from data."""
    if data is None or data.empty or "Sprint" not in data.columns:
        return []

    # Get unique sprints and sort by sprint number
    sprints_df = data[["Sprint", "Sprint Number"]].drop_duplicates()
    sprints_df = sprints_df[
        sprints_df["Sprint"].str.contains("BP: EFDDH Sprint", na=False)
    ]
    sprints_df = sprints_df.sort_values("Sprint Number", ascending=False)

    return sprints_df["Sprint"].tolist()


def get_sprint_data(data: pd.DataFrame, sprint_name: Optional[str]) -> pd.DataFrame:
    """Get data for a specific sprint."""
    if data is None or data.empty or not sprint_name or "Sprint" not in data.columns:
        return pd.DataFrame()

    return data[data["Sprint"] == sprint_name].copy()

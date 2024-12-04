"""Dashboard constants and shared utilities."""

from typing import Any, Dict, List, Optional, Union

import pandas as pd

# ANZ Color Palette
ANZ_COLORS = {
    "primary": "#007DBA",  # ANZ Blue
    "secondary": "#0A2F64",  # Dark Blue
    "accent1": "#78BE20",  # Green
    "accent2": "#00A9E0",  # Light Blue
    "neutral": "#1E1E1E",  # Dark Gray
    "background": "#F5F5F5",  # Light Gray
    "success": "#4CAF50",  # Success Green
    "warning": "#FFC107",  # Warning Yellow
    "error": "#DC3545",  # Error Red
}


def create_metric_card(
    title: str, value: str, delta: str = None, tooltip: str = None
) -> str:
    """Create a styled metric card with optional tooltip."""
    delta_html = ""
    if delta:
        delta_color = (
            "color: #4CAF50" if not delta.startswith("-") else "color: #DC3545"
        )
        delta_html = f'<div class="metric-delta" style="{delta_color}">{delta}</div>'

    return f"""
        <div class="metric-card" title="{tooltip if tooltip else ''}">
            <h3>{title}</h3>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
    """


def filter_sprint_data(
    data: pd.DataFrame, sprint_name: str = "BP: EFDDH Sprint 21"
) -> pd.DataFrame:
    """Filter data for specific sprint."""
    return data[data["Sprint"].str.contains(sprint_name, na=False)]

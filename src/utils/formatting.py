from datetime import datetime
from typing import Any, Dict, Union
import plotly.graph_objects as go

def format_date(date: Union[str, datetime]) -> str:
    """Format date consistently."""
    if isinstance(date, str):
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
            return parsed_date.strftime("%d/%m/%Y")
        except ValueError:
            return date  # Return original string if parsing fails
    return date.strftime("%d/%m/%Y")

def format_percentage(value: float) -> str:
    """Format value as percentage."""
    return f"{value:.2f}%"

def format_days(value: float) -> str:
    """Format value as days."""
    return f"{value:.2f} days"

def get_anz_template() -> dict[str, Any]:
    """Get ANZ chart template."""
    return {
        "layout": go.Layout(
            font={"family": "Arial, sans-serif", "size": 12},
            showlegend=True,
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            margin=dict(l=40, r=40, t=40, b=40),
        )
    }

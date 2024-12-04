import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class ChartSettings:
    default_height: int = 400
    default_width: int = 800
    chart_theme: str = "anz"
    color_palette: List[str] = field(
        default_factory=lambda: ["#007DBA", "#0A2F64", "#78BE20", "#1E1E1E", "#FFFFFF"]
    )
    font_family: str = "Arial, sans-serif"
    background_color: str = "#FFFFFF"
    text_color: str = "#1E1E1E"


@dataclass
class AppSettings:
    business_hours_per_day: float = 8.0
    capacity_threshold: float = 0.6
    sprint_duration_days: int = 10
    date_format: str = "%d/%m/%Y"
    charts: ChartSettings = field(default_factory=ChartSettings)
    app_title: str = "ANZ Jira Analytics Dashboard"


settings = AppSettings()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Data paths
DEFAULT_DATA_PATH = BASE_DIR / "data" / "sample.csv"
DATA_PATH = os.getenv("JIRA_DATA_PATH", str(DEFAULT_DATA_PATH))


# Streamlit secrets handling
def get_jira_config():
    """Get JIRA configuration from environment or streamlit secrets."""
    try:
        import streamlit as st

        return {
            "server": st.secrets.get("JIRA_SERVER", ""),
            "username": st.secrets.get("JIRA_USERNAME", ""),
            "api_token": st.secrets.get("JIRA_API_TOKEN", ""),
        }
    except Exception:
        return {
            "server": os.getenv("JIRA_SERVER", ""),
            "username": os.getenv("JIRA_USERNAME", ""),
            "api_token": os.getenv("JIRA_API_TOKEN", ""),
        }


# Application settings
APP_NAME = "JIRA Analytics Dashboard"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Add to existing settings
VELOCITY_SETTINGS = {
    "SPRINT_DURATION_WEEKS": 2,
    "ROUND_DECIMALS": 1,
    "MIN_COMPLETED_ITEMS": 1,
}

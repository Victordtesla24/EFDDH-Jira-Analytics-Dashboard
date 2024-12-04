import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any

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

# Construct data path using multiple os.path.dirname calls for readability
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
DATA_PATH = os.path.join(root_dir, "data")

# Add to existing settings
VELOCITY_SETTINGS = {
    "SPRINT_DURATION_WEEKS": 2,
    "ROUND_DECIMALS": 1,
    "MIN_COMPLETED_ITEMS": 1,
}

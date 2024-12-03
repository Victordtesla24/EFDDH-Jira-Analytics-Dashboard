from dataclasses import dataclass, field
from typing import List
import os


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

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")

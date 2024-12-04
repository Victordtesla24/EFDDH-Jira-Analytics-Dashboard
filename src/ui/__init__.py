"""UI package initialization."""

from typing import Any, Dict, List, Optional, Union

from src.ui.dashboard.content import show_dashboard_content
from src.ui.dashboard.file_handler import handle_file_upload
from src.ui.dashboard.header import show_header
from src.ui.dashboard.issue_analysis import (create_daily_created_trend,
                                             create_issue_types_chart,
                                             create_priority_distribution,
                                             create_story_points_distribution)
from src.ui.dashboard.metrics import get_sprint_metrics
from src.ui.dashboard.sprint_progress import (create_burndown_chart,
                                              create_status_distribution,
                                              create_velocity_chart)
from src.ui.dashboard.sprint_selector import get_sprint_data
from src.ui.dashboard.view import show_dashboard

__all__ = [
    "handle_file_upload",
    "show_dashboard",
    "show_dashboard_content",
    "show_header",
    "get_sprint_data",
    "get_sprint_metrics",
    "create_burndown_chart",
    "create_status_distribution",
    "create_velocity_chart",
    "create_issue_types_chart",
    "create_priority_distribution",
    "create_story_points_distribution",
    "create_daily_created_trend",
]

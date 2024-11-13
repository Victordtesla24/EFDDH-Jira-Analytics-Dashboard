from typing import List

# Column names
STORY_POINTS_COL = 'Custom field (Story Points)'
STATUS_COL = 'Status'
ISSUE_KEY_COL = 'Issue key'
EPIC_NAME_COL = 'Custom field (Epic Name)'
ASSIGNEE_COL = 'Assignee'
PRIORITY_COL = 'Priority'

# Sprint columns
SPRINT_COLS = ['Sprint', 'Current Sprint']

# Required columns for validation
REQUIRED_COLUMNS: List[str] = [
    STORY_POINTS_COL,
    STATUS_COL, 
    ISSUE_KEY_COL,
    EPIC_NAME_COL,        # Added Epic Name
    ASSIGNEE_COL,         # Added Assignee
    PRIORITY_COL,         # Added Priority
    'Sprint',             # Added Sprint
    # 'Current Sprint',     # Removed as it's derived within the application
    'Issue Type',         # Added Issue Type for defect density
    'Resolution Date',    # Added for lead time
    'Creation Date',      # Added for lead time
    'Done Date',          # Added for cycle time
    'In Progress Date'    # Added for cycle time
]

# Graph configuration
GRAPH_CONFIG = {
    'displayModeBar': True,
    'scrollZoom': True
}

# Default values
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 8050

import pytest
from Jira_dashboard import JiraDashboard
import pandas as pd

@pytest.fixture(scope="module")
def dashboard():
    # Create test data
    test_data = pd.DataFrame({
        'Issue key': ['TEST-1', 'TEST-2'],
        'Status': ['Done', 'In Progress'],
        'Custom field (Story Points)': [5, 3],
        'Priority': ['High', 'Medium'],
        'Assignee': ['User1', 'User2'],
        'Current Sprint': ['Sprint 1', 'Sprint 1']
    })
    
    # Save test data to temp CSV
    test_csv = 'test_data.csv'
    test_data.to_csv(test_csv, index=False)
    
    # Initialize dashboard with test data
    dashboard = JiraDashboard(test_csv)
    yield dashboard
    
    # Cleanup
    import os
    if os.path.exists(test_csv):
        os.remove(test_csv)

@pytest.mark.usefixtures("selenium_config")
class TestJiraDashboard:
    def test_calculate_metrics(self, dashboard):
        metrics = dashboard.calculate_metrics(dashboard.df)
        assert metrics.total_stories == 2
        assert metrics.total_points == 8.0
        assert metrics.completed == 1
        assert metrics.completion_rate == 50.0
        assert metrics.average_story_points == 4.0

    # Add more tests...
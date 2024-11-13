import pytest
from dash.testing.composite import DashComposite
import pandas as pd
from Jira_dashboard import JiraDashboard

class TestJiraDashboardUI:
    @pytest.fixture
    def test_data(self):
        """Create sample test data"""
        return {
            'Issue key': ['EFDDH-1', 'EFDDH-2', 'EFDDH-3', 'EFDDH-4', 'EFDDH-5'],
            'Status': ['Done', 'In Progress', 'Backlog', 'Blocked', 'Done'],
            'Custom field (Story Points)': [5, 3, 8, None, 2],
            'Custom field (Epic Name)': ['Epic1', 'Epic2', 'Epic1', 'Epic2', 'Epic3'],
            'Priority': ['High', 'Highest', 'Low', 'Blocker', 'Medium'],
            'Assignee': ['John', 'Jane', 'John', None, 'Jane'],
            'Sprint': ['Sprint 1', 'Sprint 1', 'Sprint 2', 'Sprint 2', 'Sprint 1'],
            'Parent id': ['', 'EFDDH-1', '', 'EFDDH-2', ''],
            'Current Sprint': ['Sprint 1', 'Sprint 1', 'Sprint 2', 'Sprint 2', 'Sprint 1']
        }

    @pytest.fixture
    def test_csv_path(self, test_data, tmp_path):
        """Create temporary CSV file"""
        df = pd.DataFrame(test_data)
        csv_path = tmp_path / "test_jira_data.csv"
        df.to_csv(csv_path, index=False)
        return str(csv_path)

    @pytest.fixture
    def dashboard_duo(self, test_csv_path, chrome_options, dash_thread_server):
        """Initialize JiraDashboard and DashComposite for UI testing"""
        dashboard = JiraDashboard(test_csv_path)
        duo = DashComposite(dashboard.app)
        dash_thread_server(dashboard.app.server, 8050)
        return duo, dashboard

    def test_initial_layout(self, dashboard_duo):
        """Test initial dashboard layout"""
        duo, dashboard = dashboard_duo
        with duo.start_server(dashboard.app):
            # Add timeout for elements
            duo.wait_for_element("h1", timeout=10)
            duo.wait_for_element("#status-filter", timeout=10) 
            
            # Validate all expected elements
            assert len(duo.find_elements(".metric-card")) == 5
            assert len(duo.find_elements(".js-plotly-plot")) >= 6
            
            # Validate dropdown options
            status_options = duo.find_elements("#status-filter option")
            assert len(status_options) == 4

    def test_filter_interactions(self, dashboard_duo):
        """Test filter interactions"""
        duo, dashboard = dashboard_duo
        with duo.start_server(dashboard.app):
            # Test status filter
            duo.select_dcc_dropdown("#status-filter", "Done")
            duo.wait_for_element("#total-stories-value")
            total_stories = duo.find_element("#total-stories-value").text
            assert total_stories == "2"  # Should show 2 done stories

            # Test priority filter
            duo.select_dcc_dropdown("#priority-filter", "High")
            duo.wait_for_element("#total-stories-value")
            total_stories = duo.find_element("#total-stories-value").text
            assert total_stories == "1"  # Should show 1 high priority story

    def test_graph_updates(self, dashboard_duo):
        """Test graph updates on filter changes"""
        duo, dashboard = dashboard_duo
        with duo.start_server(dashboard.app):
            # Wait for initial graph load
            duo.wait_for_element("#sprint-progress-graph", timeout=10)
            
            # Validate graph data updates
            initial_data = duo.find_element("#sprint-progress-graph")._data
            duo.select_dcc_dropdown("#status-filter", "Done")
            duo.wait_for_graph_update("#sprint-progress-graph")
            updated_data = duo.find_element("#sprint-progress-graph")._data
            
            assert initial_data != updated_data

    def test_error_handling(self, dashboard_duo):
        """Test dashboard error handling"""
        duo, dashboard = dashboard_duo
        with duo.start_server(dashboard.app):
            # Test invalid filter values
            duo.select_dcc_dropdown("#status-filter", "Invalid")
            error_msg = duo.find_element("#error-message")
            assert error_msg is not None

    def test_data_validation(self, test_data):
        """Test data validation logic"""
        invalid_data = test_data.copy()
        del invalid_data['Status']  # Remove required column
        
        with pytest.raises(ValueError):
            dashboard = JiraDashboard(invalid_data)

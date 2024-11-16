import logging
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from flask import Flask
from Jira_dashboard_graphs import JiraDashboardGraphs
from config import *
from error_handler import ErrorHandler
from data_validator import DataValidator
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import traceback

@dataclass
class DashboardMetrics:
    total_stories: int
    total_points: float 
    completed: int
    completion_rate: float
    average_story_points: float
    queries: Dict[str, str]

class JiraDashboard:
    def __init__(self, csv_path: str) -> None:
        self.setup_logging()
        self.validator = DataValidator()
        logging.info("Initializing JiraDashboard...")
        self.df = self.load_and_preprocess_data(csv_path)
        self.current_sprint_df = self.get_current_sprint_data()
        self.app = self.initialize_app()
        self.graphs = JiraDashboardGraphs()
        self.query_templates = {
            'sprint_metrics': """
                SELECT s.name as Sprint, 
                       COUNT(i.key) as Total_Issues,
                       SUM(i.story_points) as Story_Points_Completed
                FROM issue i
                JOIN sprint s ON i.sprint = s.id
                WHERE i.status = 'Done'
                GROUP BY s.name
                ORDER BY s.name
            """,
            'status_distribution': """
                SELECT status,
                       COUNT(*) as Issue_Count,
                       ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM issue)), 2) as Percentage
                FROM issue
                GROUP BY status
                ORDER BY Issue_Count DESC
            """,
            'priority_distribution': """
                SELECT priority,
                       COUNT(*) as Issue_Count,
                       ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM issue)), 2) as Percentage
                FROM issue
                GROUP BY priority
                ORDER BY Issue_Count DESC
            """,
            'assignee_metrics': """
                SELECT assignee,
                       COUNT(*) as Total_Issues,
                       SUM(CASE WHEN status = 'Done' THEN 1 ELSE 0 END) as Completed_Issues,
                       SUM(story_points) as Total_Story_Points
                FROM issue
                WHERE assignee IS NOT NULL
                GROUP BY assignee
                ORDER BY Total_Issues DESC
            """,
            'epic_metrics': """
                SELECT e.summary as Epic_Name,
                       COUNT(i.key) as Total_Issues,
                       SUM(CASE WHEN i.status = 'Done' THEN 1 ELSE 0 END) as Completed_Issues,
                       SUM(i.story_points) as Total_Story_Points
                FROM issue i
                JOIN issue e ON i.parent_id = e.id
                WHERE e.issue_type = 'Epic'
                GROUP BY e.summary
            """
        }
        logging.info("JiraDashboard initialized successfully")

    @staticmethod
    def setup_logging():
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    @ErrorHandler.handle_errors(default_return=pd.DataFrame())
    def load_and_preprocess_data(self, csv_path: str) -> pd.DataFrame:
        """Load and preprocess data with optimized operations"""
        try:
            df = pd.read_csv(csv_path)
            
            # Validate before processing
            self.validator.validate_dataset(df, REQUIRED_COLUMNS)
            
            # Use vectorized operations
            df[STORY_POINTS_COL] = pd.to_numeric(
                df[STORY_POINTS_COL], errors='coerce'
            ).fillna(0)  # Ensure the parenthesis is closed here
            
            # Process sprints more efficiently
            sprint_cols = [col for col in df.columns if 'Sprint' in col]
            sprint_mask = df[sprint_cols].notna().any(axis=1)
            df['Current Sprint'] = df[sprint_cols].ffill(axis=1).iloc[:, -1]
            
            # Ensure 'Current Sprint' column exists
            if 'Current Sprint' not in df.columns:
                df['Current Sprint'] = 'No Sprint'
            
            # Clean and standardize data
            df = self.clean_data(df)
            df = self.standardize_columns(df)
            
            return df
            
        except Exception as e:
            logging.error(f"Data loading failed: {e}")
            raise

    def validate_required_columns(self, df):
        """Validate required columns exist"""
        required_cols = [STORY_POINTS_COL, STATUS_COL, ISSUE_KEY_COL]
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def clean_data(self, df):
        """Clean data by removing duplicates and invalid rows"""
        original_len = len(df)
        df = df.dropna(subset=[ISSUE_KEY_COL])
        df = df.drop_duplicates(subset=[ISSUE_KEY_COL])
        cleaned_len = len(df)
        if cleaned_len < original_len:
            logging.warning(f"Removed {original_len - cleaned_len} invalid/duplicate rows")
        return df

    def standardize_columns(self, df):
        """Standardize column values"""
        df[STATUS_COL] = df[STATUS_COL].str.strip().str.title()
        df[PRIORITY_COL] = df[PRIORITY_COL].str.strip().str.title()
        df[STATUS_COL] = df[STATUS_COL].str.strip().str.title()
        df[PRIORITY_COL] = df[PRIORITY_COL].str.strip().str.title()
        return df

    def get_current_sprint_data(self):
        try:
            # Ensure 'Current Sprint' and 'Status' columns exist
            if 'Current Sprint' not in self.df.columns:
                self.df['Current Sprint'] = 'No Sprint'
            if 'Status' not in self.df.columns:
                self.df['Status'] = 'Unknown'
            
            sprint_values = sorted([s for s in self.df['Current Sprint'].unique() if s != 'No Sprint'], key=lambda x: self.extract_sprint_number(x))
            if not sprint_values:
                logging.warning("No sprint data found")
                return pd.DataFrame()
            current_sprint = sprint_values[-1]
            sprint_data = self.df[self.df['Current Sprint'] == current_sprint].copy()
            # Ensure critical columns have no missing values
            sprint_data.dropna(subset=[STORY_POINTS_COL, 'Status'], inplace=True)
            logging.info(f"Filtered Sprint Data: {len(sprint_data)} stories after cleaning")
            return sprint_data
        except Exception as e:
            logging.error(f"Error getting current sprint data: {e}")
            return pd.DataFrame()

    @staticmethod
    def extract_sprint_number(sprint_name):
        import re
        match = re.search(r'\d+', sprint_name)
        return int(match.group()) if match else 0

    def initialize_app(self):
        server = Flask(__name__)
        app = dash.Dash(__name__, server=server)
        app.layout = self.create_layout()
        self.setup_callbacks(app)
        return app

    def create_layout(self):
        return html.Div([
            self.header(),
            self.filter_options(),
            self.summary_cards(),
            self.graphs_layout(),
            dcc.Input(id='dummy-input', type='hidden', value='dummy'),
            html.Div(id='error-message', style={'color': 'red'})  # Added error message display
        ])  # Added missing closing brackets

    def filter_options(self):
        return html.Div([
            html.Label('Filter by Status:'),
            dcc.Dropdown(
                id='status-filter',
                options=[
                    {'label': 'All', 'value': 'All'},
                    {'label': 'Done', 'value': 'Done'},
                    {'label': 'In Progress', 'value': 'In Progress'},
                    {'label': 'Blocked', 'value': 'Blocked'}
                ],
                value='All'
            ),
            html.Label('Filter by Priority:'),
            dcc.Dropdown(
                id='priority-filter',
                options=[
                    {'label': 'All', 'value': 'All'},
                    {'label': 'Highest', 'value': 'Highest'},
                    {'label': 'High', 'value': 'High'},
                    {'label': 'Medium', 'value': 'Medium'},
                    {'label': 'Low', 'value': 'Low'}
                ],
                value='All'
            )
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'})

    def summary_cards(self):
        return html.Div([
            self.create_metric_card('Total Stories', '0', 'total-stories-value'),
            self.create_metric_card('Story Points', '0', 'story-points-value'),
            self.create_metric_card('Completed', '0', 'completed-value'),
            self.create_metric_card('Completion Rate', '0%', 'completion-rate-value'),
            self.create_metric_card('Average Story Points', '0', 'average-story-points-value'),
            html.Div(id='queries-display', style={'marginTop': '20px', 'color': '#2c3e50'})
        ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'marginBottom': '30px'})

    @staticmethod
    def header():
        return html.Div([
            html.H1("EFDDH Jira Analytics Dashboard", style={
                'textAlign': 'center',
                'color': 'white',
                'padding': '20px',
                'background': 'linear-gradient(90deg, #2c3e50 0%, #3498db 100%)',
                'borderRadius': '0 0 10px 10px',
                'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'
            })
        ])

    @staticmethod
    def create_metric_card(label, value, id):
        return html.Div([
            html.H4(label, style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '14px'}),
            html.H2(value, style={'margin': '10px 0', 'color': '#2c3e50', 'fontSize': '28px'}, id=id)
        ], style={
            'backgroundColor': 'white',
            'borderRadius': '8px',
            'padding': '15px 25px',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.05)',
            'flex': '1',
            'margin': '0 10px'
        })

    def graphs_layout(self):
        return html.Div([
            html.Div([
                dcc.Graph(id='sprint-progress-graph'),
                dcc.Graph(id='status-distribution-graph')
            ], style={'width': '48%', 'display': 'inline-block'}),
            html.Div([
                dcc.Graph(id='velocity-graph'),
                dcc.Graph(id='epic-level-metrics-graph')
            ], style={'width': '48%', 'display': 'inline-block'}),
            dcc.Graph(id='high-priority-stories-graph'),
            dcc.Graph(id='wip-stories-graph'),
            dcc.Graph(id='estimation-metrics-graph'),
            dcc.Graph(id='dependency-metrics-graph'),
            dcc.Graph(id='workload-priority-graph'),
            dcc.Graph(id='workload-status-graph'),
            dcc.Graph(id='story_points_box_plot'),
            dcc.Graph(id='sprint_heatmap')
        ])

    def setup_callbacks(self, app):
        app.callback(
            [
                Output('total-stories-value', 'children'),
                Output('story-points-value', 'children'),
                Output('completed-value', 'children'),
                Output('completion-rate-value', 'children'),
                Output('average-story-points-value', 'children'),
                Output('sprint-progress-graph', 'figure'),
                Output('status-distribution-graph', 'figure'),
                Output('velocity-graph', 'figure'),
                Output('epic-level-metrics-graph', 'figure'),
                Output('high-priority-stories-graph', 'figure'),
                Output('wip-stories-graph', 'figure'),
                Output('estimation-metrics-graph', 'figure'),
                Output('dependency-metrics-graph', 'figure'),
                Output('workload-priority-graph', 'figure'),
                Output('workload-status-graph', 'figure'),
                Output('story_points_box_plot', 'figure'),
                Output('sprint_heatmap', 'figure'),
                Output('queries-display', 'children'),
                Output('error-message', 'children')  # Added error message output
            ],
            [
                Input('dummy-input', 'value'),
                Input('status-filter', 'value'),
                Input('priority-filter', 'value')
            ]
        )(self.update_dashboard)

    def update_dashboard(self, _, status_filter, priority_filter):
        try:
            logging.info(f"Updating dashboard with status_filter={status_filter} and priority_filter={priority_filter}")
            filtered_df = self.df.copy()  # Create a copy to avoid modifying original

            if (status_filter != 'All'):
                filtered_df = filtered_df[filtered_df['Status'].str.title() == status_filter]
            if (priority_filter != 'All'):
                filtered_df = filtered_df[filtered_df['Priority'].str.title() == priority_filter]

            logging.info(f"Filtered DataFrame shape: {filtered_df.shape}")

            metrics = self.calculate_metrics(filtered_df)
            logging.info(f"Calculated metrics: {metrics}")

            # Convert DataFrame to JSON string with proper orientation
            filtered_df_json = filtered_df.to_json(date_format='iso', orient='split')

            figures = [
                self.graphs.generate_sprint_progress(filtered_df_json),
                self.graphs.generate_status_distribution(filtered_df),
                self.graphs.generate_velocity_metrics(self.df),
                self.graphs.generate_epic_level_metrics(filtered_df),
                self.graphs.generate_high_priority_stories(filtered_df),
                self.graphs.generate_wip_stories(filtered_df),
                self.graphs.generate_estimation_metrics(filtered_df),
                self.graphs.generate_dependency_metrics(filtered_df),
                self.graphs.generate_workload_priority(filtered_df),
                self.graphs.generate_workload_status(filtered_df),
                self.graphs.generate_story_points_box_plot(filtered_df),
                self.graphs.generate_sprint_heatmap(filtered_df)
            ]
            figures = [fig.to_dict() for fig in figures]

            # Update queries display using dataclass attributes
            queries_display = html.Div([
                html.P("SQL Queries Used:"),
                html.P(f"Sprint Metrics: {metrics.queries.get('sprint_metrics', 'N/A')}"),
                html.P(f"Status Distribution: {metrics.queries.get('status_distribution', 'N/A')}"),
                html.P(f"Priority Distribution: {metrics.queries.get('priority_distribution', 'N/A')}"),
                html.P(f"Assignee Metrics: {metrics.queries.get('assignee_metrics', 'N/A')}"),
                html.P(f"Epic Metrics: {metrics.queries.get('epic_metrics', 'N/A')}")
            ])

            # Clear any existing error messages
            error_message = ""
            return (
                str(metrics.total_stories),
                str(metrics.total_points),
                str(metrics.completed),
                f"{metrics.completion_rate:.1f}%",
                f"{metrics.average_story_points:.1f}",
                *figures,
                queries_display,
                error_message  # Return empty error message on success
            )

        except Exception as e:
            logging.error(f"Dashboard update error: {str(e)}")
            error_message = "An error occurred while loading the dashboard data."
            # Return empty/default values and the error message
            empty_fig = self.graphs.create_empty_figure()
            return (
                "0", "0", "0", "0%", "0",
                *[empty_fig.to_dict() for _ in range(12)],
                html.Div("Error loading dashboard data"),
                error_message
            )

    @ErrorHandler.handle_errors()
    def calculate_metrics(self, df: pd.DataFrame) -> DashboardMetrics:
        """Calculate dashboard metrics with type validation"""
        try:
            if df.empty:
                return DashboardMetrics(0, 0.0, 0, 0.0, 0.0, self.query_templates)

            # Input validation
            required_cols = ['Status', 'Custom field (Story Points)', 'Issue key']
            if not all(col in df.columns for col in required_cols):
                raise ValueError(f"Missing required columns: {set(required_cols) - set(df.columns)}")

            # Type checking
            if not pd.api.types.is_numeric_dtype(df['Custom field (Story Points)']):
                df['Custom field (Story Points)'] = pd.to_numeric(df['Custom field (Story Points)'], errors='coerce')

            # Calculate metrics with error handling
            try:
                total_stories = len(df)
                total_points = float(df['Custom field (Story Points)'].sum())
                completed = len(df[df['Status'] == 'Done'])
                completion_rate = self.safe_division(completed, total_stories) * 100
                average_story_points = self.safe_division(total_points, total_stories)
            except Exception as e:
                logging.error(f"Metric calculation error: {traceback.format_exc()}")
                raise

            return DashboardMetrics(
                total_stories=total_stories,
                total_points=total_points,
                completed=completed,
                completion_rate=completion_rate,
                average_story_points=average_story_points,
                queries=self.query_templates
            )

        except Exception as e:
            logging.error(f"Error calculating metrics: {traceback.format_exc()}")
            return DashboardMetrics(0, 0.0, 0, 0.0, 0.0, self.query_templates)

    def get_default_metrics(self) -> DashboardMetrics:
        """Return typed default metrics"""
        return DashboardMetrics(0, 0.0, 0, 0.0, 0.0, self.query_templates)

    @staticmethod
    def safe_division(numerator: Union[int, float], denominator: Union[int, float]) -> float:
        """Type-safe division with validation"""
        try:
            if not isinstance(numerator, (int, float)) or not isinstance(denominator, (int, float)):
                raise TypeError("Numerator and denominator must be numeric")
            return float(numerator) / float(denominator) if denominator else 0.0
        except Exception as e:
            logging.error(f"Division error: {traceback.format_exc()}")
            return 0.0

    def debug_info(self) -> Dict[str, Any]:
        """Return debug info about dashboard state"""
        return {
            'df_shape': self.df.shape if hasattr(self, 'df') else None,
            'current_sprint': self.current_sprint_df.shape if hasattr(self, 'current_sprint_df') else None,
            'memory_usage': self.df.memory_usage().sum() if hasattr(self, 'df') else None,
            'column_types': self.df.dtypes.to_dict() if hasattr(self, 'df') else None
        }

    def run_server(self, host='127.0.0.1', port=8050, debug=True):
        self.app.run_server(host=host, port=port, debug=debug)

if __name__ == '__main__':
    csv_path = '/Users/vicd/Downloads/EFDDH-Jira-12Nov.csv'
    dashboard = JiraDashboard(csv_path)
    dashboard.run_server()

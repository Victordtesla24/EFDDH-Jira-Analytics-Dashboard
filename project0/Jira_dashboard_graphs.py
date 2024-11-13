import plotly.express as px
import plotly.graph_objects as go
import logging
import pandas as pd
from functools import lru_cache
from typing import Optional, Dict, Any
from dataclasses import dataclass
import hashlib

@dataclass
class GraphResult:
    figure: Any
    error: Optional[str] = None

class JiraDashboardGraphs:
    def __init__(self):
        self.default_layout = {
            'title_x': 0.5,
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'showlegend': True
        }
        self.default_layout.update({
            'margin': dict(l=40, r=40, t=40, b=40),
            'font': dict(family='Arial', size=12),
            'hovermode': 'closest'
        })
        self.cache = {}
        self.error_counts: Dict[str, int] = {}

    def _get_cache_key(self, df: pd.DataFrame, func_name: str) -> str:
        """Generate cache key from dataframe hash and function name"""
        df_hash = hashlib.md5(pd.util.hash_pandas_object(df).values).hexdigest()
        return f"{func_name}_{df_hash}"

    def _log_error(self, func_name: str, error: Exception) -> None:
        """Track error counts per function"""
        self.error_counts[func_name] = self.error_counts.get(func_name, 0) + 1
        logging.error(f"Error in {func_name} (count: {self.error_counts[func_name]}): {str(error)}")

    def generate_graph(self, df: pd.DataFrame, graph_func: str) -> GraphResult:
        """Generic graph generation with caching and error handling"""
        try:
            if df.empty:
                return GraphResult(self.create_empty_figure(f"No Data for {graph_func}"))

            cache_key = self._get_cache_key(df, graph_func)
            if (cache_key in self.cache):
                return self.cache[cache_key]

            func = getattr(self, f"generate_{graph_func}")
            result = GraphResult(func(df))
            self.cache[cache_key] = result
            return result

        except Exception as e:
            self._log_error(graph_func, e)
            return GraphResult(
                self.create_empty_figure(f"Error in {graph_func}"), 
                str(e)
            )

    def clear_cache(self) -> None:
        """Clear graph cache"""
        self.cache.clear()
        self.error_counts.clear()

    def get_error_stats(self) -> Dict[str, int]:
        """Return error statistics"""
        return dict(self.error_counts)

    def create_empty_figure(self, title="No Data Available"):
        """Create standardized empty figure"""
        return go.Figure(
            go.Indicator(
                mode="number",
                value=0,
                title={"text": title}
            )
        ).update_layout(**self.default_layout)

    @lru_cache(maxsize=32)
    def generate_sprint_progress(self, df_json: str):
        """Generate sprint progress visualization using DataFrame JSON string as cache key"""
        try:
            logging.info("Generating sprint progress graph")
            # Read JSON with split orientation
            df = pd.read_json(df_json, orient='split')
            
            # Check for required columns
            required_columns = ['Status', 'Current Sprint']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logging.error(f"Missing columns for sprint progress graph: {missing_columns}")
                return self.create_empty_figure("Missing Data Columns")
            
            if df.empty:
                logging.warning("No data available for sprint progress graph")
                return self.create_empty_figure("No Sprint Data")

            # Ensure Status column exists
            if 'Status' not in df.columns:
                logging.warning("Missing Status column in data for sprint progress graph")
                return self.create_empty_figure("Missing Status Column")

            status_counts = df['Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            fig = px.treemap(
                status_counts, 
                path=['Status'], 
                values='Count',
                title='Sprint Progress',
                color='Count',
                color_continuous_scale='RdBu'
            )
            
            fig.update_layout(**self.default_layout)
            return fig

        except Exception as e:
            logging.error(f"Sprint progress generation failed: {str(e)}")
            return self.create_empty_figure("Error in Sprint Progress Chart")

    def generate_status_distribution(self, df):
        if df.empty:
            return self.create_empty_figure("No Status Data")
            
        try:
            status_df = df.groupby('Status').size().reset_index(name='count')
            return px.sunburst(status_df, path=['Status'], values='count', title='Status Distribution')
        except Exception as e:
            logging.error(f"Error generating status distribution: {e}")
            return self.create_empty_figure("Error Generating Chart")

    def generate_velocity_metrics(self, df):
        if df.empty:
            return self.create_empty_figure("No Velocity Data")
            
        try:
            velocity_df = df.groupby('Current Sprint')['Custom field (Story Points)'].sum().reset_index()
            velocity_df = velocity_df.sort_values('Current Sprint')  # Ensure correct sprint order
            return px.bar(velocity_df, x='Current Sprint', y='Custom field (Story Points)', title='Sprint Velocity')
        except Exception as e:
            logging.error(f"Error generating velocity metrics: {e}")
            return self.create_empty_figure("Error Generating Chart")

    def generate_epic_level_metrics(self, df):
        if df.empty:
            return self.create_empty_figure("No Epic Data")
            
        try:
            epic_metrics = df.groupby('Custom field (Epic Name)').agg(
                total_stories=('Issue key', 'nunique'),
                total_story_points=('Custom field (Story Points)', 'sum'),
                completed_stories=('Status', lambda x: (x.str.lower() == 'done').sum()),
                in_progress_stories=('Status', lambda x: (x.str.lower() == 'in progress').sum()),
                blocked_stories=('Status', lambda x: (x.str.lower() == 'blocked').sum())
            ).reset_index()

            epic_metrics['completion_rate'] = (epic_metrics['completed_stories'] / epic_metrics['total_stories'] * 100).round(1)
            epic_metrics['average_story_points'] = (epic_metrics['total_story_points'] / epic_metrics['total_stories']).round(1)
            epic_metrics['status'] = epic_metrics.apply(JiraDashboardGraphs.determine_epic_status, axis=1)

            return px.funnel(epic_metrics, x='completion_rate', y='Custom field (Epic Name)', title='Epic Completion Rates')
        except Exception as e:
            logging.error(f"Error generating epic level metrics: {e}")
            return self.create_empty_figure("Error Generating Chart")

    @staticmethod
    def determine_epic_status(row):
        if row['blocked_stories'] > 0:
            return 'Blocked'
        if row['in_progress_stories'] > 0:
            return 'In Progress'
        if row['completed_stories'] == row['total_stories']:
            return 'Completed'
        return 'On Track'

    def generate_high_priority_stories(self, df):
        if df.empty:
            return self.create_empty_figure("No High Priority Data")
            
        try:
            high_priority = df[df['Priority'] == 'Highest']
            high_priority_count = high_priority.groupby('Assignee').size().reset_index(name='High Priority Stories')
            return px.bar_polar(high_priority_count, r='High Priority Stories', theta='Assignee', title='High Priority Stories by Assignee')
        except Exception as e:
            logging.error(f"Error generating high priority stories: {e}")
            return self.create_empty_figure("Error Generating Chart")

    def generate_wip_stories(self, df):
        if df.empty:
            return self.create_empty_figure("No WIP Data")
            
        try:
            wip = df[df['Status'].str.contains('In Progress|In Dev', na=False)].copy()
            wip['Custom field (Epic Name)'] = wip['Custom field (Epic Name)'].str.replace('arf223', 'AR223', case=False)
            wip_count = wip.groupby('Custom field (Epic Name)').size().reset_index(name='WIP Stories')
            return px.line_polar(wip_count, r='WIP Stories', theta='Custom field (Epic Name)', line_close=True, title='WIP Stories by Epic')
        except Exception as e:
            logging.error(f"Error generating WIP stories: {e}")
            return self.create_empty_figure("Error Generating Chart")

    def generate_estimation_metrics(self, df):
        if df.empty:
            return self.create_empty_figure("No Estimation Data")
            
        try:
            # Handle None values in groupby aggregation
            estimation = df.groupby('Custom field (Epic Name)').agg({
                'Custom field (Story Points)': [
                    ('total_story_points', 'sum'),
                    ('average_story_points', 'mean')
                ],
                'Status': lambda x: ', '.join(str(i) for i in x.unique() if i is not None)
            }).reset_index()
            
            # Flatten column names
            estimation.columns = ['Epic Name', 'total_story_points', 'average_story_points', 'status']
            
            # Create scatter plot instead of matrix for better null handling
            return px.scatter(estimation, 
                             x='total_story_points',
                             y='average_story_points',
                             color='status',
                             hover_data=['Epic Name'],
                             title='Estimation Metrics by Epic')
        except Exception as e:
            logging.error(f"Error generating estimation metrics: {e}")
            return self.create_empty_figure("Error Generating Chart")

    def generate_dependency_metrics(self, df):
        if df.empty or not {'Source', 'Target', 'Value'}.issubset(df.columns):
            return self.create_empty_figure("No Dependency Data")
            
        try:
            sources = df['Source'].unique().tolist()
            targets = df['Target'].unique().tolist()
            all_nodes = sources + targets
            source_indices = df['Source'].apply(lambda x: all_nodes.index(x)).tolist()
            target_indices = df['Target'].apply(lambda x: all_nodes.index(x)).tolist()
            return go.Figure(go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=all_nodes,
                    color="blue"
                ),
                link=dict(
                    source=source_indices,
                    target=target_indices,
                    value=df['Value'].tolist()
                )
            )).update_layout(**self.default_layout)
        except Exception as e:
            logging.error(f"Error generating dependency metrics: {e}")
            return self.create_empty_figure("Error Generating Chart")

    def generate_workload_priority(self, df):
        if df.empty:
            return self.create_empty_figure("No Workload Data")
            
        try:
            return px.histogram(df, x='Priority', color='Assignee', title='Workload by Priority')
        except Exception as e:
            logging.error(f"Error generating workload priority: {e}")
            return self.create_empty_figure("Error Generating Chart")

    def generate_workload_status(self, df):
        if df.empty:
            return self.create_empty_figure("No Workload Data")
            
        try:
            return px.histogram(df, x='Status', color='Assignee', title='Workload by Status')
        except Exception as e:
            logging.error(f"Error generating workload status: {e}")
            return self.create_empty_figure("Error Generating Chart")

    def generate_story_points_box_plot(self, df):
        if df.empty:
            return self.create_empty_figure("No Story Points Data")
            
        try:
            return px.violin(df, x='Assignee', y='Custom field (Story Points)', title='Story Points Distribution by Assignee')
        except Exception as e:
            logging.error(f"Error generating story points box plot: {e}")
            return self.create_empty_figure("Error Generating Chart")

    def generate_sprint_heatmap(self, df):
        if df.empty:
            return self.create_empty_figure("No Sprint Data")
            
        try:
            sprint_counts = df.groupby(['Current Sprint', 'Status']).size().unstack(fill_value=0)
            return px.density_heatmap(sprint_counts, title='Sprint Status Heatmap')
        except Exception as e:
            logging.error(f"Error generating sprint heatmap: {e}")
            return self.create_empty_figure("Error Generating Chart")

    # New proposed charts and metrics
    def generate_burn_down_chart(self, df):
        if df.empty:
            return self.create_empty_figure("No Burn Down Data")
            
        try:
            burn_down_df = df.groupby('Sprint')['Custom field (Story Points)'].sum().reset_index()
            burn_down_df['Remaining Points'] = burn_down_df['Custom field (Story Points)'].cumsum()
            return px.line(burn_down_df, x='Sprint', y='Remaining Points', title='Burn Down Chart')
        except Exception as e:
            logging.error(f"Error generating burn down chart: {e}")
            return self.create_empty_figure("Error Generating Chart")

    def generate_cumulative_flow_diagram(self, df):
        if df.empty:
            return self.create_empty_figure("No Cumulative Flow Data")
            
        try:
            cfd_df = df.groupby(['Sprint', 'Status']).size().unstack(fill_value=0).cumsum(axis=1).reset_index()
            return px.area(cfd_df, x='Sprint', y=cfd_df.columns[1:], title='Cumulative Flow Diagram')
        except Exception as e:
            logging.error(f"Error generating cumulative flow diagram: {e}")
            return self.create_empty_figure("Error Generating Chart")

    def generate_lead_time_chart(self, df):
        if df.empty:
            return self.create_empty_figure("No Lead Time Data")
            
        try:
            df['Lead Time'] = (df['Resolution Date'] - df['Creation Date']).dt.days
            lead_time_df = df.groupby('Sprint')['Lead Time'].mean().reset_index()
            return px.line(lead_time_df, x='Sprint', y='Lead Time', title='Lead Time Chart')
        except Exception as e:
            logging.error(f"Error generating lead time chart: {e}")
            return self.create_empty_figure("Error Generating Chart")

    def generate_cycle_time_chart(self, df):
        if df.empty:
            return self.create_empty_figure("No Cycle Time Data")
            
        try:
            df['Cycle Time'] = (df['Done Date'] - df['In Progress Date']).dt.days
            cycle_time_df = df.groupby('Sprint')['Cycle Time'].mean().reset_index()
            return px.line(cycle_time_df, x='Sprint', y='Cycle Time', title='Cycle Time Chart')
        except Exception as e:
            logging.error(f"Error generating cycle time chart: {e}")
            return self.create_empty_figure("Error Generating Chart")

    def generate_throughput_chart(self, df):
        if df.empty:
            return self.create_empty_figure("No Throughput Data")
            
        try:
            throughput_df = df.groupby('Sprint')['Issue key'].count().reset_index()
            return px.bar(throughput_df, x='Sprint', y='Issue key', title='Throughput Chart')
        except Exception as e:
            logging.error(f"Error generating throughput chart: {e}")
            return self.create_empty_figure("Error Generating Chart")

    def generate_blocker_chart(self, df):
        if df.empty:
            return self.create_empty_figure("No Blocker Data")
            
        try:
            blocker_df = df[df['Priority'] == 'Blocker'].groupby('Sprint')['Issue key'].count().reset_index()
            return px.bar(blocker_df, x='Sprint', y='Issue key', title='Blocker Issues by Sprint')
        except Exception as e:
            logging.error(f"Error generating blocker chart: {e}")
            return self.create_empty_figure("Error Generating Chart")

    def generate_defect_density_chart(self, df):
        if df.empty:
            return self.create_empty_figure("No Defect Density Data")
            
        try:
            defect_density_df = df[df['Issue Type'] == 'Bug'].groupby('Sprint')['Issue key'].count().reset_index()
            return px.line(defect_density_df, x='Sprint', y='Issue key', title='Defect Density by Sprint')
        except Exception as e:
            logging.error(f"Error generating defect density chart: {e}")
            return self.create_empty_figure("Error Generating Chart")

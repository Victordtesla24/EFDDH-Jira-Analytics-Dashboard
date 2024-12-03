import pandas as pd
import streamlit as st
from typing import Optional

from src.components.visualizations import (
    show_charts,
    show_epic_progress,
    show_summary_metrics,
    show_timeline_analysis,
    show_velocity_metrics,
)


def show_analytics(data: Optional[pd.DataFrame]) -> None:
    """Display analytics dashboard."""
    st.title("JIRA Analytics Dashboard")
    
    if data is None or data.empty:
        st.error("No data available for analysis")
        return

    # Ensure required columns exist
    required_columns = ["Issue Type", "Priority", "Status", "Story Points"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
        return

    # Display visualizations
    show_charts(data)
    
    # Create columns with proper error handling
    try:
        columns = st.columns(3)
        
        # Display metrics in columns
        with columns[0]:
            total_points = data["Story Points"].sum()
            st.metric("Total Story Points", f"{total_points:.1f}")
        
        with columns[1]:
            total_issues = len(data)
            st.metric("Total Issues", total_issues)
        
        with columns[2]:
            completed = len(data[data["Status"] == "Done"])
            st.metric("Completed Issues", completed)
            
    except Exception as e:
        st.error(f"Error displaying metrics: {str(e)}")

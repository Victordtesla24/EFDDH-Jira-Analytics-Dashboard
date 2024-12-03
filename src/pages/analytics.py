import pandas as pd
import streamlit as st

from src.components.visualizations import (show_charts, show_epic_progress,
                                           show_velocity_metrics)


def show_analytics(data: pd.DataFrame) -> None:
    """Show analytics page content."""
    if data is None or data.empty:
        st.error("No data available for analysis")
        return

    # Check required columns
    required_columns = ["Story Points", "Status", "Created"]
    missing_columns = [col for col in required_columns if col not in data.columns]

    if missing_columns:
        error_msg = f"Missing required columns: {', '.join(missing_columns)}"
        st.error(error_msg)
        return

    # Clean data by removing null values
    data = data.copy()
    data = data.dropna(subset=required_columns)

    if len(data) == 0:
        st.warning("No valid data points after cleaning")
        return

    # Show visualizations with cleaned data
    show_charts(data)
    show_epic_progress(data)
    show_velocity_metrics(data)

"""Analytics page for the JIRA dashboard."""

import logging
from pathlib import Path

import streamlit as st

from data.data_loader import load_data, prepare_data
from pages.analytics import show_analytics

logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    with st.spinner("Loading analytics dashboard..."):
        # Load and prepare data
        data_path = Path("data/EFDDH-Jira-Data-Sprint21.csv")
        raw_data = load_data(data_path)

        if raw_data is None or raw_data.empty:
            logger.error("Failed to load data from CSV file")
            st.error("Failed to load data from CSV file")
            st.stop()

        data = prepare_data(raw_data)
        if data is None or data.empty:
            logger.error("Failed to prepare data for analysis")
            st.error("Failed to prepare data for analysis")
            st.stop()

        # Display analytics dashboard
        show_analytics(data)

except Exception as e:
    error_msg = f"An error occurred: {str(e)}"
    logger.error(error_msg)
    st.error(error_msg)
    st.stop()

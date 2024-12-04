"""Capacity management page for the JIRA dashboard."""
import streamlit as st

from src.data.data_loader import load_data, prepare_data
from src.components.visualizations import show_capacity_management

# Page configuration
st.set_page_config(
    page_title="Capacity Management",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    with st.spinner("Loading data..."):
        # Load and prepare data
        raw_data = load_data()
        if raw_data is not None and not raw_data.empty:
            data = prepare_data(raw_data)
            if not data.empty:
                show_capacity_management(data)
            else:
                st.error("Failed to prepare data for capacity analysis")
                st.stop()
        else:
            st.error("No data available for capacity analysis")
            st.stop()
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.stop()

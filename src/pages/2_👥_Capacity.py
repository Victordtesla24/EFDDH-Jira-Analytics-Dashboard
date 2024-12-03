import streamlit as st

from src.components.visualizations import show_capacity_management
from src.data.data_loader import load_data, prepare_data

st.set_page_config(page_title="Capacity Management", page_icon="👥")

# Load and prepare data
jira_data = load_data()
if jira_data is None:
    st.error("Failed to load data. Please check the data source.")
    st.stop()

prepared_data = prepare_data(jira_data)
if prepared_data is None:
    st.error("Failed to prepare data. Please check the data format.")
    st.stop()

show_capacity_management(prepared_data)

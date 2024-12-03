import streamlit as st

from src.components.visualizations import show_capacity_management
from src.data.data_loader import load_data, prepare_data

st.set_page_config(page_title="Capacity Management", page_icon="👥")
jira_data = load_data()
jira_data = prepare_data(jira_data)
show_capacity_management(jira_data)

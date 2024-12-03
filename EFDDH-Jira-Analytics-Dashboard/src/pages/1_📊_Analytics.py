import streamlit as st
from pathlib import Path

from src.components.visualizations import show_charts
from src.data.data_loader import load_data, prepare_data
from src.pages.analytics import show_analytics

# Page config
st.set_page_config(page_title="Analytics", page_icon="📊")

# Load and prepare data
data_path = Path("data/EFDDH-Jira-Data-Sprint21.csv")
jira_data = load_data(data_path)
jira_data = prepare_data(jira_data)

# Display analytics dashboard
show_analytics(jira_data)

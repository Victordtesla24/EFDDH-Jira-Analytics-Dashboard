import streamlit as st

from src.components.visualizations import (show_charts, show_epic_progress,
                                           show_velocity_metrics)
from src.config.settings import settings
from src.data.data_loader import load_data, prepare_data

# Page config
st.set_page_config(
    page_title=settings.app_title,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enhanced ANZ styling with better UI elements
st.markdown(
    """
    <style>
        .stApp {
            font-family: Arial, sans-serif;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            background-color: #F5F5F5;
            border-bottom: 2px solid #007DBA;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 0px 24px;
            background-color: #FFFFFF;
            border-radius: 4px 4px 0px 0px;
            color: #1E1E1E;
            font-weight: 500;
            border: none;
            transition: all 0.3s ease;
        }
        .stTabs [aria-selected="true"] {
            background-color: #007DBA;
            color: #FFFFFF;
            border-bottom: none;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #F0F0F0;
            color: #007DBA;
        }
        .stTabs [aria-selected="true"]:hover {
            background-color: #006BA1;
            color: #FFFFFF;
        }
        .stMetric {
            background-color: #F5F5F5;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #007DBA;
        }
        .stSidebar {
            background-color: #F5F5F5;
        }
        .stButton button {
            background-color: #007DBA;
            color: #FFFFFF;
            border-radius: 4px;
        }
        .stProgress .st-bo {
            background-color: #007DBA;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Create tabs with enhanced styling
tab1, tab2, tab3 = st.tabs(
    ["📊 Jira Analytics", "📚 JIRA Handbook", "🔄 Agile Process"]
)

# Tab 1: Jira Analytics Dashboard
with tab1:
    st.title(settings.app_title)

    try:
        with st.spinner("Loading data..."):
            # Load and prepare data
            jira_data = load_data()
            if jira_data is None:
                st.error("Failed to load data. Please check the data source.")
                st.stop()

            jira_data = prepare_data(jira_data)
            if jira_data is None:
                st.error("Failed to prepare data. Please check the data format.")
                st.stop()

            # Sidebar filters with enhanced UI
            with st.sidebar:
                st.header("Dashboard Filters")
                st.markdown("---")

                # Date range filter with proper type handling
                min_date = jira_data["Created"].min().date()
                max_date = jira_data["Created"].max().date()
                date_range = st.date_input(
                    "Select Date Range",
                    value=[min_date, max_date],
                    key="date_range",
                )

                # Ensure date_range is a tuple of two dates
                if isinstance(date_range, tuple) and len(date_range) == 2:
                    start_date, end_date = date_range
                else:
                    # Default to min/max dates if not properly selected
                    start_date = min_date
                    end_date = max_date

                st.subheader("Issue Filters")
                priorities = sorted(jira_data["Priority"].unique().tolist())
                selected_priority: list[str] = st.multiselect(
                    "Priority",
                    options=priorities,
                    default=priorities,
                    key="priority",
                )

                issue_types = sorted(jira_data["Issue Type"].unique().tolist())
                selected_issue_type: list[str] = st.multiselect(
                    "Select Issue Type",
                    options=issue_types,
                    default=issue_types,
                )

                sprints = sorted(jira_data["Sprint"].dropna().unique().tolist())
                selected_sprint: list[str] = st.multiselect(
                    "Sprint",
                    options=sprints,
                    default=sprints,
                    key="sprint",
                )

                # Reset filters button
                if st.button("Reset Filters"):
                    st.session_state.priority = priorities
                    st.session_state.issue_type = issue_types
                    st.session_state.sprint = sprints
                    st.rerun()

            # Filter data with proper date handling
            mask = (
                (jira_data["Priority"].isin(selected_priority))
                & (jira_data["Issue Type"].isin(selected_issue_type))
                & (jira_data["Sprint"].isin(selected_sprint))
                & (jira_data["Created"].dt.date >= start_date)
                & (jira_data["Created"].dt.date <= end_date)
            )
            filtered_data = jira_data[mask]

            # Show Metrics and Visuals in columns
            col1, col2 = st.columns([2, 1])
            with col1:
                # Display basic metrics
                total_issues = len(filtered_data)
                completed_issues = len(filtered_data[filtered_data["Status"] == "Done"])
                st.metric("Total Issues", total_issues)
                st.metric("Completed Issues", completed_issues)
            with col2:
                info_text = (
                    f"Showing data for {len(filtered_data)} issues "
                    f"from {start_date} to {end_date}"
                )
                st.info(info_text)

            # Show charts with enhanced styling
            show_charts(filtered_data)

            # Add new sections
            st.markdown("---")
            show_velocity_metrics(filtered_data)

            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                # Display status distribution
                status_counts = filtered_data["Status"].value_counts()
                st.subheader("Status Distribution")
                st.bar_chart(status_counts)
            with col2:
                show_epic_progress(filtered_data)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.exception(e)

# Tab 2: JIRA Handbook
with tab2:
    st.title("JIRA Handbook")
    st.info("Content coming soon...")
    # Placeholder for future handbook content
    st.markdown(
        """
        ### Coming Soon
        - JIRA Best Practices
        - Workflow Guidelines
        - Issue Management
        - Reporting and Analytics
    """
    )

# Tab 3: Agile Process Documentation
with tab3:
    st.title("Agile Process Documentation")
    st.info("Content coming soon...")
    # Placeholder for future agile documentation
    st.markdown(
        """
        ### Coming Soon
        - Sprint Planning
        - Daily Stand-ups
        - Retrospectives
        - Agile Metrics
    """
    )

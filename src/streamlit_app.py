"""Main Streamlit application."""
import streamlit as st
import pandas as pd

from src.config.settings import settings
from src.data.data_loader import prepare_data
from src.ui.agile_process import show_agile_process
from src.ui.dashboard.file_handler import handle_file_upload
from src.ui.dashboard.view import show_dashboard
from src.ui.handbook import show_handbook
from src.ui.styles import CUSTOM_CSS

# Must be the first Streamlit command
st.set_page_config(
    page_title=settings.app_title,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

def initialize_app() -> None:
    """Initialize the Streamlit app with configuration and styling."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def show_sidebar() -> None:
    """Display the sidebar with controls and instructions."""
    with st.sidebar:
        st.title("Dashboard Controls")

        if st.button("🔄 Clear Cache"):
            st.cache_data.clear()
            st.rerun()

        st.markdown("---")
        st.markdown(
            """
        ### 📋 Instructions
        1. Upload your JIRA CSV file
        2. View analytics and metrics
        3. Use filters to analyze data

        ### 🔍 Need Help?
        Contact support for assistance
        """
        )

def run_app() -> None:
    """Main application entry point with error handling."""
    try:
        # Initialize app
        initialize_app()

        # Show sidebar
        show_sidebar()

        # Main content with tabs
        tab1, tab2, tab3 = st.tabs(
            ["📊 Analytics Dashboard", "📚 JIRA Handbook", "🔄 Agile Process"]
        )

        # Initialize data as empty DataFrame
        data = pd.DataFrame()
        
        with tab1:
            raw_data = handle_file_upload()
            if not isinstance(raw_data, pd.DataFrame) or raw_data.empty:
                show_dashboard(None)  # Pass None to show empty dashboard state
                st.info("Please upload a JIRA CSV file to begin analysis")
            else:
                data = prepare_data(raw_data)
                if data.empty:
                    show_dashboard(None)  # Pass None if data preparation failed
                    st.error("Failed to prepare data for analysis")
                else:
                    show_dashboard(data)  # Pass prepared data

        with tab2:
            show_handbook(data)  # Pass data to show benchmark stories

        with tab3:
            show_agile_process(data)  # Pass data to show real examples

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.stop()

if __name__ == "__main__":
    run_app()

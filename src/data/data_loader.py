import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

# Set pandas option to opt into future behavior
pd.set_option("future.no_silent_downcasting", True)

logger = logging.getLogger(__name__)


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data(file_path: Optional[Path] = None) -> Optional[pd.DataFrame]:
    """Load and validate Jira data with improved caching and error handling."""
    try:
        if file_path is None:
            file_path = Path("data/EFDDH-Jira-Data-Sprint21.csv")

        if not file_path.exists():
            error_msg = f"Data file not found: {file_path}"
            logger.error(error_msg)
            st.error("Failed to load data: " + error_msg)
            return None

        df = pd.read_csv(file_path)

        # Check for empty dataset
        if df.empty:
            error_msg = "Empty dataset loaded"
            logger.error(error_msg)
            st.error("Failed to load data: " + error_msg)
            return None

        # Check for required columns
        required_cols = ["Created", "Resolved", "Priority", "Issue Type", "Sprint"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            error_msg = f"Missing required columns: {missing_cols}"
            logger.error(error_msg)
            st.error("Failed to load data: " + error_msg)
            return None

        # Convert dates and handle invalid formats
        try:
            for col in ["Created", "Resolved"]:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])
                    if df[col].isna().all():
                        error_msg = f"Invalid date format in column: {col}"
                        logger.error(error_msg)
                        st.error("Failed to load data: " + error_msg)
                        return None
        except (ValueError, TypeError) as e:
            error_msg = f"Invalid date format: {str(e)}"
            logger.error(error_msg)
            st.error("Failed to load data: " + str(e))
            return None

        return df

    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        st.error("Failed to load data: " + str(e))
        return None


def prepare_data(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
    """Prepare data for analysis."""
    if df is None or df.empty:
        return None

    df = df.copy()

    # Handle date fields
    if "Created" in df.columns:
        df["Created"] = pd.to_datetime(df["Created"]).fillna(pd.Timestamp("2024-01-01"))
        df["Created_Week"] = df["Created"].dt.isocalendar().week
    if "Resolved" in df.columns:
        df["Resolved"] = pd.to_datetime(df["Resolved"])

    # Handle null values with specific defaults
    # First fill null values, then infer objects without copy parameter
    df["Story Points"] = df["Story Points"].fillna(0)
    df["Story Points"] = df["Story Points"].infer_objects()
    df["Epic Name"] = df["Epic Name"].fillna("No Epic")
    df["Status"] = df["Status"].fillna("In Progress")

    # Handle remaining null values using ffill and bfill
    df = df.ffill().bfill()

    return df

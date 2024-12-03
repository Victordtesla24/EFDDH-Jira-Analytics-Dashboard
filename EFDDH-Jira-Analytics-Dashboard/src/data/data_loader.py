import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data(file_path: Optional[Path] = None) -> Optional[pd.DataFrame]:
    """Load and validate Jira data with improved caching and error handling."""
    try:
        if file_path is None:
            file_path = Path("data/EFDDH-Jira-Data-Sprint21.csv")

        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")

        df = pd.read_csv(file_path)
        if df.empty:
            raise ValueError("Empty dataset loaded")

        required_cols = ["Created", "Resolved", "Priority", "Issue Type", "Sprint"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Convert dates here to ensure consistent format
        for col in ["Created", "Resolved"]:
            df[col] = pd.to_datetime(df[col], format="%d/%m/%Y", errors="coerce")

        return df

    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        st.error(f"Failed to load data: {str(e)}")
        return None


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare data for analysis."""
    try:
        # Convert date columns to datetime
        date_columns = ["Created", "Resolved", "Updated", "Due Date"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format="mixed", errors="coerce")

        # Create week-based columns
        df["Created_Week"] = df["Created"].dt.strftime("%Y-%m-%d")

        # Handle missing values
        df["Story Points"] = df["Story Points"].fillna(0)
        df["Epic Name"] = df["Epic Name"].fillna("No Epic")

        return df
    except Exception as e:
        logger.error(f"Error preparing data: {str(e)}")
        raise

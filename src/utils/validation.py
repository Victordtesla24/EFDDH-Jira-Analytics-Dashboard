from pathlib import Path
from typing import List

import pandas as pd
import streamlit as st


def validate_jira_data(df: pd.DataFrame) -> bool:
    """Validate Jira data format and content."""
    if df is None or df.empty:
        return False

    # Required columns
    required_columns = [
        "Issue key",
        "Created",
        "Priority",
        "Issue Type",
        "Status",
        "Epic Name",
    ]

    # Check required columns exist
    if not all(col in df.columns for col in required_columns):
        return False

    # Check for null values in critical columns
    critical_columns = ["Issue key", "Created", "Priority", "Status"]
    if df[critical_columns].isnull().any().any():
        return False

    # Validate date formats
    try:
        pd.to_datetime(df["Created"], format="%Y-%m-%d")
        if "Resolved" in df.columns:
            pd.to_datetime(df["Resolved"], format="%Y-%m-%d", errors="coerce")
        return True
    except (ValueError, TypeError):
        return False


def ensure_test_data() -> bool:
    """Ensure test data file exists and is valid."""
    data_path: Path = Path("data/test-data.csv")
    if not data_path.exists():
        st.error(f"Data file not found: {data_path}")
        st.stop()

    df = pd.read_csv(data_path)
    if not validate_jira_data(df):
        st.error("Invalid data format in CSV file")
        st.stop()

    return True


def validate_velocity_data(df: pd.DataFrame) -> bool:
    """Validate data required for velocity metrics."""
    required_cols = ["Sprint", "Story Points", "Status"]
    if not all(col in df.columns for col in required_cols):
        return False

    # Verify Story Points are numeric
    try:
        pd.to_numeric(df["Story Points"], errors="raise")
    except Exception:
        return False

    return True


def validate_epic_data(df: pd.DataFrame) -> bool:
    """Validate data required for epic progress tracking."""
    required_cols = ["Epic Name", "Story Points", "Status"]
    if not all(col in df.columns for col in required_cols):
        return False

    # Verify Epic Names are not all null
    if df["Epic Name"].isna().all():
        return False

    return True


def validate_input_data(data: pd.DataFrame, required_columns: List[str]) -> bool:
    """Validate input data against required columns.
    Args:
        data: DataFrame to validate
        required_columns: List of required column names
    Returns:
        bool: True if data is valid, False otherwise
    """
    if data is None or data.empty:
        return False

    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        return False

    return True

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import streamlit as st

from src.data.processors import process_jira_data

logger = logging.getLogger(__name__)


@st.cache_data(show_spinner=False)
def load_data(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Load data from CSV file with proper error handling and caching."""
    try:
        if file_path is None:
            file_path = Path("data/EFDDH-Jira-Data-Sprint21.csv")

        if not file_path.exists():
            logger.error(f"Data file not found: {file_path}")
            st.error(f"Data file not found: {file_path}")
            return pd.DataFrame()

        logger.info(f"Loading data from {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} rows")

        # Basic validation of required columns
        required_columns = ["Issue key", "Created", "Status"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            st.error(f"Missing required columns: {missing_columns}")
            return pd.DataFrame()

        if df.empty:
            logger.warning("Loaded DataFrame is empty")
            st.error("No data found in file")
            return pd.DataFrame()

        logger.info("Data loaded successfully")
        return df

    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare and clean the data for analysis."""
    try:
        if df.empty:
            logger.warning("Empty DataFrame received")
            return pd.DataFrame()

        # Create a copy to avoid modifying the original
        processed_df = df.copy()

        logger.info("Starting data preparation")

        # Convert date columns with explicit format
        date_columns = ["Created", "Updated", "Resolved", "Due Date"]
        for col in date_columns:
            if col in processed_df.columns:
                logger.info(f"Converting {col} to datetime")
                processed_df[col] = pd.to_datetime(processed_df[col], errors="coerce")
                # Ensure datetime64 dtype even if all values are NaT
                if not pd.api.types.is_datetime64_dtype(processed_df[col]):
                    processed_df[col] = processed_df[col].astype("datetime64[ns]")

        # Basic data cleaning - only drop rows with missing required fields
        if "Issue key" in processed_df.columns and "Created" in processed_df.columns:
            initial_rows = len(processed_df)
            processed_df = processed_df.dropna(subset=["Issue key", "Created"])
            dropped_rows = initial_rows - len(processed_df)
            if dropped_rows > 0:
                logger.info(
                    f"Dropped {dropped_rows} rows with missing Issue key or Created date"
                )

        # Ensure Story Points is numeric
        story_points_col = next(
            (col for col in processed_df.columns if col.lower() == "story points"), None
        )
        if story_points_col:
            logger.info("Converting Story Points to numeric")
            processed_df["Story Points"] = pd.to_numeric(
                processed_df[story_points_col], errors="coerce"
            ).fillna(0)

        # Ensure Status has valid values and consistent casing
        status_col = next(
            (col for col in processed_df.columns if col.lower() == "status"), None
        )
        if status_col:
            logger.info("Cleaning Status values")
            processed_df["Status"] = processed_df[status_col].fillna("In Progress")

        # Ensure Priority is a string
        priority_col = next(
            (col for col in processed_df.columns if col.lower() == "priority"), None
        )
        if priority_col:
            logger.info("Cleaning Priority values")
            processed_df["Priority"] = (
                processed_df[priority_col].fillna("Medium").astype(str)
            )

        # Ensure Issue Type is a string
        issue_type_col = next(
            (col for col in processed_df.columns if col.lower() == "issue type"), None
        )
        if issue_type_col:
            logger.info("Cleaning Issue Type values")
            processed_df["Issue Type"] = (
                processed_df[issue_type_col].fillna("Story").astype(str)
            )

        # Clean Sprint column - handle multiple sprints per issue
        sprint_cols = [col for col in processed_df.columns if col.lower() == "sprint"]
        if sprint_cols:
            logger.info("Cleaning Sprint values")
            # Get the first non-empty sprint value for each row
            sprints = processed_df[sprint_cols].fillna("")
            processed_df["Sprint"] = sprints.apply(
                lambda row: next(
                    (s for s in row if pd.notna(s) and str(s).strip()), "No Sprint"
                ),
                axis=1,
            )

        # Handle Epic Link/Name
        epic_link_col = next(
            (
                col
                for col in processed_df.columns
                if col.lower() in ["epic link", "epic name"]
            ),
            None,
        )
        if epic_link_col:
            logger.info("Cleaning Epic Link values")
            processed_df["Epic Link"] = processed_df[epic_link_col].fillna("No Epic")

        # Process the data using the processor
        processed_df = process_jira_data(processed_df)

        # Log summary statistics
        logger.info(f"Final dataset shape: {processed_df.shape}")
        logger.info("Data preparation completed successfully")

        return processed_df

    except Exception as e:
        logger.error(f"Error preparing data: {str(e)}")
        st.error(f"Error preparing data: {str(e)}")
        return pd.DataFrame()

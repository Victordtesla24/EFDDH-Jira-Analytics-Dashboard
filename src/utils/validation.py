import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)


def validate_data(
    data: Optional[pd.DataFrame], required_cols: Optional[List[str]] = None
) -> bool:
    """
    Validate DataFrame has required columns and is not empty.

    Args:
        data: DataFrame to validate
        required_cols: List of required column names

    Returns:
        bool: True if data is valid, False otherwise
    """
    try:
        if data is None or data.empty:
            logger.warning("Data validation failed: DataFrame is None or empty")
            return False

        if required_cols:
            missing_cols = [col for col in required_cols if col not in data.columns]
            if missing_cols:
                logger.warning(
                    f"Data validation failed: Missing required columns {missing_cols}"
                )
                return False

        return True

    except Exception as e:
        logger.error(f"Error validating data: {str(e)}")
        return False


def validate_jira_data(data: pd.DataFrame) -> bool:
    """Validate Jira data format and content."""
    required_columns = [
        "Issue key",
        "Created",
        "Priority",
        "Issue Type",
        "Status",
        "Epic Name",
    ]

    if not validate_input_data(data, required_columns):
        return False

    # Validate date format in Created column
    try:
        pd.to_datetime(data["Created"])
    except (ValueError, TypeError):
        logger.warning("Data validation failed: Invalid date format in Created column")
        return False

    # Validate Epic Names - require at least one non-null value
    if data["Epic Name"].isnull().all():
        logger.warning("Data validation failed: All Epic Names are null")
        return False

    return True


def validate_velocity_data(data: pd.DataFrame) -> bool:
    """Validate velocity data format and content."""
    required_columns = ["Sprint", "Story Points", "Status"]
    if not validate_input_data(data, required_columns):
        return False

    # Check if Story Points are numeric
    try:
        pd.to_numeric(data["Story Points"])
        return True
    except (ValueError, TypeError):
        logger.warning("Data validation failed: Story Points must be numeric")
        return False


def validate_epic_data(data: pd.DataFrame) -> bool:
    """Validate epic data format and content."""
    required_columns = ["Epic Name", "Story Points", "Status"]
    if not validate_input_data(data, required_columns):
        return False

    # Check if there are any non-null epic names
    if data["Epic Name"].isnull().all():
        logger.warning("Data validation failed: All Epic Names are null")
        return False

    return True


def validate_input_data(data: pd.DataFrame, required_columns: List[str]) -> bool:
    """Validate input data against required columns."""
    if data is None or data.empty:
        logger.warning("Data validation failed: DataFrame is None or empty")
        return False

    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        logger.warning(
            f"Data validation failed: Missing required columns {missing_columns}"
        )
        return False

    return True


def validate_data_types(metrics: Dict[str, Any]) -> bool:
    """Validate metric data types."""
    if not isinstance(metrics, dict):
        logger.warning("Metrics validation failed: Input is not a dictionary")
        return False

    required_keys = ["velocity", "completed"]
    if not all(key in metrics for key in required_keys):
        logger.warning("Metrics validation failed: Missing required keys")
        return False

    return (
        isinstance(metrics["velocity"], (int, float))
        and isinstance(metrics["completed"], int)
        and metrics["velocity"] is not None
        and metrics["completed"] is not None
    )


def validate_calculations(metrics: Dict[str, Any]) -> bool:
    """Validate metric calculations."""
    if not isinstance(metrics, dict):
        logger.warning("Calculations validation failed: Input is not a dictionary")
        return False

    required_keys = ["velocity", "completed"]
    if not all(key in metrics for key in required_keys):
        logger.warning("Calculations validation failed: Missing required keys")
        return False

    velocity = metrics["velocity"]
    completed = metrics["completed"]

    # Check for valid ranges
    if not (isinstance(velocity, (int, float)) and isinstance(completed, int)):
        logger.warning("Calculations validation failed: Invalid data types")
        return False

    if not (0 <= velocity <= 100 and completed >= 0):
        logger.warning("Calculations validation failed: Values out of valid range")
        return False

    return True


def validate_display_format(metrics: Dict[str, Any]) -> bool:
    """Validate metric display format."""
    if not isinstance(metrics, dict):
        logger.warning("Display format validation failed: Input is not a dictionary")
        return False

    required_keys = ["velocity", "completed"]
    if not all(key in metrics for key in required_keys):
        logger.warning("Display format validation failed: Missing required keys")
        return False

    return (
        isinstance(metrics["velocity"], (int, float))
        and isinstance(metrics["completed"], int)
        and metrics["velocity"] is not None
        and metrics["completed"] is not None
    )


def validate_metric_output(metrics: Dict[str, Any]) -> bool:
    """Validate complete metric output."""
    return (
        validate_data_types(metrics)
        and validate_calculations(metrics)
        and validate_display_format(metrics)
    )


def ensure_test_data() -> None:
    """Ensure test data file exists and is valid."""
    test_file = Path("data/EFDDH-Jira-Data-Sprint21.csv")

    if not test_file.exists():
        st.error("Test data file not found")
        st.stop()

    try:
        data = pd.read_csv(test_file)
        if not validate_jira_data(data):
            st.error("Invalid data format in test file")
            st.stop()
    except Exception as e:
        st.error(f"Error reading test data: {str(e)}")
        st.stop()

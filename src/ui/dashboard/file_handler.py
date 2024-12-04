"""File upload handling for the dashboard."""
from typing import Dict, List, Optional, Union, Any

import pandas as pd
import streamlit as st


def validate_csv_structure(df: pd.DataFrame) -> bool:
    """Validate required columns in CSV file."""
    required_columns = {
        "Issue key",
        "Sprint",
        "Status",
        "Story Points",
        "Created",
        "Updated",
        "Resolved",
        "Due Date",
    }
    return all(col in df.columns for col in required_columns)


def handle_file_upload() -> pd.DataFrame:
    """Handle file upload and data processing."""
    st.markdown(
        """
        <div class="upload-section">
            <h3>Upload JIRA Data</h3>
            <p>Upload your JIRA CSV export file to begin analysis</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "JIRA CSV File Upload",  # Non-empty label for accessibility
        type=["csv"],
        help="Upload a CSV file exported from JIRA",
        label_visibility="collapsed",  # Hide the label but keep it for accessibility
    )

    if uploaded_file is not None:
        try:
            # Read CSV file
            df = pd.read_csv(uploaded_file)

            # Validate CSV structure
            if not validate_csv_structure(df):
                st.markdown(
                    """
                    <div class="error-message">
                        ❌ Invalid CSV format: Missing required columns
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                return pd.DataFrame()

            if not df.empty:
                # Convert date columns with proper format
                date_columns = ["Created", "Updated", "Resolved", "Due Date"]
                for col in date_columns:
                    if col in df.columns:
                        # Try different date formats
                        try:
                            # First try with dayfirst=True for DD/MM/YYYY format
                            df[col] = pd.to_datetime(
                                df[col], dayfirst=True, errors="coerce"
                            )
                        except Exception:
                            try:
                                # Then try ISO format
                                df[col] = pd.to_datetime(
                                    df[col], format="ISO8601", errors="coerce"
                                )
                            except Exception:
                                # Finally try mixed format
                                df[col] = pd.to_datetime(
                                    df[col], format="mixed", errors="coerce"
                                )

                # Convert numeric columns
                if "Story Points" in df.columns:
                    df["Story Points"] = pd.to_numeric(
                        df["Story Points"], errors="coerce"
                    )

                st.markdown(
                    """
                    <div class="success-message">
                        ✅ Data loaded successfully!
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                return df
            else:
                st.markdown(
                    """
                    <div class="error-message">
                        ❌ The uploaded file is empty
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                return pd.DataFrame()

        except Exception as e:
            st.markdown(
                f"""
                <div class="error-message">
                    ❌ Error processing file: {str(e)}
                </div>
                """,
                unsafe_allow_html=True,
            )
            return pd.DataFrame()

    return pd.DataFrame()

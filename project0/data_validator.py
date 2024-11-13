import pandas as pd
import logging
from typing import List, Dict, Optional

class DataValidator:
    @staticmethod
    def validate_dataset(df: pd.DataFrame, required_columns: List[str]) -> Dict[str, bool]:
        """Validate DataFrame structure and content"""
        validation_results = {
            'has_required_columns': all(col in df.columns for col in required_columns),
            'has_data': not df.empty,
            'has_valid_types': True
        }
        
        if not validation_results['has_required_columns']:
            missing = [col for col in required_columns if col not in df.columns]
            logging.error(f"Missing required columns: {missing}")
            validation_results['has_valid_columns'] = False
        else:
            validation_results['has_valid_columns'] = True
        
        return validation_results

    @staticmethod
    def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize DataFrame"""
        df = df.copy()
        # Remove duplicates
        df = df.drop_duplicates()
        # Fill nulls appropriately
        df = df.fillna({
            'Status': 'No Status',
            'Priority': 'No Priority',
            'Custom field (Story Points)': 0
        })
        return df

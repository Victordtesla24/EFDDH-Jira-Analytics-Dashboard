from datetime import datetime


def format_percentage(value: float) -> str:
    """Format value as percentage with 2 decimal places."""
    return f"{value:.2f}%"


def format_days(value: float) -> str:
    """Format value as days with 2 decimal places."""
    return f"{value:.2f} days"


def format_date(date_str: str) -> str:
    """Format date string to dd/mm/yyyy."""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        return date.strftime("%d/%m/%Y")
    except ValueError:
        # Return original string if parsing fails
        return date_str

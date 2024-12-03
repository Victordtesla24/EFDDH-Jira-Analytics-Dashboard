from src.utils.formatting import format_date, format_days, format_percentage


def test_format_percentage():
    """Test percentage formatting."""
    assert format_percentage(75.5) == "75.50%"
    assert format_percentage(0) == "0.00%"
    assert format_percentage(100.123) == "100.12%"


def test_format_days():
    """Test days formatting."""
    assert format_days(5.5) == "5.50 days"
    assert format_days(0) == "0.00 days"
    assert format_days(10.123) == "10.12 days"


def test_format_date():
    """Test date string formatting."""
    assert format_date("2024-01-01") == "01/01/2024"
    assert format_date("invalid-date") == "invalid-date"  # Test error case
    assert format_date("2024-12-31") == "31/12/2024"

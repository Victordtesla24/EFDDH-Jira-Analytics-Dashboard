import logging
from pathlib import Path

import pytest

from src.utils.caching import cache_data
from src.utils.formatting import format_date
from src.utils.logging import setup_logging


@pytest.fixture(autouse=True)
def setup_logs_directory():
    """Create logs directory for tests."""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    yield
    # Cleanup test log files
    for log_file in logs_dir.glob("app_*.log"):
        log_file.unlink()


def test_cache_data():
    @cache_data(ttl=3600)
    def sample_function():
        return "cached_value"

    result = sample_function()
    assert result == "cached_value"


def test_format_date():
    test_date = "2024-01-01"
    formatted = format_date(test_date)
    assert formatted == "01/01/2024"


def test_setup_logging(setup_logs_directory):
    """Test logging setup."""
    logger = setup_logging()
    assert logger.level == 20  # INFO level
    assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)

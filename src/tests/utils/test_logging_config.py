import logging
import os
from datetime import datetime
from unittest.mock import MagicMock, call, patch

import pytest

from src.utils.logging_config import setup_logging


def test_setup_logging(tmp_path):
    with patch("src.utils.logging_config.os.path.exists", return_value=False), patch(
        "src.utils.logging_config.os.makedirs"
    ) as mock_makedirs, patch("logging.FileHandler") as mock_file_handler, patch(
        "logging.StreamHandler"
    ) as mock_stream_handler, patch(
        "logging.basicConfig"
    ) as mock_basic_config:

        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        with patch("src.utils.logging_config.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_now

            logger = setup_logging()

            mock_makedirs.assert_called_once_with("logs")
            mock_basic_config.assert_called_once()
            config_args = mock_basic_config.call_args[1]
            assert config_args["level"] == logging.INFO
            assert (
                config_args["format"]
                == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            assert len(config_args["handlers"]) == 2
            assert isinstance(logger, logging.Logger)


def test_existing_log_directory():
    with patch("src.utils.logging_config.os.path.exists", return_value=True), patch(
        "src.utils.logging_config.os.makedirs"
    ) as mock_makedirs, patch("logging.FileHandler"), patch(
        "logging.StreamHandler"
    ), patch(
        "logging.basicConfig"
    ):
        setup_logging()
        mock_makedirs.assert_not_called()


def test_directory_creation_error():
    with patch("src.utils.logging_config.os.path.exists", return_value=False), patch(
        "src.utils.logging_config.os.makedirs", side_effect=PermissionError
    ), patch("logging.FileHandler"), patch("logging.StreamHandler"), patch(
        "logging.basicConfig"
    ):
        with pytest.raises(PermissionError):
            setup_logging()


def test_file_handler_error():
    with patch("src.utils.logging_config.os.path.exists", return_value=True), patch(
        "logging.FileHandler", side_effect=PermissionError
    ), patch("logging.StreamHandler"), patch("logging.basicConfig"):
        with pytest.raises(PermissionError):
            setup_logging()


def test_module_specific_log_levels():
    mock_loggers = {}

    def mock_get_logger(name):
        if name not in mock_loggers:
            mock_logger = MagicMock()
            mock_loggers[name] = mock_logger
        return mock_loggers[name]

    with patch("logging.getLogger", side_effect=mock_get_logger), patch(
        "src.utils.logging_config.os.path.exists", return_value=True
    ), patch("logging.FileHandler"), patch("logging.StreamHandler"), patch(
        "logging.basicConfig"
    ):
        setup_logging()

        expected_calls = [
            call(logging.WARNING) for _ in ["streamlit", "urllib3", "matplotlib"]
        ]

        for module in ["streamlit", "urllib3", "matplotlib"]:
            assert mock_loggers[module].setLevel.called
            assert mock_loggers[module].setLevel.call_args == call(logging.WARNING)


def test_log_file_naming():
    with patch("src.utils.logging_config.os.path.exists", return_value=True), patch(
        "logging.FileHandler"
    ) as mock_file_handler, patch("logging.StreamHandler"), patch(
        "logging.basicConfig"
    ):
        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        with patch("src.utils.logging_config.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_now

            setup_logging()

            expected_log_file = os.path.join("logs", "app_20240101_120000.log")
            mock_file_handler.assert_called_once()
            assert mock_file_handler.call_args[0][0] == expected_log_file


def test_handler_configuration():
    with patch("src.utils.logging_config.os.path.exists", return_value=True), patch(
        "logging.FileHandler"
    ) as mock_file_handler, patch(
        "logging.StreamHandler"
    ) as mock_stream_handler, patch(
        "logging.basicConfig"
    ) as mock_basic_config:
        setup_logging()

        assert mock_file_handler.called
        assert mock_stream_handler.called
        config_args = mock_basic_config.call_args[1]
        assert len(config_args["handlers"]) == 2


def test_logging_format_validation():
    with patch("src.utils.logging_config.os.path.exists", return_value=True), patch(
        "logging.FileHandler"
    ), patch("logging.StreamHandler"), patch(
        "logging.basicConfig"
    ) as mock_basic_config:
        setup_logging()

        config_args = mock_basic_config.call_args[1]
        log_format = config_args["format"]

        # Verify all required components are in the format string
        required_components = [
            "%(asctime)s",
            "%(name)s",
            "%(levelname)s",
            "%(message)s",
        ]
        for component in required_components:
            assert component in log_format


def test_stream_handler_error():
    with patch("src.utils.logging_config.os.path.exists", return_value=True), patch(
        "logging.FileHandler"
    ), patch(
        "logging.StreamHandler", side_effect=Exception("Stream handler error")
    ), patch(
        "logging.basicConfig"
    ):
        with pytest.raises(Exception, match="Stream handler error"):
            setup_logging()


def test_multiple_calls():
    with patch("src.utils.logging_config.os.path.exists", return_value=True), patch(
        "logging.FileHandler"
    ) as mock_file_handler, patch("logging.StreamHandler"), patch(
        "logging.basicConfig"
    ):
        logger1 = setup_logging()
        logger2 = setup_logging()

        # Should create new file handlers for each call
        assert mock_file_handler.call_count == 2
        # But should return the same logger instance
        assert logger1.name == logger2.name


def test_custom_log_levels():
    mock_loggers = {}

    def mock_get_logger(name):
        if name not in mock_loggers:
            mock_logger = MagicMock()
            mock_loggers[name] = mock_logger
        return mock_loggers[name]

    with patch("logging.getLogger", side_effect=mock_get_logger), patch(
        "src.utils.logging_config.os.path.exists", return_value=True
    ), patch("logging.FileHandler"), patch("logging.StreamHandler"), patch(
        "logging.basicConfig"
    ):
        # Test with different log levels
        for level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]:
            mock_loggers.clear()
            with patch("logging.basicConfig") as mock_basic_config:
                setup_logging()
                config_args = mock_basic_config.call_args[1]
                assert (
                    config_args["level"] == logging.INFO
                )  # Default level should be INFO


def test_timestamp_microseconds():
    with patch("src.utils.logging_config.os.path.exists", return_value=True), patch(
        "logging.FileHandler"
    ) as mock_file_handler, patch("logging.StreamHandler"), patch(
        "logging.basicConfig"
    ):
        # Test with microseconds
        mock_now = datetime(2024, 1, 1, 12, 0, 0, 123456)
        with patch("src.utils.logging_config.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_now

            setup_logging()

            # Should not include microseconds in filename
            expected_log_file = os.path.join("logs", "app_20240101_120000.log")
            assert mock_file_handler.call_args[0][0] == expected_log_file

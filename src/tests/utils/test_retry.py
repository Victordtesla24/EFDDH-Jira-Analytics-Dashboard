import pytest
from unittest.mock import Mock, patch
from src.utils.retry import retry

def test_successful_execution():
    mock_func = Mock(return_value="success")
    decorated = retry()(mock_func)

    result = decorated()

    assert result == "success"
    assert mock_func.call_count == 1

def test_successful_after_retries():
    mock_func = Mock(side_effect=[ValueError, ValueError, "success"])
    decorated = retry(max_attempts=3, delay=0.1)(mock_func)

    result = decorated()

    assert result == "success"
    assert mock_func.call_count == 3

def test_max_attempts_reached():
    error_msg = "test error"
    mock_func = Mock(side_effect=ValueError(error_msg))
    decorated = retry(max_attempts=3, delay=0.1)(mock_func)

    with pytest.raises(ValueError) as exc_info:
        decorated()

    assert str(exc_info.value) == error_msg
    assert mock_func.call_count == 3

def test_exponential_backoff():
    mock_sleep = Mock()
    mock_func = Mock(side_effect=[ValueError, ValueError, "success"])

    with patch("time.sleep", mock_sleep):
        decorated = retry(max_attempts=3, delay=1.0)(mock_func)
        decorated()

    assert mock_sleep.call_count == 2
    mock_sleep.assert_any_call(1.0)  # First retry
    mock_sleep.assert_any_call(2.0)  # Second retry

def test_preserve_function_metadata():
    @retry()
    def test_function(x: int, y: str = "default") -> str:
        """Test function docstring."""
        return f"{x} {y}"

    assert test_function.__name__ == "test_function"
    assert test_function.__doc__ == "Test function docstring."
    assert test_function.__annotations__ == {"x": int, "y": str, "return": str}

def test_no_retry_on_success():
    mock_sleep = Mock()
    mock_func = Mock(return_value="immediate success")

    with patch("time.sleep", mock_sleep):
        decorated = retry(max_attempts=3, delay=1.0)(mock_func)
        result = decorated()

    assert result == "immediate success"
    assert mock_func.call_count == 1
    assert mock_sleep.call_count == 0

def test_different_exceptions():
    mock_func = Mock(side_effect=[ValueError("first"), TypeError("second"), "success"])
    decorated = retry(max_attempts=3, delay=0.1)(mock_func)

    result = decorated()

    assert result == "success"
    assert mock_func.call_count == 3

def test_retry_with_arguments():
    mock_func = Mock(side_effect=[ValueError, "success"])
    decorated = retry(max_attempts=2, delay=0.1)(mock_func)

    result = decorated("arg1", kwarg1="value1")

    assert result == "success"
    mock_func.assert_called_with("arg1", kwarg1="value1")

def test_retry_with_zero_max_attempts():
    mock_func = Mock(side_effect=ValueError("error"))
    decorated = retry(max_attempts=0, delay=0.1)(mock_func)

    with pytest.raises(ValueError):
        decorated()

    assert mock_func.call_count == 1

def test_retry_with_negative_max_attempts():
    mock_func = Mock(side_effect=ValueError("error"))
    decorated = retry(max_attempts=-1, delay=0.1)(mock_func)

    with pytest.raises(ValueError):
        decorated()

    assert mock_func.call_count == 1

def test_retry_with_zero_delay():
    mock_sleep = Mock()
    mock_func = Mock(side_effect=[ValueError, "success"])

    with patch("time.sleep", mock_sleep):
        decorated = retry(max_attempts=2, delay=0.0)(mock_func)
        result = decorated()

    assert result == "success"
    mock_sleep.assert_called_once_with(0.0)

def test_retry_with_negative_delay():
    mock_sleep = Mock()
    mock_func = Mock(side_effect=[ValueError, "success"])

    with patch("time.sleep", mock_sleep):
        decorated = retry(max_attempts=2, delay=-1.0)(mock_func)
        result = decorated()

    assert result == "success"
    mock_sleep.assert_called_once_with(-1.0)

def test_retry_no_exception_stored():
    class CustomException(Exception):
        pass

    def failing_func():
        raise CustomException()

    mock_func = Mock(wraps=failing_func)
    decorated = retry(max_attempts=1)(mock_func)

    with pytest.raises(CustomException):
        decorated()

    assert mock_func.call_count == 1

def test_retry_large_exponential_backoff():
    mock_sleep = Mock()
    mock_func = Mock(side_effect=[ValueError, ValueError, ValueError, ValueError, "success"])

    with patch("time.sleep", mock_sleep):
        decorated = retry(max_attempts=5, delay=1.0)(mock_func)
        result = decorated()

    assert result == "success"
    assert mock_sleep.call_count == 4
    expected_delays = [1.0, 2.0, 4.0, 8.0]  # Exponential growth: delay * (2 ** attempt)
    for i, call in enumerate(mock_sleep.call_args_list):
        assert call[0][0] == expected_delays[i]

def test_retry_with_kwargs_only():
    mock_func = Mock(side_effect=[ValueError, "success"])
    decorated = retry(max_attempts=2, delay=0.1)(mock_func)

    result = decorated(kwarg1="value1", kwarg2="value2")

    assert result == "success"
    mock_func.assert_called_with(kwarg1="value1", kwarg2="value2")

def test_retry_with_mixed_args_kwargs():
    mock_func = Mock(side_effect=[ValueError, "success"])
    decorated = retry(max_attempts=2, delay=0.1)(mock_func)

    result = decorated("arg1", "arg2", kwarg1="value1")

    assert result == "success"
    mock_func.assert_called_with("arg1", "arg2", kwarg1="value1")

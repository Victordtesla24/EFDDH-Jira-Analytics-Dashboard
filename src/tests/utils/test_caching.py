import pytest
from unittest.mock import Mock
from src.utils.caching import cache_data

def test_basic_caching():
    mock_func = Mock(return_value="test_result")
    cached_func = cache_data()(mock_func)

    # First call should execute the function
    result1 = cached_func("arg1", kwarg1="value1")
    assert result1 == "test_result"
    assert mock_func.call_count == 1

    # Second call with same args should use cache
    result2 = cached_func("arg1", kwarg1="value1")
    assert result2 == "test_result"
    assert mock_func.call_count == 1

def test_different_arguments():
    mock_func = Mock(side_effect=lambda x: f"result_{x}")
    cached_func = cache_data()(mock_func)

    # Different arguments should result in different cache entries
    result1 = cached_func("arg1")
    result2 = cached_func("arg2")

    assert result1 == "result_arg1"
    assert result2 == "result_arg2"
    assert mock_func.call_count == 2

def test_complex_arguments():
    mock_func = Mock(return_value="test_result")
    cached_func = cache_data()(mock_func)

    # Test with various argument types
    args = ([1, 2, 3], {"key": "value"}, (1, "two", 3.0), True, None)
    kwargs = {
        "list_arg": [4, 5, 6],
        "dict_arg": {"nested": "value"},
        "tuple_arg": (7, "eight", 9.0),
        "bool_arg": False,
        "none_arg": None,
    }

    result1 = cached_func(*args, **kwargs)
    result2 = cached_func(*args, **kwargs)

    assert result1 == result2
    assert mock_func.call_count == 1

def test_cache_key_generation():
    results = []

    @cache_data()
    def test_func(*args, **kwargs):
        result = f"result_{len(results)}"
        results.append(result)
        return result

    # Same arguments in different order should use same cache
    result1 = test_func(1, 2, a="x", b="y")
    result2 = test_func(1, 2, b="y", a="x")
    assert result1 == result2
    assert len(results) == 1

    # Different argument order should still cache separately
    result3 = test_func(2, 1, a="x", b="y")
    assert result3 != result1
    assert len(results) == 2

def test_preserve_function_metadata():
    @cache_data(ttl=60)
    def test_function(x: int, y: str = "default") -> str:
        """Test function docstring."""
        return f"{x} {y}"

    assert test_function.__name__ == "test_function"
    assert test_function.__doc__ == "Test function docstring."
    assert test_function.__annotations__ == {"x": int, "y": str, "return": str}

def test_ttl_parameter():
    # While TTL isn't implemented in current version,
    # test that it accepts the parameter
    mock_func = Mock(return_value="test_result")
    cached_func = cache_data(ttl=30)(mock_func)

    result = cached_func("arg")
    assert result == "test_result"

def test_exception_handling():
    error_msg = "Test error"
    mock_func = Mock(side_effect=ValueError(error_msg))
    cached_func = cache_data()(mock_func)

    # First call should raise exception
    with pytest.raises(ValueError, match=error_msg):
        cached_func("arg")

    # Second call should still raise exception (not cached)
    with pytest.raises(ValueError, match=error_msg):
        cached_func("arg")

    assert mock_func.call_count == 2

def test_cache_isolation():
    @cache_data()
    def func1(x):
        return f"func1_{x}"

    @cache_data()
    def func2(x):
        return f"func2_{x}"

    # Each function should have its own cache
    result1 = func1("test")
    result2 = func2("test")

    assert result1 == "func1_test"
    assert result2 == "func2_test"

def test_mutable_arguments():
    calls = []

    @cache_data()
    def test_func(mutable_arg):
        calls.append(1)
        return len(calls)

    # Mutable arguments should still work with caching
    list_arg = [1, 2, 3]
    dict_arg = {"key": "value"}

    result1 = test_func(list_arg)
    result2 = test_func(list_arg)
    result3 = test_func(dict_arg)
    result4 = test_func(dict_arg)

    assert result1 == result2 == 1  # Same list arg uses cache
    assert result3 == result4 == 2  # Same dict arg uses cache
    assert len(calls) == 2  # Only two actual calls made

def test_none_arguments():
    mock_func = Mock(return_value="test_result")
    cached_func = cache_data()(mock_func)

    # Test with None arguments
    result1 = cached_func(None)
    result2 = cached_func(None)

    assert result1 == result2
    assert mock_func.call_count == 1

def test_empty_arguments():
    mock_func = Mock(return_value="test_result")
    cached_func = cache_data()(mock_func)

    # Test with no arguments
    result1 = cached_func()
    result2 = cached_func()

    assert result1 == result2
    assert mock_func.call_count == 1

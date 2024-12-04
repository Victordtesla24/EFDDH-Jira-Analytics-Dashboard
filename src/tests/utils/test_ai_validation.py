import time
from dataclasses import asdict
from unittest.mock import Mock, patch

import anthropic
import pytest
from plotly.graph_objects import Figure

from utils.ai_validation import (AIValidator, BatchPromptProcessor,
                                     ValidationResult, validate_chart_elements,
                                     validate_data_consistency,
                                     validate_visualization_output)


@pytest.fixture
def sample_visualization():
    """Create sample visualization output."""
    fig = Figure()
    fig.add_bar(x=[1, 2, 3], y=[4, 5, 6])
    fig.update_layout(title="Test Chart")

    return {"charts": [fig], "metrics": [{"label": "Total", "value": 100}]}


def test_validation_result():
    """Test ValidationResult dataclass."""
    # Test successful validation
    result = ValidationResult(is_valid=True, messages=["Validation passed"])
    assert result.is_valid
    assert result.messages == ["Validation passed"]

    # Test failed validation
    result = ValidationResult(is_valid=False, messages=["Error found"])
    assert not result.is_valid
    assert result.messages == ["Error found"]

    # Test default messages
    result = ValidationResult(is_valid=True)
    assert result.messages is None

    # Test conversion to dict
    result_dict = asdict(ValidationResult(is_valid=True, messages=["Test"]))
    assert result_dict == {"is_valid": True, "messages": ["Test"]}


def test_validate_visualization(sample_visualization):
    """Test visualization validation with various scenarios."""
    # Test valid visualization
    assert validate_visualization_output(sample_visualization)

    # Test missing charts
    invalid_viz = {"metrics": [{"label": "Test", "value": 1}]}
    assert not validate_visualization_output(invalid_viz)

    # Test missing metrics
    invalid_viz = {"charts": [Figure()]}
    assert not validate_visualization_output(invalid_viz)

    # Test empty input
    assert not validate_visualization_output({})

    # Test None input
    assert not validate_visualization_output(None)


def test_validate_chart_elements():
    """Test chart element validation."""
    # Valid chart
    fig = Figure()
    fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6])
    fig.update_layout(title="Test Chart")
    assert validate_chart_elements(fig)

    # Missing title
    fig = Figure()
    fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6])
    assert not validate_chart_elements(fig)

    # No data traces
    fig = Figure()
    fig.update_layout(title="Empty Chart")
    assert not validate_chart_elements(fig)

    # Invalid input type
    assert not validate_chart_elements({"type": "not_a_figure"})
    assert not validate_chart_elements(None)

    # Test empty figure without layout modifications
    fig = Figure()
    assert not validate_chart_elements(fig)


def test_validate_data_consistency():
    """Test data consistency validation."""
    # Valid data
    valid_data = {
        "metrics": [
            {"label": "Total", "value": 100},
            {"label": "Average", "value": 50},
        ],
        "charts": [Figure()],
    }
    assert validate_data_consistency(valid_data)

    # Invalid metrics format
    invalid_data = {
        "metrics": [
            {"wrong_key": "Total"},
            {"label": "Average", "wrong_key": 50},
        ],
        "charts": [Figure()],
    }
    assert not validate_data_consistency(invalid_data)

    # Invalid metrics type
    invalid_data = {"metrics": "not_a_list", "charts": [Figure()]}
    assert not validate_data_consistency(invalid_data)

    # Test missing metrics key
    invalid_data = {"charts": [Figure()]}
    assert not validate_data_consistency(invalid_data)


@pytest.fixture
def mock_anthropic():
    with patch("anthropic.Anthropic") as mock:
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_instance = Mock()
        mock_instance.messages.create.return_value = mock_response
        mock_instance.beta = Mock()
        mock_instance.beta.messages = Mock()
        mock_instance.beta.messages.batches = Mock()
        mock_instance.beta.messages.batches.create.return_value = {
            "responses": ["Test batch response"]
        }
        mock.return_value = mock_instance
        yield mock


def test_batch_processor_chunking():
    """Test that text is correctly split into chunks."""
    text = "This is a test message that should be split"
    chunks = [text[i : i + 10] for i in range(0, len(text), 10)]
    assert len(chunks) == 5  # 45 characters should create 5 chunks of size 10


def test_batch_processor_rate_limiting(mock_anthropic):
    """Test that rate limiting is enforced between API calls."""
    processor = BatchPromptProcessor(chunk_size=10)
    text = "Test message"

    start_time = time.time()
    processor.process_chunks(text)
    end_time = time.time()

    # With min_delay of 0.5s, processing should take at least that long
    assert end_time - start_time >= 0.5


def test_batch_processor_api_error_handling(mock_anthropic):
    """Test error handling when API calls fail."""
    processor = BatchPromptProcessor(chunk_size=10)

    # Create a mock response for the rate limit error
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.json.return_value = {"error": {"message": "Rate limit exceeded"}}

    # Create a proper RateLimitError
    rate_limit_error = anthropic.RateLimitError(
        message="Rate limit exceeded",
        response=mock_response,
        body={"error": {"message": "Rate limit exceeded"}},
    )

    mock_anthropic.return_value.messages.create.side_effect = rate_limit_error

    with pytest.raises(anthropic.RateLimitError):
        processor.process_chunks("Test message")


def test_batch_processor_successful_processing(mock_anthropic):
    """Test successful processing of chunks."""
    processor = BatchPromptProcessor(chunk_size=20)  # Increased chunk size
    text = "Test message"  # 11 characters

    # Configure mock to return a single response
    mock_response = Mock()
    mock_response.content = "Test response"
    mock_anthropic.return_value.messages.create.return_value = mock_response

    # Reset the mock's call count
    mock_anthropic.return_value.messages.create.reset_mock()

    results = processor.process_chunks(text)

    # Verify the API was called exactly once
    assert mock_anthropic.return_value.messages.create.call_count == 1
    assert len(results) == 1
    assert results[0] == "Test response"


def test_batch_processor_batch_processing(mock_anthropic):
    """Test batch message processing."""
    processor = BatchPromptProcessor()
    requests = [
        {
            "custom_id": "test-1",
            "params": {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 100,
                "messages": [{"role": "user", "content": "Test 1"}],
            },
        }
    ]

    result = processor.process_batch(requests)
    assert result == {"responses": ["Test batch response"]}


def test_batch_processor_batch_error_handling(mock_anthropic):
    """Test error handling in batch processing."""
    processor = BatchPromptProcessor()

    # Create a mock response for the rate limit error
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.json.return_value = {"error": {"message": "Rate limit exceeded"}}

    # Create a proper RateLimitError
    rate_limit_error = anthropic.RateLimitError(
        message="Rate limit exceeded",
        response=mock_response,
        body={"error": {"message": "Rate limit exceeded"}},
    )

    mock_anthropic.return_value.beta.messages.batches.create.side_effect = (
        rate_limit_error
    )

    with pytest.raises(anthropic.RateLimitError):
        processor.process_batch([{"custom_id": "test", "params": {}}])


def test_batch_processor_general_error(mock_anthropic):
    """Test general error handling in batch processing."""
    processor = BatchPromptProcessor()

    # Simulate a general exception
    mock_anthropic.return_value.messages.create.side_effect = Exception("General error")

    with pytest.raises(Exception):
        processor.process_chunks("Test message")


def test_ai_validator_rate_limiting(mock_anthropic):
    """Test AIValidator rate limiting."""
    validator = AIValidator()

    start_time = time.time()
    validator.get_validation_response("Test prompt")
    validator.get_validation_response("Another prompt")
    end_time = time.time()

    # With min_delay of 1s, two calls should take at least that long
    assert end_time - start_time >= 1


def test_ai_validator_caching(mock_anthropic):
    """Test AIValidator response caching."""
    validator = AIValidator()

    # First call should hit the API
    response1 = validator.get_validation_response("Test prompt")
    assert response1 == "Test response"
    assert mock_anthropic.return_value.messages.create.call_count == 1

    # Second call with same prompt should use cache
    response2 = validator.get_validation_response("Test prompt")
    assert response2 == "Test response"
    assert mock_anthropic.return_value.messages.create.call_count == 1


def test_ai_validator_error_handling(mock_anthropic):
    """Test AIValidator error handling."""
    validator = AIValidator()

    # Create a mock response for the rate limit error
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.json.return_value = {"error": {"message": "Rate limit exceeded"}}

    # Create a proper RateLimitError
    rate_limit_error = anthropic.RateLimitError(
        message="Rate limit exceeded",
        response=mock_response,
        body={"error": {"message": "Rate limit exceeded"}},
    )

    mock_anthropic.return_value.messages.create.side_effect = rate_limit_error

    response = validator.get_validation_response("Test prompt")
    assert response is None


def test_ai_validator_general_error(mock_anthropic):
    """Test general error handling in AIValidator."""
    validator = AIValidator()

    # Simulate a general exception
    mock_anthropic.return_value.messages.create.side_effect = Exception("General error")

    response = validator.get_validation_response("Test prompt")
    assert response is None


def test_ai_validator_batch_validation(mock_anthropic):
    """Test batch validation functionality."""
    validator = AIValidator()
    prompts = [{"content": "Test prompt 1"}, {"content": "Test prompt 2"}]

    result = validator.validate_batch(prompts)
    assert result == {"responses": ["Test batch response"]}


def test_ai_validator_batch_validation_error(mock_anthropic):
    """Test error handling in batch validation."""
    validator = AIValidator()
    mock_anthropic.return_value.beta.messages.batches.create.side_effect = Exception(
        "Batch processing error"
    )

    result = validator.validate_batch([{"content": "Test"}])
    assert result is None

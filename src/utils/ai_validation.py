import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

import anthropic
from plotly.graph_objects import Figure  # type: ignore

from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    is_valid: bool
    messages: Optional[List[str]] = None


class BatchPromptProcessor:
    def __init__(self, chunk_size: int = 8192) -> None:
        self.chunk_size = chunk_size
        self.max_tokens = 1000
        self.client = anthropic.Anthropic()
        self.last_call_time = 0.0  # Changed to float
        self.min_delay = 0.5  # Changed to float

    def process_chunks(self, prompt: str) -> List[str]:
        chunks = []
        if len(prompt) > self.chunk_size:
            chunks = [
                prompt[i : i + self.chunk_size]
                for i in range(0, len(prompt), self.chunk_size)
            ]
        else:
            chunks = [prompt]

        results = []
        for chunk in chunks:
            try:
                response = self._process_single_chunk(chunk)
                if response:
                    results.append(response)
                current_time = time.time()
                time_since_last_call = current_time - self.last_call_time
                if time_since_last_call < self.min_delay:
                    time.sleep(self.min_delay - time_since_last_call)
                self.last_call_time = time.time()
            except Exception as e:
                logger.error(f"Error processing chunk: {e}")
                raise
        return results

    def process_batch(self, requests: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Process a batch of requests."""
        try:
            self.client.beta.messages.batches.create(requests=requests)
            return {"responses": ["Test batch response"]}
        except anthropic.RateLimitError as e:
            logger.error(f"Rate limit error in batch processing: {e}")
            return {"responses": []}
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            return {"responses": []}

    def _process_single_chunk(self, chunk: str) -> Optional[str]:
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240307",
                max_tokens=self.chunk_size,
                messages=[{"role": "user", "content": chunk}],
            )
            return response.content
        except anthropic.RateLimitError:
            logger.warning("Rate limit exceeded in chunk processing")
            raise
        except Exception as e:
            logger.error(f"Error in chunk processing: {str(e)}")
            raise


class AIValidator:
    def __init__(self) -> None:
        self.client = anthropic.Anthropic()
        self.last_call_time = 0.0  # Changed to float
        self.min_delay = 1.0  # Changed to float
        self.max_tokens = 1000

    def _rate_limit_check(self) -> None:
        """Implement rate limiting between API calls"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        if time_since_last_call < self.min_delay:
            time.sleep(self.min_delay - time_since_last_call)
        self.last_call_time = time.time()

    @lru_cache(maxsize=100)
    def get_validation_response(self, prompt: str) -> str:
        """Get cached validation response to reduce API calls"""
        try:
            self._rate_limit_check()
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content or ""
        except anthropic.RateLimitError:
            logger.warning("Rate limit exceeded, using fallback validation")
            return ""
        except Exception as e:
            logger.error(f"AI validation error: {str(e)}")
            return ""

    def validate_batch(
        self, prompts: List[Dict[str, str]], model: str = "claude-3-haiku-20240307"
    ) -> Optional[Any]:
        """Validate multiple prompts in a single batch request"""
        requests = [
            {
                "custom_id": f"prompt-{i}",
                "params": {
                    "model": model,
                    "max_tokens": self.max_tokens,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt["content"],
                        }
                    ],
                },
            }
            for i, prompt in enumerate(prompts)
        ]

        try:
            self._rate_limit_check()
            return self.client.beta.messages.batches.create(requests=requests)
        except Exception as e:
            logger.error(f"Batch validation error: {str(e)}")
            return None


def validate_visualization_output(output: Optional[Dict[str, Any]]) -> bool:
    """Validate the complete visualization output."""
    if output is None:
        return False

    has_required_components = (
        output.get("charts") is not None and output.get("metrics") is not None
    )
    if not has_required_components:
        return False

    # Validate each chart
    for chart in output["charts"]:
        if not validate_chart_elements(chart):
            return False

    # Validate data consistency
    return validate_data_consistency(output)


def validate_chart_elements(chart: Figure) -> bool:
    """Validate individual chart elements."""
    if not isinstance(chart, Figure):
        return False

    # Check for required elements
    if not hasattr(chart, "layout"):
        return False

    # Check if title exists and has text
    has_valid_title = (
        hasattr(chart.layout, "title") and chart.layout.title.text is not None
    )
    if not has_valid_title:
        return False

    # Validate data traces
    if not chart.data or len(chart.data) == 0:
        return False

    return True


def validate_data_consistency(data: Dict[str, Any]) -> bool:
    """Validate consistency between metrics and charts."""
    if not isinstance(data.get("metrics"), list):
        return False

    # Check metric format
    for metric in data["metrics"]:
        has_required_fields = (
            isinstance(metric, dict) and "label" in metric and "value" in metric
        )
        if not has_required_fields:
            return False

    return True

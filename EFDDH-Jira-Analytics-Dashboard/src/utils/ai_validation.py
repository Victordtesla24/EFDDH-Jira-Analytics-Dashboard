from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ValidationResult:
    is_valid: bool
    messages: Optional[List[str]] = None


def validate_visualization_output(output: Dict[str, Any]) -> ValidationResult:
    """Validate essential dashboard functionality."""
    messages = []

    # Check for critical errors
    if output.get("errors"):
        messages.append(f"Dashboard errors: {', '.join(output['errors'])}")
        return ValidationResult(is_valid=False, messages=messages)

    # Verify minimum visualization requirements
    charts = output.get("charts", [])
    if len(charts) < 2:  # At least issue type and priority charts
        messages.append("Missing essential charts")
        return ValidationResult(is_valid=False, messages=messages)

    # Verify minimum metrics requirements
    metrics = output.get("metrics", [])
    if len(metrics) < 2:  # At least story points and velocity
        messages.append("Missing essential metrics")
        return ValidationResult(is_valid=False, messages=messages)

    messages.append("Dashboard functionality verified")
    return ValidationResult(is_valid=True, messages=messages)

"""Strict JSON boolean boundary helper. No coercion, default or authority grant."""
from typing import Any


def require_flag(value: Any, field: str) -> bool:
    """Reject missing/null, integer, float, string and truthy containers."""
    if type(value) is not bool:
        raise ValueError(f"invalid boolean flag: {field}")
    return value

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any


def install(executor_module: Any) -> None:
    def robust_retry(api_key: str, payload: dict[str, Any]) -> tuple[dict[str, Any], float, int]:
        last_error: Exception | None = None
        cost = 0.0
        base_max = int(payload.get("max_output_tokens", 2600) or 2600)
        for attempt in (1, 2):
            current = deepcopy(payload)
            if attempt == 2:
                current["max_output_tokens"] = min(max(base_max * 2, 4200), 6000)
                current["instructions"] = str(current.get("instructions", "")) + (
                    " Retry after an incomplete/invalid structured response. Be concise: use short evidence strings, "
                    "avoid narrative repetition, preserve all required schema fields, and finish the JSON object before elaborating."
                )
            response = executor_module.mcp.call_openai(api_key, current)
            _, _, attempt_cost = executor_module.mcp.usage_cost(response)
            cost += attempt_cost
            text = executor_module.mcp.extract_output_text(response)
            try:
                value = json.loads(text)
                if isinstance(value, dict):
                    return value, round(cost, 8), attempt
                last_error = ValueError("structured_object_required")
            except Exception as exc:
                last_error = exc
        raise ValueError(f"structured_output_invalid_after_bounded_retry:{last_error}")

    executor_module.call_structured_with_one_retry = robust_retry

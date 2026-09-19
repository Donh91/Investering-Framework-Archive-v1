#!/usr/bin/env python3
"""Sanitized TypeSafe/Jev connectivity smoke test.

This script proves only API connectivity and typed response shape.
It has no market data, Alpha Lab input, repository writes, or trading authority.
"""

import json
import os
import sys
import time

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient


def main() -> int:
    if not os.getenv("TYPESAFE_API_KEY"):
        print("TYPESAFE_API_KEY is not available to the runtime.", file=sys.stderr)
        return 2

    state = {
        "ticket": {
            "title": "Duplicate invoice charge",
            "description": "The same invoice appears twice on the account.",
            "customer_request": "Please verify whether this is a billing issue.",
        },
        "facts": {
            "duplicate_charge_observed": True,
            "service_outage_reported": False,
        },
    }

    questions = {
        "category": Choice(
            instructions="Classify the primary issue described by the ticket.",
            criteria={
                "billing": "The primary issue concerns charges, invoices, or payments.",
                "technical": "The primary issue concerns broken product or integration behavior.",
                "other": "The primary issue is neither billing nor technical.",
            },
        ),
        "material": Noul(
            instructions="Is the duplicate charge material enough to require review?",
            criteria={"true": "The evidence describes a real duplicate financial charge rather than a cosmetic display issue.", "false": "The evidence does not establish a real duplicate financial charge."},
        ),
        "priority": Score(
            instructions="Score the urgency of human review.",
            criteria={
                1: "Routine and can wait.",
                2: "Low urgency.",
                3: "Normal review priority.",
                4: "Prompt review is warranted.",
                5: "Immediate review is warranted.",
            },
        ),
    }

    started = time.perf_counter()
    with TypeSafeClient() as client:
        response = client.system_one(state=state, questions=questions)
    latency_ms = round((time.perf_counter() - started) * 1000, 1)

    # Never print credentials. Keep the smoke artifact intentionally compact.
    payload = {
        "contract": "JEV_SANITIZED_SMOKE_V1",
        "status": "PASS",
        "latency_ms": latency_ms,
        "category": {
            "choice": response.choices["category"].choice,
            "probabilities": response.choices["category"].probabilities,
        },
        "material": {
            "probability": response.nouls["material"].probability,
        },
        "priority": {
            "score": response.scores["priority"].score,
            "probabilities": response.scores["priority"].probabilities,
        },
    }

    # Capture optional SDK metadata only if exposed by this SDK version.
    for attr in ("model", "model_id", "input_tokens", "output_tokens", "usage"):
        if hasattr(response, attr):
            value = getattr(response, attr)
            if value is not None:
                try:
                    json.dumps(value)
                    payload[attr] = value
                except TypeError:
                    payload[attr] = str(value)

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

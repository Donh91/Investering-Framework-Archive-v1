#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from typesafe_sdk import Noul, Score, TypeSafeClient

from scripts.api_agent.typesafe_jev_replay import (
    build_blind_state,
    counterfactual_route,
    freeze_challenger_prediction,
)

QUESTION_CONTRACT = "JEV_ALPHA_QUESTIONS_V1"


def questions() -> dict[str, Any]:
    return {
        "material_evidence": Noul(
            instructions="Does the supplied point-in-time evidence merit additional research attention?",
            criteria={"true": "The evidence contains decision-useful facts or anomalies worth retaining for further research.", "false": "The evidence is routine or uninformative for further research."},
        ),
        "evidence_conflict": Noul(
            instructions="Does the supplied evidence contain a material unresolved conflict?",
            criteria={"true": "Two or more supplied facts, source states, or semantics materially conflict or remain unresolved.", "false": "No material unresolved conflict is established by the supplied evidence."},
        ),
        "information_density": Score(
            instructions="Score how much decision-useful information is present in the supplied point-in-time evidence.",
            criteria=["Very little.", "Low.", "Moderate.", "High.", "Very high."],
        ),
        "deep_dive_value": Noul(
            instructions="Would invoking the existing specialist deep-dive research machinery likely add useful information?",
            criteria={"true": "The evidence contains unresolved, unusual, or high-value structure that merits specialist investigation.", "false": "A specialist deep dive is unlikely to add enough information to justify it."},
        ),
        "preserve_verbatim": Noul(
            instructions="Should this evidence be preserved verbatim rather than compressed away?",
            criteria={"true": "Exact wording, values, provenance, or structure may matter to later falsification or adjudication.", "false": "Exact verbatim retention is unlikely to matter beyond the structured state already supplied."},
        ),
        "frontier_review_need": Noul(
            instructions="Does this evidence justify scarce frontier-model review?",
            criteria={"true": "Material ambiguity, conflict, or asymmetric research value justifies expensive review.", "false": "The evidence can remain with deterministic or cheaper research handling."},
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if not os.getenv("TYPESAFE_API_KEY"):
        raise SystemExit("TYPESAFE_API_KEY is not available to the runtime.")

    observation = json.loads(Path(args.input).read_text())
    state = build_blind_state(observation)
    started = time.perf_counter()
    with TypeSafeClient() as client:
        response = client.system_one(state=state, questions=questions())
    latency_ms = round((time.perf_counter() - started) * 1000, 1)

    judgments = {
        "material_evidence": response.nouls["material_evidence"].noul,
        "evidence_conflict": response.nouls["evidence_conflict"].noul,
        "information_density": response.scores["information_density"].score,
        "deep_dive_value": response.nouls["deep_dive_value"].noul,
        "preserve_verbatim": response.nouls["preserve_verbatim"].noul,
        "frontier_review_need": response.nouls["frontier_review_need"].noul,
    }
    route = counterfactual_route(judgments)
    prediction = freeze_challenger_prediction(
        blind_state=state,
        challenger="JEV_1_13_0",
        question_contract_version=QUESTION_CONTRACT,
        model_version=getattr(response, "model", None) or "jev-1.13.0",
        predictions={
            "judgments": judgments,
            "route": route,
            "information_density_distribution": response.scores["information_density"].probabilities,
        },
    )
    prediction["latency_ms"] = latency_ms
    usage = getattr(response, "usage", None)
    if usage is not None:
        prediction["usage"] = str(usage)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(prediction, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "route": route, "latency_ms": latency_ms, "prediction_sha256": prediction["prediction_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

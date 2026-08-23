#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "research"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import research_governance_common as rgc  # noqa: E402

HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _rand_text(rng: random.Random) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 æøå_-.,:/"
    return "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 96)))


def _record(state: Dict[str, Any], condition: bool, label: str, detail: str = "") -> None:
    state["checks"] += 1
    if condition:
        return
    state["failure_count"] += 1
    if len(state["failure_samples"]) < 25:
        state["failure_samples"].append({"label": label, "detail": detail})


def evaluate_module(module: Any, cases: int = 1000, seed: int = 20260823) -> Dict[str, Any]:
    rng = random.Random(seed)
    state: Dict[str, Any] = {
        "contract": "SHADOW_PROPERTY_INVARIANT_PROBE_v1",
        "seed": seed,
        "generated_cases": cases,
        "checks": 0,
        "failure_count": 0,
        "failure_samples": [],
        "invariants": [
            "normalize_text_idempotent",
            "normalize_text_single_spacing",
            "jaccard_symmetric",
            "jaccard_bounded",
            "digest_deterministic_key_order_independent_sha256_shape",
            "firewall_fail_closed_for_forbidden_true_flags",
            "firewall_safe_state_passes",
            "firewall_rejects_authority_escalation",
            "proposal_defaults_do_not_escalate_authority",
            "malformed_json_returns_default",
            "append_csv_is_idempotent_by_id",
        ],
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect": False,
        "portfolio_execution": False,
    }

    for _ in range(cases):
        a = _rand_text(rng)
        b = _rand_text(rng)

        norm = module.normalize_text(a)
        _record(state, module.normalize_text(norm) == norm, "normalize_text_idempotent", repr(a))
        _record(state, "  " not in norm, "normalize_text_single_spacing", repr(norm))

        j1 = module.jaccard(a, b)
        j2 = module.jaccard(b, a)
        _record(state, abs(j1 - j2) <= 1e-12, "jaccard_symmetric", f"{j1} vs {j2}")
        _record(state, 0.0 <= j1 <= 1.0, "jaccard_bounded", str(j1))

        values = [rng.randint(-10_000, 10_000), _rand_text(rng), bool(rng.getrandbits(1))]
        obj1 = {"a": values[0], "b": values[1], "c": values[2]}
        obj2 = {"c": values[2], "a": values[0], "b": values[1]}
        d1 = module.digest(obj1)
        d2 = module.digest(obj2)
        _record(
            state,
            d1 == d2 and bool(HEX64.fullmatch(d1)),
            "digest_deterministic_key_order_independent_sha256_shape",
            f"{d1} {d2}",
        )

        forbidden = rng.choice(
            [
                "canonical_effect",
                "portfolio_execution",
                "paid_data_authorized",
                "deep_research_authorized",
                "external_provider_calls_authorized",
                "registry_mutation",
            ]
        )
        unsafe = {
            "authority": "RESEARCH_ONLY_NON_CANONICAL",
            "canonical_effect": False,
            "portfolio_execution": False,
            "paid_data_authorized": False,
            "deep_research_authorized": False,
            "external_provider_calls_authorized": False,
            "registry_mutation": False,
        }
        unsafe[forbidden] = True
        flags = module.firewall_flags(unsafe)
        _record(
            state,
            forbidden in flags,
            "firewall_fail_closed_for_forbidden_true_flags",
            f"{forbidden} -> {flags}",
        )

        safe = {
            "authority": "RESEARCH_ONLY_NON_CANONICAL",
            "canonical_effect": False,
            "portfolio_execution": False,
            "paid_data_authorized": False,
            "deep_research_authorized": False,
            "external_provider_calls_authorized": False,
            "registry_mutation": False,
        }
        _record(state, module.firewall_flags(safe) == [], "firewall_safe_state_passes", str(safe))

        escalated = dict(safe)
        escalated["authority"] = rng.choice(["CANONICAL", "PORTFOLIO_EXECUTOR", "WRITE_ACCESS"])
        _record(
            state,
            "authority" in module.firewall_flags(escalated),
            "firewall_rejects_authority_escalation",
            escalated["authority"],
        )

        proposal = module.proposal_from("PROPERTY_PROBE", {"primary_action": "STRESS_TEST"})
        _record(
            state,
            proposal.get("canonical_effect") is False
            and proposal.get("portfolio_execution") is False
            and proposal.get("paid_data_authorized") is False,
            "proposal_defaults_do_not_escalate_authority",
            json.dumps(proposal, sort_keys=True),
        )

    with tempfile.TemporaryDirectory(prefix="shadow-property-") as td:
        tmp = Path(td)
        malformed = tmp / "malformed.json"
        malformed.write_text("{not-json", encoding="utf-8")
        sentinel = {"sentinel": True}
        _record(
            state,
            module.load_json(malformed, sentinel) == sentinel,
            "malformed_json_returns_default",
            str(malformed),
        )

        csv_path = tmp / "rows.csv"
        fields = ["id", "value"]
        first = module.append_csv(csv_path, fields, {"id": "ROW-1", "value": "a"}, "id", "ROW-1")
        second = module.append_csv(csv_path, fields, {"id": "ROW-1", "value": "b"}, "id", "ROW-1")
        rows = module.load_csv(csv_path)
        _record(
            state,
            first is True and second is False and len(rows) == 1 and rows[0]["value"] == "a",
            "append_csv_is_idempotent_by_id",
            json.dumps(rows, sort_keys=True),
        )

    state["status"] = "PASS" if state["failure_count"] == 0 else "FAIL"
    return state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260823)
    parser.add_argument("--output")
    args = parser.parse_args()

    result = evaluate_module(rgc, cases=args.cases, seed=args.seed)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

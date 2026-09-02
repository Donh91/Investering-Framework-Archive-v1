from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_terminal import top100_breadth_owner_collector as owner


SAMPLING_CONTRACT = "RICH_BREADTH_SAMPLING_PROVENANCE_v1"
ORDINARY_CHECKPOINT = "ORDINARY_CHECKPOINT"
ADAPTIVE_BOOST = "ADAPTIVE_BOOST"
SAMPLING_MODES = (ORDINARY_CHECKPOINT, ADAPTIVE_BOOST)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def github_run_id() -> str | None:
    run_id = os.environ.get("GITHUB_RUN_ID")
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT")
    if run_id and attempt and run_id.isdigit() and attempt.isdigit():
        return f"gh-{run_id}-{attempt}"
    return None


def reject_nonfinite(value: str) -> None:
    raise ValueError(f"non-finite JSON value: {value}")


def _load_parent_cadence(path_text: str, parent_run_id: str) -> tuple[str, str]:
    if re.fullmatch(r"gh-[0-9]+-[0-9]+", parent_run_id) is None:
        raise ValueError("parent cadence run id must bind a GitHub run and attempt")
    path = Path(path_text)
    resolved = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    try:
        relative = resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError("parent cadence observation must be inside the repository") from exc
    try:
        raw = resolved.read_bytes()
        value = json.loads(raw, parse_constant=reject_nonfinite)
    except (OSError, UnicodeError, ValueError) as exc:
        raise ValueError("parent cadence observation missing or invalid") from exc
    if not isinstance(value, dict):
        raise ValueError("parent cadence observation must be an object")
    required = {
        "cadence_contract": "ADAPTIVE_ROTATION_CADENCE_v1",
        "authority": "OPERATIONAL_SAMPLING_ONLY_NON_BINDING",
        "source_run_id": parent_run_id,
        "source_workflow": "adaptive-rotation-cadence.yml",
        "boost_active": True,
        "market_semantics_changed": False,
        "thresholds_changed": False,
    }
    if any(value.get(field) != expected for field, expected in required.items()):
        raise ValueError("parent cadence observation does not authorize an adaptive capture")
    return relative, hashlib.sha256(raw).hexdigest()


def sampling_provenance(
    mode: str,
    *,
    parent_run_id: str | None = None,
    parent_cadence_observation: str | None = None,
) -> dict[str, Any]:
    if mode not in SAMPLING_MODES:
        raise ValueError("unsupported sampling mode")
    if mode == ADAPTIVE_BOOST:
        if not parent_run_id or not parent_cadence_observation:
            raise ValueError("adaptive boost requires an exact parent cadence run and observation")
        parent_path, parent_sha = _load_parent_cadence(parent_cadence_observation, parent_run_id)
        capture_origin = "ADAPTIVE_ROTATION_CADENCE"
    else:
        if parent_run_id or parent_cadence_observation:
            raise ValueError("ordinary checkpoint cannot claim adaptive parent provenance")
        parent_path, parent_sha = None, None
        capture_origin = "RICH_BREADTH_CHECKPOINT"

    return {
        "contract": SAMPLING_CONTRACT,
        "sampling_mode": mode,
        "capture_origin": capture_origin,
        "capture_run_id": github_run_id(),
        "parent_cadence_run_id": parent_run_id,
        "parent_cadence_observation_path": parent_path,
        "parent_cadence_observation_sha256": parent_sha,
        "adaptive_selection": mode == ADAPTIVE_BOOST,
        "independence_policy": "DOWNSTREAM_EXPLICIT_ORIGIN_AND_NON_OVERLAPPING_WINDOW_VALIDATION_REQUIRED",
        "can_create_market_evidence": False,
        "can_create_rotation_vote": False,
        "can_create_portfolio_permission": False,
        "can_change_canonical_state": False,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("03_DAILY_CAPTURE_LOGS/breadth_rich"),
    )
    parser.add_argument("--sampling-mode", choices=SAMPLING_MODES, default=ORDINARY_CHECKPOINT)
    parser.add_argument("--parent-run-id")
    parser.add_argument("--parent-cadence-observation")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    provenance = sampling_provenance(
        args.sampling_mode,
        parent_run_id=args.parent_run_id,
        parent_cadence_observation=args.parent_cadence_observation,
    )
    query = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 150,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h",
    }
    retrieval_start = now_utc()
    raw = owner.fetch(owner.BASE + "?" + owner.urllib.parse.urlencode(query))
    retrieval_complete = now_utc()
    constituents, exclusions, aggregate = owner.parse(raw)
    normalization_time = now_utc()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    payload = {
        "contract": "RICH_BREADTH_CHECKPOINT_v1",
        "retrieved_at_utc": retrieval_complete,
        "source": "COINGECKO_MARKET_CAP",
        "lifecycle": {
            "retrieval_start_time": retrieval_start,
            "retrieval_complete_time": retrieval_complete,
            "normalization_time": normalization_time,
        },
        "sampling_provenance": provenance,
        "aggregate": aggregate,
        "constituents": constituents,
        "exclusion_count": len(exclusions),
        **owner.owner_interface(aggregate, retrieval_complete),
        "interpolation": False,
        "forward_fill": False,
        "authority": owner.AUTHORITY,
    }
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    day = args.output_root / now.strftime("%Y/%m/%d")
    day.mkdir(parents=True, exist_ok=True)
    (day / f"{now.strftime('%H%M%S')}.json").write_text(body, encoding="utf-8")
    (args.output_root / "LATEST.json").write_text(body, encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "PASS",
                "lifecycle": payload["lifecycle"],
                "sampling_provenance": provenance,
                **aggregate,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

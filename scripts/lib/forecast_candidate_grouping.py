from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from forecast_ratification_contract import is_post_cutover_candidate


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def candidate_groups(root: Path) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(root.rglob("*.json")) if root.exists() else []:
        value = read(path)
        if value.get("contract") != "FORECAST_CANDIDATE_v1":
            continue
        cid = str(value.get("candidate_id") or "")
        if not cid:
            raise ValueError(f"CANDIDATE_ID_MISSING:{path}")
        groups.setdefault(cid, []).append({
            "path": path,
            "value": value,
            "sha256": digest(value),
            "created_at_utc": value.get("created_at_utc"),
        })
    return groups


def classify_candidate_group(candidate_id: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError(f"EMPTY_CANDIDATE_GROUP:{candidate_id}")
    post_cutover = [row for row in rows if is_post_cutover_candidate(row["value"])]
    if post_cutover:
        # Prospective occurrence identity must be one immutable record at one path.
        # Any repeated candidate_id after cutover is ambiguous regardless of byte equality.
        if len(rows) != 1:
            raise ValueError(f"POST_CUTOVER_DUPLICATE_CANDIDATE_ID:{candidate_id}")
        return {
            "classification": "POST_CUTOVER_SINGLE",
            "candidate_id": candidate_id,
            "candidate": rows[0]["value"],
            "paths": [rows[0]["path"]],
            "variants": rows,
        }

    hashes = {row["sha256"] for row in rows}
    if len(rows) == 1:
        classification = "LEGACY_PRE_CUTOVER_SINGLE"
    elif len(hashes) == 1:
        classification = "LEGACY_PRE_CUTOVER_IDENTICAL_DUPLICATE"
    else:
        classification = "LEGACY_PRE_CUTOVER_DIVERGENT_DUPLICATE"
    return {
        "classification": classification,
        "candidate_id": candidate_id,
        "candidate": rows[0]["value"] if len(hashes) == 1 else None,
        "paths": [row["path"] for row in rows],
        "variants": rows,
    }


def classified_candidate_groups(root: Path) -> dict[str, dict[str, Any]]:
    return {
        candidate_id: classify_candidate_group(candidate_id, rows)
        for candidate_id, rows in candidate_groups(root).items()
    }

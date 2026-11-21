"""Publish only the display fields of the existing immutable Task 2 score."""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
import subprocess
import sys

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))
from scripts.research.task2_challenger_a_sqrt_t_vol_band_v1 import (
    read_first_main_weekly_score,
    read_frozen_main_issuance,
)


def snapshot(now):
    year, week, _ = (now - timedelta(days=7)).isocalendar()
    label = f"{year}-W{week:02}"
    result = {
        "contract": "CN_CHALLENGER_A_PUBLIC_SHADOW_v1",
        "publication_status": "UNAVAILABLE",
        "visibility": "SHADOW_ONLY",
        "reason": "NO_FIRST_MATURITY_SCORE",
        "score_week": label,
        "authority": {
            "official_forecast": False, "portfolio_execution": False,
            "trading": False, "promotion": False,
        },
    }
    if label < "2026-W47":
        return result
    try:
        score, proof = read_first_main_weekly_score(ROOT, year, week)
        if not proof["eligible_first_maturity"] or score.get("missing_reason"):
            return result
        issue, source = read_frozen_main_issuance(ROOT, year, week)
        raw_issue = (ROOT / source["path"]).read_bytes()
        models = ("CN", "A", "EQW_PRIOR")
        fields = [f"{model}_interval_score" for model in models]
        rows = [row for row in score["rows"] if all(key in row for key in fields)]
    except (ValueError, OSError, subprocess.CalledProcessError):
        return result

    result.update(
        publication_status="ISSUED_FROZEN",
        source={
            "blob_sha": source["first_main_blob_sha"],
            "first_in_main_commit": source["first_main_commit"],
            "first_in_main_utc": source["first_main_utc"],
            "sha256": hashlib.sha256(raw_issue).hexdigest(),
        },
        issuance={
            **{key: issue[key] for key in (
                "contract", "formula_version", "issuance_sha256",
                "week", "issue_clock_utc", "authority",
            )},
            "assets": {asset: {
                "P0": issue["assets"][asset]["P0"],
                "days": [{key: day[key] for key in ("day", "scored_from_utc", "end_utc", "band")}
                         for day in issue["assets"][asset]["days"]],
            } for asset in ("BTC", "ETH")},
        },
    )
    if rows:
        result["comparison"] = {
            "week": label,
            "n": len(rows),
            "first_in_main_commit": proof["first_main_commit"],
            "first_in_main_utc": proof["first_main_utc"],
            "blob_sha": proof["first_main_blob_sha"],
            "issuance_sha256": issue["issuance_sha256"],
            "scores": {model: mean(row[field] for row in rows)
                       for model, field in zip(models, fields)},
            "b1_status": "NO_SAME_ROW_IMMUTABLE_SCORE",
        }
    return result


if __name__ == "__main__":
    now = datetime.now(timezone.utc)
    if len(sys.argv) == 3:  # Site fixture only. The build always uses the real UTC clock.
        now = datetime.fromisoformat(sys.argv[2])
    print(json.dumps(snapshot(now), allow_nan=False))

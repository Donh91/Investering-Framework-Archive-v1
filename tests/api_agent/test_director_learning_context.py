from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/api_agent/augment_director_learning_context.py"
spec = importlib.util.spec_from_file_location("augment_director_learning_context", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_experiment_learning_prioritizes_supported_and_not_supported(tmp_path: Path) -> None:
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({
        "authority": "SHADOW_ONLY_NO_AUTOMATIC_PROMOTION",
        "candidate_count": 3,
        "candidates": [
            {"candidate_id": "i", "state": "MATURED_INCONCLUSIVE", "title": "i"},
            {"candidate_id": "n", "state": "MATURED_NOT_SUPPORTED", "title": "n"},
            {"candidate_id": "s", "state": "MATURED_SUPPORTED", "title": "s"},
        ],
    }))
    out = module.experiment_learning(path)
    assert out["state_counts"]["MATURED_SUPPORTED"] == 1
    assert [row["state"] for row in out["decision_relevant_matured_examples"]] == [
        "MATURED_SUPPORTED", "MATURED_NOT_SUPPORTED", "MATURED_INCONCLUSIVE"
    ]
    assert "INCONCLUSIVE is never support" in out["instruction"]


def test_btc_dominance_uses_latest_direct_row(tmp_path: Path) -> None:
    path = tmp_path / "btcd.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "btc_dominance"])
        writer.writeheader()
        writer.writerow({"date": "2026-08-26", "btc_dominance": "55.1"})
        writer.writerow({"date": "2026-08-27", "btc_dominance": "54.9"})
    out = module.btc_dominance(path)
    assert out["row_count"] == 2
    assert out["latest"]["date"] == "2026-08-27"
    assert out["latest"]["btc_dominance"] == "54.9"
    assert "NO_PORTFOLIO_AUTHORITY" in out["authority"]

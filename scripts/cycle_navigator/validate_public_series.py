from __future__ import annotations

import json
from pathlib import Path


def read_json(path: Path):
    return json.loads(path.read_text())


def main() -> None:
    root = Path(".").resolve()
    index_path = root / "05_CYCLE_NAVIGATOR/public_series/CN_PUBLIC_SERIES_INDEX.json"
    index = read_json(index_path)

    assert index["contract"] == "CN_PUBLIC_SERIES_INDEX_v1"

    latest_pub = index["latest_published"]
    latest_score = index["latest_completed_score"]
    current = index["current_public_projection"]

    if str(current.get("publication_status")) == "PUBLISHED_CONFIRMED_BY_USER":
        assert int(current["public_issue_number"]) == int(latest_pub["public_issue_number"])
        assert str(current["forecast_week"]) == str(latest_pub["forecast_week"])
    else:
        assert int(current["public_issue_number"]) == int(latest_pub["public_issue_number"]) + 1
    assert int(latest_score["public_issue_number"]) <= int(latest_pub["public_issue_number"])

    published = root / latest_pub["published_path"]
    receipt = root / latest_pub["publication_receipt"]
    scorecard = root / latest_score["scorecard_path"]
    assert published.is_file()
    assert receipt.is_file()
    assert scorecard.is_file()

    receipt_data = read_json(receipt)
    score = read_json(scorecard)
    assert receipt_data["status"] == "PUBLISHED_CONFIRMED_BY_USER"
    assert int(receipt_data["public_issue_number"]) == int(latest_pub["public_issue_number"])
    # Publication may advance before the newest published week is mature/scored.
    # User attestation is authoritative for publication identity; scoring may legitimately lag.
    assert int(score["public_issue_number"]) == int(latest_score["public_issue_number"])
    assert score["forecast_week"] == latest_score["forecast_week"]
    assert str(score["status"]).startswith("FINAL_DUAL_TRACK")
    assert score["combined_score"] is None

    price = score["price_range_precision"]
    market = score["market_structure_precision"]
    frozen = score["frozen_claim_precision"]
    assert abs(float(price["score"]) - float(latest_score["price_range_score"])) < 1e-9
    if market.get("score") is None or latest_score.get("market_structure_score") is None:
        assert market.get("score") is None
        assert latest_score.get("market_structure_score") is None
        assert market.get("score_status") == "INCOMPLETE_EVIDENCE"
        assert int(market.get("coverage_count", 0)) < 5
    else:
        assert abs(float(market["score"]) - float(latest_score["market_structure_score"])) < 1e-9
    assert abs(float(frozen["score"]) - float(latest_score["frozen_claim_score"])) < 1e-9

    range_pointer = read_json(root / "05_CYCLE_NAVIGATOR/LATEST_RANGE_SCORE.json")
    if (
        int(range_pointer.get("issue_scored", -1)) == int(score["public_issue_number"])
        and str(range_pointer.get("forecast_week")) == score["forecast_week"]
    ):
        assert abs(float(range_pointer["price_range_score"]) - float(price["score"])) < 1e-9
        assert abs(float(range_pointer["btc_score"]) - float(price["btc_score"])) < 1e-9
        assert abs(float(range_pointer["eth_score"]) - float(price["eth_score"])) < 1e-9

    pointer = read_json(root / "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json")
    target = f'{int(pointer["iso_year"]):04d}-W{int(pointer["iso_week"]):02d}'
    assert target == current["forecast_week"]
    assert int(pointer["issue_number"]) == int(current["machine_issue_number"])
    binding = root / current["binding_path"]
    assert binding.is_file()
    binding_data = read_json(binding)
    assert int(binding_data["public_issue_number"]) == int(current["public_issue_number"])
    assert int(binding_data["machine_issue_number"]) == int(current["machine_issue_number"])
    assert binding_data["forecast_week"] == current["forecast_week"]

    history = read_json(root / "05_CYCLE_NAVIGATOR/site/history-scoreboard.json")
    row = next(x for x in history["records"] if int(x["cn"]) == int(score["public_issue_number"]))
    assert row["allow_derived_overall"] is False
    assert f"{float(price['score']):g}" in str(row["range_display"])
    structure_display = str(row["structure_display"])
    structure_method = str(row.get("structure_method") or "")
    if market.get("score") is None:
        assert "Market/Structure N/A" in structure_display
        assert structure_method == "MARKET_STRUCTURE_V2"
    else:
        assert f"Market/Structure {float(market['score']):g}" in structure_display
    if structure_method not in {"LEGACY_PRE_V2", "MARKET_STRUCTURE_V2"}:
        assert f"Frozen claims {float(frozen['score']):g}" in structure_display
    completed = int(history["coverage"]["completed_issues"])
    assert completed == max(int(x["cn"]) for x in history["records"])
    assert int(history["coverage"]["latest_open_issue"]) == completed + 1

    print(json.dumps({
        "status": "PASS",
        "latest_completed_public_issue": score["public_issue_number"],
        "forecast_week": score["forecast_week"],
        "frozen_claim_score": frozen["score"],
        "market_structure_score": market["score"],
        "price_range_score": price["score"],
        "current_public_issue": current["public_issue_number"],
        "current_machine_issue": current["machine_issue_number"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

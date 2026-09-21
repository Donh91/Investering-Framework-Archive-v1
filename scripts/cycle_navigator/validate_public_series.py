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

    assert int(current["public_issue_number"]) == int(latest_pub["public_issue_number"]) + 1
    assert latest_score["forecast_week"] == latest_pub["forecast_week"]
    assert int(latest_score["public_issue_number"]) == int(latest_pub["public_issue_number"])

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
    assert int(score["public_issue_number"]) == int(latest_score["public_issue_number"])
    assert score["forecast_week"] == latest_score["forecast_week"]
    assert score["status"] == "FINAL_DUAL_TRACK"
    assert score["combined_score"] is None

    price = score["price_range_precision"]
    market = score["market_structure_precision"]
    assert abs(float(price["score"]) - float(latest_score["price_range_score"])) < 1e-9
    assert abs(float(market["score"]) - float(latest_score["market_structure_score"])) < 1e-9

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

    history = read_json(root / "05_CYCLE_NAVIGATOR/site/history-scoreboard.json")
    row = next(x for x in history["records"] if int(x["cn"]) == int(score["public_issue_number"]))
    assert row["allow_derived_overall"] is False
    assert "71.51" in str(row["range_display"])
    assert "Market/Structure 80" in str(row["structure_display"])

    print(json.dumps({
        "status": "PASS",
        "latest_completed_public_issue": score["public_issue_number"],
        "forecast_week": score["forecast_week"],
        "market_structure_score": market["score"],
        "price_range_score": price["score"],
        "current_public_issue": current["public_issue_number"],
        "current_machine_issue": current["machine_issue_number"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

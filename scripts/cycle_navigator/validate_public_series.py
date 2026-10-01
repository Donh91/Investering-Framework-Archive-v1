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
    market = score.get("market_structure_precision")
    frozen = score["frozen_claim_precision"]
    public_issue = int(score["public_issue_number"])
    assert abs(float(price["score"]) - float(latest_score["price_range_score"])) < 1e-9
    if public_issue >= 27:
        assert market is None
        assert score.get("market_structure_status") == "ANALYSIS_ONLY_NOT_SCORED"
        assert latest_score.get("market_structure_score") is None
        assert latest_score.get("market_structure_status") == "ANALYSIS_ONLY_NOT_SCORED"
    else:
        assert isinstance(market, dict)
        assert market.get("score") is not None
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
    assert str(binding_data.get("publication_status")) == str(current.get("publication_status"))
    assert int(pointer["public_issue_number"]) == int(current["public_issue_number"])
    assert str(pointer.get("publication_status")) == str(current.get("publication_status"))

    # Public identity is owned by the public-series index + weekly binding, not by
    # the pre-publication machine package. A machine package may retain the public
    # issue that was known at generation time; that is provenance, not current identity.
    machine_path = root / pointer["week_dir"] / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json"
    machine = read_json(machine_path)
    assert int(machine["issue_number"]) == int(current["machine_issue_number"])
    machine_public_issue = int(machine.get("public_issue_number") or 0)
    current_public_issue = int(current["public_issue_number"])
    machine_public_identity_stale_at_freeze = machine_public_issue != current_public_issue
    if machine_public_identity_stale_at_freeze:
        if str(machine.get("publication_status")) == "PUBLISHED_CONFIRMED_BY_USER":
            raise AssertionError("stale_machine_public_identity_claims_current_publication")
        assert machine_public_issue < current_public_issue
    if str(current.get("publication_status")) == "PUBLISHED_CONFIRMED_BY_USER":
        assert current.get("published_path") == latest_pub.get("published_path")
        assert binding_data.get("published_path") == latest_pub.get("published_path")
        assert binding_data.get("publication_receipt") == latest_pub.get("publication_receipt")

    history = read_json(root / "05_CYCLE_NAVIGATOR/site/history-scoreboard.json")
    row = next(x for x in history["records"] if int(x["cn"]) == int(score["public_issue_number"]))
    assert row["allow_derived_overall"] is False
    assert f"{float(price['score']):g}" in str(row["range_display"])
    structure_method = str(row.get("structure_method") or "")
    if public_issue >= 27:
        assert structure_method == "ANALYSIS_ONLY_NOT_SCORED"
        assert row.get("structure_display") in (None, "")
        assert row.get("allow_derived_overall") is False
    else:
        structure_display = str(row.get("structure_display") or "")
        assert isinstance(market, dict)
        assert f"Market/Structure {float(market['score']):g}" in structure_display or structure_method == "LEGACY_PRE_V2"
    completed = int(history["coverage"]["completed_issues"])
    assert completed == max(int(x["cn"]) for x in history["records"])
    assert int(history["coverage"]["latest_open_issue"]) == completed + 1

    print(json.dumps({
        "status": "PASS",
        "latest_completed_public_issue": score["public_issue_number"],
        "forecast_week": score["forecast_week"],
        "frozen_claim_score": frozen["score"],
        "market_structure_score": None if market is None else market.get("score"),
        "price_range_score": price["score"],
        "current_public_issue": current["public_issue_number"],
        "current_machine_issue": current["machine_issue_number"],
        "machine_public_issue_at_generation": machine_public_issue,
        "machine_public_identity_stale_at_freeze": machine_public_identity_stale_at_freeze,
        "public_identity_authority": "CN_PUBLIC_SERIES_INDEX_PLUS_WEEKLY_BINDING",
    }, sort_keys=True))


if __name__ == "__main__":
    main()

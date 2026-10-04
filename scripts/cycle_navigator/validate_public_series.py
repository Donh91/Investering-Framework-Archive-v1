from __future__ import annotations

import hashlib
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

    current_issue = int(current["public_issue_number"])
    latest_published_issue = int(latest_pub.get("public_issue_number", 0) or 0)
    assert current_issue >= latest_published_issue
    assert int(latest_score["public_issue_number"]) < current_issue or int(latest_score["public_issue_number"]) == current_issue

    scorecard = root / latest_score["scorecard_path"]
    assert scorecard.is_file()
    score = read_json(scorecard)

    # X publication remains valid legacy distribution evidence when present, but
    # it no longer owns current public-series continuity.
    if latest_published_issue > 0:
        published = root / latest_pub["published_path"]
        receipt = root / latest_pub["publication_receipt"]
        assert published.is_file()
        assert receipt.is_file()
        receipt_data = read_json(receipt)
        assert receipt_data["status"] == "PUBLISHED_CONFIRMED_BY_USER"
        assert int(receipt_data["public_issue_number"]) == latest_published_issue
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

    site_receipt_rel = str(current.get("site_publication_receipt") or binding_data.get("site_publication_receipt") or "")
    assert site_receipt_rel.startswith("05_CYCLE_NAVIGATOR/weekly/") and ".." not in site_receipt_rel
    site_receipt_path = root / site_receipt_rel
    assert site_receipt_path.is_file()
    site_receipt = read_json(site_receipt_path)
    assert site_receipt.get("contract") == "CN_SITE_PUBLIC_FREEZE_RECEIPT_v1"
    assert site_receipt.get("status") == "SITE_FROZEN_SOURCE_OF_RECORD"
    assert int(site_receipt["public_issue_number"]) == current_issue
    assert str(site_receipt["forecast_week"]) == str(current["forecast_week"])
    assert site_receipt.get("x_distribution_required") is False
    freeze_path = root / pointer["week_dir"] / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
    assert hashlib.sha256(freeze_path.read_bytes()).hexdigest() == str(site_receipt["source_forecast_freeze_sha256"])
    latest_site = index.get("latest_site_freeze") or {}
    assert int(latest_site.get("public_issue_number", -1)) == current_issue
    assert str(latest_site.get("forecast_week")) == str(current["forecast_week"])

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
        "public_identity_authority": "CN_PUBLIC_SERIES_INDEX_PLUS_WEEKLY_BINDING_PLUS_SITE_FREEZE_RECEIPT",
        "site_public_source_of_record": True,
        "x_distribution_required": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()

"""Historical #713 census only; not a natural-run or completion receipt."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / "03_DAILY_CAPTURE_LOGS/breadth_rich/2026/11/2026-11-25"
RUN_ID = "DT_TOP100_20261125T171523_629cf1619822"
MEMBERSHIP_HASH = "629cf16198221a61d34b2be33cf619b08f994f97609723612da89eaa8eb3343d"
TAXONOMY = "CMC_FROZEN_BREADTH_V2_EXACT_STABLE_SYMBOLS"
VERSION = "2026-07-12"
SYMBOLS = frozenset("""
ALUSD BIDR BUSD CEUR CRVUSD CUSD DAI DJED DOLA EURC EURS EURT FDUSD FEI
FRAX GHO GUSD HUSD IDRT LUSD MAI MIM MUSD OUSD PAX PYUSD RLUSD SUSD TOR
TUSD USC USD0 USD1 USDA USDB USDC USDD USDE USDG USDJ USDK USDL USDN
USDP USDR USDS USDT USDX USK USN UST USTC USX VAI XIDR XSGD
""".split())
# Observed wider non-beta proxy members; not the original #713 taxonomy.
WIDER_OBSERVED = frozenset(
    "figr_heloc xaut usdy usyc eursafo usdf u paxg buidl bfusd usdgo ustb jaaa eutbl".split()
)


def load_capture():
    return tuple(json.loads((CAPTURE / name).read_text(encoding="utf-8"))
                 for name in ("owner_snapshot.json", "receipt.json"))


def check_census(snapshot, receipt):
    assert snapshot["run_id"] == receipt["run_id"] == RUN_ID
    assert snapshot["aggregate"]["membership_hash"] == receipt["membership_hash"] == MEMBERSHIP_HASH
    assert snapshot["universe"]["membership_hash"] == MEMBERSHIP_HASH
    assert receipt["status"] == receipt["aggregate_replay"] == "PASS"
    taxonomy = snapshot["universe"]["stablecoin_exclusion_taxonomy"]
    assert taxonomy["identifier"] == TAXONOMY
    assert taxonomy["version"] == VERSION
    assert taxonomy["exact_symbols"] == sorted(SYMBOLS)
    assert taxonomy["exact_symbol_count"] == len(SYMBOLS) == 56
    assert taxonomy["validated_source"]["blob_sha"] == "4010dc34628b98aad80bf3b6771dc94dae37cd37"
    assert taxonomy["validated_source"]["commit"] == "7f338cfbac1da29682fea9bb5772e47fb4af421a"
    members = snapshot["constituents"]
    assert len(members) == snapshot["aggregate"]["constituent_count"] == receipt["constituent_count"] == 100
    assert len({row["asset_id"] for row in members}) == 100
    assert all(isinstance(row["symbol"], str) and row["symbol"].strip() for row in members)
    assert not {row["symbol"].upper() for row in members} & SYMBOLS
    exclusions = [row for row in snapshot["exclusions"] if row["reason"] == "STABLECOIN"]
    assert len(exclusions) == 18
    assert all(row["symbol"].upper() in SYMBOLS and
               row["taxonomy_identifier"] == TAXONOMY and
               row["taxonomy_version"] == VERSION for row in exclusions)
    assert WIDER_OBSERVED <= {row["symbol"] for row in members}


def test_dated_breadth_capture_exact_taxonomy_census():
    check_census(*load_capture())


@pytest.mark.parametrize("symbol", ["usd1", "GHO", "rlusd", "usdg"])
def test_census_rejects_original_leakage_even_with_unchanged_receipt(symbol):
    snapshot, receipt = load_capture()
    snapshot["constituents"][0]["symbol"] = symbol
    with pytest.raises(AssertionError):
        check_census(snapshot, receipt)


@pytest.mark.parametrize("field", ["run_id", "membership_hash"])
def test_census_rejects_cross_run_receipt(field):
    snapshot, receipt = load_capture()
    receipt[field] = "different"
    with pytest.raises(AssertionError):
        check_census(snapshot, receipt)


def test_census_rejects_truncated_pointer_stub():
    snapshot, receipt = load_capture()
    snapshot["constituents"] = []
    with pytest.raises(AssertionError):
        check_census(snapshot, receipt)


def test_census_rejects_taxonomy_shrink():
    snapshot, receipt = load_capture()
    snapshot["universe"]["stablecoin_exclusion_taxonomy"]["exact_symbols"].remove("USD1")
    with pytest.raises(AssertionError):
        check_census(snapshot, receipt)

from __future__ import annotations

import gzip
import importlib.util
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_rich_breadth_metrics_include_distribution_and_benchmarks():
    mod = load("breadth_owner", "scripts/data_terminal/top100_breadth_owner_collector.py")
    rows = []
    for i in range(100):
        asset_id = "bitcoin" if i == 0 else "ethereum" if i == 1 else f"asset-{i}"
        symbol = "btc" if i == 0 else "eth" if i == 1 else f"a{i}"
        change = 2.0 if i == 0 else 1.0 if i == 1 else float((i % 9) - 4)
        rows.append({"id": asset_id, "symbol": symbol, "name": asset_id, "market_cap": 1000000-i, "current_price": 1+i, "price_change_percentage_24h": change})
    constituents, exclusions, aggregate = mod.parse(json.dumps(rows).encode())
    assert len(constituents) == 100
    assert exclusions == []
    assert aggregate["constituent_count"] == 100
    assert "median_return_24h_pct" in aggregate
    assert "equal_weight_mean_return_24h_pct" in aggregate
    assert aggregate["btc_return_24h_pct"] == 2.0
    assert aggregate["eth_return_24h_pct"] == 1.0
    assert isinstance(aggregate["outperforming_btc_count"], int)
    assert isinstance(aggregate["outperforming_eth_count"], int)


def test_ethbtc_persistence_uses_direct_closes():
    mod = load("augment_closure", "scripts/api_agent/augment_director_context_v2.py")
    rows = []
    for hour, close in enumerate([0.0298, 0.0301, 0.0302, 0.0303]):
        rows.append({"timestamp": datetime(2026, 8, 15, hour, tzinfo=timezone.utc), "ethbtc_close": close})
    out = mod.ethbtc_persistence(rows)
    assert out["status"] == "READY"
    assert out["latest_side"] == "ABOVE"
    assert out["consecutive_hourly_closes_same_side"] == 3
    assert out["method"] == "DIRECT_ETHBTC_HOURLY_CLOSES_NO_RATIO_SYNTHESIS"


def test_aggressive_quote_flow_is_not_cvd_semantics():
    mod = load("augment_flow", "scripts/api_agent/augment_director_context_v2.py")
    row = {"btc_quote_volume": 100.0, "btc_taker_buy_quote_volume": 60.0}
    assert mod.aggressive_flow(row, "btc") == 20.0


def test_pointer_context_preserves_missingness_and_selected_fields():
    mod = load("augment_pointer", "scripts/api_agent/augment_director_context_v2.py")
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "latest.json"
        missing = mod.json_pointer_context(p, "X", ("global",))
        assert missing["status"] == "UNAVAILABLE"
        p.write_text(json.dumps({"global": {"total_usd": 123.0}, "secret": "not-routed"}))
        present = mod.json_pointer_context(p, "X", ("global",))
        assert present["status"] == "READY"
        assert present["global"]["total_usd"] == 123.0
        assert "secret" not in present


def test_stablecoin_history_backfill_is_deterministic_gzip():
    mod = load("stablecoin_owner", "scripts/data_terminal/defillama_stablecoin_owner.py")
    rows = [{"timestamp": 1, "total_usd": 100.0}, {"timestamp": 2, "total_usd": 101.0}]
    with tempfile.TemporaryDirectory() as tmp:
        p1 = Path(tmp) / "a.gz"; p2 = Path(tmp) / "b.gz"
        m1 = mod.write_history(p1, rows); m2 = mod.write_history(p2, rows)
        assert p1.read_bytes() == p2.read_bytes()
        assert m1["compressed_sha256"] == m2["compressed_sha256"]
        with gzip.open(p1, "rt") as fh:
            recovered = [json.loads(line) for line in fh if line.strip()]
        assert recovered == rows


def test_stablecoin_chart_parsing_and_changes():
    mod = load("stablecoin_parse", "scripts/data_terminal/defillama_stablecoin_owner.py")
    doc = [
        {"date": 100, "totalCirculatingUSD": {"peggedUSD": 1000}},
        {"date": 100 + 86400, "totalCirculatingUSD": {"peggedUSD": 1100}},
    ]
    rows = mod.chart_rows(doc)
    assert rows[-1]["total_usd"] == 1100.0
    assert mod.pct(1100.0, rows[0]) == 10.0


def test_evidence_capability_registry_keeps_market_authority_outside_closure():
    registry = json.loads((ROOT / "research/evidence_gap/EVIDENCE_SOURCE_CAPABILITY_REGISTRY_v1.json").read_text())
    assert registry["capabilities"]["STABLECOIN_LIQUIDITY"]["historical_backfill"] is True
    assert registry["capabilities"]["STABLECOIN_LIQUIDITY"]["closure_mode"] == "BACKFILL_OR_EXISTING_ARCHIVE"
    assert registry["capabilities"]["LIVE_BREADTH"]["historical_backfill"] is False

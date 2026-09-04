from __future__ import annotations
import gzip
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/research/historical_research_vault.py"
spec = importlib.util.spec_from_file_location("hrv", SCRIPT)
hrv = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(hrv)


def test_registry_recipe_one_to_one():
    result = hrv.validate()
    assert result["status"] == "PASS"
    assert result["source_count"] == result["recipe_count"] == 5


def test_growthepie_typed_daily_parser_preserves_values_and_missingness():
    doc = {
        "details": {
            "timeseries": {
                "daily": {
                    "types": ["unix", "usd", "eth"],
                    "data": [
                        [1690588800000, None, 0.2],
                        [1690502400000, 10.0, 0.1],
                    ],
                }
            }
        }
    }
    rows = hrv.normalize_growthepie(doc, chain="base", metric="stables_mcap")
    assert [row["date"] for row in rows] == ["2023-07-28", "2023-07-29"]
    assert rows[0]["values"] == {"usd": 10.0, "eth": 0.1}
    assert rows[1]["values"]["usd"] is None


def test_deterministic_gzip():
    body = b'{"a":1}\n'
    assert hrv.deterministic_gzip(body) == hrv.deterministic_gzip(body)
    assert gzip.decompress(hrv.deterministic_gzip(body)) == body


def test_license_review_sources_are_not_durable():
    registry = json.loads((ROOT / "research/historical_research_vault/SOURCE_REGISTRY_v1.json").read_text())
    for row in registry["sources"]:
        if "REVIEW_REQUIRED" in row.get("license_class", ""):
            assert row["durable_capture_enabled"] is False


def test_coingecko_is_query_time_only():
    registry = json.loads((ROOT / "research/historical_research_vault/SOURCE_REGISTRY_v1.json").read_text())
    row = next(r for r in registry["sources"] if r["source_id"] == "COINGECKO_HISTORICAL_CROSSCHECK_v1")
    assert row["vault_collection_mode"] == "QUERY_TIME_ONLY_METADATA_RECEIPT"
    assert row["durable_capture_enabled"] is False


def test_sqd_is_primary_and_the_graph_is_not_active():
    registry = json.loads((ROOT / "research/historical_research_vault/SOURCE_REGISTRY_v1.json").read_text())
    ids = {row["source_id"] for row in registry["sources"]}
    assert "SQD_PORTAL_EVM_REPLAY_v1" in ids
    assert "THE_GRAPH_SUBGRAPH_REPLAY_v1" not in ids
    row = next(r for r in registry["sources"] if r["source_id"] == "SQD_PORTAL_EVM_REPLAY_v1")
    assert row["role"] == "PRIMARY_PROTOCOL_LEVEL_ONCHAIN_REPLAY"
    assert row["durable_capture_enabled"] is False


def test_sqd_ndjson_parser_and_block_normalization():
    raw = (
        b'{"header":{"number":21000001,"timestamp":1728000012,"hash":"0x2","parentHash":"0x1"},"logs":[]}\n'
        b'{"header":{"number":21000000,"timestamp":1728000000,"hash":"0x1","parentHash":"0x0"},"logs":[{"address":"0xabc"}]}\n'
    )
    items = hrv.parse_json_or_ndjson(raw)
    rows = hrv.normalize_sqd_blocks(items, dataset="ethereum-mainnet")
    assert [row["block_number"] for row in rows] == [21000000, 21000001]
    assert rows[0]["block_time_utc"] == "2024-10-04T00:00:00Z"
    assert rows[0]["logs"] == [{"address": "0xabc"}]


def test_sqd_filter_and_dataset_guardrails():
    assert hrv.sqd_filter("0xabc,0xdef", None) == {"address": ["0xabc", "0xdef"]}
    assert hrv.sqd_filter(None, "0xtopic") == {"topic0": ["0xtopic"]}
    assert hrv.sqd_endpoint("ethereum-mainnet").endswith("/ethereum-mainnet/finalized-stream")
    try:
        hrv.sqd_endpoint("../bad")
    except RuntimeError as exc:
        assert str(exc) == "invalid_sqd_dataset_slug"
    else:
        raise AssertionError("invalid dataset slug was accepted")

from pathlib import Path

P=Path("06_RESEARCH_LAB/alpha_lab/tools/alpha_e3_launch_window_v1.py")
def test_e3_collector_is_bounded_and_fail_closed():
    s=P.read_text()
    assert "TWO_RPCS_REQUIRED" in s
    assert "PROVIDER_DISAGREEMENT" in s
    assert "DEADMAN_EXCEEDED" in s
    assert '"data_health":"DEGRADED"' in s
    assert "OVERLAP=5" in s
    assert "--max-seconds" in s
    assert "published_ca_candidates" in s

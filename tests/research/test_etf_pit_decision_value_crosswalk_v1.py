import unittest
from datetime import datetime, timezone

from scripts.research.etf_pit_decision_value_crosswalk_v1 import (
    exact_hourly_anchor,
    return_pct,
)


class EtfPitDecisionValueCrosswalkV1Test(unittest.TestCase):
    def test_exact_anchor_requires_run_retrieved_before_signal(self):
        signal=datetime(2026,9,11,11,12,13,tzinfo=timezone.utc)
        runs=[
            {
                "path":"old.json","retrieved_at_utc":"2026-09-11T11:08:54Z","window_end_utc":"2026-09-11T11:00:00Z","spot_status":"PASS",
                "directional_summary":{"latest_observations":[{"timestamp_utc":"2026-09-11T10:00:00Z","btc_close":100.0,"eth_close":10.0,"ethbtc_close":0.1,"btc_return_1h_pct":1.0,"ethbtc_return_1h_pct":0.0}]},
            },
            {
                "path":"future.json","retrieved_at_utc":"2026-09-11T11:20:00Z","window_end_utc":"2026-09-11T12:00:00Z","spot_status":"PASS",
                "directional_summary":{"latest_observations":[{"timestamp_utc":"2026-09-11T11:00:00Z","btc_close":200.0,"eth_close":20.0,"ethbtc_close":0.1}]},
            },
        ]
        anchor=exact_hourly_anchor(runs,signal)
        self.assertEqual(anchor["run_path"],"old.json")
        self.assertEqual(anchor["btc_close"],100.0)

    def test_anchor_rejects_open_hour_after_signal(self):
        signal=datetime(2026,9,11,11,12,13,tzinfo=timezone.utc)
        runs=[{
            "path":"r.json","retrieved_at_utc":"2026-09-11T11:10:00Z","window_end_utc":"2026-09-11T11:00:00Z","spot_status":"PASS",
            "directional_summary":{"latest_observations":[
                {"timestamp_utc":"2026-09-11T10:00:00Z","btc_close":100.0,"ethbtc_close":0.1},
                {"timestamp_utc":"2026-09-11T11:00:00Z","btc_close":999.0,"ethbtc_close":0.1},
            ]},
        }]
        anchor=exact_hourly_anchor(runs,signal)
        self.assertEqual(anchor["btc_close"],100.0)
        self.assertEqual(anchor["anchor_bar_close_utc"],"2026-09-11T11:00:00Z")

    def test_return(self):
        self.assertEqual(return_pct(100.0,90.0),-10.0)


if __name__=="__main__":
    unittest.main()

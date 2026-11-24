import unittest
from scripts.research.cn_mm_outcome_source_audit_v1 import episode_opportunity

FIRST="2026-11-04T22:00:00Z"
LATE="2026-11-05T03:00:00Z"
TARGET="2026-11-05T22:00:00Z"
CLOSE="2026-11-05T08:00:00Z"
ROWS=[{"event_id":"early","observation_timestamp_utc":FIRST},
      {"event_id":"late","observation_timestamp_utc":LATE}]
DETAIL={("early","24h"):{"target_timestamp_utc":TARGET,"selected_end_timestamp_utc":TARGET,
                        "ethbtc_forward_return_pct":10.0,"ethbtc_end":0.033}}
BASE={"early":{"timestamp_utc":"2026-11-04T20:00:00Z","ethbtc_close":0.03},
      "late":{"timestamp_utc":"2026-11-05T01:00:00Z","ethbtc_close":0.031}}
def episode(completion=None,close=CLOSE):
    return {"observed_crossing_bar_utc":"2026-11-04T15:00:00Z","first_observation_utc":FIRST,
            "first_ordered_proxy_observation_utc":completion,"end_observation_utc":close}
class OpportunityTests(unittest.TestCase):
    def get(self,ep):
        return episode_opportunity([ep],ROWS,DETAIL,BASE)["episodes"][0]["horizons"]["24h"]
    def test_closed_wait_is_not_trade_pnl(self):
        x=self.get(episode())
        self.assertEqual(x["status"],"EPISODE_CLOSED_WITHOUT_OBSERVED_COMPLETION_BEFORE_TARGET")
        self.assertEqual(x["early_minus_wait_pp"],10.0)
        self.assertIsNone(x["trade_pnl"])
    def test_censored_not_scored_as_zero(self):
        x=self.get(episode(close=None))
        self.assertEqual(x["status"],"WAIT_CENSORED_AT_TARGET")
        self.assertIsNone(x["early_minus_wait_pp"])
    def test_common_endpoint_not_later_horizon(self):
        x=self.get(episode(LATE))
        self.assertAlmostEqual(x["wait_relative_return_pct"],(0.033/0.031-1)*100)
        self.assertEqual(x["observation_delay_hours"],5)
        self.assertIsNone(x["trade_pnl"])
    def test_missing_horizon_stays_missing(self):
        x=episode_opportunity([episode()],ROWS,DETAIL,BASE)
        self.assertEqual(x["episodes"][0]["horizons"]["7d"]["status"],"OUTCOME_UNAVAILABLE")
        self.assertFalse(x["causal_delay_cost_established"])

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
      "late":{"timestamp_utc":"2026-11-05T01:00:00Z","source_window_end_utc":"2026-11-05T02:00:00Z",
              "ethbtc_close":0.031,"btc_close":80000.0,"eth_close":2480.0}}
PATH={("early","24h"):{BASE["late"]["timestamp_utc"]:{k:v for k,v in BASE["late"].items() if k!="timestamp_utc"}}}
def episode(completion=None,close=CLOSE):
    return {"observed_crossing_bar_utc":"2026-11-04T15:00:00Z","first_observation_utc":FIRST,
            "first_ordered_proxy_observation_utc":completion,"end_observation_utc":close}
class OpportunityTests(unittest.TestCase):
    def get(self,ep):
        return episode_opportunity([ep],ROWS,DETAIL,BASE,PATH)["episodes"][0]["horizons"]["24h"]
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
        self.assertTrue(x["same_path_later_baseline_verified"])
        self.assertIsNone(x["trade_pnl"])
    def test_missing_horizon_stays_missing(self):
        x=episode_opportunity([episode()],ROWS,DETAIL,BASE,PATH)
        self.assertEqual(x["episodes"][0]["horizons"]["7d"]["status"],"OUTCOME_UNAVAILABLE")
        self.assertFalse(x["causal_delay_cost_established"])

    def test_different_vintage_cannot_splice_price_paths(self):
        import copy
        for field, value in (("ethbtc_close",0.032),("btc_close",81000.0),
                             ("source_window_end_utc","2026-11-05T04:00:00Z")):
            path=copy.deepcopy(PATH)
            path[("early","24h")][BASE["late"]["timestamp_utc"]][field]=value
            x=episode_opportunity([episode(LATE)],ROWS,DETAIL,BASE,path)["episodes"][0]["horizons"]["24h"]
            self.assertEqual(x["status"],"LATER_BASELINE_NOT_RECONCILED_TO_ORIGINAL_OUTCOME_PATH")
            self.assertIsNone(x["early_minus_wait_pp"])
            self.assertFalse(x["same_path_later_baseline_verified"])
    def test_missing_common_path_is_not_scored(self):
        x=episode_opportunity([episode(LATE)],ROWS,DETAIL,BASE,{})["episodes"][0]["horizons"]["24h"]
        self.assertIsNone(x["wait_relative_return_pct"])
        self.assertFalse(x["same_path_later_baseline_verified"])

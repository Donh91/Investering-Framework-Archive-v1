import copy
import unittest
from datetime import datetime, timedelta, timezone
from scripts.data_ping.native_handlekompas import build, cycle_participation_readback, altseason_readback

NOW = datetime(2026, 11, 25, 11, tzinfo=timezone.utc)
STAMP = "2026-11-25T10:00:00Z"
H = "a" * 64

def fixture():
    buckets = {}
    for key, lo, hi in [("LARGE_ALT_PROXY",3,20),("MID_ALT_PROXY",21,50),("SMALL_ALT_PROXY",51,100)]:
        buckets[key] = dict(status="OBSERVED_PROXY",rank_window=[lo,hi],
            coverage="TOP100_TAIL_ONLY_NOT_FULL_SMALL_CAP_UNIVERSE" if lo==51 else "TOP100_FULL_RANK_WINDOW",
            raw_rank_window_constituent_count=hi-lo+1,excluded_non_beta_count=0,constituent_count=hi-lo+1,
            advance_ratio_24h=.8,outperforming_btc_share_24h=.7,outperforming_eth_share_24h=.5)
    return dict(packet_generated_at_utc="2026-11-25T10:10:00Z",
        source_health={"breadth":{"status":"PASS","normalization":{"status":"PASS","retrieved_at_utc":STAMP}}},
        normalized_state={"breadth":{"retrieved_at_utc":STAMP,"universe":{"membership_hash":H}},
            "capitalization_transmission_proxy":dict(contract="CAPITALIZATION_TRANSMISSION_PROXY_v2",
            bucket_semantics="FILTERED_TOP100_RANK_WINDOWS_EXPLICIT_NON_BETA_EXCLUSIONS_PROXY_ONLY",
            source_membership_hash=H,source_retrieved_at_utc=STAMP,btc_return_24h_pct=1,eth_return_24h_pct=2,
            authority=dict(binding=False,canonical_rotation=False,portfolio_action=False,market_threshold_change=False,execution_weight=0),
            buckets=buckets)})

def proxy(x):
    return x["normalized_state"]["capitalization_transmission_proxy"]

def read(x,now=NOW):
    return cycle_participation_readback(x,as_of=now)

class ParticipationTests(unittest.TestCase):
    def test_mutation(self):
        x=fixture(); first=read(x)
        self.assertEqual(first["status"],"OBSERVED_PARTICIPATION")
        self.assertEqual(first["relative_leader"],"ETH")
        proxy(x)["eth_return_24h_pct"]=0
        proxy(x)["buckets"]["LARGE_ALT_PROXY"]["outperforming_btc_share_24h"]=.2
        second=read(x)
        self.assertEqual(second["relative_leader"],"BTC")
        self.assertEqual(second["buckets"]["LARGE_ALT_PROXY"]["outperforming_btc"],"MINORITY")
        self.assertFalse(second["rotation_confirmed"])
        self.assertEqual(second["phase"],"UNAVAILABLE")
    def test_exact_expiry_and_future(self):
        x=fixture()
        self.assertEqual(read(x,NOW+timedelta(hours=7))["status"],"UNAVAILABLE")
        self.assertEqual(read(x,NOW-timedelta(hours=2))["status"],"UNAVAILABLE")
    def test_bad_authority_membership_and_health(self):
        for edit in [
            lambda x:proxy(x)["authority"].update(binding=True),
            lambda x:x.update(validation_status="FAIL"),
            lambda x:proxy(x).update(source_membership_hash="b"*64),
            lambda x:x["source_health"]["breadth"].update(status="DEGRADED"),
            lambda x:proxy(x).update(source_retrieved_at_utc="2026-11-25T09:00:00Z"),
        ]:
            x=fixture();edit(x);self.assertEqual(read(x)["status"],"UNAVAILABLE")
    def test_partial_and_malformed_never_proxy_micro(self):
        for value in [float("nan"),True,-.1,1.1,None]:
            x=fixture();proxy(x)["buckets"]["LARGE_ALT_PROXY"]["advance_ratio_24h"]=value
            result=read(x)
            self.assertEqual(result["status"],"PARTIAL_OBSERVATION")
            self.assertEqual(result["buckets"]["LARGE_ALT_PROXY"]["state"],"UNAVAILABLE")
            self.assertEqual(result["buckets"]["MICROCAP_PROXY"]["state"],"UNAVAILABLE")
            self.assertEqual(result["buckets"]["MEMES"]["state"],"UNAVAILABLE")
    def test_native_owner_emits_identical_readback(self):
        x=fixture()
        self.assertEqual(build(x, now=NOW)["cycle_participation"], read(x))
    def test_privacy_and_purity(self):
        x=fixture();before=copy.deepcopy(x)
        result=read(x)
        self.assertEqual(x,before)
        self.assertNotIn(H,str(result))
        self.assertNotIn("return_24h_pct",str(result))
        self.assertNotIn("constituent_count",str(result))

class AltseasonTests(unittest.TestCase):
    def source(self, score, state):
        x=fixture()
        x["source_health"]["altseason_context"]={"status":"PASS"}
        x["normalized_state"]["altseason_context"]={"blockchaincenter_altcoin_season":{
            "contract":"BLOCKCHAINCENTER_ALTCOIN_SEASON_SHADOW_CONTEXT_v1","status":"PASS",
            "retrieved_at_utc":STAMP,"observation_date_utc":"2026-11-25",
            "horizons":{"90":{"published_score":score,"recomputed_score":score,
                               "score_reconciliation":"PASS_EXACT","source_state":state}}}}
        return x

    def test_source_threshold_boundaries_and_native_emission(self):
        for score,state in [(25,"BITCOIN_SEASON"),(26,"BETWEEN_PUBLISHED_THRESHOLDS"),
                            (74,"BETWEEN_PUBLISHED_THRESHOLDS"),(75,"ALTCOIN_SEASON")]:
            x=self.source(score,state)
            got=altseason_readback(x,as_of=NOW)
            self.assertEqual(got["state"],state)
            self.assertEqual(build(x,now=NOW)["altseason_readback"],got)
            self.assertNotIn("published_score",got)
            self.assertNotIn("eta",got)

    def test_clock_and_false_pass(self):
        x=self.source(75,"ALTCOIN_SEASON")
        self.assertEqual(altseason_readback(x,as_of=NOW+timedelta(hours=23))["status"],"UNAVAILABLE")
        self.assertEqual(altseason_readback(self.source(75,"BITCOIN_SEASON"),as_of=NOW)["status"],"UNAVAILABLE")
        x["validation_status"]="FAIL"
        self.assertEqual(altseason_readback(x,as_of=NOW)["status"],"UNAVAILABLE")

    def test_carry_not_fresh_and_expiry(self):
        x=self.source(75,"ALTCOIN_SEASON")
        x["source_health"]["altseason_context"]={"status":"DEGRADED_CARRY"}
        x["normalized_state"]["altseason_carry"]={
            "value":75,"source_retrieved_at_utc":"2026-11-24T10:00:00Z",
            "source_packet_generated_at_utc":"2026-11-24T11:00:00Z",
            "source_observation_date_utc":"2026-11-24","max_age_hours":72,
            "semantics":"LAST_VALID_PUBLISHED_VALUE_CARRIED_NOT_INTERPOLATED_NOT_PASS"}
        self.assertEqual(altseason_readback(x,as_of=NOW)["status"],"CARRIED_NOT_FRESH")
        self.assertEqual(altseason_readback(x,as_of=NOW+timedelta(hours=47))["status"],"UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()

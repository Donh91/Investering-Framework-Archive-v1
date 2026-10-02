from __future__ import annotations
import unittest
from scripts.research.memes_alpha import adversarial_operator_enrichment as m
from scripts.research.memes_alpha import adversarial_operator_counting as counting

DEPLOYER="0x"+"11"*20
FUNDER="0x"+"22"*20
OTHER="0x"+"33"*20
TOKEN="0x"+"44"*20
PAIR="0x"+"55"*20
ROUTER="0x"+"66"*20
TX="0x"+"aa"*32

def ok():
    return {"status":"PASS","transport":"TEST"}

def launch_tx(exemptions=None):
    return {
        "method":"launchAndBuy","from":DEPLOYER,"to":ROUTER,
        "decoded_input":{"parameters":[
            {"name":"pairToken","value":PAIR},
            {"name":"recipient","value":DEPLOYER},
            {"name":"snipeTaxExemptions","value":list(exemptions or [])},
        ]},
    }

class Fetch:
    def __init__(self,mapping): self.mapping=mapping
    def __call__(self,endpoint,*,query=None,**kwargs):
        value=self.mapping[endpoint]
        if callable(value): value=value(query)
        return value,ok()

class EnrichmentTests(unittest.TestCase):
    def test_self_exemption_filtered(self):
        row=m.raw_and_third_party_exemptions(launch_tx([DEPLOYER,OTHER]),DEPLOYER)
        self.assertEqual(row["third_party"],[OTHER])

    def test_post_t0_discarded(self):
        fetch=Fetch({f"/api/v2/addresses/{DEPLOYER}/transactions":{
            "items":[
                {"timestamp":"2026-09-08T03:35:18Z","from":OTHER,"to":DEPLOYER,"value":"10"},
                {"timestamp":"2026-09-08T03:29:31Z","from":FUNDER,"to":DEPLOYER,"value":"10"},
            ],"next_page_params":None}})
        out=m.fetch_address_window(DEPLOYER,t0=m.parse_iso("2026-09-08T03:35:17Z"),fetch=fetch)
        self.assertEqual(len(out["rows"]),1)
        self.assertTrue(out["post_t0_rows_discarded"])

    def test_high_throughput_eoa_unknown_hub(self):
        fetch=Fetch({
            f"/api/v2/addresses/{FUNDER}":{"is_contract":False,"name":None,"metadata":None,"public_tags":[]},
            f"/api/v2/addresses/{FUNDER}/counters":{"transactions_count":"796947"},
        })
        self.assertEqual(m.classify_address(FUNDER,fetch=fetch)["class"],"UNKNOWN_HUB")

    def test_outcome_field_rejected(self):
        manifest={"contract":m.MANIFEST_CONTRACT,"events":[{"token_address":TOKEN,"future_return":3.0}]}
        with self.assertRaisesRegex(ValueError,"OUTCOME_FIELD_FORBIDDEN"):
            m.assert_outcome_blind_manifest(manifest)

    def test_no_cohort_is_deterministic_no_hit(self):
        block=57373399
        tx=launch_tx([])
        tx["token_transfers"]=[{"token":{"address_hash":TOKEN},"to":DEPLOYER}]
        fetch=Fetch({
            f"/api/v2/transactions/{TX}":tx,
            f"/api/v2/addresses/{DEPLOYER}/transactions":{
                "items":[
                    {"timestamp":"2026-09-08T03:35:07Z","from":DEPLOYER,"to":PAIR,"value":"0","method":"approve","hash":"0x1"},
                    {"timestamp":"2026-09-08T03:29:31Z","from":FUNDER,"to":DEPLOYER,"value":"10","hash":"0x2"},
                ],"next_page_params":None},
            f"/api/v2/blocks/{block}/transactions":{"items":[tx],"next_page_params":None},
            f"/api/v2/blocks/{block+1}/transactions":{"items":[],"next_page_params":None},
        })
        event={"token_address":TOKEN,"block_timestamp_utc":"2026-09-08T03:35:17Z","tx_hash":TX,
               "deployer_address":DEPLOYER,"pair_token_address":PAIR,"block_number":block}
        enriched=m.enrich_event(event,seed_addresses=set(),fetch=fetch)
        self.assertTrue(enriched["pre_t0_prep_observed"])
        self.assertFalse(enriched["privileged_bundle_evidence"])
        self.assertFalse(enriched["synchronized_inventory"])
        self.assertFalse(enriched["common_funding"])
        self.assertEqual(counting.classify_event(enriched)["classification"],"NO_HIT")

if __name__=="__main__":
    unittest.main()

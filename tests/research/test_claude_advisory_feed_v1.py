"""No Claude invocation and no fabricated original-owner runtime receipt."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[2] / "scripts/research/build_claude_advisory_feed_v1.py"
spec = importlib.util.spec_from_file_location("claude_advisory_feed", P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixtures(root: Path):
    meta = {
        "contract":"RESEARCH_META_ORCHESTRATOR_STATE_v1",
        "authority":"RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect":False,"portfolio_execution":False,
        "paid_data_authorized":False,"external_provider_calls_authorized":False,
        "binding_integrity":"PRIMARY_COMPLETE","sentinel_verdict":"PASS",
        "primary_action":"QUEUE_BOUNDED_RESEARCH",
        "primary_source":"SHADOW_REGISTRY",
        "primary_target":"CYCLE_NAVIGATOR_RESEARCH_FAMILY",
        "queue":[{"orchestrator_action":"QUEUE_BOUNDED_RESEARCH","source":"SHADOW_REGISTRY",
                  "target":"CYCLE_NAVIGATOR_RESEARCH_FAMILY","evidence_fingerprint":"a"*64}],
        "active_heavy_workstreams":[{"orchestrator_action":"QUEUE_BOUNDED_RESEARCH"}],
    }
    precision = {
        "contract":"CN_PRECISION_LEARNING_STATE_v1",
        "authority":"RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect":False,"portfolio_execution":False,
        "family_states":{
            "rotation":{"state":"PERSISTENT_WEAKNESS","valid_observations_4w":3,"mean_4w":50},
            "breadth":{"state":"NORMAL","valid_observations_4w":3,"mean_4w":100},
        },
        "checkpoint_sequence":2,"last_settled_score_key":"Y2026-W45-CN33",
    }
    learning = {
        "contract":"NEXT_BEST_EXPERIMENT_PROPOSAL_v1",
        "authority":"RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect":False,"portfolio_execution":False,
        "automatic_execution":False,"automatic_promotion":False,
        "proposal_status":"NO_NEW_SCIENTIFICALLY_ELIGIBLE_CHILD_TEST",
    }
    for name, obj in (("meta",meta),("precision",precision),("compounding",learning)):
        path = root / m.SOURCES[name]
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(obj))
    return meta, precision, learning


class FeedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.meta,self.precision,self.learning = fixtures(self.root)

    def replace(self, name, value):
        (self.root/m.SOURCES[name]).write_text(json.dumps(value))

    def test_safe_source_pinned_candidates_and_no_native_receipt(self):
        first=m.build(self.root, head="a"*40)
        again=m.build(self.root, head="b"*40)
        self.assertEqual(first["semantic_fingerprint"],again["semantic_fingerprint"])
        self.assertEqual(first["candidate_count"],2)
        self.assertFalse(first["claude_invoked"])
        self.assertFalse(first["automatic_execution"])
        self.assertFalse(first["automatic_paid_dispatch"])
        self.assertEqual(first["candidates"][0]["native_action_run_id"],None)
        self.assertEqual(first["candidates"][0]["execution_proof_in_current_state"],"NOT_OBSERVED_IN_SOURCE")
        self.assertEqual(first["candidates"][1]["weak_families"][0]["family"],"rotation")
        self.assertEqual(set(first["source_receipts"]),set(m.SOURCES))
        self.assertEqual(first["current_learning_proposal"],"NO_NEW_SCIENTIFICALLY_ELIGIBLE_CHILD_TEST")
        self.assertEqual(first["source_checkout_sha"],"a"*40)

    def test_no_fabrication_when_nothing_actionable(self):
        self.meta["primary_action"]="WAIT_FOR_EVIDENCE"
        self.precision["family_states"]["rotation"]["state"]="NORMAL"
        self.replace("meta",self.meta)
        self.replace("precision",self.precision)
        f=m.build(self.root,head=None)
        self.assertEqual(f["candidate_count"],0)
        self.assertFalse(f["claude_invoked"])

    def test_fail_closed_missing_tampered_and_authority(self):
        (self.root/m.SOURCES["precision"]).unlink()
        with self.assertRaises(m.SourceFailure):
            m.build(self.root)
        self.replace("precision",self.precision)
        self.meta["sentinel_verdict"]="BLOCK_RESEARCH_ESCALATION"
        self.replace("meta",self.meta)
        with self.assertRaisesRegex(m.SourceFailure,"SENTINEL"):
            m.build(self.root)
        self.meta["sentinel_verdict"]="PASS"
        self.meta["canonical_effect"]=True
        self.replace("meta",self.meta)
        with self.assertRaisesRegex(m.SourceFailure,"AUTHORITY_ELEVATION"):
            m.build(self.root)

    def test_reject_mismatched_fingerprint_and_queue(self):
        self.meta["queue"]=[]
        self.replace("meta",self.meta)
        with self.assertRaisesRegex(m.SourceFailure,"PRIMARY_QUEUE_ITEM_UNVERIFIED"):
            m.build(self.root)
        self.meta["queue"]=[{"orchestrator_action":"QUEUE_BOUNDED_RESEARCH","source":"SHADOW_REGISTRY",
                             "target":"CYCLE_NAVIGATOR_RESEARCH_FAMILY","evidence_fingerprint":"notsha"}]
        self.replace("meta",self.meta)
        with self.assertRaisesRegex(m.SourceFailure,"PRIMARY_SOURCE_FINGERPRINT_UNVERIFIED"):
            m.build(self.root)

    def test_existing_script_no_side_effect_on_dry_run_and_stable_digest(self):
        p=self.root/m.OUTPUT
        a=m.build(self.root,head=None)
        b=m.build(self.root,head=None)
        self.assertEqual(a["semantic_fingerprint"],b["semantic_fingerprint"])
        self.assertFalse(p.exists())
        self.precision["checkpoint_sequence"]=3
        self.replace("precision",self.precision)
        changed=m.build(self.root,head=None)
        self.assertNotEqual(a["semantic_fingerprint"],changed["semantic_fingerprint"])


if __name__=="__main__":
    unittest.main()

import copy
import json
import unittest
from datetime import timedelta
from pathlib import Path
import tempfile
from unittest.mock import patch
from scripts.research import cn_mm_core_shadow_bridge_v1 as bridge
from scripts.research.cn_mm_core_shadow_bridge_v1 import CORE, evaluate_rows, read_rows

START = "2026-11-16T00:00:00Z"
END = "2026-11-23T00:00:00Z"
FLOOR = "2026-10-24T12:00:00Z"
MUTABLE = {"outcome_24h", "outcome_72h", "outcome_7d", "mae_24h", "mfe_24h"}


def row(hour, e, b, d):
    states = (e, b, d, e and b, e and d, b and d, e and b and d)
    return {"event_id": f"PSR_20261122T{hour:02d}0000Z",
            "observation_timestamp_utc": f"2026-11-22T{hour:02d}:00:00Z",
            "information_cutoff_utc": f"2026-11-22T{hour:02d}:00:00Z",
            "row_integrity_contract": "SHARED_ROW_P0_BINDING_v1",
            "source_version_commit": "a"*40, "provenance_hash": "b"*64,
            "source_binding_manifest": "{}", "candidate_decisions": json.dumps(dict(zip(CORE, states))),
            "outcome_24h": "1", "mae_24h": "-5"}


class CoreBridge(unittest.TestCase):
    def replay(self, rows, verify=None):
        def check(projection, at, decisions):
            self.assertFalse(MUTABLE.intersection(projection))
            if verify:
                verify(projection, at, decisions)
        return evaluate_rows(rows, START, END, FLOOR, check, MUTABLE)

    def test_reuse_candidate_and_pivotal_family(self):
        result = self.replay([row(12, True, False, True)])
        self.assertEqual(result["status"], "CORE_REPLAY_AT_OBSERVATION_ONLY")
        self.assertFalse(result["latest_observation"]["decisions"]["C07_SIMPLE_3"])
        self.assertTrue(result["attribution"]["BREADTH_SURVIVAL"]["pivotal_in_frozen_and_rule"])
        self.assertFalse(result["attribution"]["ETHBTC_PERSISTENCE"]["pivotal_in_frozen_and_rule"])
        changed = self.replay([row(12, True, True, True)])
        self.assertTrue(changed["latest_observation"]["decisions"]["C07_SIMPLE_3"])
        self.assertFalse(changed["attribution"]["BREADTH_SURVIVAL"]["pivotal_in_frozen_and_rule"])

    def test_outcomes_cannot_affect_projection(self):
        rows = [row(12, True, False, True)]
        before = self.replay(rows)
        rows[0].update(outcome_24h="0", mae_24h="999999", outcome_7d="1")
        self.assertEqual(before, self.replay(rows))

    def test_ordered_intervals_are_not_original_sequence_equivalence(self):
        rows = [row(0, False, False, False), row(1, True, False, False),
                row(2, True, False, True), row(3, True, True, True)]
        result = self.replay(list(reversed(rows)))["transition_diagnostic"]
        self.assertEqual(result["status"], "ORDERED_OBSERVATION_INTERVALS")
        self.assertFalse(result["original_sequence_equivalence"])
        self.assertFalse(result["event_time_certified"])
        same_interval = self.replay([rows[0], rows[-1]])["transition_diagnostic"]
        self.assertEqual(same_interval["status"], "ORDER_NOT_ESTABLISHED")

    def test_rejected_latest_row_has_no_fallback(self):
        def reject(projection, at, decisions):
            if projection["event_id"].endswith("120000Z"):
                raise ValueError("SOURCE_BINDING_FAILED")
        result = self.replay([row(11, True, True, True), row(12, False, False, False)], reject)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertIsNone(result["latest_observation"])

    def test_wrong_cutoff_duplicate_and_future(self):
        a = row(12, True, True, True)
        self.assertEqual(self.replay([a, copy.deepcopy(a)])["status"], "UNKNOWN")
        altered = copy.deepcopy(a)
        altered["information_cutoff_utc"] = END
        self.assertEqual(self.replay([altered])["status"], "UNKNOWN")
        future = copy.deepcopy(a)
        future["observation_timestamp_utc"] = END
        self.assertEqual(self.replay([a, future]), self.replay([a]))

    def test_ambiguous_candidate_json_and_csv_rejected(self):
        a = row(12, True, True, True)
        a["candidate_decisions"] = '{"C01_ETHBTC":true,"C01_ETHBTC":false}'
        self.assertEqual(self.replay([a])["status"], "UNKNOWN")
        for raw in (b"x,x\n1,2\n", b"x,y\n1\n", b"x,y\n1,2,3\n"):
            with self.assertRaises(ValueError):
                read_rows(raw)

    def test_no_observations(self):
        self.assertEqual(self.replay([])["reason"], "NO_ELIGIBLE_OBSERVATIONS")


def _real_w47_owner_replay(self):
    owner = bridge.load_owner()
    raw = (bridge.ROOT / bridge.LEDGER).read_bytes()
    rows = [r for r in read_rows(raw) if r["event_id"] == "PSR_20261122T224954Z"]
    self.assertEqual(len(rows), 1)
    at = bridge.clock(rows[0]["observation_timestamp_utc"])
    eligible = set(owner.eligible_candidates())
    self.assertTrue(set(CORE).issubset(eligible))

    def verify(row, cutoff, decisions):
        owner.verify_frozen_provenance(row)
        owner.validate_core_decision_contract(row, decisions, eligible)
        owner.verify_source_bindings(row, cutoff)

    args = (bridge.iso(at), bridge.iso(at + timedelta(seconds=1)), FLOOR,
            verify, owner.PROVENANCE_MUTABLE_FIELDS)
    # Direct call exposes the underlying verifier error instead of only UNKNOWN.
    projection = {k: v for k, v in rows[0].items() if k not in owner.PROVENANCE_MUTABLE_FIELDS}
    verify(projection, at, json.loads(projection["candidate_decisions"]))
    result = evaluate_rows(rows, *args)
    self.assertEqual(result["status"], "CORE_REPLAY_AT_OBSERVATION_ONLY")
    self.assertFalse(result["latest_observation"]["decisions"]["C07_SIMPLE_3"])
    self.assertTrue(result["attribution"]["ETHBTC_PERSISTENCE"]["pivotal_in_frozen_and_rule"])
    altered = copy.deepcopy(rows)
    altered[0]["source_version_commit"] = "0" * 40
    self.assertEqual(evaluate_rows(altered, *args)["status"], "UNKNOWN")
    altered = copy.deepcopy(rows)
    altered[0]["outcome_24h"] = "1" if rows[0]["outcome_24h"] == "0" else "0"
    self.assertEqual(evaluate_rows(altered, *args), result)
    head = bridge.git("rev-parse", "HEAD").decode().strip()
    pinned = owner.PinnedSourceReplay(bridge.ROOT, head)
    freeze = {"window_start_utc": bridge.iso(at),
              "window_end_utc": bridge.iso(at + timedelta(seconds=1)),
              "created_at_utc": bridge.iso(at + timedelta(seconds=2))}
    packet = {"checkout_sha": head, "ledger_sha256": bridge.sha(raw), "core": result}
    diag = bridge.verify_packet_projection(packet, freeze, raw, pinned.registry_raw, repo=bridge.ROOT)
    self.assertEqual(diag["persistence"]["side"], rows[0]["ethbtc_derived_state"])
    self.assertFalse(diag["persistence"]["scientific_pit_eligible"])
    self.assertIsNone(diag["persistence"]["stable_confirmation_utc"])
    self.assertEqual(diag["sequence"]["observation_n"], 1)
    self.assertFalse(diag["sequence"]["forecast_authority"])
    self.assertFalse(diag["forensics_context"]["forecast_authority"])
    self.assertIsNone(diag["forensics_context"]["liquidation_clearance"])
    self.assertFalse(diag["leverage_context"]["forecast_authority"])
    self.assertIsNone(diag["leverage_context"]["reset_state"])
    self.assertIn(diag["leverage_context"]["status"],{"ARCHIVED_DECLARED_CLOCK_CONTEXT_ONLY","UNAVAILABLE"})
    shared = bridge.intelligence_projection(packet,diag)
    self.assertEqual(shared["models"]["C2"]["observed_c06_permission"],result["latest_observation"]["decisions"]["C06_BREADTH_BTCD"])
    self.assertFalse(shared["models"]["C2"]["issued"])
    self.assertFalse(shared["forecast_authority"])
    self.assertNotIn("learning",shared)
    self.assertNotIn("outcome",shared)
    digest = shared.pop("feature_sha256")
    self.assertEqual(digest,bridge.sha(bridge.canon(shared)))
    forged = copy.deepcopy(packet)
    forged["core"]["latest_observation"]["decisions"]["C07_SIMPLE_3"] = True
    with self.assertRaisesRegex(ValueError, "SHADOW_PROJECTION_MISMATCH"):
        bridge.verify_packet_projection(forged, freeze, raw, pinned.registry_raw, repo=bridge.ROOT)



class ExistingOwnerReplay(unittest.TestCase):
    def test_real_w47_row_uses_existing_byte_replay_and_frozen_candidates(self):
        # The repository-wide suite imports and mutates owner modules in many
        # fixtures. Exercise the real production CLI's fresh-process context,
        # without skipping, mocking or weakening any of the source verifiers.
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, "-c",
             "import runpy, unittest; "
             "ns=runpy.run_path('tests/cycle_navigator/test_cn_mm_core_shadow_bridge_v1.py'); "
             "ns['_real_w47_owner_replay'](unittest.TestCase())"],
            cwd=bridge.ROOT, capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_optional_source_coverage_on_original_admitted_cohort(self):
        import subprocess
        import sys
        # Existing native test job executes against full Git history. No new collector.
        code = """
import json
from scripts.research import cn_mm_core_shadow_bridge_v1 as b
from scripts.research.cn_mm_optional_source_context_v1 import coverage, leverage_context
from collections import Counter
owner=b.load_owner()
head=b.git('rev-parse','HEAD').decode().strip()
replay=owner.PinnedSourceReplay(b.ROOT,head)
rows=b.read_rows(replay.ledger_raw)
observations=[]
leverage_status=Counter()
leverage_fields=Counter()
for row in rows:
    at=b.clock(row['observation_timestamp_utc'])
    if at < replay.floor:
        continue
    replay.verify(row,at,json.loads(row['candidate_decisions']))
    observations.append({'observation_utc':b.iso(at),'source_commit':row['source_version_commit']})
    lev=leverage_context(replay,row,at)
    leverage_status[lev['status']]+=1
    assert lev['reset_state'] is None and lev['reclaim_state'] is None
    for asset,v in lev['assets'].items():
        assert v['open_interest_contracts'] is None and v['oi_change_24h_pct'] is None
        assert v['notional_change_is_contract_deleveraging'] is False
        if v['funding_event_rate'] is None:
            assert v['funding_event_observation_utc'] is None
        for field in ('open_interest_owner_amount','open_interest_owner_declared_usd_notional','oi_owner_declared_usd_notional_change_24h_pct','long_short_account_ratio','funding_event_rate'):
            if v[field] is not None:
                leverage_fields[asset+':'+field]+=1
result=coverage(replay,observations)
result['leverage_status_counts']=dict(leverage_status)
result['leverage_field_counts']=dict(leverage_fields)
assert leverage_status['ARCHIVED_DECLARED_CLOCK_CONTEXT_ONLY']>0,result
assert sum(leverage_status.values())==len(observations)
assert result['observation_n']==len(observations)>0
assert sum(result['etf_status_counts'].values())==len(observations)
assert sum(result['liquidation_status_counts'].values())==len(observations)
assert result['scientific_pit_eligible'] is False and result['forecast_authority'] is False
print('OPTIONAL_SOURCE_COHORT '+json.dumps(result,sort_keys=True))
"""
        result = subprocess.run([sys.executable, "-c", code], cwd=bridge.ROOT,
                                capture_output=True, text=True, timeout=180)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        print(result.stdout)

    def test_original_matured_outcome_source_replay(self):
        import subprocess
        import sys
        code = """
import json
from scripts.research import cn_mm_core_shadow_bridge_v1 as b
from scripts.research.cn_mm_outcome_source_audit_v1 import audit_outcome_cohort
owner=b.load_owner()
head=b.git('rev-parse','HEAD').decode().strip()
replay=owner.PinnedSourceReplay(b.ROOT,head)
report=audit_outcome_cohort(replay,evaluate=True)
research=report.pop('matched_research')
print('PINNED_OUTCOME_COHORT '+json.dumps(report,sort_keys=True))
if report['status']=='REPLAY_COMPLETE':
    assert research['status']=='DESCRIPTIVE_ONLY_NOT_INDEPENDENT_EDGE',research
    assert not research['forecast_authority'] and not research['edge_established']
    for h,panel in research['core_ablation']['horizons'].items():
        assert panel['matched_matured_n']==report['verified_horizon_counts'].get(h,0)
    compact={k:v for k,v in research.items() if k!='core_ablation'}
    compact['horizons']=research['core_ablation']['horizons']
    assert not research['veto_magnitude']['forecast_authority']
    print('PINNED_MATCHED_RESEARCH '+json.dumps(compact,sort_keys=True))
else:
    assert research['status']=='BLOCKED_OUTCOME_SOURCE_REPLAY'
assert report['verified_n']>0,report
assert report['verified_n']+report['rejected_n']+report['unmatured_or_unavailable_n']==3*report['parent_n'],report
assert not report['scientific_pit_eligible'] and not report['outcomes_used_as_features']
# Rejections are explicit research blockers, never silently scored or rewritten.
assert report['status'] in {'REPLAY_COMPLETE','REPLAY_BLOCKED'}
"""
        result = subprocess.run([sys.executable, "-c", code], cwd=bridge.ROOT,
                                capture_output=True, text=True, timeout=240)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        print(result.stdout)

    def test_task2_original_w47_comparator_readback(self):
        import subprocess
        import sys
        code = """
import json
from scripts.research import cn_mm_core_shadow_bridge_v1 as b
from scripts.research.cn_mm_task2_comparator_readback_v1 import audit_week
replay=b.load_owner().PinnedSourceReplay(b.ROOT,b.git('rev-parse','HEAD').decode().strip())
report=audit_week(replay,2026,47)
assert report['paired_n']==report['point_comparison']['all']['n']>0
assert not report['scientific_pit_eligible'] and not report['forecast_authority']
report['point_comparison'].pop('rows')
print('TASK2_ORIGINAL_COMPARATOR '+json.dumps(report,sort_keys=True))
"""
        result = subprocess.run([sys.executable, "-c", code], cwd=bridge.ROOT,
                                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        print(result.stdout)

    def test_c2_fixture_model_is_nonactivating(self):
        import subprocess
        import sys
        result = subprocess.run([sys.executable, "-m", "unittest",
            "tests.research.test_cn_mm_c2_relative_tilt_fixture_v1"], cwd=bridge.ROOT,
            capture_output=True,text=True,timeout=60)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_shared_intelligence_unknown_never_promotes(self):
        result=bridge.intelligence_projection({"core":bridge.unknown("missing")})
        self.assertEqual(result["status"],"UNKNOWN")
        self.assertIsNone(result["models"]["C2"]["observed_c06_permission"])
        self.assertFalse(result["models"]["C2"]["issued"])
        self.assertEqual(result["families"],{})
        self.assertFalse(result["forecast_authority"])

    def test_calibration_and_cn_share_projection_and_separate_learning(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as root:
            result=bridge.calibration_intelligence(Path(root),Path(root)/"missing.json",{})
            self.assertEqual(result["status"],"UNAVAILABLE")
            self.assertFalse(result["feature_uses_outcomes"])
            self.assertEqual(result["learning"]["status"],"UNAVAILABLE")
        context=(bridge.ROOT/"scripts/api_agent/build_weekly_calibration_context.py").read_text()
        self.assertIn('context["cn_mm_shared_intelligence"] = calibration_intelligence',context)
        self.assertLess(context.index('context["cn_mm_shared_intelligence"] ='),context.index('context["context_hash"] ='))
        self.assertIn('shared = intelligence_projection(packet,diagnostics)',(bridge.ROOT/"scripts/research/cn_mm_core_shadow_bridge_v1.py").read_text())
        self.assertIn("calibration_feature_binding(context,freeze)",(bridge.ROOT/"scripts/master_monday/publish_master_monday_outputs.py").read_text())

    def test_common_feature_receipt_requires_exact_independent_projection(self):
        packet={"core":bridge.unknown("missing"),"freeze_sha256":"a"*64,
                "checkout_sha":"b"*40,"packet_sha256":"c"*64}
        feature=bridge.intelligence_projection(packet)
        intelligence={"status":"SHADOW_CONTEXT_ONLY","feature":feature,"freeze_sha256":packet["freeze_sha256"],
                      "checkout_sha":packet["checkout_sha"],"feature_uses_outcomes":False}
        intelligence["context_sha256"]=bridge.sha(bridge.canon(intelligence))
        context={"cn_mm_shared_intelligence":intelligence}
        context["context_hash"]=bridge.sha(bridge.canon(context))
        binding=bridge.calibration_feature_binding(context,packet)
        self.assertEqual(binding["status"],"BOUND_CALIBRATION_FEATURE")
        machine={"freeze_sha256":packet["freeze_sha256"],"context_hash":context["context_hash"],
                 "cn_mm_calibration_feature_binding":binding}
        machine["package_sha256"]=bridge.sha(bridge.canon(machine))
        pointer={"freeze_sha256":packet["freeze_sha256"],"machine_package_sha256":machine["package_sha256"]}
        self.assertEqual(bridge.compare_calibration_feature(machine,pointer,feature),"MATCHED_MM_CALIBRATION_FEATURE")
        forged=copy.deepcopy(feature)
        forged["models"]["C2"]["observed_c06_permission"]=True
        forged.pop("feature_sha256")
        forged["feature_sha256"]=bridge.sha(bridge.canon(forged))
        self.assertEqual(bridge.compare_calibration_feature(machine,pointer,forged),"MM_CALIBRATION_FEATURE_MISMATCH")
        self.assertEqual(bridge.compare_calibration_feature({},pointer,feature),"UNATTESTED_MM_CALIBRATION_BINDING")
        context["cn_mm_shared_intelligence"]["feature"]["forecast_authority"]=True
        self.assertEqual(bridge.calibration_feature_binding(context,packet)["status"],"UNAVAILABLE")

    def test_learning_snapshot_is_original_cutoff_tree_not_current_ledger(self):
        import os
        import subprocess
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            def git(*args,stamp=None):
                env=dict(os.environ)
                if stamp:
                    env.update(GIT_AUTHOR_DATE=stamp,GIT_COMMITTER_DATE=stamp)
                return subprocess.check_output(["git","-C",directory,*args],env=env,
                    stderr=subprocess.DEVNULL).decode().strip()
            git("init","-q")
            git("config","user.name","Fixture")
            git("config","user.email","fixture@example.invalid")
            ledger=root/"ledger.csv"
            ledger.write_text("original")
            git("add",".")
            git("commit","-qm","original",stamp="2026-11-23T09:00:00Z")
            first=git("rev-parse","HEAD")
            ledger.write_text("late outcome")
            git("add",".")
            git("commit","-qm","late",stamp="2026-11-23T10:00:00Z")
            head=git("rev-parse","HEAD")
            cutoff=bridge.clock("2026-11-23T09:42:55Z")
            pin=bridge.learning_checkout_at_cutoff(root,head,cutoff)
            self.assertEqual(pin["checkout_sha"],first)
            self.assertEqual(git("show",pin["checkout_sha"]+":ledger.csv"),"original")
            self.assertIn("NOT_INDEPENDENT_KNOWN_BY",pin["clock_class"])
            self.assertEqual(bridge.learning_checkout_at_cutoff(root,head,
                bridge.clock("2026-11-23T10:00:00Z"))["checkout_sha"],head)
            with self.assertRaisesRegex(ValueError,"NO_CHECKOUT"):
                bridge.learning_checkout_at_cutoff(root,head,bridge.clock("2026-11-23T08:00:00Z"))
            ledger.write_text("inverted")
            git("add",".")
            git("commit","-qm","inverted",stamp="2026-11-23T09:30:00Z")
            with self.assertRaisesRegex(ValueError,"CLOCK_INVERSION"):
                bridge.learning_checkout_at_cutoff(root,git("rev-parse","HEAD"),
                    bridge.clock("2026-11-23T09:42:55Z"))

    def test_real_w47_calibration_learning_uses_historical_snapshot(self):
        import subprocess
        import sys
        code = """
import json
from scripts.research import cn_mm_core_shadow_bridge_v1 as b
head=b.git('rev-parse','HEAD').decode().strip()
path='research/master_monday_preflight/frozen/2026/W47/WEEKLY_EVIDENCE_FREEZE.json'
freeze=json.loads(b.git('show',head+':'+path))
result=b.calibration_learning_at_cutoff(b.ROOT,head,freeze)
pin=result['learning_source_snapshot']
assert pin['checkout_sha']!=head
assert b.clock(pin['checkout_committer_utc'])<=b.clock(freeze['created_at_utc'])
assert result['learning']['status']=='DESCRIPTIVE_ONLY_NOT_INDEPENDENT_EDGE',result
assert result['learning']['source_checkout_sha']==pin['checkout_sha']
assert result['learning']['verified_n']>0 and result['learning']['rejected_n']==0
assert set(('cce','odm','sre','fae'))<=set(result['learning']['meta_learning'])
assert not result['learning']['meta_learning']['automatic_weight_updates']
assert result['task2']['paired_n']==14 and not result['task2']['scientific_pit_eligible']
print('W47_ORIGINAL_CALIBRATION_READBACK '+json.dumps({'pin':pin,'verified_n':result['learning']['verified_n'],'horizons':result['learning']['verified_horizon_counts'],'task2_paired_n':result['task2']['paired_n'],'incremental_inventory':result['incremental_inventory']},sort_keys=True))
"""
        result=subprocess.run([sys.executable,"-c",code],cwd=bridge.ROOT,
                              capture_output=True,text=True,timeout=180)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        print(result.stdout)

    def test_outcome_cache_is_scoped_and_digest_sensitive(self):
        import hashlib
        from scripts.research.cn_mm_outcome_source_audit_v1 import OutcomePathReadCache
        class Replay:
            def __init__(self): self.calls=0
            def read_blob(self,commit,path): self.calls+=1; return b"fixture"
        replay=Replay()
        cache=OutcomePathReadCache(replay,max_entries=1)
        manifest=[{"path":"p","sha256":hashlib.sha256(b"fixture").hexdigest(),"bytes":7}]
        parse=lambda rows: rows
        unique=lambda rows: tuple(rows)
        self.assertEqual(cache.records("a",manifest,parse,unique),cache.records("a",manifest,parse,unique))
        self.assertEqual(replay.calls,1)
        self.assertEqual(cache.hits,1)
        cache.records("b",manifest,parse,unique)
        self.assertEqual(replay.calls,2)
        with self.assertRaisesRegex(ValueError,"SOURCE_BYTES_MISMATCH"):
            cache.records("b",[{**manifest[0],"sha256":"0"*64}],parse,unique)
        self.assertEqual(replay.calls,3)

    def test_leverage_missing_source_never_becomes_reset(self):
        from scripts.research.cn_mm_optional_source_context_v1 import leverage_context
        class Replay:
            def require_ancestor(self,commit): raise ValueError("unavailable")
        result=leverage_context(Replay(),{"source_version_commit":"0"*40},bridge.clock(START))
        self.assertEqual(result["status"],"UNAVAILABLE")
        self.assertIsNone(result["reset_state"])
        self.assertIsNone(result["reclaim_state"])
        self.assertFalse(result["forecast_authority"])

    def test_incremental_inventory_detects_new_maturity_and_frozen_rewrites(self):
        from scripts.research.cn_mm_outcome_source_audit_v1 import immutable_delta_inventory
        old={"event_id":"A","source":"x","outcome_24h":""}
        matured={**old,"outcome_24h":"1"}
        detail={"event_id":"A","horizon":"24h","digest":"x"}
        new={"event_id":"B","source":"y","outcome_24h":""}
        m={"outcome_24h"}
        report=immutable_delta_inventory([old],[],[matured,new],[detail],m)
        self.assertEqual(report["status"],"APPEND_ONLY_DELTA_IDENTIFIED")
        self.assertEqual(report["new_parent_ids"],["B"])
        self.assertEqual(report["new_matured_prior_parent_n"],1)
        self.assertFalse(report["prior_verdict_reuse_authorized"])
        for rows,details in (([{**matured,"source":"changed"},new],[detail]),
                             ([{**matured,"outcome_24h":"0"},new],[detail]),
                             ([matured,new],[{**detail,"digest":"changed"}]),
                             ([matured,new],[]),([new],[detail])):
            report=immutable_delta_inventory([matured],[detail],rows,details,m)
            self.assertEqual(report["status"],"REVIEW_FULL_REPLAY_REQUIRED")
        with self.assertRaisesRegex(ValueError,"DUPLICATE_IDENTITY"):
            immutable_delta_inventory([old],[],[old,old],[],m)

    def test_real_incremental_replay_matches_full_original_w47(self):
        import subprocess
        import sys
        code = """
import json
from scripts.research import cn_mm_core_shadow_bridge_v1 as b
from scripts.research.cn_mm_outcome_source_audit_v1 import replay_incremental_pair,audit_outcome_cohort
owner=b.load_owner()
head=b.git('rev-parse','HEAD').decode().strip()
def original(week):
    path='research/master_monday_preflight/frozen/2026/W'+str(week)+'/WEEKLY_EVIDENCE_FREEZE.json'
    freeze=json.loads(b.git('show',head+':'+path))
    pin=b.learning_checkout_at_cutoff(b.ROOT,head,b.clock(freeze['created_at_utc']))
    return owner.PinnedSourceReplay(b.ROOT,pin['checkout_sha'])
before,after=original(46),original(47)
result=replay_incremental_pair(before,after)
full=audit_outcome_cohort(after,evaluate=True)
incremental=result.pop('current')
for x in (full,incremental): x.pop('path_read_cache')
assert incremental==full,'INCREMENTAL_FULL_REPLAY_NOT_EQUAL'
assert result['reused_feature_n']==59 and result['reused_outcome_n']==145,result
assert result['new_feature_replay_n']==18 and result['new_outcome_replay_n']==54,result
assert result['durable_verdict_reuse_authorized'] is False
result['full_replay_equivalent']=True
print('W47_INCREMENTAL_EQUIVALENCE '+json.dumps(result,sort_keys=True))
"""
        result=subprocess.run([sys.executable,"-c",code],cwd=bridge.ROOT,
                              capture_output=True,text=True,timeout=240)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        print(result.stdout)

    def test_learning_gateway_input_receipt_is_not_model_use(self):
        packet={"core":bridge.unknown("missing"),"freeze_sha256":"a"*64,
                "checkout_sha":"b"*40,"packet_sha256":"c"*64}
        feature=bridge.intelligence_projection(packet)
        intelligence={"status":"SHADOW_CONTEXT_ONLY","feature":feature,"freeze_sha256":packet["freeze_sha256"],
                      "checkout_sha":packet["checkout_sha"],"feature_uses_outcomes":False,
                      "learning":{"status":"DESCRIPTIVE_ONLY_NOT_INDEPENDENT_EDGE","verified_n":199},
                      "task2":{"status":"SOURCE_REPLAYED_DESCRIPTIVE_ONLY","paired_n":14}}
        intelligence["context_sha256"]=bridge.sha(bridge.canon(intelligence))
        context={"cn_mm_shared_intelligence":intelligence}
        context["context_hash"]=bridge.sha(bridge.canon(context))
        receipt={"contract":"API_AGENT_RECEIPT_v3","task":"WEEKLY_CALIBRATION_SHADOW",
                 "context_hash":bridge.sha(bridge.canon(context)),"status":"PASS","response_id":"fixture",
                 "untrusted_input_envelope":True}
        good=bridge.calibration_learning_binding(context,packet,receipt,"success")
        self.assertEqual(good["api_input_status"],"MATCHED_GATEWAY_INPUT_RECEIPT")
        self.assertEqual(good["verified_outcome_n"],199)
        self.assertFalse(good["model_utilization_verified"])
        self.assertFalse(good["forecast_authority"])
        for bad in ({**receipt,"context_hash":context["context_hash"]},{**receipt,"task":"OTHER"}):
            self.assertEqual(bridge.calibration_learning_binding(context,packet,bad,"success")["api_input_status"],"RECEIPT_CONTEXT_MISMATCH")
        self.assertEqual(bridge.calibration_learning_binding(context,packet,receipt,"failure")["api_input_status"],"MATCHED_CONTEXT_NO_SUCCESSFUL_API_DELIVERY")
        self.assertEqual(bridge.calibration_learning_binding(context,packet,{},"failure")["api_input_status"],"UNATTESTED")
        context["cn_mm_shared_intelligence"]["learning"]["verified_n"]=999
        self.assertEqual(bridge.calibration_learning_binding(context,packet,receipt,"success")["status"],"UNAVAILABLE")

    def test_mm_translation_readback_rejects_malformed_or_authoritative_shadow_rows(self):
        from copy import deepcopy
        digest="a"*64;ctx="b"*64;out="c"*64
        t={"contract":"MM_SHADOW_ANALYTICAL_TRANSLATION_v1","status":"DEGRADED",
           "authority":"SHADOW_ONLY_NO_ACTION_OR_FORECAST_AUTHORITY","candidate_status":"VALIDATED_UNADMITTED",
           "phase":"UNAVAILABLE","rotation":"UNAVAILABLE","forecast_authority":False,"portfolio_action":False,
           "model_weight_change":False,"model_utilization_verified":False,
           "context_sha256":ctx,"freeze_sha256":digest,"gateway_context_sha256":ctx,"gateway_output_sha256":out,
           "candidate_count":1,"candidate_horizon_counts":{"7":1},"candidate_direction_counts":{"UP":1},
           "spot_candidate_directions":[{"asset":"BTC","horizon_days":7,"direction":"UP","target_mode":"PCT_MOVE"}]}
        machine={"operational_translation":t,"context_hash":ctx,"freeze_sha256":digest,"api_status":"success",
                 "api_receipt":{"contract":"API_AGENT_RECEIPT_v3","task":"WEEKLY_CALIBRATION_SHADOW",
                                "status":"PASS","response_id":"fixture","untrusted_input_envelope":True,
                                "context_hash":ctx,"output_hash":out,"forecast_candidate_count":1}}
        pointer={"freeze_sha256":digest}
        result=bridge.mm_translation_readback(machine,pointer)
        self.assertEqual(result["spot_candidate_directions"],t["spot_candidate_directions"])
        self.assertFalse(result["independent_model_output_replay"])
        self.assertFalse(result["forecast_authority"])
        for mutate in (
            lambda x:x.update(forecast_authority=True),
            lambda x:x.update(gateway_output_sha256="d"*64),
            lambda x:x.update(candidate_direction_counts={"DOWN":1}),
            lambda x:x.update(candidate_horizon_counts={"14":1}),
            lambda x:x["spot_candidate_directions"][0].update(asset="MEME"),
            lambda x:x["spot_candidate_directions"][0].update(horizon_days=True),
            lambda x:x["spot_candidate_directions"][0].update(target_mode="ABSOLUTE_RANGE"),
            lambda x:x["spot_candidate_directions"][0].update(target_value=123),
        ):
            altered=deepcopy(machine);mutate(altered["operational_translation"])
            self.assertIsNone(bridge.mm_translation_readback(altered,pointer))
        self.assertIsNone(bridge.mm_translation_readback(machine,{"freeze_sha256":"e"*64}))

    def test_real_historical_w47_context_and_gateway_preserve_unknown_feature(self):
        # Real existing context CLI and gateway request construction.
        # Synthetic receipt only; no paid request or historical output write.
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/"context.json"
            result=subprocess.run([sys.executable,"scripts/api_agent/build_weekly_calibration_context.py",
                 "--weekly-pointer","03_DAILY_CAPTURE_LOGS/weekly/LATEST_WEEKLY_CALIBRATION.json",
                 "--daily-output-root","research/api_agent/outputs/daily",
                 "--freeze-file","research/master_monday_preflight/frozen/2026/W47/WEEKLY_EVIDENCE_FREEZE.json",
                 "--legacy-root","04_MARKET_LEARNING/legacy_framework_knowledge_bootstrap_v1",
                 "--experiment-registry","research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json",
                 "--experiment-outcome-root","research/framework_memory/outcome_memory",
                 "--output",str(output)],cwd=bridge.ROOT,capture_output=True,text=True,timeout=240)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            code = """
import json,sys
from pathlib import Path
from scripts.research import cn_mm_core_shadow_bridge_v1 as b
from scripts.api_agent.api_gateway import build_request,canonical_bytes,sha256_bytes
context=json.loads(Path(sys.argv[1]).read_text())
freeze_file=Path('research/master_monday_preflight/frozen/2026/W47/WEEKLY_EVIDENCE_FREEZE.json')
freeze=json.loads(freeze_file.read_text())
head=b.git('rev-parse','HEAD').decode().strip()
intel=context['cn_mm_shared_intelligence']
assert intel['status']=='SHADOW_CONTEXT_ONLY',intel
assert intel['learning']['verified_n']==199
assert intel['task2']['paired_n']==14
assert intel['incremental_inventory']['identity_counts']['new_receipt_keys']==54
assert 'new_receipt_keys' not in intel['incremental_inventory']
assert set(('cce','odm','sre','fae'))<=set(intel['learning']['meta_learning'])
packet=b.build_checkout(freeze_file,head)
# W47 is an authentic historical freeze, NOT a newly bound producer fixture.
from scripts.master_monday.weekly_source_binding_v1 import verify_sidecar
original_pointer=json.loads(b.git('show','ec36550041fe48b2976c06733dc4bad093b9eed5:03_DAILY_CAPTURE_LOGS/weekly/LATEST_WEEKLY_CALIBRATION.json'))
verified=verify_sidecar(freeze_file.parent,freeze,original_pointer,Path('03_DAILY_CAPTURE_LOGS'),freeze['freeze_sha256'])
assert verified['status']=='UNKNOWN' and verified['reason']=='SOURCE_BINDING_MISSING',verified
assert not (freeze_file.parent/'SOURCE_BINDINGS'/(freeze['freeze_sha256']+'.json')).exists()
assert packet['core']['status']=='UNKNOWN',packet
assert packet['core']['latest_observation'] is None
feature=b.intelligence_projection(packet)
assert feature['status']=='UNKNOWN' and feature['observation'] is None
assert not feature['forecast_authority'] and not feature['scientific_pit_eligible']
assert feature==intel['feature']
registry=json.loads(Path('research/api_agent/API_TASK_REGISTRY_v1.json').read_text())
task='WEEKLY_CALIBRATION_SHADOW'
request=build_request(task,registry['tasks'][task],'fixture no paid call',context)
user=next(x for x in request['input'] if x['role']=='user')
envelope=json.loads(user['content'][0]['text'])
assert envelope['context_data']==context
receipt={'contract':'API_AGENT_RECEIPT_v3','task':task,'context_hash':sha256_bytes(canonical_bytes(context)),
         'status':'PASS','response_id':'synthetic_no_api_call','untrusted_input_envelope':True}
binding=b.calibration_feature_binding(context,freeze)
learning=b.calibration_learning_binding(context,freeze,receipt,'success')
assert binding['status']=='BOUND_CALIBRATION_FEATURE'
assert learning['api_input_status']=='MATCHED_GATEWAY_INPUT_RECEIPT'
assert not learning['model_utilization_verified']
machine={'freeze_sha256':freeze['freeze_sha256'],'context_hash':context['context_hash'],'api_status':'success',
         'api_receipt':receipt,'cn_mm_calibration_feature_binding':binding,'cn_mm_calibration_learning_binding':learning}
machine['package_sha256']=b.sha(b.canon(machine))
pointer={'freeze_sha256':freeze['freeze_sha256'],'machine_package_sha256':machine['package_sha256']}
assert b.compare_calibration_feature(machine,pointer,feature)=='MATCHED_MM_CALIBRATION_FEATURE'
print('W47_HISTORICAL_CONTEXT_GATEWAY_UNKNOWN_PROOF '+json.dumps({'feature_sha256':feature['feature_sha256'],'learning_n':learning['verified_outcome_n'],'task2_n':learning['task2_paired_n'],'gateway_context_sha256':learning['gateway_context_sha256'],'api_called':False,'receipt_fixture':True,'model_utilization_verified':False},sort_keys=True))
"""
            result=subprocess.run([sys.executable,"-c",code,str(output)],cwd=bridge.ROOT,
                                  capture_output=True,text=True,timeout=180)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            print(result.stdout)


    def test_new_producer_binding_reaches_existing_cn_consumer_in_isolated_git_fixture(self):
        # Replay the existing W47 source bytes as an explicitly synthetic NEW
        # producer execution. Never add a receipt to the actual historical tree.
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "fixture-checkout"
            def run(*args, cwd=bridge.ROOT, timeout=240):
                result = subprocess.run(args, cwd=cwd, capture_output=True,
                                        text=True, timeout=timeout)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return result.stdout
            head = bridge.git("rev-parse", "HEAD").decode().strip()
            run("git", "worktree", "add", "--detach", "--quiet", str(root), head)
            try:
                code = """
import json, subprocess, sys, tempfile
from pathlib import Path
from scripts.research import cn_mm_core_shadow_bridge_v1 as b
from scripts.master_monday.weekly_source_binding_v1 import write_binding_sidecar, verify_sidecar
def git(*args):
    return subprocess.check_output(['git',*args]).decode().strip()
def commit(paths, message):
    git('add','--',*(str(p) for p in paths))
    git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','-c','commit.gpgsign=false','commit','-qm',message)
def execute(*args):
    subprocess.run([sys.executable,*args],check=True,capture_output=True,text=True,timeout=180)
capture=Path('03_DAILY_CAPTURE_LOGS')
freeze_file=Path('research/master_monday_preflight/frozen/2026/W47/WEEKLY_EVIDENCE_FREEZE.json')
historical_raw=freeze_file.read_bytes()
historical=json.loads(historical_raw)
historical_head=git('rev-parse','HEAD')
assert 'weekly_source_binding' not in historical
# Use original pointer bytes, not an advancing LATEST pointer.
pointer_path=capture/'weekly/LATEST_WEEKLY_CALIBRATION.json'
close_path=capture/'weekly_close/LATEST_WEEKLY_MARKET_CLOSE.json'
for p in (pointer_path,close_path):
    p.write_bytes(subprocess.check_output(['git','show','ec36550041fe48b2976c06733dc4bad093b9eed5:'+str(p)]))
pointer=json.loads(pointer_path.read_bytes())
with tempfile.TemporaryDirectory() as empty:
    execute('scripts/orchestration/weekly_orchestration_controller.py','--capture-root',str(capture),
            '--accepted-data-ping-root',empty,'--output',str(freeze_file),
            '--now-utc',historical['created_at_utc'])
freeze=json.loads(freeze_file.read_bytes())
assert freeze['freeze_sha256']!=historical['freeze_sha256']
assert freeze['weekly_source_binding']['status']=='BYTE_BOUND_AT_PRODUCER'
commit([freeze_file,pointer_path,close_path],'synthetic producer fixture only')
head=git('rev-parse','HEAD')
assert b.build_checkout(freeze_file,head)['core']['status']=='UNKNOWN'
sidecar=write_binding_sidecar(freeze_file.parent,freeze)
assert verify_sidecar(freeze_file.parent,freeze,pointer,capture,freeze['freeze_sha256'])['status']=='BYTE_BINDING_AND_RECEIPT_VERIFIED'
# A receipt only present in the worktree is not sufficient.
assert b.build_checkout(freeze_file,head)['core']['status']=='UNKNOWN'
commit([sidecar],'synthetic committed source receipt only')
head=git('rev-parse','HEAD')
packet=b.build_checkout(freeze_file,head)
assert packet['core']['status']=='CORE_REPLAY_AT_OBSERVATION_ONLY',packet
assert not packet['scientific_pit_eligible'] and not packet['forecast_authority']
# Dirty source bytes must never be admitted.
source=Path(freeze['weekly_source_binding']['path'])
raw=source.read_bytes()
source.write_bytes(raw+b' ')
assert b.build_checkout(freeze_file,head)['core']['status']=='UNKNOWN'
source.write_bytes(raw)
with tempfile.TemporaryDirectory() as temp:
    packet_path=Path(temp)/'packet.json'
    packet_path.write_bytes(b.canon(packet))
    out=Path('research/api_agent/outputs/weekly/2026/W47')
    # A genuine replay of the old core rows cannot manufacture the missing
    # historical producer binding, even with a correctly rehashed packet.
    forged={**packet,'checkout_sha':historical_head,
            'freeze_sha256':historical['freeze_sha256'],
            'freeze_file_sha256':b.sha(historical_raw)}
    forged.pop('packet_sha256')
    forged['packet_sha256']=b.sha(b.canon(forged))
    old_ledger=b.committed(b.LEDGER,historical_head)
    old_registry=b.committed(b.BASE/'TRANSFORM_FREEZE_REGISTRY.json',historical_head)
    b.verify_packet_projection(forged,historical,old_ledger,old_registry,repo=b.ROOT)
    forged_path=Path(temp)/'forged.json'
    forged_path.write_bytes(b.canon(forged))
    new_raw=freeze_file.read_bytes()
    try:
        freeze_file.write_bytes(historical_raw)
        try:
            b.publish_packet(forged_path,freeze_file,historical_head,out)
        except ValueError as exc:
            assert str(exc)=='SHADOW_PINNED_WEEKLY_BINDING_UNVERIFIED',exc
        else:
            raise AssertionError('PUBLISH_ACCEPTED_UNBOUND_HISTORICAL_PACKET')
    finally:
        freeze_file.write_bytes(new_raw)
    old_path=out/('CN_MM_CORE_SHADOW_'+historical['freeze_sha256']+'.json')
    old_path.write_bytes(b.canon(forged))
    commit([old_path],'synthetic adversarial historical packet only')
    old_pointer={'iso_year':2026,'iso_week':47,'freeze_sha256':historical['freeze_sha256']}
    rejected=b.consume_cn_shadow(b.ROOT,old_pointer)
    assert rejected['status']=='UNKNOWN' and rejected['shadow_candidate_decision'] is None,rejected
    # The positive packet is still bound to its original earlier checkout.
    published=b.publish_packet(packet_path,freeze_file,head,out)
    mm_pointer={'iso_year':2026,'iso_week':47,'freeze_sha256':freeze['freeze_sha256']}
    assert b.consume_cn_shadow(b.ROOT,mm_pointer)['status']=='UNKNOWN'
    commit([published],'synthetic committed shadow receipt only')
    consumed=b.consume_cn_shadow(b.ROOT,mm_pointer)
    assert consumed['status']=='CONSUMED_SHADOW_ONLY',consumed
    assert consumed['packet_sha256']==packet['packet_sha256']
    assert consumed['shared_intelligence_feature']['status']=='SOURCE_REPLAYED_OBSERVATION_ONLY'
    assert not consumed['official_forecast_effect'] and not consumed['scientific_pit_eligible']
    # Real publisher projection and actual committed CN consumer; only the
    # gateway receipt/response are synthetic, no paid call or original write.
    from scripts.master_monday.publish_master_monday_outputs import analytical_translation
    feature=consumed['shared_intelligence_feature']
    intel={'status':'SHADOW_CONTEXT_ONLY','feature':feature,'freeze_sha256':freeze['freeze_sha256'],
           'checkout_sha':feature['checkout_sha'],'feature_uses_outcomes':False,
           'learning':{'status':'UNAVAILABLE'},'task2':{'status':'UNAVAILABLE'}}
    intel['context_sha256']=b.sha(b.canon(intel))
    context={'contract':'WEEKLY_API_CALIBRATION_CONTEXT_v6','authority':'SHADOW_ONLY',
             'iso_year':2026,'iso_week':47,'freeze_sha256':freeze['freeze_sha256'],
             'cn_mm_shared_intelligence':intel}
    context['context_hash']=b.sha(b.canon(context))
    api={'status':'READY','summary':'synthetic only','evidence_for':[],'evidence_against':[],
         'uncertainties':[],'hypotheses':[],'forecast_candidates':[
         {'metric_path':'market_metrics.spot.ETHUSDT.close','direction':'DOWN','target_mode':'PCT_MOVE',
          'threshold_pct':1.0,'target_value':None,'range_low':None,'range_high':None,'horizon_days':14,'rationale':'fixture only'}]}
    receipt={'contract':'API_AGENT_RECEIPT_v3','task':'WEEKLY_CALIBRATION_SHADOW',
             'status':'PASS','response_id':'synthetic_no_api_call','untrusted_input_envelope':True,
             'context_hash':b.sha(b.canon(context)),'output_hash':b.sha(b.canon(api)),'forecast_candidate_count':1}
    translation=analytical_translation(context,freeze,api,receipt,'success')
    assert translation['candidate_status']=='VALIDATED_UNADMITTED',translation
    machine={'freeze_sha256':freeze['freeze_sha256'],'context_hash':context['context_hash'],
             'api_status':'success','api_receipt':receipt,'operational_translation':translation,
             'cn_mm_calibration_feature_binding':b.calibration_feature_binding(context,freeze),
             'cn_mm_calibration_learning_binding':b.calibration_learning_binding(context,freeze,receipt,'success')}
    machine['package_sha256']=b.sha(b.canon(machine))
    machine_path=out/'MASTER_MONDAY_MACHINE_PACKAGE.json'
    machine_path.write_bytes(b.canon(machine))
    mm_pointer.update(machine_package_path=str(machine_path),machine_package_sha256=machine['package_sha256'])
    # A worktree-only result is not a committed delivery.
    assert b.consume_cn_shadow(b.ROOT,mm_pointer)['mm_learning_delivery'] is None
    commit([machine_path],'synthetic MM translation delivery only')
    consumed=b.consume_cn_shadow(b.ROOT,mm_pointer)
    projected=consumed['mm_learning_delivery']['mm_analytical_translation']
    assert projected['spot_candidate_directions']==[{'asset':'ETH','horizon_days':14,'direction':'DOWN','target_mode':'PCT_MOVE'}]
    assert projected['forecast_authority'] is False and projected['independent_model_output_replay'] is False
    assert consumed['official_forecast_effect'] is False
    # Tampered working tree must not replace committed delivery.
    machine_path.write_bytes(b.canon({**machine,'operational_translation':{'status':'READY'}}))
    assert b.consume_cn_shadow(b.ROOT,mm_pointer)['mm_learning_delivery'] is None
print('SYNTHETIC_NEW_PRODUCER_TO_CN_FIXTURE_PASS')
"""
                result = run(sys.executable, "-c", code, cwd=root, timeout=300)
                self.assertIn("SYNTHETIC_NEW_PRODUCER_TO_CN_FIXTURE_PASS", result)
                print(result)
            finally:
                run("git", "worktree", "remove", "--force", str(root))
            self.assertEqual(bridge.git("rev-parse", "HEAD").decode().strip(), head)

    def test_existing_workflow_wires_readback_without_paid_context_change(self):
        workflow = (bridge.ROOT / ".github/workflows/weekly-api-calibration-shadow.yml").read_text()
        self.assertEqual(workflow.count("python scripts/research/cn_mm_core_shadow_bridge_v1.py"), 2)
        self.assertIn("--output runtime/weekly-calibration/CN_MM_CORE_SHADOW.json", workflow)
        self.assertIn("--publish-from runtime/weekly-calibration/CN_MM_CORE_SHADOW.json", workflow)
        self.assertIn("paths.append(Path(Path('runtime/cn_mm_core_shadow_path.txt').read_text().strip()))", workflow)
        self.assertIn("--context-file runtime/weekly-calibration/context.json", workflow)


class DurableShadowPublication(unittest.TestCase):
    def test_exact_binding_write_once_and_authority(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            head, freeze_sha = "a" * 40, "b" * 64
            frozen = b"fixture freeze"
            source = {"freeze_sha256": freeze_sha, "iso_year": 2026, "iso_week": 47}
            base = {"contract": "CN_MM_CORE_SHADOW_BRIDGE_v1", "authority": "RESEARCH_ONLY_NON_CANONICAL",
                    "checkout_sha": head, "freeze_sha256": freeze_sha, "freeze_file_sha256": bridge.sha(frozen),
                    "first_known_status": "UNKNOWN", "scientific_pit_eligible": False,
                    "forecast_authority": False, "portfolio_execution": False, "canonical_effect": False,
                    "ledger_sha256": None, "core": bridge.unknown("NO_ELIGIBLE_OBSERVATIONS")}
            path = root / "packet.json"
            out = root / "research/api_agent/outputs/weekly/2026/W47"

            def write(value):
                packet = dict(value)
                packet["packet_sha256"] = bridge.sha(bridge.canon(packet))
                path.write_bytes(bridge.canon(packet))

            write(base)
            with patch.object(bridge, "ROOT", root), patch.object(bridge, "freeze_identity", return_value=(Path("freeze"), frozen, source)):
                target = bridge.publish_packet(path, Path("freeze"), head, out)
                self.assertEqual(target.read_bytes(), path.read_bytes())
                self.assertEqual(bridge.publish_packet(path, Path("freeze"), head, out), target)
                with self.assertRaisesRegex(ValueError, "ROUTE_MISMATCH"):
                    bridge.publish_packet(path, Path("freeze"), head, root / "wrong")
                write({**base, "forecast_authority": True})
                with self.assertRaisesRegex(ValueError, "AUTHORITY_MISMATCH"):
                    bridge.publish_packet(path, Path("freeze"), head, out)
                write({**base, "core": bridge.unknown("CHANGED")})
                with self.assertRaisesRegex(ValueError, "WRITE_ONCE_CONFLICT"):
                    bridge.publish_packet(path, Path("freeze"), head, out)


class CNConsumer(unittest.TestCase):
    def test_real_git_binding_and_missing_receipt_are_nontrading(self):
        import subprocess
        import csv
        import io
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def git(*args):
                return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True).stdout

            def write(path, raw):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)

            git("init", "-q")
            git("config", "user.email", "fixture@example.invalid")
            git("config", "user.name", "Fixture")
            freeze_sha = "b" * 64
            pointer = {"iso_year": 2026, "iso_week": 47, "freeze_sha256": freeze_sha}
            freeze = {**pointer, "window_start_utc": START, "window_end_utc": END,
                      "created_at_utc": "2026-11-23T09:45:00Z"}
            frozen = bridge.canon(freeze)
            frozen_path = root / "research/master_monday_preflight/frozen/2026/W47/WEEKLY_EVIDENCE_FREEZE.json"
            write(frozen_path, frozen)
            sample = row(12, True, False, True)
            buffer = io.StringIO(newline="")
            writer = csv.DictWriter(buffer, fieldnames=list(sample))
            writer.writeheader()
            writer.writerow(sample)
            ledger = buffer.getvalue().encode()
            write(root / bridge.LEDGER, ledger)
            registry = {"core_activation_rule": {"start_only_when": list(bridge.SINGLES), "candidates": list(CORE)},
                        "families": [{"family_id": k, "prospective_eligibility_start": FLOOR} for k in bridge.SINGLES]}
            write(root / bridge.BASE / "TRANSFORM_FREEZE_REGISTRY.json", bridge.canon(registry))
            git("add", ".")
            git("commit", "-qm", "source")
            head = git("rev-parse", "HEAD").decode().strip()
            self.assertEqual(bridge.consume_cn_shadow(root, pointer)["status"], "UNKNOWN")
            core = evaluate_rows([row(12, True, False, True)], START, END, FLOOR, lambda *_: None, MUTABLE)
            packet = {"contract": "CN_MM_CORE_SHADOW_BRIDGE_v1", "authority": "RESEARCH_ONLY_NON_CANONICAL",
                      "checkout_sha": head, "freeze_sha256": freeze_sha, "freeze_file_sha256": bridge.sha(frozen),
                      "completed_week": "2026-W47", "first_known_status": "UNKNOWN", "scientific_pit_eligible": False,
                      "forecast_authority": False, "portfolio_execution": False, "canonical_effect": False,
                      "target_semantics": "ETHBTC_FORWARD_RELATIVE_RETURN_GT_ZERO_NOT_ALTSEASON_LIFECYCLE",
                      "ledger_sha256": bridge.sha(ledger), "core": core}
            packet["packet_sha256"] = bridge.sha(bridge.canon(packet))
            path = root / f"research/api_agent/outputs/weekly/2026/W47/CN_MM_CORE_SHADOW_{freeze_sha}.json"
            write(path, bridge.canon(packet))
            self.assertEqual(bridge.consume_cn_shadow(root, pointer)["status"], "UNKNOWN")
            git("add", ".")
            git("commit", "-qm", "shadow")
            result = bridge.consume_cn_shadow(root, pointer)
            # A self-hashed synthetic ledger without source owners is not evidence.
            self.assertEqual(result["status"], "UNKNOWN")
            self.assertIsNone(result["shadow_candidate_decision"])
            self.assertFalse(result["official_forecast_effect"])
            self.assertFalse(result["scientific_pit_eligible"])
            path.write_bytes(path.read_bytes() + b" ")
            self.assertEqual(bridge.consume_cn_shadow(root, pointer)["status"], "UNKNOWN")
            forged = copy.deepcopy(packet)
            forged["core"]["latest_observation"]["decisions"]["C07_SIMPLE_3"] = True
            forged.pop("packet_sha256")
            forged["packet_sha256"] = bridge.sha(bridge.canon(forged))
            write(path, bridge.canon(forged))
            git("add", ".")
            git("commit", "-qm", "forged shadow")
            self.assertEqual(bridge.consume_cn_shadow(root, pointer)["status"], "UNKNOWN")

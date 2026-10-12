"""Zero-network regressions for bounded REA research admission."""
import copy
import hashlib
import unittest
from scripts.research.rea_custom_fit_gate_v1 import inspect_release, inspect_technical_trial, MISSION, TRIAL_CONTRACT

DATA = b"function switchLanguage(lang) { return lang === 'en' ? 'en' : 'da'; }"
HASH = hashlib.sha256(DATA).hexdigest()

def queue_packet():
    q={"contract":"RESEARCH_LAB_SOL_QUEUE_v1","task_name":"RESEARCH_LAB_SOL_ANALYSIS", "max_active_missions":1,"trigger_issue":1476,"active_mission":"RL-DISTRIBUTION-SURVIVAL-META-006","authority":{"automatic_merge":False},"missions":[{"mission_id":"RL-DISTRIBUTION-SURVIVAL-META-006","state":"ACTIVE_RELEASED"},{"mission_id":MISSION,"state":"WAITING_PREDECESSOR","mission_packet":"06_RESEARCH_LAB/mission_packets/2026-10-12__RL-REA-CUSTOM-FIT-007__sol-api.json"}]}
    p={"contract":"RESEARCH_LAB_SOL_MISSION_PACKET_v1","mission_id":MISSION,"task":"RESEARCH_LAB_SOL_ANALYSIS","status":"DESIGN_FROZEN_WAITING_PREDECESSOR_M6","authority":{"automatic_merge":False,"trading_instruction":False}}
    return q,p

def trial():
    return {"contract":TRIAL_CONTRACT,"mission_id":MISSION,"authority":"RESEARCH_ONLY","source":{"sha256":HASH,"rights_confirmed":True},"safety":{"no_secrets_in_payload":True,"authorized_capture":True,"real_process_ownership_guard":True},"host_status":"RUN_COMPLETED","baseline":{"source_sha256":HASH,"preregistered_before_rea":True,"fact_ids":["language-toggle"]},"rea":{"source_sha256":HASH,"findings":[{"fact_id":"additional-language-branch","source_anchor_exact":"return lang === 'en' ? 'en' : 'da';","independent_source_review":True,"actionable_owner_confirmed":True}]}}

class QueueGuard(unittest.TestCase):
    def test_stays_queued_not_released(self):
        q,p=queue_packet();o=inspect_release(q,p)
        self.assertEqual(o["state"],"QUEUED_NOT_RELEASED");self.assertFalse(o["api_call_permitted"])
    def test_cannot_release_while_m6_active(self):
        q,p=queue_packet();q["missions"][1]["state"]="ACTIVE_RELEASED"
        self.assertEqual(inspect_release(q,p)["state"],"BLOCKED")
    def test_duplicate_mission_id(self):
        q,p=queue_packet();q["missions"].append(copy.deepcopy(q["missions"][1]))
        self.assertEqual(inspect_release(q,p)["reason"],"DUPLICATE_MISSION_IDS")
    def test_authority_escalation(self):
        q,p=queue_packet();p["authority"]["automatic_merge"]=True
        self.assertEqual(inspect_release(q,p)["reason"],"AUTHORITY_NOT_ZERO")
    def test_conflicted_active_pointer(self):
        q,p=queue_packet();q["active_mission"]="something_else"
        self.assertEqual(inspect_release(q,p)["reason"],"ACTIVE_MISSION_POINTER_CONFLICT")

class TechnicalGate(unittest.TestCase):
    def test_source_anchored_research_only(self):
        r=inspect_technical_trial(trial(),DATA)
        self.assertEqual(r["state"],"SOURCE_ANCHORED_NOVELTY_CANDIDATE")
        self.assertEqual(r["economic_edge"],"NOT_ASSESSED")
        self.assertFalse(r["production_promotion_allowed"])
    def test_no_credit_for_duplicate_fact(self):
        t=trial();t["rea"]["findings"][0]["fact_id"]="language-toggle"
        self.assertEqual(inspect_technical_trial(t,DATA)["incremental_fact_count"],0)
    def test_no_credit_without_raw_evidence(self):
        t=trial();t["rea"]["findings"][0]["source_anchor_exact"]="I claim a secret backend exists"
        self.assertEqual(inspect_technical_trial(t,DATA)["incremental_fact_count"],0)
    def test_source_hash_mismatch(self):
        t=trial();t["source"]["sha256"]="bad"
        self.assertEqual(inspect_technical_trial(t,DATA)["reason"],"SOURCE_HASH_OR_RIGHTS_UNVERIFIED")
    def test_no_rights(self):
        t=trial();t["source"]["rights_confirmed"]=False
        self.assertEqual(inspect_technical_trial(t,DATA)["state"],"BLOCKED")
    def test_no_fake_process_guard(self):
        t=trial();t["safety"]["real_process_ownership_guard"]=False
        self.assertEqual(inspect_technical_trial(t,DATA)["reason"],"SAFETY_OR_HOST_GUARD_UNVERIFIED")
    def test_host_gated_is_not_benefit(self):
        t=trial();t["host_status"]="HOST_CAPABILITY_GATED"
        self.assertEqual(inspect_technical_trial(t,DATA)["state"],"HOST_CAPABILITY_GATED")
    def test_incomplete_run_is_blocked(self):
        t=trial();t["host_status"]="FAILED"
        self.assertEqual(inspect_technical_trial(t,DATA)["reason"],"HOST_OR_RUN_UNVERIFIED")
    def test_unfrozen_baseline(self):
        t=trial();t["baseline"]["preregistered_before_rea"]=False
        self.assertEqual(inspect_technical_trial(t,DATA)["reason"],"BASELINE_NOT_FROZEN_BEFORE_TREATMENT")
    def test_no_independent_review_no_credit(self):
        t=trial();t["rea"]["findings"][0]["independent_source_review"]=False
        self.assertEqual(inspect_technical_trial(t,DATA)["incremental_fact_count"],0)
    def test_no_owner_actionability_no_credit(self):
        t=trial();t["rea"]["findings"][0]["actionable_owner_confirmed"]=False
        self.assertEqual(inspect_technical_trial(t,DATA)["incremental_fact_count"],0)
    def test_no_challenger_future_file(self):
        t=trial();t["rea"]["source_sha256"]="not-same-file"
        self.assertEqual(inspect_technical_trial(t,DATA)["reason"],"UNEQUAL_SOURCE_CLOCK_OR_BYTES")

if __name__=="__main__": unittest.main()

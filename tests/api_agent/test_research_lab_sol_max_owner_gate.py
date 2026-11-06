"""Only one explicit owner-bound MAX exception, without promoting other missions."""
import unittest
import json
from pathlib import Path
from scripts.api_agent.research_lab_sol_dispatch import effective_registry_for_mission, MAX_ONESHOT_MISSION, TASK_NAME
class ResearchLabMaxOwnerGateTests(unittest.TestCase):
    def setUp(self):
        self.base={"tasks":{TASK_NAME:{"model":"gpt-6.1-sol","reasoning_effort":"high","max_attempts":1}}}
        self.packet={"mission_id":MAX_ONESHOT_MISSION,"original_owner_issue":1156,"reasoning_effort":"max","max_runs_for_this_release":1,"public_storage_consent_30_days":True,"public_storage_consent_comment_id":6682722905,"public_source_only":True,"one_shot_owner_mandate":"https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156#issuecomment-6682722905","review_only_no_code_write":True,"authority":{"portfolio_action":False,"repository_write":False}}
    def test_max_and_no_global_mutation(self):
        out=effective_registry_for_mission(self.base,self.packet,MAX_ONESHOT_MISSION)
        self.assertEqual(out["tasks"][TASK_NAME]["reasoning_effort"],"max")
        self.assertEqual(out["tasks"][TASK_NAME]["max_attempts"],1)
        self.assertTrue(out["tasks"][TASK_NAME]["recoverable_background"])
        self.assertTrue(out["tasks"][TASK_NAME]["public_background_storage_authorized"])
        self.assertEqual(self.base["tasks"][TASK_NAME]["reasoning_effort"],"high")
    def test_max_without_public_storage_consent_fails_before_paid_post(self):
        packet=dict(self.packet)
        del packet["public_storage_consent_30_days"]
        with self.assertRaisesRegex(ValueError, "MAX_PUBLIC_BACKGROUND_STORAGE_CONSENT_REQUIRED"):
            effective_registry_for_mission(self.base,packet,MAX_ONESHOT_MISSION)
    def test_consent_proof_and_only_public_source_are_binding(self):
        for broken in (
            dict(self.packet, public_storage_consent_comment_id=1),
            dict(self.packet, public_source_only=False),
            dict(self.packet, one_shot_owner_mandate="forged"),
            dict(self.packet, public_storage_consent_30_days=False),
        ):
            with self.assertRaisesRegex(ValueError, "MAX_PUBLIC_BACKGROUND_STORAGE_CONSENT_REQUIRED"):
                effective_registry_for_mission(self.base, broken, MAX_ONESHOT_MISSION)
    def test_new_single_active_queue_and_old_unknown_quarantine(self):
        root=Path(__file__).resolve().parents[2]
        queue=json.loads((root/"research/api_agent/research_lab_sol/RESEARCH_LAB_SOL_QUEUE_v1.json").read_text())
        active=[r for r in queue["missions"] if r["state"]=="ACTIVE_RELEASED"]
        self.assertEqual([r["mission_id"] for r in active], [MAX_ONESHOT_MISSION])
        self.assertEqual(queue["active_mission"], MAX_ONESHOT_MISSION)
        old=[r for r in queue["missions"] if r["mission_id"]=="SOL61-MAX-CYCLE-RECOVERY-ALTSEASON-20261105"]
        self.assertEqual(len(old), 1)
        self.assertFalse(old[0]["new_paid_attempts_authorized"])
        self.assertNotEqual(old[0]["state"], "ACTIVE_RELEASED")
        packet=json.loads((root/active[0]["mission_packet"]).read_text())
        self.assertEqual(packet["mission_id"], MAX_ONESHOT_MISSION)
        self.assertTrue(packet["public_storage_consent_30_days"])
        self.assertFalse(packet["authority"]["repository_write"])
    def test_normal_high_unchanged(self):
        self.assertEqual(effective_registry_for_mission(self.base,dict(self.packet,reasoning_effort="high"),"OLD")["tasks"][TASK_NAME]["reasoning_effort"],"high")
    def test_wrong_mission_owner_attempt_or_authority_fails(self):
        for packet,mid in [(self.packet,"OTHER"),(dict(self.packet,original_owner_issue=1),MAX_ONESHOT_MISSION),(dict(self.packet,max_runs_for_this_release=2),MAX_ONESHOT_MISSION),(dict(self.packet,authority={"repository_write":True}),MAX_ONESHOT_MISSION)]:
            with self.assertRaises(ValueError):effective_registry_for_mission(self.base,packet,mid)
    def test_reject_unapproved_effort_and_base_drift(self):
        with self.assertRaises(ValueError):effective_registry_for_mission(self.base,dict(self.packet,reasoning_effort="xhigh"),MAX_ONESHOT_MISSION)
        with self.assertRaises(ValueError):effective_registry_for_mission({"tasks":{TASK_NAME:{"model":"gpt-6.1-sol","reasoning_effort":"max"}}},self.packet,MAX_ONESHOT_MISSION)
if __name__=="__main__":unittest.main()

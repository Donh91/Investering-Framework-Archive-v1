"""Only one explicit owner-bound MAX exception, without promoting other missions."""
import unittest
from scripts.api_agent.research_lab_sol_dispatch import effective_registry_for_mission, MAX_ONESHOT_MISSION, TASK_NAME
class ResearchLabMaxOwnerGateTests(unittest.TestCase):
    def setUp(self):
        self.base={"tasks":{TASK_NAME:{"model":"gpt-6.1-sol","reasoning_effort":"high","max_attempts":1}}}
        self.packet={"mission_id":MAX_ONESHOT_MISSION,"original_owner_issue":1918,"reasoning_effort":"max","max_runs_for_this_release":1,"public_storage_consent_30_days":True,"review_only_no_code_write":True,"authority":{"portfolio_action":False,"repository_write":False}}
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
    def test_normal_high_unchanged(self):
        self.assertEqual(effective_registry_for_mission(self.base,dict(self.packet,reasoning_effort="high"),"OLD")["tasks"][TASK_NAME]["reasoning_effort"],"high")
    def test_wrong_mission_owner_attempt_or_authority_fails(self):
        for packet,mid in [(self.packet,"OTHER"),(dict(self.packet,original_owner_issue=1),MAX_ONESHOT_MISSION),(dict(self.packet,max_runs_for_this_release=2),MAX_ONESHOT_MISSION),(dict(self.packet,authority={"repository_write":True}),MAX_ONESHOT_MISSION)]:
            with self.assertRaises(ValueError):effective_registry_for_mission(self.base,packet,mid)
    def test_reject_unapproved_effort_and_base_drift(self):
        with self.assertRaises(ValueError):effective_registry_for_mission(self.base,dict(self.packet,reasoning_effort="xhigh"),MAX_ONESHOT_MISSION)
        with self.assertRaises(ValueError):effective_registry_for_mission({"tasks":{TASK_NAME:{"model":"gpt-6.1-sol","reasoning_effort":"max"}}},self.packet,MAX_ONESHOT_MISSION)
if __name__=="__main__":unittest.main()

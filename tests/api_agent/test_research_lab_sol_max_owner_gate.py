"""Only one explicit owner-bound MAX exception, without promoting other missions."""
import unittest
import json
import os
import tempfile
from unittest.mock import patch
from pathlib import Path
from scripts.api_agent import research_lab_sol_dispatch as native
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
class NativeNewPaidClaimTests(unittest.TestCase):
    """Mock the authenticated native GitHub evidence, not the API provider."""
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.head="a"*40
        self.trigger="100001"
        self.packet={
            "mission_id":MAX_ONESHOT_MISSION, "original_owner_issue":1156,
            "reasoning_effort":"max","max_runs_for_this_release":1,
            "public_storage_consent_30_days":True,
            "public_storage_consent_comment_id":6682722905,
            "one_shot_owner_mandate":
                "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156#issuecomment-6682722905",
            "public_source_only":True,"review_only_no_code_write":True,
            "authority":{"repository_write":False,"portfolio_action":False}
        }
        self.packetpath="06_RESEARCH_LAB/mission_packets/new-s1.json"
        for path,data in (
            (native.QUEUE_PATH, {"missions":[{
                "mission_id":MAX_ONESHOT_MISSION,"state":"ACTIVE_RELEASED",
                "mission_packet":self.packetpath}]}),
            (Path(self.packetpath),self.packet),
            (Path("research/api_agent/API_TASK_REGISTRY_v1.json"),{
                "tasks":{TASK_NAME:{"model":"gpt-6.1-sol",
                  "reasoning_effort":"high","max_attempts":1}}}),
        ):
            target=self.root/path
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(json.dumps(data))
        self.event=self.root/"event.json"
        self.event.write_text(json.dumps({"issue":{"number":1476},"comment":{
            "id":int(self.trigger),"user":{"login":"Donh91"},
            "author_association":"OWNER"}}))
        self.env={"GITHUB_REPOSITORY":"Donh91/Investering-Framework-Archive-v1",
                  "GITHUB_EVENT_NAME":"issue_comment","GITHUB_ACTOR":"Donh91",
                  "GITHUB_RUN_ATTEMPT":"1","GH_TOKEN":"test-only",
                  "GITHUB_EVENT_PATH":str(self.event)}
        self.claims=[]
        self.writes=0

    def remote(self, command, text, timeout):
        self.assertEqual(command[0],"gh")
        if command[1:3]==["api","repos/Donh91/Investering-Framework-Archive-v1/git/ref/heads/main"]:
            return json.dumps({"object":{"sha":self.head}})
        if command[1:3]==["api","repos/Donh91/Investering-Framework-Archive-v1/issues/comments/6682722905"]:
            return json.dumps({"user":{"login":"Donh91"},
                "issue_url":"https://api.github.com/repos/Donh91/Investering-Framework-Archive-v1/issues/1156",
                "body":"<!-- OWNER_RELEASE_SOL_MAX_PUBLIC_30D_20261106 -->\\n"
                       +MAX_ONESHOT_MISSION+" 30 DAYS"})
        if command[1:4]==["api","--paginate","--slurp"]:
            return json.dumps([self.claims])
        if command[1:4]==["issue","comment","1476"]:
            self.writes+=1
            self.claims.append({"body":command[-1],"id":654321,
                                "user":{"login":"github-actions[bot]"}})
            return "native-comment-created"
        raise AssertionError("unexpected native mock command "+repr(command))

    def execute(self):
        with patch.dict(os.environ,self.env), \\
             patch.object(native,"current_head",return_value=self.head), \\
             patch("subprocess.check_output",side_effect=self.remote):
            return native.reserve_native_max_claim(self.root,MAX_ONESHOT_MISSION,
                                                   1476,self.trigger)

    def test_real_owner_consent_claim_once_and_never_repeat(self):
        result=self.execute()
        self.assertEqual(result["status"],"NATIVE_PRE_HTTP_CLAIM_VERIFIED")
        self.assertEqual(self.writes,1)
        with self.assertRaisesRegex(ValueError,"MAX_CLAIM_ALREADY_EXISTS_NO_REPOST"):
            self.execute()
        self.assertEqual(self.writes,1)

    def test_wrong_or_lost_30_day_consent_cannot_claim(self):
        self.packet["public_storage_consent_comment_id"]=1
        (self.root/self.packetpath).write_text(json.dumps(self.packet))
        with self.assertRaisesRegex(ValueError,"MAX_PUBLIC_BACKGROUND_STORAGE_CONSENT_REQUIRED"):
            self.execute()
        self.assertEqual(self.writes,0)

    def test_wrong_actor_cannot_make_paid_claim(self):
        self.env["GITHUB_ACTOR"]="attacker"
        with self.assertRaisesRegex(ValueError,"MAX_NATIVE_OWNER_EVENT_INVALID"):
            self.execute()
        self.assertEqual(self.writes,0)

if __name__=="__main__":unittest.main()

"""Only one explicit owner-bound MAX exception, without promoting other missions."""
import unittest
import json
import os
import tempfile
import subprocess
import sys
from unittest.mock import patch
from pathlib import Path
from scripts.api_agent import research_lab_sol_dispatch as native
from scripts.api_agent import sol_max_shared_policy_v1 as sol_policy
from scripts.api_agent.research_lab_sol_dispatch import effective_registry_for_mission, MAX_ONESHOT_MISSION, TASK_NAME
class ResearchLabMaxOwnerGateTests(unittest.TestCase):
    def setUp(self):
        self.base={"tasks":{TASK_NAME:{"model":"gpt-6.1-sol","reasoning_effort":"high","max_attempts":1}}}
        self.packet={"mission_id":MAX_ONESHOT_MISSION,"original_owner_issue":1156,"reasoning_effort":"max","max_runs_for_this_release":1,"max_model_output_tokens_per_new_attempt":48000,"public_storage_consent_30_days":True,"public_storage_consent_comment_id":6683279250,"public_source_only":True,"one_shot_owner_mandate":"https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156#issuecomment-6683279250","review_only_no_code_write":True,"authority":{"portfolio_action":False,"repository_write":False}}
    def test_max_and_no_global_mutation(self):
        out=effective_registry_for_mission(self.base,self.packet,MAX_ONESHOT_MISSION)
        self.assertEqual(out["tasks"][TASK_NAME]["reasoning_effort"],"max")
        self.assertEqual(out["tasks"][TASK_NAME]["max_attempts"],1)
        self.assertEqual(out["tasks"][TASK_NAME]["max_output_tokens"],48000)
        self.assertTrue(out["tasks"][TASK_NAME]["recoverable_background"])
        self.assertTrue(out["tasks"][TASK_NAME]["public_background_storage_authorized"])
        self.assertEqual(out["tasks"][TASK_NAME]["model"], "gpt-6.1-sol")
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
    def test_future_token_limit_128k_and_beyond_bound_rejected(self):
        newer = dict(self.packet, max_model_output_tokens_per_new_attempt=128000)
        cfg = effective_registry_for_mission(self.base, newer, MAX_ONESHOT_MISSION)
        self.assertEqual(cfg["tasks"][TASK_NAME]["max_output_tokens"], 128000)
        for out in (0, 128001, 200000, "128000"):
            with self.assertRaisesRegex(ValueError, "MAX_OUTPUT_LIMIT_INVALID"):
                effective_registry_for_mission(
                    self.base, dict(self.packet,
                                    max_model_output_tokens_per_new_attempt=out),
                    MAX_ONESHOT_MISSION)
    def test_native_cli_direct_execution_imports_existing_repo_packages(self):
        """Native run #42218784447 failed before HTTP when direct CLI could not import scripts.

        Isolated subprocess removes Python's implicit current working directory.
        No source, budget, owner claim, GitHub or provider call occurs.
        """
        root = Path(__file__).resolve().parents[2]
        script = root / "scripts/api_agent/research_lab_sol_dispatch.py"
        code = (
            "import runpy,sys;"
            "module=runpy.run_path(sys.argv[1],run_name='cli_import_probe');"
            "from scripts.api_agent import sol_max_shared_policy_v1;"
            "assert module['TASK_NAME']=='RESEARCH_LAB_SOL_ANALYSIS'"
        )
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, "-I", "-c", code, str(script)],
                cwd=tmp, capture_output=True, text=True, timeout=20,
                check=False,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_new_single_active_queue_and_old_unknown_quarantine(self):
        root=Path(__file__).resolve().parents[2]
        queue=json.loads((root/"research/api_agent/research_lab_sol/RESEARCH_LAB_SOL_QUEUE_v1.json").read_text())
        active=[r for r in queue["missions"] if r["state"]=="ACTIVE_RELEASED"]
        # This is a one-use rotating queue, not a permanent legacy mission ID.
        # Releasing a new original owner-bound mission must not weaken the
        # one-active rule or let an old completed/unknown POST be replayed.
        self.assertEqual(len(active), 1)
        self.assertEqual(queue["active_mission"], active[0]["mission_id"])
        self.assertTrue(active[0]["new_paid_attempts_authorized"])
        self.assertEqual(active[0]["requested_effort"], "max")
        for archived in ("SOL61-MAX-CYCLE-RECOVERY-ALTSEASON-20261105",
                         "S1-ELITE-RESILIENCE-SOL61-MAX-20261106"):
            rows=[r for r in queue["missions"] if r["mission_id"]==archived]
            self.assertEqual(len(rows),1)
            self.assertFalse(rows[0]["new_paid_attempts_authorized"])
            self.assertNotEqual(rows[0]["state"],"ACTIVE_RELEASED")
        old=[r for r in queue["missions"] if r["mission_id"]=="SOL61-MAX-CYCLE-RECOVERY-ALTSEASON-20261105"]
        self.assertEqual(len(old), 1)
        self.assertFalse(old[0]["new_paid_attempts_authorized"])
        self.assertNotEqual(old[0]["state"], "ACTIVE_RELEASED")
        packet=json.loads((root/active[0]["mission_packet"]).read_text())
        self.assertEqual(packet["mission_id"], active[0]["mission_id"])
        self.assertEqual(packet["original_owner_issue"], 1156)
        self.assertEqual(packet["reasoning_effort"], "max")
        self.assertEqual(packet["max_runs_for_this_release"], 1)
        self.assertEqual(packet["review_only_no_code_write"], True)
        self.assertTrue(packet["public_source_only"])
        self.assertTrue(packet["public_storage_consent_30_days"])
        self.assertFalse(packet["authority"]["repository_write"])
        if active[0]["mission_id"] != MAX_ONESHOT_MISSION:
            legacy = [r for r in queue["missions"]
                      if r["mission_id"] == MAX_ONESHOT_MISSION]
            self.assertEqual(len(legacy), 1)
            self.assertNotEqual(legacy[0]["state"], "ACTIVE_RELEASED")
            self.assertFalse(legacy[0]["new_paid_attempts_authorized"])
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
            "reasoning_effort":"max","max_runs_for_this_release":1,"max_model_output_tokens_per_new_attempt":48000,
            "public_storage_consent_30_days":True,
            "public_storage_consent_comment_id":6683279250,
            "one_shot_owner_mandate":
                "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156#issuecomment-6683279250",
            "public_source_only":True,"review_only_no_code_write":True,
            "authority":{"repository_write":False,"portfolio_action":False}
        }
        self.packetpath="06_RESEARCH_LAB/mission_packets/new-s1.json"
        self.registry={"tasks":{TASK_NAME:{"model":"gpt-6.1-sol",
                          "reasoning_effort":"high","max_attempts":1}}}
        self.effective = native.effective_registry_for_mission(
            self.registry, self.packet, MAX_ONESHOT_MISSION)
        source_policy=json.loads((Path(__file__).resolve().parents[2]/
                                   sol_policy.POLICY_PATH).read_text())
        for path,data in (
            (sol_policy.POLICY_PATH, source_policy),
            (Path("runtime/research-lab-sol/effective_registry.json"), self.effective),
            (Path("runtime/research-lab-sol/context.json"),
             {"mission_id":MAX_ONESHOT_MISSION, "model":"gpt-6.1-sol"}),
            (native.QUEUE_PATH, {"missions":[{
                "mission_id":MAX_ONESHOT_MISSION,"state":"ACTIVE_RELEASED",
                "mission_packet":self.packetpath}]}),
            (Path(self.packetpath),self.packet),
            (Path("research/api_agent/API_TASK_REGISTRY_v1.json"),
             self.registry),
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
        self.invalid_consent=False

    def remote(self, command, text, timeout):
        self.assertEqual(command[0],"gh")
        if command[1:3]==["api","repos/Donh91/Investering-Framework-Archive-v1/git/ref/heads/main"]:
            return json.dumps({"object":{"sha":self.head}})
        if command[1:3]==["api","repos/Donh91/Investering-Framework-Archive-v1/issues/comments/"+str(self.packet["public_storage_consent_comment_id"])]:
            marker=("<!"+ "-- OWNER_RELEASE_SOL_MAX_PUBLIC_30D_20261106B -->"
                    if self.packet["mission_id"] == MAX_ONESHOT_MISSION
                    else "<!-- OWNER_RELEASE_SOL_MAX_PUBLIC_30D_20261106 -->")
            return json.dumps({"user":{"login":"Donh91"},
                "issue_url":"https://api.github.com/repos/Donh91/Investering-Framework-Archive-v1/issues/1156",
                "body":marker+"\\n"+self.packet["mission_id"]+" 30 DAYS PUBLIC SOURCE ONLY"})
        if command[1:4]==["api","--paginate","--slurp"]:
            return json.dumps([self.claims])
        if command[1:4]==["issue","comment","1476"]:
            self.writes+=1
            self.claims.append({"body":command[-1],"id":654321,
                                "user":{"login":"github-actions[bot]"}})
            return "native-comment-created"
        raise AssertionError("unexpected native mock command "+repr(command))

    def execute(self):
        with (
            patch.dict(os.environ,self.env),
            patch.object(native,"current_head",return_value=self.head),
            patch("subprocess.check_output",side_effect=self.remote),
        ):
            return native.reserve_native_max_claim(self.root,self.packet["mission_id"],
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

    def configure_future_thread_mission(self):
        mid="OTHER-THREAD-OWNER-SOLMAX-20261107-001"
        self.packet["mission_id"]=mid
        self.packet["public_storage_consent_comment_id"]=6682722905
        self.packet["one_shot_owner_mandate"]=(
            "https://github.com/Donh91/Investering-Framework-Archive-v1/"
            "issues/1156#issuecomment-6682722905")
        (self.root/self.packetpath).write_text(json.dumps(self.packet))
        (self.root/native.QUEUE_PATH).write_text(json.dumps({"missions":[{
            "mission_id":mid,"state":"ACTIVE_RELEASED",
            "mission_packet":self.packetpath}]}))
        (self.root/"runtime/research-lab-sol/context.json").write_text(
            json.dumps({"mission_id":mid,"model":"gpt-6.1-sol"}))
        digest=native.sha256_bytes((self.root/self.packetpath).read_bytes())
        release=("<!"+"-- SOL_MAX_OWNER_RELEASE_V1 mission="+mid
                 +" packet_sha256="+digest+" -->")
        event=json.loads(self.event.read_text())
        event["comment"]["body"]=("[RESEARCH_LAB_SOL] mission="+mid+"\\n"
                                   +release+"\\n30 DAYS PUBLIC SOURCE ONLY "
                                   "max_output_tokens=48000")
        self.event.write_text(json.dumps(event))
        return mid

    def test_any_chat_thread_owner_native_sourced_new_mission_can_claim_once(self):
        mid=self.configure_future_thread_mission()
        result=self.execute()
        self.assertEqual(result["mission"],mid)
        self.assertEqual(result["model"],"gpt-6.1-sol")
        self.assertEqual(self.writes,1)
        with self.assertRaisesRegex(ValueError,"MAX_CLAIM_ALREADY_EXISTS_NO_REPOST"):
            self.execute()
        self.assertEqual(self.writes,1)

    def test_forged_new_owner_comment_cannot_claim(self):
        self.configure_future_thread_mission()
        event=json.loads(self.event.read_text())
        event["comment"]["body"]=event["comment"]["body"].replace(
            "packet_sha256=", "packet_sha256=forged")
        self.event.write_text(json.dumps(event))
        with self.assertRaisesRegex(ValueError,
                                    "MAX_NATIVE_TRIGGER_PACKET_HASH_NOT_OWNER_SIGNED"):
            self.execute()
        self.assertEqual(self.writes,0)

    def test_wrong_actor_cannot_make_paid_claim(self):
        self.env["GITHUB_ACTOR"]="attacker"
        with self.assertRaisesRegex(ValueError,"MAX_NATIVE_OWNER_EVENT_INVALID"):
            self.execute()
        self.assertEqual(self.writes,0)

if __name__=="__main__":unittest.main()

"""No-bill regression safety for owner Astra two-mission research program."""
import unittest,tempfile,os,json
from pathlib import Path
from unittest import mock
from scripts.research import manual_astra_s1_vnext_20261116 as a, manual_astra_compass_total_20261116 as b, manual_astra_compass_edge_20261116 as c, manual_astra_compass_warning_20261116 as d, manual_astra_alpha_lab_20261116 as e
class Tests(unittest.TestCase):
 def test_ids_and_cost(self):
  self.assertEqual(len({m.MISSION for m in (a,b,c,d,e)}),5)
  self.assertEqual(len({m.TRIGGER for m in (a,b,c,d,e)}),5)
  self.assertNotEqual(a.TRIGGER,b.TRIGGER)
  for m in (a,b,c,d,e):
   self.assertEqual(m.MODEL,"gpt-6-astra")
   self.assertLessEqual((m.MAX_REQUEST_BYTES*m.INPUT_USD_M+m.MAX_OUTPUT_TOKENS*m.OUTPUT_USD_M)/1e6,10)
 def test_no_network_source_preparation(self):
  for m in (a,b):
   with tempfile.TemporaryDirectory() as d:
    with mock.patch.dict(os.environ,{"GITHUB_SHA":"a"*40}),mock.patch.object(m.core,"http_json",side_effect=AssertionError("network")):
     m.prepare(Path(d),preview=True)
    q=json.loads((Path(d)/"request.json").read_text())
    s=json.loads((Path(d)/"source_manifest.json").read_text())
    self.assertEqual(q["reasoning"]["effort"],"high")
    self.assertNotIn("tools",q)
    self.assertLessEqual(s["worst_case_text_only_usd"],10)
 def test_wrong_owner_rejected(self):
  for m in (a,b):
   with mock.patch.dict(os.environ,{"GITHUB_EVENT_NAME":"issue_comment","GITHUB_ACTOR":"not-owner","GITHUB_REPOSITORY":m.REPO,"GITHUB_REF":"refs/heads/main","GITHUB_SHA":"a"*40}):
    with self.assertRaisesRegex(ValueError,"NATIVE_OWNER_EVENT_REQUIRED"):m.owner_event()
 def test_replay_rejected(self):
  for m in (a,b):
   with tempfile.TemporaryDirectory() as d:
    p=Path(d);req={"model":m.MODEL,"reasoning":{"effort":"high"}}
    m.core.write_once(p/"request.json",req)
    m.core.write_once(p/"claim.json",{"mission":m.MISSION,"request_sha256":m.digest(m.core.canonical(req)),"run_id":"1","source_main_sha":"a"*40})
    m.mark_attempt(p)
    with self.assertRaises(Exception):m.mark_attempt(p)

 def test_real_paid_path_requires_distinct_prehttp_reservation(self):
  for m in (a,b,c,d,e):
   with self.assertRaisesRegex(ValueError, "CANONICAL_SHARED_BUDGET_UNVERIFIED|DISTINCT_ASTRA_10USD_RESERVATION_REQUIRED"):
    m.check_reservation()  # Consumed work cannot regain paid authority.
   with self.assertRaisesRegex(ValueError,'CANONICAL_SHARED_BUDGET_UNVERIFIED|DISTINCT_ASTRA_10USD_RESERVATION_REQUIRED'):
    with unittest.mock.patch.object(m, 'MISSION', 'FAKE-UNRESERVED-MISSION'):
     m.check_reservation()

 def test_exact_one_work_id_for_all_five_in_ledger(self):
  from scripts.api_agent.check_monthly_cost_guard import pending_risk
  from pathlib import Path
  src=Path(__file__).resolve().parents[2]/"research/api_agent/coordination/API_PENDING_BILLING_RISK_V1.json"
  lo,hi,n=pending_risk(src)
  self.assertEqual((lo,hi,n),(0.0,49.0,5))  # the canonical USD20 R2 (consumed) + USD3 Alpha-on-Sol + USD3 Sol A/B (consumed) + USD20 Navigator One + USD3 Navigator-on-Sol mission rows (#1156)
 def test_paid_workflow_five_unique_issue_owner_events(self):
  from pathlib import Path
  w=(Path(__file__).resolve().parents[2]/".github/workflows/owner-astra-research-program-20261116.yml").read_text()
  self.assertNotIn("false &&", w)
  for m in (a,b,c,d,e):
   self.assertEqual(w.count("github.event.comment.body == '"+m.TRIGGER+"'"),1)

 def test_five_distinct_native_concurrency_groups(self):
  from pathlib import Path
  wf=(Path(__file__).resolve().parents[2]/".github/workflows/owner-astra-research-program-20261116.yml").read_text()
  rows=[line.strip().split("group: ",1)[1] for line in wf.splitlines() if line.strip().startswith("group: owner-astra-high-20261116-")]
  self.assertEqual(len(rows),5)
  self.assertEqual(len(set(rows)),5)


 def test_submit_twice_bills_at_most_one_http(self):
  # Reproduce Codex P1 regression with a mocked paid provider. Never network.
  for m in (a,b,c,d,e):
   with self.subTest(mission=m.MISSION),tempfile.TemporaryDirectory() as tempdir:
    out=Path(tempdir)
    request={"model":m.MODEL,"reasoning":{"effort":"high"}}
    m.core.write_once(out/"request.json",request)
    digest=m.digest(m.core.canonical(request))
    m.core.write_once(out/"claim.json",{"mission":m.MISSION,"request_sha256":digest,
      "source_main_sha":"a"*40,"run_id":"123"})
    m.mark_attempt(out)
    with mock.patch.dict(os.environ,{"OPENAI_API_KEY":"mock"}):
     with mock.patch.object(m.core,"http_json",return_value={"id":"resp_SYNTHETIC123456",
       "model":m.MODEL,"status":"in_progress"}) as http:
      m.submit(out)
      with self.assertRaises(FileExistsError):m.submit(out)
      self.assertEqual(http.call_count,1)
      self.assertEqual(http.call_args[0][0],"POST")
    self.assertTrue((out/"submission_started.json").is_file())

 def test_all_five_no_bill_source_and_budget_admissions(self):
  import subprocess,sys
  root=Path(__file__).resolve().parents[2]
  for m in (a,b,c,d,e):
   with self.subTest(mission=m.MISSION),tempfile.TemporaryDirectory() as tmp:
    with mock.patch.dict(os.environ,{"GITHUB_SHA":"a"*40}),mock.patch.object(m.core,"http_json",side_effect=AssertionError("NETWORK_BLOCKED")):
     m.prepare(Path(tmp),preview=True)
    manifest=json.loads((Path(tmp)/"source_manifest.json").read_text())
    self.assertEqual(manifest["source_count"],len(m.SOURCE))
    self.assertGreaterEqual(len(m.SOURCE),8)
    self.assertLessEqual(manifest["worst_case_text_only_usd"],10)
    command=[sys.executable,str(root/"scripts/api_agent/check_monthly_cost_guard.py"),
      "--receipt-root",str(root/"research/api_agent/outputs"),
      "--hard-stop-usd","100","--reserve-usd","4",
      "--new-request-upper-usd","0",
      "--owner-astra-program-work-id",m.MISSION]
    proc=subprocess.run(command,text=True,capture_output=True,cwd=root,timeout=30)
    self.assertTrue(proc.stdout,proc.stderr)
    result=json.loads(proc.stdout)
    self.assertNotEqual(proc.returncode,0,result)
    self.assertEqual(result["status"],"BLOCKED",result)
    self.assertEqual(result["pending_liability_upper_usd"],49.0)  # the canonical USD20 R2 (consumed) + USD3 Alpha-on-Sol + USD3 Sol A/B (consumed) + USD20 Navigator One + USD3 Navigator-on-Sol mission rows (#1156)
    self.assertEqual(result["owner_global_hard_stop_usd"],100.0)
  bad=subprocess.run([sys.executable,str(root/"scripts/api_agent/check_monthly_cost_guard.py"),
   "--receipt-root",str(root/"research/api_agent/outputs"),
   "--hard-stop-usd","100","--reserve-usd","4","--owner-astra-program-work-id","FAKE-UNAUTHORISED"],
   text=True,capture_output=True,cwd=root,timeout=30)
  self.assertNotEqual(bad.returncode,0)
  self.assertIn("BLOCKED",bad.stdout)


 def test_public_claim_quote_cannot_deny_owner_launch(self):
  # Codex P2: never count an unauthenticated public discussion as a paid claim.
  for m in (a,b,c,d,e):
   with self.subTest(mission=m.MISSION):
    fake=[{"body":"I quoted "+m.CLAIM_MARKER+" run=123 request_sha256="+"a"*64,
           "user":{"login":"random_commenter"}}]
    with mock.patch.object(m.core,"http_json",return_value=fake):
     m.claims("synthetic_token")
    quoted=[{"body":m.CLAIM_MARKER+" run=123 request_sha256="+"a"*64+" no_retry=true research_only=true",
             "user":{"login":"random_commenter"}}]
    with mock.patch.object(m.core,"http_json",return_value=quoted):
     m.claims("synthetic_token")
    real=[{"body":m.CLAIM_MARKER+" run=123 request_sha256="+"a"*64+" no_retry=true research_only=true",
           "user":{"login":"github-actions[bot]"}}]
    with mock.patch.object(m.core,"http_json",return_value=real):
     with self.assertRaisesRegex(ValueError,"ASTRA_ONE_USE_CLAIM_ALREADY_CONSUMED"):
      m.claims("synthetic_token")

"""No-bill regression safety for owner Astra two-mission research program."""
import unittest,tempfile,os,json
from pathlib import Path
from unittest import mock
from scripts.research import manual_astra_s1_vnext_20261116 as a, manual_astra_compass_total_20261116 as b
class Tests(unittest.TestCase):
 def test_ids_and_cost(self):
  self.assertNotEqual(a.MISSION,b.MISSION)
  self.assertNotEqual(a.TRIGGER,b.TRIGGER)
  for m in (a,b):
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

 def test_real_paid_path_requires_future_distinct_prehttp_reservation(self):
  for m in (a,b):
   with self.assertRaisesRegex(ValueError,'DISTINCT_ASTRA_10USD_RESERVATION_REQUIRED'):
    m.check_reservation()

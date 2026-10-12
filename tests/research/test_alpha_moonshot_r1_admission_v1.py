import copy
import unittest
from scripts.research.alpha_moonshot_r1_admission_v1 import result,CONTRACT

def valid():
 return {"contract":CONTRACT,"case_id":"fixture","chain_id":1,"token_id":"0x123","pool_id":"0xpool","source_refs":["tx:a"],"source_exact_version_hash":"sha256:abc","source_delivery_verified":True,"matched_control_id":"control","discovery_at_utc":"2026-10-12T10:00:00Z","source_first_available_at_utc":"2026-10-12T10:05:00Z","pool_first_executable_at_utc":"2026-10-12T10:03:00Z","source_version_first_observed_at_utc":"2026-10-12T10:04:00Z","route_proof":{"exact_historical_pool_state":True,"fee_tax_gas_slippage_proven":True,"exit_endpoint_complete":True}}

class Admission(unittest.TestCase):
 def test_admits_only_technical_candidate(self):
  r=result(valid());self.assertEqual(r["state"],"TECHNICAL_ADMISSION_CANDIDATE");self.assertEqual(r["economic_edge"],"NOT_ASSESSED");self.assertFalse(r["trading_authority"])
 def test_no_source(self):
  x=valid();x["source_refs"]=[];self.assertEqual(result(x)["state"],"DATA_BLOCKED")
 def test_no_source_delivery(self):
  x=valid();x["source_delivery_verified"]=False;self.assertEqual(result(x)["state"],"DATA_BLOCKED")
 def test_bad_chain(self):
  x=valid();x["chain_id"]=True;self.assertEqual(result(x)["state"],"DATA_BLOCKED")
 def test_no_pool(self):
  x=valid();x["pool_id"]="";self.assertEqual(result(x)["state"],"DATA_BLOCKED")
 def test_unknown_clock(self):
  x=valid();x["discovery_at_utc"]="";self.assertEqual(result(x)["state"],"DATA_BLOCKED")
 def test_naive_clock(self):
  x=valid();x["discovery_at_utc"]="2026-10-12T10:00:00";self.assertEqual(result(x)["state"],"DATA_BLOCKED")
 def test_future_version_cannot_backdate(self):
  x=valid();x["source_version_first_observed_at_utc"]="2026-10-12T10:07:00Z";self.assertEqual(result(x)["state"],"DATA_BLOCKED")
 def test_route_unavailable(self):
  x=valid();x["route_proof"]={};self.assertEqual(result(x)["state"],"DATA_BLOCKED")
 def test_no_endpoint(self):
  x=valid();x["route_proof"]["exit_endpoint_complete"]=False;self.assertEqual(result(x)["state"],"DATA_BLOCKED")
 def test_latest_observation_wins(self):
  x=valid();x["discovery_at_utc"]="2026-10-12T10:06:00Z";self.assertIn("10:06:00",result(x)["earliest_eligible_at_utc"])
 def test_no_contract(self):
  x=valid();x["contract"]="other";self.assertEqual(result(x)["state"],"BLOCKED")
 def test_no_identity(self):
  x=valid();x["case_id"]="";self.assertEqual(result(x)["state"],"BLOCKED")
if __name__=="__main__":unittest.main()

import importlib.util, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
P=ROOT/"scripts/research_sources/validate_research_source_receipt.py"
S=importlib.util.spec_from_file_location("v",P); V=importlib.util.module_from_spec(S); S.loader.exec_module(V)

def good():
    return {
        "contract":"X","source":"TEST","payload_sha256":"a"*64,"payload_bytes":10,"raw_persisted":False,
        "authority":{"binding":False,"canonical_acceptance":False,"state_change":False,"portfolio_action":False,"automatic_promotion":False},
    }

class TestReceiptValidator(unittest.TestCase):
    def test_pass(self):
        self.assertEqual(V.validate(good())["status"],"PASS")
    def test_reject_raw_persistence(self):
        d=good(); d["raw_persisted"]=True
        with self.assertRaises(V.ValidationError): V.validate(d)
    def test_reject_authority(self):
        d=good(); d["authority"]["portfolio_action"]=True
        with self.assertRaises(V.ValidationError): V.validate(d)
    def test_reject_bad_hash(self):
        d=good(); d["payload_sha256"]="x"
        with self.assertRaises(V.ValidationError): V.validate(d)

if __name__=="__main__": unittest.main()

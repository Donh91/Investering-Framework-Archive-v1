import importlib.util, json, pathlib, tempfile, unittest
P=pathlib.Path('scripts/data_storage/durable_promotion_controller.py')
S=importlib.util.spec_from_file_location('dpc',P); M=importlib.util.module_from_spec(S); S.loader.exec_module(M)

class TestPromotion(unittest.TestCase):
    def good(self):
        return {"artifact_id":1,"artifact_digest":"sha256:"+"a"*64,"dataset_id":"X","partition_id":"2026-07","source_run_id":"r1","schema_version":"v1","row_count":10,"member_manifest_sha256":"b"*64,"durable_pointer":"object://x","durable_sha256":"c"*64,"independent_readback":"PASS"}
    def test_good(self): self.assertEqual(M.validate(self.good()),[])
    def test_missing(self):
        x=self.good(); del x['durable_pointer']; self.assertTrue(M.validate(x))
    def test_readback(self):
        x=self.good(); x['independent_readback']='FAIL'; self.assertIn('readback_not_pass',M.validate(x))
    def test_digest(self):
        x=self.good(); x['artifact_digest']='bad'; self.assertIn('artifact_digest_invalid',M.validate(x))
if __name__=='__main__': unittest.main()

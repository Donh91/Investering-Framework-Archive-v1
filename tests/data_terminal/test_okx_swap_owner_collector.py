import importlib.util, json, pathlib, tempfile, unittest
P=pathlib.Path('scripts/data_terminal/okx_swap_owner_collector.py')
S=importlib.util.spec_from_file_location('okx',P); M=importlib.util.module_from_spec(S); S.loader.exec_module(M)

def payload(metric,inst):
    row={"instId":inst}
    if metric=='funding': row.update({"fundingRate":"0.0001","nextFundingRate":"0.0002","fundingTime":"1780000000000"})
    elif metric=='open_interest': row.update({"oi":"100","oiCcy":"10","ts":"1780000000000"})
    else: row.update({"markPx":"65000","ts":"1780000000000"})
    return json.dumps({"code":"0","data":[row]}).encode()

class T(unittest.TestCase):
    def test_parsers(self):
        for inst in M.INSTRUMENTS:
            for metric in M.ENDPOINTS: self.assertEqual(M.parse(payload(metric,inst),metric,inst)['metric'],metric)
    def test_bad_code(self):
        with self.assertRaises(M.E): M.parse(b'{"code":"1","data":[]}','funding','BTC-USDT-SWAP')
    def test_run_and_readback(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d); ps={(i,m):payload(m,i) for i in M.INSTRUMENTS for m in M.ENDPOINTS}; M.run(ps,root,'2026-07-31T20:00:00Z'); self.assertEqual(M.verify(root)['status'],'PASS')
            p=root/'owner_snapshot.json'; p.write_text('tamper'); self.assertEqual(M.verify(root)['status'],'FAIL')
if __name__=='__main__': unittest.main()

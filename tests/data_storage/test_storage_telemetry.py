import importlib.util, pathlib, unittest
P=pathlib.Path('scripts/data_storage/storage_telemetry.py')
S=importlib.util.spec_from_file_location('st',P); M=importlib.util.module_from_spec(S); S.loader.exec_module(M)
class T(unittest.TestCase):
    def test_green(self): self.assertEqual(M.classify(1_000_000,1_000_000),('GREEN','GREEN'))
    def test_warn(self): self.assertEqual(M.classify(1_000_000,int(500*1024*1024*.65))[1],'WARN')
    def test_promote(self): self.assertEqual(M.classify(1_000_000,int(500*1024*1024*.8))[1],'PROMOTE')
    def test_emergency(self): self.assertEqual(M.classify(1_000_000,int(500*1024*1024*.95))[1],'EMERGENCY')
if __name__=='__main__': unittest.main()

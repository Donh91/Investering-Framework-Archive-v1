import importlib.util
import pathlib
import unittest

spec = importlib.util.spec_from_file_location("tree_screen", pathlib.Path(__file__).resolve().parents[2] / "research/s1_root_v2/tree_screen.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def tree(names):
    return {"truncated": False, "tree": [{"path": n, "sha": "a"*40, "mode": "040000", "type": "tree"} for n in names]}

class TreeScreenTest(unittest.TestCase):
    def test_match_is_not_authority(self):
        r, s = tree(m.ROOT_PINS), tree(m.SCRIPT_PINS)
        self.assertEqual(m.screen(r,r,s,s), "PINS_MATCH_ONLY")
    def test_every_pin_changed(self):
        for pins, root in ((m.ROOT_PINS, True), (m.SCRIPT_PINS, False)):
            for i in range(len(pins)):
                a,b = tree(pins),tree(pins)
                b["tree"][i]["sha"] = "b"*40
                r,s = tree(m.ROOT_PINS),tree(m.SCRIPT_PINS)
                args = (a,b,s,s) if root else (r,r,a,b)
                with self.subTest(pin=pins[i]):
                    self.assertEqual(m.screen(*args), "STALE")
    def test_missing_truncated_duplicate(self):
        r,s = tree(m.ROOT_PINS),tree(m.SCRIPT_PINS)
        for bad in ({"truncated":True,"tree":r["tree"]},tree(()),{"truncated":False,"tree":r["tree"]*2}):
            self.assertEqual(m.screen(r,bad,s,s),"UNKNOWN")
    def test_unpinned_change_not_authorized(self):
        r,s = tree(m.ROOT_PINS),tree(m.SCRIPT_PINS)
        b = tree((*m.ROOT_PINS,"unreviewed.py"))
        self.assertEqual(m.screen(r,b,s,s),"PINS_MATCH_ONLY")

"""Research-only nonrecursive Git tree screen; never grants merge authority."""
import re

OID = re.compile(r"[0-9a-f]{40}")
ROOT_PINS = ("AGENTS.md", "00_FMOS", ".github", ".agents", "tests")
SCRIPT_PINS = ("governance", "health")

def index(tree):
    if type(tree) is not dict or tree.get("truncated") is not False:
        raise ValueError("incomplete tree")
    result = {}
    for entry in tree["tree"]:
        name, oid = entry["path"], entry["sha"]
        if not isinstance(name, str) or "/" in name or name in result or not OID.fullmatch(oid):
            raise ValueError("invalid entry")
        result[name] = (entry["mode"], entry["type"], oid)
    return result

def screen(old_root, new_root, old_scripts, new_scripts):
    try:
        a, b, c, d = map(index, (old_root, new_root, old_scripts, new_scripts))
        for left, right, pins in ((a,b,ROOT_PINS),(c,d,SCRIPT_PINS)):
            for pin in pins:
                if pin not in left or pin not in right:
                    return "UNKNOWN"
                if left[pin] != right[pin]:
                    return "STALE"
        # Caller must independently bind fetched scripts trees to root entries.
        # Matching pins do not establish ancestry, disjointness or data-only drift.
        return "PINS_MATCH_ONLY"
    except (KeyError, TypeError, ValueError, AttributeError):
        return "UNKNOWN"

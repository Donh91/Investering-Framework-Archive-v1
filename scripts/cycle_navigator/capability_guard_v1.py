"""Compare reviewed capability manifests. Does not grant or establish release authority."""
import json
import sys

REQUIRED = {'owner', 'family', 'freshness', 'first_known', 'decision_effect', 'output', 'authority', 'fallback', 'acceptance_test'}

def validate(doc):
    if doc.get('contract') != 'CN_MM_CAPABILITY_CONTRACT_v1' or not isinstance(doc.get('capabilities'), dict):
        raise ValueError('INVALID_CONTRACT')
    for name, capability in doc['capabilities'].items():
        if not name or not REQUIRED.issubset(capability) or any(not capability[k] for k in REQUIRED):
            raise ValueError('INCOMPLETE_CAPABILITY:' + name)

def compare(old, new):
    validate(old); validate(new)
    problems = []
    for name, previous in old['capabilities'].items():
        current = new['capabilities'].get(name)
        if current is None:
            problems.append(name + ':REMOVED'); continue
        for key in REQUIRED:
            if previous[key] != current[key]:
                problems.append(name + ':CHANGED:' + key)
    return problems

if __name__ == '__main__':
    with open(sys.argv[1]) as f: old = json.load(f)
    with open(sys.argv[2]) as f: new = json.load(f)
    failures = compare(old, new)
    print(json.dumps({'status': 'FAIL' if failures else 'PASS', 'changes_requiring_review': failures}, sort_keys=True))
    sys.exit(bool(failures))

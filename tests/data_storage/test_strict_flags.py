"""Repository-wide syntactic guard for Python boolean boundary mistakes.

This is a bounded AST check, not type inference or an authorization proof.
Each exception is exact-path/rule/expression/count and requires a reason.
"""
import ast
from collections import Counter
import json
from pathlib import Path
import tokenize
import unittest

from scripts.lib.strict_flags import require_flag

FLAG_FIELDS = frozenset({
    "pit_admitted", "ledger_screen", "authorized", "approved", "enabled",
    "research_only", "official_forecast", "trading", "promotion",
    "merge_authority", "portfolio_execution", "automatic_merge",
    "automatic_code_write", "automatic_model_weight_change",
    "automatic_model_reweighting", "canonical_promotion_allowed",
    "production_admitted", "publication_authorized", "merge_authorized",
    "external_source_authenticated", "raw_dataset_bytes_verified",
    "first_known_proof_independently_verified", "trading_edge_proven",
    "production_verified", "permit_path_live_gates", "official_scoring_eligible",
    "portfolio_action_authority", "provider_first_known_verified",
})
FLAG_SUFFIXES = ("_authorized", "_allowed", "_admitted", "_enabled", "_verified")
ALLOWLIST = Path(__file__).with_name("strict_flag_allowlist.json")


def flag_field(node):
    key = None
    if isinstance(node, ast.Attribute):
        key = node.attr
    elif isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
        key = node.slice.value
    elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
          and node.func.attr == "get" and node.args
          and isinstance(node.args[0], ast.Constant)):
        key = node.args[0].value
    return isinstance(key, str) and (
        key in FLAG_FIELDS or key.endswith(FLAG_SUFFIXES)
    )


def findings(source, path):
    tree = ast.parse(source, filename=path)
    hits = {}

    def add(rule, node):
        # Deduplicate overlapping truth contexts, but not separate occurrences.
        hits[(rule, node.lineno, node.col_offset)] = (path, rule, ast.unparse(node))

    def truth(node):
        if flag_field(node):
            add("FLAG_TRUTHINESS", node)
        elif isinstance(node, ast.BoolOp):
            for value in node.values:
                truth(value)
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            truth(node.operand)
        elif isinstance(node, ast.IfExp):
            truth(node.body)
            truth(node.orelse)
        elif isinstance(node, ast.NamedExpr):
            truth(node.value)

    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            operands = [node.left, *node.comparators]
            for left, op, right in zip(operands, node.ops, operands[1:]):
                if isinstance(op, (ast.Eq, ast.NotEq)) and any(
                    isinstance(x, ast.Constant) and type(x.value) is bool
                    for x in (left, right)
                ):
                    add("BOOL_EQUALITY", node)
        if isinstance(node, (ast.If, ast.While, ast.IfExp, ast.Assert)):
            truth(node.test)
        elif isinstance(node, ast.comprehension):
            for test in node.ifs:
                truth(test)
        elif isinstance(node, ast.match_case) and node.guard is not None:
            truth(node.guard)
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            truth(node.operand)
        elif isinstance(node, ast.BoolOp):
            for operand in node.values[:-1]:
                truth(operand)
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
              and node.func.id == "bool" and len(node.args) == 1):
            truth(node.args[0])
    return [(key[1], value) for key, value in sorted(hits.items())]


def scan(root):
    counts = Counter()
    locations = {}
    paths = sorted((root / "scripts").rglob("*.py"))
    if not paths:
        raise ValueError("scripts scan empty")
    for file in paths:
        path = file.relative_to(root).as_posix()
        with tokenize.open(file) as handle:
            for line, key in findings(handle.read(), path):
                counts[key] += 1
                locations.setdefault(key, []).append(line)
    return counts, locations


def exceptions(rows):
    if not isinstance(rows, list):
        raise ValueError("allowlist must be a list")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
            "path", "rule", "expression", "count", "reason"
        }:
            raise ValueError("malformed allowlist entry")
        key = tuple(row[k] for k in ("path", "rule", "expression"))
        if (not all(isinstance(x, str) and x.strip() for x in key)
                or not key[0].startswith("scripts/") or not key[0].endswith(".py")
                or key[1] not in {"BOOL_EQUALITY", "FLAG_TRUTHINESS"}
                or type(row["count"]) is not int or row["count"] < 1
                or not isinstance(row["reason"], str) or not row["reason"].strip()
                or key in result):
            raise ValueError("invalid or duplicate allowlist entry")
        result[key] = row["count"]
    return result


class StrictFlagGuardTests(unittest.TestCase):
    def test_exact_boolean_boundary(self):
        self.assertIs(require_flag(True, "pit_admitted"), True)
        self.assertIs(require_flag(False, "pit_admitted"), False)
        for bad in (None, 0, 1, 0.0, 1.0, "false", "true", [], {}, [1]):
            with self.subTest(value=repr(bad)), self.assertRaises(ValueError):
                require_flag(bad, "pit_admitted")

    def test_bad_patterns(self):
        for source in (
            "x == True", "False != x", "0 < x == False",
            "if row.get('pit_admitted'): pass",
            "if not row['merge_authorized']: pass",
            "while obj.production_verified: pass",
            "x = row.get('trading') and action()",
            "assert bool(row['publication_authorized'])",
            "x = [r for r in rows if r['pit_admitted']]",
            "x = 1 if row.get('promotion') else 2",
            "if a and (row.get('trading') or b): pass",
        ):
            with self.subTest(source=source):
                self.assertTrue(findings(source, "scripts/demo.py"))

    def test_good_patterns(self):
        for source in (
            "if row.get('pit_admitted') is True: pass",
            "if row['merge_authorized'] is False: pass",
            "if require_flag(row['trading'], 'trading'): pass",
            "if type(value) is bool: pass",
            "if row.get('items'): pass",
            "x = 'x == True' # not code",
        ):
            with self.subTest(source=source):
                self.assertFalse(findings(source, "scripts/demo.py"))

    def test_exception_requires_exact_count_and_reason(self):
        row = dict(path="scripts/demo.py", rule="BOOL_EQUALITY",
                   expression="x == True", count=1, reason="explicit test exception")
        self.assertEqual(exceptions([row]), {("scripts/demo.py", "BOOL_EQUALITY", "x == True"): 1})
        for change in ({"count": True}, {"reason": ""}, {"path": "other.py"}):
            with self.assertRaises(ValueError):
                exceptions([{**row, **change}])
        with self.assertRaises(ValueError):
            exceptions([row, row])

    def test_repository_strict_flag_guard(self):
        root = Path(__file__).resolve().parents[2]
        counts, locations = scan(root)
        allowed = exceptions(json.loads(ALLOWLIST.read_text(encoding="utf-8")))
        differences = []
        for key in sorted(counts.keys() | allowed.keys()):
            actual, expected = counts[key], allowed.get(key, 0)
            if actual != expected:
                differences.append(
                    f"{key[0]}:{locations.get(key, [])} {key[1]} {key[2]} "
                    f"actual={actual} allowed={expected}"
                )
        self.assertFalse(differences, "\n" + "\n".join(differences))


if __name__ == "__main__":
    unittest.main()

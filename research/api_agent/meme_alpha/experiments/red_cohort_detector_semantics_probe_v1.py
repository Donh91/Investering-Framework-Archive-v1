from __future__ import annotations

import argparse
import ast
import gzip
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from typing import Any, Iterable

KEYWORDS = ("cohort", "launch", "rank", "score", "window", "wallet", "buyer", "pair", "union", "edge", "min_", "max_")
TARGET_CONSTANTS = {"FIRST_N_BUYERS", "MIN_LAUNCHES", "MAX_COHORT_SIZE"}
TARGET_FUNCTIONS = {"group_buyers_by_mint", "build_pair_counts", "merge_into_cohorts", "score_cohort", "main"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def member_by_basename(zf: zipfile.ZipFile, basename: str) -> str:
    for name in zf.namelist():
        if Path(name).name == basename:
            return name
    raise FileNotFoundError(basename)


def jsonl_rows(zf: zipfile.ZipFile, member: str) -> Iterable[dict[str, Any]]:
    raw = zf.read(member)
    stream = gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") if member.endswith(".gz") else io.BytesIO(raw)
    for line in stream:
        if line.strip():
            yield json.loads(line)


def literal(value: ast.AST) -> Any:
    try:
        return ast.literal_eval(value)
    except Exception:
        return None


def is_relevant(name: str) -> bool:
    low = name.lower()
    return any(k in low for k in KEYWORDS)


def expr(node: ast.AST | None) -> str | None:
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return None


def function_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any]:
    args = list(node.args.posonlyargs) + list(node.args.args)
    defaults = [None] * (len(args) - len(node.args.defaults)) + list(node.args.defaults)
    params = []
    for arg, default in zip(args, defaults):
        params.append({"name": arg.arg, "default_expr": expr(default), "default_literal": literal(default) if default else None})
    if node.args.vararg:
        params.append({"name": "*" + node.args.vararg.arg, "default_expr": None, "default_literal": None})
    for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
        params.append({"name": arg.arg, "default_expr": expr(default), "default_literal": literal(default) if default else None})
    if node.args.kwarg:
        params.append({"name": "**" + node.args.kwarg.arg, "default_expr": None, "default_literal": None})
    return {"name": node.name, "parameters": params}


def inspect_source(source: str) -> dict[str, Any]:
    tree = ast.parse(source)
    constants: dict[str, Any] = {}
    constant_expressions: dict[str, str | None] = {}
    functions: list[str] = []
    target_function_signatures: list[dict[str, Any]] = []
    comparisons: list[dict[str, Any]] = []
    assignments: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    slices: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
            if node.name in TARGET_FUNCTIONS:
                target_function_signatures.append(function_signature(node))
        elif isinstance(node, ast.Assign):
            value = literal(node.value)
            rhs = expr(node.value)
            for target in node.targets:
                if isinstance(target, ast.Name) and is_relevant(target.id):
                    assignments.append({"name": target.id, "expr": rhs, "literal_value": value})
                    if target.id.isupper():
                        constants[target.id] = value
                        constant_expressions[target.id] = rhs
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
            if is_relevant(name):
                value = literal(node.value) if node.value is not None else None
                rhs = expr(node.value)
                assignments.append({"name": name, "expr": rhs, "literal_value": value})
                if name.isupper():
                    constants[name] = value
                    constant_expressions[name] = rhs
        elif isinstance(node, ast.Compare):
            text = expr(node) or ""
            if any(k in text.lower() for k in KEYWORDS):
                comparisons.append({"expr": text[:500]})
        elif isinstance(node, ast.Call):
            text = expr(node) or ""
            low = text.lower()
            if any(k in low for k in ("pair", "cohort", "launch", "rank", "buyer")):
                calls.append({"expr": text[:500]})
        elif isinstance(node, ast.Subscript):
            text = expr(node) or ""
            if "buyer" in text.lower() or "rank" in text.lower():
                slices.append({"expr": text[:300]})

    source_lines = source.splitlines()
    keyword_line_summaries: list[dict[str, Any]] = []
    for idx, line in enumerate(source_lines, start=1):
        low = line.lower()
        if any(k in low for k in ("min_", "cohort", "first_rank", "score", "n_launch", "union", "window_sec", "first_n_buyers")):
            stripped = re.sub(r"\s+", " ", line.strip())
            if stripped and not stripped.startswith("#"):
                keyword_line_summaries.append({"line": idx, "sha256": hashlib.sha256(stripped.encode()).hexdigest(), "length": len(stripped)})

    return {
        "source_sha256": sha256_bytes(source.encode("utf-8")),
        "line_count": len(source_lines),
        "relevant_constants": constants,
        "constant_expressions": {k: constant_expressions.get(k) for k in sorted(TARGET_CONSTANTS)},
        "relevant_assignments": assignments[:120],
        "function_names": sorted(functions),
        "target_function_signatures": target_function_signatures,
        "relevant_comparisons": comparisons[:140],
        "relevant_calls": calls[:140],
        "buyer_or_rank_subscripts": slices[:80],
        "keyword_line_fingerprints": keyword_line_summaries[:160],
        "raw_source_archived": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    with zipfile.ZipFile(args.zip) as zf:
        detector_member = member_by_basename(zf, "analyze_sniper_cohorts.py")
        source_bytes = zf.read(detector_member)
        source = source_bytes.decode("utf-8")
        detector = inspect_source(source)

        catalogue_member = member_by_basename(zf, "sniper_cohorts.jsonl")
        intra_member = member_by_basename(zf, "sniper_cohorts_intra.jsonl.gz")
        catalogue = list(jsonl_rows(zf, catalogue_member))
        intra = list(jsonl_rows(zf, intra_member))

    result = {
        "experiment": "RED_COHORT_DETECTOR_SEMANTICS_PROBE_v1_1",
        "source": "RED-COHORT-2026-v1.1.1",
        "detector": detector,
        "catalogue": {
            "rows": len(catalogue),
            "keys": sorted({k for row in catalogue for k in row}),
            "n_launches_min": min((int(r.get("n_launches", 0)) for r in catalogue), default=None),
            "n_launches_max": max((int(r.get("n_launches", 0)) for r in catalogue), default=None),
            "cohort_size_min": min((int(r.get("cohort_size", 0)) for r in catalogue), default=None),
            "cohort_size_max": max((int(r.get("cohort_size", 0)) for r in catalogue), default=None),
        },
        "intra_launch": {
            "rows": len(intra),
            "keys": sorted({k for row in intra for k in row}),
            "window_sec_values": sorted({int(r.get("window_sec", 0)) for r in intra if r.get("window_sec") is not None}),
            "first_rank_min": min((int(r.get("first_rank", 0)) for r in intra), default=None),
            "first_rank_max": max((int(r.get("first_rank", 0)) for r in intra), default=None),
        },
        "scientific_question": "derive exact persistence criteria and then replay them causally in event-time order to compute earliest-knowable cohort timestamps",
        "authority": {
            "research_only": True,
            "automatic_trading": False,
            "buy_now_promotion": False,
            "live_threshold_change": False,
        },
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

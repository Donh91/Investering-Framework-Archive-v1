from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from typing import Any, Iterable

TARGET_BASENAMES = {
    "sniper_cohorts.jsonl",
    "sniper_cohorts_intra.jsonl.gz",
    "README.md",
    "DEPOSIT_NOTE.md",
    "paper7_v3_psm.py",
    "paper7_v3_psm_nocohort_zerofill.py",
    "analyze_sniper_cohorts.py",
}

IDENTITY_TERMS = ("mint", "token", "launch", "cohort", "wallet", "buyer", "address")
TIME_TERMS = ("time", "timestamp", "slot", "rank", "order", "window")
ECON_TERMS = ("amount", "sol", "quote", "volume", "inflow", "price", "reserve")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def md5(path: Path) -> str:
    h = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def basename_map(zf: zipfile.ZipFile) -> dict[str, str]:
    out: dict[str, str] = {}
    for name in zf.namelist():
        base = Path(name).name
        if base and base not in out:
            out[base] = name
    return out


def open_jsonl_bytes(zf: zipfile.ZipFile, member: str) -> Iterable[dict[str, Any]]:
    raw = zf.read(member)
    stream: io.BufferedReader | gzip.GzipFile
    if member.endswith(".gz"):
        stream = gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb")
    else:
        stream = io.BytesIO(raw)  # type: ignore[assignment]
    for line in stream:
        if not line.strip():
            continue
        yield json.loads(line)


def walk_schema(value: Any, prefix: str = "", depth: int = 0) -> list[tuple[str, str]]:
    if depth > 3:
        return []
    rows: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            rows.append((path, type(child).__name__))
            if isinstance(child, (dict, list)):
                rows.extend(walk_schema(child, path, depth + 1))
    elif isinstance(value, list) and value:
        path = f"{prefix}[]"
        rows.append((path, type(value[0]).__name__))
        rows.extend(walk_schema(value[0], path, depth + 1))
    return rows


def summarize_jsonl(zf: zipfile.ZipFile, member: str) -> dict[str, Any]:
    field_presence: collections.Counter[str] = collections.Counter()
    field_types: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    top_level_keys: collections.Counter[str] = collections.Counter()
    row_count = 0
    samples_examined = 0
    candidate_value_sets: dict[str, set[str]] = collections.defaultdict(set)

    for obj in open_jsonl_bytes(zf, member):
        row_count += 1
        for key in obj.keys():
            top_level_keys[str(key)] += 1
            lowered = str(key).lower()
            if any(term in lowered for term in IDENTITY_TERMS) and isinstance(obj[key], (str, int)):
                if len(candidate_value_sets[str(key)]) < 250000:
                    candidate_value_sets[str(key)].add(str(obj[key]))
        if samples_examined < 5000:
            for path, typ in walk_schema(obj):
                field_presence[path] += 1
                field_types[path][typ] += 1
            samples_examined += 1

    schema_paths = sorted(field_presence)
    def matching(terms: tuple[str, ...]) -> list[str]:
        return [path for path in schema_paths if any(term in path.lower() for term in terms)]

    return {
        "member": member,
        "rows": row_count,
        "schema_samples_examined": samples_examined,
        "top_level_keys": sorted(top_level_keys),
        "field_paths": schema_paths,
        "identity_candidate_paths": matching(IDENTITY_TERMS),
        "timing_candidate_paths": matching(TIME_TERMS),
        "economic_candidate_paths": matching(ECON_TERMS),
        "candidate_unique_counts_capped": {key: len(values) for key, values in sorted(candidate_value_sets.items())},
        "field_types": {
            path: dict(sorted(counter.items()))
            for path, counter in sorted(field_types.items())
        },
    }


def script_key_literals(text: str) -> list[str]:
    patterns = [
        r"\[['\"]([^'\"]+)['\"]\]",
        r"\.get\(['\"]([^'\"]+)['\"]",
    ]
    found: set[str] = set()
    for pattern in patterns:
        found.update(re.findall(pattern, text))
    return sorted(found)


def likely_paths(paths: list[str], terms: tuple[str, ...]) -> list[str]:
    return sorted(path for path in paths if any(term in path.lower() for term in terms))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--expected-md5", default="172198eade99f702f1da0bfdd4cf3079")
    args = ap.parse_args()

    zip_path = Path(args.zip)
    actual_md5 = md5(zip_path)
    if args.expected_md5 and actual_md5 != args.expected_md5:
        raise RuntimeError(f"RED_COHORT_MD5_MISMATCH expected={args.expected_md5} actual={actual_md5}")

    with zipfile.ZipFile(zip_path) as zf:
        mapping = basename_map(zf)
        missing = sorted(TARGET_BASENAMES - set(mapping))
        if missing:
            raise RuntimeError("RED_COHORT_EXPECTED_MEMBERS_MISSING:" + ",".join(missing))

        cohort = summarize_jsonl(zf, mapping["sniper_cohorts.jsonl"])
        intra = summarize_jsonl(zf, mapping["sniper_cohorts_intra.jsonl.gz"])

        scripts: dict[str, Any] = {}
        for base in ("paper7_v3_psm.py", "paper7_v3_psm_nocohort_zerofill.py", "analyze_sniper_cohorts.py"):
            text = zf.read(mapping[base]).decode("utf-8", errors="replace")
            keys = script_key_literals(text)
            scripts[base] = {
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "referenced_key_literals": keys,
                "identity_like_keys": likely_paths(keys, IDENTITY_TERMS),
                "timing_like_keys": likely_paths(keys, TIME_TERMS),
                "economic_like_keys": likely_paths(keys, ECON_TERMS),
            }

        readme = zf.read(mapping["README.md"]).decode("utf-8", errors="replace")
        note = zf.read(mapping["DEPOSIT_NOTE.md"]).decode("utf-8", errors="replace")

    all_intra_paths = intra["field_paths"]
    mint_like = likely_paths(all_intra_paths, ("mint", "token"))
    wallet_like = likely_paths(all_intra_paths, ("wallet", "buyer", "address"))
    time_like = likely_paths(all_intra_paths, ("time", "timestamp", "slot", "rank", "order"))
    amount_like = likely_paths(all_intra_paths, ("amount", "sol", "quote", "volume", "inflow"))

    result = {
        "experiment": "RED_COHORT_SCHEMA_JOINABILITY_PROBE_v1",
        "record_id": 21765387,
        "doi": "10.5281/zenodo.21765387",
        "release_version": "1.1.1",
        "archive": {
            "bytes": zip_path.stat().st_size,
            "md5": actual_md5,
            "sha256": sha256(zip_path),
        },
        "catalogue": cohort,
        "intra_launch": intra,
        "script_semantics": scripts,
        "joinability": {
            "explicit_mint_or_token_paths": mint_like,
            "explicit_wallet_or_buyer_paths": wallet_like,
            "event_timing_or_order_paths": time_like,
            "economic_amount_paths": amount_like,
            "has_identity_candidate": bool(mint_like),
            "has_wallet_candidate": bool(wallet_like),
            "has_timing_candidate": bool(time_like),
            "has_amount_candidate": bool(amount_like),
        },
        "guardrails": [
            "Schema presence does not by itself prove point-in-time economic-return joinability.",
            "The published headline is downstream buyer-flow, not sellable return.",
            "Cohort membership must not be augmented with future outcomes before a historical signal cutoff.",
            "Entity/funder independence requires an external point-in-time evidence layer.",
            "One public wallet prefix is intentionally redacted; exact traceability for that address is incomplete by design.",
            "Dataset/code CC-BY-4.0 does not eliminate the separately disclosed patent/licensing consideration for commercial methodology implementation.",
        ],
        "readme_sha256": hashlib.sha256(readme.encode("utf-8")).hexdigest(),
        "deposit_note_sha256": hashlib.sha256(note.encode("utf-8")).hexdigest(),
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
    print(json.dumps({
        "rows_catalogue": cohort["rows"],
        "rows_intra": intra["rows"],
        "joinability": result["joinability"],
        "archive_sha256": result["archive"]["sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()

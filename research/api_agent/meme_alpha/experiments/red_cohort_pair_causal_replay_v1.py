from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import io
import itertools
import json
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Iterable

PUMP_PROGRAM_ID = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
MIN_LAUNCHES = 3


def h(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def member_by_basename(zf: zipfile.ZipFile, basename: str) -> str:
    for name in zf.namelist():
        if Path(name).name == basename:
            return name
    raise FileNotFoundError(basename)


def rows(zf: zipfile.ZipFile, member: str) -> Iterable[dict[str, Any]]:
    raw = zf.read(member)
    stream = gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") if member.endswith(".gz") else io.BytesIO(raw)
    for line in stream:
        if line.strip():
            yield json.loads(line)


def rpc_get_tx(url: str, sig: str, timeout: int = 20) -> tuple[str, dict[str, Any] | None]:
    payload = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "getTransaction",
        "params": [sig, {"encoding": "jsonParsed", "commitment": "finalized", "maxSupportedTransactionVersion": 0}],
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "User-Agent": "MemeAlphaResearch/1.2"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        return f"HTTP_{exc.code}", None
    except Exception as exc:
        return f"ERROR_{type(exc).__name__}", None
    if body.get("error"):
        return "RPC_ERROR", None
    if body.get("result") is None:
        return "NOT_FOUND", None
    return "OK", body["result"]


def account_sets(tx: dict[str, Any]) -> tuple[set[str], set[str]]:
    keys = ((((tx.get("transaction") or {}).get("message")) or {}).get("accountKeys")) or []
    accounts: set[str] = set()
    signers: set[str] = set()
    for item in keys:
        if isinstance(item, dict):
            pubkey = item.get("pubkey")
            if pubkey:
                accounts.add(str(pubkey))
                if item.get("signer") is True:
                    signers.add(str(pubkey))
        elif isinstance(item, str):
            accounts.add(item)
    return accounts, signers


def pump_evidence(tx: dict[str, Any]) -> bool:
    accounts, _ = account_sets(tx)
    logs = ((tx.get("meta") or {}).get("logMessages")) or []
    return PUMP_PROGRAM_ID in accounts or any(PUMP_PROGRAM_ID in str(x) for x in logs)


def maximum_matching(wallets: list[str], sigs: list[str], txs: dict[str, dict[str, Any]]) -> dict[str, str]:
    edges: dict[str, list[str]] = {}
    for w in wallets:
        edges[w] = []
        for sig in sigs:
            tx = txs.get(sig)
            if tx is None:
                continue
            _, signers = account_sets(tx)
            if w in signers:
                edges[w].append(sig)
    sig_owner: dict[str, str] = {}
    def aug(w: str, seen: set[str]) -> bool:
        for sig in edges[w]:
            if sig in seen:
                continue
            seen.add(sig)
            old = sig_owner.get(sig)
            if old is None or aug(old, seen):
                sig_owner[sig] = w
                return True
        return False
    for w in wallets:
        aug(w, set())
    return {w: sig for sig, w in sig_owner.items()}


def choose_pairs(intra: list[dict[str, Any]], *, pair_count: int, max_signatures: int) -> list[tuple[tuple[str, str], list[dict[str, Any]]]]:
    pair_rows: dict[tuple[str, str], dict[str, dict[str, Any]]] = collections.defaultdict(dict)
    for row in intra:
        wallets = sorted({str(x) for x in (row.get("wallets") or [])})
        sigs = row.get("tx_sigs") or []
        if not (3 <= len(wallets) <= 4 and len(wallets) == len(sigs)):
            continue
        mint = str(row.get("mint", ""))
        for pair in itertools.combinations(wallets, 2):
            pair_rows[pair][mint] = row

    candidates = []
    for pair, by_mint in pair_rows.items():
        rs = list(by_mint.values())
        if 4 <= len(rs) <= 6:
            candidates.append((pair, rs))
    candidates.sort(key=lambda item: h("|".join(item[0])))

    selected = []
    used_sigs: set[str] = set()
    for pair, rs in candidates:
        candidate_sigs = {str(s) for r in rs for s in (r.get("tx_sigs") or [])}
        if len(used_sigs | candidate_sigs) > max_signatures:
            continue
        selected.append((pair, rs))
        used_sigs |= candidate_sigs
        if len(selected) >= pair_count:
            break
    return selected


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rpc-url", default="https://api.mainnet-beta.solana.com")
    ap.add_argument("--pairs", type=int, default=2)
    ap.add_argument("--max-signatures", type=int, default=36)
    ap.add_argument("--sleep-seconds", type=float, default=2.20)
    args = ap.parse_args()

    with zipfile.ZipFile(args.zip) as zf:
        intra = list(rows(zf, member_by_basename(zf, "sniper_cohorts_intra.jsonl.gz")))
    selected = choose_pairs(intra, pair_count=args.pairs, max_signatures=args.max_signatures)
    sigs = []
    seen = set()
    for _, rs in selected:
        for row in rs:
            for sig in row.get("tx_sigs") or []:
                sig = str(sig)
                if sig not in seen:
                    seen.add(sig)
                    sigs.append(sig)

    txs: dict[str, dict[str, Any]] = {}
    statuses: collections.Counter[str] = collections.Counter()
    pump_count = 0
    for idx, sig in enumerate(sigs):
        status, tx = rpc_get_tx(args.rpc_url, sig)
        statuses[status] += 1
        if tx is not None:
            txs[sig] = tx
            pump_count += int(pump_evidence(tx))
        if idx + 1 < len(sigs):
            time.sleep(args.sleep_seconds)

    pair_results = []
    total_fully_mapped_rows = 0
    total_subsequent_hits = 0
    for pair, rs in selected:
        reconstructed = []
        for row in rs:
            wallets = [str(x) for x in (row.get("wallets") or [])]
            row_sigs = [str(x) for x in (row.get("tx_sigs") or [])]
            mapping = maximum_matching(wallets, row_sigs, txs)
            full = len(mapping) == len(wallets) == len(row_sigs)
            if full:
                total_fully_mapped_rows += 1
            pair_mapped = all(w in mapping for w in pair)
            pair_times = []
            if pair_mapped:
                for w in pair:
                    bt = txs.get(mapping[w], {}).get("blockTime")
                    if isinstance(bt, int):
                        pair_times.append(bt)
            event_time = max(pair_times) if len(pair_times) == 2 else None
            reconstructed.append({
                "mint_sha256": h(str(row.get("mint", ""))),
                "wallet_count": len(wallets),
                "tx_sig_count": len(row_sigs),
                "fully_mapped": full,
                "pair_wallets_mapped": pair_mapped,
                "pair_event_time": event_time,
                "released_detected_at": int(row.get("detected_at")) if row.get("detected_at") is not None else None,
            })
        known = [r for r in reconstructed if r["pair_event_time"] is not None]
        known.sort(key=lambda r: (r["pair_event_time"], r["mint_sha256"]))
        qualification = known[MIN_LAUNCHES - 1] if len(known) >= MIN_LAUNCHES else None
        qualification_time = qualification["pair_event_time"] if qualification else None
        subsequent = [r for r in known[MIN_LAUNCHES:] if qualification_time is not None and r["pair_event_time"] > qualification_time]
        total_subsequent_hits += len(subsequent)
        lag = None
        if qualification and qualification["released_detected_at"] is not None:
            lag = qualification["released_detected_at"] - qualification["pair_event_time"]
        pair_results.append({
            "pair_identity_sha256": h("|".join(pair)),
            "compact_distinct_launches": len(rs),
            "reconstructed_launches_with_pair_event_time": len(known),
            "qualification_supported": qualification is not None,
            "qualification_launch_sha256": qualification["mint_sha256"] if qualification else None,
            "qualification_time_epoch": qualification_time,
            "released_detected_at_minus_qualification_event_seconds": lag,
            "strictly_subsequent_compact_hits": len(subsequent),
            "subsequent_launch_sha256": [r["mint_sha256"] for r in subsequent],
            "same_qualification_launch_excluded": True,
            "launch_reconstruction": reconstructed,
            "raw_wallet_mint_or_signature_values_logged": False,
        })

    result = {
        "experiment": "RED_COMPACT_PAIR_CAUSAL_REPLAY_v1",
        "source": "RED-COHORT-2026-v1.1.1",
        "released_detector_rule": {"first_n_buyers": 10, "minimum_distinct_pair_cooccurring_launches": 3},
        "selection": {
            "selected_pairs": len(selected),
            "selection_rule": "deterministic SHA256 order among pairs with 4-6 distinct compact hits, equal 3-4 wallet/signature row cardinality, bounded total unique signatures",
            "unique_signatures_requested": len(sigs),
            "raw_identifiers_logged": False,
        },
        "rpc": {
            "status_counts": dict(sorted(statuses.items())),
            "transactions_resolved": len(txs),
            "transactions_with_pump_evidence": pump_count,
        },
        "aggregate": {
            "fully_mapped_rows": total_fully_mapped_rows,
            "strictly_subsequent_hits_after_pair_qualification": total_subsequent_hits,
        },
        "pairs": pair_results,
        "scientific_interpretation": {
            "qualification_time": "max blockTime of the two pair-wallet transactions on the third distinct reconstructed cooccurring launch",
            "same_launch_prediction_allowed": False,
            "subsequent_launches_only": True,
            "scope": "bounded causal feasibility within released compact final-cohort rows; not a full denominator or profitability test",
            "does_not_prove": ["wallet independence", "economic alpha", "sellable return", "full online union-find cohort membership"],
        },
        "authority": {"research_only": True, "automatic_trading": False, "buy_now_promotion": False, "live_threshold_change": False},
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

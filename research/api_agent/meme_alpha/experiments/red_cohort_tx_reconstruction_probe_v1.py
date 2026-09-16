from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import io
import json
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

PUMP_PROGRAM_ID = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _zip_member_by_basename(zf: zipfile.ZipFile, basename: str) -> str:
    for name in zf.namelist():
        if Path(name).name == basename:
            return name
    raise FileNotFoundError(basename)


def _rows(zf: zipfile.ZipFile, member: str) -> Iterable[dict[str, Any]]:
    raw = zf.read(member)
    stream = gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") if member.endswith(".gz") else io.BytesIO(raw)
    for line in stream:
        if line.strip():
            yield json.loads(line)


def _rpc_get_transaction(rpc_url: str, signature: str, *, timeout: int = 20) -> tuple[str, dict[str, Any] | None]:
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            {
                "encoding": "jsonParsed",
                "commitment": "finalized",
                "maxSupportedTransactionVersion": 0,
            },
        ],
    }).encode("utf-8")
    req = urllib.request.Request(
        rpc_url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "MemeAlphaResearch/1.1"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return f"HTTP_{exc.code}", None
    except Exception as exc:
        return f"ERROR_{type(exc).__name__}", None
    if body.get("error"):
        code = body["error"].get("code", "UNKNOWN") if isinstance(body["error"], dict) else "UNKNOWN"
        return f"RPC_ERROR_{code}", None
    if body.get("result") is None:
        return "NOT_FOUND", None
    return "OK", body["result"]


def _account_sets(tx: dict[str, Any]) -> tuple[set[str], set[str]]:
    message = (((tx.get("transaction") or {}).get("message")) or {})
    keys = message.get("accountKeys") or []
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


def _has_pump_evidence(tx: dict[str, Any]) -> bool:
    accounts, _ = _account_sets(tx)
    if PUMP_PROGRAM_ID in accounts:
        return True
    logs = ((tx.get("meta") or {}).get("logMessages")) or []
    return any(PUMP_PROGRAM_ID in str(line) for line in logs)


def _epoch_guess(value: Any) -> tuple[str, int | None]:
    try:
        x = int(value)
    except (TypeError, ValueError):
        return "UNPARSEABLE", None
    if x > 10**14:
        return "MICROSECONDS", x // 1_000_000
    if x > 10**11:
        return "MILLISECONDS", x // 1_000
    if x > 10**9:
        return "SECONDS", x
    return "NON_EPOCH_OR_RELATIVE", None


def _maximum_matching(wallets: list[str], sigs: list[str], tx_by_sig: dict[str, dict[str, Any]]) -> tuple[int, dict[str, str]]:
    """Maximum wallet->transaction matching using signer membership only.

    This fixes the denominator error in the first probe: a 3-wallet/3-signature
    row should be evaluated as a bipartite graph, not as 3 wallets against each
    single transaction independently.
    """
    edges: dict[str, list[str]] = {}
    for wallet in wallets:
        candidates: list[str] = []
        for sig in sigs:
            tx = tx_by_sig.get(sig)
            if tx is None:
                continue
            _, signers = _account_sets(tx)
            if wallet in signers:
                candidates.append(sig)
        edges[wallet] = candidates

    sig_owner: dict[str, str] = {}

    def augment(wallet: str, seen: set[str]) -> bool:
        for sig in edges.get(wallet, []):
            if sig in seen:
                continue
            seen.add(sig)
            previous = sig_owner.get(sig)
            if previous is None or augment(previous, seen):
                sig_owner[sig] = wallet
                return True
        return False

    matched = 0
    for wallet in wallets:
        if augment(wallet, set()):
            matched += 1
    wallet_to_sig = {wallet: sig for sig, wallet in sig_owner.items()}
    return matched, wallet_to_sig


def _stats(values: list[int]) -> dict[str, Any]:
    if not values:
        return {"n": 0}
    s = sorted(values)
    return {"n": len(s), "min": s[0], "median": s[len(s) // 2], "max": s[-1]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rpc-url", default="https://api.mainnet-beta.solana.com")
    ap.add_argument("--sample-rows", type=int, default=24)
    ap.add_argument("--max-signatures", type=int, default=40)
    ap.add_argument("--sleep-seconds", type=float, default=0.30)
    args = ap.parse_args()

    zip_path = Path(args.zip)
    with zipfile.ZipFile(zip_path) as zf:
        member = _zip_member_by_basename(zf, "sniper_cohorts_intra.jsonl.gz")
        all_rows = list(_rows(zf, member))

    ranked = sorted(all_rows, key=lambda r: _hash(str(r.get("mint", ""))))
    sample = ranked[: max(1, args.sample_rows)]

    row_shape = collections.Counter()
    detected_units = collections.Counter()
    detected_epochs: list[int] = []
    for row in all_rows:
        wallets = row.get("wallets") or []
        sigs = row.get("tx_sigs") or []
        row_shape[(len(wallets), len(sigs))] += 1
        unit, epoch = _epoch_guess(row.get("detected_at"))
        detected_units[unit] += 1
        if epoch is not None:
            detected_epochs.append(epoch)

    selected: list[tuple[dict[str, Any], str]] = []
    for row in sample:
        for sig in row.get("tx_sigs") or []:
            selected.append((row, str(sig)))
    seen: set[str] = set()
    deduped: list[tuple[dict[str, Any], str]] = []
    for row, sig in selected:
        if sig in seen:
            continue
        seen.add(sig)
        deduped.append((row, sig))
        if len(deduped) >= args.max_signatures:
            break

    status_counts: collections.Counter[str] = collections.Counter()
    pump_tx_count = 0
    tx_error_free = 0
    tx_by_sig: dict[str, dict[str, Any]] = {}
    tx_blocktimes: list[int] = []

    for idx, (_, sig) in enumerate(deduped):
        status, tx = _rpc_get_transaction(args.rpc_url, sig)
        status_counts[status] += 1
        if tx is not None:
            tx_by_sig[sig] = tx
            if _has_pump_evidence(tx):
                pump_tx_count += 1
            if (tx.get("meta") or {}).get("err") is None:
                tx_error_free += 1
            if isinstance(tx.get("blockTime"), int):
                tx_blocktimes.append(int(tx["blockTime"]))
        if idx + 1 < len(deduped):
            time.sleep(args.sleep_seconds)

    rows_with_any_resolved = 0
    rows_fully_resolved = 0
    rows_equal_cardinality_fully_resolved = 0
    rows_perfect_signer_bijection = 0
    rows_partial_matching = 0
    resolved_wallets_total = 0
    matched_wallets_total = 0
    detected_minus_earliest_tx: list[int] = []
    detected_minus_latest_tx: list[int] = []
    row_matching_summaries: list[dict[str, Any]] = []

    for row in sample:
        wallets = [str(w) for w in (row.get("wallets") or [])]
        sigs = [str(s) for s in (row.get("tx_sigs") or [])]
        resolved_sigs = [sig for sig in sigs if sig in tx_by_sig]
        if resolved_sigs:
            rows_with_any_resolved += 1
        fully_resolved = bool(sigs) and len(resolved_sigs) == len(sigs)
        if fully_resolved:
            rows_fully_resolved += 1
        equal_cardinality = bool(wallets) and len(wallets) == len(sigs)
        if fully_resolved and equal_cardinality:
            rows_equal_cardinality_fully_resolved += 1

        matched, wallet_to_sig = _maximum_matching(wallets, sigs, tx_by_sig)
        resolved_wallets_total += len(wallets) if fully_resolved else 0
        matched_wallets_total += matched if fully_resolved else 0
        perfect = fully_resolved and equal_cardinality and matched == len(wallets)
        if perfect:
            rows_perfect_signer_bijection += 1
        elif matched > 0:
            rows_partial_matching += 1

        blocktimes = [
            int(tx_by_sig[sig]["blockTime"])
            for sig in resolved_sigs
            if isinstance(tx_by_sig[sig].get("blockTime"), int)
        ]
        _, detected_epoch = _epoch_guess(row.get("detected_at"))
        if fully_resolved and blocktimes and detected_epoch is not None:
            detected_minus_earliest_tx.append(detected_epoch - min(blocktimes))
            detected_minus_latest_tx.append(detected_epoch - max(blocktimes))

        row_matching_summaries.append({
            "row_identity_sha256": _hash(str(row.get("mint", ""))),
            "wallet_count": len(wallets),
            "tx_sig_count": len(sigs),
            "resolved_tx_count": len(resolved_sigs),
            "matched_wallet_count": matched,
            "equal_cardinality": equal_cardinality,
            "fully_resolved": fully_resolved,
            "perfect_signer_bijection": perfect,
            "raw_wallets_or_signatures_logged": False,
        })

    result = {
        "experiment": "RED_COHORT_TX_RECONSTRUCTION_FEASIBILITY_v1_1",
        "source": "RED-COHORT-2026-v1.1.1",
        "sample_design": {
            "all_intra_rows": len(all_rows),
            "deterministic_sample_rows": len(sample),
            "unique_tx_signatures_requested": len(deduped),
            "selection_rule": "sort all rows by SHA256(mint), take first N; then dedupe tx_sigs and cap signatures",
            "sample_identity_sha256": _hash("|".join(sorted(_hash(str(r.get("mint", ""))) for r in sample))),
            "raw_mints_or_signatures_logged": False,
        },
        "row_shape": {
            "wallet_count_equals_tx_sig_count_rows": sum(n for (w, s), n in row_shape.items() if w == s),
            "wallet_count_differs_tx_sig_count_rows": sum(n for (w, s), n in row_shape.items() if w != s),
            "most_common_wallet_sig_count_pairs": [
                {"wallets": pair[0], "tx_sigs": pair[1], "rows": n}
                for pair, n in row_shape.most_common(12)
            ],
        },
        "detected_at_semantics": {
            "unit_guess_counts": dict(sorted(detected_units.items())),
            "epoch_range_utc": {
                "min": datetime.fromtimestamp(min(detected_epochs), tz=timezone.utc).isoformat().replace("+00:00", "Z") if detected_epochs else None,
                "max": datetime.fromtimestamp(max(detected_epochs), tz=timezone.utc).isoformat().replace("+00:00", "Z") if detected_epochs else None,
            },
            "detected_at_minus_earliest_row_tx_seconds": _stats(detected_minus_earliest_tx),
            "detected_at_minus_latest_row_tx_seconds": _stats(detected_minus_latest_tx),
            "interpretation": "detected_at is not assumed to equal entry time or earliest-knowable cohort time",
        },
        "rpc_reconstruction": {
            "rpc_host_class": "PUBLIC_SOLANA_MAINNET_RPC_NO_AUTH",
            "status_counts": dict(sorted(status_counts.items())),
            "transactions_resolved": len(tx_by_sig),
            "transactions_with_pump_program_evidence": pump_tx_count,
            "transactions_error_free": tx_error_free,
            "blocktime_stats": _stats(tx_blocktimes),
        },
        "row_level_bipartite_mapping": {
            "method": "maximum bipartite matching of row wallets to row tx_sigs using signer membership",
            "rows_with_any_resolved_tx": rows_with_any_resolved,
            "rows_fully_resolved": rows_fully_resolved,
            "rows_equal_cardinality_and_fully_resolved": rows_equal_cardinality_fully_resolved,
            "rows_with_perfect_signer_bijection": rows_perfect_signer_bijection,
            "rows_with_partial_matching": rows_partial_matching,
            "perfect_bijection_rate_given_equal_cardinality_fully_resolved": (
                round(rows_perfect_signer_bijection / rows_equal_cardinality_fully_resolved, 6)
                if rows_equal_cardinality_fully_resolved else None
            ),
            "matched_wallet_rate_given_fully_resolved": (
                round(matched_wallets_total / resolved_wallets_total, 6)
                if resolved_wallets_total else None
            ),
            "bounded_row_summaries": row_matching_summaries,
        },
        "decision_logic": {
            "reconstruction_path_supported_if": [
                "material sampled tx_sigs resolve on chain",
                "row-level wallet/signature sets support one-to-one signer mapping",
                "Pump program evidence is present",
                "timing semantics are treated separately from economic-return semantics",
            ],
            "does_not_prove": [
                "wallet independence",
                "profitability",
                "sellable return",
                "cohort intent",
                "earliest-knowable cohort time",
            ],
        },
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

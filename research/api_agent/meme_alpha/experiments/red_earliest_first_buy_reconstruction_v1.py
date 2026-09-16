from __future__ import annotations

import argparse
import base64
import collections
import concurrent.futures
import gzip
import hashlib
import io
import itertools
import json
import struct
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Iterable

PUMP_IDL_ASOF_COMMIT = "3c6721a67c0b206b39130b454c8ba22a83ce972e"
TRADE_EVENT_DISC = bytes([189, 219, 127, 211, 78, 230, 97, 238])
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
QUALIFICATION_LAUNCH_ORDINAL = 3


def h(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def b58encode(raw: bytes) -> str:
    n = int.from_bytes(raw, "big")
    out = ""
    while n:
        n, rem = divmod(n, 58)
        out = B58[rem] + out
    zeros = len(raw) - len(raw.lstrip(b"\0"))
    return "1" * zeros + (out or "")


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


def rpc(url: str, method: str, params: list[Any], *, timeout: int = 20, retries: int = 6) -> tuple[str, Any]:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode("utf-8")
    status = "RETRY_EXHAUSTED"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": "MemeAlphaResearch/1.6"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            if not body.get("error"):
                return "OK", body.get("result")
            code = body["error"].get("code", "UNKNOWN") if isinstance(body["error"], dict) else "UNKNOWN"
            status = f"RPC_ERROR_{code}"
        except urllib.error.HTTPError as exc:
            status = f"HTTP_{exc.code}"
            if exc.code not in (429, 500, 502, 503, 504):
                return status, None
        except Exception as exc:
            status = f"ERROR_{type(exc).__name__}"
        if attempt + 1 < retries:
            time.sleep(min(0.5 * (2**attempt), 5.0))
    return status, None


class Cursor:
    def __init__(self, data: bytes):
        self.data = data
        self.i = 0

    def take(self, n: int) -> bytes:
        if self.i + n > len(self.data):
            raise ValueError("TRUNCATED")
        out = self.data[self.i : self.i + n]
        self.i += n
        return out

    def u8(self) -> int:
        return self.take(1)[0]

    def bool(self) -> bool:
        value = self.u8()
        if value not in (0, 1):
            raise ValueError("INVALID_BOOL")
        return bool(value)

    def u16(self) -> int:
        return struct.unpack("<H", self.take(2))[0]

    def u32(self) -> int:
        return struct.unpack("<I", self.take(4))[0]

    def u64(self) -> int:
        return struct.unpack("<Q", self.take(8))[0]

    def i64(self) -> int:
        return struct.unpack("<q", self.take(8))[0]

    def pubkey(self) -> str:
        return b58encode(self.take(32))

    def string(self) -> str:
        n = self.u32()
        if n > 256:
            raise ValueError("STRING_TOO_LONG")
        return self.take(n).decode("utf-8")


def decode_trade_event(payload: bytes) -> dict[str, Any]:
    pos = payload.find(TRADE_EVENT_DISC)
    if pos < 0:
        raise ValueError("NO_TRADE_EVENT_DISCRIMINATOR")
    c = Cursor(payload[pos + 8 :])
    out = {
        "mint": c.pubkey(),
        "sol_amount": c.u64(),
        "token_amount": c.u64(),
        "is_buy": c.bool(),
        "user": c.pubkey(),
        "timestamp": c.i64(),
        "virtual_sol_reserves": c.u64(),
        "virtual_token_reserves": c.u64(),
        "real_sol_reserves": c.u64(),
        "real_token_reserves": c.u64(),
        "fee_recipient": c.pubkey(),
        "fee_basis_points": c.u64(),
        "fee": c.u64(),
        "creator": c.pubkey(),
        "creator_fee_basis_points": c.u64(),
        "creator_fee": c.u64(),
        "track_volume": c.bool(),
        "total_unclaimed_tokens": c.u64(),
        "total_claimed_tokens": c.u64(),
        "current_sol_volume": c.u64(),
        "last_update_timestamp": c.i64(),
        "ix_name": c.string(),
        "mayhem_mode": c.bool(),
        "cashback_fee_basis_points": c.u64(),
        "cashback": c.u64(),
        "buyback_fee_basis_points": c.u64(),
        "buyback_fee": c.u64(),
    }
    n_shareholders = c.u32()
    if n_shareholders > 64:
        raise ValueError("SHAREHOLDER_VECTOR_TOO_LONG")
    for _ in range(n_shareholders):
        c.pubkey()
        c.u16()
    out.update(
        {
            "quote_mint": c.pubkey(),
            "quote_amount": c.u64(),
            "virtual_quote_reserves": c.u64(),
            "real_quote_reserves": c.u64(),
            "trailing_bytes": len(c.data) - c.i,
        }
    )
    return out


def trade_events(tx: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for line in (tx.get("meta") or {}).get("logMessages") or []:
        if not str(line).startswith("Program data: "):
            continue
        try:
            payload = base64.b64decode(str(line).split("Program data: ", 1)[1])
            event = decode_trade_event(payload)
        except Exception:
            continue
        key = (
            event["mint"],
            event["user"],
            event["timestamp"],
            event["token_amount"],
            event["quote_amount"],
            event["is_buy"],
        )
        if key not in seen:
            seen.add(key)
            found.append(event)
    return found


def account_sets(tx: dict[str, Any]) -> tuple[set[str], set[str]]:
    accounts: set[str] = set()
    signers: set[str] = set()
    keys = (((tx.get("transaction") or {}).get("message") or {}).get("accountKeys") or [])
    for item in keys:
        if isinstance(item, dict) and item.get("pubkey"):
            pubkey = str(item["pubkey"])
            accounts.add(pubkey)
            if item.get("signer") is True:
                signers.add(pubkey)
        elif isinstance(item, str):
            accounts.add(item)
    return accounts, signers


def choose_pairs(intra: list[dict[str, Any]], count: int) -> list[tuple[tuple[str, str], list[dict[str, Any]]]]:
    by_pair: dict[tuple[str, str], dict[str, dict[str, Any]]] = collections.defaultdict(dict)
    for row in intra:
        wallets = sorted({str(x) for x in row.get("wallets") or []})
        sigs = [str(x) for x in row.get("tx_sigs") or []]
        if not (3 <= len(wallets) <= 4 and len(wallets) == len(sigs)):
            continue
        mint = str(row.get("mint", ""))
        for pair in itertools.combinations(wallets, 2):
            by_pair[pair][mint] = row
    candidates = [
        (pair, list(rows_by_mint.values()))
        for pair, rows_by_mint in by_pair.items()
        if 4 <= len(rows_by_mint) <= 6
    ]
    candidates.sort(key=lambda item: h("|".join(item[0])))
    return candidates[:count]


def map_wallets(wallets: list[str], sigs: list[str], txs: dict[str, dict[str, Any]]) -> dict[str, str]:
    edges = {
        wallet: [sig for sig in sigs if sig in txs and wallet in account_sets(txs[sig])[1]]
        for wallet in wallets
    }
    owners: dict[str, str] = {}

    def augment(wallet: str, seen: set[str]) -> bool:
        for sig in edges[wallet]:
            if sig in seen:
                continue
            seen.add(sig)
            previous = owners.get(sig)
            if previous is None or augment(previous, seen):
                owners[sig] = wallet
                return True
        return False

    for wallet in wallets:
        augment(wallet, set())
    return {wallet: sig for sig, wallet in owners.items()}


def fetch_tx(url: str, sig: str) -> tuple[str, str, dict[str, Any] | None]:
    status, tx = rpc(
        url,
        "getTransaction",
        [sig, {"encoding": "jsonParsed", "commitment": "finalized", "maxSupportedTransactionVersion": 0}],
    )
    return sig, status, tx


def fetch_address_history(
    url: str,
    address: str,
    before_signature: str,
    *,
    page_size: int,
    max_pages: int,
) -> tuple[list[dict[str, Any]], bool, str, list[str]]:
    infos: list[dict[str, Any]] = []
    seen: set[str] = set()
    cursor = before_signature
    statuses: list[str] = []

    for _ in range(max_pages):
        status, result = rpc(
            url,
            "getSignaturesForAddress",
            [address, {"before": cursor, "limit": page_size, "commitment": "finalized"}],
        )
        statuses.append(status)
        if status != "OK" or result is None:
            return infos, False, f"SIGNATURE_HISTORY_{status}", statuses

        page = [item for item in result if isinstance(item, dict) and item.get("signature")]
        if not page:
            return infos, True, "ADDRESS_HISTORY_EXHAUSTED_EMPTY", statuses

        new_items = 0
        for item in page:
            sig = str(item["signature"])
            if sig in seen:
                continue
            seen.add(sig)
            infos.append(item)
            new_items += 1

        if len(page) < page_size:
            return infos, True, "ADDRESS_HISTORY_EXHAUSTED_SHORT_PAGE", statuses
        if new_items == 0:
            return infos, False, "SIGNATURE_HISTORY_CURSOR_STALLED", statuses
        cursor = str(page[-1]["signature"])

    return infos, False, "MAX_HISTORY_PAGES_REACHED", statuses


def target_identity(pair: tuple[str, str], mint: str, wallet: str, ordinal: int) -> str:
    return h("|".join([*pair, mint, wallet, str(ordinal)]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pairs", type=int, default=2)
    ap.add_argument("--rpc-url", default="https://api.mainnet-beta.solana.com")
    ap.add_argument("--history-page-size", type=int, default=250)
    ap.add_argument("--max-history-pages", type=int, default=8)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    with zipfile.ZipFile(args.zip) as zf:
        intra = list(rows(zf, member_by_basename(zf, "sniper_cohorts_intra.jsonl.gz")))

    selected_pairs = choose_pairs(intra, args.pairs)
    ordered_pairs = [
        (
            pair,
            sorted(pair_rows, key=lambda row: (int(row.get("detected_at") or 0), h(str(row.get("mint", ""))))),
        )
        for pair, pair_rows in selected_pairs
    ]

    expected_targets: list[dict[str, Any]] = []
    target_launches = 0
    released_sigs: set[str] = set()

    for pair, pair_rows in ordered_pairs:
        for launch_ordinal, row in enumerate(pair_rows, start=1):
            if launch_ordinal < QUALIFICATION_LAUNCH_ORDINAL:
                continue
            target_launches += 1
            sigs = [str(x) for x in row.get("tx_sigs") or []]
            released_sigs.update(sigs)
            mint = str(row.get("mint", ""))
            for wallet in pair:
                expected_targets.append(
                    {
                        "pair": pair,
                        "row": row,
                        "wallet": wallet,
                        "mint": mint,
                        "launch_ordinal": launch_ordinal,
                        "prediction_eligible": launch_ordinal > QUALIFICATION_LAUNCH_ORDINAL,
                        "target_identity_sha256": target_identity(pair, mint, wallet, launch_ordinal),
                    }
                )

    released: dict[str, dict[str, Any]] = {}
    released_statuses: collections.Counter[str] = collections.Counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        for sig, status, tx in executor.map(lambda s: fetch_tx(args.rpc_url, s), sorted(released_sigs)):
            released_statuses[status] += 1
            if tx is not None:
                released[sig] = tx

    mapped_targets: list[dict[str, Any]] = []
    fully_mapped_target_launches = 0
    for pair, pair_rows in ordered_pairs:
        for launch_ordinal, row in enumerate(pair_rows, start=1):
            if launch_ordinal < QUALIFICATION_LAUNCH_ORDINAL:
                continue
            wallets = [str(x) for x in row.get("wallets") or []]
            sigs = [str(x) for x in row.get("tx_sigs") or []]
            mapping = map_wallets(wallets, sigs, released)
            full_row_resolution = bool(sigs) and all(sig in released for sig in sigs)
            full_row_bijection = full_row_resolution and len(mapping) == len(wallets) == len(sigs)
            if full_row_bijection:
                fully_mapped_target_launches += 1
            mint = str(row.get("mint", ""))
            for wallet in pair:
                mapped_targets.append(
                    {
                        "pair": pair,
                        "row": row,
                        "wallet": wallet,
                        "mint": mint,
                        "launch_ordinal": launch_ordinal,
                        "prediction_eligible": launch_ordinal > QUALIFICATION_LAUNCH_ORDINAL,
                        "target_identity_sha256": target_identity(pair, mint, wallet, launch_ordinal),
                        "released_sig": mapping.get(wallet) if full_row_bijection else None,
                        "full_row_resolution": full_row_resolution,
                        "full_row_bijection": full_row_bijection,
                    }
                )

    histories: dict[str, dict[str, Any]] = {}
    history_rpc_statuses: collections.Counter[str] = collections.Counter()
    for target in mapped_targets:
        released_sig = target["released_sig"]
        if not released_sig:
            continue
        tx = released.get(released_sig)
        accounts, _ = account_sets(tx or {})
        mint_account_evidence = target["mint"] in accounts
        history_key = target["target_identity_sha256"]
        if not mint_account_evidence:
            histories[history_key] = {
                "infos": [],
                "complete": False,
                "reason": "RELEASED_TX_DOES_NOT_CONTAIN_TARGET_MINT_ACCOUNT",
                "mint_account_evidence": False,
            }
            continue
        infos, complete, reason, statuses = fetch_address_history(
            args.rpc_url,
            target["mint"],
            released_sig,
            page_size=args.history_page_size,
            max_pages=args.max_history_pages,
        )
        history_rpc_statuses.update(statuses)
        histories[history_key] = {
            "infos": infos,
            "complete": complete,
            "reason": reason,
            "mint_account_evidence": True,
        }

    history_success_sigs: set[str] = set()
    target_required_sigs: dict[str, set[str]] = {}
    for target in mapped_targets:
        key = target["target_identity_sha256"]
        released_sig = target["released_sig"]
        hist = histories.get(key)
        required: set[str] = set()
        if released_sig:
            released_tx = released.get(released_sig)
            if released_tx is not None and (released_tx.get("meta") or {}).get("err") is None:
                required.add(released_sig)
        if hist:
            for info in hist["infos"]:
                if info.get("err") is None and info.get("signature"):
                    required.add(str(info["signature"]))
        target_required_sigs[key] = required
        history_success_sigs.update(required)

    txcache = dict(released)
    historical_tx_statuses: collections.Counter[str] = collections.Counter()
    missing = sorted(history_success_sigs - set(txcache))
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        for sig, status, tx in executor.map(lambda s: fetch_tx(args.rpc_url, s), missing):
            historical_tx_statuses[status] += 1
            if tx is not None:
                txcache[sig] = tx

    output_rows: list[dict[str, Any]] = []
    for target in mapped_targets:
        key = target["target_identity_sha256"]
        released_sig = target["released_sig"]
        hist = histories.get(key) or {
            "infos": [],
            "complete": False,
            "reason": "TARGET_NOT_MAPPED",
            "mint_account_evidence": False,
        }
        required = target_required_sigs.get(key, set())
        resolved_required = {sig for sig in required if sig in txcache}
        history_transactions_complete = bool(hist["complete"]) and required == resolved_required

        candidates: list[tuple[int, int, str, dict[str, Any]]] = []
        if history_transactions_complete:
            for sig in sorted(required):
                tx = txcache[sig]
                slot = int(tx.get("slot") or 0)
                for event in trade_events(tx):
                    if event["mint"] == target["mint"] and event["user"] == target["wallet"] and event["is_buy"] is True:
                        candidates.append((int(event["timestamp"]), slot, sig, event))
        candidates.sort(key=lambda item: (item[0], item[1], item[2]))

        first = candidates[0] if candidates else None
        earliest_tie_count = 0
        if first is not None:
            earliest_tie_count = sum(1 for item in candidates if (item[0], item[1]) == (first[0], first[1]))
        earliest_unambiguous = first is not None and earliest_tie_count == 1

        output_rows.append(
            {
                "target_identity_sha256": key,
                "pair_identity_sha256": h("|".join(target["pair"])),
                "mint_sha256": h(target["mint"]),
                "wallet_sha256": h(target["wallet"]),
                "launch_ordinal": target["launch_ordinal"],
                "qualification_launch": target["launch_ordinal"] == QUALIFICATION_LAUNCH_ORDINAL,
                "prediction_eligible": target["prediction_eligible"],
                "prediction_exclusion_reason": (
                    "QUALIFICATION_LAUNCH_MUST_NOT_BE_SCORED"
                    if target["launch_ordinal"] == QUALIFICATION_LAUNCH_ORDINAL
                    else None
                ),
                "released_signature_sha256": h(released_sig) if released_sig else None,
                "released_detected_at": target["row"].get("detected_at"),
                "full_row_signature_resolution": target["full_row_resolution"],
                "full_row_wallet_signature_bijection": target["full_row_bijection"],
                "released_mint_account_evidence": hist["mint_account_evidence"],
                "history_complete": hist["complete"],
                "history_completion_reason": hist["reason"],
                "history_signatures_discovered": len(hist["infos"]),
                "successful_history_transactions_required": len(required),
                "successful_history_transactions_resolved": len(resolved_required),
                "history_transactions_complete": history_transactions_complete,
                "earliest_buy_found": first is not None,
                "earliest_buy_unambiguous": earliest_unambiguous,
                "earliest_buy_tie_count_at_min_timestamp_and_slot": earliest_tie_count,
                "earliest_buy_signature_sha256": h(first[2]) if first else None,
                "earliest_buy_timestamp": first[0] if first else None,
                "earliest_buy_slot": first[1] if first else None,
                "earliest_buy_quote_amount_raw": first[3]["quote_amount"] if first else None,
                "earliest_buy_token_amount_raw": first[3]["token_amount"] if first else None,
                "earliest_buy_real_quote_reserves_raw": first[3]["real_quote_reserves"] if first else None,
                "earliest_buy_real_token_reserves_raw": first[3]["real_token_reserves"] if first else None,
                "raw_identifiers_logged": False,
            }
        )

    expected_count = len(expected_targets)
    mapped_count = sum(1 for row in output_rows if row["released_signature_sha256"] is not None)
    history_complete_count = sum(1 for row in output_rows if row["history_complete"])
    history_tx_complete_count = sum(1 for row in output_rows if row["history_transactions_complete"])
    earliest_found = sum(1 for row in output_rows if row["earliest_buy_found"])
    earliest_unambiguous = sum(1 for row in output_rows if row["earliest_buy_unambiguous"])
    qualification_leak_count = sum(
        1
        for row in output_rows
        if row["launch_ordinal"] == QUALIFICATION_LAUNCH_ORDINAL and row["prediction_eligible"]
    )
    post_qualification_ineligible_count = sum(
        1
        for row in output_rows
        if row["launch_ordinal"] > QUALIFICATION_LAUNCH_ORDINAL and not row["prediction_eligible"]
    )

    supported = (
        expected_count > 0
        and len(output_rows) == expected_count
        and mapped_count == expected_count
        and history_complete_count == expected_count
        and history_tx_complete_count == expected_count
        and earliest_found == expected_count
        and earliest_unambiguous == expected_count
        and qualification_leak_count == 0
        and post_qualification_ineligible_count == 0
    )

    result = {
        "experiment": "RED_EARLIEST_FIRST_BUY_RECONSTRUCTION_v2_FAIL_CLOSED",
        "source": "RED-COHORT-2026-v1.1.1",
        "historical_protocol_schema": {"pump_idl_commit": PUMP_IDL_ASOF_COMMIT},
        "method": {
            "target_population": "freeze every pair-wallet occurrence from launch #3 onward before any RPC/mapping drop can occur",
            "released_row_mapping": "require complete row transaction resolution and one-to-one wallet/signature signer bijection",
            "history_search": "for each mapped wallet+mint occurrence, walk target-mint signature history strictly backward from that occurrence's released signature until address history exhaustion; cap exhaustion is BLOCKED",
            "selection": "earliest exact mint+wallet Pump TradeEvent where is_buy=true using pinned historical schema",
            "history_page_size": args.history_page_size,
            "max_history_pages": args.max_history_pages,
            "parallel_rpc_workers": args.workers,
        },
        "counts": {
            "selected_pairs": len(ordered_pairs),
            "target_launches": target_launches,
            "expected_target_occurrences": expected_count,
            "materialized_target_occurrences": len(output_rows),
            "released_signatures_requested": len(released_sigs),
            "released_transactions_resolved": len(released),
            "fully_mapped_target_launches": fully_mapped_target_launches,
            "mapped_target_occurrences": mapped_count,
            "history_complete_occurrences": history_complete_count,
            "history_transactions_complete_occurrences": history_tx_complete_count,
            "earliest_buy_found": earliest_found,
            "earliest_buy_unambiguous": earliest_unambiguous,
            "unique_historical_transactions_required": len(history_success_sigs),
            "unique_historical_transactions_resolved": sum(1 for sig in history_success_sigs if sig in txcache),
        },
        "rpc": {
            "released_transaction_status_counts": dict(sorted(released_statuses.items())),
            "history_signature_status_counts": dict(sorted(history_rpc_statuses.items())),
            "historical_transaction_status_counts": dict(sorted(historical_tx_statuses.items())),
        },
        "invariants": {
            "qualification_launch_ordinal": QUALIFICATION_LAUNCH_ORDINAL,
            "qualification_launch_prediction_eligible_count": qualification_leak_count,
            "post_qualification_prediction_ineligible_count": post_qualification_ineligible_count,
            "launch_3_excluded_from_prediction": qualification_leak_count == 0,
            "only_launch_4_plus_prediction_eligible": post_qualification_ineligible_count == 0,
            "target_population_frozen_before_rpc_mapping": True,
            "history_cap_is_fail_closed": True,
        },
        "rows": output_rows,
        "verdict": {
            "causal_first_buy_reconstruction": "SUPPORTED" if supported else "PARTIAL_OR_BLOCKED",
            "safe_to_use_released_tx_timestamp_as_first_buy": False,
            "pilot_gate_ready": supported,
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

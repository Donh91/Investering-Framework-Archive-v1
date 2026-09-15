from __future__ import annotations

import argparse
import base64
import collections
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

PUMP_PROGRAM_ID = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
PUMP_IDL_ASOF_COMMIT = "3c6721a67c0b206b39130b454c8ba22a83ce972e"
PUMP_IDL_ASOF_DATE_UTC = "2026-05-18T19:03:28Z"
TRADE_EVENT_DISC = bytes([189, 219, 127, 211, 78, 230, 97, 238])
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def h(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def b58encode(raw: bytes) -> str:
    n = int.from_bytes(raw, "big")
    out = ""
    while n:
        n, r = divmod(n, 58)
        out = B58[r] + out
    zeros = len(raw) - len(raw.lstrip(b"\0"))
    return "1" * zeros + (out or "")


def b58decode(text: str) -> bytes:
    n = 0
    for c in text:
        n = n * 58 + B58.index(c)
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    zeros = len(text) - len(text.lstrip("1"))
    return b"\0" * zeros + raw


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
    payload = json.dumps({"jsonrpc":"2.0","id":1,"method":"getTransaction","params":[sig,{"encoding":"jsonParsed","commitment":"finalized","maxSupportedTransactionVersion":0}]}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type":"application/json","User-Agent":"MemeAlphaResearch/1.3"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        return f"HTTP_{exc.code}", None
    except Exception as exc:
        return f"ERROR_{type(exc).__name__}", None
    if body.get("error"):
        return "RPC_ERROR", None
    return ("OK", body.get("result")) if body.get("result") else ("NOT_FOUND", None)


def account_sets(tx: dict[str, Any]) -> tuple[set[str], set[str]]:
    keys = ((((tx.get("transaction") or {}).get("message")) or {}).get("accountKeys")) or []
    accounts, signers = set(), set()
    for item in keys:
        if isinstance(item, dict) and item.get("pubkey"):
            p = str(item["pubkey"]); accounts.add(p)
            if item.get("signer") is True: signers.add(p)
        elif isinstance(item, str): accounts.add(item)
    return accounts, signers


def max_matching(wallets: list[str], sigs: list[str], txs: dict[str, dict[str, Any]]) -> dict[str, str]:
    edges = {w: [] for w in wallets}
    for w in wallets:
        for sig in sigs:
            if sig in txs and w in account_sets(txs[sig])[1]: edges[w].append(sig)
    owners: dict[str, str] = {}
    def aug(w: str, seen: set[str]) -> bool:
        for sig in edges[w]:
            if sig in seen: continue
            seen.add(sig)
            old = owners.get(sig)
            if old is None or aug(old, seen): owners[sig] = w; return True
        return False
    for w in wallets: aug(w, set())
    return {w:s for s,w in owners.items()}


def choose_pairs(intra: list[dict[str, Any]], count: int) -> list[tuple[tuple[str,str], list[dict[str,Any]]]]:
    pair_rows: dict[tuple[str,str], dict[str,dict[str,Any]]] = collections.defaultdict(dict)
    for row in intra:
        wallets = sorted({str(x) for x in row.get("wallets") or []})
        sigs = row.get("tx_sigs") or []
        if not (3 <= len(wallets) <= 4 and len(wallets) == len(sigs)): continue
        for pair in itertools.combinations(wallets,2): pair_rows[pair][str(row.get("mint",""))] = row
    candidates = [(p,list(m.values())) for p,m in pair_rows.items() if 4 <= len(m) <= 6]
    candidates.sort(key=lambda x:h("|".join(x[0])))
    return candidates[:count]


class Cursor:
    def __init__(self, data: bytes): self.data=data; self.i=0
    def take(self,n:int)->bytes:
        if self.i+n > len(self.data): raise ValueError("TRUNCATED")
        out=self.data[self.i:self.i+n]; self.i+=n; return out
    def u8(self)->int: return self.take(1)[0]
    def bool(self)->bool:
        v=self.u8()
        if v not in (0,1): raise ValueError("INVALID_BOOL")
        return bool(v)
    def u16(self)->int: return struct.unpack("<H",self.take(2))[0]
    def u32(self)->int: return struct.unpack("<I",self.take(4))[0]
    def u64(self)->int: return struct.unpack("<Q",self.take(8))[0]
    def i64(self)->int: return struct.unpack("<q",self.take(8))[0]
    def pubkey(self)->str: return b58encode(self.take(32))
    def string(self)->str:
        n=self.u32()
        if n > 256: raise ValueError("STRING_TOO_LONG")
        return self.take(n).decode("utf-8")


def decode_trade_event(payload: bytes) -> dict[str,Any]:
    pos = payload.find(TRADE_EVENT_DISC)
    if pos < 0: raise ValueError("NO_DISCRIMINATOR")
    c=Cursor(payload[pos+8:])
    out={
        "mint":c.pubkey(),"sol_amount":c.u64(),"token_amount":c.u64(),"is_buy":c.bool(),"user":c.pubkey(),"timestamp":c.i64(),
        "virtual_sol_reserves":c.u64(),"virtual_token_reserves":c.u64(),"real_sol_reserves":c.u64(),"real_token_reserves":c.u64(),
        "fee_recipient":c.pubkey(),"fee_basis_points":c.u64(),"fee":c.u64(),"creator":c.pubkey(),"creator_fee_basis_points":c.u64(),"creator_fee":c.u64(),
        "track_volume":c.bool(),"total_unclaimed_tokens":c.u64(),"total_claimed_tokens":c.u64(),"current_sol_volume":c.u64(),"last_update_timestamp":c.i64(),
        "ix_name":c.string(),"mayhem_mode":c.bool(),"cashback_fee_basis_points":c.u64(),"cashback":c.u64(),"buyback_fee_basis_points":c.u64(),"buyback_fee":c.u64(),
    }
    n=c.u32()
    if n > 64: raise ValueError("SHAREHOLDER_VEC_TOO_LONG")
    for _ in range(n): c.pubkey(); c.u16()
    out.update({"quote_mint":c.pubkey(),"quote_amount":c.u64(),"virtual_quote_reserves":c.u64(),"real_quote_reserves":c.u64()})
    out["bytes_consumed_after_discriminator"] = c.i
    out["trailing_bytes"] = len(c.data)-c.i
    return out


def payload_candidates(tx: dict[str,Any]) -> list[tuple[str,bytes]]:
    out=[]
    for line in ((tx.get("meta") or {}).get("logMessages") or []):
        if str(line).startswith("Program data: "):
            try: out.append(("LOG_PROGRAM_DATA",base64.b64decode(str(line).split("Program data: ",1)[1])))
            except Exception: pass
    msg=((tx.get("transaction") or {}).get("message") or {})
    instrs=list(msg.get("instructions") or [])
    for group in ((tx.get("meta") or {}).get("innerInstructions") or []): instrs.extend(group.get("instructions") or [])
    for ins in instrs:
        if isinstance(ins,dict) and isinstance(ins.get("data"),str):
            try: out.append(("INSTRUCTION_BASE58",b58decode(ins["data"])))
            except Exception: pass
    return out


def trade_events(tx: dict[str,Any]) -> list[tuple[str,dict[str,Any]]]:
    found=[]; seen=set()
    for source,payload in payload_candidates(tx):
        if TRADE_EVENT_DISC not in payload: continue
        try: event=decode_trade_event(payload)
        except Exception: continue
        key=(event["mint"],event["user"],event["timestamp"],event["token_amount"],event["quote_amount"],event["is_buy"])
        if key not in seen: seen.add(key); found.append((source,event))
    return found


def main()->None:
    ap=argparse.ArgumentParser(); ap.add_argument("--zip",required=True); ap.add_argument("--out",required=True); ap.add_argument("--pairs",type=int,default=2); ap.add_argument("--sleep-seconds",type=float,default=2.2); ap.add_argument("--rpc-url",default="https://api.mainnet-beta.solana.com"); args=ap.parse_args()
    with zipfile.ZipFile(args.zip) as zf: intra=list(rows(zf,member_by_basename(zf,"sniper_cohorts_intra.jsonl.gz")))
    pairs=choose_pairs(intra,args.pairs)
    # Qualification rows (third) plus all later compact hits are enough for entry-decode feasibility.
    target_rows=[]
    for pair,rs in pairs:
        rs=sorted(rs,key=lambda r:int(r.get("detected_at") or 0))
        for row in rs[2:]: target_rows.append((pair,row))
    sigs=[]; seen=set()
    for _,row in target_rows:
        for sig in row.get("tx_sigs") or []:
            sig=str(sig)
            if sig not in seen: seen.add(sig); sigs.append(sig)
    txs={}; statuses=collections.Counter()
    for i,sig in enumerate(sigs):
        st,tx=rpc_get_tx(args.rpc_url,sig); statuses[st]+=1
        if tx is not None: txs[sig]=tx
        if i+1<len(sigs): time.sleep(args.sleep_seconds)

    row_results=[]; decoded_events=0; exact_mint_events=0; exact_user_events=0; decoded_buys=0; decoded_sells=0; source_counts=collections.Counter()
    for pair,row in target_rows:
        wallets=[str(x) for x in row.get("wallets") or []]; row_sigs=[str(x) for x in row.get("tx_sigs") or []]; mint=str(row.get("mint","")); mapping=max_matching(wallets,row_sigs,txs)
        pair_decodes=[]
        for w in pair:
            sig=mapping.get(w); tx=txs.get(sig) if sig else None
            matches=[]
            if tx:
                for source,event in trade_events(tx):
                    decoded_events+=1; source_counts[source]+=1
                    mint_ok=event["mint"]==mint; user_ok=event["user"]==w
                    exact_mint_events+=int(mint_ok); exact_user_events+=int(mint_ok and user_ok); decoded_buys+=int(event["is_buy"]); decoded_sells+=int(not event["is_buy"])
                    if mint_ok and user_ok:
                        matches.append({
                            "source":source,"is_buy":event["is_buy"],"timestamp":event["timestamp"],"quote_amount_raw":event["quote_amount"],"token_amount_raw":event["token_amount"],
                            "real_quote_reserves_raw":event["real_quote_reserves"],"real_token_reserves_raw":event["real_token_reserves"],"virtual_quote_reserves_raw":event["virtual_quote_reserves"],"virtual_token_reserves_raw":event["virtual_token_reserves"],
                            "ix_name":event["ix_name"],"trailing_bytes":event["trailing_bytes"]
                        })
            pair_decodes.append({"wallet_sha256":h(w),"mapped_signature_present":bool(sig),"exact_trade_events":matches})
        row_results.append({"mint_sha256":h(mint),"released_detected_at":row.get("detected_at"),"pair_identity_sha256":h("|".join(pair)),"pair_wallet_decode":pair_decodes,"raw_identifiers_logged":False})

    result={
        "experiment":"RED_PUMP_TRADE_EVENT_DECODE_FEASIBILITY_v1",
        "source":"RED-COHORT-2026-v1.1.1",
        "historical_protocol_schema":{"pump_idl_commit":PUMP_IDL_ASOF_COMMIT,"commit_date_utc":PUMP_IDL_ASOF_DATE_UTC,"selection_reason":"latest official pump.json commit before RED observation window began 2026-06-11","trade_event_discriminator":list(TRADE_EVENT_DISC),"schema_scope":"TradeEvent through real_quote_reserves as published at that commit"},
        "rpc":{"status_counts":dict(sorted(statuses.items())),"transactions_resolved":len(txs)},
        "decode":{"trade_events_decoded":decoded_events,"events_matching_target_mint":exact_mint_events,"events_matching_target_mint_and_pair_wallet":exact_user_events,"decoded_buy_events":decoded_buys,"decoded_sell_events":decoded_sells,"source_counts":dict(source_counts)},
        "rows":row_results,
        "verdict":{"entry_execution_reconstruction":"SUPPORTED" if exact_user_events else "NOT_YET_SUPPORTED","next_if_supported":"use exact historical TradeEvent quote/token amounts and reserve state as entry anchor; then enumerate post-entry mint transactions and decode subsequent buy/sell events for sellability-aware MFE/MAE and exit-capacity feasibility","chart_only_outcome_is_sufficient":False,"historical_idl_version_pinning_required":True},
        "authority":{"research_only":True,"automatic_trading":False,"buy_now_promotion":False,"live_threshold_change":False}
    }
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2,sort_keys=True)); print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__": main()

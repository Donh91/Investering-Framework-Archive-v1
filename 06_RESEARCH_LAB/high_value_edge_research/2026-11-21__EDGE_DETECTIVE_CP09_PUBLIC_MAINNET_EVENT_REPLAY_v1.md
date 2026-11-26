# EDGE DETECTIVE CP09 | Independent public Solana Explorer event replay

**Date:** 2026-11-21 Europe/Copenhagen. **Authority:** PUBLIC_RESEARCH_ONLY. **Classification:** EXPLORER_RENDERED_ONCHAIN_EVENT_REPLAY, NOT original raw JSON-RPC byte attestation, NOT first-known signal, NOT quote-capacity or trading edge. **Scope:** two publicly selected, previously known PumpSwap mainnet transactions. Selection is not random, exhaustive or prospective. No user-owned wallets, private positions, API keys, signer, public source feed, paid RPC or new autonomous agent.

## 1. Independent source and exact version

- Primary deployed-program schema reference: `pump-fun/pump-public-docs` at exact commit `bc35796152027d2744ca02066d305438e34b67e7`, `idl/pump_amm.json` Git blob `d907b16a91f035aeb3c3182bfa0972a91bf23a86`. PumpSwap program ID: `pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA`. Official `SellEvent` discriminator `[62,47,55,10,165,3,220,42]`; official `BuyEvent` discriminator `[103,244,82,31,44,245,119,119]`. These IDL definitions are a **current pinned source snapshot**, not independent on-chain program-upgrade history across previous slots.
- Independent **public on-chain explorer**, not the earlier decoder/fixtures: Solana Explorer transaction pages below. A JavaScript-capable, read-only web extraction displayed finalized status, exact transaction signature, slot and nested PumpSwap `SellV2` instructions including raw `Program data: <base64>` event log. No direct `getTransaction` raw JSON-RPC envelope hash was captured. Therefore call this `EXPLORER_EVENT_REPLAY`, not `RPC_NATIVE_READBACK`.
- Parser used by the investigation **did not consume the third-party project's decoded expected output**: it decoded each Explorer-rendered raw base64 event as an 8-byte official discriminator followed by the pinned IDL's ordered Borsh `i64/u64/i128/bool/pubkey` fields, plus length-prefixed string for `BuyEvent.ix_name`. Values were accumulated as **arbitrary precision signed or unsigned integers**, not JavaScript Number. A complete decode required the cursor to consume **all** bytes, without trailing fields. No new binary decoder was deployed to Alpha production.
- Adversarial comparator, only **after** the independent extraction: public Apache-2.0 source `Charliewytk/pumpswap-decode@14cb8e54d63a21d1386069c7f487832742718072` with exact public Git fixture blobs `a2e36b0c1b5f3bee825d5b3a1fe14ff7a6d4d63a` and `88eb3650a00a9bcbfed32c9e33b926bf4562c1bf`.

## 2. Transaction A: independently decoded completed SellV2

Public Explorer transaction:
https://explorer.solana.com/tx/2VStUexLU9anazTAnRweUN5Qznaktrub5asALf43htoVVThqBgDabaAqZj9qGimXQELDeKJ8itWHrfEYuZwsyJqX

- **Finalized and success**, slot **455293193**, event timestamp `1791643513` (2026-10-10 14:45:13 UTC).
- PumpSwap `SellEvent` discriminator matched official IDL; **441 of 441 bytes** consumed by full, independent Borsh event decode.
- Exact raw pool quote reserve `173987909809`, exact **signed** virtual quote reserve `-1156939`. Effective quote reserve **`173986752870` raw quote units**, not the whole vault balance.
- Base input `15051941279` raw token units. Gross quote amount `20341526` raw units. User quote out **`20097426` raw units**, matching the independently displayed **0.020097426 WSOL transferred** from pool-side token accounts to the trader's transaction-side quote account in the Explorer page.
- Event components: LP fee `40684`, protocol fee `10171`, creator fee `193245`, and buyback fee `5085` as **protocol-fee subcomponent**, not a second independent fee. Arithmetic **`20341526 - 40684 - 10171 - 193245 = 20097426`** exactly. Do not double charge buyback fee.
- These original event+token-transfer facts corroborate the previously published fixture numbers for one **actually executed historical swap**. They do **not** establish that an Alpha bot could have identified the opportunity before decision time or replicated that quote at a larger notional.

## 3. Transaction B: independent signed-reserve and large-u64 check

Public Explorer transaction:
https://explorer.solana.com/tx/3EGHPVsAWWGPEjjqYq6zT4aYUWV438RBUE2zSGAU9DkvwPZXVZichYPsJMsSiKSXdJ27gTvF267tsxsYZpKWQwcN

- Explorer status **finalized**, slot **455287607**; two separate raw PumpSwap program-data events recognized with the exact official `SellEvent` and `BuyEvent` discriminators, **441/441** and **489/489** bytes consumed.
- **Sell leg**, quote reserve before trade: `76183860355337791`; signed virtual `-153587008`; effective `76183860201750783`. Base input `5294492710`, gross quote out `622052027550240`, user quote out `620185871467588`, all in exact raw asset units.
- **Buy leg**, quote reserve before trade: `75563363457856427`; signed virtual `-153587008`; effective `75563363304269419`. Base output `7889103455`, gross quote in `930667566197985`, user quote in `933459568896579`, all in exact raw asset units.
- Both quote reserves are **larger than** JavaScript `Number.MAX_SAFE_INTEGER = 9007199254740991`. Coercing RPC raw u64s through ordinary `Number` can round them **before** model or storage checks. Original exact binary/log bytes or raw decimal strings are needed, and the current pure Alpha helper rejects floats. An apparently close displayed value is not byte-level economic parity.
- Each event is a separate BUY/SELL leg within a real transaction. Do NOT interpret it as one trader's reusable strategy return, as an independent sequence of two new participants, or as a baseline for `$100/$500/$1000` quote capacity. The two event states must not be assigned one common reserve snapshot.

## 4. Evidence ladder and remaining blockers

| Gate | Result | What would be required to advance |
| --- | --- | --- |
| Pinned **official** IDL event layout and exact discriminator | **PASS, at inspected schema snapshot** | On-chain program upgrade/IDL history at the transaction slot for original protocol-era certification |
| Independent public Explorer **signature/slot/finality and raw-event parsing** | **PASS for two selected transactions** | Store separately verified read-only RPC request-response envelope SHA-256, independently reconciled slot/blockhash and event-index path |
| Exact integer fee and reserve arithmetic | **PASS for observed event values** | Contract-version and quote-path match for prospective source cohort and full execution route |
| First-known timely complete Solana mint/curve/pool census | **NOT TESTED** | Existing original MAL #194/#126 source admission, natural contiguous source intervals and signed/hashed first-observed clock |
| Prospective full-size buy **and full sell** including failures at $100/$500/$1k | **NOT TESTED** | Existing original #98 source-matched two-way quote / route receipts and all missing/nonfilled cases |
| Incremental risk-filter or strategy edge after costs vs simple controls | **NOT IDENTIFIABLE** | Existing original #77/#85 matured all-candidate outcomes and sacrificed sellable winners |
| Live model/portfolio/trading permission | **NEVER AUTHORIZED** | Separate future owner/security release, not supplied by this checkpoint |

**Negative transport receipts:** initial Solscan and official Explorer text extractors returned loading/page metadata, and SolanaFM GET endpoints returned three HTTP 502s. A later JavaScript-capable public Explorer extraction succeeded and exposed raw `Program data` logs. This distinction matters: transport failure was **not** evidence of missing on-chain transactions, and the successful Explorer event bytes still do **not** create an original RPC provenance hash or historical first-known receipt.

**Precise scientific disposition:** `EXPLORER_CONFIRMED_TWO_SELECTED_REAL_SWAP_EVENTS`; `SIGNED_QUOTE_ARITHMETIC_AND_U64_EXACTNESS_REPRODUCED`; `NO_SOLANA_FULL_POPULATION`; `NO_FIRST_KNOWN_MACHINE_CLOCK`; `NO_CAPACITY_PNL_OR_TRADING_EDGE`.

## 5. Machine learning and original-owner routing

This is new **source reliability / execution mechanics intelligence**, not a speculative asset recommendation. The prior merged Alpha implementation is now: PR #297 `201c96f624ef36de48a2dd24317aa92d3f06e921`, PR #298 `d08a57886433347d49a9f389238a80069d190049`, PR #299 `e35db60bd13d995a9b139eddbdf2c1ac04940efd`, with **49 offline Pump parity test methods** and the existing native V4 CI. They improve correctness but do not automatically consume these two Explorer events or enable a Solana feed.

Route the next *single* bounded, read-only, no-schedule source study to **MAL #194/#126** under existing **Archive #1512**: a first-party RPC request-response/slot witness with raw JSON digit integrity and program-era discriminator check, then source completeness/first-known, followed only afterward by original **#98** two-way exit capability and **#77/#85** matured outcomes. No duplicated scanner, no new Research Lab agent, paid provider, live orders, or external market maker. Maintain the archived source and negative cases even if live PnL tests eventually fail.

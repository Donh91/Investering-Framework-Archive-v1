# ADYROS SDK | Open-source specialist dissection and Alpha Lab transfer

**Source snapshot:** 2026-11-07; external `ADYROS/adyros-sdk` **main commit** `c6a89b853f7e6266a083e8e1c6aaffdcb0b9d343`  
**Authority:** RESEARCH_ONLY / SHADOW / NO_TRADE / NO_SIGNING / NO_NEW_ENGINE  
**Intake owner:** [Framework Research Lab #1512](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1512)  
**Original operational owners:** Meme-Alpha-Lab #126 (user-submitted CA, intake), #194/#98 (CA identity/market execution), #88 (wallet/distribution), #77/#85 (outcomes/cohorts), existing Case Memory and S1.  
**Method:** `architecture/EXTERNAL_SPECIALIST_DISSECTION_V1.md` in Meme-Alpha-Lab.  
**Discipline:** Do not increase active specialist queue priority, create a new scanner, or replace original evidence writers. This report is a research source, not a canonical rule promotion or LIVE feature.

## Executive decision

**METHOD_ONLY_TRANSFER + DEDUPED_TO_EXISTING_OWNER.** Source code is openly reusable under MIT, but direct runtime integration is NOT approved. Meaningfully useful concepts: (1) offline preflight risk checks of external agent skills, (2) reproducible tamper-evident event/anchor completeness testing, (3) explicit transaction-policy denial as an adversarial negative test. Alpha Lab already implements stronger native event continuity and has separate original safety/authority controls. Hosted Adyros platform claims are not established by its client SDK.

**"How much can be taken?"** 3 small concepts / selected utilities can be borrowed or reimplemented; zero reasons today to import all of `adyros`, use Adyros cloud wallets, pay x402 fees, add a second scanner, or connect live token trading. Copying copyrightable source is legally permitted *subject to* preserving MIT copyright and permission notices in copies/substantial portions, plus dependency and security checks; citing/adapting algorithms and test patterns needs the same source provenance discipline.

## Verifiable external source inventory

| Public source | Actual content | Research relevance and disposition |
| --- | --- | --- |
| [`src/scanner/rules.ts`](https://github.com/ADYROS/adyros-sdk/blob/c6a89b853f7e6266a083e8e1c6aaffdcb0b9d343/src/scanner/rules.ts) and [`src/scanner/scan.ts`](https://github.com/ADYROS/adyros-sdk/blob/c6a89b853f7e6266a083e8e1c6aaffdcb0b9d343/src/scanner/scan.ts) | Static regex rules for secrets, malicious remote code, exfiltration, risky approvals, injected instructions, obfuscation, persistence; output file/line finding IDs and three-state verdict | **P2 optional, method transfer**: inspect agent skills before use. It does **not** scan token smart-contract risk, liquidity or honeypots. |
| [`src/cli.ts`](https://github.com/ADYROS/adyros-sdk/blob/c6a89b853f7e6266a083e8e1c6aaffdcb0b9d343/src/cli.ts) | Offline CLI, JSON output, exit 2=blocked, 1=review, 0=clean; traverses local directory with content filters | **P2 optional**: deterministic CI preflight pattern; do not blindly install or run on secrets-bearing directories. |
| [`src/proof-hash.ts`](https://github.com/ADYROS/adyros-sdk/blob/c6a89b853f7e6266a083e8e1c6aaffdcb0b9d343/src/proof-hash.ts) and [`src/proof.ts`](https://github.com/ADYROS/adyros-sdk/blob/c6a89b853f7e6266a083e8e1c6aaffdcb0b9d343/src/proof.ts) | Canonical JSON encoding, SHA256 linked events, Merkle root, optional Base transaction-input anchor check | **Research challenger only**: test evidence-completeness failure modes against existing receipt policies. Do not replace native Case Memory. |
| [`src/index.ts`](https://github.com/ADYROS/adyros-sdk/blob/c6a89b853f7e6266a083e8e1c6aaffdcb0b9d343/src/index.ts) | Client wrapper for hosted `/log`, `/wallet`, `/wallet/send`, agent-check APIs | **No integration**: server wallet guard and remote auditability are not proved by client code. |
| [`src/x402.ts`](https://github.com/ADYROS/adyros-sdk/blob/c6a89b853f7e6266a083e8e1c6aaffdcb0b9d343/src/x402.ts) | USDC Base EIP-3009 signed authorization payment after HTTP 402 and client-configured maximum | **Reject for current Alpha Lab**: payment and signing conflict with research-only authority and add funding/secret risk. |
| [`src/demo.ts`](https://github.com/ADYROS/adyros-sdk/blob/c6a89b853f7e6266a083e8e1c6aaffdcb0b9d343/src/demo.ts) | Example deliberately attempts unlimited token approval as negative test | **Method-only**: safe controlled refusal testing, NEVER actual money or production wallet sends. |
| [`test/scanner.test.mjs`](https://github.com/ADYROS/adyros-sdk/blob/c6a89b853f7e6266a083e8e1c6aaffdcb0b9d343/test/scanner.test.mjs), [`test/proof.test.mjs`](https://github.com/ADYROS/adyros-sdk/blob/c6a89b853f7e6266a083e8e1c6aaffdcb0b9d343/test/proof.test.mjs), [`test/x402.test.mjs`](https://github.com/ADYROS/adyros-sdk/blob/c6a89b853f7e6266a083e8e1c6aaffdcb0b9d343/test/x402.test.mjs) | Local unit tests for scripted malicious/benign samples, hashes and payment signatures | Tests exist, but do not measure real-world detector sensitivity, live wallet security, or independent product adoption. |
| [`LICENSE`](https://github.com/ADYROS/adyros-sdk/blob/c6a89b853f7e6266a083e8e1c6aaffdcb0b9d343/LICENSE) | MIT copyright 2026 Adyros | Keep copyright and license text if copying substantial code. |

External latest examined CI on source commit: [run 42250977772](https://github.com/ADYROS/adyros-sdk/actions/runs/42250977772) reported SUCCESS. That confirms its configured CI, not an external audit of the hosted product.

## Source-level red-team findings, with confidence bounds

1. **Scanner scope and false negatives.** `scanSkill` evaluates at most the first 2,000 characters of each line for pattern matches; the CLI skips eligible files >400 KB and traversal stops at 2,000 collected files. Heuristics operate line-by-line, without documented AST/interprocedural flow analysis. `clean` is NOT an independent proof of safety. **VERIFIED_CODE_FACT / risk inference**.
2. **Potential reporting exposure.** Scanner findings include up to 220 characters of the matching source line, and JSON output includes snippets. If the input itself contains credentials, retaining scan results without redaction could leak material. Require redacted logs, local-only execution, fixture tests and refusal to scan sensitive directories. **CODE_FACT + HYPOTHESIS**.
3. **Partial hash-chain verification.** External `verifyChain` sorts by sequence and verifies each entry hash and previous hash against preceding returned event; it does not explicitly assert genesis, first sequence number, strictly adjacent sequence increments, exact machine identity or an expected total. A valid *partial subset* must not be interpreted as a proven complete stream. **VERIFIED_CODE_FACT**.
4. **Anchor unavailability.** External `verifyProof` exposes `onchainMatches:null` for unavailable blockchain transaction lookup; its CLI only exits nonzero on explicit false anchors/root mismatches, not unknown. No independently verified completeness/availability proof emerges from this state. **VERIFIED_CODE_FACT**.
5. **Guard behavior cannot be inferred from the demo.** Demo tests a dangerous unlimited approval, but on unexpected success it prints a warning rather than failing the run. Real hosted enforcement is opaque from this SDK. **VERIFIED_CODE_FACT**.
6. **External payment recipient/data.** x402 signs an EIP-3009 authorization against the recipient supplied in a payment challenge, subject to an amount cap. The helper itself does not establish an Alpha Lab-approved payee list. This is not suitable to import into a no-signing, no-trading system. **VERIFIED_CODE_FACT**.
7. **Commercial claims are separate evidence.** The repo proves real public source commits and a release; does not prove hosted safety, audited deployments, paying users, useful token economics, independent adoption or token investment upside. **LIMITATION**.

## Critical overlap audit against our code

The existing Meme-Alpha-Lab `scripts/case_memory_v1.py` `rebuild_data()` already asserts `sequence == n` starting at 1, the prior hash, content hash and exact case identity. `verify()` checks derivative case index and continuity capsule. Existing source admission, privacy and DVL contracts are stronger/more specific for token research than a vendor's general-purpose log client. **DO NOT import `verifyChain` or reduce current invariants.**

Agent-skill screening is NOT the same thing as token CA security, Uniswap sellability or holder/cluster forensics. The words "skill score", "security score" and "alpha score" must never be conflated.

## One bounded reproducible experiment, ONLY when an original owner finds a real gap

**Hypothesis:** A stricter completeness gate outperforms vendor-style *valid subset* verification in detecting truncated/partial agent-operation receipts; it should not weaken our existing Case Memory.

**Design:** Under existing evidence/receipt verifier ownership, synthesize small entirely fake data fixtures: valid complete chain, prefix deleted, middle sequence missing, wrong machine ID, modified payload, mismatched anchor, anchor missing, onchain transaction unavailable and zero-event report. Freeze expected outcomes first, compare vendor method as challenger vs unchanged existing native gate. Zero real keys and zero external production wallet calls. Preserve agreement/disagreement and false-positive rows.

**Promotion condition:** Only if the existing native verifier demonstrably misclassifies at least one material case *and* a minimal owner-bound patch passes regression, independently reviewed release requirements and true main readback. If native tests already fail closed, outcome `DUPLICATE_NO_ACTION`. No inference of investment/trading edge from security tests.

**Separate OPTIONAL P2 study:** After P0 source, sellability and privacy work, test offline vendor skill rules against curated malicious/benign skills and an independent open-source scanner on the exact same frozen inputs. Define recall, false-positive rate, evasions, speed and source exposure. If rules are inferior or duplicate existing coverage, reject. No extra cron/API costs.

## Investor / meme-swing interpretation of the associated ADYROS token

**Do not confuse software development with profitable token entry.** A legitimate developer repository is only a qualitative project-continuity signal. Alpha Lab CA intake must separately test early price/flow dynamics, 1-3d realizable exits for $100/$500/$1,000, first-N buyer retention, holder independence, sniper sell overhang, launch/LP/hook control, exact product->token value capture, original machine first-known vs owner submission, and source-frozen +15m/+1h/+6h/+24h/+72h/+7d outcomes. If a hard gate is unknown, do not imply a BUY. The original source family and scanner eligible denominator must be confirmed, never inferred by GitHub filename search.

**Known prior contextual snapshot, not a new live read:** Robinhood Chain token `0x8c8378a6a7dea5d0c37ab12aced6682a3bc0919f` was previously observed in DexScreener/GeckoTerminal at roughly USD 40k FDV, USD 17.5k principal pool liquidity; Blockscout around 250 holders; independent provider reported ~10.74% first-10-block sniper supply. These metrics are volatile and **must be refetched** before any current entry/exit judgment. External scanner's LOW risk / 95 score is neither our sellability proof nor a risk-adjusted alpha score.

**Existing routing:** #126 original CA intake/scanner recall, #194/#98 exact token/route safety, #88 sniper/distribution, #77/#85 frozen outcome, #1512 specialist knowledge, no new owners.

## Reusable evaluation conclusion template for all user-submitted meme/microcap CA cases

Separate (A) PROJECT QUALITY, (B) INVESTMENT THESIS 3-12m, and (C) SWING TRADE QUALITY 1-3d. An attractive trade can be an otherwise low-quality project; strong code can belong to an illiquid and overpriced token.

Required:
- Exact chain+CA and source clocks/coverage; scanner first-known versus user-submitted first-known.
- Microstructure snapshot, eligible buyer retention and velocity, top-wallet and sniper distributions, LP/hook/owner, two-sided feasible exit $100/$500/$1,000, fee/slippage and liquidity stress.
- Catalysts: independently timed product release/social promotion/holder growth against volume and liquidity, not price screenshot.
- Bull/base/bear *conditional* paths, entry triggers, invalidation and exit plans, separated from automatic execution.
- Frozen forward outcomes and matched losers, with all UNKNOWN conditions preserved.
- End with dual **preliminary** Alpha Scores (1–3d, 3–12m) and exact scanner receipt classification, **not** an arbitrary uncalibrated risk percentage mislabeled as model.

No immediate architecture/code change is justified by the external SDK. Any later adoption must follow existing Strategist disposition and owner PR+CI+main-readback.

## Case classification and receipts

- `SOURCE_REVIEWED`: external repo public code + license + GitHub Actions success at source commit.
- `METHOD_ONLY_TRANSFER`: scanner preflight patterns; hash anchor completeness; refusal negative tests.
- `NOT_IMPLEMENTED`: no vendor SDK dependency, no scanner run in Framework, no hosted product test, no credential permission, no trade.
- `CASE_MEMORY_PERSISTENCE_PENDING`: this research document / GitHub issue is **not** the canonical token Case Memory append-only event.
- **Next action:** original owner checks any evidence-completeness regression first; otherwise archive as `DUPLICATE_NO_ACTION`, retain public source references for future targeted reuse.

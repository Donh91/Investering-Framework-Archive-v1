# Paired autotrading research archive

Owner-authorized 2026-10-24. This is the existing Research Lab's document layout, not a new queue, runtime or trading authority. Governing [AUTO_TRADING policy](../GOVERNANCE.md) and [Bridge handoff agreement](../source_notes/2026-10-24__grok_bridge_research_intake_and_pr65_adjudication.md) remain binding.

## Three distinct voices in one packet

Each packet has a stable ID and README source binding. Use these tracks:

- `grok/`: original public-safe Grok report, or clearly labelled edited public extract when the original is private. Keep original immutable at its exact Bridge head/path/blob. Never attribute ChatGPT edits or tests to Grok.
- `chatgpt_reviews/`: dated, append-only ChatGPT adjudications of named Grok/source versions. State ACCEPT/ADAPT/DEFER/REJECT, strongest objection, public source evidence, actual tests vs reported tests, open questions and finite next step. Later reviews link and supersede earlier conclusions without rewriting them.
- `chatgpt_research/`: only actual separately scoped ChatGPT research/results. Link the motivating Grok claim and preregistered question, method, data/source clocks, controls, negative results, cost and limitations. Do not present review reasoning as a completed experiment. Create this track only when such research exists.
- Future `external_reviews/`: source-pinned owner-delivered Claude/other review, distinguished from both primary research and ChatGPT adjudication. The archive is public for review; no external model is dispatched or purchased by these files.

## Delivery without forgotten backlog

Grok submits via the existing private Bridge report path/PR. Existing S1 takes materially new packets through source check -> content adjudication -> privacy-cleared archive PR -> main/blob readback -> feedback on the original Bridge PR. The original Bridge PR is the existing pending handoff until archive verification; do not close it merely because it has been seen. If blocked, retain exact missing gate and owner there. No second ledger, scanner, task or provider routine.

Dedupe by original artifact ID, exact source version and substantive digest. A date/head-only change is not new research. Valid statuses: RECEIVED, NEEDS_SOURCE, REVIEWED, ARCHIVED, DEFERRED, REJECTED. These are document dispositions, not dispatch or scientific acceptance. ARCHIVED requires actual main paths/blob receipts for both research and review. A report may be archived with rejected conclusions; retain negative evidence.

Originals with restricted Alpha/provider/proprietary material remain private. Public extracts enumerate withheld categories and are never called verbatim full reports. Public-safe complete originals may be copied verbatim with hashes. No keys, wallet data, raw restricted values or unauthorized private findings.

## Current packets

- [AT-GROK-20261024-001: RUN-002 gap research](AT-GROK-20261024-001/README.md) — original private source + public extract + separate ChatGPT adjudication. No ChatGPT experiment or external review is claimed.
- [AT-GROK-20261025-002: CN miss / NO_TRADE target-EV constraints](AT-GROK-20261025-002/README.md) — private Bridge PR #67 bound to a sanitized Grok extract and separate ChatGPT review; no experiment or external review is claimed.
- [AT-GROK-20261024-002: frozen Compass source / NO_TRADE inventory](AT-GROK-20261024-002/README.md) — Bridge PR #66, historical Compass snapshot, separate review; source-input limitations retained.
- [AT-GROK-20261023-002: edge-completion and matched-baseline falsifier](AT-GROK-20261023-002/README.md) — Bridge PR #63 and its prior ChatGPT companion; the un-reproduced B1 number remains rejected.

## Toward a future app

Later synthesis may compare multiple packets, contradictions and failed hypotheses and propose an application specification. Keep evidence ladder, baseline/after-cost/PIT controls, trial denominator and stage gates. Building/deploying a paper/live executor, venue access, orders, signing, credentials, capital and paid tools require their separate explicit qualified scope. This archive does not prejudge the provider/model/builder or hire a premium service.

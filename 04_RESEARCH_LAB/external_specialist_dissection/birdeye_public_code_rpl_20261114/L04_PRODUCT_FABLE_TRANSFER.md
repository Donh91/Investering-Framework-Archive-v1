# L04 | Product, agent runtime and Fable implementation boundary
Question: Which technical patterns improve Alpha Lab Pro research reliability without a new agent, model, scanner or provider dependency?
Original owner MAL #228, existing 26-milestone handoff/ALPHA_LAB_PRO_PROGRAM_ORDER_V1.json; original Research Lab #1512 and Strategist #1157.

Birdeye CLI source transfer:
- Chain-specific skills, explicit scopes and failure modes; UI/report JSON can render MISSING, page-limited results, provenance and source as-of rather than synthetic live confidence.
- Source planner estimates bounded request count and compute units before calls; source executor emits explicit missing steps. API retry cost is uncertain and MCP charge cannot be bounded by generic CU estimate. Existing Alpha audit-to-evidence skill owns research dispatch; no new Fable/Birdeye agent runner or paid calls.
- Page truncation and privacy are product features: show cohort N, N eligible, observed page cap, unresolved and timestamp availability. Proof Desk must show source truth before score or pretty design.
- UI states distinct: project integrity, executable 1–3d trade, durable 3–12m conviction. Never imply a smart-money wallet 'copy ROI' from current top trader ranking.

Proposed small original-owner tasks:
(1) D3 original #120/#194 source: first-known completeness and exact chain/token/pool identity; preserve Pons/Torch and invalid-source abstention.
(2) D3 original #98: same-asof full exit economic quote checks; no positive paper outcome without both sides.
(3) D4 original #88/#77/#85: wallet candidate + paper strategy cohort measured on common bankroll, no correlated multiple full bankroll wins.
(4) D5 original #22/#228: present source-health and falsifier receipts, not free-form AI chatter or a fictional live signal.

Fable handoff rule:
FABLE_5_2_PACKAGE_v1.0_FROZEN at Bridge blob 435b8385a3d2c1d98ddde07e41d25270e7e10e2b is a narrow Kompas daily-source-staleness/weekly-protection AUDIT-04b review; optional 10-min Alpha appendix only. Do NOT amend or reinterpret it as a full Alpha mission.
Future independent Alpha/Fable work must reuse existing original FABLE_ROADMAP Round9 / NOTE_TRADING_BOT E0-E3, after current Fable/CN work and separate owner authorization, and use original #228 and native model usage receipts. This packet is PREPARATION, not an API trigger or Fable run.

No live code change or model invocation. Source audit proved fields and failure classes, not production readiness. A lower-priority Birdeye UI polish cannot outrank source first-known, privacy, realistic exit, due outcome and public site release gates.

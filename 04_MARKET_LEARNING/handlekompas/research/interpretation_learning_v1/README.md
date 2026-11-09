# KIL v1.0, Kompas Interpretation Learning

Status: **OWNER APPROVED 2026-11-09. Research-only pilot, 56 days from first main publication.**
Original owners: [Kompas Pro #1516](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1516), [Task 2 #1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596), [Risk-to-Action #1553](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1553).

## Purpose and honest first-stage scope

The requested long-term goal is a 72-hour evaluation of **what Kompas said, what actually happened, whether its explanation was sound, and whether waiting or acting had value**.

Stage 1 implements the safe measurement foundation using existing official original issuances and existing official 72h outcomes. It does **not** pretend to capture or score the assistant's freeform chat interpretation; on-demand chat text has no automatic bridge to the repository. Until a prospective, privacy-reviewed chat-analyst receipt owner exists, **assistant narrative hit rate, turning-point understanding, timing precision, investor PnL, and economic edge are all UNAVAILABLE**. The official 12h NOWCAST is explicitly excluded from forecast scoring.

## Operating contract

- No second supervisor, no new model/collector/scheduled workflow, no new LLM API or paid task.
- Existing `.github/workflows/compass-outcomes.yml` invokes the optional KIL step during ordinary hourly due-only maturity after Official/Strategic/Shadow outcomes. Any KIL failure is isolated from official outcome publication.
- Source: current `official/LATEST_COMPASS.json` to immutable original `official/daily/.../CMP-*.json`. Validate contract, ID, self-hash, pointer, issue clock, UTC source/reference clock, first Git add timestamp, activation, original age (max 6h) and same Copenhagen calendar day. Register **at most one original official issuance per local day**, selected by the first eligible scheduled run. No retroactive case recruitment.
- Activation comes from the first main commit adding the KIL script, not a backdated fixed date. The first Git-add timestamp is only a repository custody clock, **not independent exchange/provider first knowledge**.
- Freeze one append-only registration with original 72h direction, expected-path prose, risk/action labels, source SHA and issue/reference/target timestamps. Preserve official forecast and action authority unchanged.
- After the exact 72h original target, require the *existing* immutable Official v3 outcome sidecar, valid digest and owner, target equality, coherent maturation clocks and time-basis PASS before writing one append-only research review. **Do not rescore Official, create a target from hindsight, or misrepresent BTC/ETH dependent outcomes as independent.**
- Every third Copenhagen day, beginning after activation and no earlier than local noon, publish one append-only 14-day **descriptive** synthesis with observation/abstention counts, nonoverlapping 72h window count, hashes and explicit lack of proven incremental edge. Reports are a cadence, not a model-training mechanism.
- Outputs live under this directory in `registrations/`, `outcomes/`, `reports/`; no overwrite, no private holdings or chat transcripts.
- Fail closed: invalid, late, absent, degraded, or unverified evidence must not count as successes. Research writer is optional; core official maturity writer retains precedence.
- 8-week review gate: examine prospective sample size, nonoverlap, source first-known/issuance, persistence and always-WAIT baselines, BTC/ETH correlations, M6 warning lead/lag, missed rebounds, after-cost investor utility, 6h/24h availability, and human analyst narrative capture before deciding promotion. No auto promotion, reweighting, trade permission, or public site score.

## Next governed extension, not implemented by this stage

Add a **separately authorized, point-in-time, structured assistant-interpretation receipt** from the existing Kompas product/original AI owner at analysis time. It should freeze a typed thesis, expected sequence, price ranges only when genuinely issued, horizon, falsifier, confidence quality, evidence versions, optional challenger, and actual delivery/first-known. It must exclude raw conversations, holdings, private credentials and text written after the event. Then pair independently at +6h/+24h/+72h under Task 2 measurement control and objectively compare with a preregistered price-momentum/persistence baseline. Absent that receipt, qualitative scoring remains NOT_EVALUABLE.

## Verification

`python -m unittest tests.learning.test_kompas_interpretation_learning_v1 -v`

`python scripts/learning/kompas_interpretation_learning_v1.py --dry-run`

The script writes no files when `--dry-run` is used. The first production run may legitimately report NOT_PROSPECTIVE_ELIGIBLE, and the first due report may contain zero outcomes. Neither is a failure.

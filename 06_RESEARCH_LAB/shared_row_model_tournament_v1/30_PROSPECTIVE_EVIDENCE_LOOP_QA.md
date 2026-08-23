# Prospective Evidence Loop QA

- Market transforms in automation code: **NONE**. Transform semantics live only in frozen family contracts.
- Candidate decisions invented by controller: **NO**. Controller accepts only precomputed decisions for candidates whose required family freeze records are READY.
- Missing -> zero: **FORBIDDEN**.
- Backdated decisions: **FORBIDDEN**.
- Outcome semantics invented by maturation job: **NO**. Maturation copies only outcomes already registered on the shared row.
- Full Stack special disadvantage: **NO**. It remains eligible when its row-time family/version map and decision contract become reproducible.
- Tail-error reporting: scaffolded in weekly report, remains `UNAVAILABLE` until matured numeric divergence evidence exists.
- Canonical writes: **NONE**.
- Paid calls introduced: **0**.

The loop is operational in `COLLECTING` mode even while core transforms are unresolved. This is intentional: weekly automation must report what is missing rather than fabricate eligibility.

## Independent Work audit containment, 2026-08-23

The earlier operational QA statement is superseded for eligibility purposes by an independent adversarial audit of current `main`. The audit verdict is `ARCHITECTURAL_RISK`. It registered 43 reproducible failure modes and found that the green synthetic gate did not cover production owner schemas, same-cutoff enforcement, exact core coverage, immutable row-time outcomes or reachable governance gates.

Audit package identity:

```text
package: PROSPECTIVE_EVIDENCE_AUTONOMOUS_GOVERNANCE_AUDIT_2026-08-22.zip
sha256: 4992a8b43f85c629425f334825fefd060f380a10a6306975b5d04143f898b0b5
audited_controller_snapshot: 551c39e20270a0c7a9e3e0f9f12a0eda43914faa
current_main_revalidation_start: 5f7fd82b9a11118c8b49654e12ec10cc57b329ac
eligible_rows_at_containment: 0
divergence_rows_at_containment: 0
outcome_rows_at_containment: 0
```

Binding P0 findings:

1. The production breadth owner stores `membership_hash` under `aggregate`, while the materializer reads a top-level field. The shared `breadth_rich/LATEST.json` is also written by owner, rich-checkpoint and adaptive-cadence workflows with different contracts.
2. Breadth retrieval and BTC.D verification timestamps can be later than the row cutoff and still be accepted.
3. The 168-row ETHBTC contract can accept a sparse or gapped window.
4. BTC.D rows are selected by file order without requiring three distinct chronological settled dates.
5. Outcomes can be matured from a later mutable hourly tree without reconciling the frozen row-time baseline and source version.
6. The only prospective structural regime is post-ETF, while later controller actions require two distinct regimes. The gate is therefore unreachable under the frozen taxonomy.

Containment decision:

```text
status: QUARANTINED_PENDING_P0_REPAIR
old_floor: 2026-08-23T04:50:00Z
old_floor_disposition: INVALID_FOR_FUTURE_ACCUMULATION_WITH_ZERO_ROWS_CREATED
temporary_floor: 2026-09-30T00:00:00Z
temporary_floor_role: CONTAINMENT_SENTINEL_ONLY
automatic_promotion: FORBIDDEN
pre_repair_rows: PRESERVE_BUT_QUARANTINE_AND_EXCLUDE
```

The sentinel must be replaced after the P0 implementation is merged and the first complete post-repair owners exist. The replacement must be a new future timestamp later than both the implementation merge and every source capture used by the first row. No row may be backdated or migrated from the old floor.

P0 acceptance requires production-schema tests, future/stale/provider/version controls, exact 168-hour continuity, distinct chronological BTC.D prints, immutable source bindings, row-time outcome reconciliation, a reachable preregistered prospective-block robustness design and a clean rerun of the negative-control suite.

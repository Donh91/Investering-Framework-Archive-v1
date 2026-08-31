# Independent code audit: revalidation and bounded intake

**Dato:** 2026-08-31
**Status:** SOURCE_NOTE / REPRODUCED_FINDINGS_INTAKE, NOT_REMEDIATED
**Område:** Control-plane code, evidence integrity and CI
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/code_audit_20260831/`

Baseline: `fa18006c3c0b2a1ab89f5dcebb3ce4a02bd50195`. The subsequent eight commits through `786910c20b36cead83a29f7acc26824a722508fe` were inspected for overlap; they do not change the reproduced target code. Other active branches, private data and frozen historical observations were not modified. Round 3 hypothesis testing and outcome scoring remain OFF.

This intake does not claim that any defect is fixed or any candidate is CODEX_READY. The event-driven maturation controller and `LATEST_CODEX_READY_TASKS.json` remain the authority. Existing Daily Director output-validation, accepted-DATA-PING-lineage, macro-freshness, temporal-alignment, intraday and Shadow Registry tasks were checked to avoid duplicating their authority. Eight new candidates address distinct bounded implementation defects; overlapping owner files require fresh-state coordination.

## Independently reproduced

| Reference | Result at baseline | Consequence |
|---|---|---|
| H4 / N1 | Lane guard accepts truncated JSON; monthly guard accepts NaN cost | Missing or invalid cost evidence can produce PASS |
| H2 | 118 eligible weekly outcomes, zero returned | Current v3 learning disappears from weekly context |
| M3 | Valid/bad/valid CSV gives one valid row | One malformed row discards the remaining file |
| H7 | Corrupt entry state returns the same None as an absent file | Initialization can conceal damaged evidence |
| M4 | 168-hour observation written into the 24h slot | Fixed-horizon measurement is mislabeled |
| H3 | All current v2 ETF captures rejected by the old v1 adapter | The current owner lane cannot supply the experiment |
| M13 | Timezone-naive input accepted by a UTC validator | Mixed timestamp comparison may crash instead of reject |
| D4 | An unseen run ID with an ancient timestamp is declared fresh | Deduplication is being used as a freshness check |
| N2 | 168 rows containing only 167 unique hours declared COMPLETE | A duplicate masks a missing hour |
| T2 | 4 failed, 823 passed, 247 successful subtests | The current broad local suite is not green |

Run the read-only probes from a clean checkout with Python and existing test dependencies:

```bash
PYTHONDONTWRITEBYTECODE=1 python 06_RESEARCH_LAB/audit_summaries/code_audit_20260831/reproduce.py . > audit-results.json
python -m pytest tests/ -q
```

The probe reports observations rather than declaring remediation from string matches. The fixed ISO week is intentional for reproducibility. Use temporary fixtures for negative tests and never production API calls.

## Corrections to the supplied external audit

- M4 is still open. The supplied harness reports FIXED because a `measurement_validity` token exists elsewhere, but the behavior test still creates the wrong horizon. A token-presence check is insufficient.
- D3's purported missing transition receipts are largely future destination paths for unstarted tasks. At the baseline all four IN_REMEDIATION and five RESOLVED transition receipts exist. Do not fabricate receipts for CODEX_READY tasks.
- D11 compares a source-workbook payload hash with a generated revision JSON hash. Those hash scopes differ deliberately; the revision manifest hashes verify. This is not demonstrated corruption.
- Timezone support under GitHub Actions schedules is real. Do not remove the `timezone` keys. GitHub documents spring-forward adjustment; claims about double execution need actual run evidence.
- The shared main-writer lock is required by current repository governance. GitHub now supports `queue: max` for up to 100 pending runs. Assess this option before proposing unsafe independent writer locks.
- CFGI's current policy authorizes ten fields. The meaningful unresolved discrepancy is five mixed-timeframe daily captures in policy versus six four-hour captures in the workflow, not simply that ten fields exist.
- Stored conflicting ETF versions are verified, but historical unknown cells are not evidence of their correct replacement values. Preserve as-of knowledge and expose eligibility; never guess revisions.

## Safety and follow-through

High-impact workflow and governance edits are not included. The prescribed external vault returned 404 through the authenticated connector, and archive-governance requires a verified safepoint/vault sequence first. This is a real remaining safety gate, not a claim of successful backup. Bounded code-only candidates preserve workflow files, gates, weights, source authority, portfolio logic, budgets and historical evidence.

The Daily Director concurrency spelling, unfiltered full-suite CI, workflow queue depth, source-governance drift and paid-collector cadence remain distinct review items. One character in the Director workflow cannot by itself fix the separately reproduced output-validation failure.

## Primary platform references

- [GitHub Actions concurrency queue behavior](https://docs.github.com/actions/writing-workflows/choosing-what-your-workflow-does/control-the-concurrency-of-workflows-and-jobs)
- [Larger concurrency queues, May 7 2026](https://github.blog/changelog/2026-05-07-github-actions-concurrency-groups-now-allow-larger-queues/)
- [Schedule timezone support, March 19 2026](https://github.blog/changelog/2026-03-19-github-actions-late-march-2026-updates/)
- [Schedule events and daylight saving behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

## Archive decision

Classification SOURCE_NOTE; append-only research intake and reproducibility artifact. Branch `agent/task-20260831-code-audit-intake` verified before creation. No deleted paths, canonical index, registry, workflow or governance changes. High-impact gate NOT_REQUIRED for this intake only; no external backup claimed. All candidates validate against the existing JSON schema and are subject to independent controller maturation. No current queue or execution ledger is edited by this change.

# OnChainMind / Public Data Source Admission v1

Status: `WORK_PREP / SHADOW_ONLY / NO_MARKET_AUTHORITY`

This folder is the bounded engineering/research handoff created after the 2026-09-01 OnChainMind deep-dive.

## What is already decided

- OnChainMind is a discovery/context source, not a machine data owner.
- Do not automate scraping of OnChainMind or ChartInspect.
- Coin Metrics Community is the preferred open long-history baseline candidate.
- BGeometrics is the strongest rich recent on-chain / URPD research-source candidate, with no public raw payload persistence.
- Polymarket is a high-interest expectations source but network collection is blocked until official data-use/storage rights are resolved.
- DefiLlama should reuse the existing owner rather than create a new source.
- No new engine, live weight, threshold, portfolio action or predictive authority is authorized.

## Files

- `SOURCE_CONTRACTS_v0_1.json` — provisional provider contracts and hard boundaries.
- `PRIORITY_AND_KILL_MATRIX_v0_1.json` — ordered Work queue and stop rules.
- `RESEARCH_EXPERIMENT_SPEC_v0_1.md` — retrospective/prospective research design.
- `WORK_MASTER_HANDOFF_v1.md` — execution mission for Work.

Related source-discovery audit:

- `../audit_summaries/2026-09-01__onchainmind-public-data-source-admission-audit__shadow.md`
- `../audit_summaries/onchainmind_source_admission_v1/SOURCE_CAPABILITY_MANIFEST.json`

Research-only probes:

- `../../scripts/research_sources/coinmetrics_community_probe.py`
- `../../scripts/research_sources/bgeometrics_research_probe.py`
- `../../scripts/research_sources/polymarket_expectations_parser.py`
- `../../scripts/research_sources/validate_research_source_receipt.py`

Tests:

- `../../tests/research_sources/test_public_research_source_probes.py`
- `../../tests/research_sources/test_research_source_receipt_validator.py`

## Handoff line

This package intentionally stops before the work becomes broad/heavy: full current-main synchronization, production-quality source adapters, historical replay across thousands of rows, current-framework timestamp joins, restricted-plane URPD retention, CI remediation and final merge/readback.

Those are the Work mission.

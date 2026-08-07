# Audit receipt — DATA PING dprun_32c45bcac4df4fa4

```yaml
processed_at_local: 2026-08-07T09:20:00+02:00
source_packet_attachment: packet(1).json
source_validation_attachment: validation_report.json
collector_version: 15.3.1
validator_method_id: DATA_PING_PACKET_VALIDATOR_v3
validator_pass: false
main_thread_ingest: false
bounded_owner_advanced: false
canonical_state_change: NONE
portfolio_effect: NONE
```

## Attachment integrity

- packet attachment bytes: `12010`
- packet attachment SHA-256: `4d8978d0426d25e6bd7cf5dba3fd315dabe6059127fd6d8f6808e7e25985caa9`
- collector canonical packet SHA-256: `6a822acf3c5c068b88b41c3126bfc479205446f431fee43e72f899cb918b6691`
- validation attachment bytes: `7073`
- validation attachment SHA-256: `ca466eaff3656f14af2c53c36d3f43dfb8a1e6847511c171b0336c43abb26747`
- validator payload SHA-256: `235a468e2fbbd8bf2d23fe5bd5ea33aeb4ab86163a53a3d4e69b9bac66e6d055`

## Adjudication

1. Confirmed hard runtime interruption after one registered core action.
2. Confirmed `ORC-001` incremental-commit violation and `INV-007` unregistered source call as the principal failure mechanism.
3. Confirmed no terminal freeze and no snapshot.
4. Confirmed 59 core actions and one optional action were unattempted.
5. Quarantined the partial BTC ETF `29.2M` row because 8 issuer cells remained dashes/unknown despite exact displayed-total tie-out.
6. Preserved the partial row only as owner-finality QA evidence.
7. Created engineering issue #325.
8. Added finality learning to issue #318.
9. Left active bounded owner unchanged.
10. Left H7/OTA state unchanged.

## GitHub records

- `08_SOURCE_MATERIAL/data_ping/2026-08-07__dprun_32c45bcac4df4fa4__validation-failed-source-record.md`
- `09_SOURCE_QA/data_ping/2026-08-07__dprun_32c45bcac4df4fa4__validation.json`
- `04_MARKET_LEARNING/data_ping/2026-08-07__dprun_32c45bcac4df4fa4__non-decision-assessment.md`
- engineering issue #325

```yaml
RESEARCH_ESCALATION: NO
engineering_required: true
primary_engineering_issue: 325
targeted_ETF_owner_validation_pending: DP-ETF-DIRECT-OWNER-20260807-02
```

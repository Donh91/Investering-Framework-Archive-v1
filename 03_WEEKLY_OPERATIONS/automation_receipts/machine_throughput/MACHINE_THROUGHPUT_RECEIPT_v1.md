# Daily Machine Throughput Receipt v1

Status: `OPERATIONAL_OBSERVABILITY`

Authority: `OPERATIONAL_OBSERVABILITY_ONLY`

This receipt measures how much of the framework machine actually ran, persisted, analyzed and converted into bounded learning artifacts during one closed Europe/Copenhagen calendar day.

It does not create or modify market state, thresholds, model weights, forecast authority, portfolio permissions or portfolio action.

## Window

The scheduled workflow runs at 00:50 Europe/Copenhagen and measures the previous fully closed local day. The receipt records exact UTC start/end boundaries and the Git commits immediately before both boundaries.

Manual replay may supply an explicit local date.

## Exact metrics

The following are treated as exact within their declared scope:

- GitHub Actions runs started inside the closed window, including scheduled-run counts, events, conclusions and failures.
- Immutable live-anchor captures persisted for the local day.
- Owner collection attempts and owner exit outcomes exposed by live-anchor indexes.
- Unique persisted hourly observation rows for the local day.
- Recorded hourly `source_records`, response bytes and returned row counts.
- End-of-window bytes and structural JSON scalar values for durable evidence paths touched during the window.
- API-agent receipts, actual model calls, zero-cost skips, recorded token use and recorded cost.
- Daily Director and conflict-review model-call counts.
- New experiment candidate, observation, dispatch, forecast-memory and outcome-memory files created in the window.

`normalized_values_total_structural` is a machine-throughput measure. It is not the count of economically independent features and must not be interpreted as information value.

`core_observation_units` is the sum of unique hourly observation rows plus immutable live-anchor captures. It is a stable throughput denominator, not a market-quality score.

## Physical external-call boundary

V1 does not claim an exact total physical HTTP-request count across the entire framework because not every point-in-time or specialist owner currently records one physical-request counter per network request.

The receipt therefore exposes:

- exact instrumented physical calls from Hourly Sequence `source_records`;
- exact owner collection attempts from live-anchor indexes;
- `exact_total_physical_http_calls: null` while instrumentation coverage is incomplete;
- an explicit `PARTIAL_INSTRUMENTATION` status rather than an inferred total.

This is intentional. False precision in the observability layer is forbidden.

Future owner instrumentation may close this gap without changing the receipt's market authority.

## Efficiency fields

V1 derives bounded operational ratios such as:

- actual model calls per 100 core observation units;
- new experiment candidates per 100 core observation units;
- recorded API cost per 100 core observation units;
- new experiment candidates per 1,000 structural normalized values.

These ratios help detect machine bloat, duplicated work and analysis growth without evidence growth. They do not prove forecast skill or investment edge.

## Durable outputs

Scheduled production writes:

```text
LATEST_MACHINE_THROUGHPUT.json
03_WEEKLY_OPERATIONS/automation_receipts/machine_throughput/LATEST.json
03_WEEKLY_OPERATIONS/automation_receipts/machine_throughput/LATEST.md
03_WEEKLY_OPERATIONS/automation_receipts/machine_throughput/YYYY/MM/YYYY-MM-DD.json
03_WEEKLY_OPERATIONS/automation_receipts/machine_throughput/YYYY/MM/YYYY-MM-DD.md
```

Each JSON receipt includes a semantic `receipt_sha256` calculated before the hash field is appended.

## Failure semantics

A RED market or framework state does not make this observer fail. The throughput workflow fails only if it cannot obtain the run census, construct a closed-window receipt, validate its contract/hash, run its tests, durably publish the receipt or verify readback.

Observed workflow/owner failures remain data inside the receipt.

## Governance

- public control-plane metadata only;
- no restricted provider values are copied from `Donh91/secrets`;
- no credential values enter outputs;
- no hidden interpolation or inferred physical-call total;
- no automatic framework-rule or portfolio authority;
- writes are serialized by `framework-main-writer` and verified after push.

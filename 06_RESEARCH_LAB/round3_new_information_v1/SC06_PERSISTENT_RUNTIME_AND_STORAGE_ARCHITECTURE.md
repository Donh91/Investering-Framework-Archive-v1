# SC06 persistent runtime and private storage architecture

Status: `DESIGN_COMPLETE_DEPLOYMENT_NOT_AUTHORIZED`  
Authority: implementation architecture only, no market or analysis authority  
Private requirements: `Donh91/secrets/GOVERNANCE/SC06_PERSISTENT_RUNTIME_REQUIREMENT.md`  
Cross-repository boundary: `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`

## Decision

The recommended production design is one Amazon ECS Fargate On-Demand service for the persistent collector and a private Amazon S3 bucket with versioning, checksum validation, lifecycle management and Object Lock. GitHub Actions deploys and validates the service, but is not the continuous websocket runtime.

This is a design decision only. No AWS account, paid service, bucket, role or runtime is created or authorized by this document.

## Non-negotiable acceptance criteria

- Sequence-contiguous eligible time must remain at least `99.9%`.
- Deterministic five-minute snapshot coverage must remain at least `90%`.
- Binance sequence gaps trigger an explicit invalid interval and REST re-bootstrap. They are never interpolated, forward-filled or bridged.
- Collection remains `PROSPECTIVE_COLLECTION_ONLY`.
- Hypothesis testing and outcome scoring remain `OFF`.
- Raw diffs and normalized order-book values remain in the restricted data plane.

Service uptime is not the continuity metric. Continuity is computed from accepted Binance update-ID transitions and the frozen SC06 eligibility rules.

## Why this runtime

An ECS service maintains the desired task count and replaces failed tasks. Fargate removes host administration. ECS container health checks, deployment circuit breaker and rollback give a bounded recovery path. An ECS task IAM role provides short-lived runtime access to S3 without credential files.

On-Demand capacity is required for the primary collector. Interruptible/Spot capacity is not acceptable for the sole writer because avoidable termination risk conflicts with the continuity target.

Reviewed alternatives:

| Option | Result | Reason |
|---|---|---|
| GitHub Actions scheduled or long-running job | reject as primary runtime | job lifecycle and restart model are not a durable websocket service |
| Self-hosted GitHub runner | reject as primary runtime | moves host patching, supervision and recovery to the project without improving evidence integrity |
| Single unmanaged VM plus object storage | viable lower-cost fallback | more operational burden, host recovery and deployment risk |
| Google managed instance group plus Cloud Storage retention lock | robust alternative | comparable controls, no clear simplicity advantage for this bounded service |
| ECS Fargate On-Demand plus S3 | recommended | managed restart, health/rollback, IAM task identity, immutable/versioned object storage and native checksum support |

## Collector lifecycle

1. Start one fenced writer epoch with a unique `collector_epoch_id` and control-plane collector commit SHA.
2. Open the Binance `@depth@100ms` stream and buffer events.
3. Fetch the REST depth snapshot.
4. Discard buffered events with `u` at or before the snapshot update ID.
5. Require the first accepted event to cover the local update ID transition and apply subsequent events only when update IDs are contiguous under the frozen source contract.
6. On any gap, mark the current interval incomplete, seal available raw evidence, abandon the local book and repeat the bootstrap. Never repair a gap synthetically.
7. Rotate the websocket before Binance's 24-hour connection limit. The new connection starts a new bootstrap/epoch and cannot silently bridge the old sequence.
8. Emit a deterministic snapshot at each UTC five-minute boundary only when the book is sequence-valid under the frozen contract.

Deployments use a single active fenced writer. A replacement task must acquire a lease/fencing token before emitting canonical private chunks. Overlap may collect quarantined raw events but may not create two authoritative writers. The lease store and permissions are infrastructure details requiring approval at deployment.

## Chunk and object contract

Recommended raw chunk cadence is one UTC minute, with five-minute manifests and snapshots. One-minute sealing bounds uncommitted loss and makes recovery verification small enough while keeping object counts manageable.

Private object layout:

```text
sc06/raw/v1/YYYY/MM/DD/HH/<start>_<end>_<compressed_sha256>.ndjson.zst
sc06/manifests/v1/YYYY/MM/DD/HH/<five_minute_window>.json
sc06/snapshots/v1/YYYY/MM/DD/HH/<five_minute_boundary>_<sha256>.json.zst
```

Each raw record carries provider event time, collector receive time, `U`, `u`, connection ID, collector epoch, schema version and raw payload bytes. Each manifest binds:

- source-contract ID and collector commit SHA;
- object key and immutable version ID;
- compressed and uncompressed bytes;
- compressed and uncompressed SHA-256;
- storage-side checksum and readback result;
- first/last provider and receive timestamps;
- first/last `U` and `u`, update count and duplicate count;
- bootstrap, reconnect and gap events;
- eligible milliseconds and sequence-continuity status;
- snapshot expected/produced/valid status;
- schema ID/version/hash and validation status.

Upload is accepted only after local hash, S3 SHA-256 checksum validation, `HEAD`/readback metadata verification and immutable version-ID capture. ETag alone is not a content hash.

## Immutability and retention

Enable S3 Versioning before first production write. Use Object Lock in Governance mode during the authorized commissioning phase. Do not enable irreversible Compliance retention until a human approves the retention duration and legal/provider-rights basis.

Retention values remain human decisions. Proposed policy for approval:

- keep all raw chunks hot for 30 days;
- transition older raw chunks to an approved archive tier after 30 days;
- retain manifests, hashes, private snapshots and source-health evidence for at least the full prospective programme plus reproducibility window;
- prohibit deletion while a dataset is referenced by an open gate, audit, incident or research decision;
- record every lifecycle transition or authorized deletion in a private receipt.

Provider terms and the final retention authority may require a shorter or longer period. Lifecycle automation cannot outrank those terms.

## Recovery and observability

Recovery state is derived from immutable objects and the last validated private checkpoint, never from an assumed clean shutdown.

On task loss:

1. seal or quarantine recoverable local spool data;
2. publish a private incident/gap receipt;
3. start a new fenced epoch;
4. reconnect, buffer, REST-bootstrap and re-establish sequence validity;
5. mark every uncovered interval missing;
6. resume deterministic boundary snapshots only after validity is restored.

Target operational objectives for commissioning are raw-chunk RPO at most one minute and automated collector restart within five minutes. These targets support, but do not replace, the frozen continuity and snapshot-coverage metrics.

Private alerts must cover:

- websocket event age and connection lifetime;
- sequence gap/re-bootstrap rate;
- writer lease/fence failures;
- raw spool age and upload/readback failures;
- expected versus valid five-minute snapshots;
- rolling `99.9%` sequence-continuity and `90%` snapshot-coverage gates;
- object-lock/versioning/checksum drift.

Alerts and logs must not contain order-book values or credentials.

## Cross-repository receipts

The restricted repository owns exact object keys, version IDs, restricted health evidence and raw/normalized data. It periodically commits an immutable manifest receipt that contains the binding required by `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`.

The control plane may publish only a provider-value-free receipt containing:

```text
source_contract_id
private_repository
private_commit_sha
exact_private_manifest_path
private_manifest_bytes
private_manifest_sha256
capture_window_utc
schema_id/version/hash
object/chunk counts
gap/completeness/validation status
```

The public receipt does not contain depth values, object credentials, signed URLs or sensitive object-store coordinates. The private manifest resolves those details for an authorized reader.

## Deployment and credential plane

Recommended deployment flow:

1. human approves provider, account, region, budget, retention mode/period and alert destination;
2. infrastructure is reviewed as code on an isolated branch/PR;
3. GitHub Actions assumes a narrowly scoped deployment role using GitHub OIDC;
4. ECS uses separate execution and task roles; the task role has least-privilege object/manifest access;
5. deployment circuit breaker and rollback are enabled;
6. a commissioning canary validates sequence, chunk hashes, object readback, recovery and public/private receipt redaction;
7. continuous collection is activated only by a new governed receipt.

Long-lived AWS access keys are not stored in repository files. If OIDC is unavailable, any temporary deployment credential stays in GitHub Actions Secrets and must be rotated after commissioning. Runtime credentials use the ECS task role or another explicitly approved workload identity.

## Official technical references reviewed

- Binance Spot WebSocket streams and connection limits: <https://developers.binance.com/en/docs/products/spot/web-socket-streams>
- Binance Spot diff-depth stream: <https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/ws-streams/~>
- Binance local order-book bootstrap and gap handling: <https://developers.binance.com/en/docs/products/spot/testnet/web-socket-streams>
- Amazon ECS services: <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html>
- AWS Fargate: <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html>
- ECS deployment circuit breaker: <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-circuit-breaker.html>
- ECS task IAM roles: <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html>
- S3 upload checksum verification: <https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity-upload.html>
- S3 Object Lock: <https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html>
- S3 Versioning: <https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html>
- S3 Lifecycle: <https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html>
- GitHub Actions OIDC for AWS: <https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services>

## Remaining authorization blockers

Production activation requires explicit human authority for:

- paid cloud deployment and budget ceiling;
- AWS account and region;
- Object Lock mode and retention duration;
- provider-rights/retention confirmation;
- alert destination and on-call owner;
- lease/fencing implementation and infrastructure PR;
- a new SC06 commissioning and activation receipt.

Until those decisions exist, SC06 remains `FROZEN_CANARY_ONLY_PERSISTENT_RUNTIME_REQUIRED`.

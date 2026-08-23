# Agent Tool Shadow Round 2 v1

Status: SHADOW_TESTING
Authority: RESEARCH_ONLY_NON_CANONICAL
Canonical effect: false
Portfolio execution: false
Human confirmation required for lifecycle decision: false

## Purpose

Round 2 evaluates a very small set of external agent-engineering capabilities that may improve the framework's laboratory, testing and engineering machinery without becoming part of the market-decision brain.

The round tests three research objects:

1. **Codebase context bake-off** - current baseline versus Graft versus codebase-memory-mcp.
2. **Agent/skill evaluation harness** - Inspect AI as an isolated evaluation framework.
3. **Adversarial skill red-team harness** - Promptfoo as an isolated attack/evaluation framework.

Agency Agents, Agent-Reach and Orca are not runtime candidates in this round. They remain external pattern/reference material only.

## Prime rule

No external repository, package, MCP server, hook, agent configuration or generated file is trusted because it is popular or because its author reports a benchmark.

Every candidate must beat the existing framework or the simplest relevant in-house baseline after complexity tax.

## Stage A - hostile qualification

Stage A is intentionally narrow and secret-free.

- runs only on pull request or explicit manual dispatch;
- has `contents: read` only;
- receives no OpenAI key, provider key, secrets-repository access or market-data credentials;
- executes external software only inside runner-temporary directories;
- gives every candidate a byte-identical independent copy of the frozen synthetic fixture so one candidate cannot contaminate another candidate's evidence;
- may not write to the checked-out framework repository;
- may not modify agent configuration, user configuration or production workflows;
- may not start persistent daemons or background watchers;
- may not call an LLM or external model provider;
- may install only exact frozen package artifacts; when an exact package's documented installation requires an authenticated publisher runtime bootstrap, that bootstrap is treated as explicit supply-chain complexity tax and is permitted only in the isolated secret-free runner;
- records evidence as an ephemeral GitHub Actions artifact only.

Stage A can only produce `QUALIFIED_FOR_STAGE_B`, `KEEP_SHADOW` or `BLOCK` evidence. It cannot promote anything.

## Candidate A - codebase context bake-off

### Arms

- `BASELINE`: ordinary repository/file exploration without an external context layer.
- `GRAFT`: structural tree-sitter mode only. `graft init`, deep/LLM build modes and agent wiring are forbidden.
- `CODEBASE_MEMORY`: documented one-shot JSON CLI only with an isolated cache. Installer-driven agent configuration, MCP wiring, daemon, watcher and UI modes are forbidden. Its npm wrapper's verified native-runtime bootstrap counts against its complexity/supply-chain score.

### Stage A question

Can each external arm safely build/query its own byte-identical copy of a deterministic fixture and recover preregistered architecture facts without touching the framework checkout or requiring secrets?

### Stage B promotion question

On a frozen set of at least 20 representative framework engineering tasks, does one arm reduce exploration cost by at least 20% without a correctness regression, architecture misunderstanding or unacceptable complexity/security tax?

Only one external context arm may ultimately win. If Graft and Codebase Memory are materially equivalent, prefer the simpler/lower-risk arm. If neither clearly beats baseline, retire both.

## Candidate B - Inspect AI evaluation harness

### Stage A question

Can the pinned Inspect package be installed and its task/dataset/scorer contracts be constructed locally without model calls or writes outside the isolated runner home?

### Stage B promotion question

Does an Inspect-based harness make skill/agent evaluation more reproducible, more discriminating or easier to audit than the existing in-house testing stack, while preserving the framework's own post-flight/clean-tree and protected-path guardrails?

Inspect is never permitted to replace the framework guardrail layer. A task that succeeds while causing collateral state damage is a failed evaluation even if an Inspect scorer reports success.

## Candidate C - Promptfoo adversarial harness

### Stage A question

Can the pinned Promptfoo CLI validate a frozen local red-team configuration with telemetry, update checks, sharing and remote generation disabled, without provider credentials or target calls?

### Stage B promotion question

Can a bounded adversarial suite detect authority escalation, prompt injection, secret-access attempts, protected-path mutation attempts, evidence tampering, self-promotion or provenance corruption that the existing baseline would miss?

Promptfoo may be promoted only as a test instrument. It may not become a decision authority, production source, provider proxy or persistent telemetry backend.

## Frozen Stage A upstream versions

See `UPSTREAM_PINS.json`. Changing a version or source pin is a new experimental condition and must be reviewed as such; it is not an invisible dependency update.

## Complexity tax

For every candidate measure or record:

- setup time;
- wall time;
- output/context size;
- additional package/dependency count;
- network requirements;
- filesystem writes;
- background processes;
- cache footprint where available;
- native runtime/bootstrap requirements;
- failure clarity;
- source/version fragility;
- security/privacy surface;
- maintenance burden;
- overlap with existing framework capabilities.

## Fail-closed conditions

Immediate `BLOCK` for the affected arm if any of the following occurs:

- checked-out framework repository becomes dirty after the test;
- candidate tries to read a secret or requires a provider credential in Stage A;
- candidate modifies global/agent configuration;
- candidate requires a standing daemon, watcher or UI for the qualification path;
- unexpected external provider/model call occurs;
- telemetry or sharing cannot be disabled for the tested path;
- a package version cannot be pinned/reproduced;
- result cannot be bound to the upstream pin and fixture hash.

## Lifecycle

Stage A evidence is non-promotional. A candidate that survives Stage A may enter a separately reviewed Stage B prospective comparison. The existing autonomous OpenAI lifecycle decider remains the eventual substantive PASS/FAIL authority once the candidate has evidence satisfying its preregistered promotion gate.

Master Monday is reporting-only and is not an owner approval gate.

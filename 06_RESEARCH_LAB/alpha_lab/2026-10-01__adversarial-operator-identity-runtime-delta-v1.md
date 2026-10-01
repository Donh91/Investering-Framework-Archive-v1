# Adversarial Operator Research — identity + runtime delta v1

Date: 2026-10-01
Status: SHADOW_RESEARCH / POST-FIX DELTA
Owner: #1087
Authority: RESEARCH_ONLY
Automatic trading: NO
New scanner: NO

## Purpose

Append only the evidence learned after the frozen counting-gate / forward-cohort contract was created.

Do not rewrite the earlier frozen logic.

Parents:
- `06_RESEARCH_LAB/alpha_lab/2026-10-01__adversarial-operator-claude-bitquery-counting-gate-v1.md`
- `research/api_agent/meme_alpha/experiments/ADVERSARIAL_OPERATOR_FORWARD_COHORT_v1.json`
- Bridge Claude PARTIAL + ChatGPT adjudication
- `codex-research-alpha-adversarial-runtime-wiring-v1`

## 1. Exact identity gap closed for PINK and LEGS

Fresh Blockscout exact-address reads reproduce the Bitquery launch timestamps.

| Case | Exact CA | First tx / launch timestamp |
|---|---|---|
| BYTE | `0xd5520D9D777a42D85f94834fbea162B17A197CfB` | 2026-09-27T16:42:10Z |
| CRUMBS | `0x80bAa4b3bfAC6f4978700dF824B1B3d98e889136` | 2026-09-08T23:57:56Z |
| DRAFT | `0xfe51aaf6AF1Ec2eB9286e0BdC3c9dc39240cB8F5` | 2026-09-10T23:45:04Z |
| DEED | `0x5E55f18453545d0D4314C5106a2D8Db934298E95` | 2026-09-21T23:51:56Z |
| LEGS | `0x8FcF98e1348D3DDeE46cdD15A5C7D9a8d423077d` | 2026-09-03T21:03:56Z |
| PINK | `0xBc9cc4b93A08B2dfBA87067a9C53E713DB3314Ce` | 2026-09-07T21:56:19Z |

This closes the earlier PINK/LEGS identity gap.

Important anti-false-positive:
all observed Pons-family token contracts expose common Pons factory/creator infrastructure.
Shared Pons factory/creator identity is therefore BENIGN_INFRA / protocol infrastructure, not operator lineage.

## 2. Independent external reproduction improved

The public Bitquery investigation independently reconstructed the Wazz family from chain archives and reports 56 linked launches rather than relying on the original 53-launch social thread alone.

Research consequence:
- operator/extraction pattern existence is materially better supported;
- shared public bundling tools remain non-selective;
- direct money flow / funding-key lineage remains the higher-information discriminator;
- broad Stage-A launch-privilege patterns must not be confused with Stage-B operator identity.

## 3. Runtime wiring is no longer merely CODEX_READY

The existing adversarial-runtime remediation progressed through real production-shaped runs.

### Parent stale-market replay

Restricted runtime run:
`36846083826-1`

Observed:
- task type: `ADVERSARIAL_REPLAY`;
- adversarial role active;
- same-run Stage0 exact-CA hydration executed;
- current price absent;
- current market cap absent;
- current sellability not proven;
- historical market figures were NOT reused as present-tense evidence;
- result remained `DEGRADED`;
- development candidates: 0;
- no trading / user-alert / direct-code authority.

Interpretation:
`PONSCUPINE_STALE_MARKET_REPLAY = PASS`.

### Neighbor stale-action-language replay

Restricted workflow run:
`36881054034`

Top-level task:
`2026-10-01T150500Z__ponscupine-stale-action-language-neighbor-v1.json`

Observed:
- deterministic selector chose the P0 top-level `ADVERSARIAL_REPLAY`;
- historical fixture carried `ENTRY_CANDIDATE` only as explicitly stale historical evidence;
- same-run Stage0 again lacked current price/MC/sellability;
- model explicitly rejected carrying the old action into the present;
- output remained `DEGRADED`;
- source-provenance invalidation remained preserved;
- development candidates: 0;
- two bounded P0 adversarial child/retest tasks were created automatically.

Interpretation:
`PONSCUPINE_STALE_ACTION_LANGUAGE_NEIGHBOR = PASS`.

### Routing observation

The main-to-restricted event path is live:
- main/restricted pushes wake the existing background-research workflow;
- adversarial task type is selected through the existing runtime;
- bounded child tasks route through the existing child queue;
- no parallel runtime/scheduler was created.

The legacy child queue is large, so a new P0 child can wait behind older equal-score P0 children.
This is an observability/queue-latency issue, not evidence that adversarial task routing is absent.

Current lifecycle interpretation:
`RUNTIME_WIRING = IMPLEMENTED_AND_POST_FIX_OBSERVED`.

Canonical remediation owner should advance/close the transition only through its existing lifecycle machinery; do not hand-edit generated lifecycle state merely to make status green.

## 4. Counting executor is now the missing bounded implementation

The scientific rule is already frozen.

The missing code is only a deterministic executor for:

`ADVERSARIAL_OPERATOR_FORWARD_COHORT_v1.counting_gate`

Preferred cost architecture:

### Stage A — cheap / broad

Use existing Pons launch-event rows:
- exact token;
- tx hash;
- deployer;
- pair token;
- launch block/T0.

Use raw chain/RPC launch transaction input to decode the already documented Pons `launchAndBuy` fields.

Pons first-party ABI:
`launchAndBuy(TokenParams params,uint256 launchConfigId,address pairToken,uint256 quoteIn,uint256 minTokensOut,address recipient,address[] snipeTaxExemptions)`.

Stage A should avoid one Blockscout enrichment call per launch if raw RPC transaction calldata can provide the exemption list deterministically.

Stage A is an adverse-selection surface, not operator identity.

### Stage B — expensive / selective

Only for Stage-A qualified rows:
- funding ancestry;
- pre-T0 fresh-wallet funding;
- privileged exemption overlap;
- common non-benign funder;
- prior operator proceeds -> new launch funding;
- synchronized beneficial inventory;
- Relay/router/bridge/CEX/protocol exclusions.

Reuse existing Blockscout/RPC bindings.

Do not call Blockscout across the full launch denominator if Stage A can prune first.

## 5. Current state

- PINK_IDENTITY: VERIFIED
- LEGS_IDENTITY: VERIFIED
- SHARED_PONS_FACTORY: BENIGN_INFRA_NOT_OPERATOR_IDENTITY
- CLAUDE_PARTIAL: ACCEPTED_WITH_MODIFICATIONS
- BITQUERY_INDEPENDENT_REPRODUCTION: MATERIAL
- ADVERSARIAL_RUNTIME_PARENT_REPLAY: PASS
- ADVERSARIAL_RUNTIME_NEIGHBOR_REPLAY: PASS
- EVENT_DRIVEN_ROUTE: OBSERVED
- COUNTING_CONTRACT: FROZEN
- COUNTING_EXECUTOR: MISSING
- FIRST_PUMP_STRATEGY: NOT_SUPPORTED
- NANSEN_TOPUP_REQUIRED: NO
- NEXT_BOUNDED_CODE_WORK: COUNTING_EXECUTOR_ONLY

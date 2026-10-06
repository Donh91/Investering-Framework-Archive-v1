# S1 - Executable Sellability Truth v1

Status: SPECIFIED / READY_FOR_BOUNDED_IMPLEMENTATION / RESEARCH_ONLY
Priority: P0
Master queue: README.md
Canonical queue state: QUEUE_V1.json
Execution owner: Donh91/Meme-Alpha-Lab existing paper-wallet execution realism + microstructure owners

## Research question

Can provider safety/sellability claims be converted into a calibrated, notional-aware probability that a token can be entered and exited at realistic cost?

The target is not "honeypot detection" as a binary label.

The target is:

`can buy -> can sell -> at what notional -> at what total round-trip friction -> under what liquidity/state -> did the provider or internal model predict it correctly?`

## Existing owner audit

Meme Alpha Lab already has:
- execution-capacity shadow at $100/$500/$1k/$2.5k/$5k;
- `execution_shadow_v4.csv`;
- impact_bps;
- reserve_depth_ratio;
- roundtrip_friction_floor_usd;
- mechanics_status;
- separate signal-skill and execution-realism accounting.

Therefore:
- DO NOT create a second execution engine;
- DO NOT create a second paper wallet;
- DO NOT let an external provider overwrite execution_shadow truth.

New work is a challenger/calibration layer attached to existing execution realism.

## External specialist candidates

### GoPlus

Fresh public documentation confirms:
- Token Security API;
- EVM transaction simulation API;
- Solana transaction simulation API;
- Robinhood Chain token-security support, chain id 4663, added 2026-07-28;
- Robinhood supported main tokens include WETH, USDE and USDG;
- Robinhood DEX support includes UniswapV2, UniswapV3 and UniswapV4.

Important unresolved item:
public docs reviewed do NOT yet prove that the generic EVM transaction-simulation endpoint supports every Robinhood 4663 route/state required by this experiment.

State:
`TOKEN_SECURITY_4663_CONFIRMED / TX_SIM_4663_NEEDS_LIVE_SOURCE_AUDIT`.

### Honeypot.is

Public documentation exposes:
- honeypot checks;
- buy/sell tax and gas context;
- pair information;
- top-holder resource.

Important unresolved item:
Robinhood Chain support is not established by the documentation reviewed for this spec.

State:
`API_CAPABILITY_CONFIRMED / ROBINHOOD_COVERAGE_UNKNOWN`.

## Minimal provider observation contract

For each provider observation freeze:

- observation_id;
- chain;
- token;
- pair/route if returned;
- observed_at_utc;
- provider;
- provider_schema_version/hash;
- provider_can_buy;
- provider_can_sell;
- provider_honeypot_state;
- provider_buy_tax_bps;
- provider_sell_tax_bps;
- provider_gas_estimate;
- provider_max_buy / max_sell if available;
- provider_liquidity/pair reference if available;
- unknown_fields explicitly listed;
- source response hash;
- source timestamp if provider exposes one.

Missing is UNKNOWN, never SAFE.

## Independent internal truth contract

Join provider state to existing paper-wallet execution realism by:
- chain + token + nearest admissible cutoff;
- capacity bucket;
- route/pair where known.

Internal truth should preserve:
- executable quote state;
- fill/no-fill;
- buy-side cost;
- sell-side cost;
- gas;
- token tax;
- price impact;
- reserve/depth ratio;
- stale quote state;
- route failure;
- revert reason if reproducible;
- later realized liquidity deterioration.

No later data may rewrite the provider snapshot.

## Cohort design

Start with a bounded cohort containing:
1. ordinary tradable microcaps;
2. obvious/high-risk contracts;
3. low-liquidity but technically sellable tokens;
4. tokens with restrictive tax/transfer behavior;
5. matched successful and failed launches;
6. Robinhood/Pons tokens once chain-specific source support is verified.

Do not select only known rugs.

## Primary metrics

Per provider and internal model:
- false SAFE rate;
- false UNSAFE rate;
- can-sell precision/recall;
- tax/friction estimation error;
- notional-capacity error;
- stale-state error;
- provider coverage rate;
- UNKNOWN rate;
- incremental loss avoidance;
- missed-winner opportunity cost;
- performance by chain, liquidity band and token age.

## Disagreement classes

Feed X0 DISAGREEMENT_ALPHA_V1 with:

- PROVIDER_SAFE_INTERNAL_FAIL;
- PROVIDER_UNSAFE_INTERNAL_PASS;
- PROVIDER_SELLABLE_HIGH_FRICTION;
- PROVIDER_LOW_TAX_INTERNAL_HIGH_FRICTION;
- PROVIDER_UNKNOWN_INTERNAL_KNOWN;
- PROVIDER_KNOWN_INTERNAL_UNKNOWN;
- PROVIDER_AGREEMENT_SAFE;
- PROVIDER_AGREEMENT_UNSAFE.

Later mature price/liquidity outcomes separately from mechanics truth.

## Promotion logic

Possible result:

### INTERNAL_EXECUTION_PRIMITIVE_SUPERIOR
Provider is unnecessary for canonical decision logic.

### PROVIDER_CHALLENGER_ADDS_VALUE
Provider adds incremental false-positive protection and remains challenger.

### PROVIDER_REQUIRED_FOR_GAP
Only acceptable if a material capability cannot be reproduced internally and dependency passes reliability/cost/rights audit.

### NO_INCREMENTAL_VALUE
Archive and stop.

## Falsifiers

Kill or demote if:
- direct route simulation subsumes the provider;
- provider results are too stale;
- chain coverage is too sparse;
- provider "safe" labels do not predict executable sellability;
- provider tax estimates are unstable;
- cost/latency exceeds information value;
- sample construction is dominated by retrospective known-rug selection.

## Implementation order

1. Freeze source/API semantics under SOURCE_AUDIT_V1.
2. Reuse execution_shadow_v4 capacities and mechanics state.
3. Add only the smallest provider-observation ledger required for pairwise comparison.
4. Build deterministic join and disagreement receipt.
5. Run fixtures and bounded public-source live probes.
6. Create historical replay only after timestamps/coverage are trustworthy.
7. Start prospective cohort.
8. Promote nothing until matured outcomes exist.

## Blocking / concurrency rule

Do not open a second heavy Alpha implementation while the current Ocellus/Pons research PR is unresolved.

This spec is ready; code execution should begin when the active heavy-lane gate allows it.

## Authority

No wallet signing.
No transaction submission.
No real capital.
No automatic BUY/SELL.
Provider outputs never become truth by declaration.

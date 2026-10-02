# Outputlayer Operator Target Cohort — External Reproduction Audit v1

Date: 2026-10-02
Status: SHADOW RESEARCH / EXTERNAL LEAD ADMITTED / INDEPENDENT REPRODUCTION PENDING
Owner: #1087 / #1134
Trade authority: NONE

## Executive result

The new Outputlayer/0x53a4 mission produced a high-value public external reproduction lead before Alpha Lab finished its own chain reconstruction.

A public GitHub research repository at commit `63d37fd16be47df6321363e919228490b005c36b` reports a deterministic episode-attribution method for the exact executor contract:

`0x53a42d2d0fdd60bf8f833fb94841349095a74024`

The external repository reports:
- 58 clear buy episodes found;
- 53 same-block episodes attributed to an earlier target-wallet fill;
- 25 distinct target wallets recovered, not the public ~33 claim;
- 4 examined episodes with no preceding same-block end recipient;
- 1 ambiguous episode excluded;
- a separate small-ticket method class excluded;
- operator buy episodes associated with receipt methods 0x00000007 / 0x00000009.

These numbers are external research claims until Alpha Lab independently reproduces them.

## Important new falsification

The external research does NOT support the simple story:

`good whale -> operator copies -> profit`

It reports that six of the most-frequently copied addresses are funded through Relay by the same EOA:

`0xf70da97812CB96acDF810712Aa562db8dfA3dbEF`

If correct, several apparent whales are one correlated bot fleet, not independent smart-money votes.

It further reports that the most-copied target had poor closed performance and that the external target-wallet closed records do not support the public +21.3k / 45-of-53-green performance narrative.

This is exactly why Alpha Lab must distinguish:

`TARGET_WALLET_SIGNAL_QUALITY`

from

`EXECUTOR / SAME-BLOCK EXECUTION_EDGE`.

The executor may have an execution/microstructure edge even if the copied wallets are not intrinsically strong alpha wallets.

## Comparison to our existing FOMO cohort

Alpha Lab already has a frozen 8-wallet cohort in:

`FOMO_ROBINHOOD_PROSPECTIVE_WALLET_COHORT_v0.json`

Exact-address overlap with the newly surfaced external 25-wallet set:

`0 / 8`.

Therefore:
- do NOT rewrite the old frozen cohort;
- do NOT retroactively improve its membership;
- preserve the new set as a separate external candidate dataset;
- use the existing observer/provenance/entity machinery for independent reproduction.

## Alpha Lab action

Created machine-readable candidate set:

`research/api_agent/meme_alpha/experiments/OUTPUTLAYER_OPERATOR_TARGET_COHORT_CANDIDATES_v0.json`

All 25 candidates are:
- external leads only;
- address role pending;
- economic entity pending;
- signal_eligible=false.

## Independent reproduction protocol

For each candidate operator buy episode:

1. identify an operator transaction where a non-quote token arrives at 0x53a4;
2. inspect the same block before the operator transaction;
3. find an earlier end-wallet receipt for the same token;
4. exclude pool/router/solver/hook/Relay infrastructure;
5. freeze candidate target address and evidence refs;
6. classify self-initiated trade vs passive/seeded/dust;
7. collapse common funding/control into economic entities;
8. only then allow the existing FOMO observer to consider the event.

No external wallet classification or PnL number becomes Alpha Lab truth merely because the public repo computed it.

## Live Alpha Lab evidence already independently observed

Before Blockscout MCP access became gated in the current session, Alpha Lab independently confirmed:
- 0x53a4 is a contract on Robinhood Chain 4663;
- it was created 2026-09-29;
- live repeated contract interactions continued on 2026-10-02;
- fresh token flows included MOONLET and earlier TANK/ZKSTR activity;
- the contract is called by an external EOA and interacts with shared Uniswap infrastructure.

This confirms the executor is live. It does not independently prove the 25-wallet attribution.

## Blocker

Full independent Blockscout pagination became unavailable because the current Blockscout MCP session now requires a configured PRO API key.

Fail-closed response:
- preserve the external set as candidate-only;
- do not invent missing episodes;
- do not mark unverified addresses signal eligible;
- resume deterministic reproduction when authenticated Blockscout access is restored or through another already-authorized canonical chain source.

## Next gate

P1 passes only when:
- operator episodes are independently reconstructed;
- target-wallet attribution survives infrastructure exclusion;
- correlated fleet members are collapsed;
- at least one target signal can be frozen before later outcome;
- realized/sellable outcome is measurable;
- the evidence is compared with the existing Alpha Lab champion.

Until then:
`OUTPUTLAYER_TARGET_COHORT = RESEARCH_LEAD`
`WALLET_PRECURSOR_EDGE = UNPROVEN`

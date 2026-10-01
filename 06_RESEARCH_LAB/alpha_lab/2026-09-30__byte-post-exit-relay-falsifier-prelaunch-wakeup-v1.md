# BYTE post-exit Relay falsifier + prelaunch cohort wake-up v1

Date: 2026-09-30
Status: SHADOW_RESEARCH / FRESH FORENSIC FOLLOW-UP
Owner: #1087 / existing Alpha Lab owners
Parent case: BYTE
BYTE CA: 0xd5520D9D777a42D85f94834fbea162B17A197CfB
Trade authority: NONE
Implementation authority: NONE

## Purpose

Test whether the known BYTE launch cohort can lead Alpha Lab to the operator's next launch, and preserve both the useful signal and the false lead discovered during fresh follow-up.

## 1. What remains strong from BYTE

The useful fingerprint is not a single reusable wallet.

The strong launch-time pattern remains:

- fresh / low-history wallets;
- closely timed funding;
- similar-sized preparation;
- conversion into the same quote asset before final execution;
- highly similar residual native balances;
- repeated approvals / relaunch-attempt behavior;
- tightly synchronized final Pons buys;
- a materially concentrated beneficial inventory assembled before broad distribution.

This is better described as:

`COORDINATED_PREPOSITIONING_PATTERN`

rather than:

`KNOWN_SMART_WALLET`.

## 2. Exact wallet reuse currently looks weak

Fresh Sep30 readback shows several known BYTE addresses have behaved like disposable or bounded-purpose wallets after the case:

- canonical launch caller `0xE142304Cc7A3F47106122f393DeB990F11C8D3d0` has a small transaction history and no useful evidence of a second token launch in the current read;
- cohort wallet `0x131219052b97972C6a3c8Bd2F63e4c154a07c136` sold/transferred BYTE out and later routed residual value onward;
- cohort wallet `0x3F8D24D71e630cE555Bb70228D02f4fC211698FF` similarly drained value onward;
- launch-minute wallet `0x8f05545689Ef68194d36c18328d165D122FE78DB` transferred BYTE and later routed residual value onward.

Implication:

`SAME_ADDRESS_REUSE` is not the primary next-launch detection strategy.

An operator can rotate addresses cheaply.

## 3. Fresh post-exit convergence looked promising — then failed as operator lineage

Fresh reads found several BYTE-linked wallets converging into:

`0x7d7C3EdD61628586ff47380AF40CCFE5B2C79651`

Examples observed:
- BYTE launcher sent ~0.1008 ETH;
- cohort B sent ~0.2161 ETH;
- launch-minute wallet 0x8f055... sent ~0.0080 ETH;
- smaller residual flows from other BYTE-linked addresses were also observed.

Separately, BYTE cohort A and C sent material native ETH to:

`0xC61d7ae0698E5389F584c2ad94D28232f60Ad801`

This initially looked like a possible operator collector or capital-recycling hub.

### Falsifier

Further tracing showed both paths are consistent with settlement / Relay infrastructure rather than a clean next-project operator trail.

Most decisive observation:

Fresh address:
`0x8C128017c136F0844739c3f02529FF2Ae0549E53`

Observed transaction set at review:
1. received ~0.1115 ETH from known BYTE launch-minute wallet `0xdC63cA7223632db3a28663074Aa7477a95282998`;
2. received ~1.133 ETH from `0xC61d...`;
3. received ~0.692 ETH from `0x7d7...`;
4. then deposited ~1.9365 ETH into labelled `Relay: Depository`
   `0x4cD00E387622C35bDDB9b4c962C136462338BC31`.

Additional observations:
- `0x7d7...` has high-throughput generic activity and interaction patterns consistent with routing/settlement;
- `0xC61d...` receives/sends repeated standardized native amounts across unrelated addresses;
- another shared downstream `0x513aAe13A9155E2BfeA9E5813C30f6066D6a5669` is an older generic-transfer wallet, not a fresh launch wallet.

Current conclusion:

`POST_EXIT_CONVERGENCE_TO_RELAY != NEXT_LAUNCH_OPERATOR_LINEAGE`

This is a valuable false-positive guard.

Do not follow generic cash-out / bridge / Relay destinations as alpha.

## 4. What can potentially get us earlier than broad social sharing

The highest-value prospective signal is now:

### PRELAUNCH_COHORT_WAKEUP

Look for a new cluster BEFORE or immediately around a launch where:

1. multiple fresh or dormant addresses become active in a narrow window;
2. they receive capital from non-obviously-benign sources;
3. they convert similar amounts into the same launch quote asset;
4. native residuals become unusually similar;
5. approvals / contract interactions cluster around repeated launch/relaunch attempts;
6. multiple addresses enter the same new Pons asset within seconds/minutes;
7. common-control evidence survives removal of Relay, CEX, bridge, router and other infrastructure;
8. public/project/social propagation has not yet caught up.

BYTE is valuable because parts of this preparation existed before the final canonical launch transaction.

Therefore the true lead may be:

`PREPARED_CAPITAL_BEFORE_FINAL_CA / BEFORE_BROAD_PROPAGATION`

not the final deployer wallet itself.

## 5. Critical dual-use interpretation

A coordinated pre-positioned cohort is NOT automatically bullish.

It can mean:
- informed / connected launch participation;
- operator inventory preparation;
- extraction / distribution setup;
- legitimate coordinated team allocation;
- market-making preparation.

Therefore candidate state should be:

`TIME_SENSITIVE_REVIEW_NOW`

not:

`AUTO_BUY`.

Required review before any positive interpretation:
- project legitimacy;
- sellability;
- privileged exemptions;
- beneficial inventory share;
- liquidity;
- external catalyst;
- independent wallet participation;
- operator history;
- distribution risk.

## 6. Dev-wallet research status

No dev/deployer wallet currently has enough forward evidence to be promoted as a repeatable alpha source.

Important fresh denominator/source issues:

- Bando's `58Ur...` wallet currently shows 106 Pump.fun followers / 315 following, confirming the prior source-field error;
- its current Pump.fun profile shows `Created coins 35`, materially different from the previously supplied "19 total launches / 19 graduated" claim;
- `yHCx...` currently shows a much larger created-coin count in Pump.fun UI than the historical Bando claim, showing that count semantics/time need exact definitions;
- current profile history visibly contains many weak/dead/losing positions alongside winners.

Conclusion:

`HIGH_GRADUATION_CLAIM != VALIDATED_FORWARD_DEV_EDGE`.

MadeOnSol's point-in-time deployer `as-of` feature remains a promising research challenger, not accepted truth.

## 7. Prospective experiment

### Hypothesis H-BYTE-WAKEUP

> A fresh, economically linked wallet cohort showing coordinated quote-asset preparation and launch-contract readiness before broad propagation provides earlier actionable discovery of a future high-attention launch than project/social scanning alone.

### Comparison arms

A. project/social discovery only  
B. fresh-wallet activity only  
C. fresh-wallet + quote-preparation cluster  
D. C + verified project/catalyst evidence  
E. C where cluster later proves extraction/operator inventory

Measure:
- lead time to final CA / first broad social propagation;
- market cap/liquidity at first eligible review;
- sellable MFE/MAE;
- rug/distribution rate;
- false-positive rate;
- fraction explained by benign infra;
- incremental lift over current G2 / Project->CA.

### Kill condition

Kill or downgrade if:
- most apparent prelaunch clusters collapse into Relay/router/CEX/bridge infrastructure;
- the signal appears only after public launch;
- matched controls show similar clustering;
- high false-positive/extraction exposure overwhelms incremental discovery value.

## 8. Current decision

- FOLLOW_SAME_BYTE_WALLETS_ONLY: NO
- FOLLOW_RELAY_CASHOUT_PATHS_AS_ALPHA: NO
- TRACK_BYTE_OPERATOR_BEHAVIORAL_FINGERPRINT: YES / SHADOW
- PRELAUNCH_COHORT_WAKEUP: HIGH_VALUE_PROSPECTIVE_CHALLENGER
- AUTO_BUY: NO
- TIME_SENSITIVE_REVIEW_ON_QUALIFIED_WAKEUP: RESEARCH_TARGET
- FORWARD_TEST_REQUIRED: YES

## Key learning

The operator can rotate the wallet.

It is harder to rotate the entire sequence of:
`funding -> quote preparation -> residual pattern -> approvals -> relaunch behavior -> synchronized inventory formation`.

That sequence is the candidate edge.

# Kompas Pro: source-to-decision architecture and scientific audit

**Scope:** supplied public source packet, identified as main `82f6cd830fbcd26d77e043da0ad3222abd7cae92`  
**Original owners:** integrity **#1827** · research **#1596** · Cycle Navigator/forward output **#1516** · risk/protection **#1553**  
**Status:** **READ-ONLY AUDIT — IMPLEMENTATION AND SCIENTIFIC REVIEW PENDING**

This is an audit of the supplied text, not a repository execution or current-market assessment. I have not independently verified the main commit, recomputed the supplied file hashes, opened referenced-but-unsupplied files, inspected GitHub runs, accessed private data, or contacted another model. “ASTRA HIGH” is treated as the requested audit standard—not as proof that this response came from a dispatched Astra API run.

**Independent Claude scientific review is required before adopting this audit’s research recommendations or consequential implementation changes.**

---

## 1. Executive decision

### What the supplied sources establish

Kompas has a recognizable, substantially governed architecture:

1. Autonomous evidence feeds an **Auto Market State** owner.
2. Native Handlekompas reads that state without making new provider calls.
3. Official Compass combines the current state with structured Cycle Navigator context.
4. Weekly CN and Master Monday provide distinct frozen/contextual ownership.
5. Protection, re-entry and SELL are deliberately separated.
6. Public builders project those sources into site artifacts.
7. Shadow and strategic research have separate bindings and restricted authority.

Several important safeguards are actually visible in code:

- Missing data is not universally converted to zero.
- Repeated identical hourly observations can be distinguished from genuinely flat prices.
- The current 12-hour lane explicitly says **observed momentum, not forecast**.
- Retired breadth/ETHBTC action proxies have zero action weight.
- CN prose is not parsed into protection signals.
- SELL remains unavailable without a governed decision owner.
- Original Official source clocks are preserved in several downstream checks.
- Official freezes resist ordinary rewriting.
- Shadow research does not grant action permission.

### What the supplied sources do **not** establish

They do not establish:

- a currently functioning end-to-end **LIVE** producer → issuance → Pages → consumer chain;
- a complete current source census;
- independently verified first-known histories;
- calibrated probabilistic path envelopes;
- demonstrated turn-timing or drawdown-depth skill;
- a beneficial live escalation from 3/5 to 4/5;
- a functioning dynamic buy/sell action policy;
- sufficient independent long-horizon outcomes;
- economic value after realistic delivery delays, costs and opportunity costs.

### Principal conclusion

> **The strongest justified improvement is not a more elaborate prediction engine. It is a trustworthy issuance-and-delivery chain, consistent source admission, explicit horizon semantics, and paired prospective evaluation of a small number of existing research candidates.**

The most consequential source-visible defects are:

1. **Uneven integrity verification:** Auto Market State admission is weaker than prior-Compass admission.
2. **Source-hash-only event deduplication:** CN-only protection changes can be missed.
3. **Protection state-machine gaps:** re-entry watch can disappear while risk remains elevated, and REVIEW can persist without renewed constructive confirmation.
4. **Decision-health inconsistencies:** the Official builder, Native builder and event watcher do not apply identical completeness gates.
5. **Publication truth gaps:** “request,” “issued,” “built,” “deployed” and “delivered” are not established as the same event.
6. **Public weekly admission gaps:** the top-level site snapshot consumes weekly material before proving the same custody checks used elsewhere.
7. **Semantic overstatement risks:** `NEXT_12H`, 5/5, hardcoded horizon ETAs and repeated weekly projections can look more predictive than their implementation warrants.

None of these findings justifies inventing new market thresholds, retroactively changing W46, scoring W47 from this packet, or promoting a model.

---

## 2. Evidence boundary and citation key

The following are the only inspected sources. References below use these IDs and function/section names rather than invented line numbers.

| ID | Supplied source | SHA-256 prefix |
|---|---|---|
| **S1** | `AGENTS.md` | `4c2cc641e35e` |
| **S2** | `00_ARCHIVE_CONTROL/CURRENT_PRODUCTION_DATA_AUTHORITY.json` | `a7b5ff141c1d` |
| **S3** | `scripts/data_ping/native_handlekompas.py` | `91c00f240b47` |
| **S4** | `scripts/data_ping/compass_event_refresh.py` | `7c2e5fdad9a5` |
| **S5** | `05_CYCLE_NAVIGATOR/site/build-public.mjs` | `833d6560cd41` |
| **S6** | `04_MARKET_LEARNING/handlekompas/PROTECTION_TRACKER_CONTRACT_v1.md` | `1192e597228d` |
| **S7** | `.../research/2026-11-13__W46_PULLBACK_FAILURE_RPL_V1.md` | `00a60f12bad5` |
| **S8** | `05_CYCLE_NAVIGATOR/weekly/2026/W47/CYCLE_NAVIGATOR_FORECAST_FREEZE.json` | `bc6ca7623179` |
| **S9** | Task2 `2026-11-16_ASTRA_HIGH_W46W47_FINDINGS_AND_FOLLOWUP_v1.md` | `ec4855283f9d` |
| **S10** | `06_RESEARCH_LAB/astra_program_20261116/sources/KOMPAS_G1.md` | `8eacc5ba5fe4` |

### Missing preflight material

The operational cockpit, cross-repository boundary files, current domain status files, skill implementations, current pointers and exact workflow/job receipts were not supplied.

Consequently:

- This is **not** a completed current-state repository preflight.
- Referenced files are not treated as inspected.
- Historical findings reported in S7/S9/S10 remain **reported findings**, not independently reproduced results.
- Private source authority is neither needed nor sought for this bounded audit.
- Any later task requiring unavailable private evidence must stop at that boundary rather than substitute public proxies.

### Status definitions

The requested labels combine operational status and analytical role. To avoid ambiguity:

- **LIVE:** exact current source, producer execution, persisted output and intended consumer are evidenced end to end.
- **DESCRIPTIVE:** observed-state readback, navigation translation or context; no demonstrated independent predictive/action edge.
- **SHADOW:** explicitly research-only, with no production decision or promotion authority.
- **ORPHANED:** a producer/output is evidenced, and lack of an intended consumer is established—not merely absent from this packet.
- **UNREAD:** necessary implementation, current artifact or receipt was not supplied.

**No complete chain qualifies as LIVE from this packet. No whole subsystem can responsibly be declared ORPHANED from these files alone.** Some fields and compatibility branches are potential orphan/unreachable candidates, identified below.

---

## 3. Source-bounded architecture

### 3.1 Observable graph

```text
PUBLIC CONTROL PLANE
│
├─ Current routing / operational cockpit
│    └─ Referenced, mostly UNREAD in this packet
│
├─ Autonomous source owners / collectors
│    ├─ Hourly BTC/ETH/ETHBTC
│    ├─ Rich/current breadth
│    ├─ BTC dominance
│    ├─ Settled ETF flows
│    ├─ CFGI
│    ├─ Derivatives
│    ├─ Stablecoin supply/liquidity context
│    └─ Macro / slow-cycle sources
│         Collector implementations and actual receipts: UNREAD
│
├─ Auto Market State pointer → immutable packet
│    ├─ normalized_state
│    ├─ source_health / freshness
│    ├─ predecessor and packet-to-packet deltas
│    └─ blockers / decision_context_status
│         Producer and current artifact: UNREAD
│
├─ Native Handlekompas [S3]
│    ├─ observed BTC/ETH direction
│    ├─ data/provider/budget health
│    ├─ HOLD_WAIT or HOLD_WAIT_DATA_DEGRADED
│    └─ native run → LATEST pointer
│
├─ Weekly autonomous evidence / accepted framework interpretation
│    └─ Master Monday frozen weekly package
│         Producer/ratification/freeze inputs: UNREAD
│         Site consumer verifies selected package/pointer bindings [S5]
│
├─ Cycle Navigator frozen weekly package
│    ├─ directions: 1–3d / 5–7d / 2–3w
│    ├─ strategic 21–30d and cycle 4–8w context
│    ├─ structured protection
│    ├─ weekly/daily ranges and expected closes
│    └─ optional append-only decision-projection addendum
│         Actual producer: UNREAD
│         W47 freeze artifact: supplied [S8]
│
├─ Official Compass [S3]
│    ├─ Auto State + admitted CN package + prior Official Compass
│    ├─ observed momentum / forward navigation
│    ├─ coarse bull/bear display
│    ├─ capitalization ladder
│    ├─ protection / sequential re-entry
│    ├─ SELL = UNAVAILABLE
│    └─ immutable Official + public projection + latest pointers
│
├─ Event refresh admission [S4]
│    ├─ hourly liveness / owner freshness
│    ├─ state changes / heat / missing slot / source continuity
│    ├─ decision + state + public request-status files
│    └─ actual workflow dispatch/acceptance: UNREAD
│
├─ Shadow v2 / strategic anchors
│    ├─ immutable forecast/anchor contracts referenced
│    ├─ source-bound readback implemented [S5]
│    └─ producers, current outputs and scoring: UNREAD
│
└─ Public site builder [S5]
     ├─ data/latest.json
     ├─ data/compass.json
     ├─ data/compass-event.json
     ├─ Challenger A explicit UNAVAILABLE placeholder
     ├─ premium root / legacy rollback / vnext / visual fixtures
     └─ Pages deploy → served bytes → browser/user
          Workflow, deployment, served-byte and user receipts: UNREAD
```

### 3.2 Boundary that must remain intact

The private restricted plane may supply governed evidence to its authorized owners. It does not gain market-rule authority, and this audit does not inspect it.

The public site must receive only permitted public projections. Hash verification proves integrity relative to a declared binding; it does **not**, by itself, prove that the content is authorized for publication.

---

## 4. Component status and owner map

### 4.1 Production and presentation components

| Component | Classification supported here | Proof and limitation | Original owner |
|---|---|---|---|
| Current autonomous routing | **DESCRIPTIVE governance; current resolution UNREAD** | S2 explicitly rejects manual DATA PING as default upstream. Cockpit not supplied. | #1827 / existing operational owners |
| Auto Market State producer/current packet | **UNREAD** | S3/S4/S5 consume its contract; producer and actual packet absent. | #1827 |
| Native Handlekompas | **DESCRIPTIVE implementation; LIVE unproved** | S3 `build`, `derive_market_now`, `action_context`, `write`. | #1827 / #1516 |
| Official Compass | **DESCRIPTIVE/navigation implementation; current issue UNREAD** | S3 freezes source-bound navigation. No actual current issuance supplied. | #1516; integrity #1827 |
| Master Monday | **DESCRIPTIVE weekly context; producer/current instance UNREAD** | S5 verifies package/pointer relationships and separates analytical completeness. | Existing weekly owner; #1516 interface, #1596 science |
| CN weekly forecast | **Frozen hypothesis artifact supplied; issuance/delivery UNREAD** | S8 contains W47 paths and caveats, not a full issuance/consumer receipt. | #1516 |
| Protection tracker | **DESCRIPTIVE canonical risk translation; LIVE unproved** | S3 `protection_tracker`, S6. No independent intraweek severity estimator is implemented here. | #1553 / #1516 |
| Re-entry | **DESCRIPTIVE state machine; current state UNREAD** | Sequential logic exists, but has defects described below. | #1553 |
| SELL/trim | **DESCRIPTIVE explicit unavailable capability** | S3 `sell_assessment` always returns `UNAVAILABLE`. | #1553 |
| Swing | **UNREAD** | A site module is copied, but its contents and upstream owner are absent. | #1553 / #1516 |
| Event refresh | **Admission implementation inspected; execution UNREAD** | S4 writes an admission decision, not an evidenced completed dispatch. | #1827 / #1516; operations #1156 |
| Shadow v2 | **SHADOW contract/readback; producer/current forecast UNREAD** | S5 preserves research-only authority and checks bindings. | #1596 |
| Strategic 21–30d | **DESCRIPTIVE governed navigation / research context; current anchor UNREAD** | S5 consumer inspected. S10 reports an original NO_EDGE anchor. | #1516 / #1596 |
| 4–8w cycle context | **DESCRIPTIVE; eligible asset-specific forecasts unproved** | S3 consumes CN `weeks_4_8`; S10 reports an unavailable original asset forecast. | #1516 |
| Kompas live formula display | **SHADOW policy exception; implementation UNREAD** | S1 names one owner and strict expiry/no-decision conditions. Script absent. | Existing registered owner; #1516 / #1596 |
| Challenger A public slot | **SHADOW, explicitly UNAVAILABLE in builder** | S5 writes `NO_GOVERNED_IMMUTABLE_ISSUANCE_ON_MAIN`. | #1596 / #1516 |
| Site bundle | **DESCRIPTIVE build implementation; production deployment UNREAD** | S5 writes files and copies clients; no Pages receipt supplied. | #1516 / #1827 |
| Actual human delivery | **UNREAD** | Neither Git commit nor successful build establishes it. | #1516 / #1827 |

### 4.2 Signal-family graph

| Family | What S3 actually consumes | Observable role | Status and key restriction |
|---|---|---|---|
| **BTC/ETH spot** | Hourly prices and packet deltas | Observed direction; reference prices; evidence snapshot | **DESCRIPTIVE** downstream; collector/current rows **UNREAD** |
| **ETHBTC** | Ratio and change | Relative-strength description; retired proxy shown with zero action weight | **DESCRIPTIVE**, not a top-up permission |
| **Breadth** | Current/rich aggregate ratios, counts, equal-weight return | Evidence snapshot and WHY text | **DESCRIPTIVE**; retired action weight is zero |
| **BTC dominance** | Value and timestamps | Evidence snapshot | **DESCRIPTIVE**; no direct action logic shown |
| **ETF flows** | Settled BTC/ETH totals, session date, retrieval time | Evidence snapshot | **DESCRIPTIVE**; PIT eligibility not established by session date |
| **CFGI** | Market/BTC/ETH scores and market classification | Evidence snapshot/provider health | **DESCRIPTIVE**; no direct forecast formula shown |
| **Derivatives** | BTC/ETH OI and funding | Evidence snapshot | **DESCRIPTIVE**; funding first-known remains explicitly unknown |
| **Liquidations/order-book depth** | No direct selected-feature implementation shown | Unknown | **UNREAD**, not silently included under “derivatives” |
| **Stablecoin liquidity** | Total supply/stock | Evidence snapshot | **DESCRIPTIVE**; not demonstrated deployment or buying pressure |
| **Macro** | No macro feature is selected in the inspected `evidence_snapshot` | May exist upstream or in other owners | **UNREAD in this executable chain**; S10 supports only bounded context claims |
| **Rotation** | Native posture → fixed capitalization ladder; CN cycle states | Navigation/permission presentation | **DESCRIPTIVE**, not demonstrated measured transmission |
| **News/social/TechDev** | No inspected direct consumer | Research references only | **UNREAD/SHADOW**, depending on referenced owner |

**Important:** “Not used directly in S3” does not prove a family is absent upstream or from the CN producer. It proves only that no such direct computation is visible in this supplied implementation.

---

## 5. Decision semantics: what Kompas presently means

### 5.1 `NEXT_12H` is not a 12-hour forecast

S3 is explicit:

```text
NEXT_12H_NOWCAST_SEMANTICS = OBSERVED_MOMENTUM_NOT_FORECAST
predictive_edge_status = NOT_PROVEN
eta = None
reassessment_window = 0-12h
```

The direction comes from BTC/ETH changes since a prior Auto State packet. That is an observation over a governed comparison interval—not a prediction of the next twelve hours.

#### Improvements already visible

- Public projection rejects missing/legacy semantics as forward forecasting.
- A future price-event ETA is not generated.
- Repeated same-hour zero changes can become `UNCHANGED_NO_NEW_OBSERVATION`.
- The conclusion says “not a 12h forecast.”

#### Residual risks

1. The field remains named `NEXT_12H`.
2. One expected-path string still says “current-state continuation.”
3. `SCORED_HORIZON_ORDER` includes `NEXT_12H`.
4. Official output retains `outcome_maturity["12h"] = PENDING_MATURITY`.
5. The scoring implementation is absent.

These do **not** prove that the current scorer improperly scores the nowcast. They establish a contract ambiguity that must be resolved across the unread scorer and consumers.

**Required treatment:** current-policy observed momentum must not enter a forward-forecast win rate. An explicitly registered “momentum persistence benchmark” would be a different research object, with a separate frozen target—not a relabeling of these observations.

### 5.2 5/5 is not a neutral probability estimate

S3 `_bull_bear_row` maps:

- UP → 7/3;
- DOWN → 3/7;
- SIDEWAYS or MIXED → 5/5;
- NO_EDGE or UNAVAILABLE → unavailable.

`_bull_bear_bias(5, 5)` then labels the display `NEUTRAL`.

Consequences:

- **MIXED is collapsed into NEUTRAL.**
- The scale is not an empirical probability.
- It is not five independent bullish and five independent bearish evidence items.
- It is a coarse visual encoding of a categorical direction.

The W47 freeze also uses 3/7 with `LEAN_BEARISH`, while the inspected Official mapping would label the same difference `BEARISH`. That is a **cross-surface naming inconsistency**, not evidence that either is statistically calibrated.

**Recommended presentation:** show the source direction explicitly—e.g. “MIXED; display balance 5/5”—and never imply measured neutrality or a 50% chance.

### 5.3 Static HOLD is an implemented authority ceiling

S3 `action_context` produces only:

- `HOLD_WAIT`;
- `HOLD_WAIT_DATA_DEGRADED`.

It deliberately refuses to reactivate retired breadth/ETHBTC gates.

Therefore, in the native construction path shown:

- PREPARE is not generated.
- GRADUATED_TOPUP_ACTIVE is not generated.
- The proactive ladder branches are not newly reachable.
- New re-entry REVIEW cannot open through the required constructive posture.
- SELL remains unavailable.

This is not necessarily a coding mistake. It is an explicit governance choice. But it is a **capability gap** if the product is described as a dynamic action system.

> **HOLD for new risk is not SELL for existing holdings. A bearish direction plus HOLD is not an executable protective exit policy.**

The correct fix is not to reconnect retired proxies. It is to identify an existing authorized action owner—or keep the capability unavailable.

### 5.4 Forward direction and action permission are not fully separated

In `horizon_map`, a CN 1–3d SIDEWAYS direction can become UP when posture is PREPARE or GRADUATED_TOPUP_ACTIVE.

That branch is not newly reachable through the present `action_context`, but the transformation is still a latent semantic problem:

- permission to prepare should not alter a source forecast’s direction;
- direction, permission and confidence need independent fields.

### 5.5 Hardcoded ETA strings are horizon labels

`24-72h`, `120-168h`, `14-21d` and ladder strings such as `1-7d conditional` are not estimated turn times.

They should not be presented as:

- when a pullback will start;
- when a low will form;
- when rotation will reach smaller caps;
- when recovery will complete.

Protection ETA is appropriately UNKNOWN unless a structured owner supplies it. The same discipline should govern all other displayed “ETA” fields.

---

## 6. Source integrity, missingness and freshness findings

### 6.1 Auto State verification is materially weaker than prior-Compass verification

S3 `load_prior_compass` verifies:

- pointer contract;
- path containment;
- exact content SHA-256;
- artifact contract;
- canonical self-digest;
- ID/path/time consistency.

By contrast, `load_auto_state` and `load_auto_state_bundle` primarily compare:

```text
pointer.packet_sha256 == packet.packet_sha256
```

They do not recompute that digest in the inspected functions. They also lack equivalent path containment and contract/identity checks.

S4 `run` reads the Auto State target directly without even using those loaders.

**Static failure case:** modify packet contents while leaving the embedded digest and pointer digest unchanged. These admission functions do not detect the modification themselves.

An upstream validator may exist, but it is unread and cannot substitute for a clear consumer trust boundary.

### 6.2 Unknown validation can pass structural health

`_health_ok`, `action_context` and `build` accept `validation_status != "FAIL"` rather than an explicit admitted set.

Thus a packet with:

- unknown/missing validation status;
- `decision_context_status == PASS`;
- no blockers;
- acceptable hourly freshness;

can pass the shown structural gate.

A deliberate degraded-but-decision-eligible state may be legitimate. The remedy is an explicit schema-defined admissible set, not a blanket requirement that every optional lane be perfect.

### 6.3 Mapping integrity is assessed too late and inconsistently

`build_official_compass` computes horizons, ladder and protection before checking:

```text
evidence.mapping_integrity_status
```

It may then mark the packet DEGRADED while retaining fields generated under the earlier health decision.

The event watcher calculates current data status from owner health and CN admission, without the same evidence-mapping check.

This creates a reproducible inconsistency:

- event watcher can regard the candidate as OK;
- Official builder can label the result DEGRADED;
- navigation fields may still be populated.

Required-field eligibility must be decided once and reused across these surfaces.

### 6.4 Null and zero handling is partly strong, partly incomplete

**Good:** `finite` rejects booleans, non-numeric values and non-finite numbers. Zero is retained.

**Remaining problems:**

- `derive_market_now` maps missing BTC or ETH deltas to MIXED rather than a separately identified incomplete observation.
- `new_price_observation` becomes true whenever the narrow “same observation plus zero deltas” condition is false. Missing timestamps do not establish a new observation.
- Same observation timestamps with nonzero deltas are not explicitly rejected.
- Comparison-interval duration is not exposed as a validated property.

A flat market, a repeated bar, an incomplete packet and a contradictory revision are different states.

### 6.5 Breadth can become a mixed-provenance vector

`evidence_snapshot` falls back independently from current breadth to rich breadth for ratio, advancers and decliners. It then uses a shared selected timestamp/source description.

That can combine components from different observations or owners into one apparent snapshot.

Further, health is taken from the `breadth` lane even when `current_breadth` supplies the value.

**Needed:** each selected value must retain the provenance and freshness of the exact source row that supplied it. A coherent aggregate should be selected atomically where the contract requires one.

### 6.6 Funding correctly distinguishes settlement from knowledge—but eligibility remains ambiguous

S3 `_funding_clock_metadata` explicitly says:

- settlement time is separate;
- capture is not provider first-known;
- quote status can be `UNKNOWN_NOT_PIT_ADMITTED`.

That is scientifically sound.

However, the surrounding `_feature` can still label funding `ELIGIBLE_PRESENT` from a general derivatives PASS status.

Presence, current descriptive usability and historical PIT admission must not share a single eligibility label.

### 6.7 CN content integrity is not CN temporal eligibility

`load_cn_context` verifies package bytes against the pointer and checks issue number. This is substantially better than the Auto loader.

It does not, in the inspected implementation, establish:

- package contract and full schema validity;
- issue/forecast origin time;
- current horizon expiry;
- original first publication;
- per-lane temporal eligibility;
- path containment equivalent to prior Compass.

A correctly hashed old package is still old.

### 6.8 Fresh hourly evidence must not renew an old weekly forecast

Official Compass can be reissued with fresh Auto State while consuming the same weekly direction. The shown horizon projection has no explicit origin/expiry enforcement for each CN lane.

Therefore:

> A current Official issuance time must not silently turn an early-week 1–3d hypothesis into a fresh late-week 1–3d forecast.

The actual upstream producer may handle this, but that proof is absent. The consumer contract needs origin, target interval and expiry fields—not just a direction and a new display time.

### 6.9 Provider absence is not proven health

`classify_provider_health` returns overall PASS if it finds no issue rows. An absent or empty health map therefore looks clean at that level.

The CFGI fallback is more cautious—`PASS_OR_NOT_EXPLICITLY_DEGRADED`—but that still should not be consumed as verified availability.

Budget handling is better: exact spending remains UNKNOWN when no account ledger is bound.

---

## 7. Protection, alert escalation and event-refresh audit

### 7.1 Protection is a pass-through, not an independent breach detector

S3 `protection_tracker` reads structured CN protection. It does not compute risk severity from every new price breach.

This explains how ELEVATED can persist while prices deteriorate. It does **not** prove:

- that the upstream CN producer is defective;
- that 4/5 was warranted at a particular earlier time;
- that an escalation would have reached a user;
- that an associated action would have helped.

The unread upstream CN risk producer is therefore a critical dependency.

### 7.2 Two re-entry state-machine defects are visible

#### A. Reclaim watch can disappear while risk remains elevated

A possible sequence:

1. HIGH → WAIT_FOR_FLUSH.
2. ELEVATED after HIGH → WAIT_FOR_RECLAIM.
3. ELEVATED again → falls through to INACTIVE.

The second ELEVATED observation does not meet the branch restricted to NORMAL/BUILDING, and prior risk is no longer HIGH.

That loses the outstanding reclaim requirement without constructive confirmation.

#### B. REVIEW can persist without constructive confirmation

When prior re-entry is REVIEW and risk is NORMAL/BUILDING, the code keeps REVIEW without checking current posture or bullish direction.

The message says constructive confirmation persists, but that persistence is not tested.

This is especially important for a valid historical prior REVIEW or a future authorized action owner. It should not be dismissed merely because the current Native constructor cannot newly open REVIEW.

### 7.3 Event deduplication can suppress CN-only protection changes

S4 returns early when Auto State source hash equals the source hash bound to the latest Compass, unless a scheduled freeze is judged missing.

That return happens before comparing the current CN protection.

**Concrete static counterexample:**

- same Auto packet;
- newly valid CN package or addendum;
- protection changes ELEVATED → HIGH;
- no missing scheduled slot.

The watcher can return `LATEST_COMPASS_ALREADY_BINDS_CURRENT_OWNER_PACKET` without evaluating the protection transition.

Deduplication must bind the **decision context**, not only the Auto packet.

### 7.4 Protective bypass can repeatedly request the same pending transition

Protective transitions bypass normal in-flight suppression.

That is reasonable for a genuinely new deterioration. But while the old Official issue remains current, the same unresolved transition can continue to look new relative to that issue.

The necessary distinction is:

- same pending protective episode → deduplicate;
- materially worse new protective state → permit bypass.

A dispatch timestamp alone is not an episode identity.

### 7.5 Request truth is not dispatch truth

S4 `run` records request state and public `REASSESSMENT_REQUESTED` when `decision.dispatch` is true.

The supplied file does not perform an evidenced workflow dispatch or verify its acceptance. Comments say legacy fields mean “workflow dispatch accepted,” but that acceptance is not established inside this implementation.

An unread workflow may complete the chain. Until inspected, the honest states are:

```text
ADMITTED
→ DISPATCH_ACCEPTED
→ PRODUCER_STARTED
→ ISSUED
→ BUILT
→ DEPLOYED
→ SERVED
```

Each needs its own receipt or explicit unknown.

### 7.6 Missing-slot recovery is useful but not a schedule receipt

S4 correctly recognizes that:

- a delayed cron may succeed while skipping its intended slot;
- recovery must issue at the actual current time;
- the forecast must not be backdated.

However:

- latest issue time is not proof of the scheduled slot’s execution;
- a missing/invalid original issue time returns no demonstrated miss;
- `run` requires a valid prior Compass, so first-issuance recovery is not shown;
- the actual cron, timezone gate and dispatch workflow are unread.

The code’s 08:17/20:17 Copenhagen schedule is an implemented expectation, not evidence that production runs at those times.

### 7.7 Event input health also needs custody

The hourly liveness checker validates pointer metadata and completeness counters. It does not authenticate underlying hourly bytes.

Entry heat is read from an unbound `LATEST` object in the supplied `run`. Missing values default toward NORMAL, which can affect episode rearming.

Neither a stale Entry row nor an unauthenticated hourly pointer should create a fresh market-event assertion.

### 7.8 Public request status can outlive the request

The inspected code writes public event status on dispatch but does not show clearing it when a new Compass binds or the request fails.

Another component may do this; it is unread.

The public message also defaults to “material market move or decision-state change” for several non-price causes. Health-only degradation should not be described as a market move.

---

## 8. Official issuance and site delivery

### 8.1 Official output-root ambiguity

S3 defines `DEFAULT_OFFICIAL_ROOT`, but CLI `--output-root` defaults to `DEFAULT_ROOT`.

Invoking `--official-daily-compass` without an explicit output root can therefore write outside the `.../official/` route consumed by the site and event watcher.

This is a concrete interface hazard. Whether production avoids it depends on unread workflow arguments.

### 8.2 Immutable freezes are not fully concurrency-safe

`_immutable_write` is a check-then-write operation. It is not shown as an atomic exclusive creation.

The Official writer also updates multiple latest pointers without a demonstrated atomic transaction or monotonic issuance check.

Potential failures include:

- concurrent writers racing on first creation;
- partial pointer publication;
- an old morning-slot retry repointing LATEST after a newer evening/event issue.

Scheduled-slot reuse is correct for preserving the original freeze. It must not also regress the current pointer.

### 8.3 On-demand reuse has weaker custody and path handling

The on-demand reuse path reads a path from the latest pointer using the process working directory and does not apply the full prior-Compass verification before selection.

This differs from the stronger `load_prior_compass` boundary and from `repo_root`-based loading elsewhere.

Use one verified loader and one path convention.

### 8.4 The site has strong checks—but not uniformly

S5 includes valuable defenses:

- public projection content hash and ID checks;
- more complete public/internal binding comparison in full-stack readback;
- verified original Official freshness policy;
- source-bound Native and Shadow artifacts;
- Master Monday machine-package verification;
- explicit distinction between Monday source alignment and analytical completeness;
- no automatic conversion of Shadow into Official action.

But several gaps remain.

#### A. Top-level weekly snapshot is consumed before equivalent verification

At the top level, S5:

1. reads the CN pointer;
2. resolves `week_dir`;
3. reads the package;
4. checks issue number;
5. builds `latest.json`.

This path does not first enforce the containment and exact package hash checks used later in full-stack readback.

Thus `full_stack.weeklyAligned == false` does not necessarily prevent unverified weekly content from entering the separate public snapshot.

#### B. Standalone freeze and score artifacts have incomplete visible binding

The standalone freeze, range score, public scorecard and parts of public-series history are read without a complete visible immutable manifest binding.

The prospective-range helper may add protections, but its contents were not supplied.

#### C. Verified does not necessarily mean currently fresh

`officialValid` can be true while the original source deadline has passed. The builder exposes expiry metadata but does not itself suppress all expired action fields.

Unread clients may enforce the expiry. Their behavior cannot be assumed.

The same issue applies to strategic anchors and to Shadow’s hardcoded age checks, which are not visibly equivalent to every original owner deadline.

#### D. Hashes do not sanitize strings

Some paths use strong enumerations and restrictive `publicNarrative` filtering. Others pass through:

- protection drivers and invalidation text;
- pullback class;
- selected weekly prose;
- full scorecard/range objects.

This is not proof of a privacy leak. It is proof that publication safety depends on additional upstream contracts or tests not supplied here.

#### E. Some labels are not fully source-bound

- Shadow model is rendered as a hardcoded `"GPT-6.1 Sol"`.
- Native public enum omits several producer vocabulary states, including `HOLD_WAIT_DATA_DEGRADED`.
- Official/projection identity checks are not uniformly as complete as the Python prior-Compass loader.

Presentation should reflect verified metadata and preserve meaningful fail-closed states.

### 8.5 Pages receipts are absent

The supplied build file proves what it intends to write—not what was served.

Minimum production closure requires:

1. exact source commit and artifact inputs;
2. actual build run/job/step receipt;
3. resulting bundle manifest;
4. Pages deployment ID and completion time;
5. readback of served `latest.json`, `compass.json` and relevant page assets;
6. verified issue ID, source deadline, labels and bytes;
7. a consumer receipt appropriate to the claim.

A successful public GET proves availability at that observation time. It does not prove the first user saw it then, or that any person acted.

---

## 9. W46, W47 and long-range evidence: admissible conclusions

### 9.1 W46 is one exposed, dependent development week

S7 documents an intraperiod breach and explicitly says Friday and the week were partial at that observation.

S9 later reports five dependent post-issue daily closes, 10–14 November:

| Reported result | BTC | ETH |
|---|---:|---:|
| CN point MAE | 4,145.080 USDT | 146.926 USDT |
| Fixed-price B0 MAE | 3,940.960 USDT | 143.242 USDT |
| CN relative disadvantage | 5.18% | 2.57% |
| CN close coverage | 2/5 | 0/5 |
| Same-width B0 close coverage | Same reported coverage | Same reported coverage |

These are **S9-reported calculations**, not reproduced here.

What follows:

- CN did not beat that simple point baseline on the supplied reported development rows.
- Wide-range “success” is not enough; the width-matched comparison matters.
- Already-bearish direction did not ensure adequate downside magnitude or recovery-path accuracy.
- A persistent ELEVATED warning did not constitute SELL authority.

What does **not** follow:

- five independent trials per asset;
- ten independent outcomes across BTC and ETH;
- a general finding that CN never works;
- proof that a 4/5 warning would have improved outcomes;
- proof of executable after-cost utility;
- a valid new holdout result.

W46 is exposed development material. Its thresholds, templates and failures must not be optimized and then presented as untouched validation.

### 9.2 Original and amended W46 versions must remain separate

S7 reports:

- an earlier 0/7 expected-close issue;
- a later 7/7 expected-close issue on November 9;
- different issuance histories for low/high paths and expected closes.

Therefore each field family needs its own original availability clock.

Earlier Monday prices cannot be evaluated as if the later expected-close forecast already existed. Git first-add also does not establish original venue publication or user delivery.

### 9.3 Reported historical warning counts are not a clinical performance table

S7 cites prior Claude findings:

- HIGH: 0/359 historic eligible classifications;
- ELEVATED: 42/244 followed by a ≥5% 72-hour drop;
- roughly 51.8% valid Official source coverage over the inspected seven-day period.

These were not reproduced in S7 or here.

They do not directly establish:

- specificity;
- a false-alarm rate;
- independent event count;
- sensitivity to all qualifying drawdowns;
- safe alert frequency.

Consecutive ELEVATED rows can belong to one episode. The ≥5% outcome also differs from the separately referenced 4%/72h shadow barrier.

### 9.4 W47 is not scoreable from this packet

S8 supplies a deterministic seven-day BTC/ETH scenario:

- explicit daily expected closes;
- daily low/high bands;
- broader weekly envelopes;
- conditional retest/stabilization/recovery prose;
- no calibrated probability claim.

It does not supply a verified original issue timestamp, immutable issuance receipt, first served time or completed outcomes.

S9 reports that CN and Challenger A were separate issued research objects. S5, however, writes an explicit unavailable Challenger A public slot.

These are not automatically contradictory:

- they may concern different source snapshots or delivery surfaces;
- an issued research artifact need not be connected to the public slot.

**Required reconciliation:** inspect the exact original Challenger artifact, its source/issue clocks and the builder/deployment that consumed—or did not consume—it. Do not assume publication from the report alone.

W47 remains **NOT SCORED HERE**.

### 9.5 Long-range G1 is a feasibility warning, not an edge result

S10 reports:

- 56 source-eligible Shared Row rows;
- 40 matured 7d rows;
- key comparisons spanning one prospective block and one regime;
- no jointly admitted long-horizon feature/issuance cohort;
- an original November 9 strategic anchor with 21–30d NO_EDGE and 4–8w UNAVAILABLE.

Those are not a 21–30d or 4–6w evaluation sample.

An issued NO_EDGE is an abstention. It must not become:

- a successful flat prediction;
- a failed bullish prediction;
- a synthetic incumbent direction;
- a zero-return forecast.

The 1–12 month validator is reported as offline design, not a connected forecast producer or scorer.

---

## 10. Horizon-by-horizon capability assessment

| Horizon | Observable basis | What can legitimately be claimed | Missing capability |
|---|---|---|---|
| **Observed / “12h”** | Latest governed BTC/ETH comparison | Current momentum and reassessment window | Genuine frozen 12h predictive target and demonstrated edge |
| **1–3d** | Structured CN direction; generic path text | Source-owned short-horizon hypothesis when temporally eligible | Asset-specific calibrated path/depth/turn distribution and exact origin |
| **5–7d** | CN weekly direction and frozen weekly scenarios | Frozen weekly hypothesis | Adequate independent paired outcomes, calibrated ranges, complete delivery |
| **2–3w** | Structured CN lane or explicit NO_EDGE/UNAVAILABLE | Conditional navigation, abstention preserved | Original asset-specific distributions and matured independent cohort |
| **21–30d** | Governed strategic weekly anchor | Only the actual issued strategic content | Eligible incumbent directions, PIT macro/flow rows, adequate outcomes |
| **4–6w** | No dedicated supplied forecast; broader CN 4–8w owner | At most clearly labeled context within the existing owner | Explicit 28/35/42-day targets; cannot infer them from 4–8w prose |
| **4–8w cycle** | CN-owned altcoin state/warning | Cycle navigation under Main Framework permission ceiling | Reliable asset-specific price path, turn ETA or rotation timing |

### Path envelopes are not turn forecasts

A path can have acceptable endpoint error and still miss:

- the timing of the trough;
- maximum drawdown;
- breach depth;
- duration underwater;
- order of retest and recovery.

Conversely, an extremely wide band can contain prices while conveying little information.

A smooth daily recovery template is not evidence of predictive turning-point skill. W47’s day-specific precision must remain labeled as an uncalibrated deterministic scenario unless independently validated otherwise.

---

## 11. First-known and PIT: required clock model

Every source-to-decision row should distinguish these clocks:

| Clock | Meaning | What it does not prove |
|---|---|---|
| `observation_start/end` | Period measured | When the value became knowable |
| `settlement_at` | Economic settlement | Provider publication |
| `provider_published_at` | Provider first released this vintage | Collector possession |
| `collector_captured_at` | System demonstrably possessed it | Earliest vendor availability |
| `normalized_available_at` | Admitted transformed row existed | Original source publication |
| `forecast_issued_at` | Exact forecast frozen | Public availability |
| `git_first_added_at` | Artifact reached recorded Git history | Original issuance or user delivery |
| `deployed_at` | Deployment completed | Every client received new bytes |
| `first_verified_served_at` | First observed served version | First human viewing |
| `consumer_received_at` | Intended consumer received it | Feasible or executed trade |
| `first_feasible_action_at` | Earliest admissible paper action | Actual fill |

For a forecast issued at \(t_0\), all required inputs must have an admissible system-availability time no later than \(t_0\).

When vendor first-known is unknown but an immutable capture predates issuance, that may prove **system possession by capture time**. It must not be relabeled as vendor first publication.

### Specific source restrictions

- **ETF:** session date is not knowledge time. S10 reports the pre-capture PIT restriction and later double-read requirement.
- **Funding:** settlement time is not quote publication; S3 correctly preserves this distinction.
- **Macro:** revised series need period-legal vintages.
- **Policy expectations:** realized policy rates are not the expected future rate path.
- **Breadth:** historical constituent membership must be frozen; today’s universe cannot be applied backward.
- **BTC.D:** source conventions cannot be mixed under an absolute threshold.
- **Copper/gold:** monthly averages are not continuous futures timing signals.
- **Stablecoins:** supply stock is not deployed liquidity.
- **Venue flow:** exchange taker flow is not global buying/distribution.

---

## 12. Source-legal scientific design

This is a **design proposal for existing owners**, not activation of a new experiment. S10’s foundation restrictions and S1’s Round 3 `PROSPECTIVE_COLLECTION_ONLY` / scoring OFF remain binding.

### 12.1 Start with an issuance census, not a model contest

The first task is S10’s existing `SC_ISSUANCE_ELIGIBILITY_G1` concept:

- exact original issue IDs and bytes;
- original versus amended versions;
- scheduled slot versus actual issue;
- per-horizon asset direction or abstention;
- source/knowledge clocks;
- publication and consumer evidence;
- maturity;
- reason-coded exclusions.

Outputs must include:

```text
ISSUED_ELIGIBLE
ISSUED_ABSTENTION
NO_ISSUANCE
SOURCE_BLOCKED
DELIVERY_UNKNOWN
PENDING_MATURITY
OUTCOME_UNAVAILABLE
```

Do not delete unissued, censored or inaccessible rows from the denominator.

### 12.2 Freeze precise targets

| Lane | Example target definition to preregister |
|---|---|
| 1–3d | Price/return at 24, 48 and 72 hours from genuine issue time |
| 5–7d | 120, 144 and 168 hours, or a clearly separate calendar-week target |
| 2–3w | 14 and 21 days |
| 21–30d | 21 and 30 days from the governed strategic issue |
| 4–6w | 28, 35 and 42 days only if explicitly authorized within the CN owner |

Calendar-week and rolling-horizon forecasts must not be pooled as interchangeable.

For each target, define:

- quote and venue convention;
- completed bar/close rule;
- allowable missingness;
- nominal interval interpretation, if any;
- event window;
- maturity and invalidation rules;
- source deadline versus forecast target deadline.

### 12.3 Paired baseline trials

Reuse the existing equal-width implementation identified in S7 rather than creating another.

**B0 — no-change point baseline**

The most recent admissible completed price known at issuance.

**B0-width — width-matched range control**

Use the candidate’s frozen width under a predeclared recentering rule, without using future prices. Report asymmetric-band handling explicitly.

**B-vol — cheap volatility-only control**

Predeclared ATR/EWMA or empirical return quantiles using only source-legal pre-issue history. No parameter selection after the event.

**B1 — actually issued incumbent**

Use the original CN/strategic forecast only where one genuinely exists. NO_EDGE and UNAVAILABLE remain abstentions.

**Candidate families**

Only existing registered candidates, with:

- identical issue times;
- identical legal target data;
- common eligible rows;
- separately reported coverage losses;
- fixed versions;
- no post-outcome candidate selection.

A sparse model cannot “win” because the full model lacks data. A full model cannot win by using later-arriving ETF or macro information.

### 12.4 Point and range metrics

For point forecasts:

\[
MAE = \frac{1}{n}\sum_i |\hat y_i-y_i|
\]

Report paired loss differences:

\[
\Delta_i=L_{\text{candidate},i}-L_{\text{baseline},i}
\]

Negative values favor the candidate.

Report:

- raw-price MAE per asset;
- return-scale error;
- optional ex-ante-volatility-scaled error;
- sample coverage and abstention;
- block-level uncertainty.

Do not use a lower error on a hand-selected subset as a broad improvement claim.

For non-probabilistic scenario bands, report:

- width;
- close coverage;
- intraperiod coverage separately;
- first breach;
- breach magnitude;
- time outside;
- maximum downside excursion.

Do not relabel source min/max bands as 90% intervals.

### 12.5 WIS only for genuine nominal distributions

For a central interval \([l,u]\) with miscoverage \(\alpha\):

\[
IS_\alpha =
(u-l)
+\frac{2}{\alpha}(l-y)\mathbf 1(y<l)
+\frac{2}{\alpha}(y-u)\mathbf 1(y>u)
\]

For median \(m\) and \(K\) nominal central intervals:

\[
WIS =
\frac{
\frac12|y-m|
+\sum_{k=1}^{K}\frac{\alpha_k}{2}IS_{\alpha_k}
}{
K+\frac12
}
\]

This is appropriate only when the levels and forecast distribution were frozen before outcomes.

S9 reports Challenger A nominal 50/80/95% bands. That does not establish their calibration, correct issuance clocks or eligibility. Those must be checked before computing or interpreting WIS.

### 12.6 Direction, turns and depth need separate tests

**Direction**

- UP/DOWN/SIDEWAYS target rule frozen ex ante.
- A neutral zone based on a predeclared economic/noise convention.
- Balanced metrics if classes are imbalanced.
- NO_EDGE/UNAVAILABLE not treated as directional predictions.

**Turns**

- Define what counts as a trough/peak.
- Define required subsequent reversal and confirmation window.
- Use one-to-one matching of warnings and realized events.
- Report late and missed turns.
- Never credit the ex-post deepest wick as an executable entry/exit.

**Depth**

- Maximum adverse excursion from issue or delivered-warning time.
- Threshold-crossing time.
- Time underwater.
- Recovery within a specified window.
- Separate downside depth from endpoint return.

### 12.7 Event independence

BTC and ETH during one market shock are not independent replications.

Neither are:

- seven daily points from one weekly path;
- hourly reissues of the same weekly thesis;
- overlapping 72-hour warning windows;
- multiple thresholds triggered by one selloff.

Use predeclared event/week blocks, purge overlapping train/test windows, and embargo where target windows overlap.

Report both:

- raw row count;
- independent event/block count.

S7’s 26-week collection target and S9’s eight-week review point are collection/checkpoint proposals—not statistical power guarantees.

---

## 13. Pullback 3/5 → 4/5 and the false-alarm budget

### 13.1 First verify the scale mapping

The supplied backend has risk enums and an internal rank. The actual public five-point stage renderer is not supplied.

Do not assume the internal rank numerically proves the public mapping. Bind the exact stage mapping first.

### 13.2 A valid shadow escalation question

> At the same eligible times and the same warning budget, does a predeclared escalation candidate provide earlier delivered warning of independently defined downside events than the existing risk state and a cheap price/volatility baseline?

This is narrower and testable.

It does not ask whether a hindsight 4/5 label would have looked more appropriate during W46.

### 13.3 “Clinical” discipline means operational burden, not medical validation

Treat alerts as a limited resource:

- false alarms consume attention;
- prolonged warning states induce fatigue;
- late warnings provide little preventive value;
- false exits can miss recoveries;
- incessant high severity becomes non-discriminating.

Predeclare, with the risk owner:

1. an allowed number of **independent false-warning episodes per 30 eligible days**;
2. maximum time spent in an elevated/high warning state;
3. episode rearm/cooldown rules;
4. a minimum useful delivered lead time;
5. acceptable missed-event burden;
6. explicit action-cost assumptions for any paper utility test.

A numerical budget must be owner-approved before evaluation. It cannot be inferred from the supplied data.

For intuition only: with a hypothetical 2% event base rate, 80% sensitivity and 90% specificity, positive predictive value is only about 14%. High apparent sensitivity does not make alerts useful when events are rare.

### 13.4 Evaluate at an equal alert budget

Compare candidate and baseline on:

- event sensitivity;
- first delivered-warning lead time;
- false-warning episodes per eligible month;
- warning occupancy;
- missed drawdowns;
- false exits and missed recoveries, if an action policy exists;
- burden-adjusted paper utility.

A model that raises HIGH more often must not get credit merely for greater coverage.

### 13.5 Do not count correlated evidence as independent confirmation

Likely dependencies include:

- BTC/ETH returns, momentum, volatility and price structure;
- ETHBTC algebraically derived from BTC and ETH;
- breadth, dominance and rotation measures sharing market-cap/price effects;
- funding, OI and liquidation indicators from one venue;
- ETF totals and persistence derived from the same releases;
- multiple macro transforms from the same revised series.

Use source-lineage families, training-only correlation estimates, leave-one-family-out tests and block-level incremental loss.

A “five-family” model is not five independent votes simply because five columns have different names.

---

## 14. Rotation and macro: falsifiable research, not narrative escalation

### Rotation

A credible rotation hypothesis needs separate measurements of:

1. ETH-relative leadership;
2. large-cap participation;
3. mid-cap transmission;
4. small/microcap participation;
5. persistence and liquidity quality.

The inspected ladder does not measure these transitions. It maps posture to static permission tiers.

A valid research test would ask whether source-legal relative strength and cohort breadth add incremental information over BTC/ETH price and volatility—not whether a visually appealing ladder tells a coherent story.

Historical membership, delistings, stablecoin exclusions and thin-liquidity failures must remain in scope.

### Macro

Symmetric hypotheses are essential:

- rising yields can reflect inflation/risk tightening;
- they can also reflect resilient growth;
- liquidity stock can rise without risk-asset deployment;
- credit deterioration can arrive with revision and publication lag.

A macro candidate must use the actual instrument/vintage corresponding to the hypothesis.

If expected policy-path repricing is the feature, realized overnight rates or analyst prose are not substitutes.

S10’s negative ETF and copper/gold findings should be retained as negative priors/controls—not repackaged as extra bullish or bearish votes.

---

## 15. Prioritized concrete code and test fixes

These are **proposed findings**, not persisted Codex candidates, completed patches or `CODEX_READY` declarations. Tests below are proposed acceptance cases; no supplied test suite was executed.

### P1 — source admission and protection correctness

| ID | Concrete fix | Required positive/adversarial test | Owner / dependency |
|---|---|---|---|
| **F01** | Use one strict Auto State loader in S3 and S4: containment, contract/schema, canonical digest, pointer identity and timestamps. | Alter body while preserving embedded digest; reject. Reject outside-root path and wrong contract. Accept exact valid fixture. | #1827; first dependency |
| **F02** | Strengthen CN admission: contained path, package schema/identity, original horizon clocks and bound addendum provenance. | Correct hash but wrong week/expired lane must not become current. Invalid addendum cannot replace projection. | #1827 + #1516; F01 pattern |
| **F03** | Centralize decision eligibility before horizons/protection. Use explicit admissible validation states and required-feature rules. | Unknown validation, PASS-with-missing-required-value and optional-only degradation produce distinct expected states. Native/event/Official agree. | #1827 + #1516 |
| **F04** | Preserve exact per-feature provenance; prevent breadth component splicing and funding PIT over-admission. | Current ratio missing but rich ratio present must retain rich timestamp/owner; capture-only funding stays non-PIT. | #1827; F03 |
| **F05** | Repair re-entry transitions and constructive-confirmation persistence. | HIGH→ELEVATED→ELEVATED retains reclaim watch; REVIEW with lost permission/direction closes or downgrades per contract. | #1553; independent risk review |
| **F06** | Deduplicate event refresh on a verified decision-context fingerprint, including CN/addendum/policy—not Auto hash alone. | Same Auto packet plus ELEVATED→HIGH CN change requests reassessment; identical complete context does not. | #1827 + #1553; F01/F02 |
| **F07** | Gate event protection on admitted CN and apply the same mapping-integrity decision as Official. | Rejected CN supplied to evaluator cannot generate protection; event OK and Official DEGRADED disagreement is eliminated. | #1827 + #1553; F03 |
| **F08** | Add protective-episode identity to in-flight deduplication. | Same pending protective transition emits once; a genuinely worse transition can bypass; NORMAL rearms only with valid evidence. | #1553 + #1827; F06 |

### P1 — issuance and delivery truth

| ID | Concrete fix | Required positive/adversarial test | Owner / dependency |
|---|---|---|---|
| **F09** | Separate admission, dispatch acceptance, issue completion and deployment states using the existing orchestration. | Failed dispatch cannot create ACCEPTED; accepted request without output remains pending; no fake issuance timestamp. | #1827 / #1516; operations #1156 |
| **F10** | Make Official output-root explicit and consistent with all consumers. | CLI Official mode without override writes to the official route or fails clearly; non-CWD repo root behaves correctly. | #1827 + #1516 |
| **F11** | Make immutable creation and pointer publication concurrency-safe; enforce monotonic latest selection. | Concurrent same-ID writes cannot corrupt; morning retry cannot replace a newer evening/event latest pointer. | #1827; high-impact writer review |
| **F12** | Reuse the strict prior-Compass loader for on-demand reuse and scheduled selection. | Tampered latest pointer, outside-root path, wrong digest and identity mismatch fail closed. | #1827; F01/F11 |
| **F13** | Represent missing issuance separately from a missing scheduled-slot inference; preserve actual issue time. | Missing prior artifact, delayed cron, midnight rollover and Copenhagen DST cases do not backdate or invent a slot receipt. | #1516 + #1827 |
| **F14** | Authenticate hourly and Entry event inputs and distinguish unknown heat from NORMAL. | Unverified completeness metadata cannot prove fresh source; missing Entry values do not silently rearm an episode. | #1827; F01 |
| **F15** | Close/expire public request status only from verified terminal evidence; distinguish health/maintenance/market causes. | Completed issue clears matching request; failed/pending remains truthful; health-only change does not say “market move.” | #1516 + #1827; F09 |

### P1/P2 — site custody and semantics

| ID | Concrete fix | Required positive/adversarial test | Owner / dependency |
|---|---|---|---|
| **F16** | Verify weekly package bytes before any public snapshot consumption; parse the exact verified bytes once. | Matching issue number with wrong content hash cannot enter `latest.json`; escaped week path rejected. | #1516 + #1827; F02 |
| **F17** | Bind standalone freeze, scorecard, range score and lineage artifacts through the existing immutable manifest/owner contracts. | Wrong-version freeze and unbound scorecard cannot be mixed into a current issue. | #1516 + #1827 |
| **F18** | Enforce original source/horizon expiry consistently in builder and client; never refresh clocks from unrelated packets. | Fresh Auto packet cannot renew old Official; expired Shadow/strategic lane is unavailable despite recent build time. | #1516 + #1827; F02/F03 |
| **F19** | Use strict public field/type/string allowlists across all projection paths, not just research narratives. | Wallet/private-provider text in drivers, class, scorecard or unexpected nested fields is rejected; no token-pattern-only reliance. | #1827 + #1516; privacy-sensitive |
| **F20** | Preserve nowcast semantics through schema, UI and scorer; remove current-policy nowcasts from forward-forecast denominators. | V4 nowcast never becomes a 12h prediction; legacy original issue remains separately classified; stripped marker fails closed. | #1596 + #1516 |
| **F21** | Preserve MIXED versus SIDEWAYS versus NO_EDGE versus UNAVAILABLE; align bull/bear naming across surfaces. | MIXED cannot display as measured neutral; 3/7 naming is contract-consistent; no probability language. | #1516 + #1596 |
| **F22** | Validate observation identity and comparison interval before assigning direction/new-observation status. | Same-hour nonzero changes, missing times, missing deltas and genuine flat distinct bars all yield distinct valid states. | #1827 + #1516 |
| **F23** | Keep direction independent of action permission; replace ambiguous ETA with horizon/reassessment fields. | SIDEWAYS stays SIDEWAYS under PREPARE; 24–72h cannot render as predicted trough time. | #1516 + #1553 |
| **F24** | Bind displayed model identity and retain the actual Native state vocabulary. | Unknown model metadata is not labeled Sol; degraded HOLD remains distinguishable from generic unavailable. | #1516 + #1827 |

### P2 — scientific accountability and operational closure

| ID | Concrete fix | Required positive/adversarial test | Owner / dependency |
|---|---|---|---|
| **F25** | Add per-lane original origin, target interval and expiry to forward readback; prevent weekly horizon rolling. | Late-week Official reissue cannot create a new 72h forecast from an expired early-week lane. | #1516 + #1596; F02 |
| **F26** | Preserve issuance/amendment/abstention/maturity denominators in the existing ledger. | NO_EDGE not scored as zero; pre-issue Monday excluded; amended close path not joined to earlier low/high issuance. | #1596 + #1827 |
| **F27** | Extend existing paired evaluator with point/range/nominal-WIS separation and event-block reporting. | WIS rejects uncalibrated min/max bands; repeated hourly rows do not inflate independent N; equal-width baseline retained. | #1596; F26 |
| **F28** | Bind natural producer→build→Pages→served-byte receipts to issue IDs. | Green CI without deployed/readback evidence remains POST_FIX_OBSERVATION; wrong deployed issue is detected. | #1516 + #1827; F09/F16 |
| **F29** | Distinguish unavailable, corrupt, expired and unpublished source failures in public-safe diagnostics. | Hash mismatch is not mislabeled “not published yet”; detailed internal errors do not leak publicly. | #1827 + #1516 |
| **F30** | Prove all critical regression tests execute in existing native CI; add guard-removal/mutation checks and growth assertions. | Removing digest, expiry, no-promotion or dedupe guards causes executed tests to fail; collect-only is not PASS. | #1827; operations #1156 |

**Priority note:** these are code-risk priorities, not a claim that a production privacy incident or trading loss has been observed. Any demonstrated privacy leak, evidence corruption or destructive-authority violation is a release stop.

---

## 16. Falsifiable research agenda

These should modify or complete existing registrations, not create a parallel tournament.

| Research question | Falsifiable hypothesis | Control / rejection condition | Owner |
|---|---|---|---|
| **R1: Delivery-adjusted warning value** | A registered shadow warning improves first delivered-warning lead time at equal false-alarm budget. | Reject if advantage disappears after source/delivery clocks or episode clustering. | #1553 + #1596 |
| **R2: Path versus simple price** | Frozen CN/challenger point paths reduce paired MAE versus no-change on common eligible blocks. | Reject if improvement is absent, unstable or concentrated in exposed W46-like tuning. | #1596 + #1516 |
| **R3: Range information** | Candidate intervals improve width-penalized loss, not merely coverage. | Equal-width/no-change and volatility controls perform comparably or better. | #1596 |
| **R4: Turn/depth skill** | A predeclared path predicts event depth or timing beyond endpoint direction. | Reject if only end-price accuracy improves, or matching requires hindsight tolerance changes. | #1596 + #1553 |
| **R5: Incremental signal families** | ETF/derivatives/breadth add out-of-block information beyond price/volatility. | Reject if gains vanish under PIT clocks, family ablation or shared-source correlation controls. | #1596; integrity #1827 |
| **R6: Rotation transmission** | Cohort-specific relative strength predicts later cohort participation beyond BTC/ETH controls. | Reject under frozen membership, liquidity exclusions, delayed-source controls or independent blocks. | #1596 + #1516 |
| **R7: Symmetric macro** | Vintage-valid macro/policy-repricing features improve an actually issued long-horizon baseline. | SOURCE_BLOCKED if expected-rate owner or original incumbent is absent; reject if effect is one-regime narrative. | #1596 / existing MAR owner |
| **R8: Abstention usefulness** | A predeclared abstention rule improves conditional accuracy without unacceptable coverage loss. | Reject if apparent improvement is only selective omission or post-event eligibility changes. | #1596 + #1827 |

### Mandatory negative tests

- Shift features forward in time: admission must reject leakage.
- Remove first-known metadata: PIT-sensitive use must abstain.
- Use revised macro data under an old event date: reject.
- Substitute current breadth membership historically: reject.
- Replace missing with zero: test must fail.
- Reissue the same observation with a new clock: no new scientific event.
- Relabel NO_EDGE as SIDEWAYS: reject.
- Strip nowcast semantics: no forward prediction.
- Feed private values into a public projection: reject.
- Use source stock as deployed liquidity: reject the feature interpretation.
- Shuffle/invert or otherwise falsify legally timed feature relationships within the preregistered diagnostic design: any claimed robust edge should weaken.
- Remove a critical production guard: the corresponding executed test must fail.

No negative-control result is reported here; these are required designs.

---

## 17. Dependency order, adoption gates and rollback

### Stage 0 — preserve evidence and qualify the work

- Freeze this audit against the supplied source packet.
- Obtain independent Claude review.
- Re-read current public main and required operational/boundary files.
- Deduplicate against existing original issues and ready tasks.
- Verify foundation status before new economic work.
- Keep Round 3 testing/scoring OFF.

**Stop:** source authority, required evidence or destructive-authority separation is unavailable for a consequential action.

### Stage 1 — custody and eligibility

Implement/review F01–F04, F14, F16–F19.

**Acceptance:** exact valid inputs work; tampered, stale, misbound and private-public violations fail closed.

**Rollback:** revert governed code through the original PR process; preserve all immutable artifacts and receipts. Do not “repair” history by editing original forecasts.

### Stage 2 — risk and refresh correctness

Implement/review F05–F08 and F15.

**Acceptance:** transition matrix, episode dedupe and CN-only change detection pass positive and adversarial tests.

**Rollback:** return affected new behavior to unavailable/shadow; restore the prior governed implementation without retroactively changing risk labels.

### Stage 3 — issuance and production delivery

Implement/review F09–F13 and F28–F30.

**Acceptance:** a genuine natural producer run reaches the intended consumer with exact issue/bundle binding. Scheduled-slot and delayed-recovery behavior are observed separately.

**Not sufficient:** green CI, a successful manual run, a generated file or an issue comment.

### Stage 4 — semantic/scoring repair

Implement/review F20–F27.

**Acceptance:** no nowcast scoring, no probability inflation, no horizon stretching, and complete abstention/issuance denominators.

### Stage 5 — existing shadow evaluation only

After source/science owner approval:

- use existing registrations;
- freeze candidates and baselines;
- collect actual prospective rows;
- wait for maturity;
- evaluate only at predeclared checkpoints;
- retain negative results.

**No automatic promotion.**

### Invalidation and stop rules

Stop the affected lane if any of the following is found:

- input knowledge time after issuance;
- missing or contradictory original issuance;
- frozen forecast rewrite;
- current pointer regression;
- public/private boundary failure;
- nowcast scored as forward forecast;
- expired source used as current;
- unissued/abstention rows converted into predictions;
- correlated rows counted as independent events;
- warning after the crash credited as prevention;
- paper utility claimed without required decision/delivery/fill assumptions;
- a shadow number entering Official action or the unscored live-display exception entering a scorer.

A scientific failure should retire or simplify the candidate. It should not trigger another threshold search on the same exposed cohort.

---

## 18. Independent Claude review package

**Review has not occurred in this response.**

Use the existing independent review owner/Bridge **#173**, with the exact source packet and this audit. A separately launched reviewer should assess:

1. **Source claims:** every asserted defect maps to supplied code; unread files are not implicitly treated as inspected.
2. **Integrity:** Auto/CN/public custody findings and realistic failure cases.
3. **State machine:** HIGH→ELEVATED persistence and REVIEW revocation.
4. **Event logic:** CN-only changes, in-flight protective dedupe and dispatch truth.
5. **Temporal semantics:** first-known, original issuance, horizon origin, expiry and delivery.
6. **W46 arithmetic/status:** distinguish reported values from independently reproduced calculations.
7. **W47:** no scoring, no inferred issuance or Pages availability.
8. **Long range:** no invented incumbent, no 7d-to-30d conversion.
9. **Statistics:** paired trials, proper intervals, event independence and false-alarm burden.
10. **Authority:** no model promotion, trading instruction, new scheduler or private-data expansion.

The review should return:

- exact reviewed source/report identity;
- supported/refuted/insufficient-evidence findings;
- concrete P0/P1 objections and failing cases;
- remaining unread dependencies;
- explicit scientific adoption status.

A favorable advisory review does not itself authorize release or establish forecast edge.

---

## Final assessment

**Kompas Pro is presently best understood, from these sources, as a governed synthesis and presentation system with partially implemented forecasting and research accountability—not a demonstrated predictive trading system.**

Its strongest foundations are source ownership, immutable intent, separation of warning from action, and explicit abstention. Its weakest points are inconsistent admission, incomplete temporal lineage, request-versus-delivery observability, and presentation that can imply more precision than the underlying evidence supports.

W46 supplies a useful failure investigation, not a new discovery of edge. W47 remains unscored here. G1 makes the long-range limitation explicit: eligible original forecasts and common PIT rows must exist before comparison.

**Recommended disposition:** retain Official authority, preserve unavailable states, repair the source-to-consumer chain, and test only bounded existing shadow hypotheses against cheap paired baselines. Independent Claude review precedes use; promotion remains unapproved.
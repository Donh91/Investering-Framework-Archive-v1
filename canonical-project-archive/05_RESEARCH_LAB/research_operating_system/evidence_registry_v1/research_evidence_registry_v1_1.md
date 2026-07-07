# Research Evidence Registry v1.1

Date: 2026-07-07  
Status: EXECUTED / CANONICAL WORKING REGISTRY  
Supersedes: `research_evidence_registry_v1.md` as active evidence board  
Scope: All currently ratified and non-ratified research evidence from Fable P1/P1b, DATA PING governance and framework archive context.

---

## 0. Executive summary

The framework now has enough research artifacts to separate rules into four groups:

1. **Supported and ratified**
   - v0.2 hybrid gate integrity
   - 59.0K hard-death, with tight-buffer annotation
   - FNP ledger prior around 9% [7-12], p90 around 12%

2. **Useful but not alpha / not price-edge**
   - 2/3-close persistence remains governance discipline only
   - flow-conditioning did not rescue close-persistence as a price edge

3. **Governance rules that prevent misuse**
   - Rebuy remains LOCKED
   - v0.2 can classify and measure, but cannot buy
   - 64K remains DEAD_LEVEL / STALE_LEVEL only
   - perp wick remains diagnostic-only
   - LIVE / LEDGER / GOVERNANCE / SHADOW separation remains mandatory

4. **Open research items**
   - ETH/BTC persistence
   - Rotation Watch vs Rotation Confirmed
   - ETF stabilization formula
   - breadth thresholds
   - leverage thresholds
   - Cycle Navigator weekly range skill vs dumb baselines

This registry is not a portfolio instruction file. It is a governance and research state file.

---

## 1. Evidence grade definitions

| Grade | Meaning | Can support live rule? |
|---|---|---|
| FULL | All required data layers tested, no major missing context. | Potentially, after governance ratification. |
| OHLC-GRADE | True open/high/low/close and real ATR included. | Can support price/gate mechanics. |
| CLOSE-ONLY | Close-only price test. | Limited; cannot validate wick/sweep. |
| PRICE-ONLY | Price behavior only, missing flow/breadth/leverage. | Measurement only unless rule is explicitly price-only. |
| PARTIAL-FLOW | ETF/flow data included, but not full breadth/leverage/rotation matrix. | Can support flow-conditioned language, not full rotation. |
| PROTOCOL-ONLY | Test method exists, not executed. | No. |
| UNTESTED | No empirical test yet. | No. |
| SHADOW-ONLY | May be tracked, cannot drive live decisions. | No. |

---

## 2. Active evidence board

| ID | Component | Evidence | Result | Confidence | Current status | Allowed use | Forbidden use | Next test |
|---|---|---|---|---|---|---|---|---|
| ER-001 | v0.2 hybrid gate | P1 close-only + P1b OHLC/wick | SUPPORTED. Hybrid beats binary under both close and wick triggers. | MED-HIGH | Ratified state-gate design | Classify/measure BTC-tier gate state | Buy, unlock rebuy, confirm recovery alone | Longer OHLC sample if possible |
| ER-002 | 59.0K hard-death | P1 close-only + P1b OHLC nuance | KEEP RATIFIED. Defensible but tight. | MED-HIGH | Active hard-death rule with caveat | One clear close below 59.4K shelf / 2 closes below shelf logic | Treat as wide ATR buffer | Recheck if ATR regime changes |
| ER-003 | 59.4K soft breach | Governance + E5 design | ACTIVE. Soft breach/probation level. | MED-HIGH | Active v0.2 state hygiene | Trigger probation / reset counters | Automatic full death on first breach | Keep with v0.2 rules |
| ER-004 | 2 consecutive closes <59.4K | E5/P1b interpretation | ACTIVE. Does much of hard-death work. | MED | Active hard-death leg | Confirm persistent shelf loss | Use without context as portfolio signal | Replay current window |
| ER-005 | 2/3-close persistence | P1 close-only + P1b OHLC/Farside | NOT SUPPORTED as price edge. Flow-conditioning did not rescue. | MED | Discipline only | Noise filter / governance delay | Claim alpha, recovery confirmation, historical validation | Larger sample, breadth-conditioned if data exists |
| ER-006 | N<=3 cap on persistence | P1 evidence | SUPPORTED as simplification. N4/N5 adds cost without benefit. | MED | Active language/design guardrail | Avoid over-waiting | Use 4/5-close as standard gate | None unless full retest contradicts |
| ER-007 | FNP ~9% [7-12] prior | P1 + P1b E8 | SUPPORTED as measurement. p90 around 12%. | MED | Ledger prior | Opportunity-cost accounting | Rebuy pressure or signal | Live replay and larger flow sample |
| ER-008 | FNP Meter A vs Meter B | Addendum + P1/P1b | SUPPORTED architecture. Meter B is verdict basis. | MED | Active measurement logic | Context + verdict split | Use wick/low as entry verdict | Replay historical rows |
| ER-009 | Rebuy LOCKED | Governance rule | ACTIVE. No P1/P1b result unlocks rebuy. | HIGH | Live state | Capital discipline | Override via FNP or v0.2 alone | Separate rebuy-readiness package |
| ER-010 | v0.2 cannot buy | Governance rule | ACTIVE. v0.2 is state-gate only. | HIGH | Hard constraint | Classification/measurement | Portfolio action | None |
| ER-011 | 64K stale/dead level | Fable #3/#5 governance | ACTIVE restriction. | HIGH | Governance archive only | Historical reference/collision warning | Active ladder/trigger | Only if explicitly revalidated |
| ER-012 | Cycle-low freeze dual anchor | Fable #3 governance | ACTIVE. Separate spot intraday, close basis, perp wick. | HIGH | Gate hygiene | Low/timer/source integrity | Merge wick/close/spot lows | Apply in replay |
| ER-013 | Perp wick diagnostic-only | Fable #3 governance | ACTIVE. | HIGH | Shadow diagnostics | Stress/liquidity color | Canonical cycle low, reset timer, gate death | Spot/perp study if needed |
| ER-014 | Lower-half-first path row | Fable governance | ACTIVE under R3/path only. | MED | Shadow/ledger path weighting | Path bias and diagnostic | Official v0.2 row, rebuy input | Weekly replay |
| ER-015 | PATH-WEIGHT R3 authority | Fable #5 | ACTIVE. Can cancel lower-half-first under path authority. | MED | Ledger/path row | Path interpretation | v0.2 Attempt row | Replay current windows |
| ER-016 | FNP R2 diagnostic authority | Fable #5 | ACTIVE as measurement only. | MED | Ledger diagnostic | Measure false-negative risk | Signal/portfolio action | Replay |
| ER-017 | ETF flow status line | Fable #5 + P1b | ACTIVE output requirement. | HIGH | LIVE/LEDGER output | Separate print/trend/streak/latest known | Hide as MISSING/neutral | Output audits |
| ER-018 | ETF stabilization formula | Farside available; not formula-tested | OPEN. | LOW-MED | Shadow research | Flow regime study | Freeze threshold/formula | Dedicated ETF regime study |
| ER-019 | ETH/BTC 0.0275 | Governance context | UNTESTED. Reclaim pressure only. | LOW | Shadow/live language | Early rotation pressure wording | Rotation Confirmed | E2 ETH/BTC persistence |
| ER-020 | ETH/BTC 0.0300 | Governance context | UNTESTED. Possible stronger threshold. | LOW | Shadow | Watch level | Altseason confirmation | E2 |
| ER-021 | Rotation Confirmed | Not full-tested | OPEN. | LOW | Conservative language | Only with ETHBTC+breadth+deployment matrix | Any P1/P1b inference | Rotation replay |
| ER-022 | Breadth thresholds | Missing historical breadth | UNTESTED. | LOW | Shadow | Optional context | Freeze or confirm rotation | Source and test |
| ER-023 | Funding/OI thresholds | Missing historical leverage source | DATA-CONSTRAINED. | LOW | Shadow | Context if available | Freeze leverage rules | Source discovery |
| ER-024 | Stablecoin/TVL liquidity | DeFiLlama source-mapped | SOURCE-MAPPED only. | LOW | Shadow/E12 | Liquidity feature candidate | Trigger/gate | E12 later |
| ER-025 | Cycle Navigator range skill | Weekly actuals exist partially | OPEN. | LOW-MED | Research | Forecast skill audit | Claim quantified edge | Range replay vs baselines |
| ER-026 | Cycle Navigator score | Public/formatting history exists | OPEN. | LOW-MED | Research/output | Score reliability audit | Treat score as proven accuracy | Score vs actual outcomes |
| ER-027 | Master Monday raw archive | Archive exists/needs manifest | NEEDS-EXTRACTION. | MED | Research archive | Weekly replay input | Use unstructured text as clean data | Custom GPT manifest |
| ER-028 | Highest DATA PING version wins | Governance rule | ACTIVE. | HIGH | Source governance | Select live truth feed | Hardcode old DATA PING version | Enforce in replay |
| ER-029 | LIVE/LEDGER/GOV/SHADOW separation | Fable #5 | ACTIVE. | HIGH | Output governance | Prevent risk compression | Hide state/blocker/rebuy | Output audit |
| ER-030 | Custom GPT sensor role | Architecture | ACTIVE. | HIGH | Data ingestion | Collect/source/structure | Ratify framework | Use data request prompt |
| ER-031 | Claude/Fable research role | Architecture | ACTIVE. | HIGH | Research execution | Run narrow tests | Governance final say | Continue with strict prompts |
| ER-032 | ChatGPT governance role | Architecture | ACTIVE. | HIGH | Final ratification/archive | Evidence registry and rule status | Fabricate missing data | Maintain registry |

---

## 3. Ratification board

### Confirmed active / ratified

| Component | Ratified state | Caveat |
|---|---|---|
| v0.2 hybrid gate | Active BTC-tier state-gate | Cannot buy or unlock rebuy. |
| 59.0K hard-death | Active | Tight hard-death, not wide ATR buffer. |
| 59.4K soft breach | Active | Probation/counter reset logic. |
| FNP ~9% [7-12] | Active ledger prior | Not signal. |
| FNP Meter A/B | Active | Meter B verdict basis. |
| Rebuy LOCKED | Active | Must be changed only by separate rebuy-readiness package. |
| LIVE/LEDGER/GOV/SHADOW output separation | Active | State and main blocker must never be compressed away. |
| Highest DATA PING version wins | Active | Enforce automatically. |

### Active but language-restricted

| Component | Required wording | Banned wording |
|---|---|---|
| 2/3-close | ratified discipline, price-edge unproven, flow-conditioning did not rescue edge | historically proven edge, flow-validated edge |
| ETH/BTC 0.0275 | reclaim attempt / early rotation pressure | Rotation Confirmed |
| FNP | opportunity-cost ledger prior | rebuy pressure, signal |
| 59.0K | tight hard-death / one clear close below shelf | broad ATR buffer |

### Open / not frozen

| Component | Reason |
|---|---|
| ETH/BTC persistence | No E2 execution yet. |
| Rotation Confirmed | Missing breadth/deployment matrix. |
| ETF stabilization formula | Farside available, formula not validated. |
| Breadth thresholds | Historical breadth missing. |
| Leverage thresholds | Funding/OI history missing. |
| Stablecoin/TVL trigger | Source-mapped, untested. |
| Cycle Navigator range skill | Needs baseline comparison. |

---

## 4. Implementation layers

### LIVE layer

Allowed:

- STATE line
- REBUY line
- GATE line
- FLOW line
- next up / next down triggers
- data quality

Active restrictions:

- no 2/3-close alpha claims
- no rotation confirmation from ETH/BTC reclaim alone
- no FNP pressure as buy signal
- no 64K active trigger

### LEDGER layer

Allowed:

- FNP Meter A/B
- v0.2 gate rows
- ETF print/trend/streak
- source-conflict rows
- path-weight rows
- rule_helped/rule_hurt replay labels

### GOVERNANCE layer

Allowed:

- ratification status
- hard-death definitions
- dead levels
- source hierarchy
- no-hindsight rules
- evidence registry updates

### SHADOW layer

Allowed:

- unvalidated leverage/breadth/stablecoin/options signals
- Rotation Watch candidates
- path diagnostics
- perp wick stress

---

## 5. Highest-priority next research from Evidence Registry

1. **Cycle Navigator Range Skill Audit**
   - Why: public product credibility and existing forecast/actual history.
   - Needed: weekly forecasts, actual ranges, baseline comparisons.

2. **E2 ETH/BTC Persistence Test**
   - Why: rotation language depends on it.
   - Needed: ETHBTC daily series.

3. **ETF Stabilization Formula Study**
   - Why: ETF flow is central current blocker.
   - Needed: Farside BTC/ETH flow aligned to BTC OHLC.

4. **No-Hindsight Daily Replay**
   - Why: tests whether rules helped actual state decisions.
   - Needed: DATA PING rows and daily market data.

5. **Funding/OI Source Discovery**
   - Why: leverage remains data-constrained.
   - Needed: historical funding/OI source.

---

## 6. Registry update protocol

Update this file when:

- a new Fable/Claude experiment executes
- Custom GPT provides a structured DATA PING supplement
- Master Monday / Cycle Navigator tables are extracted
- a rule is ratified, downgraded or retired
- a new source becomes canonical

Every update must include:

- source artifact
- data span
- evidence grade
- result
- confidence
- governance consequence
- next falsifier

---

## 7. Final status

This v1.1 registry is now the active research evidence board.

It does not replace raw research artifacts.

It makes the artifacts usable by future threads by turning them into rule-level evidence rows.

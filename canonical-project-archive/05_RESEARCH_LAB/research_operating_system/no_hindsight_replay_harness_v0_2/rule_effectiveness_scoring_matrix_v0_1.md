# Rule Effectiveness Scoring Matrix v0.1

Date: 2026-07-07  
Status: EXECUTION-READY SCORING GUIDE  
Purpose: Standardize rule_helped / rule_hurt / neutral labels during no-hindsight replay.

---

## 1. Allowed labels

| Label | Meaning |
|---|---|
| HELPED | Rule improved decision quality or reduced false signal/churn. |
| HURT | Rule worsened decision quality, delayed useful action or created false confidence. |
| NEUTRAL | Rule was active but did not materially affect the row. |
| DATA_MISSING | Required data missing; cannot score. |
| NOT_APPLICABLE | Rule not relevant to this row. |
| HINDSIGHT_RISK | Scoring would require future information in state section. |

---

## 2. v0.2 hybrid gate scoring

### HELPED if:

- soft breach prevented premature full gate death
- probation avoided binary churn
- hard death prevented zombie-gate after clear breakdown
- 2 consecutive closes below 59.4K correctly captured persistent shelf loss
- 59.0K tight hard-death captured one clear close below shelf without excessive delay

### HURT if:

- probation delayed obvious breakdown
- 59.0K triggered too tight relative to actual recovery
- gate churn increased vs binary baseline
- state remained ambiguous after clear directional evidence

### NEUTRAL if:

- price stayed far from gate zone
- no state transition depended on v0.2

---

## 3. 2/3-close discipline scoring

Canonical rule status:

`discipline only, price-edge unproven, flow-conditioning did not rescue edge`

### HELPED if:

- N=2/N=3 wait avoided a fake reclaim that reversed quickly
- waiting reduced false Recovery Attempt pressure
- waiting kept rebuy locked during a clear failed reclaim

### HURT if:

- waiting filtered a valid recovery entry and increased FNP cost
- N=3 added delay without reducing whipsaw
- persistence was used as false proof of recovery

### NEUTRAL if:

- no reclaim event occurred
- state did not depend on close count

### Forbidden scoring:

Do not score 2/3-close as “historically validated edge”.

---

## 4. FNP ledger scoring

Canonical rule status:

`ledger-only, not signal, ~9% [7-12], p90 ~12% prior`

### HELPED if:

- FNP made opportunity cost visible without causing action
- Meter A/B split clarified context vs permitted entry
- FNP prevented hidden false-negative drift

### HURT if:

- FNP was treated as rebuy pressure
- FNP framed waiting cost as portfolio instruction
- FNP ignored data-quality limits

### NEUTRAL if:

- no recovery opportunity existed
- no first-permitted-entry condition occurred

---

## 5. ETF flow scoring

### HELPED if:

- ETF trend separated one positive/negative print from actual regime
- ETF negative context correctly blocked overconfident recovery language
- ETF improvement helped contextualize de-escalation without confirming recovery

### HURT if:

- missing ETF data was treated as neutral
- one ETF print was over-weighted
- BTC and ETH ETF flows were collapsed into one status despite divergence

### NEUTRAL if:

- no ETF data existed for the period and was properly marked missing

---

## 6. ETH/BTC / rotation scoring

### HELPED if:

- ETH/BTC reclaim pressure was kept separate from Rotation Confirmed
- rotation language stayed conservative until matrix confirmed
- ETH/BTC failure prevented premature alt deployment language

### HURT if:

- ETH/BTC >0.0275 was treated as Rotation Confirmed
- altseason language appeared while ETH/BTC <0.0300 and breadth/deployment were missing
- derived ETHBTC was treated as direct-pair evidence without label

---

## 7. Cycle Navigator range scoring

### HELPED if:

- forecast range contained actual weekly high/low
- breach direction was correctly anticipated
- range width was efficient vs dumb baseline
- regime label improved interpretation vs price-only baseline

### HURT if:

- range was too narrow and missed actuals materially
- range was too wide and uninformative
- score stayed high despite poor forecast quality
- narrative contradicted actual data path

### NEUTRAL if:

- missing actuals prevent scoring
- forecast was explicitly qualitative only

---

## 8. Output compression scoring

### HELPED if:

- compressed output preserved state, rebuy, gate, main blocker, flow and next triggers
- shadow details were moved out without hiding risk

### HURT if:

- state line disappeared
- main blocker disappeared
- rebuy lock disappeared
- flow line disappeared
- v0.2 pending/diag status disappeared

---

## 9. Hindsight violation scoring

Mark HINDSIGHT_RISK if:

- a future high/low is used in state-at-time
- future ETF flow influences current flow status
- future Fable ratification changes old live state
- a final weekly actual is used to rewrite forecast interpretation
- missing data is filled from later knowledge

If HINDSIGHT_RISK appears, the row cannot be used for rule effectiveness until corrected.

---

## 10. Final scoring format

Each replay row should include:

```text
rule_helped: [rule IDs]
rule_hurt: [rule IDs]
rule_neutral: [rule IDs]
hindsight_check: PASS / FAIL / RISK
notes: short explanation
```

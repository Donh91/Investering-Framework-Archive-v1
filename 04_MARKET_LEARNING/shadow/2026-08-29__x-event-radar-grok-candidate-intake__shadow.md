# X Event Radar — Grok candidate intake

**Date:** 2026-08-29  
**Status:** SHADOW_OBSERVATION_ONLY  
**Authority:** NONE for market state, DATA PING gates, rotation, portfolio action or Master Monday unless independently verified and escalated under current governance.  
**Source:** User-supplied Grok X Source Candidates, runs 2026-08-22 through 2026-08-29.  

## Purpose

Preserve low-cost event intelligence without expanding the standard DATA PING. Candidates are deduplicated into incident/event lifecycles and assigned a materiality route. X discovery is not treated as verified outcome evidence. Official-account labels and claims below are inherited from the supplied candidate packet and have not been independently re-verified by this intake.

Routing model:

`X discovery -> candidate -> deduplicate -> verify -> classify materiality -> Shadow/archive -> escalate only if decision-relevant`

## Materiality gates

Escalation requires plausible impact on at least one current framework dimension: liquidity, regulation/enforcement, systemic security, stablecoin rails, BTC/ETH infrastructure, or a concrete portfolio exposure. Routine isolated protocol incidents remain compressed event history unless contagion, market transmission, or portfolio relevance emerges.

## Deduplicated event clusters

| Event cluster | First supplied observation | Latest supplied observation | Category | Supplied claim summary | Materiality | Route |
|---|---|---|---|---|---|---|
| Fogo treasury-wallet compromise | 2026-08-29 01:13:51Z | same | Security / protocol | @fogo reportedly disclosed compromise of foundation wallets and transfer of 400M FOGO; exchanges/law enforcement alerted; chain said unaffected | MEDIUM | WATCH; escalate only on liquidity/contagion/portfolio relevance |
| Avici card-balance withdrawals | 2026-08-28 18:42:24Z | 2026-08-29 16:59:31Z | Security / exchange | Initial withdrawal issue reportedly progressed to full reimbursement plus 10% cashback; self-custodial wallets said unaffected | LOW | ARCHIVE as one lifecycle: ACTIVE_INCIDENT -> RESOLVED/REIMBURSED |
| Circle stablecoin rails on Plasma | 2026-08-28 17:00:00Z | same | Protocol / stablecoin infrastructure | @circle reportedly announced USDC, EURC, CCTP and Bridge Kit live on Plasma | MEDIUM | STRUCTURAL_WATCH; candidate for stablecoin-rail/adoption context after verification |
| Core Lightning CVE response | 2026-08-26 23:26:09Z | same | Security / BTC infrastructure | @Core_LN reportedly described live CVE triage, coordinated fixes, operator restart guidance and prompt signed-binary upgrade path | MEDIUM | WATCH; escalate if Bitcoin/Lightning operations or systemic security are affected |
| Moonwell exploit | 2026-08-27 10:58:47Z | same | Security / DeFi | @PeckShieldAlert reportedly estimated an $8.7M exploit on Base and identified a destination address | LOW_MEDIUM | ARCHIVE; escalate on contagion or relevant exposure |
| U.S. Treasury Iran digital-assets sanctions | 2026-08-24 19:35:35Z | same | Regulation / enforcement | @USTreasury reportedly announced sectoral sanctions determinations covering Iran's digital-assets sector | MEDIUM_HIGH | ESCALATE_FOR_VERIFICATION; regulatory/enforcement precedent |
| The Sandbox SAND bridge exploit | 2026-08-22 07:22:23Z | 2026-08-24 19:58:51Z | Security / protocol | Initial bridge vulnerability/containment reportedly followed by forensic quantification of 14,742,341.84 SAND drained and continued bridge disablement | LOW | ARCHIVE as one lifecycle: DISCOVERED/CONTAINED -> FORENSICS/IMPACT_FINALIZED |
| Term Labs Meta Vault governance exploit | 2026-08-23 23:22:30Z | same | Security / protocol | @term_labs reportedly confirmed a governance exploit, permanent Meta Vault shutdown, withdrawals remaining open and underlying direct markets unaffected so far | LOW | ARCHIVE; escalate only on contagion/portfolio relevance |
| MANTRA Cosmos-EVM vulnerability/restart | 2026-08-22 06:28:56Z | same | Security / protocol | @MANTRA_Chain reportedly said block production resumed after vulnerability remediation and no user funds were affected | LOW | ARCHIVE |

## Current escalation shortlist

1. **U.S. Treasury / Iran digital-assets sanctions** — verify against the primary government publication before any framework use.
2. **Circle / Plasma stablecoin infrastructure** — verify and retain as structural stablecoin-rail/adoption context, not a cycle signal by itself.
3. **Fogo compromise** — watch for measurable liquidity, exchange or contagion effects.
4. **Core Lightning CVE response** — watch for BTC/Lightning operational impact or broader security significance.

## Compression and learning rule

Do not create separate framework signals for incident updates belonging to the same event cluster. Preserve lifecycle transitions instead. After sufficient history exists, evaluate whether event classes add measurable incremental information to later market decisions. If a class repeatedly has no measurable transmission, compress or retire it from active review rather than increasing DATA PING scope.

## Explicit non-effects

- DATA PING collector scope changed: **NO**
- Current market state changed: **NO**
- Rotation confirmation changed: **NO**
- Portfolio permission/action changed: **NO**
- New engine created: **NO**
- Prospective outcome evidence created: **NO**

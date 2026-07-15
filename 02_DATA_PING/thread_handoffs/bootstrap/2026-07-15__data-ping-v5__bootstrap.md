# DATA PING V5 — New Thread Bootstrap

**Bootstrap ID:** `DATA_PING_V5_BOOTSTRAP_20260715`  
**Handover:** `DATA_PING_THREAD_HANDOVER_V4_TO_V5_20260715T210212Z`  
**Status:** READY_TO_PASTE  
**Activation rule:** V5 is not active until the first complete V5 DATA PING is received and accepted.

## Paste this as the first message in the new thread

```text
DATA PING V5 — NY KANONISK TRÅD

Dette er en fortsættelse af DATA PING V4, ikke en genstart.

Indlæs først følgende fra GitHub:

1. 02_DATA_PING/thread_handoffs/latest_thread_handover_state.json
2. Den fulde handover-fil, som pointeren linker til
3. 02_DATA_PING/operational_handoffs/latest_accepted_log_state.json
4. Den aktive event-registry, som accepted-log pointeren linker til

Kontrollér især:
- seneste accepterede DATA PING og supplement
- aktiv source stack og alle authority boundaries
- aktiv event, gates og portfolio state
- brugerens output- og handlingspræferencer
- OTA/SCTA-holdout og eksperimentstatus
- alle pending/missing felter

Bekræft derefter udelukkende med:

DATA_PING_THREAD_BOOTSTRAP
handover_status: PASS / PARTIAL / FAIL
loaded_handover_id: <id>
latest_accepted_log_id: <id>
active_source_version: <version med seneste komplette ping>
intended_successor_version: V5
active_event_id: <id>
framework_state: <state>
portfolio_action: NONE
ready_for_first_complete_new_version_ping: YES / NO

Vigtigt:
- V5 bliver først aktiv, når jeg indsætter den første komplette DATA PING V5-pakke.
- Indtil da forbliver seneste accepterede V4-ping kanonisk.
- Trådskiftet må ikke ændre market state, gates, regler, event status, entry eller porteføljehandling.
- DATA_MISSING = UNKNOWN.
- GeckoTerminal closes er shadow observation only.
- OKX er venue-specific derivatives only.
- Incomplete Farside zero rows er PENDING, ikke nul.
- Main framework ejer fortolkning og handling.
- Min aktuelle handling er HOLD OG AFVENT.

Vent efter bootstrap-bekræftelsen på den første komplette V5 DATA PING.
```

## Expected loaded state before first V5 ping

```yaml
latest_accepted_log_id: DATA_PING_V4_20260715T202300Z
latest_supplement_id: FARSIDE_ETF_RECOVERY_20260715T204855Z
active_event_id: ROTATION_REPAIR_EDGE_20260712_01
framework_edge_state: NEAR_PRESENT
alert_status: STILL_ACTIVE
event_status: OPEN_TRIGGERED
rotation_status: NO_ROTATION
rebuy_status: LOCKED
large_cap_buy_window: NOT_OPEN
portfolio_action: NONE
active_source_version: V4
intended_successor_version: V5
```

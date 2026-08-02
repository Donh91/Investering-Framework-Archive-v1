# F1 post-window boundary-stress observation

```yaml
source_run: CLAUDE_OTA_2026_08_01T19_20_42Z
observation_type: POST_WINDOW_BOUNDARY_STRESS
session_status: IN_PROGRESS
window_closed: YES
score_changed: NO
canonical_effect: NONE
```

## Observation

BTCUSDT printed an in-progress intraday low of 62,275.00 on 2026-08-01.

| Candidate | Relation to 62,275 |
|---|---:|
| 62,342 | 0.11% below candidate |
| 62,200 | 0.12% above candidate |

The accepted observation is therefore a passage below the higher candidate only, not below both candidates.

## Experiment treatment

F1's historical window closed on 2026-07-28 and its rule evaluated settled closes. An in-progress intraday low five sessions after the window cannot rescore the experiment. The historical result remains `NOT_FAILED`.

## Design-hypothesis treatment

H-WIN-01 remains `UNPROVEN` with `LOW_MODERATE` confidence. No confidence increase is permitted from this print alone. Resolution remains dependent on the preregistered audit of at least ten closed windows.

# 19 | Original Official v3 public Pages publication census, all 11 attempts

**Checked 2026-10-23 Europe/Copenhagen.** Existing science owner [#1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596). [Machine receipt](19_ORIGINAL_V3_PUBLICATION_CENSUS_20261023.json). This extends the single-row [#18](18_ORIGINAL_V3_PUBLICATION_CHAIN_R1_20261023.md) without changing frozen original objects, outcomes or admission.

## Method and exact scope

Start with all 11 attempts from the frozen `2026-10-15__TASK2_R1_NATIVE_V3_ORIGINAL_ADMISSION_v2.json`, not only correctly predicted or matured rows. For each exact original forecast path, fetch its historical first path commit from GitHub, then fetch that file's Git blob at that commit and compare it with the frozen ledger. **11/11 exact Git blobs matched.** Read its Official freeze workflow ID from the commit message, inspect the freeze job log's actual `gh workflow run cycle-navigator-pages.yml` dispatch, fetch that Pages run's GitHub head and deploy job, then inspect its historical build log. Require the build's `Compass CMP-...` ID to equal that particular original forecast, the Pages run's exact head to equal its first forecast commit, and its deploy job to conclude SUCCESS with `Reported success!`. **11/11 passed this bounded public publication-chain check.**

The recorded Pages success is between **40.733 and 76.510 seconds after the respective declared issuance**. All nine rows with an original frozen target have a deployment report before that target. The two rows with no target at the frozen snapshot retain `UNKNOWN_AT_FROZEN_SNAPSHOT` here; their later outcomes must not repair that original state.

| Original forecast | Declared issue UTC | Exact Pages run | Deploy success reported UTC | Delay, seconds | Original frozen target UTC |
| --- | --- | --- | --- | ---: | --- |
| `CMP-20261012-468da783e9d8` | `2026-10-12T23:24:24Z` | [38321965455](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/38321965455) | `2026-10-12T23:25:10.0671699Z` | 46.067 | \`2026-10-13T11:00:00Z\` |
| `CMP-20261012-904299b09eca` | `2026-10-12T19:59:38Z` | [38301301357](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/38301301357) | `2026-10-12T20:00:29.2847939Z` | 51.284 | \`2026-10-13T07:00:00Z\` |
| `CMP-20261013-88618d3ad2a7` | `2026-10-13T07:46:16Z` | [38364807748](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/38364807748) | `2026-10-13T07:47:17.0234376Z` | 61.023 | \`2026-10-13T19:00:00Z\` |
| `CMP-20261013-aa70b21fc6b0` | `2026-10-13T12:20:35Z` | [38396597346](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/38396597346) | `2026-10-13T12:21:34.2056556Z` | 59.205 | \`2026-10-14T00:00:00Z\` |
| `CMP-20261013-aecf113aab74` | `2026-10-13T21:21:40Z` | [38470013946](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/38470013946) | `2026-10-13T21:22:23.8382981Z` | 43.838 | UNKNOWN_AT_FROZEN_SNAPSHOT |
| `CMP-20261013-af3bcdea9173` | `2026-10-13T23:03:36Z` | [38481861303](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/38481861303) | `2026-10-13T23:04:26.7580482Z` | 50.758 | UNKNOWN_AT_FROZEN_SNAPSHOT |
| `CMP-20261013-b1af85bff6f8` | `2026-10-13T16:10:20Z` | [38428304129](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/38428304129) | `2026-10-13T16:11:00.7336406Z` | 40.733 | \`2026-10-14T03:00:00Z\` |
| `CMP-20261013-bfb7ff123449` | `2026-10-13T14:14:43Z` | [38411702904](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/38411702904) | `2026-10-13T14:15:59.5105334Z` | 76.510 | \`2026-10-14T00:00:00Z\` |
| `CMP-20261013-cb70ee1b10f3` | `2026-10-13T02:13:56Z` | [38335906920](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/38335906920) | `2026-10-13T02:14:41.1930285Z` | 45.193 | \`2026-10-13T14:00:00Z\` |
| `CMP-20261013-d649788e5270` | `2026-10-13T00:49:07Z` | [38329113289](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/38329113289) | `2026-10-13T00:49:48.3913420Z` | 41.391 | \`2026-10-13T12:00:00Z\` |
| `CMP-20261013-f34752e8e3c4` | `2026-10-13T17:48:02Z` | [38441585843](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/38441585843) | `2026-10-13T17:49:01.6301937Z` | 59.630 | \`2026-10-14T05:00:00Z\` |

Every Pages run above is `workflow_dispatch`, `conclusion=success`, with `head_sha` equal to the specific forecast's first main commit; full SHA, Git blob and Official freeze run ID appear per row in the JSON. The historical deploy log printed each exact Compass ID. This is narrower and more reproducible than equating a generic successful site workflow with a particular forecast.

## Scientific adjudication

**11/11 public Pages deployments were reported, 0/11 first *user* deliveries were verified, 0/11 provider first-publication/revision clocks were independently verified, and R1 remains 0/11 admitted.** Here `0 verified` counts evidence receipts, not a claim that no user actually received a forecast. A Pages success is not an authenticated recipient fetch/view, notification receipt or first actionable time, and does not establish how long the particular version stayed visible before replacement. Original issue clocks, Git clocks, workflow clocks and provider clocks are distinct.

The capture custody limitations remain: original CFGI raw HTTP responses are absent from the preserved bundle and the original OKX retrieval timestamp was request-batch start, not response completion. Public Git/Pages chronology cannot manufacture these source clocks. The 11 attempts also share source/capture dependencies and overlapping target/event windows, so 11 deployments are not 11 independent market events. No model skill, economic benefit, Round 3 result or historical R2/R3 release is claimed.

**Next evidence:** find any original recipient-specific delivery receipt tied to the exact forecast ID/commit and immutable source clock, then independently substantiate first-known/revision for every decision feature. Retain the full no-forecast/no-warning denominator and only freeze R2 matched controls if R1 genuinely admits. No paid query, new scheduler or private source values were used for this census.

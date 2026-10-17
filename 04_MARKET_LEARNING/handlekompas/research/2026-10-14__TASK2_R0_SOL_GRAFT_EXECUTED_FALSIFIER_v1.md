# Task 2 R0 · Deterministically reproduced Git graft ancestry false acceptance

**Executed:** 2026-10-14, isolated ephemeral Linux Git fixture, Git **2.47.3**. **Class:** `REPRODUCED_GIT_PRIMITIVE_FALSE_ACCEPT`; not a production repository attack or original market PIT test. Current subject: [PR #1627](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1627) at immutable head `52d4a6a87ed3d41dbb4c4ccf53285b39c51a4bd5`. Source blob `7ae538e6b1f87108de3c6057c187909ffe2458a1`, test blob `b6dc5bbb99f600875eda99d3487de6f5fd0756ff`. The exact source and test code were read from that PR; **the exact PR script was not executed on this fixture**. Its source uses the same tested `git --no-replace-objects merge-base --is-ancestor` ancestry predicate, alongside direct commit and root-tree/object SHA checks.

## Why test this

The first owner-authorized independent GPT-6.1 Sol API review (issue [#1476](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1476), output comment `6173001365`) found replacement-ref and direct commit risks. Corrected PR #1627 now uses `--no-replace-objects`, direct commit typing and additional negative fixtures. A second genuine GPT-6.1 Sol API review (output comment `6175852501`, trigger `6175760286`; **0.163946 USD**) reported `VERDICT=WEAKENED`: likely unresolved legacy `.git/info/grafts` ancestry rewrite, but **model did not run** the proposed exploit. This research executes the minimal counterexample independently.

## Exact disposable reproduction

```bash
set -euo pipefail
D=$(mktemp -d /tmp/task2-r0-graft-XXXXXX)
trap 'rm -rf "$D"' EXIT
cd "$D"
git init -q
git config user.email test@example.invalid
git config user.name Task2
printf 'A\n' > p
git add p
git commit -qm baseline
B=$(git rev-parse HEAD)
T=$(git rev-parse "${B}^{tree}")
S=$(git rev-parse "${B}:p")
U=$(git commit-tree "$T" -m unrelated-root)
git merge-base --is-ancestor "$B" "$U" && echo UNEXPECTED || echo NON_ANCESTOR_BEFORE_GRAFT
printf '%s %s\n' "$U" "$B" > .git/info/grafts
git --no-replace-objects merge-base --is-ancestor "$B" "$U" && echo FALSE_ACCEPT || echo NON_ANCESTOR
git --no-replace-objects cat-file -t "$U"
test "$(git --no-replace-objects rev-parse "${U}^{tree}")" = "$T"
test "$(git --no-replace-objects rev-parse "${U}:p")" = "$S"
echo GRAFT_CAN_FORGE_ANCESTRY_WITH_IDENTICAL_TREE_AND_SOURCE_SHA
```

**Observed local console result** (SHA values generated only by the disposable test repository):

```text
GIT_VERSION=git version 2.47.3
BASE=04e7e329c48cf3a95a6468975e65e9ae331b897b
UNRELATED=83a46c3c0dfc413f1ae433ccf4894ee397c76bdd
ROOT_TREE=523651ee3ea1b8f2f4323c9d88ac6fac4dcc3b17
BLOB=f70f10e4db19068f79bc43844b49f3eece45c4e8
BEFORE_GRAFT=NON_ANCESTOR
WITH_GRAFT_NORMAL=FALSE_ACCEPT
WITH_GRAFT_NO_REPLACE=FALSE_ACCEPT
TYPE=commit
TARGET_TREE=523651ee3ea1b8f2f4323c9d88ac6fac4dcc3b17
TARGET_BLOB=f70f10e4db19068f79bc43844b49f3eece45c4e8
R0_EXACT_GUARD_PREDICATE=FALSE_ACCEPT
```

The local fixture confirms **an unrelated raw commit is falsely reported as a descendant** when a legacy graft adds a synthetic parent to the repo's metadata. Its Git object type remains `commit`, its tree equals the pinned tree, and the path `p` has the same blob SHA. No replacement refs are needed; `--no-replace-objects` does **not** prevent this on Git 2.47.3. This is a **real reproducible counterexample to the ancestry predicate** used in the current R0 verifier, not merely an untested AI hypothesis.

### Interpretation limits

This does **not** prove the real public archive contains graft metadata or that the original 36/36 Git-object drift counts are incorrect. The vulnerability is in standalone verifier acceptance for an untrusted or altered local Git checkout. Its existence means a scientific `original_pinned_source_objects_verified` result cannot be generalized to arbitrary checkouts solely from the current ancestry guard. It also does not imply historical first-known, real R1 admission, statistical skill, economic edge or trading actions.

## Bounded repair and acceptance protocol

Follow existing Task 2 R0 PR #1627 and [Task 1.5 owner #1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596), with a **single** research→Codex intake and no new supervisor or budget authority:

1. Make ancestry checks use **unmodified raw commit parents** or fail closed on every supported graft mechanism and untrusted Git process environment; do not merely add another assumption or bypass the existing `--no-replace-objects` flag.
2. Add a **deterministic positive fixture** for a truly descended commit and a **negative fixture** for an unrelated commit linked through `.git/info/grafts`. The bad fixture must yield exit **1** (unverifiable/provenance rejection), never exit 0 or scientific PASS. Test under a supported Git version with graft support, and document Git-version-dependent behavior.
3. Distinguish absent target path / genuinely changed type from `rev-parse`, `cat-file` or `merge-base` operational failures; operational errors must remain fail-closed and be diagnosed `UNKNOWN_OR_ERROR`, not unsupported `MISSING`/`TYPE_MISMATCH`/negative ancestry.
4. Make output path ordering deterministic across locale/ICU configurations where output hashes are compared. Preserve the already-fixed direct commit/tag, replacement-ref, file URL and source SHA/type fixtures.
5. Run exact branch regression suite, independent code review, CI, exact source blob readback and a fresh production-safe dry run against the previously pinned public inventory before considering merge. Historical inputs/forecasts/outcomes and the immutable previous receipt remain unchanged.

**Explicit status:** `R0_VERIFIER_SECURITY_REVIEW_BLOCKED_ON_REPRODUCED_COUNTEREXAMPLE`; `CODE_FIX_NOT_EXECUTED_HERE`; `R1_PROVIDER_FIRST_KNOWN_NOT_VERIFIED`; `R2_TO_R7_RUNS_FROM_THIS_TEST=0`. No private data, credentials, portfolio or paid model calls used for this deterministic reproduction.

**Machine-readable receipt:** [R0_SOL_GRAFT_EXECUTED_FALSIFIER_v1.json](2026-10-14__TASK2_R0_SOL_GRAFT_EXECUTED_FALSIFIER_v1.json).

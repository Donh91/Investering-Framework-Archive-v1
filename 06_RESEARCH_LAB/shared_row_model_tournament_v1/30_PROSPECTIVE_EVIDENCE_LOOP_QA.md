# Prospective Evidence Loop QA

- Market transforms in automation code: **NONE**. Transform semantics live only in frozen family contracts.
- Candidate decisions invented by controller: **NO**. Controller accepts only precomputed decisions for candidates whose required family freeze records are READY.
- Missing -> zero: **FORBIDDEN**.
- Backdated decisions: **FORBIDDEN**.
- Outcome semantics invented by maturation job: **NO**. Maturation copies only outcomes already registered on the shared row.
- Full Stack special disadvantage: **NO**. It remains eligible when its row-time family/version map and decision contract become reproducible.
- Tail-error reporting: scaffolded in weekly report, remains `UNAVAILABLE` until matured numeric divergence evidence exists.
- Canonical writes: **NONE**.
- Paid calls introduced: **0**.

The loop is operational in `COLLECTING` mode even while core transforms are unresolved. This is intentional: weekly automation must report what is missing rather than fabricate eligibility.

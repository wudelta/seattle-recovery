# ======================================================================
# FILE: aurora/subsystems/engineering_discovery/contracts/FINDING_RECONCILIATION.md
# START: ENGINEERING_FINDING_RECONCILIATION_CONTRACT
# ======================================================================

# Engineering Finding Reconciliation

**Knowledge State: VERIFIED**

**Subsystem:** engineering_discovery

---

## Purpose

This contract defines how Engineering Findings are reconciled during Initiative
closeout or postmortem.

Reconciliation determines the current disposition of each finding from the
Initiative using persisted evidence.

A finding does not automatically become future engineering work.

Engineering Discovery owns finding reconciliation semantics.

Planning owns deliberate creation of future Project → Initiative → Phase → Step
work after a human selects an engineering objective.

---

## Reconciliation Scope

Reconcile the Engineering Findings originating from one Planning Initiative.

The Initiative is the closeout scope.

Use the persisted Engineering Discovery closeout read boundary to retrieve
findings and their originating Planning provenance.

Reconciliation must begin from persisted finding evidence.

Do not reconstruct findings from conversation history, memory, or speculative
repository review.

---

## Required Closeout Disposition

Every finding presented for reconciliation must receive exactly one closeout
disposition:

1. `RESOLVED`
2. `INVALIDATED`
3. `ACCEPTED`
4. `REQUIRES_FUTURE_WORK`

These dispositions describe the closeout decision about the finding.

They are distinct from the persisted finding lifecycle state.

---

## RESOLVED

Use `RESOLVED` when the concrete observed condition has been corrected and
deterministic evidence proves the correction.

A finding may receive this disposition only when the Engineering Finding
lifecycle requirements for resolution are satisfied.

The durable finding lifecycle state should be `RESOLVED`.

Resolution evidence must identify the deterministic proof that the observed
condition no longer exists.

Do not mark a finding resolved merely because:

- the originating Step completed;
- the Initiative completed;
- the problem was discussed;
- a workaround exists;
- future work was planned;
- the finding is no longer blocking.

---

## INVALIDATED

Use `INVALIDATED` when persisted or newly obtained execution evidence proves
that the original finding no longer represents a valid engineering problem.

Invalidation means the finding's premise was disproved or superseded by
authoritative evidence.

Examples include:

- the allegedly missing authority existed and was reachable through the
  governing repository path;
- the observed behavior was caused by incorrect execution rather than a
  repository defect;
- later authoritative evidence demonstrates that the reported boundary
  conflict did not exist.

Invalidation must cite concrete evidence.

Invalidation is not the same as resolution.

Do not use `INVALIDATED` merely because the problem is inconvenient to address,
low priority, or no longer interesting.

---

## ACCEPTED

Use `ACCEPTED` when the finding remains valid, but the human closeout decision
is to accept the condition without creating corrective engineering work.

Acceptance acknowledges the persisted engineering problem and deliberately
chooses not to pursue remediation.

Typical reasons may include:

- the cost of correction is not justified;
- the limitation is intentionally tolerated;
- the condition is acceptable within the current product or engineering
  constraints.

An accepted finding is not falsely marked resolved.

Its lifecycle state remains `UNRESOLVED` unless separate resolution evidence
satisfies the Engineering Finding lifecycle contract.

Acceptance must be explicit.

Silence, omission, or failure to schedule work is not acceptance.

---

## REQUIRES_FUTURE_WORK

Use `REQUIRES_FUTURE_WORK` when the finding remains valid and unresolved and the
closeout decision is that corrective engineering work is still justified.

This disposition does not itself create Planning work.

The finding remains durable evidence available for a later human objective
selection boundary.

A later Planning workflow may use one or more selected findings as evidence for
a cleanup Initiative, but Engineering Discovery must not automatically convert
findings into executable work.

The durable finding lifecycle state remains `UNRESOLVED` until correction is
implemented and deterministically validated.

---

## Relationship to Finding Lifecycle State

Engineering Finding lifecycle state and closeout disposition answer different
questions.

Lifecycle state answers:

> Has the concrete engineering condition been deterministically corrected?

Closeout disposition answers:

> What is the deliberate closeout decision about this finding now?

The existing lifecycle states remain:

- `UNRESOLVED`
- `RESOLVED`

The closeout dispositions defined here must not be substituted for lifecycle
state.

In particular:

- `RESOLVED` disposition requires lifecycle state `RESOLVED`;
- `ACCEPTED` does not imply lifecycle resolution;
- `REQUIRES_FUTURE_WORK` requires the finding to remain available as unresolved
  evidence;
- `INVALIDATED` records that the finding is no longer considered a valid
  engineering problem and must preserve the evidence supporting that decision.

---

## Reconciliation Decision Rule

For each finding, evaluate persisted evidence in this order:

1. Has deterministic evidence proven the observed condition corrected?
   - Yes → `RESOLVED`.
2. Has authoritative evidence disproven or superseded the finding itself?
   - Yes → `INVALIDATED`.
3. Does the valid unresolved finding still justify corrective engineering work?
   - Yes → `REQUIRES_FUTURE_WORK`.
4. Otherwise, if the human deliberately accepts the valid unresolved condition:
   - `ACCEPTED`.

Do not infer `ACCEPTED` from absence of future work.

If no supported disposition can be reached, reconciliation is incomplete.

---

## Human Decision Boundary

Engineering Discovery may expose findings, evidence, provenance, and valid
reconciliation options.

A worker may determine whether evidence satisfies deterministic resolution or
invalidation criteria.

A worker must not independently choose the engineering objective represented by
future cleanup work.

The human decision boundary is required before unresolved findings become a
future Planning Initiative.

This preserves the Planning rule:

```text
persisted findings
    ↓
closeout reconciliation
    ↓
findings that still justify work
    ↓
human objective selection
    ↓
Planning generation
```

---

## Reconciliation Completeness

Initiative finding reconciliation is complete only when every finding in the
closeout scope has exactly one supported disposition.

A reconciliation result must preserve enough information to determine:

- finding identity;
- originating Planning provenance;
- finding category;
- blocking classification;
- persisted observed condition;
- persisted evidence;
- lifecycle state;
- selected closeout disposition;
- evidence or rationale supporting that disposition.

Findings assigned `REQUIRES_FUTURE_WORK` must remain retrievable after
reconciliation for later Planning use.

---

## Non-Goals

This contract does not define:

- a database schema for persisted closeout dispositions;
- a user interface for reconciliation;
- automatic cleanup Initiative creation;
- automatic priority selection;
- cleanup Initiative structure;
- Planning dictionary generation from findings;
- engineering-efficiency telemetry.

Those responsibilities require their own authoritative Planning work.

---

## Validation

This contract is sufficient when a representative Initiative closeout can take
every persisted finding and assign exactly one evidence-supported disposition:

- `RESOLVED`;
- `INVALIDATED`;
- `ACCEPTED`; or
- `REQUIRES_FUTURE_WORK`;

while valid unresolved findings selected as `REQUIRES_FUTURE_WORK` remain
available for later Planning without reconstructing conversation history.

---

# ======================================================================
# END: ENGINEERING_FINDING_RECONCILIATION_CONTRACT
# ======================================================================

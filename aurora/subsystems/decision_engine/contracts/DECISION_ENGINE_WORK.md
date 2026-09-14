# ======================================================================
# FILE: aurora/subsystems/decision_engine/contracts/DECISION_ENGINE_WORK.md
# START: DECISION_ENGINE_WORK_CONTRACT
# ======================================================================

# Decision Engine Work

**Knowledge State: VERIFIED**

**Subsystem:** decision_engine

---

## Purpose

This contract defines the durable persistence boundary for
`DecisionEngineWork`.

`DecisionEngineWork` represents organization-level work that has crossed the
Decision Engine's explicit human commit boundary.

It does not represent temporary reviewer selection, raw intake evidence,
Planning execution state, or a source subsystem's own disposition lifecycle.

This contract is intentionally narrow.

It establishes only the persistence invariants required before implementation
of the Decision Engine work model.

Later Planning Steps own aggregation behavior, intake disposition semantics,
Planning reconciliation, post-import reconciliation, and other lifecycle
details that cannot yet be defined safely.

---

## Ownership Boundary

The Decision Engine owns:

- durable `DecisionEngineWork`;
- the explicit organizational commit boundary that creates durable work;
- the invariant that committed organizational work remains durable independently
  of the lifetime of raw intake evidence;
- the organization-level identity of work that may later be aggregated,
  proposed to Planning, or otherwise reconciled.

The Decision Engine does not own:

- Delta Note capture, author privacy, author CRUD, or source persistence;
- Engineering Finding qualification, provenance, persistence, or lifecycle;
- Planning's Project → Initiative → Phase → Step hierarchy;
- Planning lifecycle transitions;
- the source subsystem's final disposition semantics;
- the final aggregation taxonomy;
- existing-Planning reconciliation behavior;
- post-import reconciliation behavior.

---

## Durable Work Boundary

`DecisionEngineWork` begins only after an explicit reviewer commit.

Before that commit, reviewer interaction is transient.

The normal boundary is:

```text
authorized unresolved intake
    ↓
reviewer selects a bounded subset
    ↓
transient working selection
    ↓
explicit commit
    ↓
DecisionEngineWork
```

Moving an intake item between review viewports does not create
`DecisionEngineWork`.

Selecting an intake item does not mark it processed, resolved, accepted,
approved, or otherwise terminal.

Browser or UI state must not become organizational workflow authority merely
because a reviewer has selected an item.

---

## Explicit Commit Invariant

Creation of `DecisionEngineWork` is a consequential organizational mutation.

It requires an explicit operation representing the reviewer's intent to commit
selected intake into durable Decision Engine work.

A generic CRUD action is not sufficient authority for this mutation.

The implementation that later owns commit must preserve:

- explicit intent;
- authorized actor identity;
- attributable creation;
- deterministic validation of the intended source set;
- rejection of ambiguous or invalid commit requests.

This contract does not define the final UI wording or service signature.

---

## Intake Resolution Cardinality

One intake record may resolve to:

```text
zero or one DecisionEngineWork
```

Multiple independent intake records may resolve to the same
`DecisionEngineWork`.

Therefore:

```text
Delta Note A ───────┐
Delta Note B ───────┼──→ DecisionEngineWork 7
Finding C ──────────┘
```

is valid.

The following is not valid:

```text
Delta Note A
    ├──→ DecisionEngineWork 7
    └──→ DecisionEngineWork 8
```

when the two work records represent unrelated organizational work.

If one intake record appears to contain multiple unrelated tasks, the system
must not silently resolve that record to multiple unrelated work records.

The ambiguity must remain visible for human mitigation.

---

## Mixed-Scope Intake

An intake item that contains multiple unrelated bodies of work is not a valid
one-to-one reconciliation candidate.

Mixed-scope detection must fail loudly enough that the reviewer can choose the
appropriate mitigation.

Possible mitigation behavior is intentionally not defined here.

Later workflow design may permit rewriting, splitting, rejecting, withdrawing,
or otherwise resolving mixed-scope intake.

This contract establishes only the invariant:

> Ambiguity must surface as work rather than being hidden inside flexible
> persistence.

A metadata field must not be used as a substitute for referential integrity in
order to bypass this rule.

---

## Source Lifetime Independence

Raw intake evidence and durable Decision Engine work have independent
lifetimes.

`DecisionEngineWork` must remain valid if an originating intake record is later
deleted under that source subsystem's retention policy.

The durable work record must not depend on source content remaining present
forever.

Likewise, deleting or retiring raw intake must not cascade-delete durable
`DecisionEngineWork`.

This contract does not require indefinite retention of Delta Notes or
Engineering Findings.

Retention policy remains deferred until operational evidence demonstrates
whether long-lived raw intake provides useful forensic value.

---

## Source-Specific Authority

Source intake remains owned by its originating subsystem.

For Delta Notes:

- Delta Notes owns human-entered capture and persistence;
- Delta Notes owns author privacy and author-scoped CRUD;
- the Decision Engine must not redefine those responsibilities.

For Engineering Findings:

- Engineering Discovery owns finding qualification, provenance, persistence,
  and lifecycle;
- the Decision Engine must not redefine finding resolution state or evidence
  semantics in this Step.

The Decision Engine may later coordinate organization-level reconciliation of
those sources without replacing their source authority.

---

## Resolving-Work Reference Direction

The expected relationship direction is from source intake toward durable
Decision Engine work.

Conceptually:

```text
DeltaNotesEntry.resolving_work
    → DecisionEngineWork | NULL

EngineeringFinding.resolving_work
    → DecisionEngineWork | NULL
```

The exact source-model fields are not implemented by this contract.

Their addition belongs to later authoritative work that owns intake
disposition semantics.

The important persistence rule is:

- a source may reference zero or one resolving work record;
- many sources may reference the same work record;
- `DecisionEngineWork` does not require reverse provenance fields in order to
  remain valid.

Django reverse relations may exist naturally when foreign keys are implemented,
but durable work does not own source lifecycle merely because reverse access is
available.

---

## DecisionEngineWork Source Independence

`DecisionEngineWork` is the normalized organization-level work product.

It should not require special persistence branches based on whether its source
was:

- one Delta Note;
- several Delta Notes;
- one Engineering Finding;
- several Engineering Findings;
- a mixture of source types;
- or later a directly authorized organizational work entry.

The durable work record represents the reconciled work itself.

Source-specific meaning remains in the source records and later reconciliation
evidence.

---

## Minimal Persistence Principle

Step 441 must implement the smallest model that satisfies this contract.

Do not add speculative fields merely because later workflow might need them.

In particular, this contract does not yet require durable fields for:

- Planning Project, Initiative, Phase, or Step linkage;
- aggregation groups or taxonomies;
- AI recommendation state;
- Planning proposal state;
- Planning dictionary paths;
- import results;
- duplicate scores;
- classification taxonomies;
- final source disposition;
- post-import provenance;
- retention policy;
- prioritization;
- assignment;
- execution state.

Those concerns belong to later authoritative Steps when their real inputs and
outputs are available.

---

## Metadata Boundary

Flexible metadata may later be useful for supporting explanation or
non-authoritative analysis.

Metadata must not replace authoritative relational state.

For example, metadata may eventually preserve information such as:

- review notes;
- classifier explanation;
- detected ambiguity;
- suggested duplicate candidates;
- non-authoritative rationale.

Metadata must not be used to encode authoritative multi-target work resolution
when the domain invariant requires one source to resolve to at most one durable
work record.

Foreign keys answer authoritative relationship questions.

Metadata may explain why.

---

## Planning Boundary

`DecisionEngineWork` is not Planning work.

Creation of durable Decision Engine work does not:

- create a Project;
- create an Initiative;
- create a Phase;
- create a Step;
- activate Planning lifecycle state;
- authorize execution.

The later Decision Engine workflow may propose transition into Planning.

Planning remains the authority that validates, imports, and executes the
resulting hierarchy.

---

## Approval Boundary

This contract distinguishes two concepts:

```text
commit to DecisionEngineWork
    ≠
approve a Planning proposal
```

The first creates durable Decision Engine work from selected organizational
intake.

The second, owned by later workflow, authorizes a proposed representation of
that work for Planning handoff.

Step 440 defines only the first persistence boundary.

---

## Validation Requirements

The persistence design is valid only if a later implementation can prove all of
the following:

1. transient reviewer selection does not create durable work;
2. an explicit commit operation creates durable `DecisionEngineWork`;
3. one intake record cannot resolve to multiple unrelated work records;
4. multiple intake records may resolve to one work record;
5. mixed-scope intake remains unresolved until a human chooses mitigation;
6. durable work does not depend on indefinite source retention;
7. deleting source intake cannot delete durable work;
8. source subsystem ownership remains intact;
9. creation of `DecisionEngineWork` does not mutate Planning;
10. later implementation can remain minimal without speculative lifecycle
    fields.

---

## Deferred Design

The following are deliberately unresolved by this contract:

- the exact `DecisionEngineWork` field set beyond minimum durable identity and
  work content;
- the exact service signature for explicit commit;
- intake disposition values;
- whether `processed` becomes derived or otherwise constrained;
- Engineering Finding terminal-resolution integration;
- aggregation operations;
- classification taxonomy;
- existing-Planning reconciliation;
- Planning proposal persistence;
- Planning import-result linkage;
- post-import reconciliation;
- raw-intake retention policy;
- direct Decision Engine work creation without intake sources.

These are not omissions to be filled opportunistically.

They are explicit design boundaries owned by later Planning Steps.

---

## Repository Placement

The future subsystem-local model belongs at:

```text
aurora/subsystems/decision_engine/models.py
```

Django model registration may continue to use the repository's established
application registration/import surface as required by the existing Aurora
application structure.

This contract does not itself create or register the model.

---

## Sufficient Authority

A worker has sufficient authority for Step 440 when it knows:

1. Decision Engine owns durable organization-level work;
2. raw selection remains transient until explicit commit;
3. one intake record resolves to zero or one durable work record;
4. many intake records may resolve to one durable work record;
5. durable work survives independently of raw intake retention;
6. source subsystems retain their own lifecycle and privacy authority;
7. Planning is not mutated by DecisionEngineWork creation;
8. later reconciliation details remain intentionally deferred.

Do not expand the persistence contract merely because later workflow questions
can already be imagined.

---

# ======================================================================
# END: DECISION_ENGINE_WORK_CONTRACT
# ======================================================================

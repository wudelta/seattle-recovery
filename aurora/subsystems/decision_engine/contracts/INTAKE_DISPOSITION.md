# ======================================================================
# FILE: aurora/subsystems/decision_engine/contracts/INTAKE_DISPOSITION.md
# START: DECISION_ENGINE_INTAKE_DISPOSITION
# ======================================================================

# Decision Engine Intake Disposition

**Knowledge State: VERIFIED**

**Subsystem:** decision_engine

---

## Purpose

This contract defines how organizational intake leaves the Decision Engine's
actionable backlog.

It owns disposition semantics only.

It does not replace the lifecycle authority of Delta Notes, Engineering
Discovery, Planning, or any other source subsystem.

The governing distinction is:

```text
source lifecycle
    ≠
Decision Engine disposition
    ≠
Planning execution
```

---

## Ownership Boundary

The Decision Engine owns:

- organization-level intake disposition;
- the distinction between actionable and terminal intake;
- whether organizational work was committed from intake;
- the resolving `DecisionEngineWork` relationship when durable work is claimed;
- human organizational decisions to reject or defer intake;
- attribution and durable explanation for terminal disposition.

The Decision Engine does not own:

- Delta Note author identity, author privacy, capture, edit, or deletion;
- Engineering Finding qualification, provenance, or resolution semantics;
- Planning Project → Initiative → Phase → Step lifecycle;
- source-specific retention behavior;
- source-specific resolution evidence;
- execution of committed organizational work.

---

## Disposition States

Decision Engine intake uses the following semantic states.

### OPEN

`OPEN` is non-terminal.

The item remains actionable and available for organizational review.

It has not been deferred, rejected, withdrawn, or committed into durable work.

### DEFERRED

`DEFERRED` is non-terminal.

A human has deliberately postponed organizational action.

Deferred intake remains eligible for later review.

Deferral must not be treated as processing, rejection, withdrawal, or work
commitment.

### NEEDS_MITIGATION

`NEEDS_MITIGATION` is non-terminal.

The item cannot be reconciled safely in its current form.

Examples include:

- mixed-scope intake containing unrelated bodies of work;
- ambiguous organizational meaning;
- conflicting or insufficient evidence;
- a source condition that requires human clarification before disposition.

The ambiguity remains visible until a human chooses a valid mitigation.

### WORK_COMMITTED

`WORK_COMMITTED` is terminal for Decision Engine intake.

The item has crossed the explicit organizational commit boundary and must
reference exactly one resolving `DecisionEngineWork`.

Multiple intake records may terminate as `WORK_COMMITTED` while referencing the
same `DecisionEngineWork`.

One intake record must not reference multiple unrelated work records.

### REJECTED

`REJECTED` is terminal for Decision Engine intake.

A human has determined that the item must not become durable organizational
work.

`REJECTED` must not reference a resolving `DecisionEngineWork`.

Rejection is an organizational disposition.

It does not delete the source record and does not redefine the source
subsystem's own lifecycle.

### WITHDRAWN

`WITHDRAWN` is terminal for Decision Engine intake.

Withdrawal represents source-author-controlled removal from organizational
consideration where the source subsystem permits that action.

`WITHDRAWN` must not reference a resolving `DecisionEngineWork`.

Withdrawal must preserve the source subsystem's authorship and authorization
rules.

The Decision Engine must not manufacture withdrawal authority for a source that
does not permit it.

---

## Terminality

The terminal Decision Engine dispositions are:

```text
WORK_COMMITTED
REJECTED
WITHDRAWN
```

The non-terminal dispositions are:

```text
OPEN
DEFERRED
NEEDS_MITIGATION
```

Terminality answers only:

> Should this intake item remain in the actionable Decision Engine backlog?

It does not answer whether the source record itself is deleted, resolved,
retained, or executable.

---

## Processed Semantics

`processed` is not an independent human-controlled lifecycle transition.

The semantic invariant is:

```text
processed = true
    if and only if
a valid terminal Decision Engine disposition exists
```

Therefore:

```text
OPEN              → processed = false
DEFERRED          → processed = false
NEEDS_MITIGATION  → processed = false
WORK_COMMITTED    → processed = true
REJECTED          → processed = true
WITHDRAWN         → processed = true
```

A generic CRUD action must not set `processed=True` without establishing a valid
terminal disposition.

The existing Delta Note `processed` field may remain as a persisted compatibility
field if later implementation requires it, but its value must be constrained by
this semantic authority.

Whether `processed` becomes derived, validated, synchronized, or eventually
removed remains an implementation decision for the authoritative Step that
enforces this contract.

---

## Resolving Work Invariant

When disposition is `WORK_COMMITTED`:

```text
resolving_work
    → exactly one DecisionEngineWork
```

When disposition is any other state:

```text
resolving_work
    → NULL
```

This preserves the existing persistence invariant:

```text
one intake
    → zero or one DecisionEngineWork

many intake records
    → one shared DecisionEngineWork
```

A flexible metadata field must not replace the authoritative relational
reference.

---

## Duplicate and Related Intake

Duplicate or related intake does not require a separate terminal disposition.

When several intake records describe the same organization-level work:

```text
source A ─┐
source B ─┼──→ DecisionEngineWork 7
source C ─┘
```

each source may terminate as:

```text
WORK_COMMITTED
resolving_work = DecisionEngineWork 7
```

This preserves independent source identity while consolidating the durable
organizational work.

A duplicate must not be silently discarded merely because another source
describes the same condition.

---

## Mixed-Scope Intake

An intake record containing multiple unrelated bodies of work must not be
silently resolved to multiple unrelated `DecisionEngineWork` records.

The default Decision Engine disposition is:

```text
NEEDS_MITIGATION
```

until a human chooses a valid source-permitted mitigation.

Possible mitigation may later include:

- source-author editing;
- source-author withdrawal;
- rejection;
- clarification;
- other source-owned correction.

This contract does not authorize automatic source rewriting or splitting.

---

## Attribution Requirement

Every terminal Decision Engine disposition must preserve enough durable state to
answer:

- who authorized the disposition;
- what terminal disposition was chosen;
- when the disposition occurred;
- why the item left the actionable backlog;
- which `DecisionEngineWork` resolved it, when work commitment is claimed.

Exact persistence fields belong to the implementation Step.

The semantic requirement is mandatory even if the final model shape differs by
source type.

---

## Delta Note Boundary

Delta Notes owns:

- human-entered capture;
- author identity;
- author-scoped display;
- editing;
- deletion;
- privacy boundaries.

The Decision Engine may consume an authorized Delta Note as organizational
intake.

The Decision Engine must not grant one user access to another user's private
Delta Note merely to perform reconciliation.

A Delta Note author may continue to create, edit, or delete their own unresolved
note according to Delta Notes authority.

If a Delta Note has already crossed a consequential Decision Engine terminal
boundary, later implementation must preserve organizational referential
integrity without silently revoking the author's source authority.

The exact retention and deletion interaction remains implementation work.

---

## Engineering Finding Boundary

Engineering Discovery owns:

```text
UNRESOLVED
RESOLVED
resolution_evidence
resolved_at
```

Decision Engine disposition must not redefine those fields.

An `UNRESOLVED` Engineering Finding may be:

```text
WORK_COMMITTED
```

when organizational work has been durably accepted but the engineering problem
has not yet been fixed.

Likewise, Engineering Discovery may later mark the Finding `RESOLVED` only
through its own resolution authority and evidence rules.

Therefore:

```text
Finding resolution_state
    ≠
Decision Engine disposition
```

A Decision Engine terminal disposition is not proof that the engineering
condition itself has been remediated.

---

## Planning Boundary

No Decision Engine intake disposition directly creates or activates Planning.

In particular:

```text
WORK_COMMITTED
    ≠
Planning approved
    ≠
Planning imported
    ≠
Planning executable
```

`WORK_COMMITTED` establishes only that durable organization-level work exists.

Later Decision Engine workflow may propose that work to Planning.

Planning remains the authority that validates, imports, and executes the
resulting hierarchy.

---

## Human Decision Boundary

The following consequential dispositions require human authorization unless a
later repository authority explicitly delegates otherwise:

- `WORK_COMMITTED`;
- `REJECTED`;
- `WITHDRAWN`;
- `DEFERRED` when deferral represents an organizational prioritization decision.

AI may recommend a disposition.

AI recommendation is not organizational authorization.

`NEEDS_MITIGATION` may be surfaced deterministically when invariant validation
shows that safe reconciliation is impossible.

---

## Prohibited Behavior

The Decision Engine must not:

- set `processed=True` merely because a UI button was clicked;
- claim `WORK_COMMITTED` without a resolving `DecisionEngineWork`;
- retain a resolving work reference for `REJECTED` or `WITHDRAWN`;
- mark `OPEN`, `DEFERRED`, or `NEEDS_MITIGATION` as processed;
- treat Decision Engine disposition as Engineering Finding resolution;
- treat Decision Engine disposition as Planning execution authority;
- silently split one mixed-scope source across unrelated work records;
- silently discard duplicate intake;
- bypass source-author privacy or lifecycle authority;
- encode authoritative work resolution only in metadata.

---

## Validation Requirements

The design is valid only if later implementation can prove:

1. non-terminal intake remains actionable;
2. terminal intake leaves the actionable backlog;
3. `processed` cannot become true without a terminal disposition;
4. `WORK_COMMITTED` requires exactly one resolving `DecisionEngineWork`;
5. `REJECTED` and `WITHDRAWN` require no resolving work reference;
6. many intake records may resolve to one shared `DecisionEngineWork`;
7. mixed-scope intake remains visible for mitigation;
8. Delta Note privacy and author-owned source behavior remain intact;
9. Engineering Finding resolution remains owned by Engineering Discovery;
10. no disposition directly creates or activates Planning work;
11. every terminal disposition is attributable and explainable;
12. a generic CRUD action cannot manufacture terminal workflow state.

---

## Deferred Implementation

This contract does not yet choose:

- the exact persistence model for disposition fields;
- whether all source types share one disposition relation or use source-local
  fields;
- whether Delta Note `processed` remains persisted or becomes derived;
- exact terminal-attribution field names;
- exact rejection or withdrawal reason schemas;
- exact UI controls;
- exact commit service signature;
- source deletion behavior after terminal disposition;
- retention policy;
- Planning proposal persistence;
- post-import reconciliation.

Those decisions belong to their authoritative implementation Steps.

---

## Sufficient Authority

A worker has sufficient authority for intake disposition when it knows:

1. which states are terminal and non-terminal;
2. when `processed` is semantically true;
3. when resolving `DecisionEngineWork` is required or forbidden;
4. that duplicates may share one durable work record;
5. that mixed-scope intake remains unresolved pending mitigation;
6. that Delta Notes retain author and privacy authority;
7. that Engineering Findings retain resolution authority;
8. that Decision Engine disposition does not create Planning execution;
9. that terminal decisions must be attributable and explainable.

Do not add source lifecycle behavior merely because disposition touches a source
record.

---

# ======================================================================
# END: DECISION_ENGINE_INTAKE_DISPOSITION
# ======================================================================

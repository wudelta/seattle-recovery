# ======================================================================
# FILE: aurora/subsystems/planning/contracts/LIFECYCLE_AND_RECONCILIATION.md
# START: PLANNING_LIFECYCLE_AND_RECONCILIATION_CONTRACT
# ======================================================================

# Planning Lifecycle and Reconciliation

## Purpose

This contract defines how Planning distinguishes editable planning data from
authoritative execution state.

Planning owns:

```text
Project → Initiative → Phase → Step
```

Planning also owns the lifecycle rules that determine which work is current,
paused, completed, historical, or eligible for execution.

Generic CRUD must not become the authority for workflow transitions.

---

## Descriptive Data vs Workflow State

Ordinary CRUD may edit descriptive planning information such as:

```text
title
description
estimate
risk
validation requirements
position
```

Workflow-sensitive fields must be changed through deterministic lifecycle
operations rather than arbitrary form updates.

These include:

```text
status
assignment
completion
active-work transitions
historical execution attribution
```

The lifecycle authority must validate the current state before mutation.

---

## Active Work

Execution state is user-dependent.

For a developer, Planning should expose one current executable work path:

```text
ACTIVE Initiative
    ↓
ACTIVE Phase
    ↓
ACTIVE Step
```

The active path must be derived from Planning lifecycle state.

`UserPosition` is not execution authority.

---

## Navigation State

`UserPosition` represents where a user is currently browsing in Planning.

It may point to:

```text
historical work
completed work
paused work
future work
```

Therefore:

> Navigation state must never be interpreted as proof of current executable
> work.

Session Management may display navigation state, but Step execution must resolve
through Planning lifecycle authority.

---

## Initiative Lifecycle

A developer may have at most one current ACTIVE Initiative.

Activating another Initiative for that developer must deterministically resolve
the existing ACTIVE Initiative first.

Normal behavior is:

```text
current ACTIVE Initiative
    ↓
PAUSED
    ↓
requested Initiative
    ↓
ACTIVE
```

Pausing an Initiative does not automatically change the status of its current
Phase or Step.

Their ACTIVE states may remain as the Initiative's resume position.

---

## Phase Lifecycle

A Phase represents a bounded execution responsibility within an Initiative.

A Phase has one current `assigned_to` developer.

Within an Initiative, active Phase state identifies the Phase to resume when
that Initiative becomes executable again.

Reassigning a Phase changes responsibility for unfinished work.

It must not rewrite historical execution evidence.

---

## Step Lifecycle

A Step is the smallest Planning unit against which active engineering work is
tracked.

A Step's current execution responsibility is derived from its Phase.

Independent Step assignment should not be treated as the long-term source of
truth.

Historical Step attribution must remain separate from current Phase ownership.

Planning must preserve:

```text
who worked on the Step
who completed the Step
when work occurred
```

Current Phase reassignment must not rewrite those facts.

---

## Time Attribution

`TimeEntry` records actual work performed against a Step.

A TimeEntry records:

```text
user
step
started_at
ended_at
```

TimeEntry history is authoritative evidence of who performed work.

Engineering Session Management may coordinate Step-work start and end events,
but Planning owns the TimeEntry records.

---

## Completion Attribution

Current assignment and historical completion are different concepts.

The intended model is:

```text
Phase.assigned_to
    current execution responsibility

Step completion attribution
    historical record of who completed the Step

TimeEntry.user
    detailed record of who spent time working on the Step
```

Completion behavior must be implemented through a deterministic lifecycle
transition rather than direct status mutation.

---

## Pause and Resume

Pausing higher-level work preserves its internal resume position.

Example:

```text
Initiative A — PAUSED
    Phase 2 — ACTIVE
        Step 4 — ACTIVE
```

This does not mean Step 4 is currently executable.

It means:

> If Initiative A becomes ACTIVE again, Phase 2 / Step 4 is its saved resume
> position.

Executable work depends on the complete active hierarchy.

---

## Planning Creation

Creating Planning records is not merely CRUD.

A new Initiative should normally originate from a planning workflow:

```text
engineering intent
    ↓
repository and Planning evidence
    ↓
AI/human discussion
    ↓
planning proposal
    ↓
validation
    ↓
canonical Planning mutation
```

The proposal must request only genuinely missing information.

It must not invent repository state or silently assume unfinished work.

---

## Dictionary Import

`import_planning_dictionary` is a transport and mutation mechanism.

It is not the authority that decides what Planning work should exist.

The correct workflow is:

```text
planning decision
    ↓
validated planning dictionary
    ↓
dry-run
    ↓
apply
```

Dictionary generation and reconciliation occur before import.

---

## Reconciliation

Planning records may become stale as repository reality evolves.

Reconciliation compares:

```text
persisted Planning state
        +
repository evidence
        +
historical execution evidence
        +
current engineering intent
```

The objective is to determine whether existing work is:

```text
STILL VALID
PARTIALLY IMPLEMENTED
COMPLETED IN REALITY
SUPERSEDED
DUPLICATE
OBSOLETE
CANCELLED
```

These are reconciliation classifications, not necessarily persisted lifecycle
statuses.

---

## Historical Work

Historical Planning records should be preserved when they provide useful
engineering history.

Historical records must not automatically become executable work.

A stale Initiative may remain valuable evidence even when its original plan has
been superseded by a better architecture.

Reconciliation should prefer preservation plus explicit lifecycle correction
over destructive deletion.

---

## Progressive Evidence

AI workers must not require repository-wide or database-wide dumps for ordinary
Planning decisions.

Evidence should be progressively bounded:

```text
global Planning summary
    ↓
Initiative summary
    ↓
Phase or Step detail
    ↓
Hansel breadcrumb
    ↓
task-specific repository authority
```

Escalate only while uncertainty remains.

---

## Hansel Integration

Planning determines what work requires reconciliation.

Hansel determines where repository authority for that work lives.

The normal discovery path is:

```text
Planning record
    ↓
identify owning subsystem or authority
    ↓
follow Hansel
    ↓
load smallest sufficient repository evidence
    ↓
return to Planning reconciliation
```

Do not perform broad repository discovery when Hansel can provide a narrower
authority.

---

## Engineering Session Integration

Engineering Session Management coordinates work occurring inside an active
engineering session.

Planning remains authoritative for:

```text
current executable Step
Step lifecycle
TimeEntry persistence
planning reconciliation
```

Engineering Session Management may invoke Planning lifecycle operations but
must not duplicate Planning execution state.

---

## Deterministic Transitions

Lifecycle operations must:

1. validate the requested transition;
2. inspect conflicting current state;
3. identify required side effects;
4. reject ambiguous or invalid transitions;
5. explain significant consequences when human review is warranted;
6. apply the transition atomically;
7. leave Planning in a valid state.

Examples include:

```text
activate Initiative
pause Initiative
resume Initiative
activate Phase
activate Step
reassign Phase
start Step work
end Step work
complete Step
```

Generic API persistence must not bypass these rules.

---

## Current Bootstrap State

Existing Planning data predates these lifecycle guarantees.

Until reconciliation is complete:

```text
existing statuses are historical evidence
not automatically authoritative execution state
```

New lifecycle services must not assume old records are internally consistent.

---

## Validation

Planning lifecycle and reconciliation are functioning correctly when:

1. navigation state cannot accidentally determine executable work;
2. invalid concurrent active-work states are prevented;
3. pause/resume preserves intended work position;
4. assignment changes do not rewrite historical execution evidence;
5. Step time is attributed through Planning TimeEntries;
6. lifecycle transitions are deterministic and validated;
7. stale Planning records can be reconciled against repository reality;
8. AI workers can obtain sufficient evidence without broad dumps;
9. planning dictionaries are produced from validated decisions rather than
   treated as the planning process itself.

# ======================================================================
# FILE: aurora/subsystems/planning/contracts/LIFECYCLE_AND_RECONCILIATION.md
# END: PLANNING_LIFECYCLE_AND_RECONCILIATION_CONTRACT
# ======================================================================

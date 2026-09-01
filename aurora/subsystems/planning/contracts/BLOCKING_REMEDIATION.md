# ======================================================================
# FILE: aurora/subsystems/planning/contracts/BLOCKING_REMEDIATION.md
# START: PLANNING_BLOCKING_REMEDIATION
# ======================================================================

# Planning Blocking Remediation

**Knowledge State: VERIFIED**

---

## Purpose

Define the Planning-owned interruption workflow used when a qualified
Engineering Finding is BLOCKING.

A blocking discovery does not create a second engineering objective.

It creates remedial work inside the already-authoritative Initiative so the
blocked Step can later resume.

---

## Ownership Boundary

Engineering Discovery owns:

- finding qualification;
- BLOCKING versus NON_BLOCKING classification;
- finding persistence;
- the durable link from a finding to its remedial Phase.

Planning owns:

- creation of the remedial Phase and Steps;
- Planning validation;
- position assignment;
- lifecycle transitions;
- activation of the remedial executable path;
- deterministic return to prior unfinished Initiative work.

Engineering Discovery must not create or directly mutate Planning rows.

Planning does not decide whether an Engineering Finding qualifies or whether it
is BLOCKING.

---

## Controlled Interruption

The authoritative workflow is:

```text
ACTIVE Initiative
    ↓
ACTIVE Phase
    ↓
ACTIVE Step
    ↓
qualified BLOCKING Engineering Finding
    ↓
append remedial Phase to same Initiative
    ↓
activate remedial Phase / first remedial Step
    ↓
previous Phase becomes PAUSED
    ↓
perform and validate remedial work
    ↓
complete / approve remedial Phase
    ↓
normal establish_initiative_work()
    ↓
earliest unfinished prior Phase
    ↓
retained interrupted Step resume position
```

No separate BLOCKED Planning status is introduced.

---

## Remedial Planning Shape

One routing operation adds exactly one new Phase to the current Initiative.

The new Phase:

- must enter Planning as `PLANNED`;
- must contain at least one Step;
- must be appended through Planning's existing dictionary updater;
- must not create another Initiative;
- must not target another Project or Initiative;
- must not reorder existing work.

Every nested remedial Step must enter as `PLANNED`.

After the append succeeds, Planning activates the first remedial Step through
existing lifecycle orchestration.

---

## Current-Step Authority

The Finding's originating Step must still be the lifecycle-authoritative current
Step when routing occurs.

If the worker has already advanced elsewhere, remediation routing must fail
rather than interrupt unrelated work.

The caller cannot select an arbitrary Planning target.

---

## Existing Authorities Reused

Append-only Planning persistence:

```text
aurora/subsystems/planning/io/updater.py
```

Lifecycle activation:

```text
aurora/subsystems/planning/services/lifecycle/orchestration.py
```

Current executable Step resolution:

```text
aurora/subsystems/planning/services/time_tracking.py
```

Bounded remedial workflow:

```text
aurora/subsystems/planning/services/remediation.py
```

The remediation workflow composes these authorities; it does not reproduce
their persistence or lifecycle rules.

---

## Return-to-Work Invariant

The interrupted work is not completed or cancelled.

Existing lifecycle semantics preserve its resume state.

Activating the remedial Phase pauses the previously ACTIVE Phase. Existing child
Step state is retained beneath that paused parent.

When remedial work finishes and no ACTIVE Phase remains,
`establish_initiative_work()` selects the earliest unfinished Phase by position.
Because the remedial Phase was appended after existing work, the interrupted
Phase is selected before later planned work.

Its retained Step state becomes the resume position.

This return path must remain deterministic.

---

## Duplicate Routing

A persisted Engineering Finding may have at most one remedial Phase.

The finding stores that relation durably.

A second attempt to route the same blocker must fail rather than create duplicate
remediation.

---

## Validation

A valid end-to-end blocking-remediation scenario proves:

1. one Step is lifecycle-authoritative and ACTIVE;
2. one finding against that Step is persisted as BLOCKING / UNRESOLVED;
3. one remedial Phase is appended to the same Initiative;
4. the finding points durably to that Phase;
5. the remedial Phase becomes ACTIVE;
6. its first Step becomes ACTIVE;
7. the interrupted Phase becomes PAUSED without being completed;
8. no second ACTIVE Initiative is created;
9. remedial work can complete through ordinary Planning workflow;
10. normal work establishment returns to the interrupted prior Phase and Step.

Do not validate by manufacturing conflicting lifecycle state that normal
application behavior cannot produce.

# ======================================================================
# END: PLANNING_BLOCKING_REMEDIATION
# ======================================================================

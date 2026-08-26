# ======================================================================
# FILE: aurora/subsystems/planning/contracts/INITIATIVE_TRANSITION.md
# START: PLANNING_INITIATIVE_TRANSITION
# ======================================================================

# Planning Initiative Transition

## Purpose

This contract owns the transition between one executable Planning Initiative
and the next.

It applies when:

- an Initiative has been completed;
- an Initiative has been deliberately paused;
- no executable engineering objective is currently active;
- or a worker has been asked to determine what engineering work should happen
  next.

The worker does not choose the engineering objective.

The worker exposes the available Planning choices and preserves the human
decision boundary.

---

## Between-Initiative Gap

When no engineering task is currently authoritative, enter the
Between-Initiative Gap.

The Gap exists to move from:

```text
no current executable objective
    ↓
Planning candidates
    ↓
human decision
    ↓
validated Initiative
    ↓
ACTIVE Initiative → ACTIVE Phase → ACTIVE Step
```

Do not invent an engineering objective merely because no Initiative is active.

---

## Candidate Presentation

Present all unfinished Initiative candidates in this order:

```text
1. PAUSED
2. PLANNED
```

Within each status group, preserve existing Planning order.

PAUSED Initiatives appear first because previously started work deserves review.

PAUSED does not mean highest priority.

A paused Initiative may be:

- resumed;
- corrected;
- superseded;
- cancelled;
- or left paused.

The human decides what happens next.

Do not score, rank, or autonomously select an Initiative.

---

## Existing-Initiative Route

When the human selects an existing PAUSED or PLANNED Initiative:

1. inspect only that Initiative and its current Phase and Step state;
2. follow Hansel only when repository evidence is required to determine whether
   the planned work remains valid;
3. stop discovery as soon as the Initiative can be classified.

Classify the selected Initiative as one of:

```text
STILL VALID
NEEDS CORRECTION
SUPERSEDED
OBSOLETE
```

Then:

```text
STILL VALID
    → resume or activate

NEEDS CORRECTION
    → revise affected Planning records
    → validate
    → activate

SUPERSEDED
    → preserve historical evidence
    → cancel when appropriate
    → create or select replacement work

OBSOLETE
    → cancel through Planning
```

Do not perform repository-wide discovery merely because an old Initiative was
selected.

---

## New-Objective Route

When the human identifies a new engineering objective:

```text
new engineering objective
    ↓
Gap discussion
    ↓
sufficient human engineering intent
    ↓
canonical Planning dictionary generation
    ↓
dry-run
    ↓
apply
    ↓
verify persisted Planning hierarchy
    ↓
activate Initiative
    ↓
establish executable Phase and Step
```

Planning dictionary generation authority:

```text
aurora/subsystems/planning/contracts/PLANNING_DICTIONARY_GENERATION.md
```

Do not create a separate Planning Handoff artifact.

The temporary planning dictionary is transport, not durable Planning authority.

---

## Git Boundary

Planning Initiative state and Git branch state should remain aligned.

### Leaving an Initiative

Before deliberately switching Initiatives:

1. reach a logical validated stopping point;
2. inspect repository state;
3. commit deliberate repository changes;
4. push the Initiative branch.

For a PAUSED Initiative:

```text
Planning Initiative PAUSED
    ↕
feature/<initiative_slug> preserved
```

Do not merge a paused Initiative merely because work has stopped temporarily.

### Completing an Initiative

A completed Initiative creates an integration boundary:

```text
validate Initiative branch
    ↓
merge current main into Initiative branch when needed
    ↓
resolve conflicts on Initiative branch
    ↓
validate again
    ↓
merge Initiative branch into main
    ↓
validate main
    ↓
push main
```

Use merge rather than rebase unless an observed engineering need justifies a
different strategy.

### Entering an Initiative

For a new Initiative:

```text
current main
    ↓
create feature/<initiative_slug>
```

For a resumed Initiative:

```text
existing Initiative branch
    ↓
merge current main when main has advanced
    ↓
resolve and validate
```

Do not use automatic stashing as part of the normal transition workflow.

---

## Lifecycle Activation

After the human selects or establishes the next Initiative, use Planning
lifecycle authority to establish one executable path:

```text
ACTIVE Initiative
    ↓
ACTIVE Phase
    ↓
ACTIVE Step
```

Existing ACTIVE child state inside a resumed hierarchy is a valid resume point.

A PAUSED Phase may retain an ACTIVE Step so that its local resume position is
preserved.

Do not normalize away valid resume state.

Worker-facing repeated Planning transitions should use:

```text
aurora/subsystems/planning/services/workflow.py
```

Do not reconstruct validation, completion, review-boundary, and advancement
logic from lower-level lifecycle services when the canonical workflow operation
already exists.

---

## Return to Hansel

Once an executable Step exists, that Step becomes the engineering task.

Return to repository discovery through:

```text
aurora/subsystems/hansel/contracts/HANSEL.md
```

Hansel then routes the executable task to its owning repository authority.

---

## Validation

A clean-context transition succeeds when:

1. a worker can discover this contract from repository-owned authority;
2. PAUSED and PLANNED candidates are presented without autonomous selection;
3. the human selects or defines the engineering objective;
4. existing work is reconciled only as deeply as necessary;
5. new work uses canonical Planning generation authority;
6. Planning establishes exactly one executable Initiative → Phase → Step path;
7. Git state is aligned with the selected Initiative;
8. the resulting Step can re-enter Hansel for task-specific repository work;
9. no hidden conversation history is required.

# ======================================================================
# END: PLANNING_INITIATIVE_TRANSITION
# ======================================================================
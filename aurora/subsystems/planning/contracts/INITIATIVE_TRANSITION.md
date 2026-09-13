# ======================================================================
# FILE: aurora/subsystems/planning/contracts/INITIATIVE_TRANSITION.md
# START: PLANNING_INITIATIVE_TRANSITION
# ======================================================================

# Planning Initiative Transition

## Purpose

This contract owns the actor-local transition between one executable Planning
Initiative and the next.

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
Planning candidates + new-objective option
    ↓
human decision
    ↓
validated Initiative
    ↓
ACTIVE Initiative → ACTIVE Phase → ACTIVE Step
```

Do not invent an engineering objective merely because no Initiative is active.

---

## Persisted Planning State

Before presenting candidates or deciding which transition route applies, inspect
persisted Planning state through the deterministic application-level entry
point catalogued by Planning:

```text
aurora/management/commands/inspect_planning_state.py
```

Start with compact reconciliation evidence:

```text
daurora-cmd inspect_planning_state
```

Use the result to determine whether an ACTIVE Initiative already exists or the
Between-Initiative Gap applies.

If an ACTIVE Initiative exists, do not present PAUSED or PLANNED candidates.
Resume the existing executable hierarchy through Planning lifecycle authority.

If no ACTIVE Initiative exists, the Between-Initiative Gap applies.

Use persisted PAUSED and PLANNED Initiative state as the Planning candidate
source.

The actor-local decision surface must include:

```text
PAUSED Initiatives
+
PLANNED Initiatives
+
define an entirely new engineering objective
```

The ability to define an entirely new engineering objective is a permanent Gap
choice. It remains available regardless of whether PAUSED or PLANNED
Initiatives exist.

Engineering Findings, Delta Notes, and organization-wide reconciliation are not
prerequisites for selecting, resuming, or defining the actor's next engineering
objective.

The worker must not score, rank, prioritize, or autonomously select among
Planning candidates.

The human remains the authority for deciding what engineering objective happens
next.

The human may define an objective that does not originate from any persisted
Planning candidate or other repository evidence.

Escalate to Initiative-scoped or `--full` inspection only when the compact
evidence is insufficient for the current transition.

Do not reconstruct current Planning state through ad hoc ORM queries when the
deterministic inspection entry point can answer the question.

---

## Candidate Presentation

Present all unfinished Planning Initiative candidates in this order:

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

These Initiative candidates form the actor-local Planning decision surface.

The permanent option to define an entirely new engineering objective must also
remain visible at the human decision boundary.

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

When the human defines a new engineering objective:

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
verify persisted PLANNED Initiative
```

Planning dictionary generation authority:

```text
aurora/subsystems/planning/contracts/PLANNING_DICTIONARY_GENERATION.md
```

A newly accepted objective may be persisted as a skeletal `PLANNED` Initiative
when the engineering objective is understood but executable decomposition is
not yet known.

Do not invent Phases or Steps merely to accept a new objective into Planning.

Objective acceptance and executable decomposition are separate decisions:

```text
accepted engineering objective
    ↓
PLANNED Initiative
    ↓
technical decomposition when sufficient authority exists
    ↓
validated Phase and Step hierarchy
    ↓
activate Initiative
    ↓
establish executable Phase and Step
```

A skeletal `PLANNED` Initiative is valid backlog state.

It must not cross into ACTIVE execution until Planning contains a valid
executable Phase and Step hierarchy.

The human does not need to select or disposition an existing Initiative or
unrelated organizational intake before defining and accepting a new objective.

Do not create a separate Planning Handoff artifact.

The temporary planning dictionary is transport, not durable Planning authority.

---

## Initiative Switching Route

This contract owns the human decision boundary that determines **which**
engineering objective happens next.

When the human has selected an existing or newly established Initiative and
moving to it requires coordinated Planning lifecycle and Git branch changes,
continue with:

```text
aurora/subsystems/planning/contracts/INITIATIVE_SWITCHING.md
```

That contract owns the deterministic mechanics for:

- checkpointing the Initiative being left;
- preserving paused resume state;
- closing and reopening Step repository-evidence segments;
- resolving and preparing the selected Initiative branch;
- sequencing Git preparation before Planning activation;
- preserving recoverable failure states;
- and proving final Planning/Git alignment.

Do not load `INITIATIVE_SWITCHING.md` merely to present candidates or obtain the
human objective decision.

The worker reaches that contract only after the target engineering objective is
known and a repository/Planning transition is actually required.

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

## Sufficient Authority in the Gap

While the worker is in the Between-Initiative Gap, this contract is sufficient
authority for:

- identifying unfinished PAUSED and PLANNED Initiative candidates;
- preserving existing Planning order;
- prohibiting autonomous prioritization or Initiative selection;
- preserving the human objective-selection boundary;
- preserving the permanent human option to define an entirely new engineering
  objective regardless of persisted candidates;
- allowing an accepted new objective to enter Planning as a skeletal `PLANNED`
  Initiative without fabricated executable decomposition;
- and determining which transition route becomes applicable after the human
  decision.

Do not load:

```text
aurora/subsystems/planning/contracts/HANSEL.md
```

merely to confirm the authority already established by this contract.

Load additional Planning authority only when the human decision creates a
specific need identified by this contract, such as:

- reconciling a selected existing Initiative;
- generating a new Planning dictionary;
- decomposing an accepted skeletal Initiative into executable work;
- applying Planning lifecycle operations;
- or establishing the executable Initiative → Phase → Step hierarchy.

Do not load Engineering Discovery, Delta Notes, or other organizational intake
authority merely to satisfy actor-local Gap transition.

Stop repository navigation at the human boundary once the actor-local Planning
decision surface has been assembled.

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
3. the permanent option to define an entirely new engineering objective remains
   available regardless of existing candidates;
4. the worker does not prioritize Planning candidates;
5. the human can accept a new objective into Planning without selecting an
   existing Initiative or dispositioning unrelated organizational intake;
6. an accepted objective may remain a skeletal `PLANNED` Initiative until
   executable decomposition is genuinely known;
7. the human selects or defines the engineering objective;
8. existing work is reconciled only as deeply as necessary;
9. new work uses canonical Planning generation authority;
10. Planning establishes exactly one executable Initiative → Phase → Step path
    before implementation begins;
11. actor-local transition does not require organization-wide reconciliation or
    serialize independent organizational workflows;
12. Git state is aligned with the selected Initiative;
13. the resulting Step can re-enter Hansel for task-specific repository work;
14. no hidden conversation history is required.

# ======================================================================
# END: PLANNING_INITIATIVE_TRANSITION
# ======================================================================

# ======================================================================
# FILE: aurora/subsystems/planning/contracts/INITIATIVE_SWITCHING.md
# START: PLANNING_INITIATIVE_SWITCHING
# ======================================================================

# Planning Initiative Switching

## Purpose
This contract defines the deterministic mechanics for moving one actor from the
current Planning Initiative and Git branch to a human-selected target Initiative
and its corresponding branch.
It applies only after the target engineering objective is known.

Objective discovery and human selection remain owned by:

```text
aurora/subsystems/planning/contracts/INITIATIVE_TRANSITION.md
```
This contract coordinates established authorities. It does not replace them.

---
## Required Outcome
A successful switch must leave these states aligned:

```text
human-selected Initiative
        =
ACTIVE Planning Initiative

expected Initiative branch
        =
checked-out Git branch

ACTIVE Planning Step baseline
        =
repository state after target-branch preparation
```
The final Planning path must contain exactly one actor-local executable:

```text
ACTIVE Initiative
    ↓
ACTIVE Phase
    ↓
ACTIVE Step
```
If those relationships cannot be proven, the switch is not complete.

---
## Human Selection Boundary
The target Initiative must already have been selected by the human.

The switching operation must not:

- score or rank Initiative candidates;
- choose the next Initiative;
- infer a target from Git activity;
- infer a target from Delta Notes, Engineering Findings, or other intake;
- or silently substitute another target when the requested Initiative cannot be
  activated.

When the target is unknown, return to `INITIATIVE_TRANSITION.md`.

---
## Authority Boundary
Planning owns:

- Initiative, Phase, and Step lifecycle;
- actor-local executable hierarchy;
- pause and resume semantics;
- Step repository-evidence attribution;
- Planning lifecycle validation;
- and establishment of the executable target Step.

Git owns repository and branch state.

A future host-capable orchestration boundary may sequence Git operations with
Planning lifecycle calls because Git execution is not a Planning database
responsibility.

That orchestration boundary may:

```text
inspect Planning state
invoke repository-owned Git operations
invoke Planning lifecycle operations
validate the combined result
return transition evidence
```
It must not:

```text
directly rewrite Planning lifecycle state
duplicate Planning lifecycle rules
choose the human objective
become a second Planning authority
hide Git failures behind Planning mutation
```
Planning lifecycle services remain authoritative for Planning mutation.

---
## Branch Identity
The normal Initiative branch convention is:

```text
feature/<initiative_slug>
```
A resumed Initiative reuses its existing branch.

A new Initiative receives its branch from current `main` using that convention.

The switching operation must stop for explicit reconciliation rather than:

- rename an existing Initiative branch automatically;
- invent a second branch for the same Initiative;
- choose between multiple plausible branches;
- rewrite branch history;
- or silently change the branch naming convention.

One deterministic target branch must be known before lifecycle transition.

---
## Transition Preflight
Before mutating Planning or Git state, establish:

```text
current Planning Initiative, if any
current executable Phase and Step, if any
human-selected target Initiative
current Git branch
expected target branch
working-tree state
repository checkpoint state
target Initiative lifecycle state
```
Reject the transition before mutation when required state is ambiguous or unsafe.

Examples include:

- multiple actor-local ACTIVE Initiatives;
- Planning and the current branch cannot be reconciled safely;
- ambiguous target branch identity;
- unresolved Git conflicts;
- deliberate repository changes that cannot be checkpointed;
- a target Initiative that lacks executable hierarchy when activation requires
  one;
- or repository execution evidence that cannot be attributed safely.

Do not repair ambiguous state implicitly as part of switching.

---
## Leaving an ACTIVE Initiative
Before deliberately switching away from current work:

```text
reach a logical validated stopping point
    ↓
inspect repository state
    ↓
commit deliberate repository changes
    ↓
push the current Initiative branch
    ↓
close the current Step repository-evidence segment
    ↓
pause the current Initiative
    ↓
Between-Initiative Gap
```
Repository checkpoint failure stops the switch before Planning pause.

Do not deliberately abandon uncommitted changes.

Do not use automatic stashing as a normal transition mechanism.

A paused Initiative preserves its feature branch.

Do not merge a paused Initiative merely because work stopped temporarily.

---
## Repository-Evidence Boundary
Repository execution evidence must follow executable Planning authority.

A paused Initiative may preserve internal resume state:

```text
Initiative — PAUSED
    Phase — ACTIVE
        Step — ACTIVE
```
Those ACTIVE child states mean **saved resume position**. They do not mean the
Step remains executable while the Initiative is paused.

An open Step repository baseline has a different meaning:

```text
open Step baseline
    = repository changes currently attributable to executable work
```
Therefore, before an ACTIVE Initiative is paused, the current Step's open
repository baseline must be finalized.

The pause preserves the child statuses but closes the repository-evidence
execution segment.

A paused Initiative must not carry an open baseline across unrelated Initiative
work. Otherwise changes made under another Initiative can be falsely attributed
to the paused Step when it resumes.

---
## Planning Pause Boundary
The future switching implementation must invoke Planning-owned lifecycle
authority for pause behavior.

The Planning-side transition used for deterministic switching must ensure:

1. the expected Initiative is ACTIVE;
2. the expected executable Step and baseline are identified when present;
3. the repository-evidence segment is finalized safely;
4. the Initiative becomes PAUSED;
5. ACTIVE child Phase and Step state remains as the resume position;
6. no actor-local executable Initiative remains after the pause; and
7. failure cannot leave a partially applied Planning transition.

Git must remain outside Planning's database lifecycle implementation.

---
## Between-Initiative Gap During Switching
After the current Initiative is safely paused and before the target Initiative is
activated, the actor is legitimately in the Between-Initiative Gap:

```text
no ACTIVE Initiative
    +
no executable Planning Step
```
This is a recoverable authoritative state, not an error to hide.

Git preparation occurs while Planning remains in this Gap.

Do not activate the target early merely to avoid the temporary Gap.

---
## Preparing a New Initiative Branch
For a target Initiative that does not yet have a branch:

```text
validated current main
    ↓
create feature/<initiative_slug>
    ↓
validate target branch state
```
The new branch must originate from current `main`.

Planning activation occurs only after branch preparation succeeds.

---
## Preparing a Resumed Initiative Branch
For a PAUSED target Initiative:

```text
existing Initiative branch
    ↓
compare with current main
    ↓
merge current main when needed
    ↓
resolve conflicts deliberately
    ↓
validate target branch state
```
Use merge rather than rebase unless an observed engineering requirement justifies
a different repository policy.

Do not normalize away the Initiative's preserved Planning resume position.

---
## Completing an Initiative Before Switching
A COMPLETED Initiative creates an integration boundary rather than a paused
resume boundary.

The normal integration sequence is:

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
Only after successful integration should a new Initiative branch be created from
that updated `main`.

Use merge rather than rebase unless repository evidence justifies otherwise.

---
## Prohibited Automatic Git Behavior
The switching operation must not automatically:

- stash working-tree changes;
- force checkout;
- force reset;
- discard local changes;
- resolve merge conflicts;
- rebase Initiative history;
- merge a PAUSED Initiative into `main`;
- or activate Planning work before target Git preparation succeeds.

A Git conflict or failed validation stops the transition for deliberate human
resolution.

---
## Activating or Resuming the Target Initiative
Only after the selected target branch is checked out and validated may Planning
make the target Initiative executable.

Use Planning lifecycle authority to establish:

```text
ACTIVE target Initiative
    ↓
ACTIVE Phase
    ↓
ACTIVE Step
```
For a resumed Initiative, existing ACTIVE child state is the preferred resume
position when valid.

For a newly activated Initiative, Planning may select the first valid unfinished
Phase and Step according to normal lifecycle rules.

The Git orchestration layer must not independently choose a Phase or Step.

---
## Fresh Repository Baseline
The target Step begins a new repository-evidence execution segment only after:

```text
target Git branch prepared
    +
target branch validated
    +
target Planning hierarchy established as executable
```
The resulting baseline must represent the repository state from which the target
Step actually resumes or begins.

A stale baseline from an earlier execution segment must not be silently reused.

If stale or ambiguous baseline state exists, activation stops for explicit
evidence reconciliation.

---
## Failure Semantics
The overall switch spans authorities that cannot be one database transaction.
Failure handling must therefore preserve the safest truthful state.

Before current Initiative pause:

```text
failure
    → current Initiative remains authoritative
```
Examples include failed checkpoint, failed push, ambiguous target branch, or
failed Planning precondition.

After current Initiative pause but before target activation:

```text
failure
    → remain in Between-Initiative Gap
    → do not reactivate work implicitly
```
Examples include target checkout failure, merge conflict, target validation
failure, stale target evidence, or failed Planning activation.

Report the exact recovery condition.

Do not guess which Initiative should become ACTIVE to hide a partial transition.

A checked-out branch with no ACTIVE Planning Initiative is preferable to falsely
claiming that work is executable.

---
## Successful Transition Evidence
A successful operation should return enough evidence to identify:

```text
human-selected target Initiative
ACTIVE Initiative
ACTIVE Phase
ACTIVE Step
checked-out Initiative branch
current-work checkpoint outcome
target-branch preparation outcome
Planning transition outcome
```
The returned target Initiative, active Planning hierarchy, and checked-out branch
must describe the same engineering objective.

---
## Future Implementation Requirements
A future switching implementation must prove that:

1. the human selected the target Initiative;
2. Planning and Git preflight completed before mutation;
3. deliberate current work was committed and pushed before leaving;
4. the outgoing Step baseline closed before Initiative pause;
5. paused child state remained available as the resume position;
6. one deterministic target branch was resolved;
7. new branches originate from current `main`;
8. resumed branches preserve history and merge current `main` when needed;
9. no automatic stash, force-reset, rebase, or implicit conflict resolution
   occurred;
10. target Git preparation succeeded before target Planning activation;
11. preserved Planning resume state was used when valid;
12. the target Step received a fresh repository baseline;
13. stale or ambiguous evidence blocked activation;
14. failure before pause left current work authoritative;
15. failure after pause left the actor safely in the Gap;
16. Planning lifecycle mutation remained owned by Planning;
17. Git execution remained outside Planning database lifecycle authority; and
18. final Git and Planning state matched the human-selected objective with exactly
    one executable Initiative → Phase → Step path.

This contract defines the switching protocol only. It does not implement it.

---
## Validation
The contract is sufficient when a clean-context worker can determine:

- when Initiative switching applies;
- who owns human target selection;
- how branch identity and current-work checkpointing work;
- where repository evidence closes and reopens;
- how PAUSED resume state differs from executable evidence;
- how new, resumed, and completed Initiative branches differ;
- which Git behaviors are forbidden;
- when target Planning activation may occur;
- what state is authoritative after partial failure; and
- what evidence proves a successful switch.

# ======================================================================
# END: PLANNING_INITIATIVE_SWITCHING
# ======================================================================

# ======================================================================
# FILE: aurora/subsystems/engineering_discovery/contracts/CAPTURE_POLICY.md
# START: ENGINEERING_DISCOVERY_CAPTURE_POLICY
# ======================================================================

# Engineering Finding Capture Policy

**Knowledge State: VERIFIED**

**Subsystem:** engineering_discovery

---

## Purpose

Prevent Engineering Discovery from becoming a speculative defect-generation
system.

Engineering Findings are produced as a byproduct of required engineering work.

Workers do not search for findings.

Workers capture a finding only when a concrete engineering problem is
encountered while following the authoritative path necessary to perform the
current required engineering work.

---

## Governing Rule

Use this question:

> Did required current work make this concrete problem observable?

If the answer is no, do not submit an Engineering Finding.

A worker must not create a finding merely because:

- a different design might be cleaner;
- a common best practice recommends another pattern;
- a hypothetical future consumer could have difficulty;
- unrelated repository inspection reveals something questionable;
- a broad refactor could make the system more elegant;
- the worker can imagine a possible failure;
- an implementation is unfamiliar or unconventional;
- another subsystem could theoretically be generalized.

Engineering Discovery records encountered engineering failures and limitations,
not generalized improvement ideas.

---

## Required Qualification Gate

Before calling `submit_finding(...)`, all of the following must be true.

### 1. Required-work connection

The condition was encountered while following repository authority necessary for
the current required engineering work. That work may be an ACTIVE Planning Step,
a Between-Initiative workflow, or another authoritative engineering path.

The worker did not widen repository inspection merely to search for defects.

### 2. Concrete observed condition

The worker can state what actually exists, failed, conflicted, blocked,
duplicated, or could not be validated.

The statement must describe an observed engineering condition rather than a
prediction or preference.

### 3. Concrete verification basis

The finding contains enough information for another worker to verify the
condition without hidden conversation history.

This requirement may be satisfied by:

- evidence;
- deterministic steps to reproduce;
- or both.

When reproduction steps themselves demonstrate the condition, duplicate
narrative evidence is not required.

### 4. Engineering significance

The condition matters beyond ordinary successful Step execution evidence.

Normal file changes, implementation choices, command output proving success, and
routine validation results are not findings by themselves.

### 5. Truthful situational provenance

Live submission asks Planning for lifecycle-authoritative current Step provenance
when one exists. Absence of an executable Step does not invalidate an otherwise
qualified finding.

The caller does not choose arbitrary Planning identifiers. Engineering Discovery
must preserve only provenance it can establish truthfully.

---

## Capture Immediately When Qualified

A worker should not defer a genuinely qualified finding merely because it does
not block current work.

Once qualification is established:

```text
qualified condition
    ↓
BLOCKING or NON_BLOCKING
    ↓
submit through Engineering Discovery
```

Blocking classification answers whether the current authoritative work can proceed
correctly and be validated without resolving the finding.

It does not answer whether the finding is severe, interesting, or worth fixing
immediately.

---

## Do Not Perform Defect Hunting

Engineering Discovery must not cause workers to inspect unrelated code,
subsystems, documentation, tests, architecture, or infrastructure merely to
populate the finding backlog.

Bad workflow:

```text
current Step
    ↓
search repository for other problems
    ↓
generate findings
```

Correct workflow:

```text
current Step
    ↓
follow only required engineering path
    ↓
problem encountered naturally
    ↓
qualify
    ↓
capture
    ↓
continue current work
```

The existence of Engineering Discovery is not authority to broaden task scope.

---

## Examples

### Capture: Broken required breadcrumb

The current Step requires a documented Hansel route.

The routed file does not exist.

The worker reached the missing file by following the required current-work
breadcrumb.

Result:

```text
CAPTURE
```

The problem was encountered through required work and is directly reproducible.

### Capture: General capability hidden under narrow ownership

The current Step needs authoritative executable Planning work.

The required resolver exists, but only under a time-tracking service and raises
a time-tracking-specific exception even though current-work resolution is used
outside timing.

Result:

```text
CAPTURE
```

The architectural limitation became concrete because current work required the
capability.

### Do not capture: Preferred naming

While editing a required service, the worker thinks another nearby class name is
awkward.

Nothing fails, blocks, conflicts, duplicates authority, or prevents validation.

Result:

```text
DO NOT CAPTURE
```

This is a preference.

### Do not capture: Unrelated old code

While implementing the current Step, the worker notices an unrelated subsystem
and decides to inspect it for technical debt.

Result:

```text
DO NOT INSPECT FOR FINDINGS
```

The inspection is outside the required path.

### Do not capture: Hypothetical scaling problem

A current implementation works correctly and satisfies its authority.

The worker predicts it may become inefficient if usage increases dramatically,
but no current requirement or observed execution exposes that problem.

Result:

```text
DO NOT CAPTURE
```

This is a prediction.

### Capture: Repeated manual reconstruction

Required current work repeatedly forces the worker to manually reconstruct
structured information that Aurora intends to preserve as durable state.

The repeated reconstruction is directly observed during current work.

Result:

```text
CAPTURE
```

This is an encountered Needed Solution, not a speculative automation proposal.

---

## Worker Submission Checklist

Immediately before submission, verify:

```text
[ ] I encountered this while performing required current work.
[ ] I did not search outside the required path to find it.
[ ] I can state a concrete observed condition.
[ ] Evidence and/or reproduction steps allow independent verification.
[ ] This is more than normal successful Step evidence.
[ ] I can classify it BLOCKING or NON_BLOCKING using the lifecycle rule.
```

If any required item is false, do not submit the finding.

---

## Limits of Mechanical Validation

The bounded submission service can enforce structural invariants such as:

- authenticated user;
- truthful Planning provenance when an executable Step exists, without requiring
  caller-supplied Planning identifiers;
- supported category;
- supported blocking classification;
- non-empty observed condition;
- evidence, reproduction steps, or both.

It cannot reliably determine from arbitrary prose whether a worker performed
unrelated defect hunting or submitted a generalized best-practice opinion.

Therefore speculative-finding prevention is also a repository-owned worker
behavior contract.

A structurally valid submission that violates this policy is still invalid
Engineering Discovery behavior.

---

## Clean-Context Acceptance Test

A clean-context worker given the canonical Hansel trail and normal required
engineering work should behave as follows:

1. perform only the work necessary for the authoritative current work;
2. capture a concrete engineering problem encountered on that path;
3. preserve sufficient evidence or reproduction steps;
4. classify it using the blocking decision boundary;
5. continue the current work when the finding is NON_BLOCKING;
6. not inspect unrelated repository areas to manufacture additional findings;
7. not submit hypothetical improvements or generalized best practices.

If Engineering Discovery causes broader defect hunting, this policy has failed.

# ======================================================================
# END: ENGINEERING_DISCOVERY_CAPTURE_POLICY
# ======================================================================

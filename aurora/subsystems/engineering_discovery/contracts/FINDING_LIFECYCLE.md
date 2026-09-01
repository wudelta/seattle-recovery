# ======================================================================
# FILE: aurora/subsystems/engineering_discovery/contracts/FINDING_LIFECYCLE.md
# START: ENGINEERING_DISCOVERY_FINDING_LIFECYCLE
# ======================================================================

# Engineering Finding Provenance and Lifecycle

**Knowledge State: VERIFIED**

**Subsystem:** engineering_discovery

---

## Purpose

Define the minimum provenance, classification, and lifecycle semantics required
for an Engineering Finding to remain understandable and actionable after the
conversation or worker execution that discovered it is gone.

This contract does not define database fields, persistence APIs, Planning
mutation, or closeout disposition values.

---

## Governing Qualification Authority

Whether an observed condition qualifies as an Engineering Finding, and which
finding category applies, is governed by:

```text
aurora/subsystems/engineering_discovery/contracts/HANSEL.md
```

Do not persist speculative observations merely to give them lifecycle state.

A condition enters this lifecycle only after it satisfies the Engineering
Finding qualification rule.

---

## Provenance Invariant

Every Engineering Finding must be understandable from durable repository-owned
evidence without requiring hidden conversation history.

At minimum, provenance must establish:

1. the Planning work during which the finding was encountered;
2. the finding category assigned under the Engineering Discovery contract;
3. the concrete condition that was observed;
4. the repository or execution evidence supporting the observation;
5. when the finding was discovered;
6. the current blocking classification;
7. the current resolution state.

Persistence implementations may choose concrete field names and storage shape
later, but they must preserve these semantics.

---

## Originating Planning Work

Every finding must identify the authoritative Planning path being executed when
the condition was encountered.

The durable origin is:

```text
Project → Initiative → Phase → Step
```

The originating Step is mandatory because Engineering Findings are qualified by
being encountered through required current work.

Initiative and Phase context must remain derivable from durable Planning state
or be preserved directly if later architecture requires it.

A finding must not be detached from its originating work merely because it is
later resolved, deferred, or incorporated into different Planning work.

---

## Evidence Provenance

A finding must preserve enough concrete evidence for a later worker to
understand why the finding qualified.

Evidence may include, as appropriate:

- a repository path or Hansel breadcrumb that failed;
- an authoritative contract involved in the failure;
- a command and its relevant result;
- a deterministic validation result;
- an observed lifecycle or state conflict;
- an application boundary that the required path would violate;
- repeated reconstructive work encountered during implementation;
- the navigation path that exposed unnecessary or non-contributing hops.

Evidence must describe what was actually observed.

Do not replace evidence with a worker's generalized opinion, recommendation, or
prediction.

Do not require the original chat transcript to reconstruct the finding.

---

## Blocking Classification

Every qualified finding must be classified as exactly one of:

```text
BLOCKING
NON_BLOCKING
```

Blocking classification answers only this question:

> Can the current authoritative Step be completed correctly and validated
> without resolving this finding?

### BLOCKING

Classify a finding as `BLOCKING` when the current Step cannot be completed
correctly and validated without resolving the finding first.

A finding is also blocking when continuing would require:

- knowingly violating an authoritative boundary;
- relying on an unsupported assumption;
- accepting invalid persisted state;
- bypassing required validation;
- pretending a broken required authority is usable.

Blocking does not mean severe, important, or urgent in the abstract.

It means the finding prevents correct completion of the current Step.

### NON_BLOCKING

Classify a finding as `NON_BLOCKING` when the current Step can still be
completed correctly and deterministically validated without resolving the
finding.

A non-blocking finding may still represent real engineering work requiring
later disposition.

Non-blocking does not mean trivial or optional.

It means current work may continue without compromising correctness.

---

## Classification Changes

Blocking classification may change only when new execution evidence changes
whether the current work can proceed correctly.

A later persistence design must preserve enough history to determine that a
classification changed and why.

Reclassification must not erase the original discovery context.

This contract does not prescribe the storage mechanism for classification
history.

---

## Resolution State

Resolution state is separate from blocking classification and separate from
future closeout disposition.

Every finding has exactly one current resolution state:

```text
UNRESOLVED
RESOLVED
```

### UNRESOLVED

A finding is `UNRESOLVED` while the concrete engineering condition it describes
still exists or has not yet been deterministically proven corrected.

Deferred work remains unresolved.

Accepted risk, invalidation, cancellation, or other future reconciliation
decisions must not be silently represented as technical resolution.

### RESOLVED

A finding becomes `RESOLVED` only when:

1. the concrete condition described by the finding has been corrected; and
2. deterministic evidence proves the correction.

A statement that the problem was addressed is insufficient without validation
evidence appropriate to the finding.

Resolution must preserve the original provenance rather than replacing it.

---

## Finding Lifecycle

The semantic lifecycle is:

```text
observed condition
    ↓
qualification under Engineering Discovery
    ↓
qualified Engineering Finding
    ↓
BLOCKING or NON_BLOCKING classification
    ↓
UNRESOLVED
    ↓
resolution work or later reconciliation
    ↓
RESOLVED, or a later closeout disposition owned by another authority
```

`observed condition` is not itself a persisted Engineering Finding.

The lifecycle begins only after qualification.

This contract does not prescribe how blocking remediation is inserted into
Planning or how non-blocking findings are persisted for later cleanup. Those
mechanisms belong to later authoritative Steps.

---

## Blocking Finding Example

During an ACTIVE Step, Hansel routes to a required lifecycle command that does
not exist.

The worker cannot complete the Step without bypassing the authoritative
workflow.

The condition qualifies as a Broken Hansel Trail and is classified:

```text
BLOCKING
UNRESOLVED
```

The finding preserves:

- the originating Project → Initiative → Phase → Step;
- the missing authority;
- the breadcrumb or contract that required it;
- the observed failure.

After the required authority is repaired and deterministic validation proves
the route works, resolution state becomes:

```text
RESOLVED
```

The original discovery provenance remains intact.

---

## Non-Blocking Finding Example

During required implementation, the worker follows the correct Hansel route but
must traverse two redundant authorities that provide no information needed for
implementation or validation.

The worker still reaches sufficient authority and completes the current Step
correctly.

The condition qualifies as Inefficient Navigation and is classified:

```text
NON_BLOCKING
UNRESOLVED
```

The finding preserves the originating Step and the observed navigation path.

Current implementation continues unchanged.

Later cleanup may resolve or otherwise dispose of the finding through a future
reconciliation authority.

---

## Reclassification Example

A worker initially classifies a missing optional validation helper as
`NON_BLOCKING` because an existing deterministic validation path remains
available.

Further required execution establishes that the remaining path cannot validate
the behavior required by the Step.

The finding may be reclassified to:

```text
BLOCKING
```

The later evidence justifying the change must be preserved.

The original classification must not disappear from durable history.

---

## Closeout Disposition Boundary

Resolution state answers whether the underlying engineering condition has been
corrected.

Closeout disposition answers what Aurora deliberately decides to do with a
finding at reconciliation.

They are not the same concept.

The specific closeout dispositions and the rule that assigns them are deferred
to the later Planning Step that owns postmortem finding reconciliation.

Do not invent disposition values in persistence or workflow code before that
authority exists.

---

## Persistence Boundary

This contract defines required semantics, not a database schema.

A later persistence implementation must be capable of representing the
provenance, blocking classification, resolution state, and lifecycle invariants
defined here.

This contract does not authorize creation of:

- Django models;
- migrations;
- repository files used as persistence;
- worker submission APIs;
- management commands;
- Planning lifecycle mutations.

Follow current Planning state before creating those surfaces.

---

## Deterministic Acceptance Conditions

This contract is sufficient only if a clean-context worker can determine, from
repository-owned authority:

1. which current Planning Step originated a finding;
2. what concrete evidence caused the observation to qualify;
3. which Engineering Finding category applies;
4. whether the finding is BLOCKING or NON_BLOCKING;
5. whether the finding is UNRESOLVED or RESOLVED;
6. what deterministic evidence is required for technical resolution;
7. that original provenance survives resolution or reclassification;
8. that closeout disposition remains a separate, later-owned concern.

No conversation transcript may be required to answer those questions.

---

# ======================================================================
# END: ENGINEERING_DISCOVERY_FINDING_LIFECYCLE
# ======================================================================

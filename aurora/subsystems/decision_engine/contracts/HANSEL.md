# ======================================================================

# FILE: aurora/subsystems/decision_engine/contracts/HANSEL.md

# START: DECISION_ENGINE_HANSEL_CONTRACT

# ======================================================================

# Decision Engine Hansel Catalogue

**Knowledge State: VERIFIED**

**Subsystem:** decision_engine

---

## Purpose

The Decision Engine owns organization-wide orchestration where evidence,
observations, proposed changes, actors, or domain authorities must be reconciled
into shared organizational decisions.

It coordinates durable organizational intake, human authorization, approved
change, cross-actor distribution, and transition into the subsystem that owns
execution.

The Decision Engine does not replace the domain authorities that produce
evidence or execute approved work.

This catalogue routes workers to the smallest repository authority needed for
Decision Engine work.

---

## Ownership Boundary

The Decision Engine owns:

* organization-wide candidate consideration;
* reconciliation of durable organizational evidence from multiple authorities;
* correlation and consolidation of related candidates;
* determination of whether a candidate is already represented by existing
  organizational work;
* AI-assisted recommendations about candidate disposition;
* the human authorization boundary for consequential organizational change;
* durable approved-change state;
* distribution and assignment of approved organizational change;
* transition of approved change into the domain authority that owns execution;
* organization-wide coordination across independently operating actors;
* organization-wide reconciliation that must not be coupled to one actor's
  Planning lifecycle transition.

The Decision Engine does not own:

* Engineering Finding qualification, capture, provenance, or lifecycle;
* human-entered Delta Note capture or persistence;
* Planning's Project → Initiative → Phase → Step hierarchy;
* Planning lifecycle transitions or executable-work authority;
* Step implementation evidence;
* repository navigation or Hansel breadcrumb integrity;
* AI process execution infrastructure;
* human-to-Wu chat presentation;
* domain-specific lifecycle rules owned by another subsystem.

---

## Organizational Change Boundary

Durable observations and evidence do not automatically become executable work.

The organization-wide flow is:

```text
durable source evidence
    ↓
Decision Engine candidate consideration
    ↓
AI-assisted reconciliation and recommendation
    ↓
human consequential decision
    ↓
approved organizational change
    ↓
distribution to owning authority
    ↓
domain-owned execution
```

A source record may remain authoritative in its originating subsystem while the
Decision Engine maintains organizational consideration or approved-change state
that refers to it.

Approval does not itself mutate Planning execution state.

When approved engineering change becomes Planning work, Planning owns creation
and lifecycle execution of the resulting hierarchy.

---

## Human Decision Boundary

AI workers may:

* gather candidate evidence;
* structure and summarize evidence;
* correlate likely duplicates or related conditions;
* identify possible existing organizational representation;
* recommend dispositions;
* explain rationale;
* prepare proposed distribution or transition.

Unless authority has been explicitly delegated elsewhere, a human authorizes
consequential organizational decisions including:

* accepting or rejecting candidate change;
* consolidating independent candidates into one organizational change;
* deciding whether existing work already represents a candidate;
* deferring an otherwise valid candidate;
* prioritizing approved change;
* choosing distribution or assignment;
* authorizing a new organizational objective;
* authorizing Emergency Change.

AI recommendation is not organizational authorization.

---

## Actor and Workflow Boundary

Aurora may have multiple simultaneously live organizational objectives and
multiple independently operating actors.

Actor-local execution may remain linear.

One actor may have one authoritative executable Planning path at a time without
requiring unrelated actors or organizational workflows to stop.

An actor-local lifecycle transition must not create an implicit global lock.

Independent work proceeds concurrently unless a real dependency, organizational
decision, or repository constraint requires coordination.

The Decision Engine owns coordination when an operation crosses actor-local
boundaries and requires shared organizational state or human organizational
decision.

---

## Source Authority Boundaries

### Engineering Discovery

Engineering Discovery owns Engineering Findings, including qualification,
classification, provenance, persistence, lifecycle, and evidence.

The Decision Engine may consume qualified Findings as organizational evidence.

It must not redefine or fabricate Engineering Findings.

### Delta Notes

Delta Notes owns deliberate human-entered observations, thoughts, reminders, and
ideas preserved with minimal friction.

AI workers must not originate Delta Notes.

The Decision Engine may consume Delta Notes as organizational evidence while
preserving their human provenance.

### Planning

Planning owns authorized executable engineering work represented as:

```text
Project → Initiative → Phase → Step
```

Planning remains the normal change-control authority for engineering execution.

A Planning Step is the normal executable change record.

The Decision Engine may authorize and coordinate transition of approved
organizational change into Planning, but Planning owns the resulting hierarchy
and lifecycle.

### Hansel

Hansel owns repository navigation, subsystem catalogues, breadcrumb integrity,
and deterministic discovery paths.

Decision Engine orchestration must use Hansel rather than becoming a competing
repository-navigation authority.

---

## AI Orchestration Boundaries

### Wu

Wu is Aurora's master AI orchestration actor.

Wu operates within repository-owned and Decision Engine organizational
boundaries.

Wu does not become the authority for organizational policy merely because it
coordinates AI work.

### Wu Chat

Wu Chat is the human interface to Wu.

UI placement in Wu Chat does not establish ownership of Decision Engine,
Planning, Engineering Discovery, or other domain behavior.

### MinionRunner

MinionRunner owns infrastructure used to execute bounded AI workers.

Execution infrastructure does not own the organizational decision that a minion
should be created, assigned, invoked, or trusted with a particular objective.

Those decisions remain with their governing organizational or domain authority.

---

## Provenance and Responsibility

Discovery provenance and remediation responsibility are separate dimensions.

The actor or subsystem that discovers a condition does not automatically become
responsible for resolving it.

The Decision Engine must preserve source provenance while allowing a human to
authorize different execution ownership.

Likewise:

```text
requirement provenance
    ≠ implementation authority
    ≠ validation execution
    ≠ validation acceptance
```

Cross-subsystem orchestration must preserve those distinctions.

---

## Normal Change and Emergency Change

Planning is Aurora's normal engineering change-control authority.

The normal path is:

```text
human organizational authorization
    ↓
Planning hierarchy
    ↓
authoritative Step
    ↓
execution
    ↓
validation
    ↓
durable evidence
```

Emergency Change is a higher-approval bounded exception used only when the
normal contract cannot safely represent or permit required recovery.

Emergency Change requires:

* explicit higher-authority approval;
* the minimum necessary exception;
* deterministic validation and evidence;
* mandatory retrospective reconciliation into normal Planning authority.

Emergency Change must not become an informal bypass around Planning.

---

## Knowledge Catalogue

### Determine whether work belongs to the Decision Engine

Use this contract.

Decision Engine ownership applies when required behavior crosses actor-local or
domain-local boundaries and requires shared organizational consideration,
authorization, distribution, or reconciliation.

If the operation remains entirely within one established subsystem's lifecycle
or authority, stay in that subsystem.

### Read the raw organizational inbox

Use:

```text
aurora/subsystems/decision_engine/services/inbox.py
```

For the read-only HTTP adapter, use:

```text
aurora/subsystems/decision_engine/api/endpoint.py
```

### Understand DecisionEngineWork persistence

Go to:

```text
aurora/subsystems/decision_engine/contracts/DECISION_ENGINE_WORK.md
```

Use this authority when work concerns the durable organization-level work
record created after explicit reviewer commit, the transient-selection boundary,
intake-to-work cardinality, source-lifetime independence, or intentionally
deferred persistence behavior.

### Understand intake disposition and processed semantics

Go to:

```text
aurora/subsystems/decision_engine/contracts/INTAKE_DISPOSITION.md
```

Use this authority when work concerns:

- terminal and non-terminal Decision Engine intake outcomes;
- when `processed` is semantically true;
- resolving `DecisionEngineWork` requirements;
- duplicate or mixed-scope intake;
- source-lifecycle separation;
- or the boundary between intake disposition and Planning execution.

### Work with Decision Engine UI

Go to:

```text
aurora/subsystems/decision_engine/contracts/UI_MAP.md
```

### Work with executable engineering objectives

Go to:

```text
aurora/subsystems/planning/contracts/HANSEL.md
```

Use Planning authority for Project, Initiative, Phase, Step, executable-work,
lifecycle, or engineering change-record behavior.

### Work with Engineering Findings

Go to:

```text
aurora/subsystems/engineering_discovery/contracts/HANSEL.md
```

Use Engineering Discovery for finding qualification, capture, classification,
provenance, lifecycle, or engineering evidence.

### Work with human-entered Delta Notes

Go to:

```text
aurora/subsystems/delta_notes/contracts/HANSEL.md
```

Use Delta Notes for human-originated ad-hoc observations, reminders, thoughts,
or ideas.

### Work with repository navigation or breadcrumb integrity

Go to:

```text
aurora/subsystems/hansel/contracts/HANSEL.md
```

Use Hansel when the task concerns repository discovery, subsystem catalogues,
breadcrumb correctness, or worker navigation.

### Work with Wu's human interface

Go to:

```text
aurora/subsystems/wu_chat/contracts/HANSEL.md
```

Use Wu Chat only for behavior owned by the human-to-Wu interaction surface.

Do not infer Decision Engine ownership from UI placement.

---

## Current Implementation State

Implemented Decision Engine authorities:

Raw organizational inbox:
- `services/inbox.py`
- `api/endpoint.py`
- `contracts/UI_MAP.md`

Durable `DecisionEngineWork`:
- `models.py`
- `services/work.py`
- `contracts/DECISION_ENGINE_WORK.md`

The inbox preserves source identity and provenance.

`DecisionEngineWork` begins at the explicit durable-work commit boundary.

Later workflow remains deferred to its authoritative Planning Steps.

---

## Unknown Territory

If this catalogue does not identify sufficient authority for the task:

1. do not invent ownership, behavior, architecture, lifecycle, or persistence;
2. determine whether the operation is actor-local, domain-local, or
   organization-wide;
3. inspect the narrowest likely repository authority;
4. follow cross-boundary dependencies only when required;
5. request additional repository evidence when necessary;
6. add a breadcrumb only when discovery reveals a durable route a future worker
   should not need to rediscover.

Do not treat absence of Decision Engine implementation as authority to place
organization-wide behavior in another subsystem.

---

## Sufficient Authority

Stop following breadcrumbs when all four are known:

1. who owns the behavior;
2. what must change;
3. what must remain unchanged;
4. how the change will be validated.

Do not load neighboring knowledge merely because it exists.

---

## Catalogue Reconciliation

After completing Decision Engine work, ask:

> Has this change made a Hansel breadcrumb or ownership route stale?

If no, no additional Hansel change is required.

If yes:

1. update affected breadcrumbs to current durable authorities;
2. remove obsolete routing;
3. add routing only for durable knowledge destinations;
4. verify changed breadcrumbs resolve.

Do not expand this catalogue with implementation knowledge learned during the
task.

The objective is accurate navigation to Decision Engine authority.

---

# ======================================================================

# END: DECISION_ENGINE_HANSEL_CONTRACT

# ======================================================================

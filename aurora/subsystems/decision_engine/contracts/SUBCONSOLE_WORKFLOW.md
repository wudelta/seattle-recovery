# ======================================================================
# FILE: aurora/subsystems/decision_engine/contracts/SUBCONSOLE_WORKFLOW.md
# START: DECISION_ENGINE_SUBCONSOLE_WORKFLOW
# ======================================================================

# Decision Engine Subconsole Workflow

## Purpose

Define the interaction contract for the guided Decision Engine subconsole.

This contract owns workflow progression, reversible navigation before
consequential boundaries, and preservation of in-progress workspace state.

It does not replace the persistence, intake-disposition, authorization, or
Planning authorities catalogued by Decision Engine Hansel.

---

## Guided Progression

The initial workflow is:

```text
Inbox
    ↓
Classification
    ↓
Aggregation
    ↓
Planning Proposal
    ↓
Import / Result
```

These are workflow stages, not a requirement that every stage permanently map
to exactly one browser view.

Implementation evidence may justify merging, splitting, or revising views when
that produces a clearer or safer interaction. Any revised view structure must
preserve the workflow semantics and authority boundaries defined here.

---

## Inbox

Inbox presents source evidence available to the current actor through existing
source-specific access rules.

Inbox navigation does not mutate source records, create DecisionEngineWork, or
change Planning state.

Source records remain authoritative for their own content and lifecycle.

---

## Classification

Classification allows the reviewer to develop and revise the organizational
interpretation of selected intake evidence before a consequential commit.

Classification state is provisional until an explicit repository-owned commit
boundary persists an authorized Decision Engine outcome.

Navigation into or out of Classification must not itself mark intake processed
or mutate source lifecycle.

---

## Aggregation

Aggregation allows compatible intake evidence to be grouped into candidate
organization-level work.

Aggregation is a review workspace, not durable organizational work by itself.

Transient grouping must remain reversible until an explicit commit boundary.

Multiple intake items may ultimately resolve to the same durable
DecisionEngineWork only through the persistence and disposition authorities
defined elsewhere.

---

## Planning Proposal

Planning Proposal represents a proposed engineering-work structure derived from
authorized organization-level work.

A proposal is not Planning state.

Viewing, editing, or navigating a Planning Proposal must not create or mutate
Project, Initiative, Phase, or Step records.

Planning remains the authority for executable engineering objectives and their
lifecycle.

---

## Import / Result

Import / Result is the workflow stage that presents the outcome of an explicit
handoff to the owning downstream authority.

Import actions must use the repository-owned Planning handoff and validation
boundaries defined by later Decision Engine authority.

Result presentation may report success, validation failure, rejection, or other
authorized outcomes without inventing lifecycle state.

---

## Reversible Navigation

Before an explicit consequential approval or commit boundary, the reviewer may
move backward and forward through the guided workflow.

Navigation must not be treated as authorization.

Navigation must not silently:

- create DecisionEngineWork;
- mark intake processed;
- mutate Delta Notes or Engineering Findings;
- create or modify Planning records;
- assign executable work;
- or approve a consequential organizational decision.

---

## State Preservation

Changing Decision Engine views should preserve the current in-progress review
workspace unless the actor explicitly discards, commits, or replaces that
state.

The browser may hold transient interaction state for navigation convenience.

Transient browser state is not repository authority and must not be mistaken
for durable organizational evidence.

When durable state becomes necessary, persistence must be owned by an explicit
Decision Engine contract and service rather than by incidental view changes.

---

## Consequential Boundaries

Consequential mutation must be explicit.

The workflow must visually and behaviorally distinguish reversible review from
operations that create or change durable organizational state.

Existing authorities remain controlling:

- `INTAKE_DISPOSITION.md` owns intake disposition and processed semantics.
- `DECISION_ENGINE_WORK.md` owns durable DecisionEngineWork persistence and the
  explicit reviewer commit boundary.
- `aurora/access/policy.py` owns Decision Engine reconciliation capability.
- Planning owns Project, Initiative, Phase, Step, and executable-work lifecycle.

A view transition is never a substitute for one of those authorities.

---

## Permission and Privacy Preservation

The subconsole must preserve source-specific privacy and ownership constraints.

Decision Engine reconciliation capability does not grant foreign Delta Note
access.

Access to a workflow stage does not imply permission to perform every operation
that may eventually exist within that stage.

Consequential operations must check their own repository-owned capability at
the mutation boundary.

---

## Implementation Freedom

The initial stage model is intentionally stable at the workflow level and
flexible at the presentation level.

Implementation may:

- merge adjacent views;
- split a complex stage into smaller views;
- revise labels;
- alter navigation controls;
- or change browser-state organization.

Such changes are acceptable when implementation evidence shows that the
original presentation is unwieldy or incomplete.

They must not change the durable authority boundaries, human approval
requirements, reversibility before commit, or state-preservation principles
defined by this contract.

---

## Validation Expectations

A conforming implementation must demonstrate that:

- the guided workflow remains understandable from Inbox through Import / Result;
- pre-commit navigation is reversible;
- moving between views does not unnecessarily reset in-progress review state;
- navigation alone causes no durable organizational mutation;
- explicit commit and approval boundaries remain distinguishable from view
  transitions;
- source privacy remains enforced;
- DecisionEngineWork begins only through its explicit persistence authority;
- and Planning records are created only through Planning-owned handoff
  authority.

# ======================================================================
# END: DECISION_ENGINE_SUBCONSOLE_WORKFLOW
# ======================================================================

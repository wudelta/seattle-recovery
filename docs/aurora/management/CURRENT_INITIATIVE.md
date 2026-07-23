# Current Initiative: Decision Engine Planning MVP

**Status:** Active
**Owner:** Delta
**Started:** 2026-07-21
**Target Completion:** 2026-07-28
**Priority:** Critical
**Scope Rule:** This is Aurora’s only active implementation initiative for this period.

---

# Objective

Create a database-backed planning system that allows Delta and Wu to define, discuss, organize, estimate, revise, and track engineering work using:

```text
Initiative
    Phase
        Step
```

The first milestone is planning only.

Aurora will not automatically execute repository changes from this system during this initiative.

---

# Desired Outcome

By the end of this initiative, Delta should be able to describe a project to Wu, answer clarifying questions, and receive a persisted implementation plan containing:

* one Initiative;
* ordered Phases;
* ordered Steps;
* preliminary effort estimates;
* visible assumptions;
* statuses;
* and enough detail to guide later implementation.

The plan must be viewable and editable inside Aurora Console.

---

# Core Architectural Decisions

## Decision Engine

The Decision Engine is the subsystem responsible for storing and managing structured project work.

It is not the user interface.

## Command Center

The Command Center is the integrated Aurora Console workspace through which Delta interacts with:

* Wu;
* project plans;
* implementation context;
* reviews;
* telemetry;
* and future execution tools.

## Integrated Workspace

Aurora must feel like one persistent workspace rather than a collection of pages.

Panels may change according to the current task, but meaningful state must be preserved when switching between them.

## Wu

Wu acts as the planning collaborator and engineering coordinator.

For this initiative, Wu may:

* discuss requirements;
* identify missing information;
* propose plans;
* create planning records;
* revise planning records;
* explain estimates;
* and recommend next work.

Wu may not automatically authorize or perform repository implementation from a planning action.

Wu consumes project state but is not the source of project state.

---

# Planning Model

## Initiative

Represents a meaningful outcome or body of work.

Required initial capabilities:

* title;
* description;
* owner;
* status;
* ordering or priority;
* created timestamp;
* modified timestamp.

An Initiative may exist in a planned state before all Phases and Steps are defined.

## Phase

Represents a coherent stage within an Initiative.

Required initial capabilities:

* parent Initiative;
* title;
* description;
* status;
* order;
* created timestamp;
* modified timestamp.

## Step

Represents the smallest planned unit that can later be assigned, implemented, validated, and completed.

Required initial capabilities:

* parent Phase;
* title;
* description;
* status;
* order;
* estimated effort;
* estimate confidence;
* validation description;
* created timestamp;
* modified timestamp.

---

# Initial Statuses

Use the smallest shared lifecycle that supports planning:

```text
planned
active
paused
completed
cancelled
```

More detailed execution statuses are deferred until the execution initiative.

---

# SMART Goals

## Goal 1: Persist the Planning Hierarchy

By **2026-07-28**, Aurora will persist Initiative, Phase, and Step records in PostgreSQL with enforced parent relationships and ordering.

Validation:

* create one Initiative;
* create at least two Phases;
* create at least three Steps;
* restart Aurora;
* confirm the hierarchy remains intact.

## Goal 2: Provide Planning CRUD

By **2026-07-28**, Aurora will support creating, viewing, editing, ordering, changing status, and safely cancelling Initiative, Phase, and Step records through an internal interface.

Direct database editing must not be required.

## Goal 3: Display the Hierarchy in Aurora Console

By **2026-07-28**, Aurora Console will display the hierarchy in an expandable planning panel.

The panel must show:

* Initiative;
* Phase;
* Step;
* status;
* order;
* and Step estimate.

Selection and expansion state should survive switching to another Console panel and returning.

## Goal 4: Allow Wu to Create Plans

By **2026-07-28**, Wu will be able to convert a project description and follow-up discussion into persisted Initiative, Phase, and Step records.

Wu must:

* ask relevant clarifying questions;
* identify assumptions;
* create ordered Phases;
* create concrete Steps;
* and provide preliminary estimates with visible confidence.

## Goal 5: Allow Wu to Revise Plans

By **2026-07-28**, Wu will be able to perform common persisted plan revisions through conversation.

At minimum:

* rename a record;
* add a Phase or Step;
* revise a description;
* reorder a Step;
* change status;
* and revise an estimate.

## Goal 6: Validate With an External Project

By **2026-07-29**, Aurora will use a project description supplied by Delta’s colleague to demonstrate:

* requirements discussion;
* missing-requirement discovery;
* Initiative creation;
* Phase and Step creation;
* preliminary estimates;
* persistence;
* and human review.

The resulting plan does not need to execute code.

---

# Implementation Phases

## Phase 1: Validate and Complete Models and Rules

Inspect the implemented Initiative, Phase, and Step models against this initiative’s requirements.

Confirm or complete:

* fields;
* relationships;
* ordering;
* statuses;
* ownership;
* estimation;
* estimate confidence;
* validation descriptions;
* cancellation behavior;
* and completion rules.

Preserve the existing implementation wherever it already satisfies the requirements.

## Phase 2: Add Planning Operations

Implement services or APIs for:

* listing the hierarchy;
* creating records;
* updating records;
* reordering records;
* changing status;
* and cancelling records.

Planning rules must not exist only in JavaScript or templates.

## Phase 3: Build the Planning Panel

Add a stateful planning surface to Aurora Console.

Prioritize:

* hierarchy clarity;
* fast panel switching;
* state preservation;
* and simple editing.

Visual polish is secondary.

## Phase 4: Integrate Wu

Allow Wu to use structured planning operations to:

* create plans;
* revise plans;
* explain decisions;
* and retrieve current planning state.

Wu must not merely describe changes in chat. The database must reflect them.

## Phase 5: Validate the Workflow

Create and revise an internal Aurora Initiative.

Then perform the external planning demonstration using the colleague’s project description.

Record missing capabilities as future work rather than expanding the current scope without review.

---

# Explicit Exclusions

Do not implement the following during this initiative:

* automatic code generation from Steps;
* automatic patch application;
* Step approval workflow;
* minion assignment;
* slash-command execution by Wu;
* execution scheduling;
* actual-time tracking;
* grading systems;
* advanced metrics;
* dependency graph visualization;
* Gantt charts;
* calendar integration;
* Blueprint removal;
* Delta Notes removal;
* Anamod replacement;
* or broad Aurora Console redesign.

These belong to later initiatives.

---

# Architectural Rules

* Planning records are the authoritative operational project state.
* Conversation is an interface, not a datastore.
* Wu consumes project state but is not the source of project state.
* Wu must persist any plan change it claims to make.
* Planning does not imply execution approval.
* All meaningful changes must remain visible and explainable.
* The human architect retains final authority.
* The implementation must follow The Delta Way.
* Steps must be small enough to understand and validate.
* New ideas outside this scope must be recorded for later rather than implemented immediately.
* Existing Blueprint, Delta Notes, Wu Chat, and Anamod functionality must not be removed until replacement workflows are validated.

---

# Acceptance Criteria

This initiative is complete when:

* Initiative, Phase, and Step models exist and are migrated.
* Existing planning models have been inspected against the initiative requirements.
* Relationships and ordering work correctly.
* Initiative ownership is recorded.
* Basic statuses, including cancellation, are supported.
* Steps support estimates, confidence, and validation descriptions.
* The hierarchy is visible in Aurora Console.
* Planning panel state survives normal panel switching.
* Internal CRUD operations work.
* Wu can create a persisted plan.
* Wu can revise a persisted plan.
* Wu identifies assumptions and missing requirements.
* No planning action automatically changes repository code.
* The colleague’s project description can be converted into a reviewable implementation plan.
* Delta confirms the workflow is useful enough to guide the next implementation initiative.

---

# Current Step

Inspect the implemented Initiative, Phase, and Step models together with the existing APIs, Aurora Console panel-loading architecture, Wu Chat integration, and project-state workflow.

Determine:

* which initiative requirements the current models already satisfy;
* which required fields or rules are missing;
* whether ordering and lifecycle behavior are enforced in application logic;
* how planning state should be projected for both Aurora Console and Wu;
* and where planning operations should live.

Pay particular attention to:

* the required `cancelled` status;
* Step effort estimates;
* estimate confidence;
* validation descriptions;
* ordering behavior;
* Initiative ownership;
* completion rules;
* and the separation between durable planning state and future execution state.

Do not redesign or replace the planning models merely because this initiative document predates their implementation.

No patch should be produced until the current implementation boundaries and requirement gaps are understood.

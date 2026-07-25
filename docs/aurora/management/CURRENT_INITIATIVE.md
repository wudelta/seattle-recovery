# Aurora Decision Engine Workflow (Manual Mode)

## Purpose

The Decision Engine is the operational heart of Aurora.

Its purpose is not simply to track tasks.

Its purpose is to preserve engineering context and guide a software project from conception to validated completion.

Aurora exists to allow the human architect to think about systems while Aurora manages engineering continuity.

The Decision Engine is the authoritative source of engineering intent.

---

# Current Status

## Phase 1 — Planning (In Progress)

Aurora now supports database-backed planning using the hierarchy:

```text
Project
    Initiative
        Phase
            Step
```

Projects represent products, applications, or engineering domains.

Each Project contains one or more Initiatives.

Each Initiative is decomposed into ordered Phases.

Each Phase is decomposed into ordered Steps.

Planning is now considered the authoritative source of engineering intent.

Execution automation has not yet been enabled.

---

# Current Implementation Status

Implemented:

* Project model
* Initiative model
* Phase model
* Step model
* database persistence
* Project CRUD
* Initiative CRUD
* Phase CRUD
* Step CRUD
* modular Planning workspace
* AJAX-based editing
* subsystem-oriented Planning architecture

Currently in progress:

* Project selector
* Initiative selector
* focused workspace navigation

Planned:

* drag-and-drop ordering
* dependency tracking
* repository relationships
* execution mode
* validation recording
* AI-assisted planning

---

# Core Philosophy

The human should spend as little time as possible asking:

* What was I doing?
* Where is that file?
* What comes next?
* Did we already decide this?
* Is this complete?

The Decision Engine should answer those questions automatically.

Every interaction with Aurora should reinforce continuity of thought.

---

# Engineering Lifecycle

Every Project progresses through the same lifecycle.

## 1. Capture

Ideas are captured with minimal friction.

Sources may include:

* Delta Notes
* conversations with Wu
* bugs
* feature requests
* architectural observations

Captured ideas are intentionally lightweight.

Nothing is organized yet.

---

## 2. Refine

Interesting ideas become Initiatives.

An Initiative defines:

* objective
* success criteria
* scope
* priority
* assumptions

An Initiative answers one question:

> What are we trying to accomplish?

---

## 3. Plan

Each Initiative is decomposed into ordered Phases.

Each Phase is decomposed into ordered Steps.

Every Step should be independently understandable and independently verifiable.

Each Step records:

* description
* estimated effort
* confidence
* assumptions
* validation requirements

Future revisions will associate Steps with:

* repository artifacts
* architectural discussions
* implementation history
* engineering decisions

The persisted plan becomes the authoritative engineering roadmap.

---

## 4. Execute

Execution focuses on exactly one active Step.

Execution Mode has not yet been implemented.

When implemented, the Decision Engine will automatically provide:

* current Project
* current Initiative
* current Phase
* current Step
* related repository artifacts
* previous architectural decisions
* validation requirements
* implementation notes

Execution should remain tightly focused.

No searching.

No rebuilding context.

Only the information required for the current engineering task should be surfaced.

---

## 5. Validate

A Step is not complete because code was written.

A Step is complete only after validation succeeds.

Validation evidence will eventually include:

* implementation notes
* validation notes
* reviewer
* completion timestamp
* automated validation results

Only then should the Decision Engine advance to the next Step.

---

## 6. Complete

Progress is derived from validated work.

When every Step has been validated:

* the Phase completes automatically.

When every Phase has been completed:

* the Initiative completes automatically.

When every Initiative has been completed:

* the Project completes automatically.

Manual progress percentages should never be required.

---

# Workspace Philosophy

Aurora should feel like one continuously evolving engineering environment.

Every major subsystem should integrate with the Decision Engine rather than existing independently.

Examples include:

* Delta Notes
* Wu
* Anamod
* Blueprint
* Telemetry
* Component Registry

Each subsystem contributes information to the active engineering context.

---

# Workspace Pattern

Every Aurora workspace follows the same structure.

## Navigator

Provides orientation.

Examples:

* Projects
* Initiatives
* Files
* Components

The Navigator answers:

> Where am I?

---

## Workbench

Provides focused work.

Only one primary activity occupies the Workbench.

Examples include:

* planning
* implementation
* repository exploration
* documentation
* code review

The Workbench answers:

> What am I doing?

---

## Context

Always visible.

Current context should include:

* active Project
* active Initiative
* active Phase
* active Step

Future context will also include:

* related repository artifacts
* active discussions
* assumptions
* validation status
* implementation history

The Context panel answers:

> Why am I doing this?

---

# Responsibilities

## Delta

Responsible for:

* vision
* architecture
* priorities
* engineering judgment
* final decisions

---

## Decision Engine

Responsible for:

* preserving engineering context
* organizing engineering work
* sequencing execution
* maintaining progress
* recording validation
* identifying the next action

The Decision Engine is the authoritative engineering memory.

---

## Wu

Responsible for:

* planning assistance
* implementation guidance
* repository reasoning
* architectural discussion
* generation of proposed execution plans

Wu assists the engineer.

Wu does not become the source of truth.

---

## Minions

Responsible for deterministic execution within clearly defined architectural boundaries.

Minions perform implementation work.

The Decision Engine coordinates that work.

---

# Architectural Direction

Aurora is transitioning toward a subsystem-oriented architecture.

Rather than organizing primarily by Django artifact type, each subsystem should eventually own its own implementation:

```text
planning/
    api/
    models.py
    templates/
    static/
    services/
```

This improves locality of reference, simplifies refactoring, and allows AI workers to reason about one subsystem at a time.

The Planning subsystem serves as the reference implementation for this architectural direction.

---

# Near-Term Roadmap

Current implementation priorities are:

1. Project selector
2. Initiative selector
3. Focused Planning workspace
4. Phase and Step ordering
5. Automatic lifecycle progression
6. Repository artifact relationships
7. Execution Mode
8. Validation recording
9. AI-generated implementation plans

---

# Success Criteria

Aurora succeeds when the user no longer manages engineering context manually.

Instead of asking:

> What should I do next?

Aurora immediately answers:

* Here is the active Project.
* Here is the active Initiative.
* Here is the active Phase.
* Here is the active Step.
* Here is why it matters.
* Here are the related repository artifacts.
* Here are the assumptions.
* Here is what must be validated.
* Here is the next engineering action.

At that point, the Decision Engine is no longer simply a planning tool.

It becomes the persistent operating system for the engineering process.

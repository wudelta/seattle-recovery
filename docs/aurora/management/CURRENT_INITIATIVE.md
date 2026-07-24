# Aurora Decision Engine Workflow (Manual Mode)

## Purpose

The Decision Engine is the operational heart of Aurora.

Its purpose is not simply to track tasks.

Its purpose is to preserve engineering context and guide a software project from conception to validated completion.

Aurora exists to allow the human architect to think about systems while Aurora manages execution.

---

# Current Status

## Phase 1 — Planning (Completed)

Aurora now supports database-backed planning using the hierarchy:

```text
Project
    Initiative
        Phase
            Step
```

The planning console provides full CRUD operations for:

* Initiatives
* Phases
* Steps

The interface allows planning work to be created, revised, organized, and persisted without leaving Aurora Console.

Planning is now considered the authoritative source of engineering intent.

Execution automation has not yet been enabled.

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

Every project progresses through the same lifecycle.

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

Future revisions will associate Steps with repository artifacts and engineering discussions.

The persisted plan becomes the authoritative source of engineering work.

**Current Aurora Status**

Implemented:

* database persistence
* Project → Initiative → Phase → Step hierarchy
* create/edit workflows
* planning workspace
* initiative navigator
* workbench context
* AJAX-based editing

Planned:

* delete operations
* ordering and reprioritization
* repository relationships
* dependency tracking
* AI-assisted planning

---

## 4. Execute

Exactly one Step should eventually become active.

Execution mode has not yet been implemented.

The Decision Engine will eventually provide:

* current context
* related files
* previous architectural decisions
* implementation history
* validation requirements
* implementation notes

Execution should remain tightly focused.

No searching.

No rebuilding context.

Only the information required for the current Step should be surfaced.

---

## 5. Validate

A Step is not complete because code was written.

A Step is complete only after validation succeeds.

Validation evidence will be recorded with the Step.

Future versions will support:

* validation notes
* reviewer
* completion timestamps
* automated validation workflows

Only then should the Decision Engine advance to the next Step.

---

## 6. Complete

Ultimately:

When every Step has been validated:

* the Phase should complete automatically.

When every Phase has been completed:

* the Initiative should complete automatically.

Project progress should always be derived from validated work rather than manual percentages.

---

# Workspace Principles

The Decision Engine is the center of Aurora.

Every major workspace should integrate with it.

Examples include:

* Delta Notes
* Wu
* Anamod
* Blueprint
* Telemetry

Each workspace contributes information to the active Initiative rather than existing in isolation.

The user should feel like they are working inside one continuously evolving engineering environment rather than switching between unrelated tools.

---

# Workspace Pattern

Every major Aurora workspace follows the same structure.

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

Only one primary activity should occupy the workbench at a time.

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

Examples:

* active Project
* active Initiative
* active Phase
* active Step

Eventually additional context should include:

* related files
* active discussions
* assumptions
* validation status

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
* organizing work
* maintaining progress
* sequencing execution
* recording validation
* identifying the next action

---

## Wu

Responsible for:

* planning assistance
* implementation guidance
* repository reasoning
* architectural discussion
* generation of proposed execution plans

Wu assists.

Wu does not become the source of truth.

The Decision Engine remains the authoritative engineering memory.

---

## Minions

Responsible for deterministic execution inside clearly defined boundaries.

Minions perform implementation work.

The Decision Engine coordinates that work.

---

# Near-Term Roadmap

The next implementation milestones are:

1. Delete operations
2. Reordering of Phases and Steps
3. Automatic lifecycle progression
4. Repository artifact relationships
5. Execution Mode
6. AI-generated implementation plans
7. Validation recording
8. Automatic advancement through engineering work

---

# Success Criteria

Aurora succeeds when the user no longer has to manage engineering context manually.

Instead of asking:

> What should I do next?

Aurora should always answer:

* Here is the current Project.
* Here is the current Initiative.
* Here is the current Phase.
* Here is the current Step.
* Here is why it matters.
* Here are the related repository artifacts.
* Here are the assumptions.
* Here is what must be validated.
* Here is what comes next.

At that point, the Decision Engine is no longer a planning tool.

It becomes the persistent operating system for the engineering process itself.

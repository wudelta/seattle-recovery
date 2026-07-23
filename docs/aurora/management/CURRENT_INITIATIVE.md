# Aurora Decision Engine Workflow (Manual Mode)

## Purpose

The Decision Engine is the operational heart of Aurora.

Its purpose is not simply to track tasks.

Its purpose is to preserve engineering context and guide a software project from conception to validated completion.

Aurora exists to allow the human architect to think about systems while Aurora manages execution.

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
* assumptions
* related repository artifacts
* validation requirements

The plan becomes the authoritative source of engineering work.

---

## 4. Execute

Exactly one Step is active.

Aurora provides:

* current context
* related files
* previous decisions
* implementation history
* validation requirements

Execution remains tightly focused.

No searching.

No rebuilding context.

---

## 5. Validate

A Step is not complete because code was written.

A Step is complete only after validation succeeds.

Validation evidence is recorded.

Only then does the Decision Engine advance to the next Step.

---

## 6. Complete

When every Step is validated:

* the Phase completes automatically.

When every Phase completes:

* the Initiative completes automatically.

Project progress is always derived from validated work.

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

---

# Workspace Pattern

Every major Aurora workspace follows a consistent structure.

## Navigator

Provides orientation.

Examples:

* Projects
* Initiatives
* Files
* Components

## Workbench

Provides focused work.

Only one primary activity should occupy the workbench at a time.

## Context

Always visible.

Examples:

* active Project
* active Initiative
* active Phase
* active Step

The user should never wonder where they are.

---

# Responsibilities

## Delta

Responsible for:

* vision
* architecture
* priorities
* final decisions

## Decision Engine

Responsible for:

* preserving context
* organizing work
* maintaining progress
* sequencing execution
* recording validation
* surfacing the next action

## Wu

Responsible for:

* planning assistance
* implementation guidance
* repository reasoning
* code generation
* architectural discussion

## Minions

Responsible for deterministic execution within clearly defined boundaries.

---

# Success Criteria

Aurora succeeds when the user no longer has to manage engineering context manually.

Instead of asking:

"What should I do next?"

Aurora should always be able to answer:

* Here is the current Initiative.
* Here is the current Phase.
* Here is the current Step.
* Here is why it matters.
* Here are the related artifacts.
* Here is what must be validated.
* Here is what comes next.

At that point, Aurora becomes more than a development environment.

It becomes the operating system for the engineering process itself.

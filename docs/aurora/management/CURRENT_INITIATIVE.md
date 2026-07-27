# Aurora Decision Engine Workflow

## Purpose

The Decision Engine is the operational heart of Aurora.

Its purpose is not simply to track tasks.

Its purpose is to preserve engineering context and guide a software project from conception to validated completion.

Aurora exists to allow the human architect to think about systems while Aurora manages engineering continuity.

The Decision Engine is the authoritative source of engineering intent.

---

# Current Status

## Phase 1 — Planning Workspace (Largely Complete)

Aurora now provides a database-backed Planning workspace built around the engineering hierarchy:

```text
Project
    Initiative
        Phase
            Step
```

Planning is now the authoritative source of engineering intent.

Projects represent complete engineering efforts.

Each Project contains one or more Initiatives.

Each Initiative contains one or more ordered Phases.

Each Phase contains one or more ordered Steps.

The Planning workspace now supports:

- database persistence
- complete Project CRUD
- complete Initiative CRUD
- complete Phase CRUD
- complete Step CRUD
- AJAX editing
- focused workspace navigation
- modular subsystem architecture

The next major milestone is Execution.

---

# Source of Truth

The Decision Engine database is Aurora's authoritative engineering memory.

Projects, Initiatives, Phases, and Steps define engineering intent.

All exported markdown, session summaries, project status documents, and AI context should ultimately be generated from this hierarchy.

Documentation becomes an output of the Decision Engine rather than its source.

---

# Engineering Hierarchy

```text
Project
    Initiative
        Phase
            Step
```

## Project

Projects represent complete engineering efforts.

Examples:

- Aurora
- HopeHub

A Project owns every engineering artifact beneath it.

---

## Initiative

An Initiative represents a major engineering objective.

Examples include:

- Decision Engine
- Component Registry
- Workspace Synchronization

An Initiative answers one question:

> What are we trying to accomplish?

---

## Phase

A Phase represents a logical milestone within an Initiative.

Examples:

- Planning
- Execution
- Validation

A Phase answers:

> What stage are we in?

---

## Step

A Step is the smallest independently executable engineering task.

Every Step should be:

- understandable
- independently executable
- independently verifiable

Each Step records information such as:

- description
- assumptions
- estimated effort
- confidence
- validation requirements

Future revisions will associate Steps with:

- repository artifacts
- implementation history
- engineering discussions
- architectural decisions

---

# Current Implementation Status

## Implemented

- Project model
- Initiative model
- Phase model
- Step model
- database persistence
- Project CRUD
- Initiative CRUD
- Phase CRUD
- Step CRUD
- Project selector
- focused Initiative navigation
- AJAX editing
- modular Planning workspace

## Current Focus

- subsystem-oriented repository architecture
- Execution workspace design
- engineering context preservation

## Planned

- drag-and-drop ordering
- dependency relationships
- repository artifact relationships
- Execution workspace
- validation recording
- AI-assisted implementation planning

---

# Engineering Lifecycle

Every Project progresses through the same lifecycle.

## 1. Capture

Ideas are captured with minimal friction.

Sources may include:

- Delta Notes
- conversations with Wu
- bugs
- feature requests
- architectural observations

Captured ideas are intentionally lightweight.

Nothing is organized yet.

---

## 2. Refine

Interesting ideas become Initiatives.

An Initiative defines:

- objective
- scope
- success criteria
- assumptions
- priority

An Initiative answers:

> What are we trying to accomplish?

---

## 3. Plan

Each Initiative is decomposed into ordered Phases.

Each Phase is decomposed into independently verifiable Steps.

Planning produces the authoritative engineering roadmap.

---

## 4. Execute

Execution focuses on exactly one active Step.

Execution Mode has not yet been implemented.

When completed, Aurora will automatically surface:

- active Project
- active Initiative
- active Phase
- active Step
- related repository artifacts
- implementation history
- architectural discussions
- validation requirements

Execution should eliminate unnecessary context switching.

---

## 5. Validate

A Step is not complete because code was written.

A Step is complete only after validation succeeds.

Validation evidence will eventually include:

- implementation notes
- validation notes
- reviewer
- completion timestamp
- automated validation results

Only then should Aurora advance to the next Step.

---

## 6. Complete

Progress is derived from validated work.

When every Step has been validated:

- the Phase completes automatically.

When every Phase has completed:

- the Initiative completes automatically.

When every Initiative has completed:

- the Project completes automatically.

Manual progress percentages should never be required.

---

# Workspace Architecture

Every Aurora workspace follows the same architectural pattern.

## Navigator

Provides orientation.

Examples:

- Projects
- Initiatives
- Files
- Components

Answers:

> Where am I?

---

## Workbench

Provides focused work.

Only one primary activity occupies the Workbench.

Examples:

- Planning
- Execution
- Documentation
- Repository exploration
- Code review

Answers:

> What am I doing?

---

## Context

Provides continuous engineering awareness.

Current context includes:

- active Project
- active Initiative
- active Phase
- active Step

Future context will also include:

- repository artifacts
- architectural discussions
- implementation history
- assumptions
- validation status

Answers:

> Why am I doing this?

---

# Responsibilities

## Delta

Responsible for:

- vision
- architecture
- priorities
- engineering judgment
- final decisions

---

## Decision Engine

Responsible for:

- preserving engineering context
- organizing engineering work
- sequencing execution
- maintaining progress
- recording validation
- identifying the next engineering action

The Decision Engine is Aurora's engineering memory.

---

## Wu

Responsible for:

- planning assistance
- implementation guidance
- repository reasoning
- architectural discussion
- proposed execution plans

Wu assists the engineer.

The Decision Engine remains the source of truth.

---

## Minions

Responsible for deterministic execution within clearly defined architectural boundaries.

Minions perform implementation work.

The Decision Engine coordinates that work.

---

# Architectural Direction

Aurora is transitioning from a repository organized primarily by Django artifact type toward one organized by engineering subsystem.

Instead of:

```text
models.py
views.py
templates/
static/
```

Aurora is moving toward:

```text
planning/
    api/
    models.py
    templates/
    static/
    services/
```

Each subsystem should own its implementation.

This architecture:

- improves locality of reference
- reduces file size
- simplifies refactoring
- reduces AI context requirements
- enables deterministic workers
- improves long-term maintainability

The Planning subsystem serves as the reference implementation for this direction.

---

# Near-Term Roadmap

1. Repository subsystem reorganization
2. Phase and Step ordering
3. Automatic lifecycle progression
4. Repository artifact relationships
5. Execution workspace
6. Validation workflow
7. AI-generated implementation plans
8. Context-aware engineering assistance
9. Autonomous engineering minions

---

# Success Criteria

Aurora succeeds when the engineer no longer manages engineering context manually.

Instead of asking:

> What should I do next?

Aurora immediately answers:

- Here is the active Project.
- Here is the active Initiative.
- Here is the active Phase.
- Here is the active Step.
- Here is why it matters.
- Here are the related repository artifacts.
- Here are the assumptions.
- Here is what must be validated.
- Here is the next engineering action.

At that point, the Decision Engine is no longer simply a planning tool.

It becomes the operating system for the engineering process.
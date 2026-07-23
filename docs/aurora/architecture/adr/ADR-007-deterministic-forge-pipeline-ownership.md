# ADR-007: Deterministic Forge Pipeline Ownership

**Status:** Accepted

**Date:** 2026-07-17

---

# Context

Aurora contains a deterministic Forge Engine responsible for generating application artifacts in response to slash commands such as:

- `/page`
- `/api`

These builders intentionally perform deterministic filesystem mutation without requiring AI assistance.

Over time, additional responsibilities accumulated inside the builders, including:

- repository registration;
- Neo4j synchronization;
- telemetry management;
- automatic unit test generation;
- repository cleanup.

This gradual expansion blurred architectural boundaries and produced several undesirable consequences:

- filesystem mutation became coupled to repository indexing;
- infrastructure concerns leaked into deterministic utilities;
- command handlers duplicated synchronization behavior;
- generated artifacts became aware of internal implementation details;
- automatic test generation produced maintenance overhead without providing durable architectural verification.

The introduction of the Workspace Synchronization pipeline provides a deterministic mechanism for separating these concerns.

This ADR formalizes those ownership boundaries.

---

# Decision

Aurora adopts a deterministic Forge architecture based upon **single ownership of responsibilities**.

The Forge Engine is responsible only for deterministic filesystem mutation.

Repository projection is performed exclusively by the Workspace Synchronization pipeline.

Telemetry is owned by a shared logging service.

Slash command handlers orchestrate these services but do not own their implementation.

Automatic unit test generation is removed from deterministic builders.

---

# Ownership Model

## 1. Skeleton Builders

Examples:

- `PageSkeletonBuilder`
- `ApiSkeletonBuilder`

Responsibilities:

- validate command parameters;
- create deterministic repository files;
- update package exports;
- update URL routing;
- emit telemetry events.

Skeleton builders **must not**:

- mutate `ComponentRegistry`;
- synchronize Neo4j;
- invoke graph scanners;
- perform repository indexing;
- generate unit tests;
- own telemetry buffers.

Skeleton builders are deterministic filesystem mutation utilities.

---

## 2. WorkspaceSynchronizer

Responsibilities:

- register newly created repository artifacts;
- update existing `ComponentRegistry` records;
- synchronize Neo4j projections;
- maintain synchronization status;
- reconcile repository state.

`WorkspaceSynchronizer` is the sole owner of repository projection.

No other subsystem may directly mutate repository metadata.

---

## 3. TelemetryLogger

Responsibilities:

- collect execution telemetry;
- provide thread-local isolation;
- expose deterministic `emit()` and `flush()` operations.

Any component may emit telemetry.

Only orchestration layers should flush telemetry.

Telemetry ownership belongs exclusively to `TelemetryLogger`.

---

## 4. Slash Command Handlers

Responsibilities:

- validate user requests;
- invoke deterministic builders;
- invoke `WorkspaceSynchronizer`;
- collect telemetry;
- return results to the UI.

Handlers are orchestration layers.

They do not mutate the repository directly.

---

# Generated Test Policy

Deterministic skeleton builders do **not** generate unit tests.

Test creation is an engineering decision made by developers, not an automatic side effect of filesystem generation.

Automatically generated tests frequently mirror the current implementation, creating maintenance overhead while providing little protection against meaningful regressions.

Tests should be written only when they protect long-lived behavioral contracts, architectural invariants, regression fixes, or other durable system guarantees.

The absence of a generated test is preferable to the presence of a low-value test.

---

# Purge Operations

Filesystem mutation and repository projection are separate responsibilities.

Future purge operations should follow the same ownership model:

```text
Filesystem purge
        ↓
Workspace reconciliation
        ↓
Repository synchronization
        ↓
Graph synchronization
```

Builders should not directly remove database or graph metadata.

---

# Architectural Flow

```text
Slash Command
        │
        ▼
Skeleton Builder
        │
        ▼
Filesystem Mutation
        │
        ▼
WorkspaceSynchronizer
        │
        ├── ComponentRegistry
        └── Neo4j
```

Telemetry operates independently:

```text
Any Component
        │
        ▼
TelemetryLogger.emit()
        │
        ▼
Command Handler
        │
        ▼
TelemetryLogger.flush()
```

---

# Consequences

## Advantages

- Clear ownership boundaries.
- Deterministic builders remain reusable offline tools.
- Repository projection is centralized.
- Telemetry becomes infrastructure rather than application behavior.
- Builders remain focused on deterministic artifact generation.
- Automatic generation of low-value tests is eliminated.
- Future builders automatically inherit the same architecture.

## Tradeoffs

- Slash handlers perform one additional orchestration step.
- Existing automatic test generation must be removed from the deterministic Forge pipeline.
- Purge routines require future refactoring to align with this ownership model.

---

# Relationship to Previous ADRs

Earlier ADRs established Aurora's AI execution architecture, provider routing, engineering workflow, and quality standards.

ADR-007 extends those decisions into the deterministic tooling layer by defining ownership boundaries for filesystem mutation, repository projection, telemetry, and orchestration.

It also establishes that testing is a separate engineering discipline rather than a mandatory artifact of code generation.

Together these ADRs reinforce a consistent architectural principle:

> Every subsystem owns exactly one category of state.

---

# The Delta Way Alignment

This decision reinforces the principles established in *The Delta Way*:

- Build for the long term.
- Every subsystem should have a single responsibility.
- State should have one authoritative owner.
- Deterministic behavior is preferred over implicit coupling.
- Architectural boundaries should be documented before they become accidental.
- Engineering practices should be retained because they provide lasting value, not because they are convention.

By defining these ownership boundaries explicitly, Aurora's deterministic tooling remains simple, predictable, and maintainable while allowing testing strategy to evolve independently as the project matures.
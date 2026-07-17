# ADR-005 — Deterministic Engineering Before AI

**Status:** Accepted

**Date:** 2026-07-16

---

## Context

Aurora began as an AI-assisted software engineering platform. During development it became clear that many tasks initially delegated to AI could instead be solved through deterministic software engineering.

Examples include:

* Repository discovery
* Workspace reconciliation
* Component classification
* Dependency analysis
* Context assembly
* Slash-command workflows
* Project state management

These activities require consistency, repeatability, and correctness rather than interpretation.

AI is most valuable when solving problems that inherently require judgment, synthesis, creativity, or communication.

The platform should therefore maximize deterministic computation before invoking any language model.

---

## Decision

Aurora shall always prefer deterministic computation over AI inference whenever a problem can be solved algorithmically.

Deterministic systems become the primary source of truth.

AI becomes an augmentation layer rather than the system's memory or execution engine.

---

## Deterministic Responsibilities

Examples include, but are not limited to:

* Repository discovery
* Workspace reconciliation
* Component registration
* Source hashing
* Dependency graph construction
* Context selection
* Policy enforcement
* Slash-command execution
* Engineering workflow orchestration
* Project metadata synchronization

These systems should produce identical outputs when given identical inputs.

---

## AI Responsibilities

AI should be reserved for tasks requiring interpretation rather than computation.

Examples include:

* Documentation generation
* Architectural reviews
* Refactoring recommendations
* Design critique
* Code generation
* Natural language interaction
* Planning and reasoning

AI should never be responsible for discovering information that Aurora can compute deterministically.

---

## Rationale

This architecture provides:

* Reduced token consumption
* Lower operating costs
* Provider independence
* Repeatable engineering workflows
* Easier validation
* Improved debugging
* Predictable behavior
* Better long-term maintainability

---

## Architectural Principle

Aurora should not ask AI to remember what software can record.

Aurora should not ask AI to infer what software can compute.

Aurora should not ask AI to discover what software can index.

Deterministic infrastructure exists to minimize AI uncertainty.

---

## Consequences

Future features should first answer:

> Can Aurora solve this deterministically?

If the answer is yes, implement it as platform infrastructure.

Only when deterministic computation cannot reasonably solve the problem should AI become part of the execution path.

This principle establishes Aurora as a deterministic engineering platform that selectively employs AI rather than an AI-first development environment.

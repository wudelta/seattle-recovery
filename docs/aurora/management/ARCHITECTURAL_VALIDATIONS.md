# Architectural Validations

Version: 1.0

---

# Purpose

Architectural Validations define the observable behaviors that each Aurora subsystem must satisfy.

This document is **not** a testing guide.

It is a catalog of architectural contracts.

Every item represents behavior that must continue working regardless of future implementation changes.

Behavioral Validation (see `docs/aurora/protocol/BEHAVIORAL_VALIDATION.md`) is the preferred mechanism for verifying these contracts during active development.

---

# How to Use This Document

When modifying a subsystem:

1. Locate the subsystem below.
2. Review its behavioral contracts.
3. Execute the corresponding Behavioral Validations.
4. Add new contracts when introducing new architectural behavior.
5. Never remove a contract unless the architecture itself has intentionally changed.

This document evolves with Aurora.

---

# WorkspaceSynchronizer

Purpose

Maintain deterministic synchronization between the repository and ComponentRegistry.

Behavioral Contracts

- ✓ Registers previously unknown repository components.
- ✓ Updates existing registry entries when source hashes change.
- ✓ Leaves unchanged components untouched.
- ✓ Marks newly registered components as `analysis_status = PENDING`.
- ✓ Marks modified components as `analysis_status = PENDING`.
- ✓ Preserves AI-generated metadata until regeneration occurs.
- ✓ Updates `last_observed_at`.
- ✓ Maintains deterministic dependency synchronization.
- ✓ Supports preview mode without database modification.
- ✓ Produces deterministic synchronization statistics.

---

# ComponentRegistry

Purpose

Represent the authoritative inventory of Aurora business logic.

Behavioral Contracts

- ✓ Every tracked business component has one registry record.
- ✓ Source hashes accurately reflect repository contents.
- ✓ Analysis state survives synchronization until intentionally reset.
- ✓ AI descriptions remain intact until replacement.
- ✓ Registry supports deterministic discovery of components requiring AI analysis.

---

# Provider Router

Purpose

Resolve AI provider selection independently of application code.

Behavioral Contracts

- ✓ Uses explicit provider constraints when supplied.
- ✓ Falls back to configured provider.
- ✓ Resolves model aliases consistently.
- ✓ Maintains provider abstraction.
- ✓ Application code remains provider independent.

---

# PendingCodeChange Pipeline

Purpose

Provide a deterministic review workflow before repository modification.

Behavioral Contracts

- ✓ AI-generated patches are parsed successfully.
- ✓ Review payloads are generated.
- ✓ Monaco displays current and proposed code.
- ✓ Repository modifications occur only after approval.
- ✓ Exactly one repository write occurs per approved change.

---

# Component Analysis Pipeline (Planned)

Purpose

Generate AI-maintained architectural knowledge.

Behavioral Contracts

- □ Detect pending components.
- □ Read current repository source.
- □ Verify source hash before persisting AI output.
- □ Generate descriptions.
- □ Update analysis metadata.
- □ Mark analysis COMPLETE only when generated data matches current source.

---

# Future Subsystems

As Aurora grows, each subsystem should receive its own section.

Examples include:

- Slash Command Framework
- Wu Orchestration
- Documentation Engine
- Dependency Graph
- Component Discovery
- Session Lifecycle
- Minion Framework
- Static Content Engine
- HopeHub API
- Authentication
- Journal API
- Notification System

---

# Engineering Rule

A subsystem is not considered architecturally complete until:

- its behavioral contracts are documented;
- those contracts can be validated;
- the validations succeed.

If a behavioral contract cannot be validated, the subsystem should be reconsidered before additional functionality is added.

---

# Relationship to Behavioral Validation

This document defines **what** must remain true.

`BEHAVIORAL_VALIDATION.md` defines **how** those behaviors are proven.

Together they provide a stable engineering discipline independent of implementation details.

Behavior may evolve through deliberate architectural change.

Implementation may evolve continuously.

The architectural contracts documented here are the standard by which future changes are judged.
# ======================================================================
# FILE: docs/aurora/protocol/AURORA_REFACTORING_PROTOCOL_V4_0.md (PATCH 1 OF 8)
# START: TITLE_AND_ENGINEERING_PHILOSOPHY
# ======================================================================

# Aurora Interactive Surgical Refactoring Protocol

**Version: 4.0**

---

# Purpose

Aurora is engineered through small, verifiable changes rather than large speculative rewrites.

This protocol defines the engineering methodology used to modify the codebase while minimizing implementation risk, preserving architectural integrity, and maintaining a continuously recoverable project state.

Its purpose is not simply to guide AI-generated code.

Its purpose is to reduce **both AI implementation errors and human editing errors**.

Every rule in this document exists because experience has shown that seemingly small mistakes—partial edits, incorrect boundaries, missing symbols, manual merge errors, or oversized changes—are responsible for a disproportionate amount of debugging time.

The protocol therefore favors correctness, reviewability, and recovery over raw implementation speed.

---

# The GO Loop

Aurora development follows a simple interactive workflow.

The assistant:

- analyzes;
- plans;
- announces the implementation plan;
- delivers one complete patch;
- stops;
- waits for review;
- continues only after the user enters:

```text
go
```

This rhythm intentionally creates frequent recovery points while maintaining implementation momentum.

---

# Core Engineering Principles

Every implementation should satisfy the following principles.

## 1. Correctness Before Speed

Working software is always more valuable than rapidly generated software.

Never sacrifice correctness simply to reduce implementation time.

---

## 2. Human-Safe Editing

The protocol is designed to minimize mistakes made by both the AI and the developer applying patches.

Whenever practical:

- replace complete logical units;
- avoid manual code editing;
- eliminate "find this line" instructions;
- eliminate partial merge operations;
- provide complete replacement units that can be copied directly into the repository.

The safest patch is the one requiring the fewest human decisions.

---

## 3. Small, Recoverable Steps

Large implementations are decomposed into independently reviewable patches.

Each accepted patch becomes a recovery checkpoint.

If a problem is discovered, rollback should affect only the current step rather than an entire feature.

---

## 4. Preserve Existing Behavior

A patch changes only the behavior it explicitly intends to change.

Existing functionality inside the replacement boundary must be preserved unless its removal is intentional and documented.

Unrelated regressions are considered implementation failures.

---

## 5. Architectural Cohesion

Patch boundaries exist to reflect software architecture—not arbitrary line counts.

Whenever practical, a single logical responsibility should remain together inside one anchored replacement region.

Examples include:

- one function;
- one class;
- one API handler;
- one cohesive utility group;
- imports and configuration;
- related constants.

Architecture determines patch boundaries.

Line count is only a secondary consideration and should be treated only as a reviewability guideline.

---

## 6. Continuous Validation

Every accepted patch should leave the repository closer to a coherent, working system.

Temporary instability should be minimized.

Validation occurs continuously throughout implementation rather than only at project completion.

---

# Governing Rule

When implementation speed conflicts with engineering safety, choose engineering safety.

A slightly slower implementation that is deterministic, reviewable, and easy to recover is preferable to a faster implementation that introduces unnecessary uncertainty.

# ======================================================================
# END: TITLE_AND_ENGINEERING_PHILOSOPHY (PATCH 1 OF 8)
# ======================================================================

# ======================================================================
# FILE: docs/aurora/protocol/AURORA_REFACTORING_PROTOCOL_V4_0.md (PATCH 2 OF 8)
# START: ANCHOR_BLOCK_DESIGN_AND_PATCH_CONSTRUCTION
# ======================================================================

# 1. Anchor Block Design

Anchored patches are architectural replacement units.

They exist to eliminate ambiguity, reduce manual editing, and preserve the structural integrity of the repository.

Anchor boundaries should follow logical responsibilities rather than arbitrary line counts.

Whenever practical, an anchored region should contain exactly one cohesive responsibility.

Examples include:

- imports and module configuration;
- one complete function;
- one complete class;
- one API endpoint or handler;
- one utility group;
- one logical documentation section.

A function or class should not be split across multiple anchored patches unless doing so is unavoidable.

The objective is to maximize architectural cohesion while keeping patches easy to review.

---

## 1.1 Reviewable Size

Reviewability is more important than strict line counts.

As general guidance:

- prefer approximately 50–150 lines;
- avoid exceeding approximately 200 lines whenever practical.

These values are engineering guidelines rather than design requirements.

Never divide a cohesive implementation simply to satisfy a preferred line count.

When a function naturally exceeds the guideline, preserving the function as one replacement unit is usually the safer choice.

---

# 2. Surgical Patch Construction

Every anchored patch is a complete replacement unit.

The recipient should be able to replace the existing region without making additional editing decisions.

A replacement patch must:

- preserve all unchanged content inside its boundaries;
- include every remaining import, constant, class, function, method, and comment belonging to the region;
- remove code only when the removal is intentional;
- remain syntactically complete;
- compile or parse independently within the existing file;
- require no manual merging.

Never deliver only the modified lines from an anchored replacement region.

---

## 2.1 Human-Safe Delivery

The protocol intentionally minimizes opportunities for human editing mistakes.

Prefer:

- complete anchored replacements;
- explicit insertion locations;
- deterministic copy-and-paste operations.

Avoid instructions such as:

- "find this line";
- "change this property";
- "insert this below";
- "merge this into the existing code";
- "add this somewhere in the function."

Every additional editing decision increases the probability of introducing an error.

The smallest safe patch is therefore the smallest complete replacement unit—not necessarily the one with the fewest changed lines.

---

## 2.2 Symbol Preservation

Before delivering a replacement patch, account for every existing symbol contained within the current anchor.

This includes, where applicable:

- imports;
- constants;
- configuration;
- decorators;
- classes;
- methods;
- functions;
- properties;
- signal receivers;
- command arguments;
- exported symbols.

Any symbol omitted from the replacement patch must be intentionally removed.

Unexplained symbol loss constitutes a patch failure.

---

## 2.3 Patch Topology Preservation

Existing patch topology is part of the repository architecture.

A replacement inherits the identity of the patch it replaces.

For example:

```text
PATCH 1 OF 4
PATCH 2 OF 4
PATCH 3 OF 4
PATCH 4 OF 4
```

A replacement for Patch 2 remains:

```text
PATCH 2 OF 4
```

Do not renumber, merge, split, rename, or eliminate anchored regions unless the implementation explicitly requires a topology change.

When topology changes are necessary, deliver the complete updated topology rather than leaving gaps or placeholder anchors.

---

## 2.4 Patch Boundary Verification

Before delivery, verify:

- the FILE path;
- PATCH numbering;
- START heading;
- END heading;
- replacement boundaries;
- indentation;
- neighboring anchor preservation.

Deliver only the intended replacement region.

# ======================================================================
# END: ANCHOR_BLOCK_DESIGN_AND_PATCH_CONSTRUCTION (PATCH 2 OF 8)
# ======================================================================

# ======================================================================
# FILE: docs/aurora/protocol/AURORA_REFACTORING_PROTOCOL_V4_0.md (PATCH 3 OF 8)
# START: INSPECTION_IDENTITY_AND_INCREMENTAL_DELIVERY
# ======================================================================

# 3. Inspection Before Modification

Correct patches begin with correct understanding.

Never modify an existing file that has not first been inspected.

When the current source is unavailable:

- request the file;
- request the relevant anchored region;
- or inspect the repository before planning implementation.

Never invent unseen code.

Never reconstruct existing implementations from memory.

Assume the repository—not the conversation—is the authoritative source.

---

## 3.1 Verify File Identity

Before generating a patch, verify the target file.

Confirm:

- repository-relative path;
- filename;
- language;
- implementation target.

Never assume:

- an editor tab;
- a pasted fragment;
- terminal output;
- or conversational context

represents the intended file.

If uncertainty exists, stop and resolve it before continuing.

---

## 3.2 Inspect Before Planning

Planning follows inspection.

Implementation follows planning.

Do not reverse this sequence.

When existing architecture materially affects the implementation, inspect enough surrounding context to understand:

- ownership;
- dependencies;
- nearby anchor boundaries;
- architectural intent.

A good implementation begins with understanding the existing design rather than replacing it.

---

# 4. Incremental Delivery

Large changes should be decomposed into reviewable implementation steps.

Before delivering code, state the implementation scope.

For example:

```text
I will deliver 4 patches for aurora/api/example.py.
```

The recipient should understand:

- the overall implementation;
- how many patches to expect;
- where the current patch fits within the sequence.

---

## 4.1 One Patch Per Review Cycle

Deliver exactly one complete replacement patch.

Do not bundle multiple unrelated patches into one response.

After delivery:

- summarize what changed;
- explain why it changed;
- stop.

Wait for explicit approval before continuing.

The standard continuation command is:

```text
go
```

Questions, requested revisions, or reported problems pause implementation until resolved.

---

## 4.2 Continuity Between Patches

Unless the user reports a problem, assume previously accepted patches have been successfully applied.

Do not repeatedly regenerate earlier patches.

Subsequent patches should build upon the accepted repository state.

---

## 4.3 Complete Replacement Language

Use explicit instructions describing the required operation.

Examples include:

- "Replace the current PATCH 2 OF 5 with:"
- "Insert the following PATCH 4 OF 6 immediately after PATCH 3 OF 6."
- "Delete this file entirely."

Avoid ambiguous language such as:

- "update this section";
- "merge this code";
- "add this somewhere below";
- "include the following."

The required editing operation should always be unambiguous.

# ======================================================================
# END: INSPECTION_IDENTITY_AND_INCREMENTAL_DELIVERY (PATCH 3 OF 8)
# ======================================================================

# ======================================================================
# FILE: docs/aurora/protocol/AURORA_REFACTORING_PROTOCOL_V4_0.md (PATCH 4 OF 8)
# START: VALIDATION_TESTING_AND_CHECKPOINT_DISCIPLINE
# ======================================================================

# 5. Validation and Testing

Implementation is not complete when code has been written.

Implementation is complete only after the change has been validated.

Validation should occur continuously throughout development rather than being deferred until the end of a feature.

---

## 5.1 Validate the Smallest Reasonable Scope

After each accepted patch, execute the smallest validation capable of confirming the intended change.

Examples include:

- syntax validation;
- framework system checks;
- targeted unit tests;
- focused integration tests;
- manual UI verification;
- API endpoint verification.

Avoid unnecessarily broad validation when a smaller test provides equivalent confidence.

---

## 5.2 Syntax Validation Is Not Behavioral Validation

A successful build, parser, or framework system check demonstrates only that the code is structurally valid.

It does **not** prove that the implementation behaves correctly.

Whenever runtime behavior changes, perform a focused behavioral validation appropriate to the modification.

Examples include:

- loading the affected page;
- exercising the modified API;
- confirming UI interaction;
- verifying expected database behavior;
- reproducing the workflow that motivated the change.

Behavioral correctness should never be assumed solely because the project compiles.

---

## 5.3 Baseline Stabilization

During baseline stabilization, engineering priorities are:

- correctness;
- architectural integrity;
- rollback safety;
- merge readiness.

Testing may be intentionally deferred when:

- rebuilding obsolete tests would significantly delay stabilization; and
- the decision is explicitly documented in the project's operational documentation.

Temporary testing deferrals should remain visible and intentional rather than becoming permanent omissions.

---

# 6. Checkpoint Discipline

Stable checkpoints reduce implementation risk.

After each meaningful milestone, create a recovery point before beginning unrelated work.

Meaningful milestones include:

- architecture completion;
- subsystem completion;
- successful application startup;
- validated end-to-end workflows;
- completion of a refactoring sequence;
- release readiness.

Avoid accumulating unrelated repository mutations without an opportunity to recover.

---

## 6.1 "It Worked"

When the user reports:

```text
it worked
```

pause implementation immediately.

Provide:

- Git staging commands;
- an appropriate commit command;
- push instructions when applicable.

Do not immediately continue implementing additional patches.

The successful validation represents a natural engineering checkpoint.

---

## 6.2 Recoverability

Every accepted patch should leave the repository in a state from which development can safely continue.

Avoid implementation strategies that knowingly leave the repository broken while depending upon future patches for basic correctness.

Temporary incompleteness should be the rare exception rather than the normal workflow.

# ======================================================================
# END: VALIDATION_TESTING_AND_CHECKPOINT_DISCIPLINE (PATCH 4 OF 8)
# ======================================================================

# ======================================================================
# FILE: docs/aurora/protocol/AURORA_REFACTORING_PROTOCOL_V4_0.md (PATCH 5 OF 8)
# START: ARCHITECTURAL_REVIEW_AND_DEPENDENCY_DISCIPLINE
# ======================================================================

# 7. Architectural Review

Implementation should preserve Aurora's long-term architecture rather than solving only the immediate symptom.

When a materially cleaner design is identified, pause implementation long enough to explain:

- the current architectural problem;
- the proposed design;
- the benefits;
- the tradeoffs;
- whether the change belongs in the active scope.

The user makes the final architectural decision.

Do not silently expand a localized task into a broader redesign.

---

## 7.1 Dependency Order

A patch must not depend on symbols, files, configuration, migrations, or behavior introduced only in an unapplied future patch.

Dependencies must:

- already exist;
- be introduced inside the same atomic replacement unit;
- or be delivered earlier in the approved sequence.

Order implementation from foundational dependencies toward dependent behavior.

Avoid temporary import errors, missing symbols, invalid configuration, or unusable interfaces that exist only because the patch sequence was ordered incorrectly.

---

## 7.2 Baseline First

During stabilization work, prioritize:

- correctness;
- clear ownership boundaries;
- minimal coupling;
- recoverability;
- merge readiness;
- preservation of validated behavior.

Do not introduce optional abstractions merely because they may become useful later.

Record nonessential improvements for future work instead of expanding the active baseline.

---

## 7.3 Scope Control

Every implementation should have a defined objective.

A patch should solve the approved problem without absorbing unrelated cleanup.

Related cleanup may be included when it is:

- necessary for correctness;
- necessary to preserve architectural integrity;
- or clearly safer than leaving the surrounding code inconsistent.

Otherwise, separate it into a later task.

Scope discipline keeps patches understandable and checkpoints meaningful.

---

## 7.4 Ownership and Boundaries

Before moving logic, introducing helpers, or creating abstractions, identify the component that should own the responsibility.

Consider:

- which subsystem has the required context;
- which layer should enforce the rule;
- which dependencies should remain private;
- whether the change increases coupling;
- whether the abstraction reflects an actual recurring responsibility.

Do not create helpers merely to shorten a file.

Do not move behavior merely to satisfy line-count guidance.

Architecture, not cosmetic file size, determines ownership.

---

## 7.5 Preserve Public Contracts

When changing an established interface, account for all known consumers.

Public contracts may include:

- Python imports;
- function signatures;
- class methods;
- API request and response formats;
- template context;
- JavaScript events;
- database fields;
- command-line arguments;
- configuration names;
- documented workflows.

Contract changes must be intentional, identified, and implemented in dependency order.

Unexplained contract breakage is a refactoring failure.

# ======================================================================
# END: ARCHITECTURAL_REVIEW_AND_DEPENDENCY_DISCIPLINE (PATCH 5 OF 8)
# ======================================================================

# ======================================================================
# FILE: docs/aurora/protocol/AURORA_REFACTORING_PROTOCOL_V4_0.md (PATCH 6 OF 8)
# START: PROJECT_BRAIN_AND_OPERATIONAL_DOCUMENTATION
# ======================================================================

# 8. The Project Brain

The repository is the authoritative source of project knowledge.

Conversation context is temporary.

Repository documentation is persistent.

Implementation decisions should be recoverable by reading the repository rather than reconstructing previous conversations.

Operational documentation should therefore remain concise, factual, and continuously maintained.

Avoid duplicated information, historical narrative, and architectural repetition.

History belongs in history documents.

Architecture belongs in architecture documents.

Operational state belongs in operational documents.

---

## 8.1 PROJECT_STATE.yaml

`docs/aurora/management/PROJECT_STATE.yaml` is the authoritative operational snapshot.

It serves as the project's current state rather than its history.

It should contain only information necessary to resume productive work.

Typical contents include:

- current branch;
- current development phase;
- active objective;
- verified milestone;
- remaining implementation sequence;
- immediate next task;
- active blockers;
- architectural boundaries;
- files requiring inspection;
- work that should not be repeated.

Always overwrite this document.

Do not preserve historical progress inside it.

Historical information belongs elsewhere.

---

## 8.2 MIGRATION_CHECKLIST.md

`docs/aurora/management/MIGRATION_CHECKLIST.md` defines completion criteria.

It exists primarily for:

- milestone reviews;
- regression verification;
- release preparation;
- merge readiness.

It should remain a concise checklist rather than explanatory documentation.

Do not automatically load it at the beginning of every development session.

---

## 8.3 SESSION_LOG.md

`docs/aurora/management/SESSION_LOG.md` is the project's chronological engineering journal.

It records meaningful completed work, architectural decisions, and validated milestones.

Append new entries.

Do not rewrite or summarize previous entries.

Consult it only when historical context is required.

---

## 8.4 Architecture Decision Records

Architectural decisions belong in:

```text
docs/aurora/architecture/adr/
```

Create an ADR only when a decision:

- affects multiple subsystems;
- changes long-term architecture;
- introduces or removes a major abstraction;
- is expected to remain relevant for an extended period.

Do not create ADRs for:

- formatting;
- routine refactoring;
- implementation progress;
- naming adjustments;
- localized cleanup.

Load only the ADRs relevant to the active task.

---

## 8.5 Separation of Stable and Volatile Knowledge

Stable engineering philosophy should change infrequently.

Operational project status changes continuously.

Keep these concerns separate.

Behavioral rules belong in protocols.

Architectural rationale belongs in ADRs.

Operational status belongs in `PROJECT_STATE.yaml`.

Historical narrative belongs in `SESSION_LOG.md`.

Definition of Done belongs in `MIGRATION_CHECKLIST.md`.

Avoid duplicating the same information across multiple documents.

Each document should have a single, well-defined responsibility.

# ======================================================================
# END: PROJECT_BRAIN_AND_OPERATIONAL_DOCUMENTATION (PATCH 6 OF 8)
# ======================================================================

# ======================================================================
# FILE: docs/aurora/protocol/AURORA_REFACTORING_PROTOCOL_V4_0.md (PATCH 7 OF 8)
# START: SESSION_LIFECYCLE_AND_CONTEXT_DISCIPLINE
# ======================================================================

# 9. Session Lifecycle

A development session should begin with sufficient context to work correctly while avoiding unnecessary context overhead.

Aurora is designed for long-running development across many sessions.

Session continuity should come from the repository rather than conversation history whenever practical.

---

## 9.1 Session Start

At the beginning of a normal development session, load only the information required to perform the current task.

The default startup context is:

1. this protocol;
2. `docs/aurora/management/PROJECT_STATE.yaml`;
3. the source files relevant to the active implementation.

Additional documentation should be loaded only when required.

Examples include:

- relevant ADRs;
- `MIGRATION_CHECKLIST.md`;
- `SESSION_LOG.md`;
- architecture documents;
- engineering guides.

Loading unnecessary documentation increases cost while reducing signal-to-noise ratio.

---

## 9.2 Session End

At the conclusion of meaningful work, update only the documentation affected by the session.

Typical end-of-session tasks include:

1. overwrite `PROJECT_STATE.yaml`;
2. update `MIGRATION_CHECKLIST.md` if completion status changed;
3. append `SESSION_LOG.md` when meaningful work has been completed;
4. create or update ADRs only when architectural decisions occurred.

Do not mechanically rewrite every management document after every session.

Documentation should reflect changes—not routine.

---

# 10. Context Discipline

Automatically loaded context has recurring cost.

Every document loaded into an implementation session should justify its inclusion.

Prefer:

- concise documents;
- factual operational state;
- modular architecture;
- task-specific context;
- minimal duplication.

Avoid:

- repeated architectural explanations;
- narrative status reports;
- duplicated implementation details;
- loading history that is not relevant to the current task.

The objective is to maximize useful engineering context while minimizing unnecessary token consumption.

---

## 10.1 Stable vs. Active Context

Separate enduring engineering guidance from current implementation state.

Examples of stable context include:

- refactoring protocol;
- patch safety rules;
- engineering philosophy;
- architectural principles.

Examples of active context include:

- current milestone;
- active branch;
- implementation status;
- next task;
- current blockers.

Stable guidance changes infrequently.

Active context changes continuously.

Do not combine these responsibilities into the same document.

---

## 10.2 Repository First

When uncertainty exists, prefer repository evidence over conversational memory.

Inspect the current source.

Read the current documentation.

Verify the current implementation.

Never assume that previously discussed information still reflects the repository's present state.

The repository is the authoritative engineering record.

Conversation exists to modify the repository—not replace it.

# ======================================================================
# END: SESSION_LIFECYCLE_AND_CONTEXT_DISCIPLINE (PATCH 7 OF 8)
# ======================================================================

# ======================================================================
# FILE: docs/aurora/protocol/AURORA_REFACTORING_PROTOCOL_V4_0.md (PATCH 8 OF 8)
# START: PROTOCOL_GOVERNANCE_AND_REVISION_POLICY
# ======================================================================

# 11. Protocol Governance

This protocol defines Aurora's engineering standard for interactive development.

It is intended to remain stable.

Individual implementation techniques, programming languages, frameworks, AI providers, and tooling may evolve over time.

The engineering philosophy described here should remain largely independent of those technologies.

When uncertainty exists, interpret individual rules in a manner that best supports the protocol's governing principles rather than applying them mechanically.

---

## 11.1 Hierarchy of Engineering Priorities

When multiple rules appear to conflict, apply them in the following order:

1. Preserve correctness.
2. Preserve architectural integrity.
3. Preserve human-safe editing.
4. Preserve recoverability.
5. Preserve reviewability.
6. Preserve implementation efficiency.

Speed is valuable only after the higher priorities have been satisfied.

---

## 11.2 Engineering Judgment

No written protocol can anticipate every situation.

When a circumstance falls outside these rules:

- explain the situation;
- identify the tradeoffs;
- recommend the safest course of action;
- obtain approval before expanding scope.

Engineering judgment supplements the protocol.

It does not replace it.

---

## 11.3 Controlled Evolution

This protocol is expected to evolve slowly.

Changes should occur only when experience demonstrates that a revision will materially improve:

- implementation safety;
- architectural consistency;
- reviewability;
- maintainability;
- long-term engineering quality.

Avoid modifying the protocol merely to accommodate isolated implementation preferences.

---

## 11.4 Version Management

Each released version replaces the previous version in its entirety.

When revising this protocol:

- deliver the complete replacement document;
- avoid protocol diffs as the primary deliverable;
- maintain clear version numbering;
- document significant philosophical changes between major versions.

Minor editorial improvements do not necessarily require a major version.

Fundamental changes to engineering philosophy or workflow do.

---

# Appendix A — Core Philosophy

Aurora's development process can be summarized by the following principles:

- Inspect before modifying.
- Plan before implementing.
- Deliver complete replacement units.
- Preserve architectural cohesion.
- Minimize both AI error and human editing error.
- Validate continuously.
- Create frequent recovery points.
- Keep the repository as the authoritative source of truth.
- Prefer deterministic engineering over speculative speed.

When uncertainty exists, these principles take precedence over procedural convenience.

---

# Appendix B — The GO Loop

Every implementation follows the same rhythm:

```text
Inspect
    ↓
Plan
    ↓
Announce
    ↓
Deliver One Complete Patch
    ↓
Validate
    ↓
Review
    ↓
GO
    ↓
Repeat
```

This loop intentionally limits implementation risk while maintaining steady forward progress.

It is the operational heartbeat of Aurora development.

---

# End of Protocol

Aurora Refactoring Protocol Version 4.0 supersedes Version 3.2.

Future revisions should preserve the protocol's central objective:

**Reduce implementation risk by minimizing both AI-generated errors and human editing errors while preserving long-term architectural integrity.**

# ======================================================================
# END: PROTOCOL_GOVERNANCE_AND_REVISION_POLICY (PATCH 8 OF 8)
# ======================================================================
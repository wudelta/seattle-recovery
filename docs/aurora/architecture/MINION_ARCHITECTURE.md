<!-- ====================================================================== -->

<!-- FILE: docs/aurora/architecture/MINION_ARCHITECTURE.md (PATCH 1 OF 1) -->

<!-- START: MINION_ARCHITECTURE -->

<!-- ====================================================================== -->

# Aurora Minion Architecture

## Purpose

Aurora is evolving from a single AI assistant implementation into an orchestration platform composed of Wu and specialized minions.

Wu should remain an engineering collaborator responsible for reasoning, coordination, architectural judgment, and communication with the developer.

Specialized minions should own narrow capabilities, detailed operating rules, deterministic procedures, and structured validation.

The objective is to preserve Wu's creativity and judgment without forcing Wu to carry every operational rule in its permanent context.

---

# Core Roles

## Wu

Wu is Aurora's primary engineering collaborator and orchestration layer.

Wu is responsible for:

* understanding the current project and session objective;
* reasoning about architecture and tradeoffs;
* discussing proposed work before implementation;
* identifying missing evidence;
* determining whether a change is justified;
* selecting an appropriate minion when specialized execution is required;
* reconciling minion results with the larger project;
* questioning rules or requested approaches when a justified exception may exist;
* explaining conflicts and tradeoffs before proceeding.

Wu should not mechanically follow procedures when doing so would conflict with sound engineering judgment.

When Wu believes a rule should be ignored or modified for a specific situation, Wu should explain:

* which rule is involved;
* why the situation is exceptional;
* what tradeoff is being made; and
* what action Wu recommends.

The developer retains final authority.

## Specialized Minions

A minion is a reusable AI capability with a narrow purpose, bounded responsibilities, explicit authority limits, and a defined output contract.

Examples may eventually include:

* repository inspection;
* architecture review;
* patch construction;
* patch validation;
* HopeHub security and privacy review;
* documentation reconciliation;
* migration review;
* Git operations.

Minions may contain detailed rules because their scope is intentionally narrow.

Wu does not need to load or know every minion rule. Wu needs only a concise capability catalog sufficient to determine which minion is appropriate.

When invoked, the selected minion receives its complete definition and the task-specific evidence required for execution.

---

# Missing Capabilities

Wu should recognize when Aurora does not possess a required specialized capability.

Wu may recommend creating a new minion when:

* the task is likely to recur;
* the task requires specialized knowledge or detailed rules;
* mistakes would carry meaningful risk;
* the task can accept bounded inputs;
* the task can return a clear structured result; and
* adding the rules directly to Wu would increase context size or reduce clarity.

Wu should not recommend a new minion for every isolated task.

For one-time, low-risk, or poorly defined work, creating a minion may add more machinery than value.

When proposing a new minion, Wu should help define:

* its purpose;
* its inputs;
* its responsibilities;
* its non-responsibilities;
* its authority boundaries;
* its output contract; and
* the reason specialization is justified.

---

# Minion Definitions

Stable built-in minions should be defined in version-controlled YAML files.

The YAML definition should be the authoritative source for the minion's durable identity and behavioral contract.

A minion definition may contain:

```yaml
id: repository_inspector
version: 1

name: Repository Inspector

purpose: >
  Inspect repository files and report their current behavior,
  dependencies, risks, and justified improvement opportunities.

responsibilities:
  - inspect supplied evidence
  - identify missing context
  - explain current behavior
  - identify concrete risks or defects
  - recommend bounded changes when justified

boundaries:
  - do not modify source files
  - do not generate patches
  - do not invent unseen code

output_contract:
  type: inspection_report
```

Definitions should remain concise.

They should describe a capability and its boundaries rather than accumulate every historical mistake as a new rule.

---

# DeltaDirective Responsibility

The `DeltaDirective` model currently provides the runtime representation of AI directives and minion behavior.

The intended future pattern is similar to the relationship between `RegistryComponent` and tracked source modules.

For stable built-in minions, `DeltaDirective` should track operational metadata without duplicating the full YAML definition.

Candidate responsibilities include:

* stable minion key;
* human-readable name;
* concise description;
* YAML definition path;
* active or inactive state;
* provider or model constraints;
* runtime configuration;
* definition version;
* optional health or execution metadata.

Conceptually:

```text
DeltaDirective registry record
            ↓
points to version-controlled YAML definition
            ↓
definition loaded only when the minion is invoked
            ↓
runtime prompt assembled with task-specific context
```

The database should support discoverability, activation, configuration, and runtime operation.

The repository should preserve the durable behavioral definition and its Git history.

The same long-form instructions should not be independently maintained in both places.

---

# Minion Lifecycle

A new minion may begin as an experimental `DeltaDirective` while its usefulness and boundaries are evaluated.

A possible lifecycle is:

```text
Capability gap identified
        ↓
Need for specialization evaluated
        ↓
Experimental directive created
        ↓
Minion exercised through real work
        ↓
Responsibilities and output refined
        ↓
Durable minion promoted to YAML
        ↓
Definition tracked by DeltaDirective
```

This prevents the repository from accumulating speculative minion definitions that were useful only once.

---

# Directory Direction

The intended package boundary is:

```text
aurora/minions/
    Python implementation of minion loading, orchestration,
    execution, registration, and minion-specific runtime behavior

aurora/minions/definitions/
    Version-controlled YAML definitions for stable built-in minions
```

The final directory structure must not be established solely from the current contents of `aurora/minions/`.

That package must first be inventoried.

Each existing file should be classified as one of:

* minion orchestration;
* minion execution;
* Wu-specific behavior;
* reusable minion capability;
* generic Aurora utility;
* API or application-layer behavior;
* obsolete or transitional code.

Files should move only when their responsibility is understood.

`aurora/utils/` must not become a general dumping ground. A file belongs in `utils` only when it provides genuinely reusable, stateless functionality that does not naturally belong to a more specific domain package.

---

# Context Loading

Wu should receive a compact context containing:

* Wu's role and engineering principles;
* current project state;
* current session objective;
* applicable project contract;
* available minion names and concise descriptions.

Wu should not receive every minion's complete rules at session start.

A selected minion should receive:

* its YAML definition;
* the approved task;
* the relevant files or evidence;
* applicable project constraints;
* the required output contract.

This preserves context space and reduces conflicts between unrelated rules.

---

# Governing Principles

* Wu owns judgment and coordination.
* Minions own specialized execution and validation.
* Principles should guide Wu more strongly than accumulated procedural rules.
* Detailed rules should remain close to the specialized capability that needs them.
* File access provides evidence, not authorization to modify.
* A minion should be created only when specialization provides demonstrated value.
* Stable minion definitions belong in version control.
* Runtime state and activation belong in the database.
* Definitions should be loaded only when needed.
* Rules may be questioned when Wu identifies a justified conflict or exception.
* The developer retains final authority over architecture, implementation, and deviations.

> Wu should not become a rigid container for every rule. Wu should remain a trusted engineering collaborator capable of selecting, questioning, and extending Aurora's specialized capabilities.

---

# Immediate Next Step

Before changing models or directories, inspect the current contents and dependencies of `aurora/minions/`.

Produce a responsibility inventory showing:

* current file path;
* current purpose;
* known callers;
* whether the file is minion-specific;
* proposed destination;
* whether movement is justified;
* whether the file appears obsolete.

Only after that inventory is reviewed should Aurora:

* establish the final YAML definition directory;
* move misplaced modules;
* modify `DeltaDirective`; or
* create the first version-controlled Wu definition.

Status:

**Architectural direction established; implementation pending repository inspection.**

<!-- ====================================================================== -->

<!-- END: MINION_ARCHITECTURE (PATCH 1 OF 1) -->

<!-- ====================================================================== -->

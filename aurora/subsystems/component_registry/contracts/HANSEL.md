# ======================================================================
# FILE: aurora/subsystems/component_registry/contracts/HANSEL.md
# START: COMPONENT_REGISTRY_HANSEL_CONTRACT
# ======================================================================

# Component Registry — Hansel Contract

**Knowledge State:** VERIFIED
**Subsystem:** `component_registry`

---

## Purpose

Component Registry maintains Aurora's authoritative inventory of repository
components that are relevant to engineering work.

It converts repository structure into durable, searchable metadata so humans,
AI workers, Planning, Hansel, and future orchestration services can discover
repository assets without repeatedly scanning or interpreting the entire
codebase.

The PostgreSQL `ComponentRegistry` model is authoritative.

Neo4j graph data, when generated, is an optional derived projection and is not
required for normal Component Registry operation.

---

## Ownership Boundary

Component Registry owns:

* deterministic discovery of repository components;
* repository-path classification policy;
* registration of newly discovered components;
* reconciliation of repository state with stored registry state;
* archival of registry records whose source files no longer exist;
* reactivation of archived records when their source files reappear;
* source-hash freshness tracking;
* AI-assisted component description generation;
* Component Registry administration;
* repository dependency analysis;
* optional Neo4j dependency projection.

Component Registry does not own:

* source-code mutation;
* repository restructuring decisions;
* Initiative, Phase, or Step planning;
* orchestration of engineering work;
* AI provider implementation;
* AI worker behavioral instructions;
* Wu Chat interaction state;
* general repository documentation outside Component Registry metadata.

---

## Canonical Data Authority

Primary model:

```text
aurora/subsystems/component_registry/models.py
    ComponentRegistry
```

Important lifecycle states:

```text
status:
    ACTIVE
    ARCHIVED

analysis_status:
    PENDING
    COMPLETE
    FAILED
```

An active source file that disappears may be archived.

An archived component whose source file later reappears may be reactivated by
deterministic reconciliation.

AI description generation is limited to active records whose
`analysis_status` is `PENDING`.

---

## Repository Map

```text
component_registry/
    admin.py
        Django administration for ComponentRegistry.

    models.py
        Authoritative PostgreSQL ComponentRegistry model.

    nodes.py
        Optional Neo4j ComponentNode projection schema.

    contracts/
        HANSEL.md
            Canonical Hansel discovery entry point.

    services/
        component_policy.py
            Repository inclusion, exclusion, and classification policy.

        dependency_analyzer.py
            Deterministic repository dependency analysis.

        documenter.py
            AI-assisted description generation for pending active components.

        graph_projection.py
            Optional PostgreSQL-to-Neo4j graph projection.

        reconciler.py
            Read-only comparison of repository reality against registry state.

        registry.py
            Component registration operations.

        synchronizer.py
            Explicit bounded mutation of ComponentRegistry based on
            reconciliation results.
```

---

## Public Entry Points

Component Registry exposes Django management commands through the
framework-required command discovery surface:

```text
aurora/management/commands/
```

The command files are Django integration adapters.

Component Registry domain behavior belongs to:

```text
aurora/subsystems/component_registry/
```

### Reconciliation

Management command:

```text
reconcile_component_registry
```

Canonical preview:

```bash
daurora-cmd reconcile_component_registry
```

Supported synchronization operations include:

```text
archive
update
register
```

Mutation requires explicit `--apply`.

Registration requires an explicit user and a bounded path or limit.

Primary implementation:

```text
aurora/subsystems/component_registry/services/reconciler.py
aurora/subsystems/component_registry/services/synchronizer.py
```

### AI Documentation

Management command:

```text
document_component_registry
```

Canonical preview:

```bash
daurora-cmd document_component_registry
```

AI execution requires explicit `--apply`.

The documenter processes only:

```text
status = ACTIVE
analysis_status = PENDING
```

Primary implementation:

```text
aurora/subsystems/component_registry/services/documenter.py
```

### Registry Reset

Management command:

```text
reset_component_registry
```

This command is a Component Registry administrative entry point.

Its exact mutation semantics and safety boundaries must be established from:

```text
aurora/management/commands/reset_component_registry.py
```

before use.

**Knowledge State:** UNKNOWN

Do not infer reset behavior from the command name alone.

---

## Deterministic Reconciliation Lifecycle

The expected reconciliation flow is:

```text
repository discovery
    ↓
component policy classification
    ↓
reconciliation preview
    ↓
explicit synchronization
```

Relevant classifications include:

```text
KEEP
UPDATE
REGISTER
ARCHIVE
EXCLUDE
REVIEW
```

Meaning:

```text
KEEP
    Repository and registry state already agree.

UPDATE
    Existing active or reactivated component requires metadata refresh.

REGISTER
    Repository component exists but has no registry record.

ARCHIVE
    Active registry component no longer exists in the repository.

EXCLUDE
    Repository policy explicitly excludes the artifact.

REVIEW
    Deterministic policy cannot confidently classify the artifact.
    No automatic registry mutation occurs.
```

`REVIEW` is an architectural signal, not a synchronization failure.

---

## AI Usage

AI is not used to decide whether a component exists or whether repository state
matches registry state.

Those responsibilities are deterministic.

AI is used only for bounded semantic enrichment of eligible Component Registry
records.

AI execution is delegated through Aurora's shared `MinionRunner`.

The current directive name used by the documenter is:

```text
component_registry_documenter
```

AI-generated descriptions are committed only when source-hash validation proves
that the source file still matches the registry state used to begin analysis.

---

## Dependencies

### Aurora

Component Registry depends on:

```text
aurora.subsystems.delta_directives
    Supplies the persistent directive used by the AI documenter.

aurora.minions.engine
    Supplies MinionRunner for AI description execution.
    This path is a known architectural marker pending the future
    orchestration-subsystem design.
```

### Core Logic

```text
core_logic.ai
    Supplies AI provider routing indirectly through MinionRunner.
```

### Django

```text
Django ORM
Django management commands
Django admin
```

### Optional External Dependency

```text
Neo4j / neomodel
```

Neo4j is optional.

Component Registry reconciliation, registration, archival, reactivation, and AI
description generation must remain usable independently of graph projection.

---

## Consumers

Known consumers include:

```text
Hansel
    Uses Component Registry as durable repository knowledge.

Planning
    Expected to use registry knowledge for repository-impact discovery,
    especially planned StepFile identification.

Future orchestration
    Expected to use registry and dependency information when determining
    implementation context and blast radius.

Humans / Wu
    Use registry metadata to identify repository assets without broad searches.
```

Consumers may query Component Registry information.

They do not own Component Registry lifecycle or synchronization policy.

---

## Framework Integration Surfaces

Some Aurora files must remain outside subsystem directories because Django
requires specific discovery locations.

These locations are integration surfaces, not domain ownership boundaries.

Component Registry currently uses:

```text
aurora/management/commands/reconcile_component_registry.py
aurora/management/commands/document_component_registry.py
aurora/management/commands/reset_component_registry.py
```

Hansel must not classify a framework-required location as an ownership
violation merely because it exists outside:

```text
aurora/subsystems/component_registry/
```

Instead, validation must determine whether the framework surface contains
domain behavior that should belong to the subsystem.

The preferred direction is:

```text
Django integration surface
    ↓
subsystem-owned implementation
```

rather than:

```text
Django integration surface
    ↓
domain behavior embedded in framework plumbing
```

---

## Validation Protocol

Component Registry changes require validation appropriate to the type of change.

### Before Moving or Removing an Asset

Identify consumers first.

Example pattern:

```bash
grep -RIn <old-path-or-symbol> aurora core_logic
```

The consumer map establishes the known blast radius before mutation.

### Tombstone Validation

After a path, module, symbol, command, or namespace is removed or renamed,
search for the obsolete reference.

Expected result:

```text
no live references
```

Historical migrations or deliberately retained historical artifacts may remain
when they accurately describe past repository state.

### Survival Validation

A move or refactor must prove that intended behavior survived.

Examples include:

```text
Django system check succeeds.
Management command remains discoverable.
Model remains registered in Django admin.
Database identity remains unchanged.
Existing records remain accessible.
Expected registry lifecycle transition still occurs.
```

The validation must prove the specific claim made by the change.

Do not create permanent implementation-specific tests merely to record a
one-time refactor when deterministic change validation can prove the mutation.

### Model Validation

When moving or changing Component Registry model ownership:

```bash
dmakemigrations --check
daurora-cmd check
```

Expected:

```text
No changes detected
System check identified no issues
```

Where appropriate, also verify:

```text
model.__module__
model._meta.app_label
model._meta.db_table
existing row count
```

### Reconciliation Validation

After repository restructuring:

```bash
daurora-cmd reconcile_component_registry
```

A structurally synchronized registry should have:

```text
UPDATE = 0
REGISTER = 0
ARCHIVE = 0
```

`EXCLUDE` may legitimately be nonzero.

`REVIEW` may remain nonzero only when unresolved architectural classification is
intentional.

### Documentation Validation

Preview:

```bash
daurora-cmd document_component_registry
```

When enrichment is complete:

```text
No pending components matched the boundary.
```

---

## Change Validation Principle

Hansel distinguishes three different proof layers:

```text
Structural validation
    Repository ownership and subsystem grammar.

Change-specific validation
    Consumer mapping, tombstone proof, identity proof, and survival proof.

Persistent regression tests
    Durable runtime or business behavior that must remain protected over time.
```

Not every implementation module requires a permanent mirrored test module.

Validation must be proportional to the architectural claim being made.

---

## Known Gaps

### REVIEW Classification

**State:** VERIFIED

Some repository artifacts may remain classified as `REVIEW` when deterministic
policy cannot establish whether they are durable engineering components.

A human architectural decision is required before changing policy or ownership.

### Dependency Visualization

**State:** PLANNED

Dependency analysis and graph projection exist, but visual dependency analysis
is not yet a normal Component Registry workflow.

Graph generation must remain optional and should be invoked only when relational
or visual dependency analysis provides decision value.

### Planning Integration

**State:** PLANNED

Planning contains models capable of recording planned and actual file impacts,
but the workflow for populating and consuming those relationships is not yet
complete.

Component Registry is expected to provide repository knowledge to that future
workflow.

### Orchestration Integration

**State:** PLANNED

Future orchestration is expected to consume Component Registry information when
determining implementation context, dependencies, and blast radius.

Component Registry itself must not become the orchestration engine.

---

## Deeper Contracts

No additional Component Registry contracts are currently authoritative.

Future specialized contracts should be created only when complexity justifies
them.

`HANSEL.md` remains the canonical discovery entry point.

---

## Hansel Rules for This Subsystem

A worker modifying Component Registry must:

1. begin with this contract;
2. identify the exact service or model that owns the behavior;
3. map consumers before moving or deleting repository assets;
4. preserve deterministic repository discovery and reconciliation;
5. keep AI enrichment separate from deterministic classification;
6. keep Neo4j projection optional;
7. perform tombstone validation after removal or rename;
8. perform survival validation appropriate to the mutation;
9. reconcile Component Registry after repository restructuring;
10. update this contract when ownership, entry points, lifecycle, or validation
    rules change.

---

## Next Hansel Breadcrumb

For deterministic repository classification:

```text
aurora/subsystems/component_registry/services/component_policy.py
```

For reconciliation behavior:

```text
aurora/subsystems/component_registry/services/reconciler.py
```

For registry mutation:

```text
aurora/subsystems/component_registry/services/synchronizer.py
```

For AI description generation:

```text
aurora/subsystems/component_registry/services/documenter.py
```

For the authoritative data model:

```text
aurora/subsystems/component_registry/models.py
```

For optional graph projection:

```text
aurora/subsystems/component_registry/services/graph_projection.py
aurora/subsystems/component_registry/nodes.py
```

For unresolved registry-reset semantics:

```text
aurora/management/commands/reset_component_registry.py
```

# ======================================================================
# END: COMPONENT_REGISTRY_HANSEL_CONTRACT
# ======================================================================

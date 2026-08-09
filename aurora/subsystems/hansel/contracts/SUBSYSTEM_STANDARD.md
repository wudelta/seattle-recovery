# ======================================================================
# FILE: aurora/subsystems/hansel/contracts/SUBSYSTEM_STANDARD.md
# START: HANSEL_SUBSYSTEM_STANDARD
# ======================================================================

# Hansel Subsystem Standard

## Purpose

Hansel defines the repository-owned discovery and validation protocol used to
make Aurora subsystems understandable to both humans and AI workers.

Hansel exists to eliminate repeated repository-wide searches for:

* ownership;
* runtime entry points;
* interfaces;
* dependencies;
* architectural decisions;
* validation requirements;
* known gaps;
* and the next authoritative source.

Hansel standardizes discovery and proof.

It does not require every subsystem to have the same implementation shape or
the same volume of documentation.

---

## Core Rule

Every recognized Aurora subsystem must expose one canonical Hansel entry point:

```text
<subsystem>/contracts/HANSEL.md
```

That file must exist when the subsystem is created.

It may contain `UNKNOWN`, `PLANNED`, or `DEFERRED` information during early
development, but it must never be blank.

`HANSEL.md` is the authoritative starting point for humans and AI entering an
unfamiliar subsystem.

---

## Canonical Subsystem Shape

Aurora subsystems are organized by ownership rather than by global Django file
type.

A subsystem may contain:

```text
<subsystem>/
    __init__.py

    contracts/
        HANSEL.md

    models.py
    admin.py

    api/
    services/

    <specialized layers>
```

Examples of legitimate specialized layers include:

```text
planning/io/
component_registry/nodes.py
```

A subsystem is not required to contain every optional layer.

A directory or module should exist only when it represents a real,
explainable responsibility.

---

## Required Hansel Contract

Every subsystem must contain:

```text
contracts/HANSEL.md
```

`HANSEL.md` must provide enough information to determine:

* why the subsystem exists;
* what it owns;
* what it explicitly does not own;
* where authoritative implementation surfaces live;
* how the subsystem is entered or invoked;
* what it depends on;
* what depends on it;
* where AI is used, when applicable;
* how changes are validated;
* what is known to be incomplete or uncertain;
* what deeper contracts exist;
* and where to go next.

---

## Required HANSEL.md Concerns

A canonical `HANSEL.md` should address the following concerns.

### Purpose

Defines why the subsystem exists and the durable capability it provides.

### Ownership Boundary

Defines:

* responsibilities owned by the subsystem;
* authoritative data or behavior;
* responsibilities explicitly excluded from the subsystem.

Ownership is based on lifecycle responsibility, not simply which code consumes
a component most often.

### Repository Map

Identifies the important local implementation surfaces and explains their roles.

Examples include:

```text
models.py
admin.py
api/
services/
contracts/
io/
nodes.py
```

The map should explain specialized layers rather than assuming their purpose is
obvious.

### Public Entry Points

Identifies supported ways the subsystem is invoked or accessed.

Examples include:

* Django API endpoints;
* management commands;
* browser events;
* service methods;
* shared Python interfaces;
* UI entry points.

### Dependencies

Identifies other Aurora subsystems, shared infrastructure, framework services,
and external dependencies required by the subsystem.

### Consumers

Identifies known subsystems, interfaces, workers, or workflows that consume the
capability.

Consumer knowledge is especially important for blast-radius analysis.

### AI Usage

When AI is involved, the contract must distinguish:

* deterministic behavior;
* AI-assisted behavior;
* directive or worker dependencies;
* provider responsibilities;
* validation boundaries around AI output.

If the subsystem does not use AI, this may be stated briefly.

### Framework Integration Surfaces

If framework requirements force files to live outside the owning subsystem,
those paths must be identified explicitly.

Examples include:

```text
aurora/models.py
aurora/admin.py
aurora/management/commands/
aurora/apps.py
aurora/routing.py
```

These locations are framework integration surfaces, not domain ownership
boundaries.

Hansel must not classify them as violations merely because they exist outside a
subsystem.

Instead, Hansel must determine whether they contain domain behavior that should
belong to the subsystem.

### Validation

Defines how changes to the subsystem are proven safe and complete.

Validation must be proportional to the architectural claim being made.

### Known Gaps

Records unresolved, deferred, planned, or intentionally incomplete behavior.

Unknown information must never be silently inferred.

### Deeper Contracts

Lists authoritative subsystem-specific contracts when additional detail is
required.

Examples include:

```text
SECURITY.md
DATA_MODEL.md
MIGRATION_PLAN.md
TECHNICAL_DEBT.md
PLANNING_DICTIONARY_GENERATION.md
```

Deeper contracts are complexity-driven.

They are not mandatory simply for structural uniformity.

### Next Hansel Breadcrumb

Identifies the narrowest authoritative next source for continued discovery.

---

## Knowledge States

Hansel uses the following knowledge states:

```text
VERIFIED
PLANNED
UNKNOWN
DEFERRED
DEPRECATED
```

These states should be applied where uncertainty or lifecycle state matters.

Hansel does not require every sentence to carry a state label.

Instead, sections, gaps, decisions, or individual claims should be marked when
their status would otherwise be ambiguous.

---

## Evidence Rule

Hansel must never present assumptions as verified facts.

When verified knowledge ends:

1. stop inference;
2. record the unknown;
3. identify the narrowest authoritative breadcrumb capable of resolving it;
4. continue discovery only from that authority.

Every `UNKNOWN` must identify an actionable next breadcrumb.

Vague unknowns are not compliant.

---

## Ownership Rule

Subsystem ownership should be visible from repository structure.

When a subsystem owns a capability, implementation should normally live under:

```text
aurora/subsystems/<owner>/
```

Examples include:

```text
models.py
admin.py
api/
services/
contracts/
static assets
templates
specialized domain layers
```

Shared infrastructure may remain outside individual subsystems when no single
subsystem owns its lifecycle.

Framework-mandated paths are governed by the Framework Integration Surface rule.

---

## Framework Integration Surface Rule

Some files must remain in framework-defined locations.

The preferred dependency direction is:

```text
framework integration surface
    ↓
subsystem-owned implementation
```

Avoid:

```text
framework integration surface
    ↓
substantial domain behavior embedded in framework plumbing
```

Hansel validators must distinguish legitimate integration surfaces from
unowned domain logic.

---

## Directory Responsibility Rule

Every subsystem directory must represent an explainable responsibility.

Hansel distinguishes:

```text
ABSENT
    The subsystem does not declare this layer.

EMPTY
    The layer exists but currently contains no meaningful implementation.

POPULATED
    The layer contains concrete responsibility.
```

An empty directory is not automatically invalid.

It may represent:

* planned architecture;
* abandoned scaffolding;
* an incomplete migration;
* or a deliberately reserved extension point.

Its state must be understandable from `HANSEL.md` or another authoritative
contract.

Unexplained empty structure is an architectural review signal.

---

## Deeper Contract Rule

Only `contracts/HANSEL.md` is universally required.

Additional contracts are created when subsystem complexity justifies them.

Hansel standardizes the discovery path, not documentation volume.

A simple subsystem may require only a compact `HANSEL.md`.

A complex subsystem may route from `HANSEL.md` into several deeper contracts.

`HANSEL.md` must remain the canonical starting point.

---

## Change Validation Protocol

Hansel requires proof appropriate to the type of architectural change.

The standard change workflow is:

```text
DISCOVER
    ↓
CLASSIFY
    ↓
CHANGE
    ↓
TOMBSTONE
    ↓
SURVIVAL
    ↓
RECONCILE
    ↓
COMMIT
```

---

## Discover

Before mutation:

* identify the asset;
* identify its current owner;
* identify consumers;
* identify framework or runtime dependencies;
* identify the authoritative contract governing the change.

Consumer mapping establishes the known blast radius.

Repository-wide search is appropriate during discovery when ownership is not
yet established.

Once an authority is identified, prefer narrower Hansel breadcrumbs.

---

## Classify

Classify the intended architectural action as one of:

```text
KEEP
MOVE
REFACTOR
DELETE
DEFER
ARCHITECTURAL_REVIEW
```

`ARCHITECTURAL_REVIEW` is appropriate when an asset does not fit the current
repository grammar and automation cannot safely decide its future owner.

Hansel must surface ambiguity rather than silently normalize it.

---

## Change

Perform the smallest complete ownership-safe mutation.

Prefer:

* complete anchored replacement units;
* deterministic filesystem moves;
* bounded command operations;
* explicit ownership-preserving changes.

Avoid partial edits whose correctness depends on manual reconstruction.

---

## Tombstone Validation

After deleting, moving, or renaming an asset, verify that obsolete references no
longer exist.

Examples include searching for:

* old module paths;
* old import paths;
* old filenames;
* old command names;
* old symbols;
* obsolete namespaces.

Expected result:

```text
no live references
```

Historical migrations and deliberately preserved historical planning artifacts
may retain obsolete terminology when they accurately describe past state.

Those cases must be distinguishable from live dependencies.

---

## Survival Validation

A move or refactor must prove that intended behavior or identity survived.

Examples include:

```text
Django system check succeeds.
No schema migration is introduced by a source-only model move.
Database table identity remains unchanged.
Existing data remains accessible.
Django admin registration survives relocation.
Management commands remain discoverable.
Expected API or UI behavior remains intact.
```

Survival validation must test the claim made by the change.

Do not substitute generic test execution for specific architectural proof.

---

## Reconciliation Validation

When repository structure changes, repository-owned metadata must be reconciled.

For Aurora Component Registry this currently includes:

```text
reconcile_component_registry
document_component_registry
```

Structural reconciliation and semantic AI enrichment are separate operations.

Repository metadata must not be assumed current merely because source code
passes framework checks.

---

## Validation Layers

Hansel distinguishes three validation layers.

### Structural Validation

Validates:

* subsystem grammar;
* ownership;
* required Hansel contracts;
* declared repository structure;
* framework integration boundaries.

### Change-Specific Validation

Validates the particular mutation using evidence such as:

* consumer mapping;
* tombstone searches;
* identity checks;
* survival checks;
* bounded reconciliation.

These checks may be temporary and need not become permanent test modules.

### Persistent Regression Tests

Protect durable runtime, business, security, or data behavior that must remain
valid across future implementation changes.

Persistent tests should protect meaningful invariants.

They should not mechanically mirror every implementation module.

---

## Testing Principle

Hansel does not require one test file per implementation module.

Testing strategy must reflect the kind of invariant being protected.

A one-time source relocation may require deterministic change validation but no
permanent regression test.

A durable business rule, security boundary, or runtime contract may require a
persistent automated regression test.

The existence of a source module alone is not sufficient reason to create a
mirrored test module.

---

## AI and Determinism Rule

When deterministic logic can establish a fact, deterministic logic should own
that decision.

AI may assist where semantic interpretation is required.

Hansel contracts must clearly identify which decisions are deterministic and
which depend on AI.

AI output must not silently replace deterministic validation.

---

## Update Rule

Architecture work is incomplete until affected Hansel contracts reflect the new
ownership, interfaces, dependencies, lifecycle, validation, or breadcrumbs.

Do not update unrelated contracts merely for documentation symmetry.

---

## Anchor Rule

Hansel contracts use complete anchored replacement regions with matching:

```text
FILE
START
END
```

The safest patch is the smallest complete architectural replacement unit.

For a canonical `HANSEL.md`, a complete-file anchored replacement is preferred
when broad contract structure changes.

---

## Validator Responsibilities

Hansel deterministic validators are expected to develop around three primary
responsibilities.

### subsystem_structure.py

Validates repository grammar, including:

* recognized subsystem structure;
* local ownership patterns;
* suspicious empty directories;
* specialized layers declared by contract;
* unexplained out-of-subsystem implementation.

### hansel_contract.py

Validates:

* presence of `contracts/HANSEL.md`;
* required contract concerns;
* valid knowledge-state usage;
* actionable breadcrumbs for `UNKNOWN` items;
* referenced repository paths where deterministic validation is possible.

### dependency_boundary.py

Validates declared ownership and dependency boundaries where they can be proven
from repository evidence.

The validator must surface uncertain architecture for human review rather than
invent ownership decisions.

---

## Success Condition

Hansel succeeds when a new human or AI can determine:

* where to begin;
* what owns the behavior;
* what the subsystem does not own;
* how it executes;
* what it depends on;
* who consumes it;
* what can be safely changed;
* what evidence is required after a change;
* and where to go next;

without another repository-wide snipe hunt.

Hansel is successful when repository anomalies become visible because the normal
architecture is understandable at a glance.

---

## Next Hansel Breadcrumb

Create and refine canonical subsystem discovery contracts at:

```text
aurora/subsystems/<subsystem>/contracts/HANSEL.md
```

Use the first validated reference implementation:

```text
aurora/subsystems/component_registry/contracts/HANSEL.md
```

Then implement deterministic contract validation beginning with:

```text
aurora/subsystems/hansel/validators/hansel_contract.py
```

# ======================================================================
# END: HANSEL_SUBSYSTEM_STANDARD
# ======================================================================

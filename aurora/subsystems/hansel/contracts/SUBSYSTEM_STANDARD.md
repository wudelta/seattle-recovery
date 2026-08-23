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

## Repository-Wide Adoption and Governance

Hansel is mandatory repository infrastructure for every recognized Aurora
subsystem.

Every subsystem must maintain one canonical entry point:

```text
aurora/subsystems/<subsystem>/contracts/HANSEL.md
```

New subsystems must be created through the canonical subsystem-generation
workflow when that workflow can represent the required subsystem shape.

Existing subsystems must remain discoverable through their canonical
`HANSEL.md` as their implementation evolves.

### Worker Entry Rule

When a task belongs to a known subsystem, humans and AI workers should enter
through that subsystem's canonical `HANSEL.md`.

Do not begin with repository-wide discovery when a durable Hansel route already
exists.

Follow only the breadcrumbs required to establish sufficient authority:

1. who owns the behavior;
2. what must change;
3. what must remain unchanged;
4. how the change will be validated.

Repository-wide discovery remains appropriate when ownership is genuinely
unknown or when validating repository-wide governance itself.

### Catalogue Scope Rule

A Hansel catalogue is an index, not an encyclopedia.

It should preserve the smallest durable breadcrumbs necessary to reach
authoritative implementation, contracts, validation, and deeper knowledge.

Do not duplicate implementation detail merely to make a catalogue appear
complete.

Do not add breadcrumbs for incidental files that workers do not need in order
to reach sufficient authority.

### Structural and Semantic Validity

Deterministic Hansel validation proves structural contract integrity.

Structural validity may include:

```text
canonical contract presence
contract identity
valid knowledge states
actionable UNKNOWN breadcrumbs
existence of declared repository authorities
```

Structural validity does not prove that catalogue knowledge is current.

A contract may be structurally valid while containing stale descriptions of
ownership, implementation, lifecycle, or available authorities.

Semantic reconciliation therefore remains a separate engineering
responsibility.

### Reconciliation Rule

When implementation changes invalidate or create a durable breadcrumb, the
owning subsystem's Hansel catalogue must be reconciled.

A stale but structurally valid breadcrumb is a Hansel defect.

Reconciliation should:

1. inspect current repository evidence;
2. replace stale knowledge with the smallest durable current authority;
3. preserve valid ownership boundaries;
4. preserve genuinely `UNKNOWN`, `PLANNED`, or `DEFERRED` knowledge rather than
   guessing;
5. rerun deterministic validation after the change.

Do not rewrite unrelated catalogue sections merely because reconciliation is
being performed.

### Repository Audit Rule

Repository-wide Hansel validation is appropriate after:

* changes to Hansel validators or contract semantics;
* subsystem-generation or scaffold changes;
* repository-wide ownership migrations;
* discovery of a defect that may affect multiple subsystem catalogues;
* or explicit Hansel governance work.

A repository-wide audit has two distinct passes:

```text
deterministic structural validation
    ↓
bounded semantic stale-knowledge review
```

Passing deterministic validation does not eliminate the semantic review when
the purpose of the audit is governance or knowledge reconciliation.

### Defect Handling

Broken declared breadcrumbs are defects and must not be silently ignored.

Historical or explanatory repository paths are not declared authorities merely
because they resemble repository paths.

Deterministic validators should validate explicit contract declarations and
must avoid converting incidental prose into architectural claims.

When deterministic validation cannot establish semantic correctness, surface
the uncertainty for bounded human or AI review rather than inventing an
answer.

### Adoption Baseline

Repository-wide adoption is established when:

1. every recognized subsystem has a canonical non-blank `contracts/HANSEL.md`;
2. all canonical contracts pass deterministic Hansel validation;
3. known stale catalogue knowledge discovered during adoption has been
   reconciled;
4. unresolved knowledge is explicitly represented rather than inferred;
5. new subsystem creation preserves the canonical Hansel entry point.

Once this baseline is established, Hansel maintenance becomes part of normal
engineering work rather than a separate documentation project.

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

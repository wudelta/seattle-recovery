# ======================================================================
# FILE: aurora/subsystems/hansel/contracts/HANSEL.md
# START: HANSEL_HANSEL_CONTRACT
# ======================================================================

# Hansel — Hansel Contract

**Knowledge State:** VERIFIED
**Subsystem:** `hansel`

---

## Purpose

Hansel defines Aurora's repository-owned discovery, ownership, and
change-validation protocol.

Its purpose is to make the repository understandable to humans and AI workers
without requiring repeated repository-wide searches, institutional memory, or
large static context prompts.

Hansel establishes the grammar by which Aurora subsystems describe:

* what they own;
* what they do not own;
* where authoritative implementation lives;
* what they depend on;
* who consumes them;
* how changes are validated;
* what remains unknown;
* and where discovery should continue next.

Hansel also defines deterministic checks that can eventually prove whether
repository structure and subsystem contracts conform to that grammar.

---

## Ownership Boundary

Hansel owns:

* the canonical subsystem-discovery protocol;
* the requirement for `contracts/HANSEL.md`;
* subsystem discovery grammar;
* Hansel knowledge-state semantics;
* breadcrumb rules;
* ownership-discovery rules;
* framework-integration exceptions;
* deterministic structural validation rules;
* tombstone-validation requirements;
* survival-validation requirements;
* dependency-boundary validation;
* subsystem-contract validation;
* Hansel templates when implemented.

Hansel does not own:

* Planning hierarchy or work state;
* repository component inventory;
* Component Registry lifecycle;
* AI provider execution;
* worker directive configuration;
* Wu Chat interaction state;
* source-code mutation;
* orchestration of Initiative execution;
* subsystem domain behavior;
* generic project documentation.

Hansel describes and validates architecture.

It does not become the implementation owner of every capability it documents.

---

## Canonical Authority

The authoritative Hansel subsystem standard is:

```text
aurora/subsystems/hansel/contracts/SUBSYSTEM_STANDARD.md
```

Every recognized subsystem must expose:

```text
<subsystem>/contracts/HANSEL.md
```

as its canonical discovery entry point.

Hansel itself follows this rule recursively through:

```text
aurora/subsystems/hansel/contracts/HANSEL.md
```

---

## Repository Map

```text
hansel/
    contracts/
        HANSEL.md
            Canonical discovery entry point for Hansel itself.

        SUBSYSTEM_STANDARD.md
            Authoritative protocol defining Hansel subsystem grammar,
            discovery requirements, and validation principles.

    validators/
        subsystem_structure.py
            Intended deterministic validation of repository structure,
            subsystem ownership patterns, and structural anomalies.

        hansel_contract.py
            Intended deterministic validation of canonical HANSEL.md
            contracts and required discovery concerns.

        dependency_boundary.py
            Intended deterministic validation of declared dependency and
            ownership boundaries.

    templates/
        subsystem_contracts/
            Reserved location for canonical Hansel contract templates.
```

---

## Current Implementation State

Hansel currently consists primarily of:

```text
authoritative contracts
+
validator shells
+
reserved template structure
```

The protocol is materially defined.

The validators and templates are not yet fully implemented.

Hansel is therefore transitioning from:

```text
philosophy
    ↓
repository convention
    ↓
formal protocol
    ↓
deterministically validated engineering grammar
```

---

## Public Entry Points

Hansel currently exposes no verified runtime API, Django model, or management
command.

**Knowledge State:** VERIFIED

The current authoritative entry points are repository contracts.

### Hansel Discovery Entry Point

```text
aurora/subsystems/hansel/contracts/HANSEL.md
```

### Subsystem Standard

```text
aurora/subsystems/hansel/contracts/SUBSYSTEM_STANDARD.md
```

### Future Structural Validators

```text
aurora/subsystems/hansel/validators/
```

No command-line or orchestration integration should be inferred until one is
implemented and documented.

---

## Hansel Discovery Model

Hansel expects a worker entering an unfamiliar subsystem to follow:

```text
repository
    ↓
subsystem/contracts/HANSEL.md
    ↓
specific deeper contract
    ↓
specific implementation authority
    ↓
deterministic validation
```

The worker should not begin by loading an entire subsystem indiscriminately when
the Hansel contract provides a narrower authority.

Repository-wide searches remain legitimate during initial discovery when
ownership is not yet established.

Once an authority is known, narrower breadcrumbs should be preferred.

---

## Knowledge States

Hansel recognizes:

```text
VERIFIED
PLANNED
UNKNOWN
DEFERRED
DEPRECATED
```

These states prevent uncertain architectural information from being presented
as established fact.

An `UNKNOWN` must identify an actionable next breadcrumb.

Hansel does not require every sentence to carry a knowledge-state label.

Knowledge states are used where uncertainty, lifecycle, or authority would
otherwise be ambiguous.

---

## Change Validation Protocol

Hansel defines the canonical architectural-change workflow:

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

### Discover

Before mutation:

* identify the asset;
* identify current ownership;
* identify consumers;
* identify framework/runtime dependencies;
* identify the authoritative contract.

### Classify

Classify the intended action as:

```text
KEEP
MOVE
REFACTOR
DELETE
DEFER
ARCHITECTURAL_REVIEW
```

### Change

Perform the smallest complete ownership-safe mutation.

### Tombstone

After a rename, move, or deletion, prove obsolete references no longer exist.

### Survival

Prove the intended behavior or identity survived the mutation.

### Reconcile

Update repository-owned metadata and affected Hansel contracts.

### Commit

Commit only after required deterministic evidence is clean.

---

## Validation Layers

Hansel distinguishes three different validation responsibilities.

### Structural Validation

Validates:

* repository grammar;
* subsystem ownership;
* required Hansel contracts;
* framework integration exceptions;
* unexplained structural anomalies.

### Change-Specific Validation

Validates the mutation being performed.

Examples include:

```text
consumer mapping
tombstone searches
Django identity checks
admin-registration checks
management-command discovery
row-count preservation
UI survival checks
bounded reconciliation
```

These checks may be temporary.

They do not automatically require permanent test modules.

### Persistent Regression Tests

Protect durable behavior that must survive future implementation changes.

Examples include:

```text
business rules
security boundaries
parser contracts
data integrity
critical runtime workflows
```

Hansel does not require one mirrored test file for every implementation module.

---

## Framework Integration Surfaces

Hansel recognizes that framework requirements may legitimately place files
outside their subsystem owner.

Known Aurora examples include:

```text
aurora/models.py
aurora/admin.py
aurora/apps.py
aurora/routing.py
aurora/management/commands/
aurora/static/
aurora/templates/
```

Hansel must distinguish:

```text
framework-required physical location
```

from:

```text
domain ownership
```

The preferred direction remains:

```text
framework integration surface
    ↓
subsystem-owned implementation
```

Framework exceptions must not become excuses for embedding unrelated domain
behavior in global files.

---

## Dependencies

### Repository Structure

Hansel depends on the repository itself as evidence.

Directory layout, file paths, imports, framework surfaces, and contracts are all
inputs to Hansel discovery and validation.

### Component Registry

Hansel and Component Registry are complementary.

Component Registry provides durable repository component metadata.

Hansel provides architectural ownership, discovery contracts, and protocol
rules.

Expected relationship:

```text
Hansel
    explains repository meaning and ownership

Component Registry
    records repository component facts
```

Neither should silently absorb the other's responsibility.

### Future Orchestration

Future orchestration is expected to consume Hansel contracts when determining:

* subsystem ownership;
* required context;
* validation obligations;
* next authoritative breadcrumbs.

Hansel informs orchestration.

Hansel does not itself orchestrate Initiative execution.

---

## Consumers

Known consumers include:

```text
Humans
    Use Hansel to understand repository ownership and safe change paths.

Wu
    Uses Hansel to locate task-specific authoritative context.

Component Registry work
    Uses Hansel ownership rules during repository cleanup and classification.

Planning
    Uses Hansel context when engineering work crosses subsystem boundaries.

Future orchestration
    Expected to use Hansel contracts and validators to constrain execution.
```

Hansel's ultimate consumer is any engineering worker that needs to make a safe
repository change without loading or rediscovering the entire codebase.

---

## AI Usage

Hansel's core rules should remain deterministic wherever repository facts can be
established deterministically.

AI may assist with:

* interpreting architectural intent;
* drafting HANSEL.md contracts;
* identifying potential anomalies;
* proposing ownership classifications;
* reasoning about unresolved architecture.

AI must not silently decide:

* whether a file exists;
* whether a reference remains;
* whether a model identity changed;
* whether a command is still registered;
* whether deterministic repository structure conforms to declared rules.

Those facts should be validated deterministically.

---

## Validator Responsibilities

### subsystem_structure.py

Intended authority:

```text
aurora/subsystems/hansel/validators/subsystem_structure.py
```

Expected responsibilities include:

* enumerate recognized subsystems;
* verify required `contracts/HANSEL.md`;
* identify local model/admin/service/API ownership patterns;
* identify suspicious empty directories;
* recognize declared specialized layers;
* identify unexplained implementation outside subsystem ownership;
* recognize legitimate framework integration surfaces.

**State:** PLANNED

---

### hansel_contract.py

Intended authority:

```text
aurora/subsystems/hansel/validators/hansel_contract.py
```

Expected responsibilities include:

* verify `HANSEL.md` existence;
* verify required discovery concerns;
* identify blank or incomplete contracts;
* validate knowledge-state usage where deterministic;
* verify actionable breadcrumbs for declared unknowns;
* validate referenced repository paths where possible.

**State:** PLANNED

---

### dependency_boundary.py

Intended authority:

```text
aurora/subsystems/hansel/validators/dependency_boundary.py
```

Expected responsibilities include:

* compare declared dependencies with repository evidence;
* surface undeclared cross-subsystem imports;
* identify ownership-boundary violations where deterministic evidence is
  sufficient;
* escalate ambiguous ownership to architectural review.

**State:** PLANNED

The validator must never invent ownership simply to produce a clean result.

---

## Templates

Reserved template location:

```text
aurora/subsystems/hansel/templates/subsystem_contracts/
```

Current contents contain no implemented contract templates beyond package
structure.

**State:** EMPTY

The old Hansel standard proposed a mandatory collection of separate subsystem
contract templates.

That design has been superseded by the current rule:

```text
contracts/HANSEL.md
    required

deeper contracts
    complexity-driven
```

Therefore template implementation should not recreate the obsolete seven-file
mandatory contract structure.

Future templates should reflect the current `SUBSYSTEM_STANDARD.md`.

---

## Known Gaps

### Validator Implementation

**State:** PLANNED

The validator modules exist as architectural shells but deterministic validation
logic is not yet established.

Next breadcrumb:

```text
aurora/subsystems/hansel/contracts/SUBSYSTEM_STANDARD.md
```

and then:

```text
aurora/subsystems/hansel/validators/hansel_contract.py
```

---

### Template Implementation

**State:** PLANNED

The template hierarchy exists but canonical templates are not yet implemented.

Next breadcrumb:

```text
aurora/subsystems/hansel/contracts/SUBSYSTEM_STANDARD.md
```

Do not generate templates from the obsolete pre-vNext subsystem standard.

---

### Repository-Wide Hansel Compliance

**State:** PLANNED

Canonical `HANSEL.md` files are being established across Aurora subsystems.

Full deterministic compliance has not yet been proven.

Next breadcrumb:

```text
aurora/subsystems/*/contracts/HANSEL.md
```

followed by implementation of:

```text
validators/hansel_contract.py
validators/subsystem_structure.py
```

---

### Orchestration Integration

**State:** PLANNED

Future orchestration is expected to use Hansel to determine:

```text
what owns the work
what context is required
what dependencies matter
what validation obligations apply
where to go next
```

The orchestration subsystem does not yet exist.

Current architectural marker:

```text
aurora/minions/engine.py
```

Hansel should inform that future subsystem but must not become the orchestration
engine itself.

---

## Deeper Contracts

### Hansel Subsystem Standard

Authoritative protocol:

```text
aurora/subsystems/hansel/contracts/SUBSYSTEM_STANDARD.md
```

Use this contract when:

* creating a subsystem;
* creating or updating `HANSEL.md`;
* evaluating subsystem structure;
* designing structural validators;
* determining framework exceptions;
* defining architectural change validation.

---

## Hansel Rules for This Subsystem

A worker modifying Hansel must:

1. begin with this contract;
2. treat `SUBSYSTEM_STANDARD.md` as the authoritative protocol definition;
3. preserve `contracts/HANSEL.md` as the canonical subsystem entry point;
4. prefer deterministic evidence over AI inference;
5. distinguish structural validation, change-specific validation, and
   persistent regression testing;
6. distinguish framework integration surfaces from ownership violations;
7. surface architectural ambiguity rather than inventing ownership;
8. avoid mandatory documentation volume that does not serve discovery;
9. avoid empty scaffolding without an explainable planned responsibility;
10. ensure validators follow the protocol rather than redefine it;
11. update this contract when Hansel's ownership, validator responsibilities,
    or discovery grammar changes.

---

## Next Hansel Breadcrumb

For the authoritative subsystem protocol:

```text
aurora/subsystems/hansel/contracts/SUBSYSTEM_STANDARD.md
```

For future contract validation:

```text
aurora/subsystems/hansel/validators/hansel_contract.py
```

For future structural validation:

```text
aurora/subsystems/hansel/validators/subsystem_structure.py
```

For future dependency-boundary validation:

```text
aurora/subsystems/hansel/validators/dependency_boundary.py
```

For future canonical templates:

```text
aurora/subsystems/hansel/templates/subsystem_contracts/
```

For the current orchestration architectural marker:

```text
aurora/minions/engine.py
```

# ======================================================================
# END: HANSEL_HANSEL_CONTRACT
# ======================================================================

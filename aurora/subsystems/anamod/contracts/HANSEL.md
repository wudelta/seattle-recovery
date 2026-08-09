# ======================================================================
# FILE: aurora/subsystems/anamod/contracts/HANSEL.md
# START: ANAMOD_HANSEL_CONTRACT
# ======================================================================

# Anamod — Hansel Contract

**Knowledge State:** VERIFIED
**Subsystem:** `anamod`

---

## Purpose

Anamod provides Aurora's repository editor and workspace-oriented development
capabilities.

Its current implemented responsibilities center on IDE operations and bounded
workspace/file services.

Anamod is undergoing architectural migration.

Its present directory structure contains both implemented responsibilities and
reserved or incomplete layers.

---

## Ownership Boundary

Anamod owns:

* repository editor operations specific to Anamod;
* bounded workspace/file operations used by the editor;
* Anamod-specific API behavior;
* future Anamod editor behavior;
* future Anamod UI behavior;
* Anamod migration and technical-debt documentation.

Anamod does not own:

* general repository component discovery;
* Component Registry state;
* Hansel repository grammar;
* Planning state;
* AI provider execution;
* Wu Chat code-review workflow;
* general Initiative orchestration;
* Django-wide static or template infrastructure.

---

## Current Implementation State

The currently populated implementation surfaces are:

```text id="ahj4ln"
api/ide_operations.py
services/workspace_service.py
```

Several additional directories exist but contain no implementation beyond
package markers or are completely empty.

These directories must not be treated as implemented capabilities merely
because they exist.

---

## Repository Map

```text id="3vdav5"
anamod/
    api/
        ide_operations.py
            Implemented Anamod IDE operation API behavior.

    services/
        workspace_service.py
            Implemented workspace/file service behavior.

    contracts/
        HANSEL.md
            Canonical Hansel discovery entry point.

        MIGRATION_PLAN.md
            Existing migration planning contract.

        SUBSYSTEM.md
            Pre-Hansel subsystem documentation.

        TECHNICAL_DEBT.md
            Known technical debt and unresolved Anamod concerns.

    docs/
        Empty directory.

    editor/
        __init__.py only.

    ui/
        __init__.py only.

    workspace/
        __init__.py only.
```

---

## Directory Classification

Hansel classifies the current Anamod structure as follows.

### API

```text id="nbu6md"
anamod/api/
```

**State:** POPULATED

Implemented authority:

```text id="10pqg4"
aurora/subsystems/anamod/api/ide_operations.py
```

---

### Services

```text id="78d4m5"
anamod/services/
```

**State:** POPULATED

Implemented authority:

```text id="9qqz3i"
aurora/subsystems/anamod/services/workspace_service.py
```

---

### Editor

```text id="s1dwzn"
anamod/editor/
```

**State:** EMPTY

The directory currently contains only:

```text id="3j0c4u"
__init__.py
```

No editor implementation responsibility is proven by current repository
contents.

Whether this directory represents planned architecture, unfinished migration, or
stale scaffolding must be established from deeper Anamod contracts.

---

### UI

```text id="z9nh6o"
anamod/ui/
```

**State:** EMPTY

The directory currently contains only:

```text id="1e6dyg"
__init__.py
```

No Anamod UI implementation responsibility is proven by current repository
contents.

---

### Workspace

```text id="7l9g8j"
anamod/workspace/
```

**State:** EMPTY

The directory currently contains only:

```text id="1u94l3"
__init__.py
```

Workspace behavior currently exists instead in:

```text id="tnmm1p"
aurora/subsystems/anamod/services/workspace_service.py
```

The reason for retaining a separate empty `workspace/` package is not
established by this contract.

---

### Docs

```text id="h0fcsg"
anamod/docs/
```

**State:** EMPTY

No current documentation responsibility is represented by files in this
directory.

Anamod architectural documentation currently resides under:

```text id="91yjbd"
anamod/contracts/
```

---

## Public Entry Points

Primary Anamod API implementation:

```text id="g7dboc"
aurora/subsystems/anamod/api/ide_operations.py
```

Primary workspace service:

```text id="bx9s6a"
aurora/subsystems/anamod/services/workspace_service.py
```

Additional runtime entry points are not established by this contract.

**Knowledge State:** UNKNOWN

Next breadcrumb:

```text id="rz9jd0"
aurora/subsystems/anamod/api/ide_operations.py
```

and consumer mapping for that module.

---

## Workspace Service

Current workspace/file implementation authority:

```text id="q58s9u"
aurora/subsystems/anamod/services/workspace_service.py
```

The service belongs to Anamod because it supports Anamod's repository editing
and IDE workflow.

This does not make Anamod the owner of all repository discovery or repository
knowledge.

Repository knowledge belongs to Hansel and Component Registry according to their
respective contracts.

---

## AI Usage

No Anamod-owned AI execution behavior is established by the current subsystem
tree.

**Knowledge State:** UNKNOWN

Do not infer AI behavior from Anamod's role as a development tool.

Next breadcrumb:

```text id="mh8d6c"
aurora/subsystems/anamod/api/ide_operations.py
aurora/subsystems/anamod/services/workspace_service.py
```

---

## Dependencies

Exact runtime dependencies are not established from the subsystem tree alone.

**Knowledge State:** UNKNOWN

Next breadcrumbs:

```text id="7jj0p3"
aurora/subsystems/anamod/api/ide_operations.py
aurora/subsystems/anamod/services/workspace_service.py
```

Existing migration and technical-debt contracts may provide additional
architectural context:

```text id="wbztgl"
aurora/subsystems/anamod/contracts/MIGRATION_PLAN.md
aurora/subsystems/anamod/contracts/TECHNICAL_DEBT.md
```

---

## Consumers

Exact current consumers of Anamod API and workspace services are not established
by this contract.

**Knowledge State:** UNKNOWN

Consumer discovery should begin with:

```text id="3nddfu"
aurora.subsystems.anamod
ide_operations
workspace_service
```

Search only as broadly as necessary to establish the current consumer map.

---

## Framework Integration Surfaces

No specific Django-mandated Anamod integration surface is established by this
contract.

**Knowledge State:** UNKNOWN

Do not invent one from subsystem naming or historical architecture.

Consumer discovery of:

```text id="g4uj5m"
api/ide_operations.py
services/workspace_service.py
```

should establish actual integration points.

---

## Validation Protocol

### Consumer Mapping

Before moving, renaming, consolidating, or deleting Anamod assets, identify
consumers first.

Example:

```bash id="qcm5mm"
grep -RIn <old-path-or-symbol> aurora core_logic
```

This is especially important while Anamod remains in migration because directory
shape alone cannot establish active runtime use.

---

### Tombstone Validation

After moving, deleting, or renaming an Anamod asset, verify obsolete references
are gone.

Expected:

```text id="rhtnb6"
no live references
```

This includes obsolete:

* module paths;
* imports;
* filenames;
* service names;
* API symbols;
* historical workspace namespaces.

---

### Survival Validation

An Anamod move or refactor must prove the affected capability survived.

Depending on the change, evidence may include:

```text id="30vnfe"
Django system check succeeds.
Existing consumers import the new authority.
IDE operations still execute.
Workspace file reads still succeed.
Workspace file writes remain bounded and safe.
Expected editor behavior remains functional.
```

The validation must correspond to the actual changed responsibility.

---

### Empty Directory Validation

Before removing an empty architectural layer:

1. inspect deeper Anamod contracts;
2. map consumers of the namespace;
3. determine whether the directory represents active planned architecture;
4. remove only when no current or intentionally reserved responsibility remains;
5. perform tombstone validation afterward.

An empty directory is an architectural question, not automatic permission to
delete it.

---

## Existing Contract Authority

Anamod contains documentation created before the canonical Hansel contract
standard.

Those files must not silently compete with `HANSEL.md`.

### HANSEL.md

```text id="yp48nv"
contracts/HANSEL.md
```

Canonical discovery entry point.

This file owns the current subsystem map and routes workers toward deeper
authority.

---

### MIGRATION_PLAN.md

```text id="ejtfq5"
contracts/MIGRATION_PLAN.md
```

Deeper authority for Anamod migration planning where its contents remain
current.

---

### TECHNICAL_DEBT.md

```text id="1tk1b0"
contracts/TECHNICAL_DEBT.md
```

Deeper authority for known Anamod technical debt and unresolved implementation
concerns.

---

### SUBSYSTEM.md

```text id="y6fs1n"
contracts/SUBSYSTEM.md
```

**State:** DEPRECATED AS ENTRY POINT

This file predates the canonical Hansel `HANSEL.md` standard.

Its contents may still contain useful architectural evidence, but workers must
begin with `HANSEL.md`.

`SUBSYSTEM.md` should eventually be:

```text id="a2d7fp"
reviewed
    ↓
useful knowledge migrated or linked
    ↓
tombstoned if no unique authority remains
```

Do not delete it until its unique information has been evaluated.

---

## Known Gaps

### Empty Editor Layer

**State:** UNKNOWN

```text id="5r73pz"
aurora/subsystems/anamod/editor/
```

contains no implemented editor behavior.

Next breadcrumb:

```text id="jy5gfn"
contracts/MIGRATION_PLAN.md
contracts/TECHNICAL_DEBT.md
contracts/SUBSYSTEM.md
```

---

### Empty UI Layer

**State:** UNKNOWN

```text id="esxdbo"
aurora/subsystems/anamod/ui/
```

contains no implemented UI behavior.

Next breadcrumb:

```text id="nx02uf"
contracts/MIGRATION_PLAN.md
contracts/TECHNICAL_DEBT.md
contracts/SUBSYSTEM.md
```

---

### Empty Workspace Layer

**State:** UNKNOWN

```text id="fjv2f3"
aurora/subsystems/anamod/workspace/
```

contains no implemented workspace behavior.

Current workspace implementation exists in:

```text id="3m7oxf"
services/workspace_service.py
```

Next breadcrumb:

```text id="c86hn7"
contracts/MIGRATION_PLAN.md
contracts/TECHNICAL_DEBT.md
contracts/SUBSYSTEM.md
```

---

### Empty Docs Layer

**State:** UNKNOWN

```text id="9bmfs3"
aurora/subsystems/anamod/docs/
```

is empty.

Next breadcrumb:

```text id="7vl8dv"
contracts/MIGRATION_PLAN.md
contracts/TECHNICAL_DEBT.md
contracts/SUBSYSTEM.md
```

Determine whether this directory has an intentional future responsibility before
retaining or removing it.

---

### Runtime Consumer Map

**State:** UNKNOWN

The current subsystem tree proves implementation exists but does not establish
who invokes it.

Next breadcrumb:

```text id="sc1i6y"
consumer search for:
    aurora.subsystems.anamod
    ide_operations
    workspace_service
```

---

## Deeper Contracts

For migration architecture:

```text id="vavqfm"
aurora/subsystems/anamod/contracts/MIGRATION_PLAN.md
```

For known technical debt:

```text id="6t71ym"
aurora/subsystems/anamod/contracts/TECHNICAL_DEBT.md
```

For pre-Hansel architectural evidence:

```text id="yr48x7"
aurora/subsystems/anamod/contracts/SUBSYSTEM.md
```

`SUBSYSTEM.md` is not the canonical entry point.

---

## Hansel Rules for This Subsystem

A worker modifying Anamod must:

1. begin with this contract;
2. distinguish populated implementation from empty architectural scaffolding;
3. consult migration and technical-debt contracts before deleting empty layers;
4. treat `SUBSYSTEM.md` as pre-Hansel evidence rather than the canonical entry
   point;
5. map consumers before moving or deleting Anamod assets;
6. perform tombstone validation after rename or removal;
7. prove IDE/workspace behavior survived relevant refactors;
8. keep repository knowledge ownership outside Anamod;
9. avoid inventing responsibility for empty directories;
10. update this contract when migration resolves current structural unknowns.

---

## Next Hansel Breadcrumb

For implemented IDE behavior:

```text id="s94npr"
aurora/subsystems/anamod/api/ide_operations.py
```

For implemented workspace behavior:

```text id="5ve70k"
aurora/subsystems/anamod/services/workspace_service.py
```

For migration intent:

```text id="9nxvzf"
aurora/subsystems/anamod/contracts/MIGRATION_PLAN.md
```

For known technical debt:

```text id="pwxemg"
aurora/subsystems/anamod/contracts/TECHNICAL_DEBT.md
```

For unresolved pre-Hansel architectural knowledge:

```text id="gpbwqf"
aurora/subsystems/anamod/contracts/SUBSYSTEM.md
```

# ======================================================================
# END: ANAMOD_HANSEL_CONTRACT
# ======================================================================

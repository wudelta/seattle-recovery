# ======================================================================
# FILE: aurora/subsystems/anamod/contracts/HANSEL.md
# START: ANAMOD_HANSEL_CONTRACT
# ======================================================================

# Anamod — Hansel Catalogue

## Purpose

Anamod owns Aurora's repository-editing workspace and the browser-facing
development tools used to inspect, load, create, edit, and operate on repository
files.

Hansel routes Anamod work to the narrowest implementation authority.

---

## Knowledge Catalogue

### Understand or change Anamod UI

Go to:

```text
aurora/subsystems/anamod/contracts/UI_MAP.md
```

Use this authority for:

```text
console layout
Project Hierarchy presentation
Workflow Controls
Operational Pipeline Log Feed
browser-side active-file behavior
Anamod-specific styling
```

### Understand or change Anamod IDE API behavior

Go to:

```text
aurora/subsystems/anamod/api/ide_operations.py
```

Use this authority when browser behavior crosses into repository file
operations.

### Understand or change repository file/workspace operations

Go to:

```text
aurora/subsystems/anamod/services/workspace_service.py
```

Use this authority for bounded repository file reads, writes, existence checks,
creation, and related workspace operations owned by Anamod.

### Understand Anamod migration intent

Go to:

```text
aurora/subsystems/anamod/contracts/MIGRATION_PLAN.md
```

### Investigate known Anamod technical debt

Go to:

```text
aurora/subsystems/anamod/contracts/TECHNICAL_DEBT.md
```

### Consult pre-Hansel architectural evidence

Go to:

```text
aurora/subsystems/anamod/contracts/SUBSYSTEM.md
```

`SUBSYSTEM.md` is not the canonical entry point.

---

## Ownership Boundary

Anamod owns:

```text
repository editor behavior
Anamod IDE operations
bounded workspace/file operations used by Anamod
Anamod browser interaction
Anamod-specific UI presentation
```

Anamod does not own:

```text
Component Registry maintenance or metadata
Hansel repository knowledge
Planning state
AI provider implementation
Wu Chat workflow
general repository discovery
```

When an Anamod task needs one of those capabilities, cross into the owning
subsystem through its `contracts/HANSEL.md`.

---

## Cross-Boundary Routes

### Component Registry

For Component Registry descriptions, maintenance, or enrichment:

```text
aurora/subsystems/component_registry/contracts/HANSEL.md
```

Anamod may consume Component Registry capabilities but must not duplicate their
domain implementation.

### Planning

For persisted engineering-work planning:

```text
aurora/subsystems/planning/contracts/HANSEL.md
```

---

## Validation

Validation must match the changed responsibility.

Examples:

```text
requested file loads successfully;
missing file is handled explicitly rather than failing silently;
created files are bounded to allowed repository paths;
Project Hierarchy reflects repository changes;
active-file UI state remains synchronized;
Component Registry information corresponds to the active file;
Django system check succeeds when backend integration changes.
```

Do not claim completion from visual inspection alone when repository mutation or
cross-subsystem behavior changed.

---

## Unknown Territory

If the requested responsibility is not mapped here:

1. do not infer ownership;
2. inspect the narrowest likely Anamod authority;
3. cross into another subsystem only when the task requires it;
4. add a breadcrumb only when discovery reveals a durable route future workers
   should not have to rediscover.

---

## Sufficient Authority

Stop discovery when all four are known:

1. who owns the behavior;
2. what must change;
3. what must remain unchanged;
4. how the change will be validated.

---

## Catalogue Reconciliation

After changing Anamod, ask whether this catalogue or `UI_MAP.md` still routes
the affected responsibility correctly.

Update only durable ownership routes.

# ======================================================================
# END: ANAMOD_HANSEL_CONTRACT
# ======================================================================

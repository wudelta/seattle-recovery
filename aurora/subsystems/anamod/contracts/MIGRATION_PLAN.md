<!-- ====================================================================== -->
<!-- FILE: aurora/subsystems/anamod/contracts/MIGRATION_PLAN.md -->
<!-- START: ANAMOD_SUBSYSTEM_MIGRATION_PLAN -->
<!-- ====================================================================== -->

# Anamod Subsystem Migration Plan

## Objective

Move Anamod from scattered legacy repository locations into one
self-discoverable subsystem without disrupting Aurora's primary source-editing
workspace.

The migration must preserve all currently supported Anamod workflows.

## Supported Scope

The supported Anamod subsystem currently includes:

- Aurora Console panel integration;
- Project Hierarchy rendering;
- repository hierarchy refresh;
- direct file loading by repository-relative path;
- Monaco Editor initialization;
- file loading;
- file editing;
- file saving;
- discarding unsaved changes;
- Copy File;
- Copy Path;
- file creation;
- directory creation;
- file rename;
- file deletion;
- active-file and dirty-state presentation;
- Anamod terminal output.

## Deferred Scope

### Sandbox Execution

The sandbox feature is present in the repository but has never worked
reliably and is not part of Delta's active Anamod workflow.

During this migration:

- do not repair it;
- do not redesign it;
- do not use it as a validation requirement;
- do not allow it to block migration;
- preserve its current code only where necessary to avoid unrelated
  regressions.

A later Initiative must decide whether to repair the sandbox as an independent
subsystem or remove it.

### Monaco Worker Configuration

**Status:** DEFERRED

Anamod currently reports Monaco worker-loading failures and falls back to
executing worker code on the main thread. Core supported workflows remain
operational.

During this migration:

- do not treat the worker defect as caused by tracker removal;
- do not repair it inside unrelated migration steps;
- record it as separate technical debt;
- preserve working editor behavior while runtime assets are relocated.

## Legacy Component Map

### User Interface

```text
aurora/templates/aurora/snippets/anamod_console_panel.html
```

### Styles

```text
aurora/static/aurora/css/anamod.css
```

### Editor Controller

```text
aurora/static/aurora/js/anamod.js
```

### Workspace Tree Controller

```text
aurora/static/aurora/js/anamod_workspace.js
```

### Legacy Tracker

**Status:** REMOVED

Former path:

```text
aurora/static/aurora/js/anamod_tracker.js
```

Repository-wide discovery confirmed that its runtime hooks were not called
outside the tracker itself. Dirty-state behavior remained operational after its
script loader was removed.

The script loader and file were deleted after validation.

### Console Integration

```text
aurora/templates/aurora/aurora_console.html
aurora/static/aurora/js/console.js
```

### Anamod-Facing API

```text
aurora/api/ide_operations.py
```

The internal `FILE:` anchors in this module currently reference the incorrect
legacy path:

```text
aurora/views/ide_operations.py
```

The repository path is authoritative.

Do not correct or move this module until its responsibilities are separated
deliberately.

## Target Structure

```text
aurora/subsystems/anamod/
    __init__.py

    api/
        __init__.py

    contracts/
        __init__.py
        SUBSYSTEM.md
        MIGRATION_PLAN.md
        TECHNICAL_DEBT.md

    services/
        __init__.py

    validation/
        __init__.py

    workspace/
        __init__.py
```

Framework-managed templates and static assets remain in Django's conventional
locations for now.

Hansel records their logical ownership without requiring physical relocation.

## Target Responsibilities

### Django-Managed Presentation

The following runtime assets remain in Django's established template and
static roots:

```text
aurora/templates/aurora/snippets/anamod_console_panel.html
aurora/static/aurora/css/anamod.css
aurora/static/aurora/js/anamod.js
aurora/static/aurora/js/anamod_workspace.js
```

Hansel defines these files as logically owned by Anamod.

Their physical locations are framework constraints, not ownership boundaries.

### `workspace/`

Owns repository navigation and file-operation logic after responsibility
separation.

### `services/`

Owns reusable application logic extracted from HTTP handlers, including path
safety and repository mutation policy.

### `api/`

Owns Anamod-facing HTTP adapters.

It must not own generic filesystem behavior merely because the browser calls
the endpoint.

### `validation/`

Owns deterministic Anamod validation helpers and future Hansel-aware checks.

### Deferred Sandbox Boundary

Docker execution and Python linting remain outside the active Anamod migration.

They must not block workspace API separation.

## Migration Sequence

### Phase 1 — Establish Contracts

Status: ACTIVE

Required evidence:

- `SUBSYSTEM.md` identifies current runtime components;
- initialization order is documented;
- current APIs are documented;
- unsupported sandbox behavior is explicitly deferred;
- target responsibilities are defined.

Validation:

```text
A future worker can begin with SUBSYSTEM.md and MIGRATION_PLAN.md
without performing a repository-wide search.
```

### Phase 2 — Validate and Remove Legacy Tracker

Status: COMPLETED

Verified evidence:

1. Repository-wide search found runtime references only inside
   `anamod_tracker.js`.
2. References in `MIGRATION_PLAN.md` were documentation, not callers.
3. The tracker script loader was removed from
   `aurora/templates/aurora/aurora_console.html`.
4. `aurora/static/aurora/js/anamod_tracker.js` was deleted.
5. Copy File, Copy Path, Load File, and hierarchy refresh remained operational.
6. Existing Monaco worker errors remained unchanged and were classified as
   separate deferred technical debt.

Validation:

- no browser-console error references `anamod_tracker.js`;
- Anamod initializes without the tracker;
- supported file navigation and clipboard workflows remain operational;
- dirty-state behavior is owned by `anamod.js`.

### Phase 3 — Preserve Django Presentation Conventions

Status: COMPLETED

Decision:

- keep Anamod templates in Django's template root;
- keep Anamod CSS and JavaScript in Django's static root;
- define subsystem ownership through Hansel contracts;
- do not create a new frontend framework or standalone Django app during this
  migration.

Validation:

- Django template discovery remains unchanged;
- static-file resolution remains unchanged;
- Anamod frontend paths remain stable;
- Hansel documents logical ownership explicitly.

### Phase 4 — Separate Workspace Backend Responsibilities

Status: ACTIVE

Current source:

```text
aurora/api/ide_operations.py
```

The module currently mixes:

```text
Repository hierarchy
Repository file operations
Sandbox execution
Python linting
```

Tasks:

1. Identify every helper used by `file_tree_api()` and
   `file_operation_api()`.
2. Separate repository workspace logic from HTTP request handling.
3. Preserve existing route names and browser behavior.
4. Leave `run_code_api()` and `lint_code_api()` untouched except where
   necessary to preserve imports.
5. Correct internal FILE anchors only when the relevant anchored region is
   moved or replaced.
6. Validate repository navigation and file operations after each extraction.

Required validation:

- Project Hierarchy loads;
- Refresh works;
- tree selection loads files;
- Load File works;
- Save works;
- Discard works;
- file creation works;
- directory creation works;
- rename works;
- delete works.

### Phase 5 — Consolidate Anamod Browser Entry Points

Status: PLANNED

Review whether `anamod.js` and `anamod_workspace.js` should remain separate
Django-managed static files or expose one subsystem initializer.

Do not move them merely for directory purity.

### Phase 6 — Reduce Console Coupling

Status: PLANNED

Move Anamod-specific initialization knowledge out of the general Aurora Console
where practical.

The Console should eventually need to know only:

```text
Anamod panel include
Anamod asset entry points
Anamod initializer
```

It should not need to understand internal editor and workspace behavior.

## Validation Baseline

After every runtime move, validate:

1. Aurora Console loads without JavaScript errors.
2. Anamod opens from the Console selector.
3. Project Hierarchy loads.
4. Refresh detects files created outside Anamod.
5. Tree selection loads a file.
6. Load File opens a repository-relative path.
7. Monaco permits editing.
8. Save persists changes.
9. Discard restores disk content.
10. Copy File copies the active buffer.
11. Copy Path copies the repository-relative path.
12. File and directory context-menu operations still work.

Sandbox execution is explicitly excluded from the current validation baseline.

## Rollback Rule

Anamod is critical-path engineering infrastructure.

If a migration step breaks a supported workflow:

1. stop;
2. restore the affected files from Git;
3. verify Anamod is operational;
4. inspect the failed step only after recovery.

Do not stack additional patches on a broken Anamod state.

## Patch Rule

All Anamod changes must use complete anchored replacement regions.

When adding a new anchored region, the delivery must identify its exact
placement relative to existing anchors.

Large complete-file replacements may be delivered as downloadable artifacts,
but they must preserve every existing responsibility unless removal is an
explicitly validated migration step.

## Next Hansel Step

Inspect the complete anchored regions in:

```text
aurora/api/ide_operations.py
```

that define:

```text
get_file_tree()
file_tree_api()
file_operation_api()
```

Identify:

- imports required only by workspace behavior;
- private helpers used by those functions;
- path-normalization and path-safety behavior;
- filesystem mutation logic;
- response construction that belongs in the HTTP adapter.

Do not modify:

```text
run_code_api()
lint_code_api()
```

during this discovery step.

The goal is to define the smallest safe extraction boundary for workspace
services while preserving the existing routes.

<!-- ====================================================================== -->
<!-- FILE: aurora/subsystems/anamod/contracts/MIGRATION_PLAN.md -->
<!-- END: ANAMOD_SUBSYSTEM_MIGRATION_PLAN -->
<!-- ====================================================================== -->

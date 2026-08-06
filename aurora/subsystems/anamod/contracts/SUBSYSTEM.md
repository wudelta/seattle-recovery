<!-- ====================================================================== -->
<!-- FILE: aurora/subsystems/anamod/contracts/SUBSYSTEM.md -->
<!-- START: ANAMOD_SUBSYSTEM_CONTRACT -->
<!-- ====================================================================== -->

# Anamod Subsystem Contract

This is the initial Hansel contract for the Anamod subsystem.

## Purpose

Anamod is Aurora's integrated repository editing workspace.

It provides the browser-facing interface used to inspect, load, edit, save, create, rename, delete, and execute repository source files from Aurora Console.

## Runtime Components

* UI:
  `aurora/templates/aurora/snippets/anamod_console_panel.html`

* CSS:
  `aurora/static/aurora/css/anamod.css`

* Primary editor controller:
  `aurora/static/aurora/js/anamod.js`

* Workspace tree controller:
  `aurora/static/aurora/js/anamod_workspace.js`

* Dirty-state tracker:
  `aurora/static/aurora/js/anamod_tracker.js`

* Console integration:
  `aurora/templates/aurora/aurora_console.html`

* Console pane controller:
  `aurora/static/aurora/js/console.js`

## Responsibilities

Anamod currently coordinates:

* repository hierarchy display;
* Monaco editor initialization;
* repository file loading;
* file save and discard operations;
* Copy File and Copy Path actions;
* direct file loading by repository-relative path;
* hierarchy refresh;
* context-menu file creation;
* context-menu directory creation;
* file rename and delete operations;
* Python syntax validation;
* sandbox execution;
* editor dirty-state presentation;
* workspace and sandbox terminal output.

## Verified Browser Interfaces

The current JavaScript integration surface includes:

```text
window.initAnamodConsole(csrfToken)
window.initAnamodWorkspaceTree()
window.refreshWorkspaceTree()
window.loadWorkspaceFile(filePath)
window.renameWorkspaceFile(oldPath, newName)
window.deleteWorkspaceFile(filePath)
window.updateAnamodTerminal(message)
```

These interfaces connect separate Anamod JavaScript files.

They must remain stable until all callers have been identified and migrated.

## Verified API Dependencies

Anamod currently consumes four Aurora API routes.

### Repository Hierarchy

```text
GET /aurora/api/files/tree/
```

Current backend implementation:

```text
aurora/views/ide_operations.py
    get_file_tree()
    file_tree_api()
```

Purpose:

* scan the repository workspace;
* exclude configured directories;
* build the hierarchy consumed by jsTree.

### Repository File Operations

```text
GET /aurora/api/files/op/
POST /aurora/api/files/op/
PATCH /aurora/api/files/op/
PUT /aurora/api/files/op/
DELETE /aurora/api/files/op/
```

Current backend implementation:

```text
aurora/views/ide_operations.py
    file_operation_api()
```

Purpose by method:

```text
GET
    Load or reload a repository file.

POST
    Create a repository file or directory.

PATCH
    Save file contents.

PUT
    Rename a repository node.

DELETE
    Delete a repository file or directory.
```

### Sandbox Execution

```text
POST /aurora/api/sandbox/run/
```

Current backend implementation:

```text
aurora/views/ide_operations.py
    run_code_api()
```

Purpose:

* execute submitted Python code inside a restricted Docker container;
* disable networking;
* apply memory and CPU limits;
* collect stdout and stderr;
* remove the temporary container after execution.

### Python Validation

```text
POST /aurora/api/sandbox/lint/
```

Current backend implementation:

```text
aurora/views/ide_operations.py
    lint_code_api()
```

Purpose:

* compile submitted Python code;
* report fatal syntax errors;
* run a filtered Flake8 validation pass;
* return validation output to Monaco.

## Verified Backend Boundary

The Anamod-facing backend currently resides in:

```text
aurora/views/ide_operations.py
```

That module contains at least three distinct responsibilities:

```text
Workspace discovery
    get_file_tree()
    file_tree_api()

Workspace file mutation
    file_operation_api()

Sandbox execution and validation
    run_code_api()
    lint_code_api()
```

The module must not be moved wholesale into the Anamod subsystem merely because Anamod consumes these endpoints.

The workspace and sandbox operations may be shared Aurora infrastructure.

Ownership must be determined by identifying every current caller before migration.

## Current Runtime Flow

```text
Aurora Console
    ↓
Anamod panel activation
    ↓
initAnamodConsole()
initAnamodWorkspaceTree()
    ↓
anamod.js
anamod_workspace.js
anamod_tracker.js
    ↓
Aurora API routes
    ↓
aurora/views/ide_operations.py
    ↓
Repository filesystem or Docker sandbox
```

## Stable Workflows

The following workflows must remain operational after every migration step.

### Open File Through Hierarchy

```text
Select repository file
    ↓
window.loadWorkspaceFile(filePath)
    ↓
GET /aurora/api/files/op/
    ↓
Monaco editor buffer
```

### Open File by Path

```text
Select Load File
    ↓
Enter repository-relative path
    ↓
window.loadWorkspaceFile(filePath)
    ↓
GET /aurora/api/files/op/
    ↓
Monaco editor buffer
```

### Refresh Repository Hierarchy

```text
Select Refresh
    ↓
window.refreshWorkspaceTree()
    ↓
jsTree refresh
    ↓
GET /aurora/api/files/tree/
```

### Save File

```text
Edit Monaco buffer
    ↓
Save
    ↓
PATCH /aurora/api/files/op/
    ↓
Repository file updated
```

### Discard Changes

```text
Discard
    ↓
GET /aurora/api/files/op/
    ↓
Monaco buffer restored
```

### Execute Python

```text
Select Execute Sandbox Run
    ↓
POST /aurora/api/sandbox/run/
    ↓
Restricted Docker container
    ↓
Terminal output
```

## Migration Rules

1. Document responsibilities before moving runtime files.
2. Replace complete anchored regions only.
3. New anchored regions must state exactly where they belong.
4. Roll back failed Anamod implementations immediately.
5. Restore existing Anamod behavior before debugging continues.
6. Preserve public browser interfaces until all callers are identified.
7. Do not move shared workspace or sandbox infrastructure into Anamod by inference.
8. Move one responsibility at a time.
9. Validate existing workflows after every move.
10. Commit each independently validated migration step before continuing.

## Current Ownership Assessment

Anamod clearly owns:

* its panel markup;
* its CSS;
* its browser-side editor coordination;
* its workspace-tree interaction;
* its active-file controls;
* its Anamod-specific terminal presentation.

Ownership is not yet established for:

* repository filesystem traversal;
* repository path validation;
* repository file mutation;
* Docker sandbox execution;
* Python linting;
* general Aurora Console pane orchestration.

## Next Hansel Step

Identify every caller of the backend functions and routes implemented by:

```text
aurora/views/ide_operations.py
```

The next discovery must determine whether these backend capabilities are:

```text
Anamod-specific
Shared Aurora workspace infrastructure
Shared Aurora sandbox infrastructure
Legacy mixed responsibilities requiring separation
```

Search specifically for callers of:

```text
file_tree_api
file_operation_api
run_code_api
lint_code_api

/aurora/api/files/tree/
/aurora/api/files/op/
/aurora/api/sandbox/run/
/aurora/api/sandbox/lint/
```

Do not move runtime files during that discovery step.

<!-- ====================================================================== -->
<!-- FILE: aurora/subsystems/anamod/contracts/SUBSYSTEM.md -->
<!-- END: ANAMOD_SUBSYSTEM_CONTRACT -->
<!-- ====================================================================== -->

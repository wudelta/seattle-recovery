# Aurora Production Blueprint Backlog

## 1. Incremental Refactoring Protocol (The "Go" Loop)
When Delta feeds the AI a file to refactor, upgrade, or extend, the engine must never return the entire file or multiple patches at once. The engine must strictly parse and deliver the update using the following conversational loop:
1. **The Partition Task**: Break the code updates down into highly localized, un-nested Surgical Block Anchor patches (e.g., `PATCH 1 OF X`, `PATCH 2 OF X`).
2. **The Single-Block Lock**: Deliver exactly **one single block** (e.g., `PATCH 1 OF X`) in the response window.
3. **The Yield Block**: Immediately halt output generation, provide a brief summary of what that specific patch modifies, and wait for Delta's confirmation.
4. **The Step Signal**: The AI must not output the next sequential patch until Delta explicitly enters the text variable keyword: **"go"**.
5. **Numbering Continuity Retention**: When returning patches for a file containing pre-existing numbered blocks, the engine must strictly preserve the file's original master index layout numbering (e.g., matching `PATCH 4 OF 5`) to prevent pipeline parsing offsets.

## 2. Refactoring & Code Delivery Standards
1. **Modification Trimming**: When refactoring or delivering codebase updates, only return patches that contain active modifications. Do not output unedited code blocks.
2. **Line Count Limits**: Keep individual code chunks under 100 lines of code whenever possible, with a strict maximum limit ceiling of 200 lines per patch.

## 3. Immediate Next Staging Steps (Tomorrow's Vector)
1. **Automated AST Dependency Topography Scanner**: Build the local static file code analyzer to parse import statements inside newly forged modules and dynamically register `DEPENDS_ON` graph links in Neo4j.
2. **Dead Code Isolation Utility**: Build a zero-token `/cleanup` or routing check that walks the Neo4j incoming relationship paths to flag and safely isolate any orphaned, unreferenced components.
3. **Agent Setup Orchestration**: Verify system configurations inside `aurora/agents.py` and activate Wu's 70B model gateway payload parameters to decompose plain English instructions down to targeted 8B Minions.

---

## Completed via DeltaNotes Lifecycle (2026-06-08)
* [x] Move the skeleton builders to utils folder and fix api_views to import them correctly
* [x] Move api_views.py from the views folder to api folder, rename to api_commands, fix urls, and register in api/__init__.py
* [x] Update urls, console views, and javascript files to utilize the api_commands namespace routing matrix
* [x] Break out console html view structures into modular snippets and use the include tag to load them
* [x] Add inline interactive Edit and Delete controls next to unprocessed_log entries in delta_notes to allow updates before processing
* [x] Integrate the Delta Notes environment directly into the master aurora_console cockpit, deleting redundant files, stale URL routes, and obsolete view exports
* [x] Remove the experimental journal debounce auto-save loop from the cockpit script asset layer
* [x] Secure full closure runtime scope alignment for focus session timers and project blueprint markdown compilers

---

## Completed via DeltaNotes Lifecycle (2026-06-09)
* [x] Standardize all application layer models, endpoints, views, and JavaScript loops on the explicit database schema class identifier `DeltaNotesEntry` to eradicate technical debt.
* [x] Update the `UNPROCESSED_LOG` interface row loops to display all active developer directives that are not marked processed in the database to allow dynamic inline modifications.
* [x] Add a completion switch control button (`✓`) to the `UNPROCESSED_LOG` entries that immediately triggers a transaction payload to mark records as processed.
* [x] Relocate the "Compile to project.md" execution control element from the header bar straight into the `CAPTURE_INTENTION` form block workspace under the active queue addition button.
* [x] Re-engineer the file compiler engine to utilize explicit non-destructive append protocols (`"a"`) that write sub-header timestamps to safeguard historic project backlog entries.
* [x] Add a distinct `PROCESSED_LOG` monitoring section adjacent to the `UNPROCESSED_LOG` view layout to render items completed during the active session.
* [x] Relocate the modular layout structure inside `notes_control_bar.html` to be a permanent, un-nested feature of `aurora_console.html` under the uniform namespace `console_control_bar`.
* [x] Synchronize the aesthetic styling of `blueprint_console_panel.html` to inherit the high-density console aesthetic parameters defined in `delta_notes.css`, utilizing transparent card bodies to pass the dark Bootswatch theme seamlessly.
* [x] Standardize all dashboard container headers across both panels to conform to a colored, capitalized, un-alphabetic underscore layout (`BLUEPRINT_DESK`, `MINION_ASSEMBLY_LINE`, `VALIDATION_INSPECTOR`, `CODE_CRUCIBLE`, `CAPTURE_INTENTION`, `UNPROCESSED_LOG`, `PROCESSED_LOG`) with distinct programmatic stage identifications.
* [x] Completely decouple `blueprint_console_panel.html` from the static DOM rendering cascade, establishing an explicit select-option router inside `console_control_bar` to dynamically mount separate panes into the viewport.
* [x] Enforce horizontal and vertical alignment parity across both console dashboards by shifting grid row configurations to unified `gx-2 gy-0` gutters and wrapping the workflow desks in height-stretching flex boxes.
* [x] Eliminate the legacy text banner tag `⚡ DELTA_NOTES: ID: delta` from the primary navigation array block to favor clean widescreen selector components.
